# The Price of Information: w as a Shadow Price on a Sensing Budget

**Status**: Derivation notes + implementation + presentation fixes + first paper draft  
**Date**: July 22–23, 2026  
**Relation to paper**: Addresses the accepted IWAI 2026 paper's limitation that the canonical weight `w=1` in Planning+IG / EFE is not reward-scale invariant. Draft: `paper/price_of_information.tex`.

### Full-battery verdicts (see `research_plan.md` for detail)
1. **Curve collapse HOLD** — `U` vs `w/α` collapses across α∈{0.1,1,10} on Diagnosis and Bandit (100% of matched points within 2·SE). Crossing brackets in `w/α` units **coincide** across scales (set-valued shadow price at gap budgets); do not report point-valued `w*(B)` alone when `B` sits in a usage gap. Stage E breadth: Tiger also 100%/coincide but trivially (usage flat ~4.2 over the sampled range — no usable budget dial); Tileworld 90% within 2·SE with adjacent brackets sharing the knot w/α=5.8 where U straddles B within one SE (budget-at-knot noise; collapse itself is exact by PI-1).
2. **Prop 2 onset HOLD** — refined grid: onset bracket `(w_thresh, 1.03·w_thresh]` on both positive-threshold Testbeds (upper relative error 3%); `U=0` at and below `w_thresh`.
3. **Dual rescale HOLD** — usage pinned at `B=8.1`; after ×10 reward rescale, windowed `w` ratio ≈9.3. Stronger set-valued agreement: pre-rescale `w=0.29` lies inside the offline crossing bracket `(0.141, 0.323]`, and post-rescale `w=2.71` lies inside the ×10-scaled bracket `(1.41, 3.23]` — the controller lands in the offline solution set at both scales. Re-adaptation (rolling-20 within ±1 of B for 20 consecutive episodes): **157 → 45** with lr reset-on-shift (reset at episode 217; window=20, k=3, abs floor 0.5).

Shadow-price staircases remain supporting (report brackets + SEs; local non-monotonicity persists on Tiger/Diagnosis/Tileworld).

## Citation check (verified before writing)

| Claim used here | Verified source |
|---|---|
| Rational inattention: agents face a finite Shannon capacity / information-processing constraint that can substitute for adjustment costs | Sims, C. A. (2003). Implications of rational inattention. *Journal of Monetary Economics*, 50(3), 665–690. DOI: 10.1016/S0304-3932(03)00029-1 |
| Discrete-choice rational inattention yields (generalized) multinomial logit; costly information acquisition before choice | Matějka, F., and McKay, A. (2015). Rational inattention to discrete choices: A new foundation for the multinomial logit model. *American Economic Review*, 105(1), 272–298. DOI: 10.1257/aer.20130047 |
| Soft Actor-Critic with constrained formulation that automatically tunes the entropy temperature by dual gradient descent | Haarnoja, T., Zhou, A., Hartikainen, K., Tucker, G., Ha, S., Tan, J., Kumar, V., Zhu, H., Gupta, A., Abbeel, P., and Levine, S. (2018). Soft Actor-Critic Algorithms and Applications. arXiv:1812.05905. (This is the applications / auto-temperature paper. The earlier ICML 2018 paper introduces SAC with a fixed temperature and does **not** contain the dual auto-tuning rule.) |
| Constrained MDPs: Lagrangian / dual LP treatment of expected-cost constraints | Altman, E. (1999). *Constrained Markov Decision Processes*. Chapman & Hall/CRC. |

Check step: each row above was verified against the publisher / arXiv record on 2026-07-22 (Altman verified via publisher record / author PDF). Do not cite the ICML SAC paper alone for automatic temperature tuning.

## 1. Budgeted problem

Let π be a (possibly history-dependent) policy in an observe-then-commit or inspection POMDP. Write:

- `R(π)` for the expected episodic return under the environment reward (including observation costs already present in the MDP),
- `U(π)` for expected **sensing usage** per episode.

Two natural usage measures, both supported by the code:

1. **Count usage**: `U_count = E[number of observe / test actions]`.
2. **Cost usage**: `U_cost = E[sum of sensing costs paid]` (absolute cost magnitude).

