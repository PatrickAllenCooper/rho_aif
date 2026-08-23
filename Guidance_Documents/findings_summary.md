# What this project found

**Scope**: the scientific findings, from the IWAI 2026 accepted paper through everything built on it.
**Sources**: `paper/full_paper_jair.tex`; every number below is traceable to a committed CSV in `results/`.
**Companion**: `verification_campaign_findings.md` covers the verification methodology. This document is the science.

---

## The question

An agent that cannot see the world directly has to decide **how much to look before it acts**. A doctor ordering tests, an inspector checking components, a rover assaying rocks: each pays for information and must decide when to stop paying.

Standard POMDPs cannot express that decision directly. Information has value only through its downstream effect on reward, so "look more" is never a goal, only a means. The ρ-POMDP framework fixes this by adding a belief-dependent utility ρ(b) — the agent gets credit for reducing its own uncertainty. But that just relocates the problem: **how much credit?** The weight on ρ is a free parameter, tuned by hand, per task.

This project is about where that weight comes from.

---

## The answer, in one page

**Part I (IWAI 2026).** The weight is not free. Active inference's Expected Free Energy objective — a variational quantity from a completely different tradition — turns out to be *exactly* a ρ-POMDP whose belief utility is expected information gain at weight **w = 1**. Not approximately, not up to a constant: the same Bellman recursion. Active inference has been solving budgeted-sensing ρ-POMDPs all along without saying so, and the weight it uses is derived from its own objective rather than searched.

**The catch.** w = 1 means "one reward unit per bit," so it depends on the reward scale. Multiply every reward by 10 and the same w = 1 buys a different amount of sensing. This looks like a fatal caveat.

**Part II (new work).** It isn't a caveat — it's the whole point. If w is a price, then scale-dependence is what prices *do*. So invert the question. Instead of asking "what weight?", state a **sensing budget** B — how much looking you can afford — and read off the weight that spends exactly that. That weight, w\*(B), is the budget's **operational shadow price**. This turns out to be well-behaved in a way the raw weight is not:

- it is **exactly scale-equivariant** — the curve computed at one reward scale transfers to every other by rescaling, no re-tuning (Prop PI-1);
- it is **set-valued** where it should be — at budgets no single weight can hit, the honest answer is a bracket, not a point (Def PI-3);
- it can be **learned online** by dual descent when the reward scale shifts mid-run (Prop PI-5).

And w = 1 falls out as one specific point on that price curve: the weight that buys whatever sensing the ambient reward scale happens to imply.

**The reframe in one line:** *"what should the exploration weight be?"* → *"how much sensing can we afford?"* — a question a practitioner can actually answer.

---

# Part I — The equivalence

## 1. EFE minimization *is* a ρ-POMDP (Proposition 1)

Write the recursive EFE objective for an observe-then-commit problem, negate it to turn minimization into maximization, and the result is literally the ρ-POMDP Bellman recursion:

```
V(observe_k, b) = −c_k  +  1 · I_k(b)  +  E_o[ max_a V(a, b'_o) ]
V(commit_i, b) = E_b[R_i]
```

The information-gain term enters with coefficient exactly 1. Commit actions carry no epistemic term — not by stipulation, but because the episode ends and no further observation is emitted.

**Why it matters.** Two literatures that don't cite each other — active inference (neuroscience-adjacent, variational) and ρ-POMDPs (planning, decision-theoretic) — are describing the same object. The bridge lets each import the other's tools: ρ-POMDP solvers become available to active inference, and active inference supplies ρ-POMDPs with a *derived* weight instead of a tuned one.

**Honest scope.** This is a notational bridge, not a discovery — a corollary of the Bellman-optimality result for sophisticated inference, specialized to the observe-then-commit partition. It is exact under log scoring rules. It holds for the recursive EFE formulation; whether the same coefficient survives under other EFE variants (FEEF, generalised free energy, Bethe-Lagrangian) is not established.

## 2. When is w = 1 actually a good weight? (Proposition 2)

Closed-form thresholds for the two-state case. Observing beats committing immediately when

> w > [ c − (p − ½)(1+α)R⁺ ] / I_max

where α = |R⁻|/R⁺ is the **reward asymmetry** (how much worse a wrong commit is than a right one is good) and I_max is the information a test yields.

