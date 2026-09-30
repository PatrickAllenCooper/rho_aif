# Statistics and Reproducibility Review

## 1. Recommendation

Accept.

## 2. Summary

This paper gives expected sensing usage an operational price in belief-dependent-reward POMDPs. It first identifies the stated recursive expected-free-energy objective with a unit-information-weight rho-POMDP under explicit structural, horizon, scoring, and unit assumptions. It then defines the population crossing threshold \(w^*(B)\), its finite-grid bracket, and an endpoint mixture for meeting an expected sensing target. The empirical work spans controlled observe-then-commit domains, Tileworld, RockSample, and Structural Inspection, with comparisons to planning, information-only, SARSOP, constrained-POMDP, POMCP-like, and MCTS baselines. The shortened main body remains statistically self-supporting because it states the estimands and headline uncertainty results, while its appendix pointers resolve to complete test mechanics, multiplicity families, per-seed robustness analyses, and limitations. I found the statistical claims carefully calibrated: non-significance is not called equivalence, retrospective TOST margins are disclosed, paired and unpaired analyses are distinguished, held-out frontier intervals are explicitly called nominal plug-in summaries, and the bracket bootstrap is correctly interpreted as selection stability rather than a price confidence interval.

## 3. Strengths

- The primary unit of analysis is the seed mean, not pooled episodes. Main comparisons use seed-level Welch tests and explicitly scoped Holm--Bonferroni families.
- The equivalence analysis states its margins, discloses that the five-seed margins were selected after inspection, adds a 20-seed run fixed before execution, and reports a paired sensitivity analysis beside the conservative unpaired analysis.
- The constrained-frontier study separates calibration seeds from held-out evaluation seeds, detects and corrects the original cross-stream comparison, archives per-seed quantities, and does not overstate its same-stream pointwise intervals.
- The bracket bootstrap is reproducible from archived per-seed usage curves and is described as bracket-selection stability, not uncertainty for the population price.
- Producer scripts, committed CSVs, generated tables, and prose have unusually clear lineage. The README maps each reported battery to a reproduction command, and `ENVIRONMENT.md` distinguishes per-episode from once-per-outer-seed stream initialization.
- Material removed from the concise main body remains available in the appendices. In particular, Appendix I gives the test-family definitions, Appendix U gives the TOST mechanics and archives, Appendix W gives frontier details and interval limitations, and Appendix Z gives a candid data-availability and seeding inventory.

## 4. Required changes

None.

## 5. Optional suggestions

1. **Section 6.9, line 674.** Quote: “The resulting Student-\(t\) intervals are nominal pointwise plug-in summaries.” The limitation is already stated correctly, so this is non-blocking. As an additional sensitivity analysis, report in Appendix W.6 either Holm-adjusted paired tests or simultaneous intervals across the 11 distinct budgets. This would let readers see how the descriptive “eight of eleven” result changes under family-wise control without changing the main-body claim. **Placement: appendix.**

2. **Appendix Z, line 2187.** Quote: “Episode-level frames for the remaining batteries are not committed as files.” The archive is sufficient for exact reruns and for reconstructing the committed Welch results, but several batteries do not retain the five individual seed means. Consider committing per-seed aggregate files for every main battery so readers can independently examine leverage, pairing, and alternative robust summaries without rerunning episodes. **Placement: appendix and repository artifact, with at most a net-neutral checklist wording update.**

## 6. Verification log

I read the complete 117-page rendered-text extraction, including all appendices, and checked the corresponding source, producers, README, environment record, and result files. I used read-only Python with SciPy to recompute Welch TOST components, Student-\(t\) intervals, paired standard errors, Holm decisions, and bootstrap frequencies directly from committed per-seed CSVs. Numerical comparisons below used the unrounded CSV values.

1. **Five-seed Tiger TOST: match.** From `results/results_tost_sarsop_per_seed.csv`, I recomputed the unpaired Welch TOST in `experiments/run_tost_sarsop.py`: difference \(0\), SE \(0.22311539615185677\), and \(p_{\mathrm{TOST}}=0.0010251972618614401\). These match `results_tost_sarsop.csv` and the main-text \(0.0010\).

2. **Five-seed Diagnosis TOST: match.** Recomputed difference \(0.2352\), SE \(0.3835672561624623\), and \(p_{\mathrm{TOST}}=0.04581788485277879\). The CSV values and main-text \(0.0458\) match.

3. **Five-seed Bandit TOST: match.** Recomputed difference \(-0.0186\), SE \(0.17529455211158168\), and \(p_{\mathrm{TOST}}=0.012975321448685073\). The CSV values and main-text \(0.0130\) match.

4. **Five-seed TOST multiplicity: match.** Applying Holm--Bonferroni to the three environment-level intersection-union \(p_{\mathrm{TOST}}\) values retains all three equivalence decisions, as claimed at line 601.

5. **Five-seed paired sensitivity: match.** Direct paired calculations reproduce degenerate zero differences for Tiger, \(p_{\mathrm{TOST}}=0.016075782354619494\) for Diagnosis, and \(3.63424253679856\times10^{-5}\) for Bandit. These match the archive and the rounded prose.

6. **Twenty-seed Tiger TOST: match.** From `results_tost_sarsop_n20_robustness_per_seed.csv`, the recomputed \(p_{\mathrm{TOST}}\) is \(4.4773915019128183\times10^{-10}\), matching the summary CSV and the reported \(4.5\times10^{-10}\).

7. **Twenty-seed Diagnosis TOST: match.** The recomputed \(p_{\mathrm{TOST}}\) is \(6.82288139505583\times10^{-7}\), matching the archive and reported \(6.8\times10^{-7}\).