**Heterogeneous costs (Stage D, July 23, 2026):** `DiagnosisEnv` supports per-test `test_costs`; `run_otc_episode` records the actual cost paid and `episode_sensing_usage` uses it directly (the count-times-mean-cost fallback remains for legacy results). On Diagnosis with test costs [0.5, 2.5], the mean cost per test `U_cost/U_count` varies 1.21–1.39 with `w` (13.5% relative spread), so cost budgets are not reducible to count budgets: the agent's test mix shifts toward the expensive test as `w` grows. Cost- and count-denominated brackets disagree accordingly. Figure: `figures/price_cost_budget.{png,pdf}`.

**Budgeted rho-POMDP (sensing upper bound):**

```text
maximize_π   R(π)
subject to   U(π) ≤ B
```

The operational question replaces "pick w" with "pick B": choose how much sensing the agent is allowed, then recover the weight that implements that budget.

## 2. Two dual stories (be precise)

### 2a. Information-floor dual (exact match to Planning+IG)

If the constraint is an **information floor** rather than a sensing upper bound,

```text
maximize_π   R(π)
subject to   E_π[I] ≥ B_I
```

the Lagrangian is

```text
L(π, w) = R(π) + w (E_π[I] − B_I).
```

For fixed multiplier `w ≥ 0`, maximizing `L` over π is exactly the Planning+IG objective already implemented in `PlanningInfoGainAgent` / `InspectionTreeSearchAgent(info_weight=w)`: expected reward plus weighted expected information gain. Complementary slackness says that at an optimum either the floor is met with equality or `w*=0`.

This is the clean theoretical identification of `w` as a Lagrange multiplier.

### 2b. Sensing-budget dual (operational inverse used in experiments)

The experiments target a **sensing upper bound** `U(π) ≤ B` (count or cost). The literal Lagrangian for that constraint is

```text
L(π, λ) = R(π) + λ (B − U(π)) = R(π) − λ U(π) + λ B,
```

i.e. an additive penalty on usage (equivalently, an increase in effective observation cost), **not** an additive `w · I` bonus.

Nevertheless, under Planning+IG the map `w ↦ U(w) := U(π*_w)` is empirically **non-decreasing** (higher info-gain weight buys more sensing). Therefore the equation `U(w) = B` can be solved for a unique bracketing interval by bisection. We call the solution `w*(B)` the **operational shadow price** of the budget: the Planning+IG weight that makes the agent spend about `B` units of sensing.

This is the same dual-control idea as SAC's automatic temperature (Haarnoja et al., 2018, arXiv:1812.05905): treat the coefficient as a dual variable and drive a monotone resource (entropy there, sensing here) to a target. It is **not** a claim that `w` is literally the Lagrange multiplier of the count constraint; that multiplier is `λ` above. The contribution is the budgeted formulation, the operational inverse `w*(B)`, scale-correct dual control, and empirical validation on this benchmark.

## 3. Monotonicity, grid solve, and bisection

**Working hypothesis:** for Planning+IG with weight `w ≥ 0`, expected sensing usage `U(w)` is *roughly* non-decreasing in `w`.

**Empirical caveat (July 22, 2026 probe):** on Diagnosis / Bandit / Tiger with finite samples, `U(w)` is a noisy step function and can locally decrease (discrete policy switches at finite horizon). Pure bisection is therefore unsafe as a default.

**Solver:** `solve_shadow_price` defaults to a log-spaced **grid search** minimizing `|U(w) - B|` (`grid_solve_usage_fn`). Bisection (`bisect_usage_fn`) remains available for synthetic monotone oracles and for Prop 2 boundary checks where a clean bracket is known.

**Interleaved settings (Stage B, July 23, 2026):** on RockSample RS[5,3], RS[7,4], and Inspection-N16 the estimated `U(w)` was nondecreasing at every sampled grid point — cleaner than the OTC staircases. Instrumental floors are large (`U(0)` = 3.81, 2.00, 22.42 checks respectively), so the unachievable-low-budget regime is prominent. Usage accounting: `family="rocksample"` in `estimate_usage` counts check actions; per-check cost is the uniform action cost.

Also: in environments with large instrumental VoI (Tiger, Diagnosis), `U(0)` is already large. Budgets `B < U(0)` are **unachievable** with nonnegative `w` (would require penalizing information gain). The solver reports `achievable=False` in that case.

Implementation: `rho_aif/budget.py`.

