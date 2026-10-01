"""Fixes from audit_trim_1.md (ledger 9.17.58), applied to both masters."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
E = [
    ("\\label{app:supp_figs}\n\n\\subsection{",
     "\\label{app:supp_figs}\n\nThese figures support the main text but are not needed to follow it.\n\n\\subsection{"),
    ("yet are near-optimal at some deeper horizon, a missed opportunity rather than a risk. No environment in this sample shows the opposite pattern, where $H{=}1$ predicts near-optimality and no deeper horizon delivers it.",
     "yet are near-optimal at some deeper horizon (the table's myopic underclaims), a missed opportunity rather than a risk. No environment in this sample is a myopic overclaim, where $H{=}1$ predicts near-optimality and no deeper horizon delivers it."),
    ("gives $69.4\\%$ for EFE and $1.4\\%$ for Planning. Planning, untuned Info Gain, and Epistemic-only take no scans and tie Myopic exactly (mechanism in Appendix~\\ref{app:tileworld_details}).",
     "gives $69.4\\%$ for EFE and $1.4\\%$ for Planning, gaps consistent with seed-to-seed variation. Planning, untuned Info Gain, and Epistemic-only take no scans and tie Myopic exactly, because a single noisy scan over 64 cells barely narrows the belief (Planning's depth-2 case in Appendix~\\ref{app:tileworld_details})."),
    ("Even there, $w{=}1$ lies on the reward-maximizing plateau",
     "Within that regime, $w{=}1$ lies on the reward-maximizing plateau"),
    ("and the gaps at $\\gamma \\geq 0.99$ are significant after Holm correction.",
     "and the Diagnosis and Bandit gaps at $\\gamma \\geq 0.99$ are significant after Holm correction."),
    ("over the same 12-point grid to this project's depth-3 tree search",
     "over the 12-point log-spaced grid of Appendix~\\ref{app:cpomdp_details} to this project's depth-3 tree search"),
    ("The standard intuition that the iterate instead stays in a step-size-dependent neighborhood of $w^*$, which would let the controller re-adapt after a shift, would require constant-step tracking arguments that we do not develop.",
     "The standard intuition is that the iterate instead stays in a step-size-dependent neighborhood of $w^*$, which would let the controller re-adapt after a shift, but making that precise requires constant-step tracking arguments that we do not develop."),
    ("\\url{tools/build_sarsop.sh} which applies", "\\url{tools/build_sarsop.sh}, which applies"),
    ("including the genuine POMCP at its tuned frozen configuration", "including POMCP at its tuned frozen configuration"),
    ("A genuine POMCP for RockSample is reported here (\\texttt{rho\\_\\allowbreak aif/\\allowbreak agents/\\allowbreak rocksample\\_\\allowbreak pomcp.py}). It builds a search tree",
     "The RockSample POMCP (\\texttt{rho\\_\\allowbreak aif/\\allowbreak agents/\\allowbreak rocksample\\_\\allowbreak pomcp.py}) builds a search tree"),
    ("POMCP is a genuine search-tree solver", "POMCP is a search-tree solver"),
]
ps = [ROOT / "paper/full_paper_jair.tex", ROOT / "paper/full_paper.tex"]
ts = [p.read_text() for p in ps]
for o, n in E:
    counts = [t.count(o) for t in ts]
    assert counts == [1, 1], (o[:60], counts)
for p, t in zip(ps, ts):
    for o, n in E:
        t = t.replace(o, n)
    p.write_text(t)
print(f"applied {len(E)} fixes")