8. **Twenty-seed Bandit TOST: match.** The recomputed \(p_{\mathrm{TOST}}\) is \(6.020624997595541\times10^{-11}\), matching the archive and reported \(6.0\times10^{-11}\).

9. **Twenty-seed TOST multiplicity: match.** Holm correction across the three environments retains all three decisions. Across all six n=5 and n=20 summary rows, my recomputed TOST quantities differed from the stored values by at most \(1.11\times10^{-16}\).

10. **TOST margin provenance: match.** Line 599 says the five-seed margins followed inspection and that the additional 15 seeds were fixed before the n=20 run. `run_tost_sarsop.py`, the README command, and the two per-seed archives agree on margins, seed sets, and 500 episodes per seed. The paper does not mislabel the original analysis as prospectively predeclared.

11. **Dual-controller restricted means: match.** From `results_price_dual_multiseed_metrics.csv`, the 10 paired seeds give decay-only mean \(157.3\) and reset mean \(51.2\), exactly matching the Figure 7 caption at line 523.

12. **Dual-controller paired interval: match.** The per-seed restricted differences have mean \(106.1\), SE \(4.124318125460256\), and Student-\(t\) 95% interval \([96.77014421060109,115.4298557893989]\). All 10 differences are positive. This matches the reported \(106.1\) and \([96.8,115.4]\).

13. **Held-out frontier row statistics: match.** I recomputed all 12 mixture rows from `results_budget_frontier.csv` and `results_cpomdp_frontier_heldout.csv` following `run_frontier_reference_heldout.py`. All mixture reward and usage means, seed-level SEs, paired gaps, paired-gap SEs, and Student-\(t\) intervals match `results_budget_frontier_heldout_reference.csv`; maximum absolute numerical discrepancy was \(8.33\times10^{-17}\).

14. **Held-out frontier interval count: match.** Nine of 12 mixture-row intervals exclude zero. Removing the duplicated Tiger gap budget leaves eight of 11 distinct budgets, exactly as reported at line 676.

15. **Held-out usage accuracy: match.** Across the 12 rows, the largest absolute difference between held-out mean usage and target budget is Diagnosis's \(0.123\). This supports the abstract and main-body statement that targets are met within \(0.13\) observations on held-out seeds.

16. **Held-out design and interval scope: match.** The frontier CSV provenance records seeds `7|8|9|10|11` and 100 episodes per seed. The producer fits reference support and mixture weights on those held-out seed means, then holds them fixed when computing the paired SE. Lines 672--676 and Appendix W disclose the cross-stream history, same-stream reselection, plug-in nature, omitted selection uncertainty, and lack of multiplicity adjustment.

17. **Bracket-bootstrap frequencies: match.** I replayed the 2,000 seed bootstraps with seed 20260928 from `results_price_usage_curves_per_seed.csv` according to `run_bracket_stability.py`. Every one of the 25 `frac_reported` values in `results_price_bracket_stability.csv` matched exactly.

18. **Bracket-bootstrap summary: match.** The replay gives 19 of 25 exact frequencies equal to 1.0, 21 of 25 at least 0.99, and a minimum of 0.789 for Inspection-N8. These match the line-567 main-text summary. The text correctly calls these selection frequencies, not confidence coverage for \(w^*(B)\).

19. **Diagnosis Holm family: match.** Reapplying the stored family rule to `results_diagnosis_n4_stats.csv` reproduced all 83 defined Holm decisions among 84 rows, with zero mismatches.

20. **Bandit Holm family: match.** Recalculation for `results_bandit_stats.csv` reproduced all 84 defined decisions, with zero mismatches.

21. **Tileworld Holm family: match.** Recalculation for `results_tileworld_6x6_stats.csv` reproduced all 62 defined decisions among 63 rows, with zero mismatches.

22. **Structural Inspection Holm family: match.** Recalculation for `results_inspection_n16_stats.csv` reproduced all 18 decisions, with zero mismatches.

23. **Distractor-study Holm family: match.** Recalculation for `results_distractor_diagnosis_stats.csv` reproduced all 60 defined decisions among 80 rows, with zero mismatches.

24. **Multiple-comparison scope: match.** Appendix I, line 1250, defines one family as all reported pairwise agent comparisons and metrics within an environment or instance table, then distinguishes explicitly uncorrected displays. The row counts and Holm flags in the sampled stats files are consistent with that scope.

25. **Main-to-appendix statistical reporting: match.** The concise main text's seed counts, SE unit, Welch/Holm rule, TOST headline, paired sensitivity, frontier interval qualification, and dual-control interval all resolve to detailed appendix protocols and named archives. I found no main empirical claim whose removed detail was absent from the appendices.

26. **Reproduction map and environment pinning: match.** README lines 130--160 map the key batteries above to their producers and list the available per-seed archives. `ENVIRONMENT.md` records the machine, pinned dependencies, canonical seeds, per-episode rule \(10^4s+i\), once-per-outer-seed exceptions, and provenance coverage. These agree with Appendix Z's reproducibility checklist.

27. **Data lineage: match.** For the focal analyses, the chain is direct: `run_tost_sarsop.py` writes both TOST summaries and per-seed archives; `run_bracket_stability.py` consumes the per-seed usage curves and writes bracket frequencies; `run_frontier_reference_heldout.py` consumes held-out family and reference archives and writes same-stream paired gaps; the dual-control trace and metrics files support Figure 7. The generated values match the corresponding tables, captions, and prose.

No checked claim mismatched. I found no quantitative claim in this sample that could not be verified from the committed artifacts.

## 7. Would you recommend unqualified Accept if the required changes were made?

Yes. There are no required changes, and the current concise manuscript already warrants unqualified acceptance under this review lens.
