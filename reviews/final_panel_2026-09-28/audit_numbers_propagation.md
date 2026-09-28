# Numbers and propagation audit

## Defects

1. **BLOCKING — `paper/full_paper_jair.tex:70,754,1077`; `paper/full_paper.tex:709,1026`**
   - Quote: “nine of the twelve attainable budgets”
   - What is wrong: This counts table rows as distinct budgets. Tiger's `gap` row is identical to its `interior_0.5` row: both have \(B=5.07\), the same family per-seed rewards, the same reference, and the same interval. There are twelve evaluated rows but only eleven distinct `(environment, budget)` pairs. The supported count is nine of twelve rows, or eight of eleven distinct pairs. The companion “other three” count is three rows and also three distinct pairs.
   - Evidence: Recomputing every mixture row from `results/results_budget_frontier.csv` and `results/results_cpomdp_frontier_heldout.csv` reproduces `results/results_budget_frontier_heldout_reference.csv` exactly. Individually, nine rows have two-sided paired 95% \(t_4\) intervals excluding zero: four Tiger rows, two Diagnosis rows, and three Bandit rows. Deduplicating Tiger's coincident `gap`/`interior_0.5` rows leaves eight significant pairs among eleven distinct pairs.
   - Exact fix: In the abstract, same-stream paragraph, and conclusion in both masters, replace “nine of the twelve attainable budgets” with “nine of the twelve evaluated budget rows (eight of the eleven distinct environment-budget pairs).” Replace “the other three” with “the other three rows” where needed. The abstract and conclusion should use plural “paired 95 percent intervals exclude zero.”

2. **BLOCKING — `paper/full_paper_jair.tex:1317`; `paper/full_paper.tex:1606`**
   - Quote: “Planning+IG uses the success-tuned weight selected as in Section~\ref{sec:methodology}.”
   - What is wrong: Figure 18 does not use the methodology's main-table Planning+IG tuning procedure. Its producer calls `tune_info_gain_weight(env, tune_episodes=100)` without `agent_class`, which tunes the myopic `InformationGainAgent`, then transfers that weight to `PlanningInfoGainAgent`. Section methodology says non-Tileworld Planning+IG is tuned on its own class with 200 episodes.
   - Evidence: `experiments/run_visualizations.py:353-359` versus `experiments/run_experiment.py:416-454` and the main-table callers at lines 481-490, 565-574, 715-723, and 747-755. The producer's own call also uses 100 rather than 200 episodes.
   - Exact fix: In both captions replace the quoted sentence with: “Planning+IG uses the myopic InformationGainAgent's success-tuned weight, selected on 100 tuning episodes and transferred to Planning+IG for this visualization, rather than the main-table own-class tuning protocol of Section~\ref{sec:methodology}.”

3. **MINOR — `experiments/run_tost_sarsop.py:2-15`**
   - Quote: “Predeclared-margin TOST equivalence test”
   - What is wrong: The producer docstring retains the chronology the manuscript now correctly withdraws. Git history shows the script was introduced with the predeclared claim after the canonical comparison was already known. The current manuscript calls the five-seed test retrospective. The n=20 run's extra seeds are a separate chronology.
   - Evidence: `git log -p -- experiments/run_tost_sarsop.py` shows the original August 6 addition already calling the margin predeclared. `Guidance_Documents/full_paper_plan.md:390-424` records that the earlier comparison existed before formal TOST. Ledger line 652 states retrospectively that seeds `{2000..2014}` were fixed before the n=20 run, but that statement and the n=20 artifact first enter git together in commit `3cfd77b`; there is no independently timestamped pre-run commit. This does not show the claim is false, only that git history cannot independently establish it.
   - Exact fix: Change the docstring to “Fixed-margin TOST equivalence test” and state that the canonical five-seed margin was chosen with the earlier comparison known. For the robustness run, say “the project ledger records that the fifteen added seeds `{2000..2014}` were fixed before running” or omit the prospective chronology claim unless a timestamped pre-run record is available.

## Changed passages checked and found correct

