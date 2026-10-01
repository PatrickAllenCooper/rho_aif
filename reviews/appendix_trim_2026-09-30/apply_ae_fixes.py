"""Hostile-AE referee fixes that do not depend on new runs (R4, R5, R6, optional 1 and 2)."""
from pathlib import Path

EDITS = [
    # R4
    ("The Epistemic-only ablation commits immediately at chance-level success on all three core environments and Tileworld. Removing the pragmatic term therefore causes degenerate non-exploration in this implementation.",
     "The Epistemic-only ablation commits immediately at chance-level success on all three core environments and Tileworld. The units force this outcome, since in bits no observation there yields as much information as it costs."),
    # R5
    ("Larger state space therefore does not itself increase the value of information weighting.",
     "With this shared leaf rule, a larger state space therefore does not by itself increase the value of information weighting."),
    # R6
    ("Success favors larger weights throughout this sweep, with its maximum at the upper grid endpoint $200$ on all five environments.",
     "Success reaches its maximum at the upper grid endpoint $200$ on all five environments, although it dips from $w{=}0.5$ to $w{=}1$ on Bandit and Tileworld."),
    # optional 2 (Champion)
    ("The claim covers the recursive hidden-state-information formulation in \\citet{champion2024}'s taxonomy.",
     "The claim covers the information-gain and pragmatic-value formulation among the four that \\citet{champion2024} relate, evaluated recursively."),
    ("In \\citet{champion2024}'s taxonomy of EFE formulations this is the variant whose epistemic term is the expected information gain about the hidden state, evaluated recursively over belief trajectories.",
     "Among the four EFE formulations that \\citet{champion2024} relate, this is the information-gain and pragmatic-value form, with information gain about the hidden state evaluated recursively over belief trajectories."),
    # optional 1 (bracket overload)
    ("lies in the reward-maximizing tied bracket on three of five swept environments",
     "lies in the reward-maximizing tied run of sampled weights on three of five swept environments"),
]
for name in ("full_paper_jair.tex", "full_paper.tex"):
    p = Path("paper") / name
    t = p.read_text()
    for old, new in EDITS:
        n = t.count(old)
        assert n == 1, (name, old[:70], n)
        t = t.replace(old, new)
    p.write_text(t)
    print(name, "ok")
