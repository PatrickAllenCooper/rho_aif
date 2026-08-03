# Poster Content Reference: Minds and Machines Manuscript

Status: comprehensive raw material for poster design. This document is intentionally
over-inclusive; editorial selection, layout, and trimming happen later. Everything
below is sourced from `paper/full_paper.tex` (the accepted, integrated manuscript)
unless otherwise noted, cross-checked line-by-line against that source on 2026-08-03.
Numbers are copied verbatim from the manuscript tables/prose, not recomputed here;
if the manuscript is revised, re-diff this document against it before using it for
the poster.

Note on scope: `paper/full_paper.tex` is the long-form integrated document (theory +
budgeted reformulation + both experiment batteries). If the Minds and Machines
production version differs from this source file in any figure numbers, table
numbers, or wording, treat the journal proofs as authoritative and reconcile this
document before the poster is finalized.

---

## 1. Publication metadata

- **Title:** Expected Free Energy as Belief-Dependent Utility for ρ-POMDPs: From a
  Canonical Information-Unit Weight to an Operational Shadow Price
- **Authors:** Patrick Cooper and Alvaro Velasquez
- **Affiliation:** Department of Computer Science, University of Colorado Boulder,
  Boulder, CO, USA
- **Venue:** Minds and Machines (accepted)
- **Code and data:** `https://github.com/PatrickAllenCooper/rho_aif`
- **Keywords (from manuscript):** Active inference, Expected free energy, ρ-POMDPs,
  Epistemic value, Belief-dependent utility, Partial observability, Information gain
- **Competing interests:** none declared
- **No external funding acknowledgment appears in the manuscript.**

---

## 2. One-line summary (for a poster title strip or subhead)

Active inference's Expected Free Energy is exactly a ρ-POMDP with the information
gain weight fixed at w = 1; that weight is a good untuned default under a shared
reward convention, but its scale-sensitivity is not a flaw — it is the operational
shadow price of an explicit sensing budget, and we show how to read it off a usage
curve or track it online.

## 3. Elevator pitch (3-5 sentences, for an abstract panel)

Agents that act under partial observability must decide when to gather more
information and which observations are worth their cost. ρ-POMDPs let a designer
reward uncertainty reduction directly, but the weight on that reward is usually
hand-tuned per task. We show that active inference's Expected Free Energy (EFE)
supplies this weight for free: minimizing EFE is exactly equivalent to solving a
ρ-POMDP with an information-gain weight of w = 1, derived from a single variational
bound rather than searched. Across environments from the classic Tiger problem to a
65,000-state Structural Inspection benchmark, this untuned weight sits near the
reward-maximizing knee of the accuracy/reward trade-off. Because the weight's
"correct" value still depends on the reward scale the designer chose, we reframe it
as the shadow price of an explicit sensing budget: state how much observation the
agent may use, and the budget-matching weight is computable offline from a usage
curve, and trackable online if the reward scale itself shifts mid-deployment.

## 4. Plain-language framing of the core idea (for a poster "big idea" panel)

- Standard POMDPs only value information indirectly, through whatever reward it
  eventually produces. This makes it hard to explicitly ask "should I gather more
  information here?"
- ρ-POMDPs fix this by letting a belief-dependent bonus ρ(b) reward uncertainty
  reduction directly, but someone still has to choose ρ and its weight by hand.
- Active inference already has an answer, hiding in plain sight: Expected Free
  Energy already contains an information-gain term, and it enters at the same
  "exchange rate" as the reward term, i.e., a weight of exactly 1, once you write
  everything in bits and normalize the reward scale.
- That means an active inference agent is a ρ-POMDP agent that never had to run a
  grid search to find its exploration bonus. It gets the same emergent
  explore/exploit trade-off other work engineers by hand.
- The catch: "weight = 1" is only meaningful once you have fixed a reward
  convention (what a unit of reward means, in this environment). Change the reward
  scale, and w = 1 silently implements a completely different trade-off.
- Rather than treat that as a bug, the paper turns it into a feature: instead of
  asking "what weight should I use," ask "how much sensing can I afford" (a budget
  B, in observation counts or dollars), and read off the weight that spends exactly
  that budget from a measured usage curve. EFE's w = 1 becomes the special case
  that spends whatever budget the ambient reward scale happens to imply.

---

## 5. Contributions (verbatim structure from the Introduction, four numbered items)

1. **Theory.** A formal bridge between ρ-POMDPs and active inference. Proves the
   equivalence for observe-then-commit POMDPs (Proposition 1 / `prop:equivalence`),
   characterizes when the information-unit weight w = 1 is near-optimal
   (Proposition 2 / `prop:nearopt`), and extends the equivalence to factored
   observation POMDPs — interleaved settings where information gathering preserves
   the hidden state (Proposition 3 / `prop:factored`).
2. **Budgeted reformulation.** Recasts the information-unit weight as the
   operational shadow price w*(B) of a sensing budget B, proves exact scale
   equivariance of the resulting policy family for the implemented
   receding-horizon agent (Proposition PI-1), defines a set-valued price at usage
   gaps (Definition PI-3), and gives an online dual controller with a stated
   tracking (not merely stationary-convergence) guarantee under reward-scale shift
   (Proposition PI-5).
3. **Evidence.** Controlled comparisons against same-horizon planning, tuned
   information gain, and POMCP across six observe-then-commit environments and
   four instances of the standard RockSample benchmark. A Pareto analysis shows
   that on Diagnosis and Bandit, w = 1 Pareto-dominates same-horizon planning,
   while remaining competitive with tuned Planning+IG across environments. A
   second experiment battery shows usage-curve collapse across reward scales,
   closed-form onset thresholds recovered as the first knot of the usage
   staircase, multi-seed online tracking through a ×10 reward rescale, and a
   near-optimal SARSOP reference indistinguishable from EFE (w = 1) on the three
   core OTC environments.
4. **Practical guidance.** A characterization of when EFE-as-ρ helps and when it
   does not. The advantage appears when the agent must choose among multiple
   observation actions, and it grows with state space size (66.5% vs. 2.5% success
   on Tileworld 8×8) and with the number of observation actions (+7.34 reward over
   reward-only Planning on RockSample[7,8]). It does not help by construction when
   information gain is reward-blind and spends a sensing budget on task-irrelevant
   uncertainty (the distractor-robustness experiment), and naive information gain
   can misvalue an action outright when observing changes the hidden state (the
   destructive-sensing example).

---

## 6. Framework and formal results

### 6.1 ρ-POMDPs (background)

A ρ-POMDP augments a POMDP's reward with a belief-dependent utility ρ: Δ(S) → ℝ:

    π* = argmax_π E_π[ Σ_t γ^t ( R(s_t, a_t) + ρ(b_t) ) ]

When ρ = 0, this is a standard POMDP. When ρ encodes information gain, the agent
is explicitly rewarded for reducing uncertainty. The paper works in the
**observe-then-commit** restriction first: actions split into observation actions
(update belief at a cost, do not change hidden state) and terminal commit actions
(end the episode with state-dependent reward). This isolates the epistemic-value
question from state-transition dynamics.

### 6.2 Expected Free Energy (EFE)

    G(π) = − E_Q(o|π)[ln P(o|C)]  −  E_Q(o|π)[ D_KL( Q(s|o,π) ‖ Q(s|π) ) ]
             \_______pragmatic______/     \_____________epistemic_____________/

