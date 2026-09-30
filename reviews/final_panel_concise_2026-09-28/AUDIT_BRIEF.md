# Adversarial audit brief, batch 1 (ledger 9.17.57)

You are an adversarial auditor. A batch of edits was just applied to both manuscript masters in response to the editor referee's report. Batches like this historically carry defects at roughly one in four, so assume there are some and look for them.

Materials (repository root /Users/pat/code/rho_aif):
- `reviews/final_panel_concise_2026-09-28/batch1.diff`: the full diff against HEAD for `paper/full_paper_jair.tex` and `paper/full_paper.tex`.
- `reviews/final_panel_concise_2026-09-28/apply_batch1.py`: the replacement list with the reason for each edit (ids R1 to R16 plus a global rename of `w^*_{\mathrm{lo}}` to `w^*_{\mathrm{thresh}}` and `w^*_{\mathrm{hi}}` to `w^*_{\mathrm{over}}`).
- `reviews/final_panel_concise_2026-09-28/report_editor_clarity.md`: the referee report that motivated the batch.
- The current masters, the compiled `paper/full_paper_jair.pdf`, `results/*.csv`, and `experiments/*.py`.

For every edit, check:
1. Every new `\ref` target resolves to a location that actually contains the material the sentence says it contains (read the target section, do not trust the label name).
2. The new wording is true against the tex, CSVs, and code. In particular R9 (Tileworld Pareto-dominated, w=1 on the plateau for Tiger and Diagnosis, against `results/results_pareto_sweep.csv`), R12 (crossing threshold versus bracket per Definition PI-3), R13 (consistent with Section 4.6 and Proposition PI-1 on scale transfer), R14 and R15 (calibrated, not weakened into something false).
3. The rename: every renamed site means the Proposition 3.2 thresholds and not the crossing bracket (w_lo, w_hi] of Definition PI-3, no site of the bracket notation was renamed, no stray `w^*_{\mathrm{lo}}`/`hi` remains, and sentences that previously explained the mapping still read correctly now that it is gone.
4. Sentences around each deletion (R7, R8a, R11) still read correctly and nothing a later sentence depends on was removed.
5. Both masters received identical edits (the LNCS file may differ only in unrelated context).
6. Style: no semicolons in prose, no rhetorical emphasis, and the project vocabulary in AGENTS.md ("near-optimal/estimated", w not the Lagrange multiplier, and so on).
7. Anything else in the touched paragraphs that the edits made wrong or left stale.

Do NOT edit any file outside `reviews/final_panel_concise_2026-09-28/`. Write your findings to `reviews/final_panel_concise_2026-09-28/audit_batch1.md`: one entry per edit id with a verdict (OK / DEFECT) and evidence, then a numbered list of defects with an exact proposed replacement for each. Return the defect list and the report path.
