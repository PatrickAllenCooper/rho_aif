# Referee report: hostile associate editor lens

Manuscript: `paper/full_paper_jair.tex` and `paper/full_paper_jair.pdf` (working tree, 2026-09-30, both modified 14:20). The PDF is 109 pages, and the references begin on page 38. Line numbers below refer to that working-tree `.tex`. The working tree also contains an uncommitted RockSample appendix trim, which removes the Flat-MC rows from the RockSample CSVs and tables and recomputes Holm-corrected flags.

## 1. Recommendation

**Major revisions.**

## 2. Summary

The paper makes two kinds of claim.

- **Formal.** A specified reward-based recursive EFE objective is the same policy as a rho-POMDP with information weight w=1, under stated conventions. Scale equivariance and monotone comparative statics hold for the weight. A projected dual controller converges when the usage target is stationary.
- **Empirical.** Calibrating w to an expected sensing-usage target works, and the untuned w=1 is a useful default. The abstract and introduction summarize the empirical side in three headline statements. Held-out usage targets are met within 0.13 observations. Reward shortfalls against a sampled constrained reference appear on eight of eleven distinct budgets, and this count replicates on fresh seeds. The weight w=1 lies in the reward-maximizing bracket on three of five swept environments.

Most of the numbers I checked reproduce from the committed CSVs. The disclosures listed in the brief are present and honest. Two findings still block acceptance.

