# Independent final evidence assessment, 2026-10-01

## Decision: ACCEPT

I recommend acceptance of the final manuscript's scientific contribution from the experimental-evidence and reproducibility perspective. No required empirical revision remains. This is an independent assessment of the present argument and its evidence, not an endorsement inherited from a prior panel or a check limited to whether my suggested replacements were applied.

The assessed final source hashes are:

- `paper/full_paper_jair.tex`: `73f6ee1feb9bf2202bc141dadf52ae557816a8934ecfa0db47a1836b07b4a44c`
- `paper/full_paper.tex`: `25a9eaa30eac01e354775cd33f8018685dc171cc932e5f5e5fc1ba6a0aeb0a44`

These supersede the initially supplied review hashes `f1653733...` and `c6573335...` and the first accepted final-source hashes `0d77ee42...` and `f498788c...`. I verified the latest hashes directly after the two final deltas reviewed in the addendum below. This report assesses source and artifacts. PDF build and visual inspection were ongoing in the parent task and are not certified by this report.

## Why the evidence is sufficient for the stated contribution

The paper's central deliverable is a way to set expected sensing usage within an explicitly chosen information-weighted policy family. It does not promise constrained-reward optimality, universal usefulness of weight one, deployment readiness, or superiority over state-of-the-art POMDP solvers. That distinction is explicit in the abstract, introduction, methods, results, discussion, and conclusion. The experiments support that narrower contribution.

The calibration study selects targets and endpoint mixtures using calibration data and evaluates usage on separate seeds. It reports accurate average usage, unattainable below-range targets, finite-sample overruns, a nonmonotone usage curve, and a within-family example where the selected endpoint mixture is not the best target mixture. That combination tests the mechanism and its limits. The target values are generated from calibration curves rather than supplied by an application, and the source makes this distinction clear. An actual industrial use case would strengthen external validity, but is not required to substantiate this synthetic known-model study as framed.

The revised reference comparison asks the appropriate two questions: what reward is lost by spending an equality target when a cap could be slack, and what shortfall remains against a sampled reference fitted to the target. The cap and target references are treated as approximate, noisy fitted mixtures. Their intervals are expressly nominal pointwise plug-in summaries, not simultaneous confidence statements or certified population-frontier bounds. Independent LP recomputation reproduced the held-out target gaps and SE. The fresh-seed replay keeps fitted supports and weights fixed, and the main text now explicitly states that fresh realized usage need not equal B. Thus the 2/11 headline is an accurate description of this fitted-reference procedure rather than a claim of fresh-stream equality matching.

The twenty-seed episode-matched SARSOP check provides meaningful additional evidence for the limited equivalence claim. Its paired statistics reproduce from per-seed means: Diagnosis 0.1118 ± 0.089912, p = 3.20309e-9; Bandit 0.0435 ± 0.031328, p = 4.57718e-12. Tiger is degenerate with zero differences. The inference is confined to the declared margins and three environments. The retrospective margin choice, added-seed scope, and distinction between seed pairing and episode matching are disclosed. These results support equivalence within those operational margins, not exact equality or universal near-optimality.

The POMCP comparisons remain a qualified implementation study, which is appropriate. The cost sign and path-belief mechanics are correct in the inspected implementation and pass their targeted tests. The fixed-configuration outcome values, selected exploration-constant comparisons, and compute control support the reported numerical findings. However, the paper also states the remaining leaf/rollout departures, fixed versus varying internal planner seeds, candidate-grid selection history, and lack of a full causal separation of leaf evaluation, commit values, and tree mechanics. It no longer claims that the implementation departures necessarily help POMCP or that comparison with exact enumeration is simulation-matched. A substantially stronger standard POMCP implementation could change this secondary comparison without refuting the calibration result.

