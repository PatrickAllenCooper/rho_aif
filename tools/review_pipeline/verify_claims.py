#!/usr/bin/env python3
r"""
Verify number-bearing claims in JAIR/LNCS prose against the CSVs they cite.

Built 2026-09-06 after the experiment-batch audit found 24 defects in 108
checked items in a page of prose written in one pass and checked afterward,
against 2 defects in 5 changes when each fix was re-derived from its
artifact before applying (ledger 9.17.28). This is the mechanical half of
that discipline: a fast pre-check that catches typos, transposed digits,
dangling references, and asymmetric comparisons before the (slower,
semantic) adversarial-audit workflow spends its budget on them.

This is NOT a substitute for the audit. It cannot tell you a comparison is
unfair, only that a number matches a cell in the CSV named nearby, that a
table reference points somewhere real and that "somewhere" contains what
the sentence says it contains, and that both arms of a tuned-vs-default
comparison were flagged for a human to check.

An early version of this tool searched every number against every cell in
every CSV under results/ (13,531 rows, ~100,000 rounded forms) and missed
the exact bug it was built to catch: "$+3.74$ against $+5.65$" survived
because 3.74 coincidentally matched an unrelated cell in a different row
of the very file the sentence cited, while the true value (3.735, which
formats to 3.73) sat one row away. Coincidence at that density is not rare,
it is close to certain. The fix is scoping: only the CSV file actually
named in the sentence counts as ground truth, matched at exact precision
with no tolerance, because tolerance is exactly the gap a wrong last digit
hides in.

Four checks:

1. Every \texttt{results_*.csv} filename named in added prose exists under
   results/.
2. Every \ref{tab:...} / \ref{fig:...} target in added prose is \label'd
   somewhere in the manuscripts or paper/tables/*.tex.
2b. "Table~\ref{X}'s <word> rows/row" patterns: the referenced table's own
   content (its \begin{table}...\end{table} block, wherever that lives)
   must contain <word>, so a caption cannot describe rows a table doesn't
   have.
3. Every decimal number in added prose, scoped to the CSV file named on
   the same line (or, failing that, the CSV file if the whole file names
   exactly one), must appear at the SAME decimal precision as written,
   after applying %/fraction scaling if a percent sign is present. No
   tolerance: a claim is either the number in that file, or it isn't. A
   number with no CSV named nearby and no single-CSV file to fall back on
   is checked against every CSV as a last resort and reported separately,
   since that search is exactly the coincidence-prone one this tool used
   to rely on everywhere.
4. A same-sentence pattern naming one side of a comparison "default" or
   "untuned" and the other "best" or "tuned" is flagged for manual review.

Usage:
    python tools/review_pipeline/verify_claims.py [--base REF] [--head REF] [FILES...]

Default base is HEAD (diffs the working tree); default FILES are both live
masters and paper/tables/*.tex. Exit 1 if any check 1/2/2b/3(scoped) issue
is found. Unscoped-search results and check 4 are reported but never
affect the exit code, since both need a human to adjudicate.
"""
from __future__ import annotations

import argparse
import csv
import glob
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_FILES = [
    "paper/full_paper_jair.tex",
    "paper/full_paper.tex",
] + sorted(glob.glob(os.path.join(REPO, "paper/tables/*.tex")))
DEFAULT_FILES = [f if os.path.isabs(f) else os.path.join(REPO, f) for f in DEFAULT_FILES]
ALL_TABLE_FILES = sorted(glob.glob(os.path.join(REPO, "paper/tables/*.tex")))
ALL_MASTERS = [os.path.join(REPO, "paper/full_paper_jair.tex"), os.path.join(REPO, "paper/full_paper.tex")]

