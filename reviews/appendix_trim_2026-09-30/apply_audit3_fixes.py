"""Fixes for audit_panel_batch.md (D1-D11, D13, D15) plus the post hoc usage-matched sensitivity.

Inline edits made before this script and recorded here for the record (already applied):
- apply_frontier_fixes.py sentence "it mixes the unpenalized policy with a subsidized one" was
  replaced by "its support includes a subsidized policy".
- The Diagnosis B=9.53 attribution sentence (Fable R1) was appended after "appears on both streams
  (Appendix~\\ref{app:frontier_details})." and is rewritten by D5 below.
- The reward-tied "bracket" -> "run" pass (eight phrasings, identical counts in both masters).
- The seed-set clause after "+0.11\\pm0.09$." in the frontier appendix (Opus re-review note 1).
- The main frontier table's tabcolsep 4pt -> 3pt.
"""
from pathlib import Path

BOTH = [
    # D1
    ("The final column of Table~\\ref{tab:budget_frontier_main} pairs",
     "The Cap gap column of Table~\\ref{tab:budget_frontier_main} pairs"),
    # D2
    ("(the last two columns of Table~\\ref{tab:budget_frontier},",
     "(the Same-stream reference and Paired gap columns of Table~\\ref{tab:budget_frontier},"),
    # D4
    ("so net observation reward stays negative while usage rises above the unpenalized level.",
     "so net observation reward stays negative. The larger subsidies raise held-out usage above the unpenalized level, to at most $7.17$ on Tiger, $16.58$ on Diagnosis, and $11.59$ on Bandit, while the smaller ones leave it unchanged or slightly lower."),
    # D5 + usage-matched qualifier in the main text
    ("Only Bandit's gap-budget shortfall, $-0.59$ held out and $-0.50$ fresh, appears on both streams (Appendix~\\ref{app:frontier_details}). Diagnosis's held-out shortfall at $B{=}9.53$ mostly pairs the $w{=}1$ usage-plateau policy with the unpenalized SARSOP policy at nearly equal usage, a pair that is equivalent within the margin on episode-matched streams (Section~\\ref{sec:sarsop}).",
     "Only Bandit's gap-budget shortfall, $-0.59$ held out and $-0.50$ fresh, appears on both streams, and its held-out interval just reaches zero when the reference is matched to the mixture's realized usage rather than to $B$ (Appendix~\\ref{app:frontier_details}). Diagnosis's held-out shortfall at $B{=}9.53$ mostly pairs a policy on the usage plateau containing $w{=}1$ with the unpenalized SARSOP policy at nearly equal usage. The twenty-seed episode-matched check of Section~\\ref{sec:sarsop} finds that pair equivalent within the margin, although on these five held-out seeds it differs by $1.01\\pm0.18$."),
    # D6
    ("a rare-event uncertainty the nominal intervals do not capture.",
     "a rare-event uncertainty the nominal intervals do not capture. If the reference erred at that rate while the family never did, the smallest-budget cap shortfall would reverse and the middle one would nearly vanish."),
    ("The plug-in intervals therefore support the aggregate shortfall count and the Tiger and Bandit rows, not the identity of the Diagnosis budgets that fall short.",
     "The plug-in intervals therefore support the aggregate shortfall count, Bandit's rows, and Tiger's largest-budget row, not the identity of the Diagnosis budgets that fall short."),
    # D7 + sensitivity in the appendix
    ("to $+0.08\\pm0.04$ (Tiger, $B{=}4.72$), and Diagnosis's largest target moves from $-1.10\\pm0.22$ against the cap reference to $-0.05\\pm0.16$.",
     "to $+0.08\\pm0.04$ (Tiger, $B{=}4.72$), and Diagnosis's largest target moves from $-1.10\\pm0.22$ against the cap reference to $-0.05\\pm0.16$. Because every Tiger policy here earns $10$ minus its usage, Tiger's target gaps equal the mixture's usage shortfall below $B$ and measure no reward efficiency. More generally, the mixture meets $B$ only within its usage error, which a target gap also carries. A post hoc sensitivity analysis, run without new episodes, refits the reference at each mixture's realized held-out usage instead (\\texttt{--usage-matched}, \\texttt{results\\_\\allowbreak budget\\_\\allowbreak frontier\\_\\allowbreak target\\_\\allowbreak reference\\_\\allowbreak usage\\_\\allowbreak matched.csv}). Every Tiger gap becomes zero, Diagnosis still falls short at $B{=}9.53$ on the held-out seeds and at $B{=}7.72$ on the fresh ones, and Bandit's gap-budget interval reaches $+0.001$ on the held-out seeds while still excluding zero on the fresh ones."),
    # D8
    ("Against the best sampled reference policy that meets the same target,",
     "Against the best mixture of sampled reference policies that meets the same target,"),
    ("or to the best sampled policy meeting the same target,",
     "or to the best sampled reference mixture meeting the same target,"),
    # D9
    ("the cap is slack and the reference is the unconstrained reward optimum.",
     "the cap is slack and the reference is the unpenalized SARSOP policy, the estimated unconstrained reward optimum."),
    # D15
    ("reseeds every episode so both policies face the same episodes.",
     "reseeds every episode so both policies face the same hidden states and, while their actions agree, the same observation draws."),
    # D13 (hand comment on the main table)
    ("%% experiments/run_budget_frontier.py and run_frontier_reference_heldout.py.",
     "%% experiments/run_budget_frontier.py, run_frontier_reference_heldout.py, and\n%% run_frontier_target_reference.py."),
]
JAIR_ONLY = [
    # D10
    ("and for its same-stream reference (\\texttt{results\\_\\allowbreak cpomdp\\_\\allowbreak frontier\\_\\allowbreak heldout.csv})",
     "and for its same-stream reference (\\texttt{results\\_\\allowbreak cpomdp\\_\\allowbreak frontier\\_\\allowbreak heldout.csv}), per-seed gaps of its fresh-seed replication and target-matched reference with the subsidized reference points behind them (\\texttt{results\\_\\allowbreak budget\\_\\allowbreak frontier\\_\\allowbreak fresh\\_\\allowbreak seed\\_\\allowbreak replication.csv}, \\texttt{results\\_\\allowbreak budget\\_\\allowbreak frontier\\_\\allowbreak target\\_\\allowbreak reference.csv}, \\texttt{results\\_\\allowbreak cpomdp\\_\\allowbreak frontier\\_\\allowbreak subsidy.csv}), per-seed means of the episode-matched SARSOP TOST (\\texttt{results\\_\\allowbreak tost\\_\\allowbreak sarsop\\_\\allowbreak episode\\_\\allowbreak paired\\_\\allowbreak per\\_\\allowbreak seed.csv})"),
    # D11
    ("seed the stream once per outer seed and let it continue across that seed's episodes, and the near-optimality horizon study",
     "seed the stream once per outer seed and let it continue across that seed's episodes, except that \\texttt{run\\_\\allowbreak tost\\_\\allowbreak sarsop.py --episode-seeding} seeds each episode at $10^4 s + i$, and the near-optimality horizon study"),
    ("are evaluated after calibration on the canonical five, the disjoint tuning seeds",
     "are evaluated after calibration on the canonical five, the fresh seeds $\\{12, \\dots, 21\\}$ at $100$ episodes/seed of the frontier replication and target-matched reference, the fifteen added seeds $\\{2000, \\dots, 2014\\}$ of the $n{=}20$ and episode-matched SARSOP checks, the disjoint tuning seeds"),
]
OTHER = {
    "README.md": [
        ("`python experiments/run_frontier_reference_heldout.py` (same-stream reference and paired gaps, the table's last two columns), then `python experiments/build_budget_frontier_table.py`",
         "`python experiments/run_frontier_reference_heldout.py` (same-stream reference and paired gaps, the Same-stream reference and Paired gap columns), then `python experiments/run_frontier_target_reference.py` (the Target reference and Target gap columns), then `python experiments/build_budget_frontier_table.py`"),
        ("| `python experiments/run_frontier_target_reference.py` |",
         "| `python experiments/run_frontier_target_reference.py` after the frontier and same-stream reference runs (`--usage-matched` then recomputes the post hoc realized-usage sensitivity from the committed archives, no episodes) |"),
    ],
    "ENVIRONMENT.md": [
        ("seed the stream once per outer seed and let it continue across that seed's episodes. The near-optimality",
         "seed the stream once per outer seed and let it continue across that seed's episodes, except that `run_tost_sarsop.py --episode-seeding` seeds each episode as `10^4 * seed + episode`. The near-optimality"),
        ("(SARSOP TOST at n=5 and n=20, budget frontier and its same-stream reference, multi-seed dual",
         "(SARSOP TOST at n=5, n=20, and episode-matched n=20, budget frontier with its same-stream,\nfresh-seed, and target-matched references, subsidized reference points, multi-seed dual"),
    ],
    "experiments/build_budget_frontier_table.py": [
        ('"%% Numbers produced by experiments/run_budget_frontier.py and experiments/run_frontier_reference_heldout.py"',
         '"%% Numbers produced by experiments/run_budget_frontier.py, experiments/run_frontier_reference_heldout.py, "\n                  "and experiments/run_frontier_target_reference.py"'),
    ],
}


def apply(path, edits):
    p = Path(path)
    t = p.read_text()
    for old, new in edits:
        n = t.count(old)
        assert n == 1, (path, old[:70], n)
        t = t.replace(old, new)
    p.write_text(t)
    print(path, "ok", len(edits))


apply("paper/full_paper_jair.tex", BOTH + JAIR_ONLY)
apply("paper/full_paper.tex", BOTH)
for path, edits in OTHER.items():
    apply(path, edits)
