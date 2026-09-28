# Independent evidence review, round 2

Reviewer: reviewer2, empirical/statistical claims and reproducibility.

## Verdict: ACCEPT — unqualified

All four conditions from my independent first review are closed in the actual revised files. I found no remaining empirical, statistical, citation-attribution, or reproducibility condition that requires a manuscript/code change or a new experiment. This vote follows direct inspection and verification of the working-tree diff against `c211422e82f9bc70150473f1a1ca910f3c74a314`, not the author's change summary or the other reviewer's vote.

The evidence was already reproducible in round 1. This revision correctly calibrates its presentation without changing the data or computations. The disclosed small-sample and fitted-envelope limitations remain limitations of the result, rather than undisclosed defects or prerequisites for another experimental campaign.

## Closure of required findings

- **E1, frontier inference:** Closed. The empirical section now states that reference support and mixture weights are fitted on the same held-out means and held fixed for the paired SE. It explicitly excludes support reselection, mixture-weight and cap-feasibility uncertainty, and multiplicity adjustment, and disclaims coverage for the population constrained frontier. Abstract and conclusion say “nominal pointwise” intervals, and the empirical paragraph calls them “nominal, pointwise plug-in summaries.” The three other intervals are described as including zero, avoiding an equivalence implication. The table caption states the same conditioning and omissions. Its producer contains that exact text, so rebuilding preserves the correction. The reference producer docstring describes the computation and the later interpretation clarification accurately. Shared body and conclusion changes appear in both masters.
- **E2, percentage scope:** Closed. The abstract's fifth-of-reference-reward claim now explicitly identifies Bandit's largest budget. It no longer gives a global percentage ceiling across positive and negative reference rewards. This is supported by 1.316 / 6.267 = 0.20999, independently verified in round 1. The body/conclusion retain their already correct Bandit scope.
- **E3, belief reporting:** Closed. README and the scoring module now describe what the log and Brier columns measure, and the EFE-only “correct belief reporter” claim is removed. The new numerical documentation matches the code: natural logarithm and default floor `eps=1e-12`. The related appendix correction usefully distinguishes overall terminal-belief quality from calibration alone, without inventing new measurements.
- **E4, measured versus expected reward:** Closed. Both masters now state that the population constrained optimum dominates the expected reward of a feasible policy. They attribute a negative estimated gap to sampling error on either side or approximation error in the reference. No empirical Monte Carlo reward is treated as a certified population bound.

The optional ambiguous antecedent in the staircase paragraph was also fixed by explicitly naming Bandit and Tileworld. I initially found three newly added prose-semicolon sites while checking the revision. Root corrected them in both masters and the caption producer and regenerated the table. I rechecked the actual files: no new unescaped prose semicolon remains in the changed manuscript/table lines. This is closed, not an outstanding condition.

## Checks against numerical or executable regressions

- `git diff c211422 -- results figures` is empty. The archived data and figures reviewed in round 1 have not changed.
- The entire generated frontier table is byte-for-byte unchanged after excluding its caption line. All numerical rows, uncertainty values, budget labels, and columns are preserved.
- Parsed Python ASTs for `experiments/run_frontier_reference_heldout.py` and `rho_aif/scoring.py` are identical to c211422 after removing only the module docstring. There is no execution change hidden in the documentation correction.
- The complete empirical Tiger rare-event passage is byte-identical in each master. The abstract and both conclusions still disclose the vulnerability of the two smaller Tiger-budget findings. No interval or percentage change erased that limitation.
- The 8-of-11 descriptive pointwise count, 0.123 maximum observed usage error, 19-of-25 complete bootstrap recoveries, minimum bootstrap agreement 0.789, and n=5/n=20 TOST conclusions therefore retain the independent recomputation and fresh replay support documented in my first review.
- I inspected the new controller proof and positivity assumption as changed text. They introduce no empirical-data claim or change to the experiment code, and they preserve the limitation to the stated stationary projected recursion. The other panel reviewer supplies the detailed formal audit. The checklist's proof-description edits agree with the actual direct proof.
- `git diff --check` passes.

## Triage of all 38 mechanical claim-check flags

The log contains 19 flags per master, duplicated across the two propagated passages. I checked all 19 unique instances against their actual producers/data, rather than assuming “no hard failures” settled them. All are benign resolution/derivation cases:

