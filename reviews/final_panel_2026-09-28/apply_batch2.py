#!/usr/bin/env python3
"""Second final-panel batch: verified optional items. Same exactly-once guard."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apply_batch import BOTH, JAIR, LNCS  # noqa: E402

EDITS = [
    ("fig15-description", (JAIR,),
     "showing the blue, orange, pink, and vermillion lines declining together from about 7 to about 4 as the penalty grows, with the pink Planning-plus-IG line dropping slightly below the others at the two largest penalties.}",
     "showing the blue Planning and vermillion EFE lines declining from about 7 to about 4.2 as the penalty grows, while the orange InfoGain-Tuned and pink Planning-plus-IG lines hold near 5.6 up to a penalty of about 50 and then decline with them, the pink line reaching about 4.2 at a penalty of 200, below the others there, and the orange line ending highest, near 4.6, at a penalty of 500.}"),
    ("fig18-caption", BOTH,
     "in panel (a) a marker terminates each series at its final plotted step. EFE commits at the right time. Planning+IG over-explores.}",
     "in panel (a) a marker terminates each series at its final plotted step. Panels (a) and (c) average, at each step, only the episodes still running at that step. Planning+IG uses the success-tuned weight selected as in Section~\\ref{sec:methodology}. EFE stops observing later than reward-only Planning and earlier than Planning+IG, whose survival curve lies at or above EFE's at every step (panel b).}"),
    ("fig17-illustrative", BOTH,
     "\\caption{Belief evolution within representative Diagnosis episodes",
     "\\caption{Belief evolution within one illustrative Diagnosis episode per agent, not chosen to be typical in length"),
    ("fig19-consistent", BOTH,
     "The near-optimality basin widens with horizon, confirming that multi-step planning amplifies the value of observation.",
     "The near-optimality basin widens with horizon, consistent with multi-step planning amplifying the value of observation."),
    ("k-gloss", BOTH,
     "Rescaling all rewards by a positive factor $k$ at fixed $w$",
     "Rescaling all rewards by a positive factor $k$ (the factor written $\\alpha$ in Proposition~\\ref{prop:pi1}) at fixed $w$"),
    ("checklist-per-seed", (JAIR,),
     "and per-seed usage and reward for every budget-frontier row (\\texttt{results\\_budget\\_frontier.csv}).",
     "per-seed usage and reward for every budget-frontier row (\\texttt{results\\_budget\\_frontier.csv}) and for its same-stream reference (\\texttt{results\\_cpomdp\\_frontier\\_heldout.csv}), and per-seed usage for the shadow-price staircase curves (\\texttt{results\\_price\\_usage\\_curves\\_per\\_seed.csv})."),
]


def main(dry: bool) -> None:
    texts = {p: p.read_text() for p in BOTH}
    errors = []
    for name, targets, old, new in EDITS:
        for p in targets:
            n = texts[p].count(old)
            if n != 1:
                errors.append(f"{name}: {p.name} has {n} matches")
                continue
            texts[p] = texts[p].replace(old, new)
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    if dry:
        print(f"dry run ok, {len(EDITS)} edits")
        return
    for p, t in texts.items():
        p.write_text(t)
    print(f"applied {len(EDITS)} edits")


if __name__ == "__main__":
    main(dry="--apply" not in sys.argv)
