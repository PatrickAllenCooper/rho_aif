# Statistics and Reproducibility Review, Round 2

## Recommendation

**Accept with minor revisions.**

## Summary

The revision resolves three of my four required changes completely and resolves the fourth for the core batteries but not yet for the reported \(n=20\) TOST robustness study. The TOST chronology is now candid, the main tuned baselines' single-stream selection protocol is fully disclosed, and the new seed-bootstrap experiment directly measures crossing-bracket selection stability. I reran that bootstrap from the archived per-seed curves and independently inspected all bootstrap category counts. The saved output, manuscript totals, and qualitative description agree exactly. The Holm family-size clarification is also correct. The only remaining required correction is narrow: README and `ENVIRONMENT.md` still imply that the SARSOP TOST battery's tests can all be recomputed from archived per-seed metrics, while the \(n=20\) test reported in the manuscript has no committed per-seed file or reproduction command.

## Strengths

- The revised TOST paragraph precisely distinguishes the retrospective five-seed analysis from the prospectively fixed fifteen additional seeds.
- The bracket-stability producer preserves common random numbers by resampling seed indices jointly across all weights, reuses the manuscript's exact crossing solver, and aborts unless both curve means and reported brackets reproduce.
- The per-seed usage archive reproduces every committed staircase mean to a maximum absolute difference of \(1.78\times10^{-15}\).
- The 2,000-resample bootstrap is deterministic under its recorded RNG seed and reproduces the committed stability CSV exactly.
- The manuscript reports the bootstrap's weaker rows rather than only its stable majority, including Inspection-\(N=8\)'s \(0.789\) agreement and Tiger's unbracketed resamples.
- The main tuning protocol now states the candidate grid, one common seed-7 stream, candidate-stream reset, smallest-weight tie rule, disjoint evaluation seeds, and the resulting sampling-noise limitation.
- README and `ENVIRONMENT.md` now accurately distinguish raw per-seed archives from artifacts containing only aggregates, seed-level SEs, and computed tests for most batteries.
- The revised Holm paragraph correctly gives 107 defined tests for Tiger, 83 for Diagnosis, and all 84 for Bandit.

## Required changes

1. **Archive or explicitly exclude the \(n=20\) TOST per-seed inputs from the recomputability claim.**  
   **Location:** Section 6.7, line 709: “We reran the identical procedure at \(n{=}20\) seeds, fixed before running rather than added post hoc...”  
   **Problem:** `README.md`, line 131, and `ENVIRONMENT.md`, lines 23--29, now say that per-seed metrics are committed for the “SARSOP TOST comparison” and that tests on that battery can be recomputed without rerunning episodes. This is true for the canonical five-seed test (`results_tost_sarsop_per_seed.csv`) but false for the \(n=20\) robustness test reported in the quoted manuscript sentence. `results_tost_sarsop_n20_robustness.csv` contains only means, SE, degrees of freedom, \(p\)-values, and confidence limits. No corresponding \(n=20\) per-seed CSV exists, and the README command runs the five default seeds only. The revised producer now automatically writes a companion `_per_seed.csv` for any `--out`, so the missing artifact is straightforward to generate.  
   **Concrete fix:** Rerun the recorded seed set \(\{42,123,456,789,1024,2000,\ldots,2014\}\) with `--out results/results_tost_sarsop_n20_robustness.csv`, commit the automatically generated `results_tost_sarsop_n20_robustness_per_seed.csv`, and add the exact \(n=20\) command to the README. Alternatively, explicitly restrict the README and `ENVIRONMENT.md` recomputability statement to the canonical \(n=5\) TOST and state that the \(n=20\) result is archived only as sufficient summaries. The first option is preferable because it requires no new design choice or new data.

## Optional suggestions

1. **Add tuning provenance to the compact tuned-weight artifact.**  
   **Location:** Section 5.1, line 394: “Every grid point is evaluated on one common tuning stream, seed \(7\)...”  
   The manuscript, checklist, README, and code now make the protocol reproducible, so this is non-blocking. Adding `tuning_seed`, episodes, candidate grid, metric, and tie rule to `results_supplementary_tuned_weights.csv` would make the artifact self-describing.

