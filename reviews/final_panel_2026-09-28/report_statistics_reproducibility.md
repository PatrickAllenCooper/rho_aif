# Statistics and Reproducibility Review

## Recommendation

**Accept with minor revisions.**

## Summary

The manuscript gives a theoretical and empirical account of Expected Free Energy (EFE) as a belief-dependent utility in \(\rho\)-POMDPs and then operationalizes the information-gain weight as the price needed to attain an expected sensing-usage budget. The empirical program is unusually broad and generally careful. Its primary comparisons use seed-level means, Welch tests, and Holm--Bonferroni correction, while equivalence to the SARSOP reference is assessed with TOST and the budget-control experiments distinguish calibration, held-out evaluation, and paired controller comparisons. I independently recomputed a substantial sample from the committed CSVs. The headline Welch tests, TOST calculations, paired recovery-time interval, and held-out budget-frontier summaries reproduce exactly. The revisions I require concern the chronology represented by “predeclared” for TOST, uncertainty in the selected crossing bracket rather than merely uncertainty in usage at fixed grid points, and two reproducibility claims that are stronger than the archived artifacts and protocol disclosure support.

## Strengths

- Seed-level means, rather than pooled episodes, are the primary unit for the main inferential comparisons. The manuscript explains why \(n=5\), not the episode count, determines inferential degrees of freedom.
- The Holm--Bonferroni family scope is stated unusually explicitly, including the exceptions for RockSample, the discount sweep, and the MCTS batteries.
- The TOST implementation uses Welch tests on per-seed means and reports margins, confidence intervals, paired sensitivity results, and an \(n=20\) robustness run.
- The dual-control comparison correctly uses a paired interval across common controller seeds. I reproduced the mean difference and Student-\(t\) interval exactly.
- The budget-frontier study cleanly separates calibration on the canonical seeds from evaluation on held-out seeds \(\{7,8,9,10,11\}\), and its per-seed arrays permit independent reconstruction.
- The POMCP exploration-constant selection uses tuning seeds \(\{11,22,33\}\) disjoint from the canonical evaluation seeds and records its selection rule. The manuscript also candidly labels the earlier Tiger comparison retrospective.
- Producer comments in the TeX, provenance columns, the README reproduction table, `ENVIRONMENT.md`, and pinned requirements give the results substantially better lineage than is usual for a paper of this scale.
- The manuscript is appropriately candid that per-episode traces are not universally committed and marks the raw-data checklist item “Partially.”

## Required changes

1. **Correct the chronology of the TOST margin and qualify “predeclared.”**  
   **Location:** Section 6.7, line 703: “The margin was set equal to the cost of one sensing action in each environment... It was fixed before these samples were inspected.”  
   **Problem:** This wording implies a prospectively chosen equivalence margin without prior access to the EFE--SARSOP comparison. The project record shows otherwise. `Guidance_Documents/full_paper_plan.md`, lines 390--401, records that the initial comparison had already been examined, that no equivalence test had been run, and that a post-hoc margin declaration was “methodologically delicate.” The TOST was added later in response to referees (`experiments/run_tost_sarsop.py`, lines 2--15). Fixing the margin before a fresh Monte Carlo sample is useful, but it does not erase prior knowledge of the comparison or make the margin prospectively predeclared in the usual confirmatory sense. The numerical TOST results themselves reproduce exactly and are not challenged.  
   **Concrete fix:** State the actual chronology. Treat the \(n=5\) TOST as a retrospectively motivated test or as a pilot-informed prospective rerun, and state that the one-sensing-action margin was selected after the earlier comparison was known. Anchor the strongest confirmatory equivalence claim in a genuinely prospective replication if one exists, explaining whether the \(n=20\) sample is independent of the pilot and when its margin and analysis were frozen. Otherwise describe both analyses as sensitivity evidence under a domain-motivated margin rather than “predeclared-margin” confirmation.

