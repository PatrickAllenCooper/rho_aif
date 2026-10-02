"""Reassemble the October 1 polish from its frozen, reviewed input revision.

Only exact, occurrence-guarded prose/caption replacements are applied. No
experimental result, table body, figure, reference, or numerical value is edited.
"""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BASE = "748052634026b2a5cf9e0c9fef64975b0e6fd682"
MASTERS = ["paper/full_paper_jair.tex", "paper/full_paper.tex"]
sources = {}
changes = []


def read_json(name):
    return json.loads((HERE / name).read_text())


def replace(file, old, new, identifier):
    if file not in sources:
        sources[file] = subprocess.check_output(
            ["git", "show", f"{BASE}:{file}"], cwd=ROOT, text=True
        )
    count = sources[file].count(old)
    if count != 1:
        raise ValueError(f"{identifier}: {file}: expected one match, found {count}")
    sources[file] = sources[file].replace(old, new, 1)
    changes.append({"id": identifier, "file": file, "old": old, "new": new})


main = read_json("prose_main_proposals.json")
appendix = read_json("prose_appendix_proposals.json")
for proposal in main["proposals"] + appendix["proposals"]:
    new = proposal["new"]
    if proposal["id"] == "M12":
        # Name RockSample as the navigation example. Inspection also implements
        # navigation, as confirmed by the post-apply audit of its step method.
        new = (
            "We now estimate usage curves and shadow prices in the interleaved "
            "observe-act settings of Sections~\\ref{sec:rocksample} and~\\ref{sec:inspection}, "
            "where sensing and acting alternate within an episode. RockSample "
            "also exercises the navigation between observations admitted by "
            "Proposition~\\ref{prop:factored}. The observe-then-commit environments "
            "above cannot exercise that case because they separate observation "
            "from commitment by construction."
        )
    for file in proposal.get("files", MASTERS):
        replace(file, proposal["old"], new, proposal["id"])

for flag in main["separate_flags"]:
    if flag["id"] in {"F01", "F02", "F03"}:
        for file in MASTERS:
            replace(file, flag["old"], flag["proposed_new"], flag["id"])

for proposal in read_json("evidence_proposals.json"):
    if proposal["id"] == "E3":
        continue  # Same correction is already applied by PA16.
    for file in proposal["targets"]:
        replace(file, proposal["old"], proposal["new"], proposal["id"])

for finding in appendix["separate_source_consistency_findings"]:
    for proposal in finding["replacements"]:
        replace(proposal["file"], proposal["old"], proposal["new"], finding["id"])

for file in MASTERS:
    replace(
        file,
        "Planning+IG is also this article's instance of a construction that two "
        "lines of prior work share, namely POMDPs with information rewards "
        "(POMDP-IR) and $\\rho$-POMDPs with an information-gain reward "
        "\\citep{spaan2015,araya2010}. \\citet{satsangi2018} show that these two "
        "formulations are equivalent, so Planning+IG stands in for both.",
        "Planning+IG represents the explicit-information-reward approach "
        "associated with POMDPs with information rewards (POMDP-IR) and "
        "$\\rho$-POMDPs \\citep{spaan2015,araya2010}. \\citet{satsangi2018} "
        "establish equivalence between the two formulations for piecewise-linear "
        "convex belief rewards. We do not invoke that equivalence for "
        "Planning+IG's concave expected-IG reward.",
        "REFEREE-SATSANGI-SCOPE",
    )
    replace(
        file,
        "at every instance, so the information gain term drives checking behavior.",
        "at every instance.",
        "REFEREE-CHECKING-CAUSALITY",
    )
    replace(
        file,
        "They differ by a fixed conversion only when all sensing actions share a cost",
        "When all sensing actions share a cost, the two differ by a fixed conversion",
        "AUDIT-UNIT-CONVERSION",
    )
    replace(
        file,
        "On RS[11,11], every tree-search agent, including Planning at $w{=}0$, "
        "instead converges to the same low-activity policy, discussed in Section~\\ref{sec:rocksample}.",
        "On RS[11,11], all tree-search agents, including Planning at $w{=}0$, "
        "instead follow low-activity policies, discussed in Section~\\ref{sec:rocksample}.",
        "AUDIT-ROCKSAMPLE-POLICIES",
    )
    replace(
        file,
        "The ablation finds no detectable effect of either in-tree information gain "
        "or max-backup at five seeds after multiplicity correction.",
        "The ablation finds no detectable effect of either in-tree information gain "
        "or max-backup on success or reward at five seeds after multiplicity correction.",
        "AUDIT-ABLATION-METRICS",
    )
    replace(
        file,
        "\\let\\appendixsection\\section\n\\renewcommand{\\section}{\\FloatBarrier\\appendixsection}",
        "% Explicit appendix float barriers preserve the class's section command.",
        "BUILD-SECTION-COMMAND",
    )
    before, appendix_source = sources[file].split("\\appendix", 1)
    sections = appendix_source.count("\n\\section{")
    expected_sections = 26 if "_jair" in file else 25
    if sections != expected_sections:
        raise ValueError(f"Unexpected appendix section count in {file}: {sections}")
    appendix_source = appendix_source.replace("\n\\section{", "\n\\FloatBarrier\n\\section{")
    sources[file] = before + "\\appendix" + appendix_source
    changes.append({"id": "BUILD-APPENDIX-BARRIERS", "file": file, "sections": sections})

hashes = {}
for file, source in sources.items():
    (ROOT / file).write_text(source)
    hashes[file] = hashlib.sha256(source.encode()).hexdigest()

(HERE / "applied_changes.json").write_text(
    json.dumps({"baseline": BASE, "changes": changes, "sha256": hashes}, indent=2) + "\n"
)
print(f"Applied {len(changes)} guarded file replacements to {len(sources)} files.")
for file, digest in hashes.items():
    print(digest, file)
