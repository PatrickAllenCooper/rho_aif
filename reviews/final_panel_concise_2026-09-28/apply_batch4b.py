"""Batch 4b of the concise-manuscript panel (ledger 9.17.57).

Applies the five defects the batch 3-4 audit found in F2 and F3
(audit_batch1.md, "Batch 3-4 audit", D1 to D5).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MASTERS = [ROOT / "paper/full_paper_jair.tex", ROOT / "paper/full_paper.tex"]

EDITS = [
    ("D1 abstract",
     r"The count replicates on fresh seeds but individual Diagnosis rows do not,",
     r"The count replicates on fresh seeds but not every Diagnosis row does,", 1),
    ("D1 + D5b appendix",
     r"Diagnosis's rows do not replicate individually. Its $0.5$ shortfall of $-0.76$ becomes $+0.02 \pm 0.29$,",
     r"Diagnosis's rows replicate only in part. Its $0.75$ shortfall replicates at $-0.82 \pm 0.28$, but its $0.5$ paired gap of $-0.76$ becomes $+0.02 \pm 0.29$,", 1),
    ("D2 narrow gap-target interval",
     r"now excludes it at $-0.56 \pm 0.24$.",
     r"now excludes it at $-0.56 \pm 0.24$, and its gap target includes zero only narrowly, at $-0.46 \pm 0.20$.", 1),
    ("D3 attribution",
     r"A wrong diagnosis costs $60$, so a few rare errors move a five-seed mean, and the replication attributes the discrepancy to that seed-set variation.",
     r"A wrong diagnosis costs $60$ relative to a correct one, so a few errors can move a five-seed mean, and the replication is consistent with seed-set variation as the source of the discrepancy.", 1),
    ("D4 antecedent",
     r"A predeclared fresh-seed replication measures how far these intervals depend on the five held-out seeds",
     r"A predeclared fresh-seed replication measures how far the same-stream paired intervals above depend on the five held-out seeds", 1),
    ("D5 mixture weight",
     r"against a reference that is $0.91$ of the unpenalized SARSOP policy.",
     r"against a reference that plays the unpenalized SARSOP policy with probability $0.91$.", 1),
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