**The intuition, which is the useful part:** when getting it wrong is much worse than getting it right, the threshold goes *negative* — meaning **any** positive weight, including w = 1, is enough to make the agent look before it leaps. Formally, the threshold → −∞ as α → ∞.

That's the regime that describes most real problems worth caring about: medical diagnosis, fault detection, security screening. A missed condition costs far more than another test. **w = 1 is well-calibrated precisely where the stakes are asymmetric.**

A second threshold bounds over-observation, giving an interval within which w = 1 is near-optimal.

**How well does this survive multi-step planning?** A Monte Carlo study over 100 random two-state environments: w = 1 passes a near-optimality test in 30% of them at H=1, 58% at H=2, **79% at H=3**. Deeper planning widens the basin. Stated as the complement, which is the number a practitioner needs: **w = 1 still fails in ~21% of that family even at H=3, and 70% at H=1.**

## 3. Beyond observe-then-commit (Proposition 3)

Real problems interleave looking and acting — navigate, then sense, then exploit. The equivalence extends to **factored-observation POMDPs**, where the hidden state is preserved by observation and navigation actions. RockSample's check-and-move, mobile sensor placement, and sequential testing with travel costs all live here.

The condition is precise: sensing must not change what is being sensed.

## 4. Where it breaks, and why that's informative (Example 3.5)

Suppose the test destroys what it measures — a drill that assays ore by consuming it. The naive reduction credits the drill with a full bit of information about a state the drill has already destroyed:

- naive value: −c + 1 bit + 1 = **2 − c**
- true value: **1 − c**

For c ∈ (1, 2) the two **disagree in sign**: the naive agent drills, the correct agent commits immediately. Worse, the drilling agent realizes expected reward −c, below the immediate-commit value of 0, for *every* c > 0.

**But the failure is in the reduction, not in EFE.** Active inference's epistemic term is defined over *post-transition* beliefs. Evaluate it correctly and it assigns the drill zero epistemic value — it knows the ore is gone regardless of what was observed — and recovers the true value. What breaks is the factored simplification that assumes sensing is non-destructive.

This is the boundary of the theory, stated as a theorem-adjacent Remark rather than buried.

---

# Part II — The price of information

## 5. The reframe

Since w converts bits into reward units, and the reward scale is a modeling convention, w is an **exchange rate**. Exchange rates are not universal constants; they are prices. So price it against something real.

Define the **usage curve** U(w): the expected sensing the agent buys at weight w. Solve U(w) = B for a stated budget B. The solution w\*(B) is the budget's shadow price.

## 6. Scale equivariance is exact, not approximate (Prop PI-1)

Rescale every reward and cost by α > 0. Then the whole policy family shifts by exactly that factor: w\*(B; α) = α · w\*(B; 1).

This holds **for the implemented receding-horizon agent**, not merely for idealized maximizers over a static policy class — which is the version that actually matters if you're going to run the thing.

Three consequences fall out:

1. **Curve collapse is a theorem.** Plot U against w/α and you get the *same curve* at every scale. Any measured deviation is Monte Carlo noise, by construction. Empirically we observe **bit-exact** collapse on every environment — matched points coincide exactly, crossing brackets agree to floating-point noise (≤ 10⁻¹⁵).
2. Brackets rescale as sets, including at gap budgets.
3. The **implicit EFE budget** drifts predictably with scale — which is precisely the sense in which w = 1 is not scale-invariant, now quantified rather than caveated.

*This is the strongest result in the paper.* It converts an empirical robustness check into a theorem with predictive content, and it means a usage curve computed once transfers to every reward scale for free.

## 7. The price is genuinely set-valued (Def PI-3)

Usage is a step function — policies change discretely. So for many budgets B, **no single weight attains usage exactly B.** Reporting a point estimate there would be false precision.

The honest object is a crossing bracket (w_lo, w_hi], and the budget is attained exactly by randomizing per episode between the two bracketing policies with probability q = (B − U(w_lo))/(U(w_hi) − U(w_lo)). This mirrors the classical constrained-MDP fact that optimal budget-constrained policies may require randomization.

A related subtlety we report rather than smooth over: **usage is not monotone in w.** The lower endpoint need not be U(0) — on Tileworld 6×6, reward-only planning at w=0 scans 15.64 times while w=1 scans 14.75.