2. **Persist the full bootstrap bracket-frequency distribution.**  
   **Location:** Section 6.6, line 667: “In every disagreeing resample but one, the alternative is a neighbouring step...”  
   I verified this exact statement by rerunning the deterministic producer, but `results_price_bracket_stability.csv` stores only the reported/modal fractions and the 90% cover set. A long-form `(environment, budget, bracket, count)` companion would let readers verify rare alternatives, including Diagnosis's 12 resamples and Tileworld's single exception, without rerunning.

## Verification log

1. **Required change 1, TOST chronology:** line 703 now calls the procedure “fixed-margin,” explicitly says the earlier same-seed comparison was already known, labels the five-seed TOST retrospective, and identifies only the fifteen added seeds as prospective. **Resolved.**
2. **Prospective-seed record:** `Guidance_Documents/full_paper_plan.md`, line 652, records the additional seeds as \(\{2000,\ldots,2014\}\) fixed before running. The revised `run_tost_sarsop.py` docstring records the same chronology. **Resolved.**
3. **TOST numerical results:** the revision does not alter the previously verified \(n=5\) or \(n=20\) summary values. **No regression found.**
4. **Required change 2, fixed-weight SE versus bracket selection:** line 667 now says explicitly that the SE is for usage at fixed weight, bracket width is grid resolution, and neither is bracket-selection uncertainty. **Resolved.**
5. **Per-seed curve reproduction:** reran `python experiments/run_bracket_stability.py --from-per-seed`. All curve means reproduce `results_price_usage_curves.csv`, maximum absolute difference \(1.78\times10^{-15}\). **Exact match.**
6. **Bootstrap output reproduction:** the rerun regenerated all 25 rows of `results_price_bracket_stability.csv` under seed 20260928 with the same fractions, modal brackets, distinct counts, and 90% cover sets. **Exact match.**
7. **Manuscript aggregate stability counts:** independently reconstructed all 2,000 selections per budget. Exactly 19/25 budgets select the reported bracket in every resample, and 21/25 do so in at least 99% of resamples. **Exact match.**
8. **Lowest agreement:** Inspection-\(N=8\), \(B=14.04347\), selects the reported \((0.316228,2.15443]\) bracket in 1,578/2,000 resamples, \(0.789\), and its neighboring lower bracket in 422. **Exact match.**
9. **Tiger boundary instability:** \(B=4.48032\) is bracketed in 1,691/2,000 resamples and unbracketed in 309; \(B=5.65968\) is bracketed in 1,813 and unbracketed in 187. **Exact match.**
10. **Other disagreements:** Diagnosis \(B=9.534\) has 12/2,000 selections of its next staircase step; Bandit \(B=9.70152\) has 236/2,000 neighboring-step selections; Tileworld \(B=16.1842\) has the manuscript's single non-neighboring exception. **Exact match.**
11. **Bootstrap design:** inspected `run_bracket_stability.py`. Seed indices are resampled jointly across all weights, preserving the paired common-random-number structure, and the manuscript's `solve_shadow_price_from_curve` is rerun for every sample. **Methodologically appropriate.**
12. **Solver tests:** `python -m pytest tests/test_budget.py -q` completes with 29/29 passing. **Pass.**
13. **Required change 3, tuning stream:** line 394 discloses seed 7, one stream, reset per candidate, disjoint evaluation seeds, smallest-weight tie rule, and selection noise. The computational-experiments checklist names seed 7 as a deviation, and README repeats it. **Resolved.**
14. **Tuned-weight artifact:** `results_supplementary_tuned_weights.csv` still contains only environment, horizon, and selected weights. This does not undermine the now-complete prose/code disclosure, but motivates Optional Suggestion 1.
15. **Required change 4, general claim:** README and `ENVIRONMENT.md` no longer claim that every reported test has committed per-seed inputs. They correctly say most batteries have aggregate sufficient summaries and require producer reruns to re-derive inputs. **Resolved for the core and other listed aggregate-only batteries.**
16. **Required change 4, \(n=20\) exception:** no `results_tost_sarsop_n20_robustness_per_seed.csv` exists. The README's only TOST reproduction command uses the five default seeds, while its prose describes the “SARSOP TOST comparison” generically as recomputable from committed per-seed metrics. **Mismatch remains.**
17. **Optional suggestion 1 from round 1, Holm sizes:** direct counts in the artifacts are Tiger 108 nominal/107 finite, Diagnosis 84/83, Bandit 84/84. The revised line 1436 states exactly this. **Resolved.**
18. **Optional suggestion 2 from round 1, seed-respecting secondary bootstrap:** waiver accepted. The manuscript identifies the primary inference as seed-level Welch testing and describes the secondary intervals as 10,000 resamples over 5,000 episodes. Their inferential scope is sufficiently distinguishable and no primary claim depends on them.
19. **Optional suggestion 3 from round 1, lineage manifest:** waiver accepted. Producer comments in TeX and the README command table already provide a usable mapping, and the new bracket battery was added to that table.
20. **No artifact mutation from verification:** the bootstrap rerun rewrote only the already-untracked intended output path deterministically; its contents remained those inspected above. No manuscript, code, or result content was edited during this review.

