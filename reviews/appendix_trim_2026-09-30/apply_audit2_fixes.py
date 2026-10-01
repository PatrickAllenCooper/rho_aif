"""Fixes from audit_trim_2.md (ledger 9.17.58), applied to both masters."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
E = [
    ("the UCB1 tree search defined in Appendix~\\ref{app:interpretation}, where its simulation-matched Tiger comparison against POMCP is reported. Exact EFE reaches",
     "the UCB1 tree search defined in Appendix~\\ref{app:interpretation}, which uses EFE as the leaf heuristic rather than random rollouts, and whose simulation-matched Tiger comparison against POMCP is reported there. As a reference point, exact EFE reaches"),
    ("The two solvers differ in more than the leaf, so", "MCTS-EFE and POMCP differ in more than the leaf, so"),
    ("so $w{=}1$ is near-optimal for reward on three of them, not for success rate,",
     "so $w{=}1$, although near-optimal for reward on three of them, is not near-optimal for success rate,"),
    ("from at most $0.5$ on Testbed to $20$ on Tileworld, the grid search that the derived weight replaces on the three environments where it attains the swept reward maximum.",
     "from at most $0.5$ on Testbed to $20$ on Tileworld. On the three environments where it attains the swept reward maximum, the derived weight replaces that grid search."),
    ("and $w{=}1$ is tuned to neither the reward criterion $w^*_{\\text{ret}}$ nor the success criterion $w^*_{\\text{succ}}$ used for Planning+IG in the main tables.",
     "and $w{=}1$ is tuned to neither criterion, unlike the reward-maximizing weight $w^*_{\\text{ret}}$ or the success-maximizing weight $w^*_{\\text{succ}}$ ($10$ to $50$) used for Planning+IG in the main tables."),
    ("sits just below the family's usage floor of $4.37$ (within one seed-level SE, Table~\\ref{tab:collapse-breadth})",
     "sits just below the Planning+IG usage curve's floor of $4.37$ (within one seed-level SE, Table~\\ref{tab:w-atlas})"),
    ("Diagnosis at $B{=}11.35$ and Bandit at $B{=}5.51$ also lie above",
     "Like Bandit's two larger interior budgets, Diagnosis at $B{=}11.35$ and Bandit at $B{=}5.51$ lie above"),
    ("On RS[7,8], the heavier weight's extra checking", "On RS[7,8], $w{=}10$'s extra checking"),
    ("with $w{=}10$ falling to $+20.55$ on RS[7,8] ($p{=}0.003$)",
     "with $w{=}10$ falling to $+20.55$ on RS[7,8] ($p{=}0.003$, significant under the per-metric Holm family)"),
    ("(Section~\\ref{sec:methodology}), so this identifies the best of three sampled weights",
     "(Section~\\ref{sec:methodology}), so on RS[7,8], where $w{=}5$ attains the highest reward of the three weights we ran and is not significantly different from $w{=}1$, this identifies the best of three sampled weights"),
    ("so a negative estimated gap reflects sampling or approximation error rather than",
     "so a negative estimated gap can reflect sampling error on either side or approximation error in the reference rather than"),
    ("A constrained POMDP is solved for the best reward", "A constrained POMDP is a POMDP solved for the best reward"),
    ("$w^*_{\\mathrm{succ}}$. They ask whether EFE's", "$w^*_{\\mathrm{succ}}$. Together they test whether EFE's"),
    ("The figure's two weighted series are not tuned", "Figure~\\ref{fig:tw_scaling}'s two weighted series are not tuned"),
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