The broader EFE evidence is balanced. The main argument includes its reward-maximizing sampled plateau on three of five environments, losses on Testbed and Tileworld, no advantage over Planning on the largest RockSample instance, a strong standalone heuristic, the horizon dependence of Tileworld's positive result, and the negative Navigation case. The RockSample results are explicitly conditional on their shared leaf rule. The paper does not turn failure to reject a difference into a TOST equivalence claim. The reward-, success-, and usage-based objectives are distinguished rather than treated as interchangeable achievements.

The methods also separate the formal claims from empirical guidance. The EFE equivalence is a conditional identity for the specified reward-based recursion, with reward normalization, bit/nat conventions, tie-breaking, and state-preservation scope disclosed. The stationary controller theorem is separated from the nonstationary reset experiment. The latter provides evidence of re-adaptation on one scale-shift scenario, not a tracking guarantee. I reviewed those claims for consistency with the experimental interpretation, rather than independently re-proving every theorem in this evidence review.

## Final-source corrections and regression check

All required issues from `evidence_audit.md` are resolved in the final source. The abstract/main result distinguishes frozen-reference fresh replay; Tiger's reward-usage identity and zero sensitivity **mean** gaps are confined to held-out data; the appendix explicitly returns to the predeclared comparison at B after discussing usage matching; and the RockSample shared-leaf claim is conditional rather than invariant. The POMCP implementation and simulation-matching language and the JAIR random-seed checklist are likewise corrected.

The final read found two additional narrow inconsistencies, both corrected before the hashes above were recorded. Equal sensing costs are now described as sufficient for fixed count/cost conversion, without falsely making them necessary. The discussion's ablation conclusion now specifies success and reward, preserving the significant Tiger observation-count effect. The adjacent RockSample prose now says that agents follow low-activity policies rather than asserting identical policies.

I examined the complete substantive diff in both masters, with word-level comparison to avoid overlooking changes within long paragraphs. The only source differences between their substantive edit sets are the structured versus unstructured abstract, the JAIR-only checklist, existing format-specific prose/accessibility material, and appendix float placement. The two changed producers only update caption text: the horizon map now states its actual reward-gap criterion, and the atlas labels brackets as estimates of the crossing threshold. Their table outputs match those edits. No result CSV changed, no solver/agent behavior changed, and the full diff introduces no new empirical outcome or strengthened inferential claim. The appendix section-wrapper replacement concerns layout and does not alter scientific content.

## Numeric-advisory triage

The claim verifier's exit status is not sufficient validation. I inspected its 84 advisories, representing 42 warning instances mirrored across the masters, and resolved them by artifact group. None identifies an unresolved numerical error.

1. **Bracket stability and Bandit crossing (7 instances per master).** `results_price_bracket_stability.csv`, rather than its counts companion, gives Inspection's minimum reported-bracket frequency 0.789. `results_price_usage_curves.csv` gives Bandit's weight/usage values 0.138950/6.192 and 0.719686/5.108, with the final crossing bracket endpoints 1.637894 and 3.727594. These round to the printed values.

2. **RockSample POMCP leaf/belief sensitivity (10 instances).** The appropriate sources are `results_rocksample_pomcp_sensitivity.csv` and its `_stats.csv`, not the nearby tuning CSV. The relevant reward/SE pairs are 12.934/0.247742 for particles, 12.813/0.425402 for the frozen setting, 14.516/0.337737 for the greedy-belief leaf, and 17.155/0.439869 for standalone approach rollout. Reward p-values are 0.813497, 0.014813, and 0.001708 for the cited comparisons, with the last two not surviving their stated Holm family. All printed roundings are supported.

3. **MCTS ablation (1 instance).** `results_mcts_efe_ablation_stats.csv` supplies Tiger full versus no-tree-IG observation-count p = 0.001356, which rounds to 0.0014 and survives correction. It is not expected in the outcome-summary CSV. The final text preserves this exception.