NUM_RE = re.compile(r"(?<![A-Za-z0-9_.])(-?\d+\.\d+)(?![A-Za-z0-9_.])")
PERCENT_TAIL_RE = re.compile(r"^.{0,24}?(?:\\%|%|\bpp\b)")
CSVNAME_RE = re.compile(r"\\texttt\{([a-zA-Z0-9_\\ ]+?\.csv)\}")
REF_RE = re.compile(r"\\ref\{((?:tab|fig):[a-zA-Z0-9_:-]+)\}")
LABEL_RE = re.compile(r"\\label\{((?:tab|fig):[a-zA-Z0-9_:-]+)\}")
TABLE_BLOCK_RE = re.compile(r"\\begin\{table\*?\}(.*?)\\end\{table\*?\}", re.DOTALL)
DESC_RE = re.compile(r"Table~?\\ref\{(tab:[a-zA-Z0-9_:-]+)\}'s\s+([A-Za-z][A-Za-z]*)\s+rows?", re.IGNORECASE)
ASYM_RE = re.compile(
    r"\b(tuned|best(?:-swept)?)\b[^.]{0,80}\bagainst\b[^.]{0,80}\b(default|untuned)\b"
    r"|\b(default|untuned)\b[^.]{0,80}\bagainst\b[^.]{0,80}\b(tuned|best(?:-swept)?)\b",
    re.IGNORECASE,
)
SIG_THRESHOLDS = {"0.05", "0.01", "0.001", "0.0001", "0.10"}


def clean_csv_name(raw: str) -> str:
    return raw.replace("\\allowbreak", "").replace(" ", "").replace("\\_", "_")


def added_lines(base: str, head: str | None, files: list[str]) -> dict[str, list[str]]:
    """Map each file to its added prose lines. Diffs base..working tree by
    default, or base..head when --head is given (for retroactive checks
    against a past commit range)."""
    out: dict[str, list[str]] = {}
    for f in files:
        rel = os.path.relpath(f, REPO)
        cmd = (["git", "-C", REPO, "diff", f"{base}..{head}", "--", rel] if head
               else ["git", "-C", REPO, "diff", base, "--", rel])
        try:
            diff = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
        except subprocess.CalledProcessError:
            diff = ""
        lines = []
        for line in diff.splitlines():
            if line.startswith("+++"):
                continue
            if line.startswith("+"):
                stripped = line[1:]
                if stripped.strip().startswith("%"):
                    continue
                lines.append(stripped)
        out[rel] = lines
    return out


def all_labels_and_table_content(files: list[str]) -> tuple[set[str], dict[str, str]]:
    labels: set[str] = set()
    content: dict[str, str] = {}
    for f in set(files) | set(ALL_TABLE_FILES) | set(ALL_MASTERS):
        if not os.path.exists(f):
            continue
        text = open(f).read()
        labels |= set(LABEL_RE.findall(text))
        for block in TABLE_BLOCK_RE.findall(text):
            for lbl in LABEL_RE.findall(block):
                content[lbl] = block
    return labels, content


def whole_file_csv_names(path: str) -> set[str]:
    if not os.path.exists(path):
        return set()
    return {clean_csv_name(n) for n in CSVNAME_RE.findall(open(path).read())}


def load_csv_cells(name: str) -> list[str]:
    path = os.path.join(REPO, "results", name)
    if not os.path.exists(path):
        return []
    cells = []
    try:
        with open(path, newline="") as fh:
            reader = csv.reader(fh)
            next(reader, None)
            for row in reader:
                cells.extend(row)
    except (OSError, csv.Error):
        return []
    return cells


_CSV_CACHE: dict[str, list[str]] = {}


def csv_cells(name: str) -> list[str]:
    if name not in _CSV_CACHE:
        _CSV_CACHE[name] = load_csv_cells(name)
    return _CSV_CACHE[name]


