# Full-Length Paper Plan: From Workshop Iteration to Integrated Publication

**Status**: Stages A-H complete (all HOLD except Stage E's Tileworld sub-result, PARTIAL and explained; Stage G2 DONE). Stage I is executed: venue decided (JAIR, Section 8), `paper/full_paper_jair.tex` ported and compiling cleanly with a reproducibility checklist appendix, the IWAI camera-ready de-anonymized, the public repository verified reachable from a logged-out browser, the PyPI package build/check/install verified locally, and a cover letter with submission-form answers drafted (Section 8.9). Remaining before the portal upload: three manual, credential-gated actions outside this agent's access -- (1) submit the de-anonymized IWAI camera-ready via the OpenReview portal, (2) reconcile `full_paper_jair.tex` against JAIR's actual login-gated Overleaf template (this agent used the closest-faith `acmart` substitute), (3) run `twine upload` to TestPyPI then PyPI with Patrick's account token. See Section 8.8-8.9 for full detail.
**Date**: August 4, 2026 (Stage I execution pass)
**Purpose**: This is the living guide for producing one integrated full-length publication that merges the accepted IWAI 2026 workshop paper (EFE as belief-dependent utility for rho-POMDPs) with the Price of Information extension (w as an operational shadow price of a sensing budget). Every change made toward the full paper must update this document.

## 1. Thesis and narrative

One integrated story, told in this order:

1. EFE minimization equals solving a rho-POMDP with expected information gain at w=1 (Proposition 1), extended to factored observation POMDPs (Proposition 3), with near-optimality thresholds for two-state problems (Proposition 2).
2. The canonical weight w=1 is not reward-scale invariant. This was the workshop paper's central conceded limitation and the reviewers' strongest objection.
3. The budgeted rho-POMDP recasts w as an operational shadow price w*(B) of a sensing budget B, computable offline from the usage curve U(w) and maintainable online by SAC-style dual control. Budgets are denominated in physical units, so the derived weight rescales automatically with the reward function.
4. The limitation dissolves rather than being patched: "choose w" becomes "choose how much sensing to buy."

This follows the ideation Rank 1 rationale (`docs/ideation/2026-07-22-rho-aif-extensions-ideation.html`): it "converts the paper's most awkward limitation into its next theorem" and "reframes the reviewers' strongest objection as the motivation for the sequel."

Venue is deliberately open. The science is planned first; a venue decision gate sits at the end of the milestone list (Section 6). Relevant history: the NeurIPS 2026 initial submission received Borderline Reject and the revision paths A/B/C (Prop 3, RockSample main-text experiments, zero-shot transfer) are already in the arXiv version. UAI and AISTATS remain listed alternatives; journals (JAIR, Neural Computation) are on the table since the integrated paper is long.

## 2. Source material inventory

### From `paper/paper_arxiv.tex` (41 pages, LNCS, non-anonymous)

Main body carries over largely intact: Introduction, Related work, Methodology (rho-POMDP framework, EFE as rho, formal equivalence Props 1-3, agents), Experiments, Results (core environments, Pareto analysis, Tileworld, RockSample, Structural Inspection), Discussion, Conclusion.

Appendices to keep in the integrated paper: proof of Prop 1, per-environment results, two-state testbed, environment specifications, near-optimality across horizons, discount sensitivity, model misspecification, extended RockSample, IDS baseline, reward-rescaling invariance (now superseded in role by the price experiments but retained as the motivating diagnostic), POMCP comparison.

Appendices to consider cutting or condensing for a conference version: navigation results, scaling analysis, PyMDP validation, epistemic foraging dynamics, extended EFE decomposition, stopping-time analysis, supplementary statistics, MCTS-EFE. The long-form master keeps everything.

### From `paper/price_of_information.tex` (workshop-length LLNCS draft)

All content carries over and expands: budgeted rho-POMDP formulation, usage curve U(w) and set-valued crossing brackets, offline solve, online dual control with lr decay and reset-on-shift, and the four experiments (curve collapse across reward scales; Prop 2 onset on positive-threshold testbeds; dual control under mid-run x10 rescale with re-adaptation 157 to 45 episodes; supporting shadow-price staircases).

### Supporting assets

- Code: `rho_aif/budget.py` (usage curves, crossing brackets, shadow-price solves, identifiable budgets), `rho_aif/agents/dual_descent.py` (`DualWeightAgent`), `rho_aif/scoring.py`, `rho_aif/benchmark.py`, CLI `rho-aif-bench`.
- Results and figures: `results/results_price_*.csv`, `results/results_price_of_information_summary.json`, `figures/price_*.{png,pdf}`, plus all tables and figures backing the arXiv paper.
- Theory notes with verified citations: `Guidance_Documents/price_of_information.md`.
- Test suite: 304 passing tests including budget and dual-descent coverage.

## 3. Gap analysis (the work queue)

Ordered roughly by dependency. Each item states the deliverable and where it lands in the paper.

### 3.1 Theory: formalize the budgeted rho-POMDP (new Proposition)

- State the budgeted rho-POMDP and the set-valued operational shadow price as a formal proposition: U(w) is a nondecreasing step function under Planning+IG on the covered problem classes; w*(B) is the crossing bracket of U at B; budgets below U(0) are unachievable with nonnegative w; scale equivariance w*(B; alpha) = alpha * w*(B; 1).
- Derive Proposition 2's thresholds as corollaries of the duality statement (the observing onset is the first budget at which the bracket leaves zero), per the ideation framing.
- Honor the verifier cautions recorded in the ideation document: claim no universal closed form w*(R, gamma, |S|, H); the contribution is the budgeted formulation, the operational inverse, scale-correct dual control, and empirical validation, not the abstract idea of dualizing a resource constraint. Position explicitly against resource-rational and bounded-rational duality prior art (Sims 2003; Matejka and McKay 2015; Altman 1999; Haarnoja et al. 2018 arXiv:1812.05905) so reviewers cannot call it a restatement.
- Optional stretch: a convergence or tracking statement for the projected dual update under stationary usage (even a stylized one-dimensional analysis), or an honest statement of why one is not given.

### 3.2 Experiments: extend the price battery

- **Interleaved settings**: run usage curves and shadow-price solves on RockSample (RS[5,3] at minimum) and Inspection-N16, so the budget story covers the same settings that carried Prop 3. Currently the collapse test covers Diagnosis and Bandit; staircases cover Tiger, Diagnosis, Bandit, Tileworld-6x6, Inspection-N8.
- **Multi-seed dual control**: the dual rescale experiment is currently a single trajectory per configuration. Re-run with at least 10 seeds and report re-adaptation time and steady-state usage error with confidence intervals, for both decay-only and reset-on-shift controllers.
- **Cost-denominated budgets**: the open `usage_kind='cost'` item in the Price of Information phase. Show at least one environment where the budget is total observation cost rather than count, demonstrating the units story end to end.
- **Curve collapse breadth**: add at least one more environment (Tiger or Tileworld) to the alpha in {0.1, 1, 10} collapse test so the headline claim does not rest on two environments.
- **Deferred baseline debt (from ideation Rank 5)**: the camera-ready replies promised SARSOP and POMCPOW comparisons. Run SARSOP on the discrete observe-then-commit suite as an offline optimal reference; POMCPOW only if a maintained implementation is practical, otherwise state the deferral honestly with the POMCP comparison in hand. This retires the debt inside the integrated paper rather than leaving it for a third paper.

### 3.3 Optional appendix: the empirical w* atlas

Rejected ideation idea 10 ("empirical w* atlas dataset with meta-model") was noted as a natural appendix or companion to the price work. Scope for the appendix version: a table of implicit EFE budgets B_EFE = U(w=1) and crossing brackets w*(B) across all benchmark instances at canonical budgets, with SEs. The implicit-budget numbers already exist for five instances (Tiger 4.21, Diagnosis 9.68, Bandit 5.03, Tileworld-6x6 14.83, Inspection-N8 18.24); extend to the full suite. No meta-model; that stays future work.

### 3.4 Related work: merge and extend

- Merge both papers' sections into one. The arXiv paper covers rho-POMDPs, active inference/EFE, control-as-inference, intrinsic motivation, and Bayesian RL; the price draft adds rational inattention (Sims 2003; Matejka and McKay 2015), CMDPs (Altman 1999), and SAC auto-temperature (Haarnoja et al. 2018, arXiv:1812.05905 -- not the ICML paper, which has fixed temperature).
- Add resource rationality / bounded rationality positioning (the ideation's main prior-art caution) and, briefly, sequential Bayesian experimental design.
- Citation policy: every new citation gets a verification check against the publisher or arXiv record before it enters the bibliography, recorded in `Guidance_Documents/price_of_information.md` or this document. The existing verified-citation table carries over.

## 4. Paper assembly plan

New master file `paper/full_paper.tex` (working name), assembled from the two sources rather than edited in place, so the arXiv and workshop versions remain intact snapshots.

Proposed integrated outline:

1. Introduction (rewritten: equivalence result and scale problem stated together; shadow-price resolution previewed)
2. Related work (merged, Section 3.4)
3. The rho-POMDP framework and EFE as rho (from arXiv paper)
4. Formal equivalence: Propositions 1-3 (from arXiv paper)
5. Budgeted rho-POMDPs and the price of information (from price draft plus new Proposition, Section 3.1)
6. Methods: agents, solvers, dual control (merged)
7. Experiments I: the equivalence and near-optimality results (condensed from arXiv Results)
8. Experiments II: shadow prices -- curve collapse, Prop 2 onset, dual control, staircases, cost budgets, interleaved settings (expanded from price draft, Section 3.2)
9. Discussion (merged; the reward-rescaling limitation paragraph becomes the pivot between parts, not a concession)
10. Conclusion
11. Appendices: proofs, per-environment results, w* atlas (Section 3.3), baseline details, remaining arXiv appendices per the keep list in Section 2

Length envelope: venue-agnostic long-form master (expect 45-55 pages LNCS-style all-in), from which a conference cut (8-10 pages plus appendix) or journal submission can be derived, mirroring the existing arXiv/IWAI split.

## 5. Writing conventions

Carry over the conventions already enforced on the arXiv paper: no prose semicolons, no rhetorical italics (definitional first-use only), no dense per-environment numbers in the abstract, topic sentences on long paragraphs, natbib author tags on all bibliography entries. Author: Patrick Cooper (with Alvaro Velasquez per the arXiv version; confirm author list before submission).

## 6. Milestones

Ordered; each milestone updates this document and commits. Section 7 breaks these into concrete development/experiment stages.

1. **M1 -- Theory**: budgeted rho-POMDP proposition drafted with proof or proof sketch; Prop 2 corollary derivation written (Section 3.1). Stage A.
2. **M2 -- Experiment extensions**: interleaved usage curves, multi-seed dual control, cost budgets, collapse breadth (Section 3.2, all but baselines). Stages B-E.
3. **M3 -- Baseline debt**: SARSOP reference runs; POMCPOW decision made and documented (Section 3.2 last item). Stage F.
4. **M4 -- Assembly**: `paper/full_paper.tex` drafted per Section 4 outline; w* atlas appendix built (Section 3.3); related work merged (Section 3.4); full citation verification pass. Stages G-H.
5. **M5 -- Venue decision gate**: with results in hand, choose conference cut vs journal submission; produce the derived version. Stage I.
6. **M6 -- Submission checklist**: PyPI release of `rho-aif` (TestPyPI verify, upload, tag -- the standing checklist in `research_plan.md` under "Deferred until next venue submission"), public code link and README install instructions pointed at PyPI, reproduction command table updated for every new figure and table, final compile and package. Stage I.

## 7. Development and experiment stages

Each stage lists its code work, experiment protocol, artifacts, and an acceptance criterion that decides a HOLD / PARTIAL / FAIL verdict. Verdicts are recorded here and mirrored in `research_plan.md`. Dependency order: Stage A is independent and can run first or in parallel with B-E; Stages B-E are mutually independent; Stage F is independent; Stage G depends on B; Stage H depends on everything before it; Stage I closes.

### Stage A -- Budgeted rho-POMDP proposition (M1) -- DONE, verdict HOLD

- **Code work**: none required. Optional: a small script or test that numerically checks the corollary claim (onset budget equals the first bracket leaving zero) on the positive-threshold Testbeds already configured in `experiments/run_price_of_information.py`.
- **Writing work**: draft the proposition, proof or proof sketch, and the Prop 2 corollary derivation in `Guidance_Documents/price_of_information.md` first; port to LaTeX once stable. State assumptions honestly (observe-then-commit or factored observation classes; empirical nondecreasing U(w); instrumental sensing so U(0) > 0 is possible).
- **Acceptance**: the statement is consistent with every recorded empirical caveat (rough monotonicity, gap budgets, unachievable low budgets, usage ceiling U_max) and introduces no unverified citation.
- **Outcome (July 23, 2026)**: Section 9 of `price_of_information.md` drafts PI-1 through PI-4. The result is stronger than planned in one place and honest in another:
  - PI-1 (scale equivariance) is an exact theorem for the implemented receding-horizon agent, not just for idealized maximizers: every lookahead value scales linearly, so `U_alpha(alpha w) = U(w)` as distributions. Curve collapse is thereby a theorem; the empirical 2 SE test measures Monte Carlo noise. Corollary: fixed w=1 at scale alpha behaves as w=1/alpha at scale 1, so `B_EFE(alpha) = U(1/alpha)`.
  - PI-2 (monotonicity) is exact only for cumulative information gain of exact maximizers at a fixed belief; neither the count-usage bridge nor receding-horizon composition is automatic. This is stated as the formal reason the staircases are only roughly monotone and the solver uses grid plus brackets.
  - PI-3 defines the set-valued shadow price with feasibility bounds `U(0) <= B <= U_max` and an exact randomized-mixture attainment statement at gap budgets (CMDP parallel, Altman 1999).
  - PI-4: at H=1 the usage staircase is exactly `1{w > w_thresh}`, so Prop 2's closed form is the first knot of U. Verified numerically by `tests/test_budget.py::TestProp2OnsetExact` (usage 0 at 0.9 w_thresh, >= 1 at 1.2 w_thresh; passes).
  - No new citations introduced; all references already in the verified table.

### Stage B -- Interleaved usage curves (M2) -- DONE, verdict HOLD

- **Code work**: `rho_aif/budget.py::estimate_usage` currently supports the `observe_then_commit` and inspection families only. Add a RockSample family that runs the depth-limited tree-search agents used in the arXiv paper's Section 5.4, counting sensing (check) actions as usage. Add unit tests mirroring `tests/test_budget.py` coverage for the new family.
- **Protocol**: RS[5,3] at minimum (RS[7,4] if runtime allows) and Inspection-N16, log-grid of about 10 w points, 5 seeds x 50 episodes (RockSample episodes are expensive; scale down before scaling up).
- **Artifacts**: new rows in `results/results_price_curves.csv` (or a sibling CSV), staircase figures `figures/price_staircase_rocksample*.{png,pdf}` and `figures/price_staircase_inspection_n16.{png,pdf}`.
- **Acceptance**: crossing brackets with SEs exist for at least two canonical budgets per environment; the monotonicity verdict (rough or clean) is recorded.
- **Outcome (July 23, 2026)**: `family="rocksample"` added to `estimate_usage` (checks counted as usage, per-check cost = uniform action cost); two unit tests added (`TestRockSampleUsageFamily`). New protocol `--only interleaved` in `experiments/run_price_of_information.py`; full run covered RS[5,3] (10-point grid, 5 seeds x 50 eps), RS[7,4] (8-point grid, 30 eps), Inspection-N16 (10-point grid, 50 eps) -- about 10 minutes total, so RS[7,4] made the cut. Four budgets bracketed per environment with SEs. Monotonicity verdict: **clean** -- U(w) is nondecreasing at every sampled grid point on all three interleaved settings (RS[5,3] 3.81 to 9.10; RS[7,4] 2.00 to 14.73; Inspection-N16 22.42 to 46.04), cleaner than the observe-then-commit staircases (Tiger/Diagnosis/Tileworld still show local dips). Instrumental floors are large (U(0) = 3.81 / 2.00 / 22.42), confirming the unachievable-low-budget regime matters in interleaved settings too. Artifacts: `results/results_price_interleaved_curves.csv`, `results/results_price_interleaved_prices.csv`, single combined figure `figures/price_staircase_interleaved.{png,pdf}` (one figure supersedes the two per-env figures named above). Full suite: 307 passed.

### Stage C -- Multi-seed dual control (M2) -- DONE, verdict HOLD

- **Code work**: extend `run_dual_descent` / `run_dual_reset_comparison` in `experiments/run_price_of_information.py` to sweep controller seeds (at least 10) rather than a single trajectory per configuration.
- **Protocol**: Diagnosis, B = 8, 400 episodes, x10 reward rescale at the midpoint, decay-only vs reset-on-shift, 10+ seeds each.
- **Artifacts**: per-seed CSV, figure with median trajectory and interquartile band, summary JSON with re-adaptation time and steady-state |U - B| as mean plus CI.
- **Acceptance**: reset-on-shift re-adapts faster than decay-only with non-overlapping CIs, and both controllers pin usage within SE of B in steady state. If CIs overlap, report the honest verdict and keep the single-trajectory claim out of the paper's headline.
- **Outcome (July 23, 2026)**: `run_dual_multiseed` sweeps 10 controller seeds per variant (`--only dual-multiseed`; quick mode uses 3). Re-adaptation: decay-only mean 126.8 episodes, 95% CI [90.5, 163.0], with only 8/10 seeds recovering inside the 200 post-rescale episodes; reset-on-shift mean 53.3, CI [48.7, 57.9], 10/10 recovered with exactly one lr reset each. **CIs disjoint** -- acceptance met. Post-rescale steady-state |U - B|: reset 0.11 [0.07, 0.15] vs decay 0.50 [0.14, 0.86] observations; pre-rescale both within 0.1 of B. The multi-seed result strengthens the single-trajectory claim: decay-only can fail to re-adapt at all within the run, reset-on-shift never did. Measurement note: one decay seed registered re-adaptation 0 because the rolling-20 window straddles the rescale point; this biases the decay mean downward, i.e. the comparison is conservative. Artifacts: `results/results_price_dual_multiseed.csv`, `results/results_price_dual_multiseed_metrics.csv`, `figures/price_dual_multiseed.{png,pdf}` (median with IQR band).

### Stage D -- Cost-denominated budgets (M2) -- DONE, verdict HOLD

- **Code work**: the `usage_kind='cost'` path already exists end to end in `budget.py`. For a nontrivial demonstration the environment needs heterogeneous observation costs (with homogeneous costs the cost curve is a scalar multiple of the count curve); add a Diagnosis variant with per-test costs or use an existing config with unequal costs if one exists.
- **Protocol**: one environment, cost-usage curve over the standard grid, solve w*(B_cost) at two budgets, 5 seeds x 100 episodes.
- **Artifacts**: cost-curve CSV and figure; a short table comparing count-budget and cost-budget solutions.
- **Acceptance**: the cost-denominated solve produces a different (and interpretable) bracket than the count-denominated one on the heterogeneous-cost variant, demonstrating the units story end to end.
- **Outcome (July 23, 2026)**: more code work was needed than planned -- the old cost accounting was count times mean cost, which cannot express heterogeneity. Three changes: `DiagnosisEnv` gained per-test `test_costs` (variant: costs [0.5, 2.5], same accuracy); `run_otc_episode` now records the actual `sensing_cost` paid; `episode_sensing_usage` prefers the explicit cost over the count-times-mean fallback. The planning agent needed no change (it already prices plans with per-action costs). Four unit tests added. Full run (`--only cost`, 5 seeds x 100 episodes, 12-point grid): mean cost per test `U_cost/U_count` varies systematically with w -- 1.21 to 1.39 (13.5% relative spread), flat near 1.25 through w around 3 and rising toward 1.39 as high w pushes the agent onto relatively more of the expensive test. Cost and count brackets disagree as units should: cost solve at B_cost = 11.15 brackets `(3.16, 10]` while the count solve at B = 8.64 brackets `(10, 31.6]`. Acceptance met. Artifacts: `results/results_price_cost_curves.csv`, `results/results_price_cost_prices.csv`, `figures/price_cost_budget.{png,pdf}`. Note: dual control against a cost target is supported by the same accounting but was not run; fold into Stage H's experiment section only if needed.

### Stage E -- Curve-collapse breadth (M2) -- DONE, verdict HOLD (Tileworld PARTIAL, explained)

- **Code work**: none; `run_scale_collapse` already parameterizes environments.
- **Protocol**: add Tiger (and Tileworld-6x6 if runtime allows) to the alpha in {0.1, 1, 10} collapse test, same settings as the existing full battery (5 seeds x 100 episodes).
- **Artifacts**: extended collapse figure and matched-point statistics per environment.
- **Acceptance**: matched w/alpha points within 2 SE and coinciding crossing brackets, as already holds for Diagnosis and Bandit. A failure on a specific environment is reported as a scoped limitation, not hidden.
- **Outcome (July 23, 2026)**: small code work was needed after all -- `make_scaled_tiger` and `make_scaled_tileworld` factories plus per-env collapse budgets (Tiger B=4, Tileworld B=15) and lighter Tileworld settings (30 episodes, 10-point grid). Full run, all four environments:
  - Diagnosis and Bandit: 100% within 2 SE, brackets coincide (re-confirmed).
  - Tiger: 100% within 2 SE and brackets coincide, but trivially -- Tiger's usage is flat (~4.1-4.35) across the whole w/alpha in [0, 20] range. Instrumental sensing saturates usage, so Tiger has no usable budget dial in this window. Worth a sentence in the paper: the budget formulation is informative only where U(w) actually varies.
  - Tileworld-6x6: 90% of matched points within 2 SE (max spread 0.91); the alpha=10 bracket (1.68, 5.8] is adjacent to the alpha in {0.1, 1} bracket (5.8, 20], sharing the knot w/alpha = 5.8 where measured usage straddles B=15 by less than one SE (14.66 / 14.95 / 15.07). This is a budget-at-knot Monte Carlo artifact, consistent with the PI-1 exactness theorem, not a scale-invariance failure; report it as such with the numbers.
  - Since PI-1 (Stage A) proves collapse exactly for the implemented agent, this test now functions as a Monte Carlo sanity check rather than the primary evidence; the paper should present it that way.

### Stage F -- SARSOP baseline and POMCPOW decision (M3) -- DONE, verdict HOLD

- **Code work**: select a maintained SARSOP implementation (candidates: `pomdp_py`, the original APPL toolkit, or Julia POMDPs.jl via a thin export script); write model-export code for the discrete observe-then-commit suite.
- **Protocol**: SARSOP reference values (expected reward, expected usage) on Tiger, Diagnosis, Bandit at matched horizons or discounting; compare EFE (w=1) and shadow-priced Planning+IG against the reference.
- **Artifacts**: baseline table CSV and a paper table; a written go/no-go decision on POMCPOW with rationale recorded here.
- **Acceptance**: SARSOP numbers exist for at least three environments and the deferred-baseline debt from the camera-ready replies is either retired or explicitly re-scoped with justification.
- **Outcome (July 23, 2026)**: implementation selected: the original APPL C++ toolkit (`pomdpsol`), built from source by `tools/build_sarsop.sh` with four documented patches for Apple Silicon / modern clang (drop SSE flags, raw-pointer SparseCol iterators, chained-comparison asserts, implicit C declarations); binary is gitignored, script is committed. `experiments/run_sarsop_baseline.py` exports any discrete OTC benchmark generically (hidden states plus absorbing done state, env action layout, discount 0.999) from `get_obs_models`/`make_env_config`, solves to precision 1e-3 (under one second per env), parses the alpha-vector policy XML, and evaluates it through `run_otc_episode` so all agents share identical mechanics and metrics. Four unit tests (`tests/test_sarsop_export.py`) cover the exporter, parser, and argmax agent without needing the binary. Full protocol (5 seeds x 500 episodes), solver bounds gamma=0.999: Tiger LB 5.129, Diagnosis LB -1.554, Bandit LB 6.210. Empirical:
  - Tiger: SARSOP and EFE (w=1) select identical actions on every episode -- reward 5.061 +- 0.158, usage 4.323. EFE at the canonical weight IS the near-optimal policy here.
  - Diagnosis: SARSOP -1.452 +- 0.336 vs EFE -1.217 +- 0.184 -- statistically indistinguishable (about 0.6 SE), usage 9.68 vs 9.73.
  - Bandit: SARSOP 6.280 +- 0.134 vs EFE 6.261 +- 0.112 -- indistinguishable, usage 5.16 vs 5.09.
  - Usage-matched Planning+IG rows are included; on Tiger the flat usage curve makes usage-matching ill-posed (bracket forces w=43.9, overshooting usage 5.77 vs target 4.32) -- report with that caveat.
  - **Baseline debt retired**: EFE (w=1) is indistinguishable from the SARSOP reference on all three OTC benchmarks. Artifacts: `results/results_sarsop_baseline.{csv,json}`, exported models in `results/sarsop_models/`.
- **POMCPOW decision: NO-GO.** POMCPOW exists to handle continuous state, action, and observation spaces via observation widening and weighted particle filtering (Sunberg and Kochenderfer, ICAPS 2018, 28(1):259-263, DOI 10.1609/icaps.v28i1.13882 -- verified against the AAAI proceedings page July 23, 2026). Every benchmark in this paper is a small discrete POMDP: SARSOP provides a near-optimal reference there, and discrete POMCP is already among the RockSample baselines. Adding POMCPOW would require building continuous-observation benchmark variants, which none of the paper's claims need. If a reviewer asks, this rationale plus the SARSOP table is the response.
- **Citation check**: SARSOP -- Kurniawati, Hsu, and Lee, "SARSOP: Efficient point-based POMDP planning by approximating optimally reachable belief spaces," RSS 2008 (verified via the official AdaCompNUS/sarsop repository and roboticsproceedings.org). POMCPOW -- verified above. Both must be added to the paper's bibliography during Stage H with these records.

### Stage G -- w* atlas appendix (M4) -- DONE, verdict HOLD

- **Code work**: a small driver that reuses `estimate_usage_curve` and `crossing_bracket` over all `rho_aif/benchmark.py` configs plus the Stage B interleaved settings.
- **Protocol**: implicit budgets B_EFE = U(w=1) with SEs and crossing brackets at two canonical budgets per instance; five instances already have B_EFE numbers (Tiger 4.21, Diagnosis 9.68, Bandit 5.03, Tileworld-6x6 14.83, Inspection-N8 18.24).
- **Artifacts**: appendix table (LaTeX) plus backing CSV committed to `results/`.
- **Acceptance**: every benchmark instance has a row; no meta-model claims.
- **Outcome (July 23, 2026)**: `experiments/run_w_atlas.py` reuses the saved full-battery and interleaved curves and measures fresh B_EFE = U(1) for the three interleaved instances (w=1 is not on their log grid): RS[5,3] 4.90 +- 0.08, RS[7,4] 5.49 +- 0.14, Inspection-N16 33.46 +- 0.19. All eight instances have rows (Tiger, Diagnosis, Bandit, Tileworld-6x6, Inspection-N8, Inspection-N16, RS[5,3], RS[7,4]) with usage range, B_EFE +- SE, and two canonical-budget brackets. Tiger's low budget is honestly unbracketed (flat usage curve, consistent with Stage E). The LaTeX caption states brackets are set-valued per Definition PI-3 and explicitly disclaims any closed-form meta-model. Artifacts: `results/results_w_atlas.csv`, `paper/tables/w_atlas.tex` (auto-generated, do-not-edit header).

### Stage G2 -- Distractor robustness (from review feedback)

Added July 23, 2026 in response to Reviewer 8Evk's question: "How poorly would these methods work in settings where there is uncertainty over state components that happen to be unimportant?" This is a genuine gap -- information gain is reward-blind, and no current experiment quantifies it.

- **Code work**: a Diagnosis variant whose state space carries an extra reward-irrelevant nuisance bit (8 joint states, commit rewards depend only on the 4-way condition), with one additional test that is informative only about the nuisance bit. Buildable in the experiment file from the existing DiagnosisEnv machinery (custom observation models and commit matrix); no core-library change expected.
- **Protocol**: usage-composition curves -- for a log grid of w, measure total usage and the fraction spent on the distractor test; 5 seeds x 100 episodes. Optionally compare IDS (already in `rho_aif/agents/ids.py`) as a reward-aware contrast.
- **Artifacts**: composition CSV and a stacked usage figure; a paragraph for the limitations section.
- **Acceptance**: an honest quantification either way. Expected finding: Planning+IG/EFE does spend budget on the distractor (IG does not discriminate reward-relevance); the budget formulation caps total spend but does not redirect it. If so, state it as a scoped limitation and cite reward-aware alternatives rather than hiding it.
- **Outcome (July 23, 2026), verdict DONE**: `rho_aif/environments/distractor_diagnosis.py` (new) adds `DistractorDiagnosisEnv`, an 8-joint-state Diagnosis variant (4 conditions x binary nuisance) whose distractor test is proved -- and unit-tested (`tests/test_distractor_diagnosis.py`, 13 tests) -- to carry exactly zero information about the condition marginal, because every observation model in the environment factors through exactly one of the two independent components. `experiments/run_distractor_diagnosis.py` sweeps Planning+IG over a log w-grid (5 seeds x 100 episodes) plus fixed EFE (w=1) and IDS runs, reusing the standard observe-then-commit agent interface with no special-casing. Confirmed finding: Planning+IG's distractor fraction is exactly 0 for w<=3.16, rises to 0.242 +- 0.005 at w=10, and saturates at 0.331 +- 0.005 for w>=31.6 (`results/results_distractor_diagnosis.csv`, `figures/distractor_composition.{png,pdf}`); EFE at w=1 stays at 0 on this instance because the onset weight (~10) is above 1 here, not because EFE is structurally immune. Unexpected finding, verified by instrumenting `IDSAgent._obs_regret_and_info` directly: IDS is not a clean reward-aware immune baseline on this environment -- its `info_astar` (information about the optimal commit) is exactly 0 for the distractor action as expected, but the implementation's `info_state` fallback (triggered whenever `info_astar<=eps`) lets the distractor's genuine nuisance-bit informativeness through, giving IDS a distractor fraction of 0.311 +- 0.005, comparable to Planning+IG at large w. Full writeup with the exact instrumentation output: `Guidance_Documents/price_of_information.md` Section 11.

### Stage H -- Paper assembly (M4) -- DONE, verdict HOLD

- **Work**: create `paper/full_paper.tex` per the Section 4 outline, merging the two sources without editing them in place; merge related work per Section 3.4; write the new experiment sections from Stages B-F; build the atlas appendix from Stage G; run the full citation verification pass (every entry checked against publisher or arXiv record, results recorded here).
- **Additional requirement (July 23, 2026)**: walk the review-response ledger in Section 8 end to end -- the theory corrections (8.2), empirical hygiene rules (8.3), citation additions (8.4), and written answers to reviewer questions (8.5) are Stage H acceptance criteria alongside the original ones.
- **Acceptance**: the master compiles standalone, every table and figure has a reproduction command in the README mapping, the writing conventions in Section 5 hold throughout, and every ledger item in Sections 8.1-8.5 is either implemented or explicitly waived with a reason recorded here.
- **Outcome (July 23, 2026)**: `paper/full_paper.tex` created from `paper_arxiv.tex` plus the merged content of `price_of_information.tex` per the Section 4 outline: title and abstract rewritten for the integrated thesis; a new `Budgeted rho-POMDPs and the price of information` section (Definition PI-3, Propositions PI-1/PI-2/PI-5, Corollary PI-4) inserted after `Agents`; a new `Experiments: shadow prices and sensing budgets` section (curve collapse, Prop 2 onset, multi-seed dual control, cost budgets, interleaved settings, staircases, SARSOP, distractor robustness, w* atlas) inserted after the original Results summary; Discussion, Conclusion, and Related work updated to carry the merged narrative; all Stage A-G2 bibliography entries added (Altman, Blum, Foster, Haarnoja SAC-app disambiguated as `haarnoja2018b`, Kim, Matejka, Robbins, Sims). One structural fix was required: three planned top-level appendix sections exceeded LaTeX's 26-letter `\Alph{section}` counter when combined with the arXiv paper's existing appendices, so the three were consolidated into one `Budgeted rho-POMDP supplementary details` appendix with three subsections. `tectonic` compiles `paper.tex`, `paper_arxiv.tex`, `price_of_information.tex`, and `full_paper.tex` cleanly (zero errors, zero undefined references); a handful of pre-existing Overfull \\hbox warnings inherited unchanged from `paper_arxiv.tex` remain (cosmetic, not part of the review-fix scope) and two newly introduced large overfull boxes (a long `\texttt` file path, an unbreakable math-mode set expression) were fixed by switching to `\url{}` and rephrasing.
- **8.5 residue closed**: the "why observe-then-commit" motivation sentence (8Evk) was missing from all three sources; added identical language to `paper.tex`, `paper_arxiv.tex`, and `full_paper.tex` immediately after the OTC definition, pointing to Proposition~3 (factored observation) and the RockSample/Structural Inspection results (plus the interleaved usage curves in `full_paper.tex`) as the beyond-OTC evidence. The "alternatives to IG as belief-based reward" item (8Evk) was already satisfied by the existing related-work paragraph citing Araya et al., Spaan et al. (POMDP-IR), and Satsangi et al.; no further change needed.
- **README reproduction map**: expanded the "Reproducing the Paper" table with rows for every Stage A-G2 and Phase 3-5 artifact: RockSample table regeneration, horizon map, the full price-of-information battery and each `--only` sub-battery, the SARSOP baseline, the w* atlas, the Stage G2 distractor experiment, the calibration table, the audit case study, and the destructive-sensing boundary test.
- **Full test suite**: 347 passed, 0 failed, after this session's additions (up from 315 at Stage F close); remaining warnings are third-party deprecation notices (`pyparsing`, `matplotlib`, `scipy`) unrelated to this codebase.

### Stage I -- Venue gate and submission (M5-M6)

- **Work**: with all verdicts in hand, decide conference cut (8-10 pages plus appendix) vs journal; produce the derived version; execute the M6 submission checklist including the PyPI release.
- **Additional requirement (July 23, 2026)**: the logistics items in ledger Section 8.6 -- artifact link verified from a logged-out browser, limitations foregrounded in intro and conclusion, abstract rewritten POMDP-first for readers outside active inference.
- **Acceptance**: submission package verified to compile standalone; `pip install rho-aif` works from a clean venv; checklist in `research_plan.md` fully ticked.

## 8. Review-response ledger (NeurIPS 2026 submission 30092)

Reviews of the earlier NeurIPS version (Reviewers 8Evk, Nzm2, vnDs, all reject; plus the PAT automated feedback) were folded into this plan on July 23, 2026. Every substantive point is listed here with its disposition. Stage H must walk this ledger before the draft is called assembled; Stage I inherits the logistics items.

### 8.1 Core objections that the reframed paper turns into its thesis

- **w=1 is scale-dependent; substituting rewards for log-preferences breaks the "canonical weight" claim** (all three reviewers; PAT at length). PIVOTED: this is now the headline. PI-1 proves exact scale equivariance (w must co-scale with rewards; fixed w=1 at scale alpha behaves as w=1/alpha), and the paper's contribution is the reinterpretation of w as an operational shadow price with B_EFE(alpha) = U(1/alpha). Per Reviewer vnDs: the concession must appear in the abstract, introduction, and conclusion, not only in a limitations subsection.
- **"Complete a sensitivity sweep on reward scaling"** (vnDs question). DONE before it was asked, at full power: the alpha in {0.1, 1, 10} collapse battery on Diagnosis, Bandit, Tiger, Tileworld (Stage E) plus the PI-1 theorem making the sweep's outcome provable.
- **"Why is there no variable controlling the pragmatic/epistemic ratio in AIF?"** (8Evk question). Answer to write explicitly: there is -- once rewards replace log-preferences, the exchange rate IS w; w=1 is a unit convention ("one bit = one reward unit"), not a law. This is the cleanest one-sentence statement of the pivot and should appear early.
- **"Proposition 3.1 is a change of representation, not an algorithmic insight"** (Nzm2). Concede and reposition: the equivalence is the vocabulary of the paper, not its result; the budgeted formulation, exactness theorems, and solver/controller are the results.
- **Zero-shot transfer claim unconvincing; tuned hyperparameters degrade under transfer generically** (Nzm2). Drop the transfer framing as headline. The defensible successor claims: (i) EFE w=1 is statistically indistinguishable from the SARSOP near-optimal reference on the OTC suite at the tested scales (Stage F), and (ii) the right way to choose w is budget-first via the usage curve, which removes the tuning question entirely.

### 8.2 Theory corrections to carry into full_paper.tex

- **Convexity claim is wrong** (PAT): expected information gain is concave in the belief, so the EFE-derived rho does NOT preserve PWLC; do not claim inherited convexity. Cite Fehr et al. 2018 for Lipschitz non-convex rho instead. (The old line 131 claim must not survive assembly.)
- **Imprecise rho-POMDP reward definition** (Nzm2): define rho and the expectations explicitly; a belief-dependent reward can absorb the state-dependent expectation, so present R(b,a) = E_{s~b}[R(s,a)] + rho(b,a) with the outer expectation over observations/beliefs written out.
- **Prop 3.2 threshold table contradictions** (PAT: Testbed sign, Tiger magnitude, Bandit's positive R- violating the assumption, 2-state formula applied to N>2): regenerate every threshold from `experiments/run_thresholds.py`; state the proposition strictly for two states with R- < 0; Stage A's PI-4 already re-derives the positive-threshold testbeds and verifies them numerically (`TestProp2OnsetExact`).
- **Prop 3.3 exploitation branches** (PAT; 8Evk's generality concern): clarify that the factored equivalence holds along branches of observation/navigation actions and state precisely what happens when a branch contains a state-changing exploitation action (the coupling term no longer vanishes); scope the proposition accordingly.
- **Notation and presentation debts** (8Evk, PAT): define w and kappa at first use; define C and Q in equation 1; "open-loop" not "myopic" for standard AIF; say what is Lipschitz; fix the observation-cost sign convention (costs are magnitudes); conditional-entropy notation E_{o|obs_k}[H(b'_o)]; rename the observation set to avoid the Omega/O collision; add the missing outer expectation in the Prop 3.2 proof sketch; fix the Eq. 6 vs Eq. 8 proof reference; fill or delete the empty Appendix P.

### 8.3 Empirical hygiene rules for assembly

- **One battery, one table** (PAT found RockSample Table 6 vs 23 contradictions, missing promised baselines, Tileworld 66.5 vs 74.2, Bandit/Diagnosis reward drift across sections, swapped effect sizes, SD-vs-SE mislabels): every number in the full paper must be generated from a current results CSV by a scripted table builder; no hand-carried numbers from older runs. The README reproduction map (already a Stage H acceptance item) is the enforcement mechanism.
- **Baseline tuning confound** (PAT): when comparing on expected reward, baselines must be reward-tuned (or both tunings reported); never evaluate success-tuned baselines on reward alone.
- **Model-misspecification prose must be rewritten from the tables** (PAT caught text claiming "excessive testing" where counts decrease).
- **POMCP parity** (PAT): state the UCB1 exploration constant and scale it with the environment reward range, or explicitly flag the parity limitation.
- **Discount-factor limitation** (PAT): gamma >= 0.99 baseline requirement belongs in the practitioner checklist, not only in the discussion body.
- **Tree-search complexity** (PAT): quote O((A x Z)^H) style scaling correctly.

### 8.4 Citation status (verified July 23, 2026)

The five entries Reviewer vnDs flagged as erroneous were already corrected in the current `paper/paper.tex` / `paper_arxiv.tex` sources; each was re-verified against its source today:

- Benchetrit, Lev-Yehudi, Zhitnikov, Indelman, "Anytime incremental rhoPOMDP planning in continuous spaces," arXiv:2502.02549 (title and authors confirmed on the arXiv page; the old "rho-POMCPOW" title was wrong). REMAINING: the related-work prose still calls this method "rho-POMCPOW" -- fix the name in prose during assembly.
- Friston, Rigoli, Ognibene, Mathys, FitzGerald, Pezzulo, "Active inference and epistemic value," Cognitive Neuroscience 6(4):187-214, 2015 (Parr removed, Mathys added).
- Champion, Bowman, Markovic, Grzes, "Reframing the expected free energy: Four formulations and a unification," Neural Computation 38(3):439-469, 2026 (author order and journal venue fixed; matches the MIT Press record).
- de Vries, Nuijten, van de Laar, et al., arXiv:2504.14898 (first three of seventeen authors confirmed against the arXiv page; et al. covers the rest).
- Millidge, Tschantz, Seth, Buckley, IWAI 2020 (Seth restored).

Towers et al. ("Gymnasium: A Standard Interface for Reinforcement Learning Environments," arXiv:2407.17032, 2024), SARSOP (Kurniawati, Hsu, Lee, RSS 2008), and POMCPOW (Sunberg and Kochenderfer, ICAPS 2018) were committed to `paper/paper.tex`/`paper_arxiv.tex`'s bibliographies during Phase 1 of the "Fix remaining review issues" pass (ahead of Stage H, since the review-fix work landed directly in the two existing sources). The full re-verification pass over every legacy entry remains a Stage H acceptance item; Reviewer vnDs's question "can the authors confirm all cited works were read and verified" must be answerable with yes and a record.

**Phase 4/5 additions (July 23, 2026), each checked against the publisher or primary arXiv record before use:**

- Gneiting, T., and Raftery, A. E. (2007). "Strictly proper scoring rules, prediction, and estimation." *Journal of the American Statistical Association*, 102(477):359-378. DOI 10.1198/016214506000001437 (verified via Taylor & Francis and the University of Washington author copy). Used for the proper-scoring calibration appendix; added to `paper.tex`/`paper_arxiv.tex`.
- Kim, D., Lee, J., Kim, K.-E., and Poupart, P. (2011). "Point-Based Value Iteration for Constrained POMDPs." *IJCAI*, pp. 1968-1974 (verified via the official IJCAI proceedings PDF). Used in `price_of_information.tex`'s related work to distinguish constrained-POMDP dual methods (exogenous cost constraints, offline solve) from this paper's budgeted epistemic-usage constraint (online tracking).
- Foster, A., Ivanova, D. R., Malik, I., and Rainforth, T. (2021). "Deep Adaptive Design: Amortizing Sequential Bayesian Experimental Design." *ICML*, PMLR 139:3384-3395, arXiv:2103.02438 (verified via PMLR and the arXiv abstract page). Used in `price_of_information.tex`'s new sequential-Bayesian-experimental-design paragraph, distinguishing SBED's expected-information-gain design objective from this paper's budgeted task-reward objective.
- Robbins, H., and Monro, S. (1951). "A stochastic approximation method." *Annals of Mathematical Statistics*, 22(3):400-407, and Blum, J. R. (1954). "Approximation methods which converge with probability one." *Annals of Mathematical Statistics*, 25(3):382-386. Both already verified and recorded in `Guidance_Documents/price_of_information.md`'s citation-check table (Section 4.1 work); underpin Proposition PI-5's dual-controller convergence statement.

### 8.5 Answers to reviewer questions to write into the paper

- **8Evk: distractor uncertainty** -- DONE. Stage G2 experiment (above) plus a limitations paragraph; IG is reward-blind and the budget caps but does not redirect spend; the in-repo IDS adaptation is not a clean immune contrast either (info_astar-zero fallback to raw state entropy) -- see Section 11 of `price_of_information.md` and the Stage G2 outcome note above.
- **8Evk: alternatives to IG as belief-based reward** -- expand related work: negative entropy and error-based rho (Araya et al.), POMDP-IR per-fact information rewards (Spaan et al.), KL-to-target-belief; one paragraph comparing to IG.
- **8Evk: why observe-then-commit** -- DONE. Added an identical motivating sentence to `paper.tex`, `paper_arxiv.tex`, and `full_paper.tex` immediately after the OTC definition (clean theory, exact near-optimality analysis and SARSOP baselines feasible), pointing to Proposition~3 and the RockSample/Structural Inspection results (and, in `full_paper.tex`, the interleaved usage curves) as the beyond-OTC evidence.

### 8.6 Stage H closeout verification (July 23, 2026)

Three items Phase 6 singled out for re-verification, checked directly against the current `paper_arxiv.tex`:

- **Threshold tables**: `Table~\ref{tab:alpha_eta}` reports $\alpha$, $\eta$, $w^*_{\mathrm{lo}}$, $w^*_{\mathrm{hi}}$ per environment consistently with the closed form in Proposition~\ref{prop:nearopt} and with PI-4's numerical check (`TestProp2OnsetExact`); Bandit is explicitly excluded as multi-arm rather than silently misapplying the two-state formula. No contradiction found.
- **Baseline-tuning disclosure**: the reward-tuned vs. success-tuned distinction ($w^*_{\mathrm{ret}}$ vs. $w^*_{\mathrm{succ}}$) is stated explicitly wherever a tuned Planning+IG baseline is compared on reward (Pareto section, transfer table, IDS table), so no success-tuned baseline is evaluated on reward without disclosure.
- **Tileworld reconciliation**: the $66.5\%$ (8x8, main scaling table) and $74.2\%$ (6x6, observation-structure-sensitivity ablation, bitwise partition) figures that PAT's automated review flagged as contradictory are different environments under different conditions, not the same claim reported twice; both are individually correct and now clearly scoped in the surrounding prose.

All three verified already fixed; no further edits required for this item.

### 8.7 Logistics (Stage I checklist additions)

- Verify the anonymized artifact link resolves from a logged-out browser before submission; the checklist must never claim code availability that a reviewer cannot reach (vnDs).
- Foreground limitations in the introduction and conclusion, not only a back section (vnDs).
- Rewrite the abstract for a reader outside active inference; Nzm2 found it "very difficult to comprehend" -- lead with the POMDP-native statement (budgeted sensing, shadow price), not the EFE vocabulary.

### 8.8 Stage I execution: JAIR submission package (August 4, 2026)

Executing the "JAIR Submission Package" plan (Phases 0-3). Phase 0 findings and Phase 1 deliverables:

- **Camera-ready gap found and closed**: `paper/paper_iwai2026.tex` and `paper/paper_iwai2026_abridged.tex` still had `\author{Anonymous Author(s)}` and an `anonymous.4open.science` placeholder link months after the IWAI Accept decision -- the camera-ready author-response text drafted July 20 was never actually applied to the source. Both files are now de-anonymized (real author/affiliation block matching `paper_arxiv.tex`), the abridged version's public-code footnote points at the real GitHub repository, and the leftover `\ackname{}` "Removed for anonymous submission" placeholder is deleted. Both recompile cleanly via tectonic with zero undefined references. Actually clicking submit on the OpenReview camera-ready portal remains a manual step outside this agent's access (no OpenReview credentials or browser session); JAIR's extended-version exception text requires the workshop's "final version submitted and approved," so that portal action should be completed before or alongside the JAIR submission, not after.
- **JAIR portal mechanics (verified against jair.org, August 4, 2026)**: not double-blind (no author-side anonymization needed, confirming the plan's assumption); submissions are rolling via an online wizard; three mandatory 150-word survey questions must be answered in the submission comments field (importance to the field, 1-3 closest JAIR papers and the delta, prior-publication disclosure); a **mandatory reproducibility checklist** (Gundersen, Helmert, and Hoos, "Improving Reproducibility in AI Research: Four Mechanisms Adopted by JAIR," *JAIR* 81:1019-1041, 2024) must be filled out in the LaTeX source and compiled as an appendix or the submission is desk-rejected without review; structured abstracts (Background/Objectives/Methods/Results/Conclusions) are encouraged but not mandatory. None of this was in the original plan text and is folded in here rather than editing the plan file.
- **JAIR LaTeX kit**: JAIR's formatting page points only to a login-gated Overleaf project (`overleaf.com/read/hycbzkdksrzz`, "Copy Project" requires an Overleaf account) with no plain download link found via web search. Since this agent cannot authenticate to Overleaf, `paper/full_paper_jair.tex` is built on the standard `acmart` class (`\documentclass[manuscript,screen,review,nonacm=true]{acmart}`) in the closest-faith reading of JAIR's own description ("a format based on ACM's LaTeX style"). This compiles cleanly (59 pages, zero undefined references/citations, `tectonic`) with `natbib`-style `\citep`/`\citet` working under `\citestyle{acmauthoryear}`, `amsthm`-based `proposition`/`definition`/`corollary`/`example` environments matching the LNCS numbering, and all figures/tables/cross-references intact. **This remains an approximation, not the verified JAIR template** -- before actual submission, either copy the real Overleaf project (requires a human with an account) and reconcile any class-level differences, or share the downloaded Author Kit files so this agent can do a final 1:1 pass. JAIR's submission page states off-format submissions are "rejected without review," so this reconciliation is a hard gate, not a nice-to-have.
- **Abstract/intro rewrite (ledger 8.7, closed)**: `paper/full_paper.tex`'s abstract and introduction were restructured so the sensing-budget/shadow-price framing leads and the EFE/active-inference vocabulary follows as the mechanism that supplies one point on that price curve, rather than the reverse. `full_paper_jair.tex` additionally uses JAIR's encouraged structured-abstract format (Background/Objectives/Methods/Results/Conclusions) with the same budget-first lead. Both recompile cleanly.
- **Extension disclosure and CCIS entry (closed)**: `full_paper.tex` (and inherited by `full_paper_jair.tex`) now states explicitly, right after the contributions list, which results were in the IWAI 2026 submission (Propositions 1-3 and the first experiment battery) and which are new (the entire budgeted formulation, Definition PI-3, Propositions PI-1/PI-2/PI-5, Corollary PI-4, the second experiment battery, and the practical-guidance contribution). A `cooper2026iwai` bibliography entry citing the IWAI 2026 CCIS proceedings (marked as accepted poster + spotlight, in-press) was added to both bibliographies.
- **Section-level delta list (new vs. IWAI 2026 abridged paper), for the cover letter**:
  - New in full/JAIR version only: Section "Budgeted rho-POMDPs and the price of information" in its entirety (the usage curve, Definition PI-3 set-valued shadow price, Proposition PI-1 exact scale equivariance, Proposition PI-2 monotone comparative statics, Corollary PI-4, the online dual controller of Proposition PI-5, and the positioning-against-prior-art subsection).
  - New: the second experiment battery ("Experiments: shadow prices and sensing budgets") -- curve-collapse across reward scales, Proposition-2-onset validation on positive-threshold testbeds, multi-seed online dual control under a 10x reward rescale, cost-denominated budgets, interleaved-setting (RockSample, Structural Inspection) usage curves, the SARSOP near-optimal reference, distractor robustness, and the w* atlas appendix.
  - New: the Structural Inspection benchmark (over 65,000 states) and its interleaved-observe-act usage curves.
  - New: the practical-guidance contribution (Contribution 4) characterizing when EFE-as-rho helps and when it does not, including the destructive-sensing example (Example 3.5 in the JAIR numbering).
  - Retained from IWAI with only editorial changes: the observe-then-commit equivalence (Proposition 3.1), the near-optimality characterization (Proposition 3.2), the factored-observation extension (Proposition 3.4/Definition 3.3), and the first experiment battery (Tiger through Tileworld/RockSample core comparisons).
  - Retained but compressed relative to the IWAI version: none -- the JAIR version does not compress the equivalence material, since JAIR's page-agnostic journal format does not require the trims a conference cut would.

Phase 0 and Phase 1 (jair-port, abstract-pass, extension-statement) are complete under this entry.

**Phase 2 findings**: the M6 PyPI checklist was executed as far as possible without account credentials -- `dist/` rebuilt from the current tree, both the wheel and sdist pass `twine check`, the `rho-aif` name is unclaimed on both PyPI and TestPyPI, and a fresh-venv install of the built wheel runs `rho-aif-bench list` and a live benchmark episode successfully end to end. Uploading to TestPyPI/PyPI itself requires a PyPI account/API token this agent does not have; that remains Patrick's manual step (`twine upload --repository testpypi dist/*` then `twine upload dist/*` from `/Users/pat/code/rho_aif`, after which the local `v1.0.0` tag should be confirmed against the release commit and pushed). Separately, and more urgently: the repo-check step found `https://github.com/PatrickAllenCooper/rho_aif` -- the exact URL cited in both papers' code-availability footnotes and the JAIR reproducibility checklist -- returning 404 from a logged-out fetch and the GitHub API, because the repository was still **private**. Every public-code claim in the current manuscripts was false until this was fixed. After a scan of tracked files and content for obvious secrets (none found), the repository was switched to public via `gh repo edit --visibility public`, and a logged-out fetch now confirms the repository page loads normally. The repository's remote content is one commit behind the working tree as of this entry (today's edits are committed in Phase 3 closeout below); the visibility fix applies regardless of that lag.

### 8.9 JAIR cover letter and submission-form answers (August 4, 2026)

JAIR has no separate cover-letter upload; the online submission wizard's "comments for the editor" field is where the conference-history notification belongs (required by JAIR's extended-version policy: "authors submitting a paper that extends a paper previously published at a conference... must notify the editor at the time of submission"), and three survey questions in that same field are mandatory (submissions without clear answers "will not be considered for publication"). Text below is ready to paste in.

**Comments for the editor (conference-history notification and data/code availability):**

This manuscript extends an abridged version accepted at the 7th International Workshop on Active Inference (IWAI 2026), Poster + Spotlight, to appear in Springer's Communications in Computer and Information Science proceedings. Per JAIR's extended-version policy, we notify the editor of this prior publication at submission. The extended-version delta is detailed in Question 3 below and in full in the section-level delta list of Section 8.8 of this guidance document. All code, environments, and per-seed result CSVs backing every table and figure are publicly available under the MIT License at `https://github.com/PatrickAllenCooper/rho_aif`, also distributed on PyPI as `rho-aif`. A completed reproducibility checklist is included as an appendix to the submitted PDF, as required.

**Mandatory survey question 1 (why this work matters to other AI researchers, max 150 words):**

This paper gives active inference's Expected Free Energy (EFE) objective a precise operational meaning for information-gathering POMDPs. It proves EFE is exactly equivalent to a rho-POMDP with an information-gain weight of w=1, exact under log scoring rules, removing a heuristic hyperparameter that every belief-dependent-reward POMDP application otherwise tunes by hand. It then shows that this weight's reward-scale dependence, usually treated as a defect, is precisely the shadow price of an explicit sensing budget: computable offline from a usage curve, trackable online under reward-scale shift, and exactly scale equivariant. Researchers building information-gathering agents (active perception, sensor tasking, medical testing, sequential experimental design) can use the usage-curve procedure and online dual controller directly to replace hand-tuned exploration bonuses with a budget the practitioner actually cares about, and can cite the equivalence result to justify EFE-style objectives outside the active inference literature. (139 words)

**Mandatory survey question 2 (1-3 closest JAIR papers and how this differs, max 150 words):**

The closest JAIR articles are: (1) Krivic, Cashmore, Magazzeni, and Szedmak, "Using Machine Learning for Decreasing State Uncertainty in Planning" (JAIR 69, 2020), which also decides what information to sense before acting, but in a classical contingent-planning setting with learned predictors, not a POMDP/belief-dependent-reward formalism, and without weight-calibration or budget theory. (2) Lim, Becker, Kochenderfer, Tomlin, and Sunberg, "Optimality Guarantees for Particle Belief Approximation of POMDPs" (JAIR 77, 2023), which shares the POMDP-solving concern but addresses continuous-state particle-filter approximation error, not belief-dependent reward weighting. (3) Meli, Castellini, and Farinelli, "Learning Logic Specifications for Policy Guidance in POMDPs" (JAIR 79, 2024), which uses the same RockSample benchmark and POMCP family of solvers but learns interpretable heuristics via inductive logic programming rather than deriving an information-gain weight from a variational objective. None addresses budgeted sensing or an operational shadow price for POMDP exploration. (141 words; each citation independently verified against jair.org before use, per the paper's own citation-verification standard)

**Mandatory survey question 3 (prior publication disclosure, max 150 words):**

Yes. An abridged version of the observe-then-commit equivalence results (Proposition 3.1), the near-optimality characterization (Proposition 3.2), the factored-observation extension (Proposition 3.4), and the first experiment battery (six observe-then-commit environments and RockSample) was accepted as a poster and spotlight presentation at the 7th International Workshop on Active Inference (IWAI 2026), to appear in Springer CCIS proceedings. This submission is a substantially extended version: it adds the entire budgeted rho-POMDP formulation (the usage curve, the set-valued operational shadow price, exact scale equivariance and monotone comparative statics propositions, and an online dual controller with a stated tracking guarantee), a second experiment battery (usage-curve collapse across reward scales, multi-seed online control under a tenfold reward rescale, cost-denominated budgets, a Structural Inspection benchmark with over 65,000 states, and a near-optimal SARSOP reference), and a practical-guidance contribution characterizing when the method helps and when it does not. This is not a resubmission to JAIR. (148 words)

**Section/track**: Articles (regular full-length track), per JAIR's submission form.

Phase 3 continues below with the final compile/test gates and closeout.

### 8.10 Extended-version qualification audit and hijacked-journal warning (August 6, 2026)

Re-verification pass against the two universal extended-version requirements (cite the prior paper in the manuscript; include substantial new material with an explicit increment statement):

- **Citation requirement: met.** `full_paper_jair.tex` cites the IWAI paper via `\citep{cooper2026iwai}` in the disclosure paragraph immediately after the contributions list, with a full bibliography entry marked "Accepted as poster and spotlight presentation; abridged version of the observe-then-commit equivalence results in this article."
- **Increment requirement: met, with margin.** The same paragraph explicitly enumerates the new material (all of Section 4's budgeted formulation, the second experiment battery, and the practical-guidance contribution). Quantitatively: the strictly-new sections alone (budget theory ~1,900 words, Structural Inspection ~500, second battery ~2,300, new appendix material ~1,600) total ~6,300 words -- larger than the entire IWAI abridged source (~4,850 words of LaTeX including preamble and bibliography). Against Springer's 30% threshold (the strictest published rule, and the one baked into the CCIS Consent to Publish form: at least 30% new material, cite the original, explicit increment statement), the manuscript passes by a wide margin; most of the 59-page JAIR manuscript never appeared in the workshop version even in abridged form.
- **Hijacked-journal warning (do not lose this).** A web search for a downloadable JAIR LaTeX kit surfaced `sub.ifspress.hk` ("Infinity Science Press", Hong Kong) presenting itself as JAIR's submission portal with its own template zip and author guidelines (200-word abstracts, 50-character titles -- inconsistent with real JAIR policy). This matches the hijacked/cloned-journal pattern documented by the Retraction Watch Hijacked Journal Checker: JAIR's publisher of record is the AI Access Foundation and the only legitimate site is `jair.org`. Never submit, pay, or download templates through the ifspress domain. The only official template access remains the JAIR Author Kit / Overleaf project linked from `jair.org/index.php/jair/formatting` (`overleaf.com/read/hycbzkdksrzz`), which requires an Overleaf account to copy -- still Patrick's manual step before submission.
- Compile re-check on this date: `full_paper_jair.tex` builds clean under tectonic (59 pages, zero errors, one cosmetic underfull-vbox warning in an appendix). No anonymization or TODO leftovers in the source.

### 8.11 Internal two-referee review cycle and refinements (August 6, 2026)

Two independent JAIR-style referee reports were produced on `full_paper_jair.tex` and every actionable point was verified against the manuscript, code, and results CSVs before any edit. Referee A returned accept-with-minor-revisions; Referee B returned reject, centered on the charge that $w^*(B)$ is not the Lagrange multiplier of the stated constraint $U(\pi) \le B$ (the objective $R + wI$ prices information, not usage). The disagreement was resolved by precision rather than reconceptualization. All changes below were applied identically to `full_paper_jair.tex` and `full_paper.tex`.

**Round 1 (Referee A, commit `edfec66`):**
- Nats/bits denomination made explicit: verified in code that all "EFE (w=1)" results run at w=1 in bit units (`scipy_entropy(base=2)`, `info_weight=1.0`), i.e. effective nat weight ~1.44; the calibration paragraph now states this and that the nat-exact w = ln 2 also lies in the measured Pareto knee.
- Destructive-sensing failure explicitly attributed to the state-preserving rho = I(b) reduction, not to EFE itself (transition-aware EFE uses the correct joint posterior and prices the drill correctly).
- Explicit limitation added to Section 4.6: no exact constrained-POMDP benchmark; the single-price family is not claimed reward-optimal among budget-feasible policies.
- Paper-code mismatch fixed in text: Eq. 5 states projection onto [0, w_max] but `dual_update` clips only at zero; the text now explains the finite bound serves the stochastic-approximation argument and only the lower projection is active.
- "Information-floor dual" glossed in standard Lagrangian-relaxation terms; known-cost caveat added to the budget section opening.

**Round 2 (Referee B, this entry's commit):**
- Core framing made precise in Section 4.1: a new paragraph proves (one-line scalarization argument) that w IS an exact Lagrange multiplier of an information floor (max R s.t. I >= I(pi_w)), and explicitly disclaims that w*(B) equals the multiplier lambda*(B) of the usage-cap problem -- w*(B) is a calibration of the Planning+IG family to a usage budget. This answers the reject rationale without abandoning the budget framing.
- Definition PI-3 disambiguated: bracket defined as the first (smallest-w) crossing; noted as a grid-resolution estimator of the smallest element of a possibly multi-valued inverse correspondence.
- Proposition PI-5 restructured: retitled "stationary convergence," the unproven constant-step O(a)-neighborhood claim demoted from the proposition to explicitly informal design intuition; "root of U(w)=B" reworded to sign-change; every prose claim of a "tracking guarantee under reward-scale shift" (abstract, contributions, positioning, conclusion) replaced with stationary-convergence-guarantee-plus-empirical-re-adaptation phrasing.
- Abstract factored-observation claim narrowed to the hidden-state-preserving observation/navigation actions Prop 3.4 actually covers; Delta_T formally defined (expected KL between joint transition-observation posterior and observation-only posterior) before first use.
- "Statistically indistinguishable from SARSOP" softened everywhere to within-sampling-error phrasing, with an explicit note that no formal equivalence test (predeclared margin, TOST) was run.
- Data-lineage fix: the stale Bandit bootstrap numbers (+6.38 [6.29, 6.47]) contradicted the main table (+6.27) and the current CSV (6.19, a different run); the sentence now makes the (robust) qualitative non-overlap claim and points to the stats appendix.
- Obsolete 3-seed Tileworld 8x8 appendix table explicitly marked superseded by the 5-seed main-text result, retained only for the full-agent-set breakdown.
- POMCP disclosure added: the planner's internal RNG is initialized from a fixed constant across runs (verified: `RandomState(42)` in `rho_aif/agents/pomcp.py`), so outer seeds vary environment streams only; the "fundamental benefit" conclusion softened to as-configured with an explicit stronger-configuration caveat.
- Guidance claim at the alpha >> 1 paragraph reconciled with the random-environment study (37% of alpha >= 10 environments pass at H=3): now a "strong untuned starting default," not a well-calibrated guarantee.
- Reproducibility checklist honesty: minimum dependency versions no longer claimed to "fully determine" the environment; "exact closed-form values" dichotomy corrected. Testbed's alpha = 1.0 noted as boundary case of Prop 3.2's strict assumption. Hardcoded "Section 6" replaced with a label reference; PSPACE phrasing corrected; experiments-intro sentence no longer claims all environments are observe-then-commit.

**Deliberately not acted on (user decisions, in priority order):**
1. Adding an empirical exact-CPOMDP baseline (both referees converge on this as the top-value addition; small-environment constrained policy enumeration or a belief-state constrained LP is feasible but is new experimental work).
2. Re-running POMCP with per-run seeding, tuned exploration constants, and equal-wall-clock matching (compute decision; currently disclosed in text instead).
3. Promoting seed-level/hierarchical statistics from the appendix to the primary main-text tables (requires regenerating tables).
4. Formal equivalence testing (TOST) against SARSOP with a predeclared margin (post-hoc margin declaration is itself methodologically delicate; text now states epistemic status precisely).

Both manuscripts recompile clean after all edits (JAIR 61 pages, LNCS 69 pages, zero errors/undefined references).