2. **Quantify, or explicitly limit, uncertainty in the selected shadow-price crossing bracket.**  
   **Location:** Section 6.6, line 667: “Crossing brackets with standard errors are what we report for every domain.”  
   **Problem:** The producer estimates an SE for \(U(w)\) at each fixed weight and saves only `usage_se_at_star` with each selected price (`experiments/run_price_of_information.py`, lines 182--205 and 525--551). It does not resample seeds and reselect the last crossing. Therefore the reported SE is an SE for estimated usage at a fixed selected grid point, not uncertainty in \(w_{\mathrm{lo}}\), \(w_{\mathrm{hi}}\), or which adjacent grid pair contains the crossing. With five seeds, sampling variation in two neighboring \(U(w)\) estimates can move the selected bracket, especially for nonmonotone Bandit and Tileworld curves. The vertical bars are correctly grid-resolution brackets, not confidence intervals, but the prose does not make this inferential limitation sufficiently explicit.  
   **Concrete fix:** State unambiguously that the existing SEs apply to usage estimates and that the crossing bars encode grid resolution only. In addition, assess bracket-selection stability by resampling the seed-level usage means jointly across weights and rerunning the same crossing rule, or provide an equivalent sensitivity analysis/confidence set over candidate grid brackets. Report the fraction selecting each bracket, especially for Bandit’s twice-crossed budget and other near-threshold rows. If the five-seed archive cannot support joint resampling, narrow all uncertainty language and identify bracket-selection uncertainty as unquantified.

3. **Disclose the single tuning stream used for the main tuned baselines in the manuscript and reproducibility checklist.**  
   **Location:** Section 5.1, line 394: “Each grid point is evaluated on 200 episodes, except on Tileworld, where 100 episodes are used...”  
   **Problem:** The manuscript gives episode counts but not the number or identity of tuning seeds. `experiments/run_experiment.py`, lines 364--366 and 416--455, shows that every candidate is evaluated on one dedicated stream, `TUNING_SEED = 7`, with that stream reset for each candidate. This is disjoint from the canonical evaluation seeds and therefore does not contaminate evaluation, but it is a statistically material single-seed hyperparameter-selection protocol. The reproducibility checklist at line 1854 says deviations from the canonical five seeds are stated and enumerates many exceptions, but omits this central one. The resulting tuned weights are archived in `results/results_supplementary_tuned_weights.csv`, without the tuning seed.  
   **Concrete fix:** State that the main Info Gain and Planning+IG weight grids use one common-random-number tuning stream at seed 7, explain the tie rule, and add this deviation to the reproducibility checklist and README. Add the tuning seed, episodes, candidate grid, metric, and tie rule to the tuned-weight artifact. Qualify the selected tuned weights as noisy single-stream selections or provide a multiseed tuning sensitivity analysis.

4. **Correct the claim that every reported test is independently recomputable from committed per-seed CSVs.**  
   **Location:** Reproducibility checklist, computational-experiments item 3, line 1851: “The repository commits, for every reported table and figure, the summary CSV it is built from...”  
   **Problem:** The manuscript’s “Partially” response is appropriately cautious, but the linked reproducibility documentation is not. `README.md`, line 131, says: “Per-seed metrics for the claim-bearing batteries are committed... so every reported test can be recomputed from the CSVs without rerunning an episode.” `ENVIRONMENT.md`, lines 23--26, repeats that claim. It is false for important batteries. For example, `results_summary.csv`, `results_diagnosis_n4.csv`, and `results_bandit.csv` contain aggregate means and seed-level SEs, while their `*_stats.csv` files contain already-computed tests; no corresponding core `*_per_seed.csv` files exist. The Welch statistic can be algebraically reconstructed from means, SEs, and \(n\), as I did, but this does not independently recompute those inputs from the five seed means or audit seed labeling. The \(n=20\) TOST robustness file likewise contains only summary inputs and outputs, not its 20 per-seed means.  
   **Concrete fix:** Either commit per-seed means for every claim-bearing inferential battery, including the core tables and \(n=20\) TOST, or narrow the README and `ENVIRONMENT.md` claim to identify exactly which tests can be recomputed from raw per-seed records and which can only be reconstructed from saved sufficient summaries. Align the manuscript checklist with that precise scope.

## Optional suggestions

