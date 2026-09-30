"""Batch 4 of the concise-manuscript panel (ledger 9.17.57).

Fable required change 2: the Diagnosis same-stream frontier rows depend on
the five held-out seeds. Reports the predeclared fresh-seed replication
(results_budget_frontier_fresh_seed_replication.csv) in the main body at
near-zero net length and in full in Appendix W.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MASTERS = [ROOT / "paper/full_paper_jair.tex", ROOT / "paper/full_paper.tex"]

APPENDIX_PARA = (
    r"A predeclared fresh-seed replication measures how far these intervals depend on the five held-out seeds "
    r"(\texttt{experiments/\allowbreak run\_\allowbreak frontier\_\allowbreak fresh\_\allowbreak seed\_\allowbreak replication.py}, "
    r"\texttt{results\_\allowbreak budget\_\allowbreak frontier\_\allowbreak fresh\_\allowbreak seed\_\allowbreak replication.csv}). "
    r"It first replays all twelve held-out paired gaps to $10^{-9}$, then keeps every committed mixture and reference support fixed "
    r"and re-evaluates both on seeds $12$ to $21$, $100$ episodes per seed, with intervals on $9$ degrees of freedom. "
    r"The count replicates. Intervals exclude zero at nine of the twelve rows, again eight of the eleven distinct budgets, "
    r"and eleven of the twelve paired means are negative. Tiger's three shortfalls and Bandit's three shortfalls replicate, "
    r"and Bandit's smallest target again includes zero. The Tiger rare-event qualification above still applies. "
    r"Diagnosis's rows do not replicate individually. Its $0.5$ shortfall of $-0.76$ becomes $+0.02 \pm 0.29$, "
    r"while its smallest target, which included zero on the held-out seeds, now excludes it at $-0.56 \pm 0.24$. "
    r"The $0.5$ mixture plays $w{=}0.316$ with probability $0.94$, on a calibration plateau from $w{=}0.316$ to $19.3$ "
    r"that contains $w{=}1$, against a reference that is $0.91$ of the unpenalized SARSOP policy. "
    r"Its held-out shortfall therefore sat uneasily with the $n{=}20$ equivalence of $w{=}1$ and that policy in "
    r"Section~\ref{sec:sarsop}. A wrong diagnosis costs $60$, so a few rare errors move a five-seed mean, and the "
    r"replication attributes the discrepancy to that seed-set variation. The referee check that prompted the replication "
    r"had already evaluated that one Diagnosis pair on these seeds, so the seeds are not blind for it. "
    r"The plug-in intervals therefore support the aggregate shortfall count and the Tiger and Bandit rows, "
    r"not the identity of the Diagnosis budgets that fall short."
)

EDITS = [
    ("F1 main body, net-neutral replacement",
     r"Three intervals include zero, at Diagnosis's smallest and gap targets and Bandit's smallest target.",
     r"A predeclared replication on ten fresh seeds again excludes zero at eight of eleven distinct budgets, but changes which Diagnosis budgets fall short (Appendix~\ref{app:frontier_details}).", 1),
    ("F2 abstract, near length-neutral",
     r"These intervals omit reference-selection uncertainty, and two Tiger comparisons are sensitive to rare errors absent from the held-out episodes.",
     r"These intervals omit reference-selection uncertainty. The count replicates on fresh seeds but individual Diagnosis rows do not, and two Tiger comparisons are sensitive to rare errors.", 1),
    ("F3 appendix paragraph before the frontier table",
     "\n\n\\input{tables/budget_frontier.tex}\n",
     "\n\n" + APPENDIX_PARA + "\n\n\\input{tables/budget_frontier.tex}\n", 1),
]


def main() -> int:
    texts = {p: p.read_text() for p in MASTERS}
    ok = True
    for p in MASTERS:
        t = texts[p]
        for eid, old, new, n in EDITS:
            c = t.count(old)
            if c != n:
                print(f"FAIL {p.name} {eid}: found {c}, expected {n}")
                ok = False
                continue
            t = t.replace(old, new)
        texts[p] = t
    if not ok:
        print("Nothing written.")
        return 1
    for p, t in texts.items():
        p.write_text(t)
    print("Applied to both masters.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
