"""Batch 7: the thirteen defects of audit_batch6.md (ledger 9.17.57)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MASTERS = [ROOT / "paper/full_paper_jair.tex", ROOT / "paper/full_paper.tex"]
RULE = "under a rule recorded before the runs reported here"
DISCLOSE = RULE + " and written after an exploratory sweep on the canonical seeds had been inspected"

EDITS = [
    ("D1", r"discusses these limitations and the diagnostic interpolation retained in the CSV.",
     r"discusses these limitations.", 1),
    ("D2", r"The CSVs regenerated under the relative comparison tolerance of Section~\ref{sec:pi1} are byte-identical to those generated under the earlier absolute tolerance, which did not bind at these points.",
     r"These CSVs are byte-identical under an absolute comparison tolerance in place of the relative one of Section~\ref{sec:pi1}, which does not bind at these points.", 1),
    ("D3", r"The collapse CSVs were regenerated under the relative comparison tolerance of Section~\ref{sec:pi1} and are byte-identical to those produced under the earlier absolute tolerance, which did not bind at any swept point.",
     r"The collapse CSVs are byte-identical under an absolute comparison tolerance in place of the relative one of Section~\ref{sec:pi1}, which does not bind at any swept point.", 1),
    ("D4", r"That conclusion now rests on a direct run", r"That conclusion rests on a direct run", 1),
    ("D5", r"It is not Thompson sampling, despite the preserved CSV label \texttt{ThompsonSamplingAgent}.",
     r"It is not Thompson sampling, although the committed CSVs label it \texttt{ThompsonSamplingAgent}.", 1),
    ("D6", r"record it under the legacy label \texttt{ThompsonSamplingAgent}, retained so the artifacts stay stable.",
     r"record it under the label \texttt{ThompsonSamplingAgent}.", 1),
    ("D7", r"every table and figure reporting experimental results in this version was produced under them.",
     r"every table and figure reporting experimental results in this article was produced under them.", (1, 0)),
    ("D8", r"one without any equivalence test, had already been reported, so the margin",
     r"one without any equivalence test, had been inspected, so the margin", 1),
    ("D9", r"The heuristic already in Table~\ref{tab:rocksample}, originally added for the POMCP comparison, settles",
     r"The heuristic already in Table~\ref{tab:rocksample}, POMCP's approach-then-check rollout rule run standalone, settles", 1),
    ("D10", r"The original POMCP comparisons use untuned exploration constants. A separate sweep selects constants on tuning seeds " + RULE + ".",
     r"The POMCP comparisons outside the exploration sweep use untuned exploration constants. A separate sweep selects constants on tuning seeds " + DISCLOSE + ".", 1),
    ("D11", RULE + ".", DISCLOSE + ".", 1),
    ("D12", r"Decay-only recovers more slowly on every seed, and on one of the ten not within the window.",
     r"Decay-only is slower than reset-on-shift on every seed, and on one of the ten it does not recover within the window.", 1),
    ("D13", r"had been inspected, and are disclosed as such in the producer's docstring.",
     r"had been inspected and are disclosed as such in the producer's docstring.", 1),
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
    print(f"Applied {len(EDITS)} edits.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
