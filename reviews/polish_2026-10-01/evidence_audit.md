# Independent evidence audit, 2026-10-01

This is a factual audit of the source available during the polish pass, not an acceptance verdict. Prior referee decisions and the polish brief were not used as verification. No manuscript, implementation, or result file was edited, and no experiment was rerun. A final-source assessment remains pending.

## Scope and method

Read the relevant portions of both live masters, with detailed claim checks against `paper/full_paper_jair.tex`, the POMCP and RockSample implementations, the SARSOP TOST producer, and the target-reference producer. Read the result CSVs directly. Recomputed paired TOST from the episode-matched per-seed archive using SciPy Student t distributions. Independently solved every held-out target-reference LP with `scipy.optimize.linprog`, rather than calling the project's mixture solver, and recomputed paired gaps and SE from the archived family/reference seed means. Recomputed interval endpoints and counted distinct budgets by `(env, budget)`, dropping Tiger's duplicate gap row.

The bounded unit-test command was:

```text
.venv/bin/python -m pytest tests/test_pomcp_cost_sign.py tests/test_pomcp_rollout_belief.py tests/test_stats_seed.py tests/test_rocksample_holm.py -q
```

Result: 14 passed in 0.07 s, with 21 existing library/statistical warnings. This verifies targeted mechanics, not full experimental reproducibility. The audit uses the archived measurements and does not independently repeat the expensive POMCP batteries or SARSOP solves.

## Supported headline results

1. **Episode-matched equivalence is numerically supported.** In `results/results_tost_sarsop_episode_paired_per_seed.csv`, each environment has 20 seed means. For differences EFE minus SARSOP, Diagnosis has mean 0.1118, SE 0.0899124603506977, paired TOST p = 3.2030924059701387e-9, and paired 90% CI [-0.04367059, 0.26727059]. Bandit has mean 0.0435, SE 0.03132835440098449, p = 4.5771762405518045e-12, and 90% CI [-0.01067089, 0.09767089]. Tiger's differences are identically zero, so its paired calculation is degenerate. The margins are 1, 1, and 0.5, respectively. The main-text rounded values are correct. The producer reseeds episode e of seed s at `10000*s+e`, so hidden states and observations are matched until policies diverge. The caveat about matching only while actions agree is accurate.

2. **The target-reference shortfall count is correct, with an important frozen-reference qualification below.** Independently solving each held-out LP with equality usage B reproduces every held-out target gap and its seed-level SE to 1e-12. The archived per-seed gap strings are rounded to four decimals, so their reconstructed summaries match within 0.000051. Both held-out and fresh 95% interval endpoints agree with the stored gap plus/minus `t.ppf(.975,n-1)*SE` to 1e-12. Held-out shortfalls are Diagnosis interior_0.5 (B=9.534) and Bandit gap (B=4.712). Fresh shortfalls are Diagnosis interior_0.25 (B=7.719) and Bandit gap. Thus there are 2/11 distinct budgets on each stream and only Bandit's gap recurs.

3. **The cap-reference count also reproduces.** Both the held-out comparison and its frozen-reference fresh replication have eight negative intervals among eleven distinct budgets. Held-out rows are Tiger's three distinct budgets, Diagnosis interior_0.5 and interior_0.75, and Bandit interior_0.5, interior_0.75, and gap. Fresh replaces Diagnosis interior_0.5 with interior_0.25. Seven distinct budgets have slack caps, but only six of the eight significant held-out shortfalls are at slack budgets, because Bandit interior_0.25 is slack and not significant. The manuscript says seven budgets are slack, which is correct. The brief's shorthand that seven of eight shortfalls were slack is incorrect and must not propagate.

4. **Corrected POMCP headline values match the archive.** At 1000 simulations, `results/results_pomcp.csv` gives success/reward/observations of Tiger 0.8916 / -3.5674 / 1.6434, Diagnosis 0.7046 / -10.9118 / 3.1878, Bandit 0.4724 / 4.5799 / 1.3434, and Tileworld 0.026 / -48.487 / 0.047. These support the manuscript's rounded values and the statement that this configuration trails EFE and Planning on both displayed performance metrics.

5. **Selected POMCP comparisons are correctly reported.** `results/results_pomcp_exploration_selected.csv` gives Tiger success 0.982 versus 0.932, p = 0.0001000286, and reward 4.326 versus 0.391, p = 0.0005104196. All six selected success/reward comparisons have true Holm flags. Diagnosis's selected comparison is 0.947 versus 0.656 success, and Tileworld's is 0.954 versus 0.082. The manuscript preserves the fact that the candidate grid/rule was informed by an exploratory canonical-seed sweep even though the selection uses separate tuning seeds.

6. **The POMCP code implements the stated cost sign and path belief.** Both tree and rollout observation rewards subtract costs. Tree observation branches update the belief before calling the descendant simulation, and rollouts receive that belief. The depth-cap sampled-state oracle value and belief-expected rollout commit value remain visible implementation departures and are disclosed. The informed-rollout test does not isolate all search architecture differences. The manuscript generally scopes the result to the tested implementation rather than claiming state-of-the-art superiority.

## Required scoping fixes

### E1. Fresh evaluation is a replay of a held-out fit, not a new target-matched optimum

The target-reference producer fits mixture support and weights against held-out usage and reward, then holds them fixed on fresh seeds. The appendix says this accurately. The abstract and main-result paragraph can be read as saying the fresh comparator also has usage B and is the best fitted reference on that stream. It is neither. The fresh reference's observed usages all fall below B in this archive.

Recomputed from the full-precision held-out LP weights and `results/results_cpomdp_frontier_subsidy.csv`:

- Tiger targets 4.719, 5.070, 5.421 have fresh reference usages 4.543589, 4.893360, 5.243131.
- Diagnosis targets 7.719, 9.534, 11.349, 7.838 have fresh reference usages 7.451744, 9.113825, 10.931353, 7.560718.
- Bandit targets 5.510, 7.788, 10.066, 4.712 have fresh reference usages 5.283309, 7.666790, 9.712494, 4.568616.

For example, at Diagnosis B=9.534 the fresh family uses 9.258 and the reference uses 9.113825. This is useful out-of-sample replay evidence, but it is not an equality-usage comparison on the fresh stream. Do not change the result values or refit the reference as a polish fix. State that the two-shortfall count recurs when the held-out-fitted mixtures are replayed on fresh seeds, and explicitly say fresh realized usage need not equal B. Exact proposed wording is in `evidence_proposals.json`.

### E2. Tiger's reward-usage identity and zero sensitivity gaps are held-out facts

The target-reference paragraph says, "Because every Tiger policy here earns 10 minus its usage" and later "Every Tiger gap becomes zero." Both require held-out scope. The usage-matched sensitivity makes the **held-out mean** Tiger gaps zero (floating residuals at about 1e-15), but the fresh mean gaps are -0.045232, +0.037862, and -0.020099, with the duplicate middle row repeated. All fresh intervals still contain zero. Even on held-out data the individual paired seed gaps and their SE are not zero, only their fitted aggregate means are.

The fresh reward-usage identity is false. For Tiger lambda=0, fresh reward is 5.638 and usage is 4.142, so `10 - usage - reward = 0.220`, reflecting wrong-commit costs. The corresponding held-out figures are reward 5.684 and usage 4.316, with residual zero. Scope the identity to held-out policies in the reference support and say "Every held-out Tiger mean gap becomes zero."

### E3. Return explicitly to the predeclared comparison after the sensitivity paragraph

The usage-matched sensitivity has **one** held-out shortfall, Diagnosis interior_0.5. Bandit's held-out interval reaches approximately +0.001, so it no longer excludes zero. The next sentence, "The two remaining held-out shortfalls are ...", refers back to the comparison at B but does not say so. Prefix it with "In the predeclared comparison at B". The fresh counts are two in both analyses, but that coincidence does not remove the ambiguity.

### E4. A shared RockSample leaf rule does not prove comparisons are unaffected

The appendix says, "Every agent in the family shares the phantom cost identically, so within-family comparisons are unaffected." The first clause establishes a controlled common implementation, not invariance to changing that implementation. In `rho_aif/agents/rocksample_agents.py`, `_leaf_value` adds `move_cost * (grid_size - 1 - sim_pos[1])`. The final `sim_pos` depends on the branch's position, posterior beliefs, and greedy collection trajectory. `_evaluate` compares these continuations with immediate exit and adds the weight-dependent information reward to checking branches. Thus the phantom cost is not a common additive constant across all competing actions or policies. Removing it can change action choices differently at different weights. No removal sensitivity experiment was identified in the inspected artifacts. Replace the invariance claim with "Every agent in the family uses this same leaf rule, so the reported comparisons are conditional on it."

## Additional narrow implementation-calibration issues

These do not overturn the archived outcomes, but they should be qualified in a final paper.

- The POMCP appendix says its clairvoyant depth-cap return and expected-commit rollout return are "Both favorable or neutral to POMCP on these small instances." The code establishes optimism at the leaf and a conditional expected rollout payoff. It does not establish that either choice improves or preserves the *executed policy's* reward or success, because action-dependent value bias can change action rankings. No paired removal sensitivity is supplied for the observe-then-commit implementation. A precise replacement is: "The first gives an optimistic terminal value, and the second replaces a sampled payoff by its conditional expectation. Their effects on the resulting policy are not isolated here."

- The initial POMCP-versus-exact-EFE/Planning appendix paragraph calls that comparison "simulation-matched." Exact EFE and Planning enumerate their trees, and the main POMCP CSV gives them `sim_budget=0`; they have no matched simulation count. The MCTS-EFE versus POMCP experiment *is* simulation-matched. Replace the first occurrence only with a sentence distinguishing the fixed POMCP-budget comparison from the subsequent matching of two Monte Carlo methods.

- The reproducibility checklist's general statement that POMCP's internal stream is seeded per run conflicts with its own appendix exception. `run_pomcp.py` and `run_pomcp_exploration_sweep.py` explicitly use `vary_agent_seed=True`; `run_pomcp_compute_matched.py` does not. The MCTS appendix explicitly says that its battery uses a fixed internal seed. Preserve those protocols and qualify the checklist, rather than rerunning them as a wording change. The fixed-stream compute-matched producer was directly inspected in this audit; this distinction limits how broadly the uncertainty can be called variation over planner seeds.

## Interpretation of uncertainty

The paper discloses retrospective five-seed TOST margins, prospective added seeds, the partly non-blind fresh frontier set, target construction from calibration curves, and the post hoc usage-matched sensitivity. Those are appropriate design disclosures. The paired reference intervals are explicitly nominal pointwise plug-in intervals, omit support/weight reselection and multiple-budget correction, and are not population frontier coverage. The two-shortfall headline is therefore descriptive under the fitted-reference procedure, not a simultaneous inferential claim of two population failures. The Tiger rare-event limitation remains necessary. The 2.8-SE Diagnosis explanation is a rough rescaling of episode count, not an independent test that proves the observed discrepancy's cause. Current "consistent with seed-set variation" wording is appropriately weaker than a causal determination.

The evidence supports the main distinction between target calibration and reward optimization. Final review should verify the scoping fixes against both masters and ensure no claim of fresh equality matching or policy invariance reappears.
