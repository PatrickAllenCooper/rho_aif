# Full-Length Paper Plan: From Workshop Iteration to Integrated Publication

**Status**: Planning document created; work not yet started
**Date**: July 23, 2026
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

Ordered; each milestone updates this document and commits.

1. **M1 -- Theory**: budgeted rho-POMDP proposition drafted with proof or proof sketch; Prop 2 corollary derivation written (Section 3.1).
2. **M2 -- Experiment extensions**: interleaved usage curves, multi-seed dual control, cost budgets, collapse breadth (Section 3.2, all but baselines).
3. **M3 -- Baseline debt**: SARSOP reference runs; POMCPOW decision made and documented (Section 3.2 last item).
4. **M4 -- Assembly**: `paper/full_paper.tex` drafted per Section 4 outline; w* atlas appendix built (Section 3.3); related work merged (Section 3.4); full citation verification pass.
5. **M5 -- Venue decision gate**: with results in hand, choose conference cut vs journal submission; produce the derived version.
6. **M6 -- Submission checklist**: PyPI release of `rho-aif` (TestPyPI verify, upload, tag -- the standing checklist in `research_plan.md` under "Deferred until next venue submission"), public code link and README install instructions pointed at PyPI, reproduction command table updated for every new figure and table, final compile and package.

## 7. Document evolution

This plan is a Guidance_Documents artifact under the project's virtuous-cycle rule: every change made toward the full paper edits this document to reflect what was done and what it changed about the plan. Verdicts (HOLD / PARTIAL / FAIL) for new experiments are recorded here and mirrored in `research_plan.md`.
