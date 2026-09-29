# Final scientific review of the concise manuscript

**Decision: ACCEPT. No required scientific or cross-reference corrections remain from this review.**

Reviewed on 2026-09-28 against the frozen `paper/legacy/2026-09-28_pre_concision/` version. This review emphasizes the empirical and editorial changes made by the other editors. I prepared the theory fragments, so their preservation was checked mechanically and their content was separately reviewed by the concision critic rather than represented here as an independent review of my own editing.

Reviewed JAIR source SHA-256: `68564de762b5620dbb4fabb9d49a7036ea5db1eed6dc5b817990d98b2d7093f9`.

Reviewed LNCS source SHA-256: `2cd4eebdc2a47d9ee46046ce2681b1bc293af9b345473f8cc5ca7a9a35eaecfe`.

## Scientific assessment

The shortened main text preserves the paper's inferential boundaries. Expected-usage calibration remains distinct from constrained reward maximization. Calibration-derived targets are not presented as independently supplied application requirements. The endpoint mixture is not called optimal among all mixtures or all feasible policies. Selected feasibility and observed held-out usage remain distinct from population feasibility. The finite sampled constrained reference remains approximate, with its fitted same-stream intervals explicitly qualified as nominal pointwise plug-in summaries.

The Tiger rare-event caveat remains in the abstract and next to the paired frontier comparisons. The eight-of-eleven claim is therefore not presented as an unconditional population superiority or inferiority result. The additional within-family mixtures are disclosed as a post-inspection amendment. The POMCP constant selection remains retrospective for the narrow Tiger finding, with no unsupported attribution of solver differences to directed observation selection alone. The n=5 TOST retains its retrospective margin choice, the additional fifteen seeds retain their prospective status, and the paired sensitivity analysis remains visible.

Adverse findings remain accessible in the main text: the two environments where weight one does not maximize sampled reward, higher success at lower reward, Tileworld's horizon dependence, the large RockSample failure and better heuristic, Navigation's null comparison, sensor-model mismatch, reward-irrelevant sensing, and the synthetic known-model scope of Structural Inspection. Moving detailed analyses to appendices has not hidden those findings.

The abstract now correctly says that minimizing EFE is equivalent to maximizing reward plus information gain. The main explanation preserves the reward convention, omitted normalizer, log-score case, bit/nat conversion, receding-horizon qualification, and distinction between mathematical equivariance and bit-exact empirical agreement.

## Numerical and artifact checks

1. Independently parsed all 12 rows of the new compact frontier table and compared its budget, mixture usage, usage SE, mixture reward, reward SE, paired gap, and gap SE with `results_budget_frontier.csv` and `results_budget_frontier_heldout_reference.csv`. **All 84 printed numeric components match at the displayed precision.** No result was recomputed or rounded differently to create the new table.
2. Recomputed the frontier summaries from those CSVs. There are 12 attainable rows and 11 distinct budgets. Maximum absolute usage error is 0.123 observations, consistent with “within 0.13.” Exactly three held-out mixture means exceed their targets. Only Bandit's gap target exceeds one usage SE, at about 1.338 SE. Nine nominal negative intervals exclude zero, leaving eight distinct budgets after the Tiger duplicate. The three intervals including zero are precisely those named in the main text.
3. Independently reconstructed the paired controller comparison from `results_price_dual_multiseed_metrics.csv`. Restricted means are 157.3 and 51.2, paired difference 106.1, and the Student-t 95% interval is [96.7701, 115.4299], matching the displayed [96.8, 115.4]. Recoveries are 9/10 versus 10/10. The new text does not substitute the recovered-only mean for the restricted estimand.
4. Compared the complete tabular bodies of `tab:sarsop`, `tab:cpomdp`, `tab:main`, and `tab:inspection` to the legacy source. **All four are byte-identical.** The unchanged RockSample table input and full frontier table remain included.
5. Scanned the integrated source and its table inputs. All 118 original direct source labels survive, there are no duplicate labels or unresolved references, and Section/Appendix references match their new locations. All 69 original citation keys remain used. This is preservation verification, not a new primary-source bibliography audit.
6. Checked the relocated empirical text and proof references against the main summaries. The restored example and short proofs occur once, while their former appendix positions now point to the correct locations. Important qualifications remain adjacent to the shorter main claims, with detailed supporting treatments preserved.

## Corrections identified and verified

This review found one overbroad inherited sentence in the held-out frontier comparison. “No single grid weight” implied held-out evaluation of every grid member, although the evaluated single-weight comparators are the bracket endpoints and the best feasible member. Both main and appendix now say that those evaluated comparators miss the targets by more. I verified the corrected wording in both masters and checked its direction against the archived values.

The budget-section roadmap was updated after selected evidence returned to main. I also verified the independent critic's corrections in the assembled source: four tested budgets are no longer called four distinct staircase steps, interleaved usage minima are restricted to the sampled grids, and the abstract's objective sign is explicit.

## Scope of this decision

This is an acceptance of the scientific preservation and clarity of the concision revision, with no remaining condition from this review. It is not a prediction of the journal's editorial decision. The root owns the final build, PDF visual inspection, archive rebuild, claim-check execution, and delivery. No fresh experiments were needed for these editorial changes, and this review does not claim a new audit of every unchanged source record in the entire project.
