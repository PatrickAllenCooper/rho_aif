# Independent final review of the concision revision

Date: 2026-09-28

**Decision: ACCEPT. No remaining source-level revision conditions.**

This is an independent assessment of the shortening and restructuring, not a prediction of JAIR's decision. I compared both assembled masters with the dated legacy sources, read the complete revised main argument, reviewed the relocated theory/evidence/interpretation material, and checked the safeguards in `critical_preservation_checklist.md`. The root agent is separately responsible for compilation and rendered-layout checks. I did not modify the masters.

## Exact sources reviewed

- `paper/full_paper_jair.tex`, SHA-256 `68564de762b5620dbb4fabb9d49a7036ea5db1eed6dc5b817990d98b2d7093f9`
- `paper/full_paper.tex`, SHA-256 `2cd4eebdc2a47d9ee46046ce2681b1bc293af9b345473f8cc5ca7a9a35eaecfe`
- Baselines: corresponding sources in `paper/legacy/2026-09-28_pre_concision/`.

## Assessment

The revised main text now carries a coherent paper rather than the entire audit history. It gives a reader enough detail to understand and critically assess the design requirement, model, method, theorem scope, principal evidence, counterexamples, and practical recommendation without treating the appendices as a substitute for the main argument. The later restoration of the cost, interleaved, staircase, distractor, RockSample, and Inspection evidence was worthwhile. It preserves the empirical breadth promised in the framing while leaving proofs, complete comparison tables, and detailed solver controls accessible in the appendices.

The central scientific distinctions survived. An expected-usage target is not a usage cap, the information weight is not the cap's Lagrange multiplier, and the selected endpoint mixture need not maximize reward even within the sampled family. Population threshold, level set, grid bracket, and randomized policy remain distinct. The closed-enclosure and no-missed-crossing conditions are retained. The nonmonotonicity of usage and limitations of transferring exact-optimizer comparative statics to replanning remain explicit.

The EFE reduction retains its sign, reward convention, exact log-score case, normalizer limitation, information units, and state-preserving structural hypotheses. Its main-text destructive-sensing example and diagram make a consequential failure mode visible. Scale equivariance still distinguishes observation count from sensing cost, measured floating-point identity from a mathematical guarantee, and calibration from directly tuned weights. PI-5 retains all four conditions, its projected decaying schedule, and the distinction between weight convergence, pointwise usage, and running-average usage at a jump. The shift experiment is correctly presented as empirical re-adaptation outside that stationary theorem.

The main empirical qualifications are substantial rather than hidden. Targets are calibration-derived under a stated rule. The post-inspection additions are identified. The feasible reference is the at-most-budget LP envelope over sampled policies rather than equal-usage interpolation. Its support and mixture weights are fitted on the same held-out means used by nominal pointwise plug-in intervals, with omitted selection, mixture-weight, feasibility, and multiplicity uncertainty stated explicitly. The Tiger rare-event caveat remains next to the comparison. Negative cases for the default weight, Navigation, RockSample, model overconfidence, and synthetic Inspection are retained. The POMCP narrative distinguishes simulation budgets, retrospective tuning, and a jointly varied search configuration from an isolated causal claim about information gain.

I found no remaining scientific strengthening caused by the shortening. The shorter connecting prose is clearer than the baseline's repeated definitions and historical correction narratives. Some formal statements remain lengthy because their conditions matter, which is appropriate for this revision's clarity-and-rigor objective.

## Verified evidence and navigation

- All original source labels are retained in each master. Including the imported table files, there are no duplicate labels or unresolved `ref`/`eqref` targets.
- Each master retains every citation key it originally used. The JAIR source still cites 69 distinct keys. The editorial rewrite itself retains all 58 keys used by the original Introduction, Related Work, and Discussion. This is a retention audit, not a new external verification of bibliographic records.
- All six propositions, two definitions, one corollary, one example, and one remark remain in each master. Proofs and supplementary scope explanations have explicit destinations.
- The normalized main scientific bodies match between masters. Their only remaining main-text prose difference is the intentional JAIR reproducibility-checklist pointer, alongside class-specific figure-description handling.
- Independently checked all **84 numeric cells across the 12 rows** of the new compact frontier table against `results_budget_frontier.csv` and `results_budget_frontier_heldout_reference.csv`. Every cell agrees at the printed precision.
- Recomputed the headline counts from those archives: 12 mixture rows, 11 distinct budgets, 8 distinct fitted comparisons with a negative 95% interval upper endpoint, and maximum absolute held-out usage error 0.123 observations, consistent with the stated bound of 0.13.
- Recomputed the controller comparison from `results_price_dual_multiseed_metrics.csv`: restricted means 157.3 and 51.2, paired mean difference 106.1, Student-t 95% interval [96.7701, 115.4299], and 9 versus 10 recoveries. These reproduce the rounded main-text values without running new episodes.
- The interleaved-price CSV confirms four evaluated budgets per instance, with some repeated nearest grid weights or brackets. The final source correctly reports four budgets rather than asserting four distinct steps.

## Corrections verified closed

The audit found one newly introduced scientific wording error in the short abstract: it said the EFE objective itself equalled reward plus information gain. The final source now says **minimizing** the specified EFE objective is equivalent to **maximizing** reward plus information gain. The sign and optimization direction are preserved.

The final source also incorporates the requested local repairs: four budgets rather than four staircase steps; sample-grid scope for empirical lower usage limits; usage SE distinguished from price uncertainty; separately evaluated rather than independently sampled scale curves; accurate relocated calibration/threshold pointers; a current-order budget-section roadmap; explicit reward in the one-step objective; and parameter-dependent wording for the two-state interval. I re-read the actual assembled passages after reassembly rather than relying only on the editors' summaries.

No new experiment or additional source revision is required by this review.