## 4. Recovery of Proposition 2 thresholds

Proposition 2 of the accepted paper gives closed-form weights at which the H=1 agent switches from immediate commit to one observation, and (separately) an H=2 over-observation upper threshold. In the dual language:

- At the **zero-observation budget boundary** (`B → 0+` under count usage), the smallest `w` that induces any observation is the Prop 2 lower threshold

```text
w*_thresh = [c − (p − 1/2)(R+ − R−)] / I_max
```

with `I_max = H(1/2) − H(p)` (see `experiments/run_thresholds.py`). Negative values mean any `w ≥ 0` induces observation.

- At the **one-vs-two observation boundary**, the Prop 2 upper threshold is the weight where a second observation becomes preferred at the post-first-observation belief.

Complementary slackness / threshold crossing: budgets that sit just above an integer observation count should recover these closed forms on Testbed/Tiger (binary, uniform prior) up to Monte Carlo noise.

## 5. Scale invariance (headline prediction)

If all rewards and costs are multiplied by `α > 0`, the MDP reward scale changes but the information-gain term (measured in bits/nats) does not. Fixed `w=1` therefore changes the observe/commit tradeoff across scales (already demonstrated in `experiments/run_reward_scaling.py`).

Predictions for budget-derived weights:

1. For a fixed count budget `B`, the induced usage under `w*(B; α)` stays pinned near `B` across `α ∈ {0.1, 1, 10}`.
2. The shadow price itself rescales: `w*(B; α) ≈ α · w*(B; 1)`, matching a price measured in reward units per bit.
3. When `B` falls inside a discrete usage gap, `w*` is **set-valued**: the scale-invariant object is the crossing bracket `(w_lo, w_hi]` in `w/α` units (`crossing_bracket` in `rho_aif/budget.py`), not a single argmin grid point.

Dual descent with a fixed usage target inherits the same invariance: when rewards are rescaled mid-run, a fixed `w` breaks the budget while the controller re-converges. Under learning-rate decay alone, re-adaptation after a mid-run rescale took 157 episodes on Diagnosis; with optional lr reset-on-shift it took 45.

## 6. Online dual control of w

Projected update that drives count/cost usage to budget `B` when `U` increases with `w`:

```text
w ← max(0, w + η_t (B − U_episode))
η_t = η0 / (1 + decay · t)
```

- If the episode overspent (`U > B`), decrease `w`.
- If it underspent (`U < B`), increase `w`.
- Project onto `w ≥ 0`.

**Shift-aware reset** (optional, `reset_window` set): when `η_t < η0/2` and the last `reset_window` usages have `|mean − B| > max(k·SE, abs_floor)`, set `t ← 0` (restore `η_t` to `η0`) and cool down for one window. Experiment defaults: window=20, k=3, abs_floor=0.5. Result on Diagnosis ×10 mid-run rescale: re-adaptation 157 (decay-only) vs 45 (reset); single reset at episode 217. Figure: `figures/price_dual_reset.{png,pdf}`.

**Multi-seed confirmation (Stage C, July 23, 2026):** 10 controller seeds per variant on the same protocol. Re-adaptation 53.3 episodes, 95% CI [48.7, 57.9] (reset, 10/10 recovered, one reset each) vs 126.8, CI [90.5, 163.0] (decay-only, 8/10 recovered — two seeds never re-adapted within the run). CIs disjoint. Post-rescale steady-state `|U − B|`: 0.11 vs 0.50. Figure: `figures/price_dual_multiseed.{png,pdf}`.

This mirrors SAC's dual temperature update (Haarnoja et al., 2018, arXiv:1812.05905), with sensing usage in place of policy entropy and `B` in place of the target entropy. Implementation: `rho_aif/agents/dual_descent.py::DualWeightAgent`.

Sign note: an update written as `w ← w + η (U − B)` has the wrong sign for an upper-bound usage target when `w` encourages sensing. The code uses `(B − U)`.

## 7. The price EFE pays