4. **POMCP exploration and selected configurations (8 instances).** P-values are in `results_pomcp_exploration_sweep_stats.csv` and `results_pomcp_exploration_selected.csv`. Relevant values include Tiger default-EFE versus POMCP c=50 success p = 0.000159 and reward p = 0.002073; Tileworld default versus c=5 MCTS reward p = 0.001741; selected Tiger reward p = 0.0005104196; Diagnosis uniform versus information-gain rollout success p = 0.573265; and Tileworld's corresponding success p = 0.000179. Outcome fractions 0.656 and 0.026 become 65.6% and 2.6%. These warnings are nearest-file or percentage-resolution artifacts.

5. **Five- and twenty-seed TOST (9 instances).** The aggregate files `results_tost_sarsop.csv` and `results_tost_sarsop_n20_robustness.csv` contain the cited intervals, SE, and paired/unpaired p-values. Tiger intervals are ±0.414894 and ±0.208664. Diagnosis paired/unpaired p-values are 0.016076 and 0.045818, with unpaired SE 0.383567. Bandit's unpaired p = 0.012975 and SE = 0.175295. The nearby per-seed archives are the inputs rather than tables of these derived quantities.

6. **Subsidy design, maxima, and reference gaps (7 instances).** The subsidy fraction endpoint 0.98 is specified in `run_frontier_target_reference.py`. `results_cpomdp_frontier_subsidy.csv` gives maximum held-out usages Tiger 7.172, Diagnosis 16.576, Bandit 11.594. The Diagnosis cap gap -1.104 ± 0.219217 comes from `results_budget_frontier_heldout_reference.csv`. The fresh target gaps -0.560155 ± 0.235923 and -0.502608 ± 0.105931 come from `results_budget_frontier_target_reference.csv`, not the nearby post hoc usage-matched file. The final text explicitly separates those comparisons.

These checks supplement the independent computations and 14 passing targeted tests recorded in `evidence_audit.md`. No new experiments or test runs were needed for this final-source assessment.

## Nonblocking limits and factual note

The five-seed families are small, several comparisons are exploratory, the reference is selected from noisy approximate policy points, and Tiger's rare wrong commits can materially change reward gaps. The target-reference fresh replay is partly non-blind in the history of the Diagnosis comparison and does not establish equality matching on the fresh stream. The horizon-map criterion is deliberately coarse and lenient. The models are known, synthetic, and mostly small. Those are substantive limitations, but the current manuscript discloses them and limits its claims accordingly. Resolving all of them would create a broader paper rather than repair the stated contribution.

The author brief's phrase "seven of the eight" cap shortfalls being slack is incorrect. Seven of eleven **budgets** are slack; six of the eight held-out negative intervals belong to those slack budgets because Bandit's smallest interior budget is slack but not significant. The manuscript states the correct seven-budget fact and does not propagate the brief's error.

No scientific or evidence blocker remains at the source hashes recorded above. Rendered-PDF and package checks remain separate deliverable checks for the parent task.

## Final two-delta confirmation

The acceptance decision holds at the latest hashes above. I read both changed passages in each live master, checked their surrounding argument, and compared the removed wording. No new experimental result or uncertainty claim is introduced.

The Agent Specifications appendix now limits the cited POMDP-IR/ρ-POMDP equivalence to piecewise-linear convex belief rewards and expressly declines to apply it to the concave expected-information-gain reward used here. This repairs an overbroad connection to prior work without changing the paper's separately proved identity between its specified EFE recursion and Planning+IG at weight one. The remaining statement that Planning+IG represents an explicit-information-reward approach is an appropriately scoped methodological association, not the removed equivalence claim. This addendum checks the revised scientific scope; the parent task performed the direct Springer §4.1 citation verification.

The RockSample detail paragraph now ends its EFE-versus-Greedy bad-rock comparison at the reported seed-level result. Removing "so the information gain term drives checking behavior" is necessary: that comparison varies planning and sensing behavior as well as the information reward, and reward-only Planning also avoids bad rocks. The retained sentence is descriptive and supported by the same unchanged measurements. It no longer assigns the observed difference uniquely to information gain.

Neither change creates a remaining empirical condition. Recommendation: **ACCEPT**.
