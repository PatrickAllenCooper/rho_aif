"""Guarded, mirrored attribution corrections from the fresh citation audit."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EDITS = [
    (
        r"Information-directed sampling (IDS) trades instantaneous regret against information gain through their ratio, rather than through a fixed additive coefficient \citep{russo2014}.",
        r"Information-directed sampling (IDS) selects an action distribution to minimize the ratio of squared expected one-period regret to expected information gain about the optimal action \citep{russo2014}.",
    ),
    (
        r"\citet{oudeyer2007} survey these intrinsic signals.",
        r"\citet{oudeyer2007} provide an earlier typology of computational intrinsic motivation.",
    ),
    (
        r"Resource-price adaptation is classical in constrained MDPs \citep{altman1999}, rational inattention \citep{sims2003,matejka2015}, and SAC \citep{haarnoja2018sac}.",
        r"Information prices and resource constraints are classical in constrained MDPs \citep{altman1999}, rational inattention \citep{sims2003,matejka2015}, and SAC \citep{haarnoja2018sac}.",
    ),
]

for name in ("full_paper_jair.tex", "full_paper.tex"):
    path = ROOT / "paper" / name
    text = path.read_text()
    for before, after in EDITS:
        assert text.count(before) == 1, (name, before, text.count(before))
        text = text.replace(before, after)
    path.write_text(text)
    print(f"{name}: {len(EDITS)} attribution corrections applied")

# The checklist is unique to the JAIR master. Retain its verified review
# purpose without making an unverified claim about a future accepted version.
path = ROOT / "paper/full_paper_jair.tex"
text = path.read_text()
before = r"This appendix answers the JAIR reproducibility checklist \citep{gundersen2024jair} for the submission version of this article, as required for review. It is not part of the accepted version."
after = r"This appendix answers the JAIR reproducibility checklist \citep{gundersen2024jair} for the submission version of this article, as required for review."
assert text.count(before) == 1
path.write_text(text.replace(before, after))
print("full_paper_jair.tex: unsupported accepted-version policy sentence removed")
