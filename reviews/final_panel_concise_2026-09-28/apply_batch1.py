"""Batch 1 of the concise-manuscript panel (ledger 9.17.57).

Guarded exact replacements, applied identically to both masters. Each entry
must match exactly the stated number of times in each file or nothing is
written. All edits are in appendices except R10 (main body, shorter).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MASTERS = [ROOT / "paper/full_paper_jair.tex", ROOT / "paper/full_paper.tex"]

# (id, old, new, expected count per file)
EDITS = [
    ("R1 stale ref Bandit",
     r"This is the same trend reported for Bandit in Section~\ref{sec:discussion}, where",
     r"This is the same trend reported for Bandit in Appendix~\ref{app:interpretation}, where", 1),
    ("R2 stale ref audit motivation",
     r"Section~\ref{sec:discussion} argues that the epistemic value term supports interpretable decisions, but nothing in the main results exposes that decomposition directly.",
     r"The Planning+IG score decomposes each action's value into task value and weighted information gain, but nothing in the main results exposes that decomposition directly.", 1),
    ("R3 above->below",
     r"the same distinction drawn for the MCTS-EFE comparison above.",
     r"the same distinction drawn for the MCTS-EFE comparison below.", 1),
    ("R4 stale ref MCTS-EFE design",
     r"we implement MCTS-EFE, the UCB1 tree search of Section~\ref{sec:discussion}, which",
     r"we implement MCTS-EFE, the UCB1 tree search of Appendix~\ref{app:interpretation}, which", 1),
    ("R5 stale ref Tileworld caption",
     r"reported in Table~\ref{tab:pomcp} and Section~\ref{sec:discussion}.",
     r"reported in Table~\ref{tab:pomcp} and Appendix~\ref{app:pomcp}.", 1),
    ("R6 stale ref IDS numerator",
     r"That numerator is the squared expected regret of taking the observation action (Section~\ref{sec:methodology}).",
     r"That numerator is the squared expected regret of taking the observation action (Appendix~\ref{app:theory_agents}).", 1),
    ("R7 leftover main-body transition",
     r" With the family's operating points recorded, the EFE benchmark battery (Section~\ref{sec:results}) follows. The Discussion after it draws the results together, beginning with the reward convention on which every claim about $w{=}1$ rests.",
     "", 1),
    ("R8a delete mapping sentence",
     r" The table writes Part (a)'s $w^*_{\mathrm{thresh}}$ as $w^*_{\mathrm{lo}}$ and Part (b)'s $w^*_{\mathrm{over}}$ as $w^*_{\mathrm{hi}}$.",
     "", 1),
    ("R8b interpretation mapping",
     r"written $w^*_{\mathrm{lo}}$ and $w^*_{\mathrm{hi}}$ in Table~\ref{tab:alpha_eta}. The lower threshold $w^*_{\mathrm{lo}}$ (the proposition's $w^*_{\mathrm{thresh}}$) is",
     r"written $w^*_{\mathrm{thresh}}$ and $w^*_{\mathrm{over}}$ there and in Table~\ref{tab:alpha_eta}. The lower threshold $w^*_{\mathrm{thresh}}$ is", 1),
    ("R8c interpretation mapping upper",
     r"The upper threshold $w^*_{\mathrm{hi}}$ (the proposition's $w^*_{\mathrm{over}}$) is",
     r"The upper threshold $w^*_{\mathrm{over}}$ is", 1),
    ("R9 Tileworld overgeneralization",
     r"precisely the regime where $w{=}1$ is well-calibrated (Tiger, Diagnosis).",
     r"the regime in which the two-state interval analysis is most favorable to $w{=}1$. There $w{=}1$ lies on the reward-maximizing plateau on Tiger and Diagnosis but is Pareto-dominated on Tileworld (Section~\ref{sec:pareto}).", 1),
    ("R10 pp unit (main body, shorter)",
     r"achieves $1.4\%\pm0.3$ percentage points success,",
     r"achieves $1.4\% \pm 0.3$pp success,", 1),
    ("R11 informal aside",
     r"Second, the frozen planning horizon handicapped it, and we say so because we measured it rather than because a referee asked.",
     r"Second, the frozen planning horizon handicapped it.", 1),
    ("R12 price vs bracket",
     r"reading it off a sensing budget as the bracket of adjacent grid weights between which",
     r"reading it off a sensing budget as the crossing threshold $w^*(B)$, estimated by the bracket of adjacent grid weights between which", 1),
    ("R13 scale transfer consistency",
     r"an offline bracket is valid only at the reward scale it was solved at, so a deployed controller must re-adapt online after an unannounced rescale",
     r"an offline bracket is valid only at a known reward scale, so a deployed controller must re-adapt online after an unannounced rescale", 1),
    ("R14 discount threshold scope",
     r"On environments with several observation actions EFE's advantage requires $\gamma \geq 0.99$, because heavier discounting truncates the effective horizon.",
     r"In this benchmark sweep, EFE's advantage on environments with several observation actions appeared only at $\gamma \geq 0.99$, consistent with heavier discounting truncating the effective horizon.", 1),
    ("R15 confirming overclaim",
     r"confirming that EFE's advantage requires sufficient recursive depth, not merely a larger state space",
     r"consistent with EFE's advantage depending on recursive depth, not merely on a larger state space", 1),
    ("R16 duplicate atlas heading",
     "\\subsection{The $w^*$ Atlas}\n\\label{sec:w_atlas}",
     "\\subsection{Where the Benchmarks Sit on Their Usage Curves}\n\\label{sec:w_atlas}", 1),
]

# Global symbol rename, applied after the targeted edits above.
RENAMES = [
    (r"w^*_{\mathrm{lo}}", r"w^*_{\mathrm{thresh}}"),
    (r"w^*_{\mathrm{hi}}", r"w^*_{\mathrm{over}}"),
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
        for old, new in RENAMES:
            print(f"{p.name}: rename {old} x{t.count(old)}")
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
