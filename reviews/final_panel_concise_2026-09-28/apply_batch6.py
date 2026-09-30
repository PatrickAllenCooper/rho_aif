"""Batch 6 of the concise-manuscript panel (ledger 9.17.57).

Pat, 2026-09-29: the manuscript is unpublished, so it describes the methods
and results as they now stand, with no account of earlier defects, earlier
versions, or review history. Disclosures that are properties of the reported
analyses themselves (a comparison added after results were inspected, seeds
that are not blind for one pair) are kept, without review framing.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MASTERS = [ROOT / "paper/full_paper_jair.tex", ROOT / "paper/full_paper.tex"]

TT = r"\texttt{tests/\allowbreak test\_\allowbreak pomcp\_\allowbreak "

EDITS = [
    ("H1 dual-control main body",
     r"These measurements come from the corrected per-episode-seeded runner. The earlier runner left the rescaled environment unseeded and reported a ratio of $2.65$ with all decay-only seeds recovering. The correction preserves the qualitative advantage while revealing slower and incomplete recovery for decay-only.",
     r"These measurements come from the per-episode-seeded runner, which also seeds the environment constructed at the rescale. Decay-only recovers more slowly on every seed, and on one of the ten not within the window.", 1),
    ("H2 frontier appendix pointer",
     r"selection details, historical reference correction, and paired archives",
     r"selection details, reference construction, and paired archives", 1),
    ("H3a dual-control metric",
     r"Under the post-rescale-only metric, which corrects the straddling one,",
     r"Under the post-rescale-only metric, which excludes pre-rescale episodes from the window,", 1),
    ("H3b dual-control provenance",
     r"These numbers come from a rerun of the battery under per-episode seeding, after a review found that the environment constructed at the rescale had not been seeded (\texttt{results\_\allowbreak price\_\allowbreak dual\_\allowbreak multiseed\_\allowbreak metrics.csv}). The earlier run's headline ratio was $2.65$ with every decay-only seed recovering, so the correction moved the estimate in the direction of a larger advantage for reset-on-shift and a slower decay-only recovery that one seed did not complete inside the window, and it did not change the qualitative finding. The ratio",
     r"These numbers come from the battery under per-episode seeding, which covers the environment constructed at the rescale (\texttt{results\_\allowbreak price\_\allowbreak dual\_\allowbreak multiseed\_\allowbreak metrics.csv}). The ratio", 1),
    ("H4 dual-control pipeline",
     r"Under the corrected pipeline, reset-on-shift recovers",
     r"Under per-episode seeding, reset-on-shift recovers", 1),
    ("H5 CPOMDP reference history",
     r" We report the current resolution rather than tuning the grid to close the gap. An earlier version of this table read the reference by equal-usage interpolation between the two sampled points bracketing $B_{\mathrm{EFE}}$, clamped to the boundary value where $B_{\mathrm{EFE}}$ fell outside the sampled range, which is not the reference the constrained problem defines. That lookup put the Diagnosis reference at $-1.297$ (a gap of $-5.65\%$) and Bandit's at $6.313$ ($-0.11\%$), and it is kept in the CSV as a diagnostic column only.",
     r" We report the current resolution rather than tuning the grid to close the gap.", 1),
    ("H6a frontier added policies",
     r"Two further policies were added after the first results had been inspected, in response to a re-review, and are disclosed as such in the producer's docstring.",
     r"Two further policies were added after the first results had been inspected, and are disclosed as such in the producer's docstring.", 1),
    ("H6b frontier reference history",
     r" An earlier version of this comparison read the reference by linear interpolation between sampled points at equal usage and left it blank outside the sampled usage range, which omitted eight feasible comparators and interpolated through points below the envelope. That interpolation is kept in the CSV as a diagnostic column (\texttt{frontier\_\allowbreak interp\_\allowbreak at\_\allowbreak B}) and is no longer the comparator.",
     r"", 1),
    ("H7 same-stream comparison",
     r"A same-stream comparison, added after the results above had been inspected and in response to a referee, therefore",
     r"A same-stream comparison, added after the results above had been inspected, therefore", 1),
    ("H8 replication blindness",
     r"The referee check that prompted the replication had already evaluated that one Diagnosis pair on these seeds, so the seeds are not blind for it.",
     r"That one Diagnosis pair had been evaluated on these seeds before the replication was specified, so the seeds are not blind for it.", 1),
    ("H9 Tileworld partition",
     r"An earlier unseeded version of this experiment showed EFE nominally ahead of Planning on reward under the bitwise partition, and the seeded rerun reverses that reward ordering. That reversal is itself the clearest evidence that the nominal reward gaps here are sampling noise rather than signal.",
     r"The nominal reward gaps here are within sampling error and are not read as signal.", 1),
    ("H10 checklist seeding",
     r"That control includes the environment that the dual-control runner constructs at its mid-run reward rescale, which an earlier version of the runner had left unseeded (found in review, fixed, and the affected battery rerun, Section~\ref{sec:dual_multiseed}).",
     r"That control includes the environment that the dual-control runner constructs at its mid-run reward rescale (Section~\ref{sec:dual_multiseed}).", (1, 0)),  # checklist is JAIR-only
    ("H11 POMCP correction note",
     r"Correction, 2026-09-29: an earlier version of this planner added the observation cost to its simulated return instead of subtracting it, a subsidy of twice the cost per simulated observation, and started every rollout from the root belief, so an observation earned no credit in the rollout after it. Both are fixed (" + TT + r"cost\_\allowbreak sign.py}, " + TT + r"rollout\_\allowbreak belief.py}) and every POMCP result in this article was rerun, with EFE, Planning, and MCTS-EFE reproducing bit-identically. The corrected planner observes less. The earlier Bandit success lead and the earlier failure to distinguish tuned POMCP from MCTS-EFE on Tiger were artifacts of the subsidy and are withdrawn.",
     r"Tests check that simulated observations are charged their cost and that rollouts start from the path belief (" + TT + r"cost\_\allowbreak sign.py}, " + TT + r"rollout\_\allowbreak belief.py}).", 1),
    ("H12 main body selection rule",
     r"under a recorded rule, written after an earlier sweep had been inspected but before the corrected POMCP runs reported here.",
     r"under a rule recorded before the runs reported here.", 1),
    ("H13 appendix selection rule",
     r" The rule was written after an earlier, uncorrected sweep had been inspected, but before the corrected runs reported here, which it selected from unchanged.",
     r"", 1),
    ("H14 Appendix Y selection rule",
     r"under a rule recorded before the corrected runs reported here.",
     r"under a rule recorded before the runs reported here.", 1),
]


def main() -> int:
    texts = {p: p.read_text() for p in MASTERS}
    ok = True
    for i, p in enumerate(MASTERS):
        t = texts[p]
        for eid, old, new, n in EDITS:
            n = n[i] if isinstance(n, tuple) else n
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
    print(f"Applied {len(EDITS)} edits to both masters.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
