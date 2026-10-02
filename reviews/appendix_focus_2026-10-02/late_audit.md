# Late appendices claim-focused audit

## Scope and verdict

Proposed replacement of the frozen JAIR span from `Extended Budget Evidence` through `Additional Interpretation and Tree-Search Controls`, before the reproducibility checklist. The frozen baseline is `paper/legacy/2026-10-02_pre_claim_focused_appendices/full_paper_jair.tex` from `3c1e99a`. Neither frozen nor live masters were edited. The three `old` values in `late_proposals.json` each occur exactly once in both frozen masters. No LNCS-specific replacement is needed.

**Proposal verdict: PASS for independent review and central reference repair.** The draft removes entire peripheral result tours and duplicated figures/tables while retaining the limiting evidence needed by the current main claims. This is a manuscript proposal, not a claim that final builds or independent review have passed. The root agent owns central application, main/checklist changes, guidance-ledger updates and commits.

The replacement text has 1,566 whitespace-delimited words versus 5,281 in the original source span, including LaTeX captions and descriptions. Four figure insertions and eight rendered table blocks are omitted: cost-budget, onset, interleaved-staircase and illustrative Tileworld figures; collapse, SARSOP, endogenous-cap, three frontier panels, Tileworld and transfer tables. The inventory is collapse (1), SARSOP (1), CPOMDP (1), frontier (3), Tileworld (1), transfer (1). No fonts, margins or spacing change. The expected late-span contribution is about 3–4 pages, subject to the root agent's integrated build.

## Claim and evidence map

- **Reward-scale equivariance and count-versus-cost calibration.** Main Sections `sec:collapse` and `sec:cost_budget` already report every bracket from the removed collapse table and both target pairs, including Tiger's unattainable target and the nonconstant count-to-cost ratio. Their own main figure/prose therefore carry the evidence. Delete the appendix copies rather than rewrite them more densely. Retained interleaved protocol now supplies actual margin fractions used for all three target-placement schemes.
- **Interleaved calibration does not imply monotone usage or arbitrary attainability.** Main `sec:interleaved_budget` already gives all usage ranges, the adverse RockSample[5,3] dip, its slack-nearest-point interpretation and the sampled-grid limitation. Retain per-seed episode counts, grid sizes and target placement in `app:interleaved_details`. Omit the duplicate staircase graphic.
- **Online reset helps in one nonstationary experiment, not by theorem.** Main `sec:dual_multiseed` already contains the full detector, hold criterion, censored restricted estimand, both means, paired Student interval, 10/10 versus 9/10 recovery, and explicit exclusion from the stationary theorem. The discarded appendix contains only supplementary conditional means, separate normal intervals and final-error summaries, none needed for the main claim. Do not replace the primary paired restricted estimator with those conditional descriptives.
- **The information-unit policy is near the offline reference within prespecified margins, under qualified design.** Retain the original five-seed TOST p-values and 90% intervals, retrospective choice of margins, the later 15-seed addition, episode-matched 20-seed design, paired/unpaired test results and raw archive pointers in `app:sarsop_details`. Omit the redundant five-seed mean table and the intermediate five-seed paired sensitivity analysis. Retain the failed Tiger usage-matching fallback explicitly.
- **Usage calibration differs from a cap-constrained optimizer.** Main `sec:cpomdp` supplies the penalty grid, approximate solve, finite-grid feasible-envelope construction, nonbinding natural EFE comparison and absence of a larger-instance constrained reference. `app:cpomdp_details` is retained on the common offline-reference subsection with exact evaluated family weights, equality-of-rewards observation and archive/routine pointers. No population bound is claimed.
- **Held-out endpoint mixtures meet attainable expected-use targets but can lose reward and need not be the best equality mixture.** Main `tab:budget_frontier_main` already reports every attainable target's B, U, R, cap gap and target gap. Main prose explicitly reports all three below-range failures, finite-sample overspend, slack-cap overspending, and the within-family Bandit failure. Retain exact within-family comparator identities in `app:frontier_details`. Omit the three-panel appendix table that repeats the primary numerical evidence. Its producer, table source and CSVs remain untouched in the repository.
- **Reference sensitivity and uncertainty limit the frontier interpretation.** Keep the subsidy construction, held-out fitting and frozen fresh replay, binding/slack partition, shortfall identities on both streams, non-blind Diagnosis pair, seed/episode counts, degrees of freedom and post hoc realized-usage sensitivity. The new text expressly points back to main `sec:budget_frontier` for fit/feasibility/multiplicity uncertainty, while retaining that these are conditional nominal pointwise summaries. Main retains stream dependence, selection bias and the important Tiger rare-event example. No deleted paragraph is needed to rescue a stronger frontier claim.
- **A sensing requirement does not guarantee relevance.** Main `sec:distractor` retains the adverse nuisance spending, factorization assumptions, ordinary versus relevance-weighted results, multiplicity family and failure of the IDS fallback. Keep `app:distractor_details` with a standalone definition of the deterministic Delta-squared/information action ratio, the quantities it uses, its fallback and the distinction from randomized IDS. This survives removal of the broader IDS appendix by the early agent.
- **Observation structure and leaf design delimit EFE comparisons.** Keep the partition study's full protocol and the severe overlapping-partition degradation, no reward/success separation, maximum reward-gap p-value and scan direction. Keep the RockSample leaf algorithm, phantom exit charge, standalone heuristic method, adverse depth-three result and mechanistic (not scaling-law) scope. Main already retains the heuristic's superior rewards on both larger instances and the exact-search failure. Omit the duplicated numerical tours, three-agent trajectory and heuristic near-optimality interpretation of Inspection.
- **Search comparisons concern coupled implementations.** Keep the full MCTS-EFE method, simulation-matched protocol/results and unequal computation, adverse reward/success comparison to Exact-EFE, and Tileworld's reward/usage cost for its accuracy increase. Keep the negative ablation finding and coupled leaf/belief/commit caveat. The early agent retains detailed exploration/rollout/compute controls and their retrospective selection qualification in `app:pomcp`.

