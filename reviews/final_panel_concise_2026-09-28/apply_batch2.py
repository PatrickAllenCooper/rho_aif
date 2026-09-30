"""Batch 2 of the concise-manuscript panel (ledger 9.17.57).

Fixes the six defects and three polish items found by the batch-1 audit
(audit_batch1.md). Guarded exact replacements, identical in both masters.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MASTERS = [ROOT / "paper/full_paper_jair.tex", ROOT / "paper/full_paper.tex"]

EDITS = [
    ("D1a star convention, Inspection appendix",
     r"drives the lower threshold $w_{\mathrm{thresh}}$ downward (the proposition's $w^*_{\mathrm{thresh}}$, written without the star from Corollary~\ref{cor:pi4} onward), and",
     r"drives the lower threshold $w^*_{\mathrm{thresh}}$ downward, and", 1),
    ("D1b star convention scoped (main body, short)",
     r"We write $w_{\mathrm{thresh}}$ for the $w^*_{\mathrm{thresh}}$ of Proposition~\ref{prop:nearopt}, dropping the star to distinguish it from $w^*(B)$.",
     r"In this corollary and its onset checks, we write $w_{\mathrm{thresh}}$ for the $w^*_{\mathrm{thresh}}$ of Proposition~\ref{prop:nearopt}, dropping the star to distinguish it from $w^*(B)$.", 1),
    ("D2 scale transfer per PI-1",
     r"Section~\ref{sec:pi5} argued that an offline bracket is valid only at a known reward scale, so a deployed controller must re-adapt online after an unannounced rescale, and it left the speed of that re-adaptation to be measured.",
     r"Section~\ref{sec:pi5} noted that a reward-scale change moves the count-budget crossing. Proposition~\ref{prop:pi1} carries an offline bracket across a known reward-and-cost rescaling by multiplying it by the scale factor, but not across an unannounced one, so a deployed controller must then re-adapt online. That section left the speed of that re-adaptation to be measured.", 1),
    ("D3 root-level decomposition",
     r"The Planning+IG score decomposes each action's value into task value and weighted information gain, but nothing in the main results exposes that decomposition directly.",
     r"At the root of each decision, the Planning+IG score of an observation action is its weighted immediate information gain plus an expected task value that carries the sensing cost and the value of continuing, including any information bonuses deeper in the tree, but nothing in the main results exposes that decomposition directly.", 1),
    ("D4 Bandit prediction disclaimer",
     r"where the low reward asymmetry predicts only marginal $H{=}1$ sufficiency yet multi-step EFE performs well in practice.",
     r"where a one-step reading would lead one to expect the least from $w{=}1$ yet multi-step EFE performs well in practice. The two-state threshold formula does not apply to Bandit, so no threshold is computed for it.", 1),
    ("D5 sibling confirming",
     r"confirming that deeper planning is increasingly valuable as state spaces grow",
     r"consistent with deeper planning becoming more valuable as state spaces grow", 1),
    ("D6 unit consistency (main body)",
     r"while EFE achieves $69.4\%\pm1.0$.",
     r"while EFE achieves $69.4\% \pm 1.0$pp.", 1),
    ("Pa name dominating weight",
     r"$w{=}1$. There $w{=}1$ lies on the reward-maximizing plateau on Tiger and Diagnosis but is Pareto-dominated on Tileworld (Section~\ref{sec:pareto}).",
     r"$w{=}1$. Within that regime, $w{=}1$ lies on the reward-maximizing plateau on Tiger and Diagnosis but is Pareto-dominated by $w{=}20$ on Tileworld (Section~\ref{sec:pareto}).", 1),
    ("Pb Tileworld caption both appendices",
     r"reported in Table~\ref{tab:pomcp} and Appendix~\ref{app:pomcp}.",
     r"reported in Table~\ref{tab:pomcp} and Appendices~\ref{app:pomcp} and~\ref{app:interpretation}.", 1),
    ("Pc name the solver",
     r"Second, the frozen planning horizon handicapped it.",
     r"Second, the frozen planning horizon handicapped POMCP.", 1),
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