## 8. Thresholds and the staircase agree (Cor PI-4)

Proposition 2's closed-form threshold is recovered as the **first knot of the usage staircase**. Two independently derived objects — an analytic threshold and an empirical step function — land in the same place. Empirically the onset bracket is (w_thresh, 1.03·w_thresh], a 3% upper relative error.

## 9. Learning the price online (Prop PI-5)

If the reward scale shifts mid-run you cannot recompute an offline curve. A dual-descent controller drives usage to the budget from interaction alone, with stationary convergence under Robbins–Monro conditions.

Tested under a ×10 mid-run reward rescale, 10 seeds:

| variant | episodes to re-adapt | 95% CI |
|---|---|---|
| decay-only | 150.9 | [142.9, 158.9] |
| reset-on-shift | **57.0** | [52.0, 62.0] |

**2.65× faster, disjoint CIs, 10/10 seeds recovering.** The controller also lands *inside* the offline crossing bracket at both scales — the online and offline answers agree.

---

# Part III — What the experiments show

Six observe-then-commit environments, four RockSample instances, and a Structural Inspection benchmark with 65,536 states. 5 canonical seeds, seed-level Welch tests as primary, Holm–Bonferroni corrected.

## 10. Untuned w = 1 against tuned baselines

| Environment | EFE (w=1) | reward-only Planning | success-tuned Planning+IG |
|---|---|---|---|
| Tiger | +5.19 / 99.4% | +5.19 / 99.4% *(exact tie)* | +4.21 / 99.9% |
| Diagnosis | **−1.37 / 97.2%** | −2.57 / 88.8% | −3.66 / 99.2% |
| Bandit | **+6.27 / 86.9%** | +5.75 / 71.0% | +5.11 / 98.9% |

On **Diagnosis and Bandit, untuned w = 1 Pareto-dominates same-horizon planning** — higher success *and* higher reward, no weight search (Diagnosis +8.3pp success, p = 4×10⁻⁸; Bandit +15.9pp, p = 2×10⁻⁵). The tuned baselines buy near-ceiling success by over-testing and give back reward to do it.

**Where w = 1 lands on the reward frontier** (regenerated sweep, five environments):

- **Inside** the reward-maximizing tied bracket on Tiger [0.01, 20], Diagnosis [0.5, 20], Bandit [1, 2].
- **Outside** it on Testbed — a genuine trade, buying +6.4pp success for −0.11 reward.
- **Pareto-dominated** on Tileworld: w = 20 wins on *both* axes (−18.95 vs −21.53 reward; 91.8% vs 72.0% success).

Reported this way rather than as an aggregate because it bounds the claim honestly: **w = 1 is reward-competitive where the reward surface is flat in w, and beaten where it has a sharp interior optimum.**

## 11. Against near-optimal references

**SARSOP** (the real APPL C++ solver, built from source, evaluated through the identical episode runner). On Tiger the two select *identical actions on every episode*. Formalized with a predeclared-margin TOST equivalence test — margin fixed before looking at the data, at the cost of one sensing action:

| | n=5 | n=20 robustness check |
|---|---|---|
| Tiger | p = 0.0010 | p = 4.5×10⁻¹⁰ |
| Diagnosis | p = 0.046 | p = 6.8×10⁻⁷ |
| Bandit | p = 0.013 | p = 6.0×10⁻¹¹ |

All equivalent, surviving Holm–Bonferroni as a family. Quadrupling the seeds **strengthens** the conclusion by three to five orders of magnitude — the direction an underpowered test would not move in.

**Constrained-POMDP reference** (Lagrangian-penalized SARSOP sweep, tracing the achievable reward/usage frontier). At EFE's own operating budget the estimated optimality gap is: **0.000 on Tiger, −0.073 on Diagnosis, −0.007 on Bandit.** The negatives are reference-frontier noise, not EFE beating the constrained optimum, and are reported as such.

## 12. Scaling and interleaved settings

**Tileworld.** At 8×8, EFE holds 69.4% ± 1.0pp success where reward-only Planning collapses to 1.4% ± 0.3pp. The mechanism, which we now state in the main text: at that scale Planning takes **zero** scans and is bit-identical to Myopic — a single binary scan of a 64-cell belief cannot repay its cost within an H=2 lookahead. So it is a joint horizon-and-scale effect, not a pure scale law.