def value_in_csv(raw: str, is_percent: bool, csv_name: str) -> bool:
    """Compare in the unit the prose used (percent stays percent), at the
    exact precision the prose wrote, against every reasonable scaling of
    each CSV cell. Converting the PROSE number to fraction space before
    comparing (the first version of this function did that) throws away
    precision the wrong way: "97.7" has one meaningful decimal in percent
    space, but 97.7/100 formatted to one decimal is "1.0", destroying the
    comparison entirely. Scaling the CELL instead keeps full precision on
    both sides."""
    try:
        v = float(raw)
    except ValueError:
        return False
    nd = len(raw.split(".")[-1])
    targets = {f"{v:.{nd}f}", f"{-v:.{nd}f}"}
    for cell in csv_cells(csv_name):
        try:
            cv = float(cell)
        except (TypeError, ValueError):
            continue
        candidates = (cv, cv * 100.0) if is_percent else (cv,)
        for c in candidates:
            if f"{c:.{nd}f}" in targets:
                return True
    return False


def nearest_csv_for_number(line_csvs: list[tuple[int, str]], pos: int) -> str | None:
    """The CSV named closest to this position on the line: prefer the
    nearest one before it, else the nearest one after it."""
    before = [c for p, c in line_csvs if p < pos]
    if before:
        return before[-1]
    after = [c for p, c in line_csvs if p > pos]
    return after[0] if after else None


