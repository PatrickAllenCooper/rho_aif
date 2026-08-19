# The Price of Destructive Information: Predeclared Study Design

**Date**: August 19, 2026
**Status**: Design predeclared before any implementation, per the project's empirical-rigor rule. No experiment in this document has been run. Changes to this protocol after data collection begins must be logged here with dated notes and reasons.
**Direction**: Rank 1 in `2026-08-19-post-jair-directions.md` (carried from Rank 2 of the July 22 ideation, confidence 80%).

## 1. Problem statement

The JAIR manuscript proves the EFE/rho-POMDP equivalence for hidden-state-preserving observation actions and exhibits a one-step counterexample (Example ex:destructive) where sensing changes the state it measures, making the state-preserving reduction rho = I(b) misvalue the action. The manuscript's transition-aware operator prices the destructive test correctly in that two-state example, and its Discussion defers the general treatment. This study supplies that treatment and joins it to the budget theory: when sensing destroys state, a test spends two currencies at once — the sensing budget B and future option value. The working thesis is that the shadow price of destructive information decomposes into an information price (the JAIR paper's w*(B)) plus an irreversibility premium, and that ignoring the premium produces systematic over-testing that no budget cap corrects.

## 2. Formal targets (theory work, in dependency order)

- **T1 (corrected operator, general form).** State the transition-aware EFE operator for factored observation POMDPs in which observation action k has an associated transition kernel T_k that is not the identity. Prove the equivalence proposition analogue: transition-aware EFE minimization equals a rho-POMDP with rho computed on the joint transition-observation posterior at w=1. Delta_T (already defined in the JAIR paper as the expected KL between the joint posterior and the observation-only posterior) quantifies the reduction error of the state-preserving operator.
- **T2 (over-testing characterization).** For the two-state destructive testbed (Section 4), derive the belief region where the state-preserving agent tests but the transition-aware agent commits, as a function of destruction probability delta, test accuracy p, and reward asymmetry alpha. Conjecture: the region is nonempty for every delta > 0 and grows monotonically in delta; over-testing loss is O(delta * R_max) per episode.
- **T3 (irreversibility premium).** Define the destructive shadow price w*_D(B) as the crossing bracket of the transition-aware usage curve U_D(w). Conjecture: U_D(w) <= U(w) pointwise (destruction suppresses sensing at equal weight), hence w*_D(B) >= w*(B) for budgets in the common achievable range. The premium pi(B) = w*_D(B) - w*(B) is the operational price of irreversibility. Prove or refute the pointwise ordering for exact maximizers at H=1; report the general case empirically with the same honesty discipline as PI-2 (exactness only where proved).
- **T4 (scale equivariance carryover).** Verify PI-1's exact scale-equivariance argument survives the transition-aware operator (every lookahead value still scales linearly in reward scale). Expected: yes, with the same proof shape; if so the destructive usage curves must collapse across reward scales, and this becomes the study's cheapest strong prediction.

## 3. Hypotheses (predeclared, falsifiable)

- **H1**: The state-preserving agent over-tests on destructive variants: its mean destructive-test count exceeds the transition-aware agent's at every w in the sweep, with the gap increasing in delta. Test: per-seed Welch t-test at each (delta, w) grid point with Holm-Bonferroni over the grid.
- **H2**: Budget caps do not fix misvaluation: at matched usage (same realized budget), the transition-aware agent achieves strictly higher reward than the state-preserving agent on destructive variants. Test: usage-matched reward comparison at the three canonical budgets, per-seed Welch, predeclared margin equal to one test's cost.
- **H3**: U_D(w) <= U(w) pointwise on the destructive Inspection variant (T3). Test: per-w one-sided per-seed comparison; report any violating w honestly.
- **H4**: Destructive usage curves collapse across reward scales alpha in {0.1, 1, 10} (T4), within 2 SE at every grid point, as in the JAIR collapse experiment.
- **H5**: The irreversibility premium pi(B) is positive and increasing in delta at the canonical budgets. No functional form is conjectured.

## 4. Environments (all discrete, exact Bayesian updates)

