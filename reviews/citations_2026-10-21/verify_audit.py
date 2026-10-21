"""Verify that the three independent audits cover every current citation use."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
BASE = "68a9c137c4529675b3fe097ccda351e464dc3afc"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


inventory = json.loads((OUT / "inventory.json").read_text())
expected = Counter(
    (entry["key"], use["file"], use["line"])
    for entry in inventory["entries"] for use in entry["uses"]
)
actual = Counter()
records = []
auditors = {}
for name in "abc":
    report = json.loads((OUT / f"{name}.json").read_text())
    subset = report["records"]
    assert len(subset) == 23
    for record in subset:
        assert record["primary_urls_checked"], record["key"]
        assert record["metadata_field_verdicts"], record["key"]
        assert record["authenticity_status"] in {"verified", "verified_real_work"}
        for use in record["manuscript_uses"]:
            actual[(record["key"], use["file"], use["line"])] += 1
        records.append({"key": record["key"], "audit": f"{name}.json",
                        "authenticity": record["authenticity_status"],
                        "uses": len(record["manuscript_uses"]),
                        "primary_urls": record["primary_urls_checked"]})
    auditors[name] = {"entries": len(subset),
                      "uses": sum(len(r["manuscript_uses"]) for r in subset)}
assert actual == expected, {"missing": list((expected - actual).elements()),
                            "extra": list((actual - expected).elements())}
assert len({r["key"] for r in records}) == 69
assert sum(actual.values()) == 111

bib = ROOT / "paper/full_paper_jair.bib"
assert sha(bib) == inventory["bibliography_sha256"]
bib_keys = set(re.findall(r"^@\w+\{([^,]+),", bib.read_text(), re.M))
assert bib_keys == {r["key"] for r in records}

cite = re.compile(r"\\cite\w*\*?(?:\[[^\]]*\]){0,2}\{([^}]+)\}")
current = Counter()
clusters = 0
for source in ["paper/full_paper_jair.tex", "paper/tables/rocksample_main.tex"]:
    for line_number, line in enumerate((ROOT / source).read_text().splitlines(), 1):
        line = re.sub(r"(?<!\\)%.*", "", line)
        for match in cite.finditer(line):
            clusters += 1
            for key in match[1].split(","):
                current[(key.strip(), source, line_number)] += 1
assert current == expected
assert clusters == 84

# Guard against an unrecorded edit after the independent reviews.
# Read the edit literals without executing the one-shot editing script.
import ast
module = ast.parse((OUT / "apply_attribution_edits.py").read_text())
edits = ast.literal_eval(next(node.value for node in module.body
                            if isinstance(node, ast.Assign)
                            and any(isinstance(t, ast.Name) and t.id == "EDITS"
                                    for t in node.targets)))
for name in ("full_paper_jair.tex", "full_paper.tex"):
    original = subprocess.check_output(["git", "show", f"{BASE}:paper/{name}"],
                                       cwd=ROOT, text=True)
    for before, after in edits:
        assert original.count(before) == 1
        original = original.replace(before, after)
    if name == "full_paper_jair.tex":
        old = " It is not part of the accepted version."
        assert original.count(old) == 1
        original = original.replace(old, "")
    assert original == (ROOT / "paper" / name).read_text()

result = {
    "date": "2026-10-21", "baseline_commit": BASE,
    "auditors": auditors, "entries": 69, "citation_clusters": clusters,
    "individual_citation_uses": sum(actual.values()),
    "missing_audit_entries_or_uses": [], "uncited_bibliography_entries": [],
    "bibliography_unchanged": True, "fabricated_references_found": 0,
    "mirrored_attribution_corrections": 3,
    "jair_only_unsupported_policy_sentences_removed": 1,
    "source_disagreements": [
        "schmidhuber1991: publisher pages 222–228 vs author HTML 222–227",
        "ghavamzadeh2015: publisher pages 359–483 vs arXiv journal-ref 359–492",
        "houthooft2016: duplicate author on landing page; official PDF matches bibliography",
    ],
    "bounded_verification_limits": [
        "Blum primary full text inaccessible; identity and metadata verified",
        "Altman complete book theorem hypotheses not freshly reread; author record/contents checked",
        "Howard original scan read on third-party host; publisher metadata separately verified",
        "Lindley content checked by root in primary Russian translation; English original blocked",
    ],
    "hashes": {str(p.relative_to(ROOT)): sha(p) for p in [
        ROOT / "paper/full_paper_jair.tex", ROOT / "paper/full_paper.tex", bib,
        ROOT / "paper/full_paper_jair.pdf", ROOT / "paper/full_paper.pdf",
        ROOT / "paper/rho_aif_jair_overleaf_2026-10-21.zip"]},
    "records": sorted(records, key=lambda r: r["key"]),
}
(OUT / "coverage.json").write_text(json.dumps(result, indent=2) + "\n")
print("PASS: 69 references, 84 citation clusters, 111 uses; complete audit coverage.")
print("Only three mirrored attribution edits and one JAIR-only policy deletion.")
