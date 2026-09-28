# Adversarial audit of the complete 2026-09-28 edit batch

Repository: /Users/pat/code/rho_aif. Do not edit any file except your report.

`reviews/final_panel_2026-09-28/batch_full_jair.diff` is the full uncommitted diff of
`paper/full_paper_jair.tex` against HEAD (every edit made in response to this referee panel). An
earlier audit already checked the first half. Audit ALL of it again, with particular attention to the
edits made after that audit:

- the scale-equivariance paragraph after Proposition PI-1 ("Second, the shadow price and its bracket rescale together..."),
- the cost-budget prose, Figure caption, and Description ("has crossing bracket (10, 31.6]"),
- the new sentences on the cost-per-test step ("On the swept grid the shift is a step..."),
- the Table 6 caption (weights inside a constant run of the usage curve that straddles w=1),
- Proposition PI-5's running-average statement and proof additions (Kronecker's lemma, n a_n limit, projection non-expansiveness and Blum's argument),
- the gloss "the weight at which the family's sensing passes from below B to at or above it",
- the new bracket-stability paragraph (seed bootstrap, 2000 resamples, 25 budgets, 19 and 21 counts, 0.789, neighbouring-step claim, Tiger ends "about one standard error"),
- the checklist addition.

For every changed sentence, check it against the artifacts it depends on: `results/*.csv` (notably
`results_price_bracket_stability.csv`, `results_price_usage_curves.csv`,
`results_price_usage_curves_per_seed.csv`, `results_price_shadow_curves.csv`,
`results_price_cost_curves.csv`, `results_price_cost_prices.csv`, `results_budget_frontier*.csv`,
`results_cpomdp_frontier_heldout.csv`), the producer code (`experiments/run_bracket_stability.py`,
`experiments/run_price_of_information.py`, `experiments/run_frontier_reference_heldout.py`,
`rho_aif/budget.py`), and Definition PI-3 as written in the manuscript. Recompute numbers yourself
(the repo has `.venv`; `source .venv/bin/activate`). Check mathematics for correctness, notation for
consistency with the paper's convention (w*(B) is the crossing threshold w-dagger(B), the bracket
(w_lo, w_hi] is its grid estimate, hat-w(B) the grid point), and prose style: no semicolons outside
math, no rhetorical italics or bold, "near-optimal/estimated" never "exact" for SARSOP/CPOMDP
references, w never called the Lagrange multiplier.

Also verify that `paper/full_paper.tex` received the same prose edits (the LNCS master has no
checklist and no Description blocks, so those are JAIR-only).

Write `reviews/final_panel_2026-09-28/audit2_report.md` listing each DEFECT with severity (BLOCKING,
MINOR), the exact current text, the evidence, and exact replacement text. Then list what you checked
and found correct. Reply with the defect count and the report path.