1. **Clarify nominal versus effective Holm family size.**  
   **Location:** Supplementary Statistics appendix, line 1436: “giving \(108\) for Tiger... \(84\) for Diagnosis and Bandit.”  
   The Diagnosis stats artifact has 84 nominal rows, but the identical zero-variance observation comparison yields an undefined seed-level \(p\)-value and is excluded by the implementation, leaving 83 finite tests in the actual Holm calculation. My recomputation of all 83 decisions matched. Say “84 nominal comparisons, 83 defined tests for Diagnosis” or define how undefined null contrasts are counted.

2. **Use a seed-respecting bootstrap for secondary confidence intervals.**  
   **Location:** Supplementary Statistics appendix, line 1436: “Bootstrap 95\% confidence intervals use 10,000 resamples with fixed seed for reproducibility.”  
   The primary seed-level tests are correct, but the displayed bootstrap intervals resample pooled episodes. A hierarchical bootstrap (seeds, then episodes within seeds) or a bootstrap of the five seed means would align the secondary intervals with the declared independent replication unit.

3. **Archive a machine-readable manifest connecting each TeX table/figure to producer and output files.**  
   **Location:** Reproducibility checklist, computational-experiments item 3, line 1851: “The repository commits, for every reported table and figure, the summary CSV it is built from...”  
   Producer comments and the README are strong but distributed. A checked manifest with TeX label, producer command, inputs, outputs, seed protocol, and code revision would make lineage auditing and stale-artifact detection mechanical.

## Verification log

All recomputations used the committed CSVs under `results/` and SciPy-compatible Welch/Student-\(t\) formulas. “Exact” below means agreement to the stored floating-point precision, apart from displayed rounding.

