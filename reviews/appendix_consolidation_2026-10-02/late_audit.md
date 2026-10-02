# Late empirical appendix audit

Baseline: `c5125ab`. Current version archived before editing under `paper/legacy/2026-10-02_pre_appendix_consolidation/` (archive commit `7855d9c`). This review proposes source changes only. It edits no manuscript, experiment, dataset, figure or table producer.

## Finding

The late appendices often preserve long versions of material relocated into the main body in earlier passes. They repeatedly explain the same environment, selection procedure, statistical caveat and conclusion, then narrate numbers already present in retained tables. The strongest safe reduction is to let the main body define each study once and make these appendices a record of residual protocols, results and limitations. Definitions of general concepts such as constrained planning, randomization and standard errors do not need to recur beside every table.

The 18 guarded replacements in `late_proposals.json` reduce approximately 14,992 whitespace-separated source words to 5,427, a 64% reduction in the selected blocks. Counts include unchanged floats, LaTeX and accessibility descriptions and are not a rendered-page estimate. All four figures and all five inline tables in these blocks remain intact, as does the external three-panel budget-frontier table. Every original label in these blocks remains. No font-size or layout compression is proposed. The retrospective real-sensor protocol is deliberately unchanged because its learned model, immutable grids, row splitting and conditional selection-aware uncertainty are important and already compact enough for the paper's strongest new evidence.

## What stays load-bearing

- All six nonstandard RockSample choices, including finite-range sensor accuracy, any-cell exit and fixed hidden rock quality. Its sensor formula was independently checked in `rho_aif/environments/rocksample.py`.
- Grid/episode protocols, shared-seed qualification, nonmonotone curves and distinction between grid brackets and uncertainty. Cost/count coincidence remains a measured negative result.
- Controller recovery censoring, primary restricted-time estimand through the main pointer, conditional means as descriptive only, normal versus Student intervals, and the seed on which resetting worsens final error.
- SARSOP's retrospective five-seed margins, prospective extra seeds, unpaired/paired/episode-matched distinctions, all numerical TOST support, and Tiger's unbracketed fallback.
- Feasible-envelope construction and approximate/noisy/finite-grid scope. Negative estimated gaps remain explicit. No certified optimum, strong duality or population feasibility claim is introduced.
- Frontier post-inspection amendments, calibration-only policy selection, held-out-fitted reference support, frozen fresh-stream replay, nonblind Diagnosis pair, unstable Diagnosis shortfall identities, Tiger rare-event uncertainty and target-versus-cap distinctions.
- The full frontier table, including the cross-stream comparison. Its meaning is not inferred from a cap-gap sign. The post hoc usage-matched sensitivity remains and still removes the held-out Tiger mean gap while weakening the Bandit result.
- The distractor repair's reward-class marginal and the IDS fallback failure, including nonsignificant lower-weight reward improvements and nonsignificant success difference.
- Posterior-vote's Bandit tie and Testbed superiority, Epistemic-only's immediate stopping, small pooled effect sizes and seed-level inference cautions.
- All Tileworld partition outcomes, lack of reward/success separation, sharply degraded performance under overlapping partitions, separate battery protocols and the no-scan depth-limited competitor at the largest grid.
- RockSample's phantom exit cost and shared heuristic, significant deficits to the standalone rollout, three-weight rather than dense tuning, null depth-three check and failure of deeper POMCP to fix the larger instance.
- Inspection's synthetic/known-model scope, costly higher-accuracy policy, reward nonsignificance and heuristic two-state reduction with unevaluated upper threshold.
- Exact MCTS implementation distinctions, unequal cost per simulation, adverse reward trade-off on Tileworld, inferior reward/success versus Exact-EFE on Tiger and Diagnosis, ablation nulls, retrospective exploration-selection scope and coupled attribution.

The removed text predominantly repeats these conclusions and their generic interpretation. Residual numerical results remain close to their primary source/table. The only whole explanatory unit removed is the speculative paragraph extrapolating two-state asymmetry to medical/security domains. Its qualified mathematical reading and all empirical evidence remain.

## Guard validation

Every `old` block matches exactly once in each baseline master, so venue-specific fields are unnecessary. Every block begins after the late-appendix section heading, and the 18 spans do not overlap. Every old label appears in its replacement. No proof environment is changed. No literal escaped newline or prose semicolon occurs in the replacement text. A preliminary broad match on the duplicate Structural Inspection heading was caught and corrected before delivery, and a late-section scope assertion now guards against that mistake.

The reconstruction helper is `build_late_proposals.py`. It reads the frozen Git baseline and writes only the proposal JSON. Do not run it as an application script: the parent agent applies the guarded replacements and performs the independent post-application review and builds.

## Further consolidation opportunity

The repeated four-row Tileworld table could be removed if its seed-level uncertainty were merged into the complete early Tileworld table and every `tab:tileworld` reference updated. I have retained it because the early table has pooled uncertainty and may be changed by another reviewer. The short curve-collapse breadth table could likewise become a sentence after updating main-text references. Neither removal is required to obtain this pass's substantial prose reduction.
