# Adversarial audit brief, final-panel edit batch (2026-09-28)

A four-referee JAIR panel (Gemini, Grok, Fable, Sol) reviewed the manuscript at HEAD `9e2666d`. Their reports are in this directory (`report_*.md`). The orchestrator verified the items and applied an edit batch to both live masters (`paper/full_paper_jair.tex`, `paper/full_paper.tex`), a table producer, a figure producer, two docstrings, README, ENVIRONMENT, and the ledger. Two new experiments were run:

- `experiments/run_frontier_reference_heldout.py` -> `results/results_cpomdp_frontier_heldout.csv`, `results/results_budget_frontier_heldout_reference.csv` (re-evaluates the saved SARSOP-Lagrangian policies on the held-out stream and computes paired same-stream gaps). These feed two new columns of `paper/tables/budget_frontier.tex` via `experiments/build_budget_frontier_table.py`.
- `experiments/run_bracket_stability.py` (still running, NOT part of this audit; ignore `results_price_usage_curves_per_seed.csv` and the bracket-stability paragraph if absent).

The edit scripts are `apply_batch.py` and `apply_batch2.py` in this directory. See the full change with `git diff` (working tree against HEAD) from the repo root `/Users/pat/code/rho_aif`.

History: every applied batch in this project has carried defects at roughly one in four. Your job is to find them. Do not trust the change descriptions. Check each changed sentence against the code, the CSVs, the figures, and the surrounding text.

## Rules

- Read-only on everything except your own report file. No commits, checkouts, stashes, or edits to the manuscripts, code, or results.
- You may run read-only Python (`source .venv/bin/activate`) to recompute numbers from the CSVs.
- Project conventions: no semicolons in prose, no rhetorical italics or bold, SARSOP and CPOMDP references are "near-optimal" or "estimated" never "exact", w is not the Lagrange multiplier of the usage cap, Prop PI-5 gives stationary convergence plus empirical re-adaptation (never a tracking guarantee), shadow prices are reported as brackets. Every prose change must be identical in both masters, except the JAIR-only abstract, checklist, and `\Description` blocks.

## Report

Write `audit_<your_lens>.md` in this directory: a numbered list of defects, each with file, line, verbatim quote (at most 30 words), what is wrong, evidence, and the exact fix, each marked BLOCKING or MINOR. Then a list of every changed passage you checked and found correct. Return to the orchestrator the full defect list and the report path. If you find nothing wrong, say so plainly. Do not pad.
