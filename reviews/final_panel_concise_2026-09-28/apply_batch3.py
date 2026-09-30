"""Batch 3 of the concise-manuscript panel (ledger 9.17.57).

Grok round-2 optional wording items, all in appendices. Guarded exact
replacements, identical in both masters.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MASTERS = [ROOT / "paper/full_paper_jair.tex", ROOT / "paper/full_paper.tex"]

EDITS = [
    ("G1 count-budget bracket under PI-1",
     r"Proposition~\ref{prop:pi1} carries an offline bracket across a known reward-and-cost rescaling by multiplying it by the scale factor,",
     r"Proposition~\ref{prop:pi1} carries an offline count-budget bracket across a known reward-and-cost rescaling by multiplying it by the scale factor,", 1),
    ("G2 derives, not bounds",
     r"Proposition~\ref{prop:nearopt} bounds $w^*_{\mathrm{thresh}}$ at",
     r"Proposition~\ref{prop:nearopt} derives $w^*_{\mathrm{thresh}}$ at", 1),
    ("G3 split long sentence",
     r"At the root of each decision, the Planning+IG score of an observation action is its weighted immediate information gain plus an expected task value that carries the sensing cost and the value of continuing, including any information bonuses deeper in the tree, but nothing in the main results exposes that decomposition directly.",
     r"At the root of each decision, the Planning+IG score of an observation action is its weighted immediate information gain plus an expected task value. That task value carries the sensing cost and the value of continuing, including any information bonuses deeper in the tree. Nothing in the main results exposes this decomposition directly.", 1),
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