**RockSample** (4 instances). EFE beats reward-only Planning by +2.19, +1.99, +9.54, and **+0.00** across increasing rock counts. Non-monotone, and exactly zero at the largest instance.

**Structural Inspection** (|S| = 65,536). EFE gains +18.0pp accuracy at N=8 and +12.6pp at N=16 over Planning — note the advantage *narrows* as the state space grows 256×.

**The unifying mechanism, and the limit of what we can claim:** EFE's advantage tracks **how much slack a problem leaves between greedy and information-optimal behavior** — not problem size. Tileworld: Planning scans too little, big margin. RS[7,8]: real ambiguity about which of 8 rocks to check, margin. RS[11,11]: rocks so widely spaced that "check nearest" is already near-optimal, no margin. We did not design instances to stress-test this prediction, so it is a reading of the data, not a validated scaling law.

---

# Part IV — The negative results

These are load-bearing and were published at full strength.

1. **A budget caps spending but does not redirect it.** With a reward-irrelevant distractor test available, ordinary information gain spends on it once the weight is high enough — distractor fraction rises to 0.233 ± 0.003 at w=10 and saturates near 0.33 for w ≥ 31.6. EFE at w=1 escapes only because this instance's onset weight (~10) exceeds 1, not because it is structurally immune.
2. **The reward-aware baseline isn't immune either.** IDS, which explicitly weights information *about the optimal action*, shows a 0.305 distractor fraction — because its implementation falls back to raw state entropy when the reward-conditional term vanishes, reintroducing exactly the blindness it was meant to avoid. This implicates the project's own baseline.
3. **A no-information-gain baseline sometimes ties.** Thompson sampling is statistically indistinguishable from EFE on Bandit on all three metrics (p = 0.58, 0.97, 0.30) and nominally ahead on reward; on Testbed it ties reward-only Planning exactly. It does not transfer — Diagnosis and Tiger go clearly to EFE — but it bounds what those two environments show about the epistemic term.
4. **The RS[11,11] mechanism is not identified.** Depth 2 and depth 3 agree, which is consistent with policy saturation *and* with a shared leaf heuristic dominating at both depths. Not separable at the depths run. Claim withdrawn.
5. **The CPOMDP reference does not extend to RockSample.** We tried. The usage-cap Lagrangian is structurally incompatible with depth-limited planning — it only rewards checking through what a 3-step lookahead can see, so the swept frontier degenerates to 0 or 1 checks and never reaches EFE's 9.84. Reported as a failed construction with a diagnosis.
6. **w = 1 is beaten on Tileworld**, by w = 20, on both axes.

---

# Part V — What it adds up to

**The durable idea is the reframe.** "What should the exploration weight be" is a question with no principled answer, which is why the field tunes it. "How much sensing can we afford" is a question a practitioner can answer from the application, and the weight follows from it. That substitution is what this project contributes.

**The theory is a bridge, not a breakthrough** — and the paper says so. Proposition 1 is a notational identification; its value is that it lets two literatures use each other's results, and that it supplies a *derived* default where there was a searched hyperparameter.

**The Price-of-Information half is where the new content is.** Exact scale equivariance (PI-1) is a small theorem with real predictive content: it turns a robustness check into a guarantee and makes a usage curve reusable across reward scales. Set-valuedness (PI-3) is the correct treatment of a discrete object that the literature usually reports as a point.

**The strongest practical claim** is narrow and well-supported: under a shared reward convention, in the asymmetric-penalty regime that describes most consequential sensing problems, **w = 1 is a defensible untuned starting point** — statistically equivalent to a near-optimal solver on the core environments, Pareto-dominant over same-horizon planning on two of them, and inside the reward-maximizing bracket on three of five. Where it isn't, the budgeted machinery is the stated recourse.

**And the boundaries are mapped**, which is unusual: we know it fails on destructive sensing, we know a budget doesn't redirect spending, we know it can be beaten where the reward surface has a sharp optimum, and we know a trivial baseline ties it on one environment.

> **One sentence.** Active inference's Expected Free Energy is exactly a ρ-POMDP with information-gain weight 1, that weight is best understood as the shadow price of a sensing budget rather than a universal constant, and pricing it that way is exactly scale-equivariant, honestly set-valued, and learnable online.