1. **0.789:** `results_price_bracket_stability.csv` records `frac_reported=0.789` at Inspection-N8 budget 14.0434666667. The checker attached the claim to the adjacent long-form counts CSV instead of the summary. Round 1 independently reproduced the complete count distribution as well.
2. **Bandit curve and bracket values (six flags):** `results_price_usage_curves.csv` records w=0.1389495494 with usage 6.192, w=0.7196856730 with usage 5.108, and w=1.6378937070 on that same 5.108 plateau. `results_price_shadow_curves.csv` records budget 5.87448 and bracket (1.6378937070, 3.7275937203]. These round to 0.139, 6.19, 0.72, 5.11, 1.64, and 3.73 exactly as printed. The checker again selected the nearby bootstrap-counts file.
3. **CPOMDP upper SE 0.39 and Diagnosis usage 9.785 (two flags):** The selected canonical Diagnosis reference row at lambda 0.05 in `results_cpomdp_frontier.csv` has reward SE 0.3943455901 and usage 9.7853333333. The baseline CSV's reference support string also records usage 9.785. The comparison paragraph's SE span is over the selected reference/policy comparisons, not over every point in the entire penalty sweep.
4. **Bandit target-mixture SE 0.19:** The gap-budget `best_target_mixture` row in `results_budget_frontier.csv` has reward 5.936 and reward SE 0.1935678176, giving 5.94 ± 0.19. The nearby held-out-reference CSV is not the family SE source.
5. **Budget-fraction labels (six repeated flags for 0.25/0.75):** These are protocol labels, recorded as `interior_0.25` and `interior_0.75` in `budget_kind`, not scalar numeric result cells. They agree with the predeclared `FRACTIONS` and the rows being discussed.
6. **Tiger success 0.994:** The canonical lambda-zero reference row in `results_cpomdp_frontier.csv` gives success 0.994. The checker had selected the held-out CSV; the sentence itself identifies the canonical stream.
7. **Tiger 0.66:** This is the stated reward-cost calculation, 110 × (1 − 0.994) = 0.6600000000, not a copied summary cell.
8. **Tiger 0.67:** Held-out reference reward 5.684 minus canonical reward 5.016 is 0.668, rounding to 0.67. Both source files are named in the passage.

These categories cover 1 + 6 + 2 + 1 + 6 + 1 + 1 + 1 = 19 flags, or 38 across both masters. None requires a numerical correction.

## Installation, availability, and build guidance

I inspected root's concrete logs in `/Users/pat/Documents/Codex/2026-09-17/plea/work/polish-2026-09-28/`, not just its success report. The initial editable-install failure is real: pip 21.2.4 rejected the pyproject-only editable package. `pip-upgrade-verified.log` records upgrade to 26.0.1, and `source-install-verified.log` records successful editable wheel build and installation of rho-aif 2.0.0. `dependency-check-verified.log` reports no broken requirements, `list-verified.log` lists all six advertised benchmark configurations, and `tiger-smoke-verified.log` completes the three-episode EFE run with finite reward and scoring metrics. The added README pip-upgrade command therefore closes a demonstrated reproducibility issue rather than adding an untested suggestion.

The README accurately distinguishes planned PyPI publication from the working clone/source-install path. The checklist's corresponding disclosure remains correct. AGENTS.md, CLAUDE.md, and the dated handoff now carry explicit dated corrections to the stale PyPI assertion. The new manuscript-build instructions run from `paper/`, use pdfLaTeX/Biber for JAIR and Tectonic for the long master, and correctly identify the generated PDF paths. The source-install smoke is on a clean environment with current compatible dependencies, not a claim of full historical bitwise reproduction under those new versions; the pinned environment remains documented separately.

I inspected the build logs available during this review: JAIR produces its 114-page PDF and the long master produces its PDF with the disclosed overfull-box warnings. The broad pytest job was still progressing at my last read, with no failures shown. Root owns completion of that routine verification. This report does not claim that an unfinished run passed. No executable implementation or result changed in this revision, and no outstanding scientific acceptance condition depends on inventing such a result.

## Reviewed-state identifiers

These content hashes identify the final inspected source after the semicolon fixes, while HEAD was still c211422:

- `paper/full_paper_jair.tex`: SHA-256 `189c500decb68c3f56197a7132af6e015559bf9ad39325b6efc2601c35889914`.
- `paper/full_paper.tex`: SHA-256 `fc5ac014ea9d07eeb5eaa3a7b61a998ed9c8e3ca3c5e438d0b4277df944fe918`.
- `paper/tables/budget_frontier.tex`: SHA-256 `27968b1666dbda2e9f8d9dbd79b5b749b52d3af1db8d958134c03944649f9b17`.

Confidence: high within the empirical/statistical/reproducibility lens. No required or optional follow-up is being imposed as a condition of this ACCEPT.