1. **Diagnosis EFE versus Planning reward, seed-level Welch:** reconstructed from `results_diagnosis_n4.csv` means/seed SEs with \(n=5\). Difference \(1.1968\), \(p=0.0020157858667\). **Exact match** to `results_diagnosis_n4_stats.csv`.
2. **Diagnosis EFE versus Planning success:** difference \(0.0834\), \(p=3.95804886025\times10^{-8}\). **Exact match**.
3. **Bandit EFE versus Planning reward:** difference \(0.5223\), \(p=0.00109080975662\). **Exact match** to `results_bandit_stats.csv`.
4. **Bandit EFE versus Planning success:** difference \(0.1590\), \(p=2.13735105159\times10^{-5}\). **Exact match**.
5. **Tileworld Planning versus EFE reward:** reconstructed seed-level Welch \(p=0.821648365293\). **Exact match** to the Tileworld stats artifact.
6. **Tileworld Planning versus EFE success:** \(p=0.166375210540\). **Exact match**.
7. **Tiger EFE--SARSOP TOST from raw five per-seed means:** margin \(1.0\), \(p_{\mathrm{TOST}}=0.00102519726186\), 90% CI \([-0.4148938,0.4148938]\). **Exact match** to `results_tost_sarsop.csv`.
8. **Diagnosis EFE--SARSOP TOST from raw five per-seed means:** margin \(1.0\), \(p_{\mathrm{TOST}}=0.0458178848528\), CI \([-0.5057616,0.9761616]\). The paired sensitivity calculation gives \(p_{\mathrm{TOST}}=0.0160757823546\). **Exact matches**.
9. **Bandit EFE--SARSOP TOST from raw five per-seed means:** margin \(0.5\), \(p_{\mathrm{TOST}}=0.0129753214487\), CI \([-0.3458967,0.3086967]\); paired \(p_{\mathrm{TOST}}=3.6342425368\times10^{-5}\). **Exact matches**.
10. **The \(n=20\) TOST robustness summaries:** Tiger \(4.4774\times10^{-10}\), Diagnosis \(6.8229\times10^{-7}\), Bandit \(6.0206\times10^{-11}\), with Tiger CI \([-0.208664,0.208664]\). **Matches manuscript and summary CSV**, but **could not be independently recomputed from raw per-seed means** because those 20 means are not committed.
11. **Dual-control recovery comparison from per-seed metrics:** decay-only mean \(157.3\), reset mean \(51.2\), paired mean difference \(106.1\), 95% Student-\(t\) CI \([96.7701,115.4299]\), minimum paired advantage 89 episodes. **Exact matches** to the manuscript and `results_price_dual_multiseed_metrics.csv`.
12. **Dual-control post-shift errors:** recomputed the means and paired intervals from the ten per-seed rows. **Exact matches** to the stored summaries and prose.
13. **Held-out budget-frontier mixtures:** decoded the pipe-delimited five-seed arrays in `results_budget_frontier.csv` and recomputed all 12 attainable mixture usage means, SEs, and absolute budget errors. **All 12 exact matches**. Maximum error is \(0.123\), 11/12 are within one SE, and the Bandit gap row has error \(0.092\) versus SE \(0.0688\), approximately \(1.34\) SE, exactly as described.
14. **Calibration/evaluation separation for the frontier:** producer inspection confirms calibration uses the canonical five seeds and held-out policy evaluation uses \(\{7,8,9,10,11\}\). **Match** to manuscript and artifact provenance.
15. **Diagnosis Holm family:** reapplied Holm to all 83 finite seed-level \(p\)-values in `results_diagnosis_n4_stats.csv`. **Zero decision mismatches**. One of 84 nominal rows is undefined because both agents have identical zero-variance observations, explaining the effective-family discrepancy noted above.
16. **Structural Inspection \(N=16\):** `results_inspection_n16_stats.csv` records Planning versus EFE reward difference \(0.3898\), seed-level \(p=0.5697415\), not Holm-significant, while accuracy and tests differ strongly. **Match** to the paper’s within-sampling-error reward interpretation.
17. **RockSample[7,8]:** `results_rocksample_7x8_stats.csv` gives Planning \(12.306\) versus EFE \(21.849\), difference \(-9.543\) in file order, seed-level \(p=5.8253\times10^{-5}\), Holm-significant. **Match** to the reported \(+9.54\) EFE advantage.
18. **Distractor diagnosis onset and \(w=100\) endpoint:** `results_distractor_diagnosis.csv` is zero through \(w=3.5\), then exactly 1.0 distractor test and fraction \(0.10265\) at \(w=4\), yielding bracket \((3.5,4.0]\). At \(w=100\), ordinary Planning+IG has 6.456 distractor tests and fraction \(0.33151\), while the reward-relevant variant remains exactly zero. Rewards are \(-10.476\) and \(-3.644\). **Exact matches** to the rounded prose.
19. **Discount-sweep multiplicity:** `results_discount_stats.csv` contains the stated 24-test family. The stored Holm decisions agree with reapplication to all 24 finite seed-level \(p\)-values. **Match**.
20. **POMCP tuning/evaluation separation:** `results_pomcp_exploration_selected.csv` records tuning seeds `11|22|33`, \(n=3\), the rule “max success on tuning seeds, ties by reward,” and evaluation \(n=5\). The selected Tiger comparison gives success \(0.982\) versus \(0.963\), raw \(p=0.0237119\), Holm-significant within its six-test selected family, while reward \(p=0.1553702\) is not. **Match** to the selected-comparison artifact and manuscript’s disjoint-seed account.
21. **Shadow-price examples:** recomputation from the stored usage curves gives Diagnosis \(B=9.534\) bracket \((0.13895,0.31623]\), usage endpoints \(5.904/9.772\); Bandit \(B=5.87448\) bracket \((1.63789,3.72759]\), endpoints \(5.108/7.318\); Tileworld \(B=23.74\) bracket \((5.62341,23.71374]\), endpoints \(14.745/24.595\). **Exact matches** to `results_price_shadow_curves.csv`. The associated stored quantity is usage SE at the selected point, not selection uncertainty for the bracket.
22. **Reproduction table and environment:** every major empirical battery named in the manuscript has a command in the README table, `ENVIRONMENT.md` pins the generating machine, Python, packages, and SARSOP binary, and it distinguishes per-episode reset seeding from once-per-outer-seed streams. **Match**, subject to Required Changes 3 and 4.

## Would you recommend unqualified Accept if the required changes were made?

**Yes.** The sampled numerical results and primary inferential calculations are sound; the required revisions concern confirmatory labeling, uncertainty scope, and reproducibility disclosure rather than a failed headline result.