## Discarded strands and why

The positive-threshold onset graph, numerical threshold tour and cross-domain Inspection threshold analogy are peripheral to expected-usage calibration and are removed together with their local claims. The theoretical proposition/proof is a separate decision owned by the theory/root agents. The zero-shot transfer matrix, Bandit one-depth-versus-another experiment and random-horizon/discount interpretation tour are removed as secondary operating-point analyses. Main reward-scale dependence, depth restrictions and adverse weight comparisons remain. No favorable-only selection is introduced: unfavorable results that bound the surviving claims remain either explicitly here or in the main paper.

The full core/Pareto/Inspection comparisons already have main tables and qualified conclusions. The late copies merely repeat table readings. Early appendices retain the negative baseline/statistical evidence, so late no longer points to removed `tab:effect_sizes` or repeats pooled/seed-level interpretation. The amended source introduces no claim that EFE is superior to reward planning, information-ratio policies or deeper solvers generally.

## Removed labels and central repair

Machine-readable exact frozen-source reference lines are saved in `late_removed_references.json`. It lists 19 affected lines outside this span. These are the complete labels removed by these three proposals, including the label introduced by the omitted table input:

- `app:core_details`
- `app:cost_details`
- `app:dual_details`
- `app:inspection_details`
- `app:pareto_details`
- `app:scale_details`
- `fig:costbudget`
- `fig:interleaved`
- `fig:prop2`
- `fig:tw_comparison`
- `sec:prop2exp`
- `tab:collapse-breadth`
- `tab:cpomdp`
- `tab:sarsop`
- `tab:tileworld`
- `tab:transfer`
- `tab:budget_frontier`

Recommended central repairs, with frozen JAIR lines:

1. Line 352: cite `sec:collapse` for Tiger's unbracketed B=4 instead of the removed collapse table.
2. Lines 470 and 514: remove the redundant collapse-table/appendix pointers. Main already reports their full numerical content and Tiger limitation.
3. Line 483: remove the promised controller appendix. The detector is already fully described immediately before the pointer and the primary recovery summaries follow.
4. Line 502: remove the cost figure/detail pointer or point to `app:interleaved_details` specifically for target margins. Keep the main target pairs and nonconstant cost-per-test result.
5. Lines 507 and 509: remove the interleaved figure pointer and the word "plotted". Describe the nearest-grid-point convention directly. `app:interleaved_details` gives sampling/target placement, not the removed brackets graphic.
6. Lines 527 and 531: remove `tab:sarsop`, retaining `app:sarsop_details` for inferential details and archives.
7. Lines 538 and 540: `app:cpomdp_details` now supplies archive/construction pointers and evaluated weights, rather than repeating all limitations. Remove the deleted table pointer and adjust any promise of additional limitations accordingly.
8. Line 555 and main frontier closing paragraph: replace promises of the complete three-panel table with an archive pointer or `app:frontier_details` for selection/reference sensitivity. Main table remains the numerical results table.
9. Line 582: the canonical-versus-held-out description currently promises direct cross-stream numerical comparisons in `app:frontier_details`. Those extra columns are omitted, so say they are in the result archive or remove that subordinate promise. Main keeps the illustrative Tiger discrepancy.
10. Line 628: retained `app:distractor_details` describes the IDS adaptation. Change the promise of full curves/comparison family/remaining numbers to that narrower method scope. Main itself already has the curves and corrected comparison family.
11. Line 641: remove the auxiliary onset summary together with its appendix pointer. The atlas strand is removed separately by the early agent.
12. Line 683: remove `app:core_details` from the list. Keep early `app:full_tables` and `app:stats` and match their revised scope.
13. Line 702: remove the extra Pareto-tradeoff appendix promise. Main preserves all qualitative trade-offs, exact suboptimal cases and nat-canonical qualification.
14. Line 707: remove the full Tileworld table/trajectory promise. `app:tileworld_details` now concerns partition robustness, which remains correctly referenced by line 709.
15. Line 731: remove the final Inspection two-state interpretation pointer. Keep all adverse reward/accuracy data and synthetic/shared-leaf scope in the main text.
16. Line 766: remove zero-shot-transfer sentence/table citation along with the separate random-horizon statement if the early proposal is accepted. The remaining paragraph already states that sampled-grid success/reward optima differ.
17. Line 942: drop the final illustrative-Tileworld-trajectory sentence if the early subsection itself is retained.
18. Line 1582: remove the last refined-grid-onset appendix sentence from the theory section if its numerical test paragraph remains.
19. Line 1619: remove or rewrite the battery-specific Tiger example that cites `tab:sarsop`. A general warning about distinct battery protocols is enough. Avoid attributing the 4.32 usage to the new failed-matching illustration instead of its original battery.

There are no direct checklist references to labels removed solely by these late edits. Checklist prose nevertheless lists now-omitted transfer, IDS, atlas, calibration and random-horizon batteries. The root agent should reduce these lists to the retained paper's scope while preserving every checklist question and truthful verdict. The seed/episode descriptions for retained TOST, frontier, dual and MCTS experiments still apply.

## Verification and review safeguards

Read `AGENTS.md`, the operative writing/process guidance, the claim-focused stage record and `reviews/appendix_consolidation_2026-10-02/independent_evidence_review.md`. The prior review's fixes are respected: no POMCP exact-belief contrast is reintroduced, the low-penalty Tiger claim is not touched, and no unsampled zero weight is substituted into the Testbed optimum. Negative results and retrospective/conditional qualifications remain central.

All new numerical results are verbatim subsets of the frozen span except the newly explicit end margins. These are protocol facts verified in `experiments/run_price_of_information.py`: `run_shadow_curves` calls `identifiable_budgets(..., margin=0.08)` at line 177, interleaved curves use `0.08` at line 518, and cost-budget curves use `0.15` at line 616. `rho_aif/budget.py:545` defines lower/upper positions as margin and one minus margin and evenly spaces targets between them. The interleaved grids use `make_log_w_grid(0.0,100.0,ng)` at line 495. The helper includes zero and logarithmically spaced positive weights. The original "narrower end margins" wording did not state these fractions even though the main text promised them.

Build-time checks remain required after central application: mechanically verify all removed refs, inspect page count/layout, confirm no duplicate labels, run the existing claim checker and independently audit the preserved evidence. No experiment, source data, bibliography, table producer or figure file was changed.