- **The Diagnosis equivalence claim depends on which evaluation stream you use.** The paper's only comparison of the w=1 policy against unpenalized SARSOP that is paired episode by episode is the held-out budget stream. On that stream the w=1 plateau policy trails SARSOP by 1.01 reward, with 95% interval [-1.51, -0.50]. The point estimate lies outside the TOST margin of ±1.0. The canonical-stream n=20 estimate is +0.15, and it is statistically incompatible with the paired one. The main body reports only the canonical result and describes its nominal-seed pairing as confirming positive covariance.
- **The headline shortfall count mixes two different things.** Six of the eight shortfalls occur at budgets where the constrained reference is just unpenalized SARSOP, whose usage is already below the target. There, a shortfall measures the cost of the target itself, not inefficiency of the calibration method. At the four budgets where the cap binds, the shortfall count is two, and only one of those (Bandit's gap budget) replicates on fresh seeds. For a method the paper frames as targeting usage rather than capping it, the reference at those six budgets is also the wrong comparator.

Smaller required items: an overstated mechanism claim for the Epistemic-only ablation, an overgeneralization from RS[11,11] that ignores a disclosed leaf-rule bias, and a false monotonicity statement about success in the weight sweep.

## 3. Strengths

- **The formal result is scoped with unusual care.** Proposition 1 states its four assumptions inside the statement. The paper calls it a notational bridge rather than an optimality theorem. Line 213 and Appendix `app:theory_setup` explicitly restrict it to the recursive hidden-state-information formulation.
- **The calibration machinery is clearly distinguished.** The crossing threshold, the grid bracket, and the endpoint mixture are kept apart (lines 95 and 381). The paper states when the bracket is undefined.
- **Most prose numbers are right.** Almost every number I traced in the main body matches its CSV at the stated precision (Section 6 lists them).
- **The constrained reference is presented honestly.** It is described as a sampled feasible envelope, not a certified frontier (line 609). The paper also says "w is not that multiplier" (line 607), consistent with the convention.
- **Negative results are reported.** RS[11,11], Tileworld's domination by w=20, Posterior-vote's tie on Bandit, and the fresh-seed Diagnosis non-replication are all in the main body.

## 4. Required changes

### R1. Diagnosis equivalence with SARSOP is contradicted by the paper's own episode-paired comparison

**Current text (line 602):**
> "A paired five-seed sensitivity analysis confirms that covariance is positive here and the unpaired analysis is conservative. [...] The conclusion is equivalence within these fixed margins on these three environments, rather than universal near-optimality of $w{=}1$."

Also line 628: "Its estimated gap from EFE is zero on Tiger, $-0.041$ on Diagnosis, and $-0.005$ on Bandit, small relative to the estimates' standard errors."

**What is wrong.**

The canonical TOST "pairing" is not real pairing. Line 602 itself says: "The nominal seed lists are shared, but differing policies consume random draws differently." So the pair members do not see the same episodes.

The only comparison in the artifacts that shares episodes between the w=1 policy and unpenalized SARSOP is the held-out budget stream. It uses per-episode `env.reset` seeds, seeds 7 to 11, and 100 episodes per seed. On Diagnosis, the calibration plateau from w=0.316 to w=19.3 contains w=1. Its usage there is 9.696, which matches the canonical EFE usage of 9.66, so this is the w=1 policy. The supporting rows:

- `results_budget_frontier_heldout_reference.csv`, Diagnosis, `best_feasible_mixture` at B=11.349 (this is the plateau policy, with q=1): reward -2.216 against SARSOP λ=0 at -1.208. Paired gap -1.008, SE 0.181, 95% interval [-1.511, -0.505].
- The per-seed differences are -0.82, -1.00, -1.12, -0.50, and -1.60, so every seed goes the same way.
- `results_cpomdp_frontier_heldout.csv`, Diagnosis λ=0, gives the per-seed SARSOP rewards: -0.90, -0.80, -3.46, 0.08, -0.96.

Compare `results_tost_sarsop_n20_robustness.csv`. Diagnosis EFE minus SARSOP is +0.146, with SE 0.145 unpaired and 0.104 under nominal pairing. The two estimates of the same population difference are about 1.15 apart. Their combined standard error is about 0.21, so they are incompatible at roughly five standard errors.

Each stream's unpaired means are individually plausible. Held-out w=1 is -2.216 with a seed SE of about 0.7, and held-out SARSOP is -1.208 with SE 0.59. The conflict appears only once the comparison is truly paired, and the truly paired design is the one that should be trusted for a difference.

So one of the following must be true:

1. Some protocol difference between the streams changes the relative performance of the two policies. Candidates are per-episode seeding versus once-per-seed seeding, or the Planning+IG family member versus the `EFEAgent` class.
2. One of the two sets of intervals is miscalibrated.

Either way, the main body's unqualified Diagnosis equivalence claim, and its statement that the pairing "confirms" conservativeness, do not survive. A hostile referee will find this from two CSVs the paper itself cites.

**Required action.**

1. Diagnose the discrepancy. The minimal check is to run `EFEAgent` and the SARSOP λ=0 policy with the held-out per-episode seeding on the n=20 seed set, paired by episode, and report the paired TOST. The paper already has the machinery in `run_frontier_reference_heldout.py`.
2. Report the result in Appendix `app:sarsop_details`.
3. Qualify the main-body sentence in the same number of words.

**Concrete replacement for line 602** (for the case where the diagnosis confirms a stream effect; the length is unchanged):
> "Nominal seed lists are shared, but differing policies consume random draws differently, so these pairings are not episode-matched. On the held-out stream, where episodes are matched, the Diagnosis plateau containing $w{=}1$ trails unpenalized SARSOP by $1.01$ ($95\%$ interval $[-1.51,-0.50]$), outside the margin (Appendix~\ref{app:sarsop_details}). Equivalence therefore holds on Tiger and Bandit and is stream-dependent on Diagnosis."

Also delete "A paired five-seed sensitivity analysis confirms that covariance is positive here and the unpaired analysis is conservative." Add ", on the canonical stream" to the line 628 sentence.

### R2. The headline shortfall count must separate slack budgets from binding ones

**Current text (line 81, abstract):**
> "Against a sampled constrained reference, nominal pointwise paired intervals show reward shortfalls on eight of eleven distinct budgets. [...] The count replicates on fresh seeds but not every Diagnosis row does"

**Current text (line 677):**
> "Under that fitted comparison, negative $95\%$ intervals exclude zero at nine of twelve attainable budgets, or eight of eleven distinct budgets after the Tiger duplicate is removed."

**What is wrong.** From `results_budget_frontier_heldout_reference.csv` (the `mixture` rows) and the `reference_support` column, the eleven distinct budgets split into two groups.

**Slack budgets.** At seven budgets the reference is SARSOP λ=0 with q=1. The unconstrained reward-optimal policy already uses less than B, so the constraint does not bind:

- Tiger 4.719, 5.070, 5.421
- Diagnosis 11.349
- Bandit 5.510, 7.788, 10.066

Six of these seven exclude zero. Bandit 5.510 does not. Appendix line 1929 already names these budgets as the ones where "the usage constraint is slack".

**Binding budgets.** At the other four the envelope mixes λ=0 with a positive λ:

- Diagnosis 7.719, 9.534, 7.838
- Bandit 4.712

Only two of these four exclude zero on held-out seeds: Diagnosis 9.534 and Bandit 4.712. On fresh seeds (`results_budget_frontier_fresh_seed_replication.csv`) the result also changes:

- Diagnosis 9.534 no longer excludes zero: +0.021, interval [-0.63, 0.67].
- Diagnosis 7.719 now excludes zero.
- Diagnosis 7.838 sits at the boundary, with upper limit +0.0002.

So the only binding-budget shortfall that is robust across both streams is Bandit's gap budget.

At slack budgets a shortfall is close to guaranteed. A policy that spends more than the reward-optimal usage must earn less reward than the reward-optimal policy. It does not show that calibration is an inefficient way to meet the target. The abstract's phrase "shortfalls against a sampled constrained reference" invites exactly the reading the data do not support: that the method underperforms a constrained optimizer. The claim "the count replicates" is literally true, but it rests mainly on the six near-mechanical slack shortfalls.

**Concrete replacement for line 677** (net length about unchanged):
> "Under that fitted comparison, negative $95\%$ intervals exclude zero at eight of eleven distinct budgets. Six of these are budgets above the unconstrained reference's usage, where the reference is unpenalized SARSOP and the shortfall is the cost of the target itself. At the four budgets where the cap binds, two intervals exclude zero, and only Bandit's gap budget does so again on ten fresh seeds (Appendix~\ref{app:frontier_details})."

**Concrete replacement for the abstract sentence:**
> "Against a sampled constrained reference, nominal pointwise paired intervals show shortfalls on eight of eleven distinct budgets, six of them at targets above the reference's own usage, and a binding-cap shortfall that replicates on fresh seeds only on Bandit."

### R3. Targets above the unconstrained usage have no matching reference

**Current text (line 607):**
> "We replace observation reward $-\mathrm{cost}_j$ by $-(\mathrm{cost}_j+\lambda)$ and solve with SARSOP over a $12$-point penalty grid in $[0,100]$."

**Current text (line 609):**
> "[...] obtained by maximizing their mixture reward subject to mixture usage at most $B$. [...] the reference is flat at the largest sampled reward once the cap is slack."

**What is wrong.** The paper frames calibration as meeting an expected usage target, $\mathbb E[U]=B$, not as optimizing under a cap. That framing is correct and was deliberately adopted. But the only reference is a cap, $\mathbb E[U]\le B$, and it is built from a penalty grid restricted to λ≥0. For every target above SARSOP λ=0's usage, which is seven of eleven budgets, the reference ignores the target. The paper therefore never answers the question its own framing raises: among POMDP policies that do meet the target, how far below the best one is the calibrated family?

The appendix's "best target mixture" (line 1925) answers this only within the calibration grid, not within the POMDP policy space. At Bandit's gap budget it already shows that the endpoint mixture leaves 0.32 reward on the table relative to another grid mixture meeting the same target (line 670).

**Required action.** Pick one of the following.

- **(a)** Extend the SARSOP sweep on Tiger, Diagnosis, and Bandit to a signed per-observation price, meaning λ<0 subsidies that push usage above λ=0's usage. Compute the equality-constrained envelope (mixture usage equal to B) at the seven slack budgets. Report it in Appendix `app:frontier_details` with the same paired intervals.
- **(b)** If that is out of scope, add a limitation sentence in the same place.

For (b), append to line 609:
> "Because the penalty grid is nonnegative, the envelope does not estimate the best policy meeting a target above the unpenalized policy's usage, so it cannot separate the cost of such a target from inefficiency of the calibrated family."

Option (b) is the minimum, and it adds one sentence to the main body. To offset it, the sentence at line 609 beginning "We do not assume that finite-state strong-duality results" can move to Appendix `app:cpomdp_details` without loss.

### R4. The Epistemic-only ablation is determined by the units, not by a mechanism

**Current text (line 749):**
> "The Epistemic-only ablation commits immediately at chance-level success on all three core environments and Tileworld. Removing the pragmatic term therefore causes degenerate non-exploration in this implementation."

**What is wrong.** `rho_aif/agents/epistemic_only.py` sets G(commit)=0 but keeps the observation cost: `_efe_observe` returns `self.obs_costs[obs_action] - info_gain + expected_continuation`. With that objective, an observation is taken only if the cumulative information gain it leads to exceeds its cumulative cost. In bits, this cannot happen in any of these four environments:

| Environment | One-step information gain (bits) | Observation cost | Horizon | Prior entropy (bits) |
|---|---|---|---|---|
| Tiger (accuracy 0.85) | 1 - H(0.85) ≈ 0.39 | 1 | not a factor | 1 |
| Diagnosis | at most 0.278 | 1 | 3 | 2 |
| Bandit | at most 0.278 | 0.5 | 2 | 2 |
| Tileworld | at most 0.278 | 1 | not a factor | not a factor |

For Tiger, even the total prior entropy (1 bit) cannot pay for a single observation. For Diagnosis at H=3, total information gain is at most 0.83 bits against 3 units of cost. For Bandit at H=2 it is at most 0.56 bits against 1 unit.

So immediate commitment is analytically forced by the cost-to-bit exchange rate. Appendix line 1023 effectively concedes this for Testbed ("Testbed's observation is cheap enough that information gain alone clears its cost"). The result says nothing about the role of pragmatic value in driving exploration. Calling it "degenerate non-exploration caused by removing the pragmatic term" overstates what the ablation shows.

Separately, the module docstring says the agent commits "only when no observation action offers positive information gain", which disagrees with the code. This is an optional fix.

**Concrete replacement (same length):**
> "The Epistemic-only ablation commits immediately at chance-level success on all three core environments and Tileworld. Its outcome is fixed by the units, since each observation there costs more than the total information in bits it could buy (Appendix~\ref{app:core_details})."

### R5. The RS[11,11] generalization ignores a disclosed leaf-rule bias

**Current text (line 792):**
> "Larger state space therefore does not itself increase the value of information weighting. At feasible search depths, distant useful checks lie beyond the tree, and the shared leaf rule values untouched rocks at zero under the uniform prior. It also charges a phantom trip to the east edge before exit, although this variant allows exit anywhere, biasing depth-capped continuations toward early exit."

**What is wrong.** The paragraph states a general conclusion and then, two sentences later, discloses that the shared leaf rule charges a cost the environment does not impose, and that this biases the planner toward early exit. The RS[11,11] result is therefore confounded by a leaf-value error that affects exactly the information-seeking behavior being evaluated. It cannot support a general statement about how state-space size interacts with information weighting.

**Concrete replacement for the first sentence:**
> "With this shared leaf rule, a larger state space therefore does not by itself increase the value of information weighting."

A more robust alternative is to correct the leaf rule to charge the exit actually available and rerun RS[11,11]. That is optional.

### R6. "Success favors larger weights throughout" is false at the canonical weight

**Current text (line 768):**
> "Success favors larger weights throughout this sweep, with its maximum at the upper grid endpoint $200$ on all five environments."

**What is wrong.** `results_pareto_sweep.csv` shows success falling as the weight rises from 0.5 to 1:

- Bandit: 89.44% to 86.92%.
- Tileworld: 74.76% to 72.04%, then 72.00% at w=2.

These drops sit exactly at the weight the paper recommends as a default. The maximum at w=200 does hold on all five environments.

**Concrete replacement:**
> "Success reaches its maximum at the upper grid endpoint $200$ on all five environments, although it dips from $w{=}0.5$ to $w{=}1$ on Bandit and Tileworld."

## 5. Optional suggestions

1. **"Bracket" is overloaded.** The abstract (line 81) and line 834 use "reward-maximizing (tied) bracket" for a run of reward-tied grid weights, while "bracket" elsewhere means the crossing bracket (w_lo, w_hi] of Definition PI-3. Line 766 already uses "reward-maximizing run of sampled weights". Use "run" in the abstract and at line 834 as well.
2. **The Champion attribution overreaches.** Lines 213 and 1650 describe \citet{champion2024} as a "taxonomy" in which the paper's objective is "the recursive hidden-state-information formulation". Champion et al. (Neural Computation 38(3), 2026) classify EFE expressions by their root definitions and prior-preference restrictions, as line 144 correctly says, not by recursive versus non-recursive planning. Rephrase lines 213 and 1650 to match line 144, for example: "the hidden-state-information expression among those \citet{champion2024} derive, evaluated recursively."
3. **The held-out usage test is close to automatic.** Line 81's "met on held-out seeds to within 0.13 observations" is a test of Monte Carlo stability of U(w) across seed sets. Once the mixture is fit on calibration seeds, it is expected to pass. Say so in one clause, so that readers do not take it as independent evidence for the method.
4. **The heuristic ties or beats EFE on every RockSample instance** (`results_rocksample_*.csv`). Line 792 says so only for RS[7,8] and RS[11,11]. A reader deciding whether to use EFE on RockSample-like tasks should see this in the table caption.
5. **Confirm the trimmed RockSample CSVs by rerunning their producer.** The uncommitted working tree removes Flat-MC rows by editing the CSVs and recomputes Holm flags via the new `--refresh-stats`. This flips at least one flag: the RS[7,8] Bad comparison between Planning and Rollout now reads True. Rerun `run_rocksample.py` from scratch, or at least diff the non-Flat-MC rows against HEAD, and confirm that no main-body sentence depends on a flipped flag.
6. **Unit-dependence is buried.** The central empirical recommendation, the untuned w=1, is w=1 in bits, or 1.44 in nats. The nat-canonical check (Appendix `app:nat_canonical`) shows this matters on Tileworld and Bandit. This caveat belongs in the conclusion's first sentence, not only in an appendix.
7. **The theoretical contribution is thin for JAIR.** Proposition 1 is, by the paper's own description, a notational identity. PI-1 and PI-2 are short. The weight of the paper rests on the empirical budget study, which is why R1 to R3 matter.
8. **Fix the `epistemic_only.py` docstring** to match its code (see R4).

## 6. What I verified

Unless stated otherwise, I verified these directly against the committed CSVs with pandas, not against prose.

**Frontier study (Section 6.9).**
- Maximum held-out usage error is 0.123, which supports "within 0.13".
- Three rows exceed B.
- The Bandit gap-budget usage error is 1.3 SE.
- Nine of twelve and eight of eleven held-out intervals exclude zero, and the same holds on fresh seeds.
- The Tiger rare-event figure of 0.66 is correct.
- Every Diagnosis and Tiger reward number at line 670 matches, as does the Bandit best-target-mixture comparison (5.94 ± 0.19 against 5.62 ± 0.21, usage errors 0.18 and 0.09).
- I derived the slack and binding classification in R2 from `heldout_reference_support` and the fresh-seed columns.

**SARSOP and TOST.**
- p_TOST values 0.0010, 0.0458, 0.0130.
- n=20 values 4.5e-10, 6.8e-7, 6.0e-11.
- Paired values 0.016 and 3.6e-5.
- The n=20 Diagnosis difference is +0.1464 (EFE -1.1454, SARSOP -1.2918).
- The held-out Diagnosis λ=0 per-seed rewards and the plateau paired gap are as quoted in R1.

**CPOMDP endogenous gaps.** 0, -0.041, -0.005. The usage-matched weights are 0.00, 0.45, and 1.07.

**Pareto sweep.**
- The tied runs are Tiger 0.01 to 20, Diagnosis 0.5 to 20, and Bandit 1 to 2.
- The Testbed trade-off is 6.4 percentage points of success for 0.11 reward.
- Tileworld: w=20 at -18.95 and 91.8% against w=1 at -21.53 and 72.0%.
- Success is maximized at w=200 on all five environments, with the non-monotonicities listed in R6.

**Other main-body results.** The main-table values, Inspection, Tileworld (6x6 p-values and 8x8 scaling), RockSample means and p-values at line 788 (16.47, 16.41, 15.96, 14.56, 21.85, 23.76, 12.31), RS[11,11] 13.23 and 28.66 ± 0.83, and POMCP horizons 12.94 to -54.78 from `results_rocksample_pomcp_horizon_11x11.csv`. That CSV predates the v2.1.0 POMCP fix, but CHANGELOG and the code confirm that the RockSample POMCP is a separate class that tracks the simulated belief and is unaffected.

**Dual control.** Recovery times of 157.3 and 51.2, and a maximum weight of 3.09.

**Bracket stability.** 19, 21, and 0.789.

**Scale collapse.** Tiger 4.368, plus the distractor values.

**Code.**
- `epistemic_only.py`: commit G=0, and observation G = cost - IG + continuation.
- I computed the one-step information-gain bounds in R4 by hand from each environment's likelihoods.
- Theory algebra: PI-5's running-average statement and the near-optimality interval algebra check out.

**Fresh reproduction.** I ran my own script, `/tmp/hae/repro.py`, with 5 canonical seeds and 1000 episodes each, using `run_experiment_multi_seed`:

| Run | Observations | Success | Reward | Seed-level SE |
|---|---|---|---|---|
| Diagnosis EFE | 9.6648 | 0.9716 | -1.3688 | 0.178 |
| Diagnosis Planning | 5.8576 | 0.8882 | -2.5656 | 0.196 |
| Bandit EFE | 5.1056 | 0.8694 | 6.2718 | 0.042 |

All three rows match the committed main-table values to every printed digit. The canonical pipeline is therefore reproducible, and the R1 discrepancy is not a stale-artifact problem.

**Bibliography.** I checked the entries this report relies on against publisher records.
- Da Costa et al. (Neural Computation 35(5), 2023; the exact-inference and β→∞ reward-dominant result) is attributed correctly at line 213.
- Champion et al. (Neural Computation 38(3):439-469, 2026) is correct as a record. Its characterization at lines 213 and 1650 overreaches (Optional 2).

**Availability.** The GitHub repository is publicly reachable.

**Conventions.** I found no semicolons in the quoted prose, no use of "exact" for SARSOP or CPOMDP, and no identification of w with the Lagrange multiplier.

---

## Re-review (2026-09-30, evening)

I re-checked the authors' responses against the working tree, not against their summary. The tree contained `paper/full_paper_jair.tex` and the rebuilt PDF (both 20:57), the new CSVs, the producers, and the 9.17.58 entry in `Guidance_Documents/full_paper_plan.md`.

### Revised recommendation

**Accept.**

### Verification of each response

**R1: resolved.**
- `full_paper_plan.md` 9.17.58 records the episode-matched check as predeclared, with its command, seed set, and margins written before the run.
- In `results_tost_sarsop_episode_paired.csv`, Diagnosis gives a paired difference of +0.1118 with SE 0.0899 on 20 seeds. From those figures, the upper one-sided t is (1 - 0.1118)/0.0899 = 9.9 on 19 degrees of freedom, which gives p of about 3e-9, as stated.
- Bandit gives +0.0435 with SE 0.031. Tiger is identical.
- The per-seed file, `results_tost_sarsop_episode_paired_per_seed.csv` (20 Diagnosis rows), reproduces the mean and the SE.
- Line 602 now says that seed-paired differences "are not episode-matched" and reports the matched check at about the same length. Line 628 carries "on the canonical stream".
- The frontier appendix (line 1935) reports the -1.01 ± 0.18 next to the +0.11 ± 0.09. It explains the gap as seed-set variation and notes that the seeds are non-blind for that pair.
- I accept that explanation, with one quantification the authors may wish to add (Optional A).

**R2 and R3: resolved, via option (a).**
- `results_cpomdp_frontier_subsidy.csv` and `results_budget_frontier_target_reference.csv` exist. Their subsidy grid, λ = -c·s with s from 0.1 to 0.98, matches the predeclared protocol in 9.17.58.
- The equality-constrained support reaches every target, with usage equal to B to three decimals, including Bandit 10.066 at λ in {-0.4, -0.475}.
- I recounted the target-gap intervals that exclude zero:
  - Held out: Diagnosis 9.534 at -0.757, interval [-1.19, -0.33], and Bandit gap at -0.587, interval [-1.13, -0.04].
  - Fresh: Diagnosis 7.719 at -0.560, interval [-1.09, -0.03], and Bandit gap at -0.503, interval [-0.74, -0.26].
  - That is two of eleven distinct budgets on each stream, with only Bandit's gap budget common to both, as the abstract (line 81) and line 677 now state.
- None of the four is at a budget where the cap reference is slack.
- On fresh seeds the reference is frozen from the held-out fit, so the fresh intervals are free of the reference-selection bias that the held-out ones carry. The text says that selection bias remains, which is adequate.
- Line 677 now splits the cap comparison into slack and binding budgets and states that a slack-budget gap "combines the cost of spending $B$ with any inefficiency of the family". That is exactly the distinction I asked for.
- The main table has a new Target gap column.

**R4: resolved.** Line 749 now reads "The units force this outcome, since in bits no observation there yields as much information as it costs." This is correct for the per-step comparison. Together with the bounded total entropy I computed, it also covers the multi-step recursion. I can no longer find the old docstring sentence in `epistemic_only.py`.

**R5 and R6: resolved.**
- Line 792 now opens with "With this shared leaf rule".
- Line 768 now reads "although it dips from $w{=}0.5$ to $w{=}1$ on Bandit and Tileworld". This matches `results_pareto_sweep.csv`.

**Optional items.**
- 1, 2, 4, and 8 are adopted.
- For 5, the authors' argument holds. The runner reseeds per agent and per seed and seeds each episode, so deleting the Flat-MC rows cannot change any other agent's rows. The one flipped Holm flag is cited nowhere.
- The rebuttals on 3, 6, and 7 are reasonable judgments, and I do not press them.

**Constraints.**
- The rebuilt PDF has 111 pages, and References still begins on page 38, so the main body has not grown.
- The new prose in lines 81, 602, 677, 749, 1903, and 1937 has no semicolons.
- "Exact" is not applied to SARSOP or CPOMDP.
- The full test suite gives 495 passed.

### Remaining required changes

None.

### Optional, non-blocking

- **A. The five-seed SE understates the spread.** The 20-seed episode-matched file gives a per-seed SD of 0.40 at 500 episodes. Scaled to the held-out design of 100 episodes, that implies a five-seed SE of about 0.40, not the 0.18 observed. The held-out -1.01 then lies about 2.8 such SEs from +0.11: unusual, but within what seed-set variation can produce. One clause at line 1935 saying the five-seed SE understates spread would make the "seed-set variation" reading quantitative rather than asserted.
- **B. The new artifacts are uncommitted.** These are `run_frontier_target_reference.py`, the three new CSVs, the per-seed file, and the modified `run_tost_sarsop.py`. README rows 162 and 166 already list them. They need to be committed with the manuscript so the paper's citations resolve at the submitted commit.
