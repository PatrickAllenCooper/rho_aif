# Statistics and Reproducibility Review

## 1. Recommendation

Accept

## 2. Summary

The paper calibrates the information-gain weight of a rho-POMDP policy family to an expected sensing-usage target, distinguishes the population crossing threshold from its finite-grid bracket, and relates the canonical EFE weight to one point in that family. The empirical program combines seed-level comparisons, fixed-margin equivalence tests, held-out budget calibration, same-stream paired reference comparisons, fresh-seed replication, and explicit reproducibility artifacts.

## 3. Strengths

- The primary tests use seed means rather than treating episodes as independent replications. The manuscript states the Welch and Holm protocols and identifies the comparison families, including the RockSample within-metric exception.
- The SARSOP comparison correctly separates non-significance from equivalence. The five-seed TOST is labelled retrospective, the operational margins are explicit, the prospective addition of fifteen seeds is disclosed, and paired and unpaired analyses are distinguished.
- The frontier study handles a consequential stream mismatch explicitly. The same-stream intervals are accurately called nominal pointwise plug-in summaries, with omitted support-selection, mixture-weight, feasibility, and multiplicity uncertainty stated.
- The fresh-seed replication freezes both family mixtures and reference supports, performs a lineage replay, and reports the Diagnosis instability and the one non-blind pair rather than hiding them.
- Seeding rules, exceptions, environment details, package versions, producer commands, and committed per-seed archives are unusually thorough. The README headline table regenerates from its CSVs, and the full test suite passes.

## 4. Required changes

None.

## 5. Optional suggestions

- Replace the README reproduction-table row “Pareto / transfer / ... see `experiments/run_*.py`” with explicit commands for each remaining artifact. Most important batteries already have precise rows, so this is documentation cleanup rather than a reproducibility blocker.
- Consider storing Holm-adjusted p-values in addition to raw p-values and rejection flags. The present flags are reproducible and sufficient for the claims, but adjusted values would make external reanalysis easier.

## 6. What I verified

- Recomputed the five-seed unpaired Welch TOST directly from `results/results_tost_sarsop_per_seed.csv`. I recovered Tiger \(p_{\mathrm{TOST}}=0.001025\), Diagnosis \(0.045818\), and Bandit \(0.012975\), with the manuscript's 90% intervals. All three survive a three-test Holm step-down family.
- Recomputed paired TOST sensitivity values from the same archive. I recovered Diagnosis \(p_{\mathrm{TOST}}=0.01608\), Bandit \(3.63\times10^{-5}\), and Tiger's degenerate zero-difference result.
- Checked `results/results_tost_sarsop_n20_robustness.csv`: the reported \(n=20\) values \(4.48\times10^{-10}\), \(6.82\times10^{-7}\), and \(6.02\times10^{-11}\) match.
- Recomputed the paired restricted recovery comparison from `results/results_price_dual_multiseed_metrics.csv`: decay-only mean 157.3, reset mean 51.2, mean paired difference 106.1, SE 4.124, and 95% Student-\(t\) interval \([96.77,115.43]\).
- Recomputed selected fresh-seed frontier intervals from the archived per-seed gaps in `results/results_budget_frontier_fresh_seed_replication.csv`. The file has nine negative intervals among twelve rows, eight among eleven distinct budgets, and eleven negative means. The Diagnosis and Bandit examples in the appendix reproduce.
- Inspected `experiments/run_frontier_reference_heldout.py` and `experiments/run_frontier_fresh_seed_replication.py`. The held-out reference uses matched episode streams, while the replication freezes the committed mixture and reference support and uses seeds 12--21. The manuscript's plug-in and rare-event qualifications match the implementation.
- Reran `python experiments/run_bracket_stability.py --from-per-seed`. The committed usage curves reproduce to \(1.78\times10^{-15}\), and all bracket frequencies reproduce `results/results_price_bracket_stability.csv`.
- Checked the main Diagnosis and Bandit Planning-versus-EFE p-values against `results/results_diagnosis_n4_stats.csv` and `results/results_bandit_stats.csv`. The manuscript's raw seed-level Welch values and Holm-survival claims match.
- Inspected `rho_aif/stats.py`, `experiments/run_experiment.py`, `experiments/run_rocksample.py`, and `experiments/run_inspection.py`. Welch tests operate on per-seed means. Holm families match the revised manuscript description, including RockSample's within-instance, within-metric families.
- Ran `python experiments/build_readme_table.py --check`; the README table matches generated values.
- Ran `python -m pytest tests/ -q`; all 495 tests passed.

## 7. Addendum after full-line re-read

I withdraw my original required change and revise the recommendation from **Accept with minor revisions** to **Accept**. My first read was based on truncated search output for the unusually long JAIR source line 567. Reading that line in full shows that the manuscript already makes the needed distinction between fixed-weight usage SE, grid width, and bracket-selection stability, then reports the bootstrap protocol and findings with both archive citations.

I verified the passage directly against `results/results_price_bracket_stability.csv` and `results/results_price_bracket_stability_counts.csv`:

- There are 25 budgets and 2,000 resamples per budget.
- Exactly 19 budgets have `frac_reported = 1.0`.
- Exactly 21 budgets have `frac_reported >= 0.99`.
- The minimum agreement is 0.789 at Inspection-\(N=8\)'s lowest budget.
- The counts file records every disagreement outcome, including the neighbouring staircase alternatives, Tiger's unbracketed outcomes, and the single non-neighbouring exception allowed by the text's phrase “in every disagreeing resample but one.”

The manuscript passage therefore fully satisfies the concern. I found nothing else genuinely missing or wrong in this lens.
