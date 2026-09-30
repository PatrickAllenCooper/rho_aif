# Adversarial audit, batch 5 (POMCP cost-sign and path-belief fix, ledger 9.17.57)

Auditor scope: `rho_aif/agents/pomcp.py`, `experiments/run_pomcp_exploration_sweep.py` (`--merge`, `--out`), every rerun POMCP CSV against `pomcp_prefix/` and `pomcp_signfix_rootbelief/`, the 24 replacements of `apply_batch5.py`, the two inline Appendix Y follow-ups, and the two citation changes. Masters were read as they stood at 14:13:51 on 2026-09-29.

**The masters changed during the audit.** At 14:13:51, `apply_batch6.py` (Pat's 2026-09-29 instruction to remove error history) replaced batch 5's dated correction note with a pointer to the two tests. It also replaced "written after an earlier sweep had been inspected but before the corrected POMCP runs reported here" with "under a rule recorded before the runs reported here" (main body and Appendix Y), and deleted the appendix sentence "The rule was written after an earlier, uncorrected sweep had been inspected...". I audited both the batch 5 wording and the current wording.

**The timing reruns are also still running.** `experiments/run_pomcp.py` was running (log `p3_run_pomcp.log`, started 14:12) as the ledger's "clean timing rerun". My timing checks below are against the concurrent-run CSVs (`results_pomcp.csv` of 11:01, `results_mcts_efe.csv` of 10:45). Every timing and ratio sentence must be re-verified once those reruns land. The concurrency-caveat sentence is still in both masters.

## 1. Code

- **Cost sign.** Both sites are now correct: the tree step is `reward = -obs_cost + ...` and the rollout is `total -= gamma_power * obs_costs[...]`. `obs_costs` are positive costs (`base.py`), and the environments pay `-cost`. OK.
- **Path belief.** The child belief is `belief * obs_models[a][:, obs]`, normalized. If the norm is 0 it falls back to the parent belief. The multiply creates a new array, so the agent's root belief is never mutated in place. `_rollout` copies the belief it receives. The belief handed to the rollout at a new leaf is the one reached along the edge into that leaf. OK.
- **Unchanged paths.** The in-tree commit reward `commit_rewards[commit_idx, state]` is unchanged. The depth-cap leaf `_best_commit_reward(state)` is unchanged and checked before any belief use. Path mode draws no extra random numbers. OK.
- **`rollout_belief='root'` reproduces old behavior apart from the sign.** I took HEAD's `pomcp.py`, patched only the two sign sites, and ran it against the new code with `rollout_belief='root'`. The environments were Tiger and Diagnosis, with 2 seeds, 15 episodes, 150 simulations, `vary_agent_seed=True`. Success, reward, and observation counts are identical. OK.
- **Tests.** `tests/test_pomcp_cost_sign.py` and `tests/test_pomcp_rollout_belief.py` give 6 passed.
- **`--merge`.** I recomputed the merge from `parts/sweep_*` and `parts/tuning_*`:
  - The rows equal the committed CSVs exactly, apart from timing and provenance columns.
  - The stats equal the committed CSVs apart from a 1-ulp CSV round-trip in two p-values.
  - Holm grouping is (family, metric) over the concatenated battery, the same as a single run.
  - Re-running `_apply_holm` on the pre-fix single-run stats reproduces every committed flag.
  - Row order is the stable ENVS order, matching a default single run. Column sets equal the prefix files.
  - The merge changes flags relative to the per-part files (4 in the sweep, 9 in the tuning), which is the intended effect.
  - The only gap is that `merge` does not check that the parts share seeds and episode counts or that environments are not duplicated. This is advisory only.
- **`--out`.** It is honored in both modes, and `--quick` still redirects to scratch. OK.

## 2. Lineage

- **Non-POMCP rows.** Every non-POMCP row is bit-identical to `pomcp_prefix/` in success, reward, std, obs, and all SE columns. That covers 8 rows in `results_pomcp`, 22 Exact-EFE/MCTS-EFE rows in `results_mcts_efe`, 1 in compute-matched, 6 in the sweep, and 6 in tuning.
- **Selection rule.** `select_pomcp_constants.py` is unchanged from HEAD. Its last commit is `08140f0` (2026-09-18), which predates every corrected run. Re-running its logic to a scratch path reproduces `results_pomcp_exploration_selected.csv` exactly.
- **Selections.** I checked by hand that the tuning-seed winners follow "max success, ties by reward":
  - The two MCTS-EFE ties at 0.97 (Tiger) and 0.95 (Diagnosis) are broken by reward in favour of c=5.
  - POMCP selects Tiger c=50 (0.930), Diagnosis c=5 uniform (0.700), and Tileworld c=5 info-gain (0.060).
- **Evaluation-seed winners.** POMCP would take Tiger c=50, Diagnosis c=2, and Tileworld c=5 info-gain. MCTS-EFE would take c=5, c=5, and the default. So "On Tiger and Tileworld these are the configurations the evaluation seeds would also have selected, and on Diagnosis ... c=2" is correct, including for MCTS-EFE.
- **"The corrected planner observes less."** This holds against the prefix for every one of the 74 POMCP configurations in all five batteries. None observes more. Relative to the sign-fix/root-belief intermediate, the final planner observes more everywhere, but the note compares to the published prefix, so this is fine. The sentence was removed by batch 6 in any case.
- **Attribution to the subsidy.** "Artifacts of the subsidy" is supported. The sign fix alone, still with root belief, removes the Bandit lead (26.6% against EFE's 86.9%) and makes the tuned Tiger comparison significant (selected success p=0.0008, reward p=0.002).

## 3. Numbers (all checked against CSVs at stated precision)

All of the following are OK.

**Table `tab:pomcp` rows T2 to T5.** Values are obs, success, reward, and seed-level SE:

| Environment | Obs | Success | Reward |
|---|---|---|---|
| Tiger | 1.6434 | 89.16 | -3.5674 ± 0.1797 |
| Diagnosis | 3.1878 | 70.46 | -10.9118 ± 0.626 |
| Bandit | 1.3434 | 47.24 | +4.5799 ± 0.0854 |
| Tileworld | 0.047 | 2.6 | -48.487 ± 0.276 |

**Comparison paragraph (P1 to P3).**
- "Underperforming both EFE and Planning on reward and success rate on every environment" holds at 1,000 simulations and also at every budget. The closest case is Bandit POMCP(5000) at 62.1% and 5.56, against Planning at 71.0% and 5.75.
- Bandit: 47.2 ± 1.0, 86.9 ± 0.3, +4.58 ± 0.09, +6.27 ± 0.04, 5.11.

**Scaling paragraph (S1).**
- Diagnosis: 71.62 ± 0.875, 97.16 ± 0.269, 329.9 and 96.2 ms.
- Tiger: 89.54 ± 0.25.
- Bandit: 50.92 ± 1.09, 51.58 ± 1.13, 62.12 ± 1.18, +5.5595 ± 0.105.
- 182.06/31.61 = 5.76, so "roughly 5.8 times" is right.
- Tileworld maximum is 3.8%.

**MCTS-EFE and compute-matched (E1, E2).**
- MCTS-EFE(500) runs at 16.2, 17.0, and 17.5 ms per episode. POMCP(500) runs at 12.0, 13.0, and 13.6 ms. Exact-EFE at H=6 runs at 79.2 ms.
- 88.1 ± 0.19 with p = 4.43e-6.
- 13.87 s. The calibration slope gives 660.95, so 661 simulations and 32%.
- 88.0 ± 0.63, -4.804 ± 0.686, 13.88 s. 88.1 ± 0.19, -4.665 ± 0.189, 10.42 s. p = 0.886 and 0.853.
- "p<0.0001 in every comparison" holds: the maximum is 2.6e-5.
- "With no other battery running" holds. The compute-matched log covers 14:00:44 to 14:01:58, after the Tileworld sweep ended at 14:00:26 and before `p3_run_pomcp` started at 14:12:32.

**Sweep paragraph (X1 to X4).**
- Tiger c=50: 93.2 ± 0.49, +0.391 ± 0.523. Constants up to 10 give 87.3, 88.1, 89.0, and 88.4, so "87.3 to 89.0" is right. Against the default, p = 1.59e-4 and 2.07e-3, both Holm-significant.
- Selected Tiger: p = 1.0e-4 and 5.1e-4, with +4.326 ± 0.284. All six selected tests are significant.
- Selected Diagnosis and Tileworld: 65.6 ± 1.4 and 8.2 ± 0.64, against 94.7 ± 0.41 and 95.4 ± 0.58.
- Diagnosis c=2: 69.1 ± 1.67.
- "At most 0.09 scans at c≥5": the counts are 0.088, 0.025, 0.017, 0.011, and 0.013.
- "Succeeds on 1.8 to 3.1%" is right. "c=1 reaches 7.1% with about one scan" is right (1.042).
- Info-gain against uniform at c=5: Diagnosis p = 0.573. Tileworld success p = 1.79e-4 is Holm-significant, and reward p = 0.0120 is not.
- The sweep table reproduces byte-identically from `build_mcts_ablation_tables.py --out-dir /tmp`.

**Appendix Y (Y1 to Y4 and the two inline follow-ups).**
- "More than eighty points behind": 95.4 - 8.2 = 87.2.
- "Above twenty-five points on Diagnosis": the minimum is 94.2 - 69.1 = 25.1.
- "Above eighty points on Tileworld": the minimum is 95.4 - 8.2 = 87.2.
- Diagnosis H=5 at 200 simulations: 65.5 ± 2.13, with p = 1.087e-4.
- Tileworld: 2.6 ± 0.43 and 3.9 ± 0.48, both at 0.088 scans. The gaps are 92.8 and 91.5, so "91 to 93" is right. p < 1e-9 at both budgets.

**Main body.**
- 843: "MCTS-EFE remains significantly ahead on Tiger success and reward" is right.
- 750: the current wording, "under a rule recorded before the runs reported here", is literally true. The batch 5 wording was also true.

## 4. Citations

Both citation changes are OK.

- `friston2015` is Friston, Rigoli, Ognibene, Mathys, FitzGerald, and Pezzulo, "Active inference and epistemic value", Cognitive Neuroscience 6(4) 187–214. It decomposes EFE into extrinsic (pragmatic) and epistemic value, so it fits both sites (JAIR lines 116 and 141).
- `sunberg2018` is Sunberg and Kochenderfer, ICAPS 2018. It introduces POMCPOW and PFT-DPW, both built on (double) progressive widening.
- Both keys exist in `full_paper_jair.bib` and in the LNCS embedded `thebibliography`.

## 5. Conventions

- The changed text is identical in both masters. The only differing added lines are the JAIR-only structured abstract and checklist item.
- There are no prose semicolons in added lines and no rhetorical emphasis. "Crucially" at 1562 predates this batch.

## Defects (4)

1. **JAIR 2156 / LNCS 2460, stale mechanism.**
   - Quoted text: "Semi-informed rollouts still cannot identify which of the 6 scans to perform."
   - What is wrong: this describes the pre-fix planner, which scanned 1.7 and 3.3 times per episode in the prefix `results_mcts_efe.csv`. The corrected POMCP barely scans at all, 0.088 per episode at both budgets (`results_mcts_efe.csv`). Its success, 2.6% and 3.9%, sits at the 1/36 ≈ 2.8% rate of committing on the uniform prior. The failure is not scanning, not a wrong choice among scans.
   - Replacement: "With almost no scans, POMCP commits on a nearly uninformed belief, and its success sits near the $1/36$ rate of an uninformed guess."
2. **JAIR 1596 / LNCS 1900, "no better than".**
   - Quoted text: "On Tiger, POMCP(5000) reaches $89.5 \pm 0.3\%$, no better than at 1{,}000 simulations."
   - What is wrong: 89.54% is nominally above 89.16% at 1,000 simulations. The difference is within sampling error (0.38 pp against a combined SE of 0.30 pp), but "no better" reads as "not higher".
   - Replacement: "On Tiger, POMCP(5000) reaches $89.5 \pm 0.3\%$, within sampling error of its $89.2 \pm 0.2\%$ at 1{,}000 simulations."
3. **JAIR 1562 / LNCS 1866, unqualified "gap".**
   - Quoted text: "The gap is smallest on Tiger, which has a single observation action, and larger on Diagnosis, Bandit, and Tileworld"
   - What is wrong: this holds for success (10.2, 26.7, 39.7, and 69.3 pp against EFE). On reward, Bandit's gap (6.27 - 4.58 = 1.69) is smaller than Tiger's (5.19 + 3.57 = 8.76).
   - Replacement: "The success-rate gap is smallest on Tiger, which has a single observation action, and larger on Diagnosis, Bandit, and Tileworld"
4. **JAIR 1594 / LNCS 1898, untested cause.**
   - Quoted text: "POMCP collapses to 2.6\% success with almost no scans ($0.05$ per episode), as the 36 commit actions and 6 scan actions create a branching factor that 1{,}000 simulations do not resolve."
   - What is wrong: the "as ..." clause states an untested cause as fact. The measured behavior is near-chance commitment without scanning (2.6% against 1/36 ≈ 2.8%), which is the same point as defect 1.
   - Replacement: "POMCP collapses to 2.6\% success with almost no scans ($0.05$ per episode), close to the $1/36$ rate of committing without information, plausibly because the 36 commit actions and 6 scan actions create a branching factor that 1{,}000 simulations do not resolve."

## Advisories (not counted)

- **A1. Disclosure consistency (Pat's call).** Batch 6 dropped the statement that the selection rule and its grid were written after the uncorrected canonical-seed sweep had been inspected. The SARSOP TOST retains the analogous "margins chosen after an earlier comparison had been inspected, so retrospective". The current wording is true, and the influence of a generic rule is small. A hostile referee comparing the two passages might still call the treatment inconsistent. The ledger records this as a deliberate choice under Pat's 2026-09-29 instruction.
- **A2. Timings are provisional.** Every timing and ratio (329.9/96.2 ms, 5.8 times, 16–18, 12–14, 79 ms) was verified against the concurrent-run CSVs. The `p3` clean reruns will change them. When they land, re-verify these sentences, remove the concurrency caveat as the ledger plans, and confirm the outcome columns stay bit-identical to `parts/results_pomcp.csv` and `parts/results_mcts_efe.csv`.
- **A3. Appendix Y timings carry no caveat.** Appendix Y's 16–18 and 12–14 ms figures are not covered by the "in this appendix" caveat, which sits in the POMCP appendix. This becomes moot once A2 is done.
- **A4. `merge()` lacks provenance guards.** It could assert that the parts share seed lists and episode counts and contain no duplicated environments.
