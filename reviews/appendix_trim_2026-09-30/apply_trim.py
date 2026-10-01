"""Apply accepted appendix-trim proposals to both masters (ledger 9.17.58).

Usage: python apply_trim.py [--dry-run] [--skip ID ...] proposals_*.json

Every edit is guarded: `old` must occur exactly `lncs_count` times in the
LNCS master and once in JAIR, no two accepted edits may overlap, and no
\\label removed may still be referenced afterwards. Nothing is written
unless every check passes.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JAIR = ROOT / "paper/full_paper_jair.tex"
LNCS = ROOT / "paper/full_paper.tex"


def spans(text, old):
    i = text.find(old)
    return (i, i + len(old))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--skip", nargs="*", default=[])
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    props = []
    for f in a.files:
        props += [p for p in json.loads(Path(f).read_text())["proposals"] if p["id"] not in a.skip]

    texts = {"jair": JAIR.read_text(), "lncs": LNCS.read_text()}
    ok = True
    edits = {"jair": [], "lncs": []}
    for p in props:
        for m in ("jair", "lncs"):
            old = p["old"] if m == "jair" or not p.get("old_lncs") else p["old_lncs"]
            new = p["new"] if m == "jair" or p.get("new_lncs") is None else p["new_lncs"]
            want = 1 if m == "jair" else p.get("lncs_count", 1)
            c = texts[m].count(old)
            if c != want:
                print(f"FAIL {p['id']} {m}: found {c}, expected {want}")
                ok = False
            elif c:
                edits[m].append((*spans(texts[m], old), new, p["id"]))

    for m, es in edits.items():
        es.sort()
        for (s1, e1, _, i1), (s2, e2, _, i2) in zip(es, es[1:]):
            if s2 < e1:
                print(f"OVERLAP {m}: {i1} and {i2}")
                ok = False
    if not ok:
        print("Nothing written.")
        return 1

    out = {}
    for m, es in edits.items():
        t = texts[m]
        for s, e, new, _ in sorted(es, reverse=True):
            t = t[:s] + new + t[e:]
        out[m] = t

    for m, t in out.items():
        inputs = re.findall(r"\\input\{([^}]+)\}", t)
        included = "".join(
            (ROOT / "paper" / (i if i.endswith(".tex") else i + ".tex")).read_text()
            for i in inputs if (ROOT / "paper" / (i if i.endswith(".tex") else i + ".tex")).exists())
        labels = set(re.findall(r"\\label\{([^}]+)\}", t + included))
        refs = set(re.findall(r"\\(?:ref|Cref|cref|autoref|pageref)\{([^}]+)\}", t))
        refs = {r for group in refs for r in group.split(",")}
        dangling = sorted(refs - labels)
        if dangling:
            print(f"DANGLING {m}: {dangling}")
            ok = False
    if not ok:
        print("Nothing written.")
        return 1

    words = sum(len(texts[m].split()) - len(out[m].split()) for m in ("jair",))
    print(f"{len(props)} proposals, {len(edits['jair'])} JAIR edits, {len(edits['lncs'])} LNCS edits, JAIR words removed {words}")
    if not a.dry_run:
        JAIR.write_text(out["jair"])
        LNCS.write_text(out["lncs"])
        print("Written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