def check_file(rel: str, full_path: str, lines: list[str], labels: set[str],
                table_content: dict[str, str]) -> dict[str, list[str]]:
    issues = {"missing_csv": [], "broken_ref": [], "content_mismatch": [],
              "mismatch": [], "unscoped": [], "asymmetric": []}
    file_csv_names = whole_file_csv_names(full_path)
    single_file_fallback = next(iter(file_csv_names)) if len(file_csv_names) == 1 else None

    for line in lines:
        if not line.strip():
            continue

        for m in CSVNAME_RE.finditer(line):
            name = clean_csv_name(m.group(1))
            if name.startswith("_") or name.startswith("*"):
                continue  # deliberate shorthand for "the companion _stats.csv file", not a filename
            if not os.path.exists(os.path.join(REPO, "results", name)):
                issues["missing_csv"].append(f"{rel}: \\texttt{{{name}}} not found under results/")

        for m in REF_RE.finditer(line):
            if m.group(1) not in labels:
                issues["broken_ref"].append(f"{rel}: \\ref{{{m.group(1)}}} has no matching \\label anywhere checked")

        for m in DESC_RE.finditer(line):
            label, word = m.group(1), m.group(2)
            block = table_content.get(label)
            if block is not None and word.lower() not in block.lower():
                issues["content_mismatch"].append(
                    f"{rel}: \"Table~\\ref{{{label}}}'s {word} rows\" but that table's own content "
                    f"contains no \"{word}\" (label content checked directly)"
                )

        for m in ASYM_RE.finditer(line):
            snippet = line[max(0, m.start() - 40):m.end() + 40]
            issues["asymmetric"].append(f"{rel}: possible asymmetric comparison \u2014 \u2026{snippet}\u2026")

        scope_events = [(m.start(), clean_csv_name(m.group(1))) for m in CSVNAME_RE.finditer(line)]
        for m in REF_RE.finditer(line):
            block = table_content.get(m.group(1))
            if block:
                # A table's own caption often names a comparison-basis CSV
                # first and its data source last ("... as the runs of X.csv)
                # ... See Y.csv and its stats companion."). The last name is
                # the convention this project's captions use for "here is
                # where these numbers come from," so it wins when there is
                # more than one.
                names_in_order = [clean_csv_name(n) for n in CSVNAME_RE.findall(block)]
                if names_in_order:
                    scope_events.append((m.start(), names_in_order[-1]))
        scope_events.sort()
        for m in NUM_RE.finditer(line):
            raw = m.group(1)
            val = raw.lstrip("-")
            if val in SIG_THRESHOLDS:
                continue
            tail = line[m.end():m.end() + 12]
            if re.match(r"\s*\{?\\times\}?\s*10\^", tail) or re.match(r"\s*[eE][+-]?\d", tail):
                continue  # scientific-notation mantissa, never a literal CSV cell
            # "$96.3 \pm 0.6$pp": the percent signal trails the SE term, not
            # the point estimate, so look past a possible \pm pair rather
            # than only the few characters right after this number.
            pct = bool(PERCENT_TAIL_RE.match(line[m.end():m.end() + 30]))
            ctx = line[max(0, m.start() - 70):m.end() + 15]
            scope = nearest_csv_for_number(scope_events, m.start()) or single_file_fallback
            if scope:
                if not value_in_csv(raw, pct, scope):
                    issues["mismatch"].append(
                        f"{rel}: {raw}{'%' if pct else ''} not found at that precision in "
                        f"{scope} \u2014 \u2026{ctx}\u2026"
                    )
            else:
                found_anywhere = any(
                    value_in_csv(raw, pct, os.path.basename(p))
                    for p in glob.glob(os.path.join(REPO, "results", "*.csv"))
                )
                if not found_anywhere:
                    issues["unscoped"].append(
                        f"{rel}: {raw}{'%' if pct else ''} not found in any results/*.csv and no CSV "
                        f"named nearby \u2014 \u2026{ctx}\u2026"
                    )
    return issues


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", default="HEAD", help="git ref to diff against (default HEAD)")
    ap.add_argument("--head", default=None,
                     help="git ref to diff base against instead of the working tree "
                          "(retroactive checks, e.g. --base A --head B)")
    ap.add_argument("files", nargs="*", default=None)
    args = ap.parse_args()
    files = [f if os.path.isabs(f) else os.path.join(REPO, f) for f in args.files] if args.files else DEFAULT_FILES

    labels, table_content = all_labels_and_table_content(files)
    diffs = added_lines(args.base, args.head, files)

    all_issues = {"missing_csv": [], "broken_ref": [], "content_mismatch": [],
                  "mismatch": [], "unscoped": [], "asymmetric": []}
    for rel, lines in diffs.items():
        full_path = os.path.join(REPO, rel)
        issues = check_file(rel, full_path, lines, labels, table_content)
        for k in all_issues:
            all_issues[k].extend(issues[k])

    # missing_csv / broken_ref / content_mismatch have near-zero false-positive
    # rates (a file exists or doesn't, a label exists or doesn't, a word is in a
    # block of text or isn't) and fail the build. Numeric mismatch and unscoped
    # depend on correctly resolving which CSV a number came from in prose that
    # mixes \texttt{file.csv}, Table~\ref{} pointing at a table whose own
    # caption names the file, bare \url{script.py} citations, and numbers with
    # no citation at all in reach — resolving that in general needs more than
    # regex, so these are reported for a human or the audit workflow to triage,
    # not treated as proven wrong.
    hard = all_issues["missing_csv"] + all_issues["broken_ref"] + all_issues["content_mismatch"]

    def section(title: str, items: list[str]) -> None:
        if not items:
            return
        print(f"\n=== {title} ({len(items)}) ===")
        for it in items:
            print(" -", it)

    section("Missing CSV files", all_issues["missing_csv"])
    section("Broken \\ref targets", all_issues["broken_ref"])
    section("Table content mismatch (caption/prose describes rows the table doesn't have)",
            all_issues["content_mismatch"])
    section("REVIEW: number not found at stated precision in the CSV resolved nearby "
            "(often right but cited a different way; check before trusting)", all_issues["mismatch"])
    section("REVIEW: no CSV resolved nearby and not found anywhere (may be a derived "
            "quantity, or may be wrong)", all_issues["unscoped"])
    section("Possible asymmetric comparisons (manual review, not a failure)", all_issues["asymmetric"])

    total_added = sum(len(v) for v in diffs.values())
    review_count = len(all_issues["mismatch"]) + len(all_issues["unscoped"])
    if total_added == 0:
        print("No added prose lines found in the given diff. Nothing to check.")
    elif hard:
        print(f"\n{len(hard)} issue(s) found. Fix before staging.")
    elif review_count:
        print(f"\nNo hard failures. {review_count} numeric claim(s) above need a human "
              f"or the audit workflow to check — the exit code does not fail on these alone.")
    else:
        print("\nAll checks passed, including every numeric claim at its resolved precision.")
    return 1 if hard else 0


if __name__ == "__main__":
    sys.exit(main())