EFE corresponds to Planning+IG at the canonical weight `w=1` (Proposition 1 of the accepted paper, under the paper's reward encoding). Inverting the usage map gives the **implicit budget**

```text
B_EFE := U(w=1).
```

Reporting `B_EFE` per environment gives an operational reading of the canonical weight: EFE is the policy that spends whatever sensing `w=1` buys in that reward scale.

## 8. Positioning and contribution boundary

Prior art using the same dual trick:

- **Rational inattention** (Sims 2003; Matějka and McKay 2015): capacity / mutual-information costs as the primitive; actions chosen under costly information.
- **SAC auto-temperature** (Haarnoja et al., 2018, arXiv:1812.05905): dual gradient descent on a Lagrange multiplier to hit a resource target (entropy).

What is **not** claimed as novel: the abstract idea of dualizing a resource constraint.

What this project contributes:

1. Budgeted formulation tied to rho-POMDP / Planning+IG / EFE on this benchmark.
2. Operational inverse `w*(B)` via bisection, with Prop 2 thresholds as boundary checks.
3. Scale-invariant dual control of `w` under reward rescaling.
4. Implicit-budget reading of EFE's `w=1`.

## 9. Formal propositions (Stage A draft for the full paper)

Drafted here first per the Stage A protocol in `full_paper_plan.md`; port to LaTeX during assembly (Stage H). Numbering PI-1..PI-4 is provisional. Every statement below is checked against the recorded empirical caveats: rough monotonicity, gap budgets, unachievable low budgets, and the usage ceiling.

### Setting and assumptions

The Planning+IG agent at belief `b` enumerates depth-`H` plans; a plan's value is the expected sum of environment rewards along the plan (commit rewards, penalties, observation costs) plus `w` times the plan's cumulative expected information gain (entropy in bits, base 2, matching the implementation). The agent takes the argmax action and re-plans each step (receding horizon).

- **(A1) Scale-free tie-breaking.** Argmax ties are broken by a fixed rule independent of the reward scale (the implementation uses first-index `argmax`).
- **(A2) Pragmatic rescaling.** The `α`-rescaled environment multiplies all pragmatic quantities — commit rewards, penalties, and observation costs — by `α > 0`. Observation models and belief updates are untouched, so information gain is unchanged.

### Proposition PI-1 (exact scale equivariance of the implemented agent)

Under A1–A2, for every `α > 0` and `w ≥ 0`, the agent facing the `α`-scaled environment with weight `αw` selects the same action as the agent facing the unscaled environment with weight `w`, at every belief. Consequently the closed-loop policies coincide, the induced usage distributions are identical, and

```text
U_α(αw) = U(w)   exactly (not just in expectation).
```

**Proof.** For any plan, the `α`-scaled value is `α·(pragmatic sum) + αw·(IG sum) = α·[pragmatic sum + w·IG sum]`, i.e. `α` times the unscaled value. Positive scaling preserves the argmax set; A1 breaks any ties identically. By induction over decision points the closed-loop policies are equal, and since the environment stochasticity is the same, so are the trajectory and usage distributions. ∎

**Corollaries.**
1. Curve collapse is a theorem for the implemented agent: `U` plotted against `w/α` is the same curve at every scale. The empirical 2·SE collapse (Diagnosis, Bandit) measures Monte Carlo noise only, which is why it HOLDs.
2. Crossing brackets rescale as sets: `w*(B; α) = α · w*(B; 1)`, including at gap budgets where `w*` is interval-valued.
3. Fixed `w = 1` at scale `α` is behaviorally identical to `w = 1/α` at scale 1. The implicit EFE budget therefore drifts with scale as `B_EFE(α) = U(1/α)`. This is the precise sense in which the canonical weight is not scale-invariant.

### Proposition PI-2 (monotone comparative statics for exact maximizers)

Let `Π` be any fixed set of plans or policies. For `w ≥ 0` let `π_w ∈ argmax_{π∈Π} R(π) + w·I(π)`, where `I` is cumulative expected information gain. Then for `w₂ > w₁`:

```text
I(π_{w₂}) ≥ I(π_{w₁})    and    R(π_{w₂}) ≤ R(π_{w₁}).
```

**Proof** (interchange argument). Optimality of `π_{w₁}` at `w₁` and of `π_{w₂}` at `w₂` gives `R(π_{w₁}) + w₁ I(π_{w₁}) ≥ R(π_{w₂}) + w₁ I(π_{w₂})` and `R(π_{w₂}) + w₂ I(π_{w₂}) ≥ R(π_{w₁}) + w₂ I(π_{w₁})`. Adding yields `(w₂ − w₁)(I(π_{w₂}) − I(π_{w₁})) ≥ 0`, so `I` is nondecreasing. Substituting back into the first inequality gives `R(π_{w₁}) − R(π_{w₂}) ≥ w₁ (I(π_{w₂}) − I(π_{w₁})) ≥ 0`. ∎

**Scope, stated honestly.** The proposition applies to the `H`-step plan chosen at each fixed belief (`Π` = depth-`H` plans). Two gaps separate it from clean monotonicity of the count-usage staircase: (i) the monotone quantity is cumulative information gain, not the observation count, and the two can locally disagree (a cheaper low-IG observation pattern versus fewer high-IG ones); (ii) receding-horizon re-planning composes plan choices across steps, and monotonicity does not compose automatically. Both gaps are visible in the data — the count staircases on Tiger, Diagnosis, and Tileworld are only roughly monotone — and are the reason `solve_shadow_price` defaults to grid search with step brackets rather than bisection.

### Definition PI-3 (operational shadow price, set-valued)

Given the usage curve `U(w)` of the Planning+IG family, define `w*(B)` as the crossing bracket `(w_lo, w_hi]` where `U` passes `B` (implementation: `crossing_bracket` in `rho_aif/budget.py`). Feasibility: budgets are achievable with `w ≥ 0` iff `U(0) ≤ B` (instrumental sensing sets a usage floor) and `B ≤ U_max` (belief saturation and episode caps set a ceiling). When `B` falls in a usage gap, `w*` is genuinely interval-valued, and randomizing per episode between the endpoint policies with probability `q = (B − U(w_lo)) / (U(w_hi) − U(w_lo))` attains expected usage exactly `B` by linearity. The need for randomization at gap budgets mirrors the CMDP fact that optimal budget-constrained policies may be randomized (Altman 1999).

### Corollary PI-4 (Prop 2 thresholds are the knots of the usage staircase)

In the two-state setting of the companion paper's Proposition 2 at `H = 1`, the plan set is `{commit now, observe once then commit}`, and the observe plan is preferred iff `w > w*_thresh` (the closed form in Section 4). Therefore

```text
U(w) = 1{w > w*_thresh}    exactly at H = 1 (ties broken toward commit),
```

and for any budget `B ∈ (0, 1)` the crossing bracket leaves zero exactly at `w*_thresh`: the onset boundary of the budgeted problem recovers Proposition 2's closed form as the first knot of the usage staircase. At `H = 2` the second knot is the over-observation threshold `w*_over`. For multi-step receding-horizon agents the onset can shift slightly; the horizon-4 positive-threshold Testbeds put it in `(w_thresh, 1.03·w_thresh]` (3% above), consistent with the corollary.

**Numeric check**: `tests/test_budget.py::TestProp2OnsetExact` verifies the `H = 1` step directly — usage exactly 0 at `0.9·w*_thresh` and at least 1 at `1.2·w*_thresh` on the positive-threshold Testbed (`p = 0.6`, `c = 0.3`, `R = ±1`, `w*_thresh ≈ 3.44` in bits).

### Non-claims (verifier cautions honored)

- `w` is not the literal Lagrange multiplier of the count constraint; that multiplier is `λ` in Section 2b. PI-3 is an operational inverse, not a duality theorem.
- No universal closed form `w*(R, γ, |S|, H)` is claimed.
- The abstract idea of dualizing a resource constraint is prior art (Sims 2003; Matějka and McKay 2015; Altman 1999; Haarnoja et al. 2018). The claims above are specific to the Planning+IG / EFE family on this benchmark.

Citation check: no new citations are introduced in this section; all references appear in the verified table at the top of this file.

## 10. Implementation map

| Piece | Path |
|---|---|
| Theory notes (this file) | `Guidance_Documents/price_of_information.md` |
| Usage accounting, `crossing_bracket`, `solve_shadow_price` | `rho_aif/budget.py` |
| Online controller | `rho_aif/agents/dual_descent.py` |
| Experiments (`--replot` for scale/dual) | `experiments/run_price_of_information.py` |
| Tests | `tests/test_budget.py`, `tests/test_dual_descent.py` |
| Figures (PNG+PDF) | `figures/price_*.png`, `figures/price_*.pdf` |
| Paper draft | `paper/price_of_information.tex` |
| Phase log | `Guidance_Documents/research_plan.md` |