- **E1: Destructive two-state testbed.** The JAIR Example ex:destructive generalized: states {healthy, faulty}; one destructive test (accuracy p, destroys the unit with probability delta on faulty, delta/2 on healthy); commit actions {accept, reject}. Grid: delta in {0, 0.05, 0.1, 0.2, 0.4}, p in {0.7, 0.85}, alpha in {1, 5, 10}. Closed-form solvable at H<=2 for T2.
  - **Amendment (Aug 19, 2026, before any data collection):** commits on a DESTROYED unit earn -R+ (the unit's value is lost), not 0 as first written. Zero-value destroyed commits create a laundering artifact: at uncertain beliefs where both live commits have negative expected value (large alpha), destroying the unit strictly dominates deciding, so a transition-aware agent would spam the destructive test to escape penalties, contaminating the H1/H2 over-testing measurements. At -R+ the ordering is domain-faithful (correct call R+ > destroyed -R+ > wrong call -alpha R+ for alpha > 1): destruction caps catastrophic downside the way real destructive testing does, without being free. The theory notes (DI-2) derive the over-testing region under this convention.
- **E2: Destructive Diagnosis.** DiagnosisEnv (N=4) plus one destructive test per condition pair: informative but with probability delta the patient state advances irreversibly (absorbing worse state with reduced commit rewards). delta in {0.05, 0.2}.
- **E3: Destructive Structural Inspection.** InspectionEnv (N=8) where each test damages the tested component with probability delta (flips it to faulty if healthy), so testing can create the fault it looks for. delta in {0.02, 0.1}. This is the flagship: it makes the "budget caps waste but cannot redirect it" boundary vivid, and reuses the factored belief machinery.

## 5. Agents

1. State-preserving EFE (current EFEAgent, w=1) — the misvalued baseline.
2. Transition-aware EFE (new; T1 operator, w=1).
3. State-preserving Planning+IG at swept w — for U(w).
4. Transition-aware Planning+IG at swept w — for U_D(w).
5. Reward-only Planning (immune to misvaluation by construction; controls for the epistemic term).
6. Myopic — weak baseline.

## 6. Protocol (inherits the house rules)

Canonical seeds {42, 123, 456, 789, 1024}; per-episode env seeds seed*10000+i; 500 episodes per seed for E1/E2, 200 for E3; seed-level Welch t-tests primary with Holm-Bonferroni; no seed-level Cohen's d; usage curves on the standard log-w grid with crossing brackets; provenance columns stamped in every CSV; every table produced by a scripted builder mapped in the README; TOST only with the predeclared margins above. Any deviation gets a dated note here before the run.

## 7. Deliverables and destination

Target: a self-contained sequel paper ("The Price of Destructive Information") aimed at JAIR or UAI depending on final length, with the corrected operator + premium theory + three-environment battery. Secondary: the reward-conditional information measure (post-JAIR directions, Direction 2) shares E2/E3 infrastructure and may fold in as a section if the distractor-redirect experiments come out clean; decide after H1-H5 data lands, not before.

## 8. Work stages (verdicts recorded here, mirrored in research_plan.md)

- **DS-A**: T1 statement and proof draft in this repo's guidance style. Acceptance: consistent with the existing Example ex:destructive and Delta_T definition; no new citations without verification records.
- **DS-B**: E1-E3 implemented with tests (belief updates under destruction verified against hand-computed posteriors). Acceptance: 100% pass, including a regression test reproducing the JAIR example's ranking flip. **Verdict (Aug 19, 2026): PARTIAL-HOLD -- E1 done and accepted (DestructiveTestbedEnv, hand-computed posterior tests, destruction-frequency tests under seeded streams, the ex:destructive regression); E2/E3 not yet built.** Modeling deviation logged: E1 uses an absorbing zero-value DESTROYED third state rather than the paper example's destroyed-coincides-with-state-0 extreme, so partial destruction (delta < 1) is expressible; the example's exact arithmetic is reproduced separately in tests.
- **DS-C**: Agents 2 and 4 implemented; Prop-1-style equivalence test between them at w=1. Acceptance: exact agreement within 1e-12 tie-breaking, mirroring tests/test_efe_pig_equivalence.py. **Verdict (Aug 19, 2026): HOLD -- TransitionAwareEFEAgent and TransitionAwarePlanningIGAgent land with the w=1 exact-equivalence test, delta=0 exact agreement with the state-preserving agents, and the joint posterior b'(s') proportional to sum_s T(s'|s) O(o|s) b(s) per the manuscript's pre-transition-emission convention. 49/49 tests passing.**
- **DS-D**: H1-H5 batteries run under the Section 6 protocol. Acceptance: every hypothesis gets a verdict (supported / refuted / mixed) with numbers; refutations are reported, not repaired post hoc.
- **DS-E**: Paper assembly, referee simulation loop, venue decision.
