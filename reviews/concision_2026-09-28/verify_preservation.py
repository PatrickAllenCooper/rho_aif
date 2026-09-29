"""Check source retention for this dated editorial pass, not scientific validity."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PAPER = ROOT / "paper"
LEGACY = PAPER / "legacy/2026-09-28_pre_concision"


def expanded(source, archived=False):
    def read_input(match):
        if archived:
            with zipfile.ZipFile(LEGACY / "rho_aif_jair_overleaf_2026-09-28.zip") as archive:
                return archive.read(match[1]).decode()
        path = PAPER / match[1]
        if not path.exists():
            path = ROOT / match[1]
        return path.read_text()
    return re.sub(r"\\input\{([^}]+)\}", read_input, source)


def citation_keys(source):
    return {key.strip() for match in re.findall(
        r"\\cite\w*\*?(?:\[[^\]]*\]){0,2}\{([^}]+)\}", source
    ) for key in match.split(",")}


def main():
    for name, expected in json.loads((LEGACY / "sha256.json").read_text()).items():
        assert sha256((LEGACY / name).read_bytes()).hexdigest() == expected, name
    results = {"legacy_hashes_unchanged": True, "masters": {}}
    for name in ["full_paper_jair", "full_paper"]:
        old = expanded((LEGACY / f"{name}.tex").read_text(), archived=True)
        new = expanded((PAPER / f"{name}.tex").read_text())
        old_labels = re.findall(r"\\label\{([^}]+)\}", old)
        labels = re.findall(r"\\label\{([^}]+)\}", new)
        references = re.findall(r"\\(?:eqref|ref)\{([^}]+)\}", new)
        # The math audit corrected this header's false implication that every
        # state-changing action has nonzero posterior divergence. Data survive.
        old = old.replace(
            r"\textbf{Factored} ($\Delta_T{=}0$) & \textbf{Non-factored} ($\Delta_T{\neq}0$)",
            r"\textbf{Preserves hidden state} & \textbf{May change hidden state}",
        )
        pattern = r"\\begin\{tabular\}.*?\\end\{tabular\}"
        old_tables = Counter(re.findall(pattern, old, re.S))
        new_tables = Counter(re.findall(pattern, new, re.S))
        result = {
            "labels": len(labels),
            "missing_labels": sorted(set(old_labels) - set(labels)),
            "duplicate_labels": [x for x, count in Counter(labels).items() if count > 1],
            "unresolved_references": sorted(set(references) - set(labels)),
            "citation_keys": len(citation_keys(new)),
            "missing_citation_keys": sorted(citation_keys(old) - citation_keys(new)),
            "missing_original_table_bodies_after_documented_header_fix": sum((old_tables-new_tables).values()),
            "main_figures": new.split(r"\appendix")[0].count(r"\begin{figure}"),
            "all_figures": new.count(r"\begin{figure}"),
        }
        for field in ["missing_labels", "duplicate_labels", "unresolved_references",
                      "missing_citation_keys", "missing_original_table_bodies_after_documented_header_fix"]:
            assert not result[field], (name, field, result[field])
        results["masters"][name] = result
    (HERE / "preservation_audit.json").write_text(json.dumps(results, indent=2) + "\n")
    print("PASS: frozen legacy hashes, labels, references, citation retention, and original table data.")


if __name__ == "__main__":
    main()
