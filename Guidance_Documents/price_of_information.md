# The Price of Information: w as a Shadow Price on a Sensing Budget

**Status**: Derivation notes and implementation targets for research extension #1  
**Date**: July 22, 2026  
**Relation to paper**: Addresses the accepted IWAI 2026 paper's limitation that the canonical weight `w=1` in Planning+IG / EFE is not reward-scale invariant. Paper draft deferred until scale-invariance and duality experiments hold.

## Citation check (verified before writing)

| Claim used here | Verified source |
|---|---|
| Rational inattention: agents face a finite Shannon capacity / information-processing constraint that can substitute for adjustment costs | Sims, C. A. (2003). Implications of rational inattention. *Journal of Monetary Economics*, 50(3), 665–690. DOI: 10.1016/S0304-3932(03)00029-1 |
| Discrete-choice rational inattention yields (generalized) multinomial logit; costly information acquisition before choice | Matějka, F., and McKay, A. (2015). Rational inattention to discrete choices: A new foundation for the multinomial logit model. *American Economic Review*, 105(1), 272–298. DOI: 10.1257/aer.20130047 |
| Soft Actor-Critic with constrained formulation that automatically tunes the entropy temperature by dual gradient descent | Haarnoja, T., Zhou, A., Hartikainen, K., Tucker, G., Ha, S., Tan, J., Kumar, V., Zhu, H., Gupta, A., Abbeel, P., and Levine, S. (2018). Soft Actor-Critic Algorithms and Applications. arXiv:1812.05905. (This is the applications / auto-temperature paper. The earlier ICML 2018 paper introduces SAC with a fixed temperature and does **not** contain the dual auto-tuning rule.) |

Check step: each row above was verified against the publisher / arXiv record on 2026-07-22. Do not cite the ICML SAC paper alone for automatic temperature tuning.

## 1. Budgeted problem

Let π be a (possibly history-dependent) policy in an observe-then-commit or inspection POMDP. Write:

- `R(π)` for the expected episodic return under the environment reward (including observation costs already present in the MDP),
- `U(π)` for expected **sensing usage** per episode.

Two natural usage measures, both supported by the code:

1. **Count usage**: `U_count = E[number of observe / test actions]`.
2. **Cost usage**: `U_cost = E[sum of sensing costs paid]` (absolute cost magnitude).

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

Dual descent with a fixed usage target inherits the same invariance: when rewards are rescaled mid-run, a fixed `w` breaks the budget while the controller re-converges.

## 6. Online dual control of w

Projected update that drives count/cost usage to budget `B` when `U` increases with `w`:

```text
w ← max(0, w + η (B − U_episode))
```

- If the episode overspent (`U > B`), decrease `w`.
- If it underspent (`U < B`), increase `w`.
- Project onto `w ≥ 0`.

This mirrors SAC's dual temperature update (Haarnoja et al., 2018, arXiv:1812.05905), with sensing usage in place of policy entropy and `B` in place of the target entropy. Implementation target: `rho_aif/agents/dual_descent.py::DualWeightAgent`.

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

## 9. Implementation map

| Piece | Path |
|---|---|
| Theory notes (this file) | `Guidance_Documents/price_of_information.md` |
| Usage accounting, `estimate_usage`, `solve_shadow_price` | `rho_aif/budget.py` |
| Online controller | `rho_aif/agents/dual_descent.py` |
| Experiments | `experiments/run_price_of_information.py` |
| Tests | `tests/test_budget.py`, `tests/test_dual_descent.py` |
| Phase log | `Guidance_Documents/research_plan.md` |

Paper draft: deferred until scale-invariance and Prop 2 duality results are in hand.