The paper uses the reward matrix directly rather than encoding rewards through a
preferred-outcome distribution P(o|C), avoiding a known hidden-tuning issue in
prior active-inference work. Recursive (sophisticated-inference-style) EFE for
observation actions:

    G(observe_k) = c_k − I_k(b) + E_o[ min_a G(a | b'_o) ]

with I_k(b) = H(b) − E_{o|obs_k}[H(b'_o)] the expected information gain. The agent
selects argmin_a G(a). There is no separate tunable exploration weight anywhere in
this expression — this absence of a free parameter is the paper's starting
observation.

### 6.3 Proposition 1 — EFE ≡ ρ-POMDP at w = 1 (`prop:equivalence`)

**Plain language:** Minimizing EFE produces exactly the same policy as solving a
ρ-POMDP whose belief-dependent utility is expected information gain with weight
w = 1, for observe-then-commit problems at any finite undiscounted horizon.

**Formal statement:** Define ρ_EFE(b,a) = I_a(b) for observation actions and 0 for
commit actions. Then for undiscounted finite horizon (γ = 1), minimizing recursive
EFE over horizon H produces the same policy as solving the ρ-POMDP Bellman
equation V*(b) = max_a { R(b,a) + ρ_EFE(b,a) + E_o[V*(b'_o)] } over the same
horizon.

**Proof idea:** Negate G to get a value function V = −G; the recursive EFE update
for observation actions becomes exactly the ρ-POMDP Bellman backup with
R(b, obs_k) = −c_k and ρ = I_k(b); for commit actions it is a terminal ρ-POMDP
action with ρ = 0. This is a corollary of the Bellman-optimality result for
sophisticated inference (Da Costa et al. 2023), specialized to action-dependent
ρ = I_a(b).

**Caveat baked into the framing (important for the poster's honesty):** this is a
notational bridge, not a claim of scale invariance. Rescaling every reward and
cost by k rescales the *effective* weight by 1/k, so w = 1 implements a different
trade-off at every reward scale. The claim is exact under log scoring rules
(Bernardo 1979); under a shared reward convention it is an *empirically robust
untuned default*, not automatic calibration.

### 6.4 Proposition 2 — near-optimality thresholds for w = 1 (`prop:nearopt`)

**Setting:** two-state observe-then-commit ρ-POMDP, uniform prior, one observation
action (accuracy p > 1/2, cost c > 0), two commit actions (correct reward R+,
incorrect penalty R− < 0, |R−| > R+). Define reward-asymmetry ratio
α = |R−|/R+ and informativeness ratio η = I_max/c.

**Lower threshold (H = 1):**

    w*_thresh = [c − (p − 1/2)(R+ − R−)] / I_max
              = [c − (p − 1/2)(1 + α) R+] / I_max

For any w > w*_thresh the agent observes before committing at H = 1. The threshold
is negative (so w = 1 already suffices) whenever
α > c / [(p − 1/2) R+] − 1, and w*_thresh → −∞ as α → ∞ for fixed p, c.

**Upper (over-observation) threshold at the post-first-observation belief:**

    w*_over = (c − VoI_2(b)) / I(b)   if VoI_2(b) < c,  else 0

**H = 2 near-optimality interval:** w ∈ (w*_thresh, w*_over). Below the lower
threshold the agent under-observes relative to instrumental reward; above the
upper threshold it over-observes even when the marginal information isn't worth
its cost.

**Validated numerically (Table `tab:alpha_eta`):**

| Environment | α | η (nats) | w*_lo | w*_hi | w=1 inside interval? | w*_ret (observed) |
|---|---|---|---|---|---|---|
| Testbed | 1.0 | 1.31 | −3.06 | 1.01 | Yes (near upper bound) | 0.5 |
| Tiger | 10.0 | 0.27 | −138.66 | 6.89 | Yes | 1.0 |
| Diagnosis | 5.0 | 0.19 | −88.20 | 7.91 | Yes | 0.5 |
| Tileworld | 5.0 | 0.19 | −88.20 | 7.91 | Yes | 0.5 |

(Bandit omitted: multi-armed, so the two-state proposition does not apply
directly.) High-asymmetry environments have w = 1 comfortably interior; Testbed
(symmetric rewards, α = 1) sits near the *upper* bound, explaining its observed
over-exploration relative to w*_ret = 0.5.

### 6.5 Proposition 3 — extension to factored observation POMDPs (`prop:factored`)

**Definition (factored observation POMDP):** state decomposes as s =
(s_vis, s_hid) with s_vis fully observable and s_hid hidden; actions partition
into (i) observation actions that inform about s_hid without changing it (may
change s_vis), (ii) navigation actions that change s_vis deterministically without
changing s_hid and produce no informative observation, and (iii) exploitation
actions that yield reward dependent on s_hid. Observe-then-commit is the special
case with no navigation actions and trivial s_vis. RockSample is a canonical
instance: position is s_vis, rock qualities are s_hid, check = observation,
move = navigation, sample/exit = exploitation.

**Result:** for any action that preserves s_hid, the transition-observation
coupling term Δ_T(b,a) vanishes, and ρ_EFE(b,a) = I_a(b) for observation actions,
0 for navigation actions — i.e., the same w = 1 equivalence carries over to
interleaved observe-act settings, wherever the hidden state survives observation
and navigation. This covers RockSample, mobile sensor placement, and sequential
testing with spatial access costs. Validated empirically across four RockSample
instances and Structural Inspection (Sections 6.7 and 6.8/8 below).

**Taxonomy table (factored vs. non-factored real-world POMDPs):**

| Factored (Δ_T = 0) | Non-factored (Δ_T ≠ 0) |
|---|---|
| Non-destructive testing | Destructive testing (drilling) |
| Medical imaging (CT, MRI) | Biopsy / tissue sampling |
| Structural inspection | Active interventions |
| Environmental monitoring | Predator-prey (target moves) |
| Security screening | Chemical testing (consumes sample) |
| Mineral exploration | Quantum measurement |
| Mobile sensor networks | Adversarial surveillance |

### 6.6 Worked counterexample — destructive sensing (`ex:destructive`)

Two-state testbed with a destructive test action a_D: perfectly reveals the
*pre-transition* state but always destroys it afterward (drilling a core sample
destroys the ore, rich or poor, no matter what was found). Naive information gain
(which assumes the state-preserving posterior) values a_D at 2 − c, recommending
drilling for any c < 2. The correct joint transition-observation posterior gives
a value of 1 − c — exactly one bit of illusory credit too high — and for
c ∈ (1, 2) the two evaluations flip sign entirely: naive says drill, correct says
commit immediately. Worse: an agent that drills and acts on its now-obsolete
observation realizes expected reward −c in the true environment, strictly below
the immediate-commit value of 0 for *every* c > 0, not merely within the
sign-flip range. Verified numerically (`tests/test_destructive_boundary.py`). No
corrected destructive-sensing operator is proposed; this is scoped explicitly as
future work.

**Poster framing:** this is the clean, falsifiable boundary case demonstrating
where the whole EFE-as-ρ equivalence breaks, and by how much — good for a
"limitations" panel with a concrete number attached.

---

## 7. The budgeted ρ-POMDP / price-of-information extension

### 7.1 Motivation

If every reward and cost is rescaled by α > 0, expected information gain (bits) is
untouched, so a fixed w = 1 implements a different pragmatic/epistemic trade-off
at every scale. Rather than tuning w per task, treat the missing degree of freedom
as a **sensing budget**.

### 7.2 The budgeted problem and usage curve

    max_π R(π)   subject to   U(π) ≤ B

R(π): expected episodic return. U(π): expected sensing usage (observation/test
count, or cumulative sensing cost). Planning+IG's additive-bonus form
R(π) + w·E_π[I] is an "information-floor" dual of the literal Lagrangian
R(π) − λU(π). Write U(w) for the usage induced by the Planning+IG-optimal policy
at weight w (the **usage curve**). Solving U(w) = B for w gives the **operational
shadow price** w*(B): the weight that spends about B units of sensing.

### 7.3 Definition PI-3 — set-valued operational shadow price

Given the usage curve U(w), w*(B) is the crossing bracket (w_lo, w_hi] at which U
passes B. A budget is achievable with w ≥ 0 iff U(0) ≤ B ≤ U_max (U(0) > 0
reflects "instrumental" sensing that pays for itself on reward alone; U_max
reflects belief saturation / episode step cap). When B falls inside a usage gap,
w* is genuinely interval-valued: no single weight attains usage exactly B, but
randomizing per episode between the bracket endpoints' policies attains expected
usage exactly B by linearity (mirrors the classical constrained-MDP fact that
optimal budget-constrained policies may need randomization).

### 7.4 Proposition PI-1 — exact scale equivariance

**Plain language:** if you scale every reward, penalty, and cost in the
environment by α, the agent that used weight w before will behave *identically*
to the agent using weight αw in the new, rescaled environment — exactly, not
approximately.

**Formal statement:** for every α > 0 and w ≥ 0, the receding-horizon Planning+IG
agent facing the α-scaled environment with weight αw selects the same action as
the agent facing the unscaled environment with weight w, at every belief.
Consequently U_α(αw) = U(w) exactly.

**Why it's true:** any candidate plan's α-scaled value is exactly α times its
unscaled value (pragmatic sum scales by α, IG sum scales by αw = α·w, information
gain itself is untouched because it depends only on the observation model).
Multiplying every candidate's value by the same positive constant preserves the
argmax set; a fixed tie-break rule then selects the same element.

**Three corollaries (good poster bullets):**
1. Curve collapse is a theorem: U plotted against w/α is the same curve at every
   scale; any measured deviation is Monte Carlo noise, not a violation.
2. Crossing brackets rescale as sets: w*(B; α) = α · w*(B; 1).
3. A fixed w = 1 at scale α behaves like w = 1/α at scale 1, so the **implicit EFE
   budget** drifts with scale: B_EFE(α) := U(1/α) — the precise sense in which
   the "canonical" weight is not scale invariant.

### 7.5 Proposition PI-2 — monotone comparative statics

For exact maximizers over a fixed plan set Π, π_w ∈ argmax_π R(π) + w·I(π): for
w2 > w1 ≥ 0, I(π_w2) ≥ I(π_w1) and R(π_w2) ≤ R(π_w1). (Standard supermodularity
argument: add the two optimality inequalities.) Two gaps separate this from clean
monotonicity of the *count*-usage staircase actually plotted: (1) the monotone
quantity is cumulative expected information gain, not observation count, and the
two can locally disagree; (2) receding-horizon replanning composes per-step
argmax choices, and monotonicity of the per-step choice doesn't automatically
compose into trajectory-level monotonicity. Both gaps are visible empirically
(Tiger, Diagnosis, Tileworld staircases are only roughly monotone) — this is why
the shadow-price solver uses grid search with bracket reporting rather than
bisection on an assumed-monotone function.

### 7.6 Corollary PI-4 — Proposition 2's thresholds are usage-staircase knots

In the two-state H = 1 setting, U(w) = 1[w > w_thresh] exactly, so for any budget
B ∈ (0,1) the crossing bracket leaves zero exactly at w_thresh: the onset boundary
of the budgeted problem recovers Proposition 2's closed form as the first knot of
the usage staircase. Verified numerically (`TestProp2OnsetExact` in
`tests/test_budget.py`): usage is exactly 0 at 0.9·w_thresh and at least 1 at
1.2·w_thresh on a positive-threshold Testbed (p = 0.6, c = 0.3, R = ±1,
w_thresh ≈ 3.44 bits).

### 7.7 Online dual control of the shadow price (Equation, Proposition PI-5)

Adapted from Soft Actor-Critic's automatic entropy-temperature update, substituting
sensing usage for policy entropy: after each episode with observed usage U_t,

    w_{t+1} = Proj_[0, w_max]( w_t + a_t (B − U_t) ),    a_t = η0 / (1 + δt)

This is exactly the Robbins-Monro (1951) stochastic-approximation recursion for a
root of U(w) = B, projected onto a bounded interval; overspending decreases w,
underspending increases it.

**Proposition PI-5 (two claims):**
1. **Stationary convergence.** Under step sizes with Σa_t = ∞ and Σa_t² < ∞
   (satisfied with δ > 0, not by the constant-step δ = 0 default), and given the
   Robbins-Monro sign condition (U(w) < B below w*, > B above — note U(w*) = B is
   *not* required, so this covers gap budgets too), w_t → w* in probability
   (Robbins-Monro 1951), and almost surely under Blum's (1954) refinement.
2. **Nonstationary tracking.** Under a constant step (δ = 0), the recursion is
   stochastic-gradient *tracking*, not root-finding: w_t is driven into and held
   within an O(a) neighborhood of w*, never fully settling in a stationary run —
   which is exactly what lets a constant-step controller re-adapt after the
   budget or environment shifts.

The **reset-on-shift** mechanism (used in the multi-seed experiment below) is an
empirical nonstationary re-adaptation heuristic — resetting the decay clock after
a detected shift — distinct from, and not covered by, the stationary-convergence
guarantee of claim 1.

### 7.8 Positioning against prior art (for a "related work" panel)

No claim of novelty for dualizing a resource constraint in the abstract — that is
classical. The contribution is the concrete operationalization for budgeted
ρ-POMDP sensing specifically:

| Prior art | What it takes as primitive | What's missing relative to this paper |
|---|---|---|
| Rational inattention (Sims 2003; Matějka & McKay 2015) | Shannon-capacity constraint | No operational sensing budget for ρ-POMDP planning |
| Constrained MDPs/POMDPs (Altman 1999; Kim & Lim 2011) | Exogenous cost constraint, solved offline | No scale equivariance result; no online tracking |
| SAC automatic temperature tuning (Haarnoja et al. 2018b) | Policy-entropy target, dual gradient ascent | Not applied to epistemic/sensing usage; direct template for Eq. (dual update) here |
| Sequential Bayesian experimental design (Lindley 1956; Foster et al. 2021) | Expected information gain about a latent, chosen every step | Objective is information alone, not reward under a sensing constraint; the two coincide only at maximally tight budgets |

Distinct contributions: exact scale equivariance of the resulting policy family
(Prop PI-1), a set-valued shadow price at usage gaps rather than a single
multiplier (Def PI-3), and an online controller with a stated *tracking*, not
only stationary-convergence, guarantee under distribution shift (Prop PI-5).

---

## 8. Agents compared (Table `tab:agents`)

| Agent | ρ function | Horizon | Controls for |
|---|---|---|---|
| Myopic | ρ = 0 | H = 1 | Weakest baseline |
| Planning | ρ = 0 | H > 1 | Planning depth |
| Info Gain | w·I(b) | H = 1 | Epistemic bonus (myopic) |
| Planning+IG | w·I(b) | H > 1 | IG + planning depth |
| EFE | I_a(b) via EFE | H > 1 | Joint objective (= Planning+IG at w=1) |
| Epistemic-only | I_a(b) only | H > 1 | Ablation: no pragmatic term |

Plus baselines: Greedy (samples/diagnoses without checking/testing — no-information
lower bound), POMCP (Monte Carlo tree search, semi-informed rollouts), MCTS-EFE
(MCTS with EFE as leaf heuristic), SARSOP (near-optimal offline point-based
solver), IDS (information-directed sampling, observe-then-commit adaptation).

Key ablation result: the Epistemic-only agent (no reward awareness) commits at
chance on all environments — 50.1% on Tiger, 25.1% on Bandit, 0.0% on Tileworld
6×6 — confirming the pragmatic term is essential; pure information-seeking without
reward alignment produces catastrophic behavior.

EFE computation is validated against `pymdp` (Heins et al. 2022).

---

## 9. Benchmark environments (specs)

| Environment | |S| | Obs. actions | Commit actions | Accuracy | Obs. cost | Correct | Incorrect |
|---|---|---|---|---|---|---|---|
| Tiger | 2 | 1 (listen) | 2 | 0.85 | −1.0 | +10 | −100 |
| Testbed | 2 | 1 | 2 | 0.75 | −0.1 | +1 | −1 |
| Diagnosis (N=4) | 4 | 2 tests | 4 | 0.80 | −1.0 | +10 | −50 |
| Bandit (K=4) | 4 | 4 inspect | 4 pull | 0.80 | −0.5 | +10 | +1 (others) |
| Navigation | 9 | 4 (move) | 0 (implicit) | varies (distance) | −0.5 | +20 | — |
| Tileworld (6×6) | 36 | 6 (scan) | 36 (collect) | 0.80 | −1.0 | +10 | −50 |
| RockSample[5,3] / [7,4] / [7,8] / [11,11] | up to 2,048 | check (distance-decaying accuracy) | sample/exit | varies | −0.5 (all actions) | +10 sample / +10 exit | −10 bad sample |
| Structural Inspection N=8 | 256 | visual (0.70, −0.5) / detailed (0.90, −2.0) | diagnose per component | — | — | +2 nominal / +5 fault | −50 missed fault / −5 false alarm |
| Structural Inspection N=16 | 65,536 | same as N=8 | same | — | — | same | same |
| DistractorDiagnosisEnv | 8-joint (4 condition × 2 nuisance) | condition tests + 1 zero-info distractor test | 4 diagnose | — | — | — | — |

All implemented as Gymnasium environments with standard reset/step API. Main
protocol: 1,000 episodes/seed × 5 seeds (42, 123, 456, 789, 1024) = 5,000 episodes
per condition, t-tests with Holm-Bonferroni correction, bootstrap CIs available.

**Poster-worthy scale claim:** Structural Inspection N=16 has |S| = 65,536 states
— explicitly called out in the abstract as the scale demonstration.

---

## 10. Headline experimental results (main battery)

### 10.1 Core environments (Table `tab:main`)

| Env (H, w*) | Agent | Obs. | Success | Reward |
|---|---|---|---|---|
| Tiger (H=6, w*=20) | Myopic | 1.00 | 84.6% | −7.98 ± 0.56 |
| | Planning | 4.28 | 99.5% | +5.15 ± 0.12 |
| | Planning+IG | 4.20 | 99.4% | +5.19 ± 0.12 |
| | **EFE** | **4.22** | **99.5%** | **+5.23 ± 0.11** |
| Diagnosis (H=3, w*=100) | Myopic | 2.00 | 64.2% | −13.48 ± 0.41 |
| | Planning | 5.91 | 89.2% | −2.37 ± 0.26 |
| | Planning+IG | 13.21 | 99.3% | −3.63 ± 0.10 |
| | **EFE** | **9.70** | **97.0%** | **−1.52 ± 0.16** |
| Bandit (H=2, w*=100) | Myopic | 2.04 | 61.7% | +5.53 ± 0.06 |
| | Planning | 3.24 | 69.6% | +5.65 ± 0.06 |
| | Planning+IG | 12.41 | 99.8% | +3.78 ± 0.04 |
| | **EFE** | **5.16** | **87.3%** | **+6.27 ± 0.05** |

**Headline framing:** on Diagnosis and Bandit, EFE **Pareto-dominates** same-horizon
Planning — higher success *and* comparable-or-better reward, with zero weight
search. Diagnosis: +7.8pp success (97.0% vs 89.2%) with better reward (−1.52 vs
−2.37). Bandit: +17.7pp success (87.3% vs 69.6%) *and* higher reward (+6.27 vs
+5.65). Tuned Planning+IG (w*=100, success-maximizing) reaches near-ceiling success
(99.3% / 99.8%) but at substantial reward cost from over-exploration (13.21 tests
/ 12.41 inspections). Bootstrap 95% CIs (10,000 resamples) confirm non-overlapping
reward intervals vs. Planning on Bandit.

**Effect sizes:** Cohen's d on reward between EFE and same-horizon Planning is
negligible on Tiger/Diagnosis/Bandit (|d| < 0.2). On success rate, d ≈ 0.33
(Diagnosis) and d ≈ 0.47 (Bandit) — small-to-medium. Medium-to-large reward d
(> 0.7) appears against over-exploring baselines and where Planning fails to
explore enough (Tileworld d > 2.0).

### 10.2 Pareto frontier (Figure `fig:pareto`, Section `sec:pareto`)

Sweeping w from 0.01 to 200 on all environments: w = 1 sits **near the
reward-maximizing weight** w*_ret on every environment, while the
success-maximizing weight w*_succ lies at 20-200. Framing: w = 1 is near-optimal
for *reward*, not for *success rate* — safety-critical applications wanting
near-certain accuracy would want higher weights at a reward cost.

### 10.3 Tileworld: spatial epistemic foraging

**6×6 grid (Table `tab:tileworld`, H=2, tuned w*=100):**

| Agent | Scans | Success | Reward |
|---|---|---|---|
| Myopic | 0.00 | 2.7% | −48.39 |
| Planning (H=2) | 15.68 | 73.7% | −21.47 |
| Planning+IG (w=100) | 33.38 | 98.4% | −24.31 |
| **EFE (H=2)** | **14.81** | **72.8%** | **−21.13** |

EFE achieves the *highest reward* while scanning less than half of Planning+IG's
count.

**Spatial scaling (4×4 to 8×8, Figure `fig:tw_scaling`):** at 8×8 (|S|=64),
reward-only Planning collapses to **2.5% success** while EFE maintains **66.5%**.
Planning+IG (w=100) reaches 98.0% success but at high reward cost. **This is the
single best "scale matters" headline number for the poster.**

**Observation-structure robustness:** replacing the structured bit-level scan
partition with random or overlapping partitions preserves EFE's relative ranking
over Planning under all three modes (bitwise −20.52/74.2%, random −29.15/56.1%,
overlapping −46.73/9.8%), confirming the result isn't an artifact of the
structured observation model.

### 10.4 RockSample (interleaved observe-act; validates Proposition 3)

| Instance | Agent | Good | Bad | Reward |
|---|---|---|---|---|
| RS[5,3] | Greedy | 1.49 | 1.51 | +3.71 ± 0.25 |
| | Planning (w=0) | 0.99 | 0.04 | +14.28 ± 0.11 |
| | Plan+IG (w=5) | 1.44 | 0.03 | **+16.47 ± 0.12** |
| | **EFE (w=1)** | 1.44 | 0.03 | **+16.47 ± 0.12** |
| RS[7,4] | Greedy | 1.98 | 2.02 | −1.38 ± 0.29 |
| | Planning (w=0) | 0.95 | 0.05 | +13.97 ± 0.11 |
| | Plan+IG (w=5) | 1.60 | 0.01 | +14.69 ± 0.12 |
| | **EFE (w=1)** | 1.44 | 0.01 | **+15.96 ± 0.12** |
| RS[7,8] | Greedy | 4.02 | 3.98 | −5.60 ± 1.23 |
| | Planning (w=0) | 0.48 | 0.03 | +12.31 ± 0.24 |
| | Plan+IG (w=5) | 2.67 | 0.03 | **+22.14 ± 0.51** |
| | EFE (w=1) | 2.20 | 0.09 | +19.65 ± 0.48 |
| RS[11,11] | Greedy | 5.48 | 5.52 | −18.90 ± 1.45 |
| | Planning (w=0) | 0.48 | 0.03 | **+13.23 ± 0.24** |
| | Plan+IG (w=5) | 0.50 | 0.03 | +13.18 ± 0.25 |
| | **EFE (w=1)** | 0.48 | 0.03 | **+13.23 ± 0.24** |

Headline: on RS[7,4], **EFE leads outright (+15.96)**. On RS[5,3], EFE ties the
tuned agent. On RS[7,8], tuned Plan+IG wins (+22.14 vs +19.65) — an honest
counterexample where a higher tuned weight keeps paying off. On RS[11,11], all
informed agents converge (policy saturation at 11 widely spaced rocks, verified
not to be a depth-ceiling artifact). "+7.34 reward over reward-only Planning on
RockSample[7,8]" is cited in the intro as a headline number (Plan+IG minus
Planning: 22.14 − 12.31 ≈ 9.83 at w=5; the abstract's +7.34 figure should be
double-checked against the exact source table/appendix before using verbatim on
the poster — see Section 15 verification note below).

### 10.5 Structural Inspection (largest state space: |S| = 65,536)

| Instance | Agent | Accuracy | Missed | Tests | Reward |
|---|---|---|---|---|---|
| N=8 (|S|=256) | Greedy | 70.7% | 2.34 | 0.0 | −114.33 ± 1.33 |
| | Planning (w=0) | 73.0% | 0.07 | 12.7 | **−17.85 ± 0.34** |
| | Planning+IG (w=5) | **94.9%** | 0.10 | 18.7 | −22.82 ± 0.35 |
| | EFE (w=1) | 87.9% | 0.08 | 18.0 | −20.60 ± 0.34 |
| N=16 (|S|=65,536) | Greedy | 70.0% | 4.81 | 0.0 | −237.46 ± 2.93 |
| | Planning (w=0) | 78.2% | 0.26 | 22.3 | −46.09 ± 0.94 |
| | Planning+IG (w=5) | **91.4%** | 0.24 | 28.1 | **−43.51 ± 0.85** |
| | EFE (w=1) | 86.1% | 0.27 | 32.8 | −45.71 ± 0.94 |

EFE is explicitly framed as "a competitive untuned trade-off rather than uniquely
best." On N=8: +14.9pp accuracy over Planning (87.9% vs 73.0%) at moderate reward
cost. On N=16 (the largest benchmark in the paper): +7.9pp accuracy over Planning
(86.1% vs 78.2%) with statistically indistinguishable reward (p > 0.05).

### 10.6 Discount-factor sensitivity (Appendix, condensed)

EFE's advantage requires γ ≥ 0.99 on multi-observation environments. On Diagnosis,
EFE's success advantage over Planning is +7.8pp at γ=1.0, drops to +1.0pp at
γ=0.95, and *reverses* to −1.6pp at γ=0.90. On Tiger (single observation action),
EFE is insensitive to γ across [0.90, 1.0]. Mechanism: discounting truncates the
effective planning horizon below the number of observations needed for confident
disambiguation.

### 10.7 Model misspecification (Appendix, condensed)

Agent's believed observation accuracy vs. true accuracy, mismatch up to ±0.15.
Tiger: success stays ≥ 96.7% across all mismatch levels — remarkably robust.
Overestimating sensor accuracy (positive mismatch) is more harmful than
underestimating (agent commits prematurely on insufficient evidence). Diagnosis
shows graceful but measurable degradation (97.4% at zero mismatch down to
~88.8-89.1% at ±0.15). EFE's intrinsic epistemic drive provides "a partial buffer"
against overconfident models.

### 10.8 POMCP baseline comparison (Appendix, condensed)

| Env | Agent | Obs. | Success | Reward |
|---|---|---|---|---|
| Tiger | Planning | 4.30 | 99.8% | +5.48 |
| | POMCP (1000) | 1.67 | 89.3% | −3.42 |
| | **EFE** | **4.29** | **99.2%** | **+4.83** |
| Diagnosis | Planning | 6.02 | 86.0% | −4.42 |
| | POMCP (1000) | 3.91 | 73.1% | −10.04 |
| | **EFE** | **9.76** | **96.6%** | **−1.80** |
| Bandit | Planning | 3.35 | 71.8% | +5.79 |
| | POMCP (1000) | 14.41 | 96.8% | +2.51 |
| | **EFE** | **5.19** | **89.0%** | **+6.42** |
| Tileworld 6×6 | Planning | — | 74.5% | −20.72 |
| | POMCP (1000) | — | 6.1% | −48.36 |
| | **EFE** | — | **73.0%** | **−21.22** |

POMCP underperforms both EFE and Planning on every environment except Bandit
success rate (where it over-explores at a steep reward cost). On Tileworld, POMCP
collapses to 6.1% success — branching factor overwhelms 1,000 simulations.
Increasing POMCP's budget to 5,000 simulations does not close the gap on
Diagnosis (71.5% vs. EFE's 96.6%) and costs ~5x the wall-clock time.

**MCTS-EFE (EFE as MCTS leaf heuristic, breaking the O((K·|O|)^H) exact-search
ceiling):** on Tiger H=10, 500 simulations: 97.2% success (7.2s/200 episodes) vs.
POMCP's 89.7% at matched budget (1.7s). On Diagnosis H=5: 98.0% vs. POMCP's 71.3%
(200 simulations). On Tileworld 6×6: MCTS-EFE(50) reaches 96.0% / −19.04 reward,
outperforming both Exact-EFE (75.0% / −20.11) and POMCP at matched or higher
budgets (2.0% / 15.0% success) — an 81-94pp gap.

### 10.9 Zero-shot weight transfer (Table `tab:transfer`, Section 8 Discussion)

| Weight | Tiger | Diagnosis | Bandit | Testbed |
|---|---|---|---|---|
| w=0.5 (w*_ret Diag./Testbed) | +5.62 | −2.19 | +6.05 | **+0.47** |
| **w=1 (EFE)** | +5.29 | **−1.41** | **+6.18** | +0.38 |
| w=20 (w*_succ Tiger) | **+5.68** | −2.21 | +5.14 | −0.22 |
| w=50 (w*_succ Testbed) | +4.32 | −3.74 | +4.28 | −0.44 |
| w=100 (w*_succ Diag./Bandit) | +4.24 | −3.44 | +3.91 | −0.37 |

Headline: **success-tuned weights transfer catastrophically** (a weight tuned for
99%+ accuracy on one task can tank reward on another), while moderate,
reward-tuned weights (including w=1) transfer robustly within a shared reward
convention. Good "why not just grid search" poster panel.

### 10.10 Near-optimality across planning horizons (Monte Carlo study, Appendix)

100 random two-state environments (α ∈ [1,50], p ∈ [0.55,0.95], cost ∈ [0.1,5]),
w=1 classified near-optimal if within max(5%, 0.5) of best achievable reward at
each horizon:

| Horizon | Near-optimality rate (all envs) | Rate for α ≥ 10 |
|---|---|---|
| H=1 | 11% | 14% |
| H=2 | 21% | 19% |
| H=3 | 38% | 37% |

**Headline framing:** deeper planning *widens* the basin where the untuned weight
is reward-competitive, rather than narrowing it. Per-environment agreement
between H=1 and H≥2 classification is only 50/100; myopic (H=1) checks
under-claim on 42 environments (safe direction — a missed opportunity) and
over-claim on 8 (risky direction — a practitioner validating with a cheap H=1
check could deploy at a depth where it actually underperforms).

---

## 11. Second experiment battery: shadow prices and sensing budgets

### 11.1 Curve collapse across reward scales (Figure `fig:collapse`, Table `tab:collapse-breadth`)

| Environment | Within 2·SE across α ∈ {0.1,1,10} | Max spread | Bracket at B |
|---|---|---|---|
| Diagnosis (B=8) | 100% | 0.49 obs. | (0.141, 0.323] at every α |
| Bandit (B=8) | 100% | 0.50 obs. | (3.84, 8.76] at every α |
| Tiger (B=4) | 100% (trivial) | 0.31 obs. | unbracketed — B below observed U at every α |
| Tileworld-6×6 (B=15) | 90% | 0.91 obs. | brackets coincide except one shared knot |

**Headline:** empirical confirmation that Proposition PI-1's exact scale
equivariance holds in practice — every matched w/α point across a 100x scale
range (α = 0.1 to 10) lies within 2 standard errors on Diagnosis and Bandit.

### 11.2 Proposition 2 onset recovery (Figure `fig:prop2`)

Constructed positive-threshold "InfoSeeking" environments (p ∈ {0.60, 0.58},
c=0.3, R=±1) with closed-form thresholds w_thresh ≈ 3.44 and 7.55. Empirical
usage onset falls in (w_thresh, 1.03·w_thresh] on both — i.e., **the theoretical
threshold predicts the empirical onset to within 3% relative error.**

### 11.3 Multi-seed online dual control under a ×10 reward rescale (Figure `fig:dualmultiseed`)

Diagnosis, target B=8, 10 controller seeds, ×10 reward-and-cost rescale at episode
200 of a 400-episode run:

| Controller | Mean re-adaptation time (episodes) | 95% CI | Recovered within 200 episodes |
|---|---|---|---|
| Decay-only | 126.8 | [90.5, 163.0] | 8/10 seeds |
| Reset-on-shift | 53.3 | [48.7, 57.9] | 10/10 seeds |

Disjoint CIs. Post-rescale steady-state |U−B|: 0.11 [0.07,0.15] (reset) vs. 0.50
[0.14,0.86] (decay-only). **Headline: reset-on-shift re-adapts ~2.4x faster and
never fails to recover, across all 10 seeds tested — decay-only failed to recover
in the given window on 2/10 seeds.**

### 11.4 Cost-denominated budgets (Figure `fig:costbudget`)

Diagnosis variant with heterogeneous per-test costs ([0.5, 2.5]). Mean cost per
test is *not* constant across w (1.21 to 1.39, a 13.5% relative spread). A count
budget B=8.64 brackets w* in (10, 31.6], while a comparable cost budget
B_cost=11.15 brackets w* in (3.16, 10] — **the two denominations give genuinely
different, individually interpretable prices**, because a count budget can't see
that the agent shifted its test mix toward the cheaper, less informative test as
w rises.

### 11.5 Interleaved settings usage curves (Figure `fig:interleaved`)

RockSample[5,3] (usage [3.81, 9.10]), RockSample[7,4] ([2.00, 14.73]),
Inspection-N=16 ([22.42, 46.04]). Unlike observe-then-commit domains, U(w) is
nondecreasing at *every* sampled grid point on all three — cleaner monotonicity
than Tiger/Diagnosis/Tileworld. Large instrumental floors (U(0) = 3.81 / 2.00 /
22.42) show that "reward alone already motivates a lot of sensing" matters in
interleaved settings too.

### 11.6 Shadow-price staircases (Figure `fig:stairs`)

w*(B) over identifiable budgets for Tiger, Diagnosis, Bandit, Tileworld-6×6,
Inspection-N=8. Bandit and Inspection are roughly monotone; Tiger, Diagnosis, and
Tileworld show local non-monotonicity from discrete policy switches, hence
brackets + SEs rather than singleton prices are reported.

### 11.7 SARSOP near-optimal reference (Table `tab:sarsop`)

| Environment | SARSOP reward | EFE reward | SARSOP usage | EFE usage |
|---|---|---|---|---|
| Tiger | 5.061 ± 0.158 | 5.061 ± 0.158 | 4.323 | 4.323 |
| Diagnosis | −1.452 ± 0.336 | −1.217 ± 0.184 | 9.68 | 9.73 |
| Bandit | 6.280 ± 0.134 | 6.261 ± 0.112 | 5.16 | 5.09 |

**Headline: on Tiger, SARSOP and EFE select IDENTICAL actions on every episode.**
On Diagnosis and Bandit, statistically indistinguishable (within 0.6 SE), usage
differs by < 0.1 observations. Built the original APPL C++ SARSOP toolkit from
source, exported benchmarks to Cassandra `.pomdp` format, solved to precision
1e-3, evaluated through the identical episode runner as every other agent. This
retires a specific reviewer debt from the workshop camera-ready ("promised a
near-optimal offline baseline").

### 11.8 Distractor robustness (Figure `fig:distractor`) — an honest limitation, good poster material

`DistractorDiagnosisEnv`: 8-joint state (4 conditions × binary nuisance bit),
reward depends only on the condition; one additional test is *provably and
unit-tested* exactly zero-information about the condition marginal.

Distractor fraction of total sensing usage as a function of w: **exactly 0 for
w ≤ 3.16**, rises to 0.242 ± 0.005 at w=10, saturates at 0.331 ± 0.005 for
w ≥ 31.6. EFE's canonical w=1 happens to stay at zero on this instance only
because the onset weight (~10) exceeds 1 here — not because EFE is structurally
immune. An IDS (information-directed sampling) baseline, despite being explicitly
reward-aware, is *also* not immune (0.311 ± 0.005 distractor fraction) due to a
specific implementation detail (its info-astar term correctly zeroes out for the
distractor, but a fallback to raw state entropy lets the distractor's genuine
nuisance-bit informativeness back in). **Framed explicitly as an honest
limitation, not elided.**

### 11.9 The w* atlas (Table `tab:w-atlas`, appendix)

Aggregates usage-curve range, implicit EFE budget B_EFE = U(w=1), and two
canonical-budget crossing brackets per benchmark instance:

| Instance | Usage range | B_EFE | Bracket 1 | Bracket 2 |
|---|---|---|---|---|
| Bandit | [3.06, 12.20] | 5.03 ± 0.17 | 4.4: (0.0611, 0.139] | 10.8: (19.3, 43.9] |
| Diagnosis | [5.72, 13.57] | 9.68 ± 0.15 | 6.9: (0.139, 0.316] | 12.4: (19.3, 43.9] |
| Inspection-N16 | [22.42, 46.04] | 33.46 ± 0.19 | 26.0: (0.316, 1.33] | 42.5: (5.62, 23.7] |
| Inspection-N8 | [12.65, 30.89] | 18.24 ± 0.19 | 15.4: (0.316, 2.15] | 28.2: (14.7, 100] |
| RS[5,3] | [3.81, 9.10] | 4.90 ± 0.08 | 4.6: (0.316, 1.33] | 8.3: (23.7, 100] |
| RS[7,4] | [2.00, 14.73] | 5.49 ± 0.14 | 3.9: (0.316, 2.15] | 12.8: (14.7, 100] |
| Tiger | [3.98, 5.62] | 4.21 ± 0.07 | — | 5.4: (19.3, 43.9] |
| Tileworld-6×6 | [14.92, 33.70] | 14.83 ± 0.22 | 17.7: (5.62, 23.7] | 30.9: (23.7, 100] |

Explicitly an atlas of *measured operating points*, not a predictive meta-model —
no closed form relating B_EFE to environment parameters is claimed.

---

## 12. Related work positioning (for a "prior art" panel)

- **POMDPs and solvers:** exact solution is PSPACE-complete; point-based offline
  (PBVI, HSVI, SARSOP) and online (POMCP, DESPOT, POMCPOW) methods all explore
  implicitly rather than valuing information explicitly.
- **ρ-POMDPs (Araya-López et al. 2010):** introduced belief-dependent utility;
  convex ρ preserves piecewise-linear-convex value functions; Fehr et al. (2018)
  extend to Lipschitz-continuous non-convex ρ (the regime this paper's ρ_EFE
  actually falls into, since information gain is concave, not convex, in belief).
  POMDP-IR (Spaan et al. 2015) is closely related, shown equivalent by Satsangi
  et al. (2018).
- **Value of information / experimental design:** Howard (1966) value of
  information; Lindley (1956) expected information gain for Bayesian experimental
  design; Bernardo (1979) grounds the reward-to-information identification (exact
  under log scoring rules); information-directed sampling (Russo & Van Roy 2014)
  minimizes a *ratio* Γ_t = δ_t²/g_t per step, contrasted with EFE's *fixed*
  absolute weight w=1.
- **Active inference and EFE:** Friston (2010) free-energy principle; Friston et
  al. (2015) pragmatic/epistemic decomposition; Da Costa et al. (2020) discrete
  synthesis; Parr et al. (2019) shows EFE decomposition requires no tunable
  exploration weight; critical examination by Millidge et al. (2021, FEEF),
  Champion et al. (2026, unification of four EFE formulations), de Vries et al.
  (2025, variational message passing recasting).
- **Sophisticated inference (Friston et al. 2021; Da Costa et al. 2023):** closed-
  loop recursive tree search over belief trajectories; proven Bellman-optimal for
  any finite horizon — this paper's recursive EFE agent is derived from this
  framework.
- **Scaling active inference:** Fountas et al. (2020, deep generative models +
  MCTS); Tschantz et al. (2020, RL-compatible FEEF objective); Maisto et al.
  (2025, AIF + MCTS on RockSample, state-of-the-art) — this paper's MCTS-EFE
  variant follows this direction.
- **Exploration / control-as-inference / intrinsic motivation:** control-as-
  inference (Todorov 2007; Levine 2018); max-entropy RL (Haarnoja et al. 2018);
  curiosity and intrinsic-motivation methods (Schmidhuber 1991; Pathak et al.
  2017; Itti & Baldi 2009; Bellemare et al. 2016; Houthooft et al. 2016; Burda et
  al. 2019) all require tunable bonus weights, unlike the derived w=1.
- **Resource-constrained information acquisition (for the budgeted section):**
  rational inattention (Sims 2003; Matějka & McKay 2015), constrained MDPs/POMDPs
  (Altman 1999; Kim & Lim 2011), SAC temperature auto-tuning (Haarnoja et al.
  2018b), sequential Bayesian experimental design (Lindley 1956; Foster et al.
  2021 — amortized/"deep adaptive design").

---

## 13. Practical guidance: when to use EFE-as-ρ (bulleted checklist, verbatim structure)

**Favors EFE:**
- Reward asymmetry α ≥ 5 (penalty for a wrong commit far exceeds observation cost)
- Multiple observation actions (EFE selects *which* information to gather)
- Moderate-to-large state spaces (|S| ≥ 16), advantage grows with |S|, up to
  |S| = 65,536 demonstrated
- Interleaved observe-act with preserved hidden state (factored observation
  POMDPs)
- Cross-environment deployment where the weight cannot be tuned per task
- Planning horizon H ≥ 2 (recursive EFE propagates epistemic value across steps)
- Discounting γ ≥ 0.99

**Not recommended:**
- Symmetric penalties (α ≈ 1)
- Navigation-style POMDPs where observation is tied to translation (a greedy
  mover already gets informative feedback) — NavMyopic leads at 3×3, 5×5, 7×7
- Model misspecification exceeding ±0.15 in observation accuracy
- Settings where information-gathering actions change the hidden state
  (destructive sensing) — requires the full, currently unaddressed, coupling term

---

## 14. Limitations (for an honest "what this doesn't solve" panel)

1. **Destructive sensing.** The formal equivalence only covers observe-then-commit
   and factored-observation (hidden-state-preserving) POMDPs. When information
   gathering changes the hidden state (drilling, biopsy, chemical assay,
   predator-prey), the coupling term Δ_T ≠ 0 and naive information gain can
   misvalue an action outright (worked counterexample, Section 6.6 above). No
   corrected operator is proposed.
2. **Distractor sensing.** Neither ordinary information gain nor the tested IDS
   adaptation is immune to spending a sensing budget on reward-irrelevant
   uncertainty (Section 11.8). A sensing budget caps total spend; it does not by
   itself redirect spend toward reward-relevant tests.
3. **Discount sensitivity.** EFE's advantage on multi-observation environments
   requires γ ≥ 0.99; it disappears or reverses under heavier discounting
   (Section 10.6).
4. **Model misspecification.** Investigated only up to ±0.15 accuracy mismatch;
   overestimating sensor accuracy is more harmful than underestimating it.
5. **Navigation-style domains.** Scale alone does not rescue epistemic planning
   when observations are proximity-based side effects of movement rather than
   discrete choices.
6. **Known generative model assumed.** Full model learning (where active
   inference and Bayes-Adaptive MDPs converge) is left to future work.
7. **MCTS-EFE scalability.** Larger observation spaces need more efficient tree
   policies (e.g., progressive/double progressive widening); left to future work.
8. **w* atlas is descriptive, not predictive.** No closed-form relationship
   between the implicit EFE budget and environment parameters (reward scale,
   state count, horizon) is claimed.
9. **Dual-controller convergence proposition (PI-5) is conditional** on a single,
   sign-consistent crossing of the budget; silent when the usage curve crosses
   the budget more than once. The reset-on-shift mechanism used empirically is
   *not* covered by the stationary-convergence guarantee — it's a distinct,
   heuristic nonstationary re-adaptation mechanism.

---

## 15. Verification / fact-check flags (per the standing rule to double-check citations and figures before use)

Before finalizing poster text, re-verify the following against the manuscript and
underlying result CSVs (do not trust this summary as a final source for exact
figures used in printed poster copy):

- The abstract's "+7.34 reward over reward-only Planning on RockSample[7,8]"
  figure should be traced to its exact source computation (candidate
  reconciliation: Plan+IG(w=5) minus Planning on RS[7,8] is 22.14 − 12.31 = 9.83,
  and EFE(w=1) minus Planning is 19.65 − 12.31 = 7.34 — the abstract figure
  matches **EFE minus Planning**, not the tuned agent minus Planning; confirm
  this reading is what is intended before printing it standalone without that
  qualifier on a poster).
- All citation years/venues listed in Section 12 above should be spot-checked
  against the manuscript's bibliography (`paper/full_paper.tex`, lines ~807
  onward) if quoted directly on the poster, per standing citation-verification
  practice. Notably Champion et al. is dated 2026 in the bibliography entry
  (`Neural Computation`, 38(3):439-469, 2026) despite the in-text citation key
  `champion2024` — use the bibliography year (2026), not the citation key year,
  if printing a reference list.
- Numbers pulled from appendices (discount sensitivity, misspecification, POMCP
  compute-matched analysis, horizon map) should be re-cross-referenced against
  `paper/full_paper.tex` directly if used verbatim, since this document
  paraphrases some appendix prose.
- If the Minds and Machines production/proof version renumbers propositions,
  figures, or tables relative to `paper/full_paper.tex`, update all
  proposition/figure/table labels in this document to match before designing the
  poster.

---

## 16. Figure inventory (all generated PDFs in `figures/`, with suggested poster role)

| File | Manuscript figure | Suggested poster role |
|---|---|---|
| `fig_pareto.pdf` | Fig. `pareto` | **Strong candidate.** Success vs. reward frontier, w=1 marker at the knee — the single best visual for the core thesis. |
| `fig_tileworld_comparison.pdf` | Fig. `tw_comparison` | **Strong candidate.** Side-by-side agent behavior on one episode; visually intuitive "EFE commits efficiently" story. |
| `fig_tileworld_scaling.pdf` | Fig. `tw_scaling` | **Strong candidate.** The 66.5% vs 2.5% scaling headline number, visualized. |
| `fig_tileworld_belief.pdf` | Fig. `tw_belief` | Belief-evolution strips; good supplementary/detail panel. |
| `fig_efe_trajectory.pdf` | Fig. `traj` | EFE decomposition / commit-crossover visualization; good for explaining mechanism. |
| `fig_asymmetry_sweep.pdf` | Fig. `sweep` | Tiger reward-asymmetry sweep; supports robustness-to-scale narrative. |
| `fig_obs_scaling.pdf` | Fig. `obs_scaling` | EFE's advantage grows with number of observation actions K. |
| `fig_nearopt_horizon.pdf` | Fig. `nearopt_horizon` | Near-optimality basin widening with horizon; supports Prop. 2 story. |
| `fig_accuracy_sensitivity.pdf` | (misspecification, referenced in appendix) | Supplementary robustness panel. |
| `fig_belief_heatmap.pdf` | (supplementary) | Supplementary visualization. |
| `fig_efficiency_curves.pdf` | (supplementary statistics appendix) | Supplementary. |
| `fig_extended_efe.pdf` | (extended EFE decomposition appendix) | Supplementary. |
| `fig_reward_scaling.pdf` | (reward-rescaling invariance appendix) | Supports scale-equivariance narrative directly — check before excluding. |
| `fig_stopping_times.pdf` | (stopping-time analysis appendix) | Supplementary. |
| `fig_tileworld_scan_atlas.pdf` | (supplementary) | Supplementary. |
| `price_scale_invariance.pdf` | Fig. `collapse` | **Strong candidate for budget section.** Curve collapse across reward scales — the visual proof of Prop. PI-1. |
| `price_prop2_jumps.pdf` | Fig. `prop2` | Onset of observing vs. closed-form threshold; ties theory to data cleanly. |
| `price_dual_multiseed.pdf` | Fig. `dualmultiseed` | **Strong candidate.** Multi-seed dual-control re-adaptation through a reward rescale; visually clear "faster recovery" story. |
| `price_dual_descent.pdf` | (single-trajectory dual descent, earlier workshop result) | Possibly superseded by multiseed version; check before including both. |
| `price_dual_reset.pdf` | (reset-on-shift mechanism illustration) | Supplementary / mechanism detail. |
| `price_cost_budget.pdf` | Fig. `costbudget` | Cost- vs. count-denominated usage curves; good for "budgets need units" panel. |
| `price_staircase_interleaved.pdf` | Fig. `interleaved` | Usage staircases for RockSample/Inspection; supports interleaved-settings extension. |
| `price_shadow_curves.pdf` | Fig. `stairs` | Shadow-price staircases across five environments; good overview panel. |
| `distractor_composition.pdf` | Fig. `distractor` | **Good for limitations panel.** Distractor usage vs. w, with onset and saturation. |

Compiled reference PDFs also available: `paper/paper.pdf` (NeurIPS-style),
`paper/paper_arxiv.pdf` (LLNCS/arXiv), `paper/full_paper.pdf` (integrated
long-form, matches this document), `paper/price_of_information.pdf` (budget
extension standalone).

---

## 17. Suggested poster narrative arcs (pick one; comprehensive options for editorial pass)

**Arc A — "Two results in one paper" (broadest coverage):**
1. Problem: information has no intrinsic value in POMDPs; ρ-POMDPs fix this but
   need a hand-tuned weight.
2. Result 1: active inference derives that weight for free (w=1), competitive
   across environments up to 65,536 states (Fig. `pareto`, Fig. `tw_scaling`).
3. Result 2: that weight isn't scale-invariant, so reframe it as a sensing
   budget's shadow price — exactly scale-equivariant, computable offline,
   trackable online (Fig. `collapse`, Fig. `dualmultiseed`).
4. Honest limits: destructive sensing, distractor sensing (one panel).
5. Takeaway: "what should w be" becomes "how much sensing can you afford."

**Arc B — "Theory-first" (for a more mathematically inclined audience):**
Lead with Proposition 1 (equivalence) and Proposition PI-1 (scale equivariance)
side by side as the two formal pillars, then use experiments as validation
panels underneath each.

**Arc C — "Applications-first" (for a more applied audience):**
Lead with Structural Inspection / RockSample as motivating real-world analogues
(industrial inspection, mobile sensing, medical testing), then reveal the theory
underneath as the reason it works, then close with the budget reframing as "how a
practitioner would actually deploy this."

---

## 18. Reproducibility / code pointers (for a QR-code or "try it yourself" panel)

- Repository: `https://github.com/PatrickAllenCooper/rho_aif`
- Full reproduction commands are enumerated in the main `README.md`
  ("Reproducing the Paper" table), covering every table and figure referenced
  above.
- Key scripts referenced directly in the manuscript text: `experiments/
  build_rocksample_tables.py`, `experiments/run_nearopt_horizon.py` +
  `experiments/build_horizon_map.py`, `experiments/run_price_of_information.py`,
  `experiments/run_sarsop_baseline.py`, `experiments/run_w_atlas.py`,
  `experiments/run_distractor_diagnosis.py`, `experiments/run_calibration_table.py`,
  `experiments/run_audit_case_study.py`.
- Key test files referenced directly in the manuscript text (useful as "verified
  numerically" citations on the poster): `tests/test_destructive_boundary.py`,
  `tests/test_budget.py` (`TestProp2OnsetExact`), `tests/test_sarsop_export.py`,
  `tests/test_distractor_diagnosis.py`.