1. **Same-stream frontier arithmetic and table columns.** All twelve mixture-row envelope values, paired gaps, SEs, and two-sided 95% \(t_4\) intervals recompute exactly from the two per-seed source CSVs. The generated `Same-stream ref.` and `Paired gap` columns match the result CSV after rounding. Tiger \(5.684\) versus committed \(5.016\) correctly rounds to \(5.68\) versus \(5.02\).

2. **Frontier qualitative numbers, after treating rows as rows.** The three non-significant rows are Diagnosis 0.25, Diagnosis gap, and Bandit 0.25. The largest shortfall in each environment occurs at its largest distinct budget. Bandit's largest-budget shortfall is \(1.316/6.267=0.20999\), correctly “about a fifth.”

3. **`experiments/run_frontier_reference_heldout.py`.** Its held-out environment seed is exactly `seed * 10000 + episode`, matching `run_budget_frontier.py`. `run_otc_episode` resets both environment and agent each episode. Pairing by outer seed is valid. The held-out feasible envelope is selected from held-out mean usage/reward, and its one common LP weight vector is correctly applied to each reference seed's reward before subtracting the corresponding family seed mean. The lineage guard really reruns every saved policy under `evaluate_agent`'s canonical once-per-seed stream and aborts on reward or usage disagreement above \(10^{-9}\).

4. **Frontier caveats.** The prose correctly says the same-stream run removes stream mismatch but not selection bias, and consistently calls the reference near-optimal and estimated rather than exact.

5. **TOST chronology rewrite in the masters.** Both masters identically disclose that the canonical five-seed test is retrospective, use “fixed margin,” and separate that from the ledger-recorded before-run choice of the fifteen added seeds. The n=5 and n=20 values match their CSVs. The old “predeclared-margin” phrase is absent from both live masters, README, and Section 8.9.1.

6. **Tuning disclosure.** For the main tables, `tune_info_gain_weight` uses candidate weights in ascending order, resets NumPy and the per-episode environment stream to tuning seed 7 for every candidate, and updates only on strict improvement, so ties select the smallest default-grid weight. The main Tiger, Testbed, Diagnosis, and Bandit callers use 200 episodes and tune `InformationGainAgent` and `PlanningInfoGainAgent` separately. Tileworld uses 100 episodes and also tunes the classes separately. `results_supplementary_tuned_weights.csv` agrees with the main result rows.

7. **README and ENVIRONMENT per-seed claims.** The named TOST, budget-frontier, same-stream reference, and dual-control files contain the claimed seed-resolved fields. `results_budget_frontier.csv` and its curve file contain pipe-delimited per-seed usage and reward. `results_cpomdp_frontier_heldout.csv` contains both per-seed metrics. The TOST file contains one row per environment and seed. The dual files contain controller-seed traces and metrics. The more limited claim for other batteries is accurate. The still-running bracket-stability artifact was excluded as directed.

8. **Figure 4.** The revised caption and JAIR Description match `figures/price_dual_multiseed.png` and `plot_dual_multiseed`: median/IQR, weight near 0.3 before rescaling, rise to about 2.7, rolling-20 usage, and the relative recovery speeds.

9. **Figure 15.** The revised JAIR Description matches `figures/fig_asymmetry_sweep.png`, including the orange and pink trajectories in the zoom panel and the values near penalties 200 and 500. Its producer draws the claimed series and zoom range.

10. **Figure 17.** The revised caption correctly calls the episodes illustrative rather than representative. The rendered heatmap shows 29, 14, and 32 observations, all correct, with the stated true-state and wrong-row behavior. The producer explicitly selects a successful EFE seed with at least six observations and replays that same episode seed for all agents.

11. **Figure 19.** “Consistent with” correctly replaces “confirming.” The rendered points and producer support only the measured horizons \(H\in\{1,2,3\}\), with guide lines rather than an asserted continuous trend.

12. **Other propagation checks.** The changed tuning, TOST, frontier, conclusion, Figure 17, Figure 18, and Figure 19 passages are identical in both masters where required. No semicolon was introduced in added manuscript prose. The surviving phrase “eleven of the twelve budgets” in the frontier paragraph refers to the different, still-correct target-mixture identity claim, not the superseded reference-envelope count. Section 8.9.1 contains neither stale phrase.