## Would you recommend unqualified Accept if the required changes were made?

**Yes.** The remaining issue is a narrowly scoped archive/documentation mismatch; the revised statistical analyses and every newly reported bracket-stability number I checked are sound.

## Round 3

### Recommendation

**Accept.**

### Confirmation summary

The sole Round 2 required change is fully resolved. The \(n=20\) TOST now has a complete 60-row per-seed archive, an exact reproduction command, and citations from the manuscript and reproducibility checklist. I recomputed both the unpaired Welch TOST and the paired sensitivity analysis directly from those rows. Every stored statistic agrees to floating-point precision, and the 17 columns that predated this rerun are exactly unchanged. Optional Suggestion 2 is also resolved by the new long-form bracket-count archive. The waiver of Optional Suggestion 1 is reasonable because the tuning protocol is already stated in the manuscript, checklist, README, and executable code.

### Required changes

None.

### Optional suggestions

None.

### Verification log

1. `results_tost_sarsop_n20_robustness_per_seed.csv` contains exactly 60 rows: 20 seeds for each of Tiger, Diagnosis, and Bandit.
2. Every environment contains exactly the recorded seed set \(\{42,123,456,789,1024,2000,\ldots,2014\}\).
3. Recomputing the unpaired Welch TOST from the per-seed means gives Tiger \(p_{\mathrm{TOST}}=4.4773915019128183\times10^{-10}\), Diagnosis \(6.82288139505583\times10^{-7}\), and Bandit \(6.020624997595541\times10^{-11}\). **Exact matches.**
4. Recomputed means, differences, SEs, Welch degrees of freedom, both one-sided \(p\)-values, 90% confidence limits, and equivalence decisions all match `results_tost_sarsop_n20_robustness.csv`; the largest absolute numeric discrepancy is \(8.33\times10^{-17}\).
5. Recomputing the paired TOST gives Tiger \(0\) in the degenerate identical-policy case, Diagnosis \(6.094158862852271\times10^{-8}\), and Bandit \(1.3322676295501878\times10^{-15}\). The paired differences, SEs, decisions, and degeneracy flags all match.
6. Comparing the revised summary with `HEAD` confirms that all 17 original columns are exactly equal. The only additions are `p_tost_paired`, `diff_paired`, `se_paired`, `equivalent_paired`, and `paired_degenerate`.
7. README line 159 records the exact \(n=20\) command, including all seeds, 500 episodes, and the noncanonical output path.
8. README line 131 names both five-seed and \(n=20\) per-seed TOST files. `ENVIRONMENT.md` identifies both TOST protocols as per-seed-archived. The latter does not spell out the filename, contrary to the revision request's summary, but this is immaterial because it points to the README reproduction section that does.
9. Manuscript line 709 cites both the \(n=20\) summary and per-seed CSV. The JAIR checklist likewise lists the \(n=20\) per-seed archive. **Round 2 required change resolved.**
10. `results_price_bracket_stability_counts.csv` contains 31 outcome rows over 25 budgets. Counts sum to 2,000 for every budget.
11. For every budget, the long-form counts reproduce `frac_reported` and `n_distinct` in `results_price_bracket_stability.csv` exactly. The main stability CSV remains numerically unchanged.
12. Manuscript line 667 cites the new count archive. **Round 2 Optional Suggestion 2 resolved.**
13. The waiver of tuning-artifact provenance columns is accepted. No statistical or reproducibility claim depends on those columns, and the full protocol remains recoverable from the manuscript, checklist, README, and `tune_info_gain_weight`.

### Would you recommend unqualified Accept?

**Yes.** All required statistical and reproducibility changes are now closed, with no new issue introduced by the confirmation reruns.
