# Critical preservation checklist for the 40-page main-text revision

Reviewer: independent concision critic. Baseline inspected: `paper/full_paper_jair.tex` at the start of the 2026-09-28 shortening pass, after the workflow-figure and copy-edit changes. This checklist is a preservation plan, not an acceptance decision on a revision that has not yet been assembled. I read `AGENTS.md`, the relevant publication ledger, and the manuscript's definitions, central results, experimental caveats, and concluding claims. No new experiment is needed for this editorial restructuring.

## Main-text argument that must survive

The main contribution is a procedure for calibrating one policy family's **expected sensing usage to a target**, with an EFE-based reference weight. It is not a constrained-reward optimizer and is not evidence that more sensing is intrinsically better. A reader should be able to recover the following argument without reading the appendix.

1. Define the known-model observe-then-commit problem, expected episodic reward, information gain, and expected usage. Explain that rewards do not enter the observation channel. Explain how the reward-plus-information planner and its receding horizon operate. State what the engineer provides, what calibration chooses, and what must be audited on deployment.
2. Distinguish the equality target from an expected-usage cap and from a hard per-episode cap. State explicitly that the information weight is an operational calibration price and is not the usage-cap Lagrange multiplier. A short equality-target motivation must remain: coverage or verification can itself be a requirement that the task reward omits. When reward maximization subject to a cap is the real requirement, a cap optimizer or best feasible mixture is the relevant method.
3. Define the usage curve, level set, crossing threshold, grid bracket, and per-episode endpoint mixture without conflating them. Explain nonmonotonicity, unattainable or unbracketed cases, and grid resolution. The mixture formula is a central operational result and should stay in the main text.
4. Give the scale-equivariance result with a scale-independent tie rule, both count and cost identities, and the fixed-weight consequence. Rescaling transfers any tuned weight under the same assumptions, not only a budget-selected one. Numerical bit identity is a measured fact for the released seeded implementation, not a mathematical guarantee for floating-point arithmetic.
5. State the stationary controller and all its hypotheses, distinguish stationary convergence from empirical recovery after a shift, and summarize the recovery result on a common estimand.
6. Present the calibration study before the broad EFE tour. State its calibration/evaluation split, target selection, actual usage error, reward cost, and reference limitations. This is the central empirical test of the paper's current framing.
7. State the EFE equivalence with its reward convention, units, normalizer limitation, and structural scope. Summarize the default weight's successes and counterexamples. Conclude with a conditional recommendation rather than a universal recommendation for weight one or for spending a stated budget.

## Theory safeguards

### EFE reduction and its scope

- Preserve the formal claim as an identity for the specified recursive reward-based objective. Do not shorten it into an unqualified identity between all active inference and all rho-POMDPs.
- The equivalence statement must retain exact Bayesian conditioning, deterministic choice, the same horizon, shared information units, and the pragmatic-value/reward identification. The undiscounted theorem and the discounted recursion are distinct formulations.
- Keep a main-text sentence that log scoring provides the exact reward interpretation. With an arbitrary reward convention, the reduction is conditional on the adopted recursion. A separately normalized preference distribution contributes a normalizer term that can be policy-dependent for variable-length episodes. The derivation can move, but this limitation cannot disappear from the setup.
- Preserve the bit/nat conversion if numerical weight-one claims appear in the main text. The theoretical nat coefficient is not automatically the literal bit coefficient used in code. A short linked explanation suffices if the full conversion and nat-canonical experiment move.
- Factored-observation coverage is for actions preserving the hidden state, with the precise reward-as-observation convention. RockSample here has a fixed hidden quality vector and is a cost-modified benchmark. Do not imply that the theorem covers the standard RockSample dynamics or all exploitation actions.
- The destructive-sensing example, timing convention, and detailed coupling derivation can move together. Main text must still say transition-changing sensing needs a transition-aware epistemic term. `Delta_T` is a diagnostic, not a proved additive correction or error bound. Do not revive “small drift gives small error.”
- The two-state near-optimality proposition and proof can be appendix material if the main text does not imply a general near-optimality theorem. Keep its horizon/two-state restriction adjacent to any main-text invocation. The measured high-penalty regime remains empirical guidance, not a universal boundary.
- Convex/PWLC guarantees do not apply to the concave information-gain utility. Fehr's guarantee needs its Lipschitz assumption. These can be one qualified related-work sentence with linked detail.

### Price, mixture, and controller

- The level set can contain many weights or be empty. `w=1` belongs to the level set of its implicit budget, but inversion need not return one.
- The crossing threshold is a scalar, selected by the last upward crossing convention. The half-open reported grid bracket is an estimate. Containment applies to its **closed enclosure**, under straddling and no missed crossing, including beyond the grid's last point.
- Some two-policy mixture may attain a target even when the selected crossing pair is undefined. A curve that only descends is the counterexample. The full example may move, but the definition must keep the distinction.
- The endpoint-mixture equality is exact for population endpoint usages. Calibration estimates determine an estimated mixture, whose held-out mean can miss the target. Do not call measured target attainment a finite-sample or population feasibility guarantee.
- The minimum attainable usage need not be `U(0)`. Preserve at least a main-text warning that positive weights can reduce usage.
- Exact maximizers over a fixed plan set have monotone information gain and nonincreasing reward. This does not prove monotone observation counts or transfer automatically to a replanning policy. The theorem's short proof is useful, but can move if the distinction stays explicit.
- PI-5 must retain stationarity, fresh independent episode noise/bounded usage, a single interior sign-consistent crossing, separation from the target away from the crossing, and the summability conditions. The full direct supermartingale proof can move intact.
- At a usage jump, convergence of the weight does not imply convergence of expected usage to the target. The running-average result is specific to the stated decaying schedule, and a stationary target-attaining policy is the endpoint mixture. Retain both distinctions in the theorem or immediately after it.
- The library constant-step/unbounded default and the reset heuristic are not covered by PI-5. Both measured controllers cross a nonstationary shift, so neither shift experiment is covered by the stationary theorem.

## Empirical safeguards

### Calibration and reference frontier

- Keep the predeclared rule's true status: budgets are calibration-derived, independent of weight-one usage, not externally specified application requirements. Post-inspection additions are the best-target/best-feasible mixtures and the same-stream reference comparison. They must not inherit the original study's preregistration description.
- Primary result: all 12 attainable rows, representing 11 distinct budgets, have held-out mean usage within 0.13 observations; three unattainable budgets are declared. This is an observed result and does not guarantee a cap, including an expected cap.
- The best feasible single weight is selected as feasible on calibration means. Its held-out feasibility is observed, not guaranteed.
- The reference is the **at-most-B LP feasible envelope** over sampled near-optimal policies, not equal-usage interpolation. It remains defined above the largest sampled usage and is flat there. The historical interpolation error and corrected numerical history can move to the appendix or ledger.
- Near-optimal sampled policies, Monte Carlo estimates, and maximization over noisy points do not certify the true constrained optimum. Avoid promoting the sampled envelope into an “optimal frontier” through a shorter caption or axis label.
- Retain the same-stream result with its correct status: 8 of 11 distinct budgets have nominal pointwise plug-in paired intervals excluding zero. Fitting support/mixture weights on those same means creates selection and feasibility uncertainty that the intervals do not propagate, and the intervals do not adjust for multiplicity.
- Retain the Tiger rare-event caveat next to this headline. No held-out wrong commits occurred; two of the Tiger shortfalls are not robust to the reference's canonical wrong-commit frequency. This should not survive only in a distant appendix if the 8-of-11 result is in the abstract or conclusion.
- Retain a concrete example that the selected crossing mixture is not reward-best even within the sampled family: Bandit's gap-target best mixture earns 5.94 versus 5.62 but misses the usage target by 0.18 rather than 0.09. This is an observed trade-off, not a claim of dominance.
- At least one concrete example should show that spending more than reward justifies lowers return (Tiger or Bandit). This establishes why target calibration and cap optimization are different design requirements.

### Supporting empirical claims

- Recovery headline must use `min(T,180)` across all ten seeds: 157.3 versus 51.2, paired difference 106.1, interval [96.8,115.4]. Keep 9/10 versus 10/10 recovery and label about-threefold as a descriptive ratio. Conditional recovery means, all detector parameters, the obsolete 2.65 ratio, and the seeding correction narrative can move.
- Scale-collapse figure needs both raw and normalized axes. The recently corrected presentation answers why identical curves are evidence rather than three plots of the same data. The four-environment numerical table can move alongside bit-identity details, with one main-text sentence that Tiger's collapse is trivial over the tested range.
- EFE's untuned default is inside the reward-maximizing bracket on three of five swept environments, outside on Testbed, and Pareto-dominated on Tileworld. Preserve those negative cases near any “strong default” claim.
- TOST claims require the fixed practical margins and scope to the three core environments. An ordinary failure to reject a reward difference is not equivalence. Full n=5/n=20, paired/unpaired details and per-seed archives can move.
- The endogenous weight-one CPOMDP comparison has a slack cap on all three core environments. It must not be sold as broad evidence for cap-constrained optimality. It can move entirely if the main text retains a pointer and does not overgeneralize it.
- A tuned POMCP comparison on Tiger is retrospective, and differences elsewhere do not isolate one EFE component. Keep the joint-configuration attribution if any mechanism claim stays. Full sweeps, rollouts, and ablations can live together in an appendix.
- Preserve the null or adverse cases that prevent a size-based superiority story: RockSample[11,11], Navigation, shallow search, and model overconfidence. Inspection shows feasibility in a synthetic known-model benchmark with a hand-coded leaf rule, not industrial deployment validation.
- A sensing budget does not protect against reward-irrelevant sensing. Keep this failure mode in the main discussion, with the distractor experiment and relevance-weighted variant linked. The IDS adaptation's raw-entropy fallback is an implementation-specific finding, not a general defect of IDS.

## Figures and tables

Keep figures that carry the core causal or empirical argument. The likely main set is the price-curve hero, engineer workflow (specifically requested by the user), target-versus-cap geometry, raw/normalized scale collapse, online recovery, one broad staircase, and one compact representation of the target/reward comparison. A Pareto figure is useful if the default-weight counterexamples otherwise become hard to see. The full frontier table can move if a faithful smaller table or plot and the limitations remain in the main text.

Strong move candidates are the OTC loop, destructive-sensing timeline, controller-loop schematic, onset test, heterogeneous-cost breakdown, second staircase, distractor composition, Tileworld trajectory, and Tileworld scaling plots. These are not incorrect or useless; each mostly supports a specialized subsection that can move intact. Do not remove the only visual explanation while leaving its main-text exposition long and dense. Move figures with their explanation and protocol rather than parking unexplained images in an appendix.

Caption condensation is appropriate, but every retained plot must still identify what was measured, relevant sample unit, uncertainty type, normalization, and whether bands are grid brackets or uncertainty intervals. The figure's main claim should be recognizable from its title/caption. All table bodies should preserve the existing uniform typography rather than buying space by shrinking text.

## Assembly audit to perform on the exact revision

1. Main text has a short experimental roadmap and meaningful appendix pointers at every moved result's first use. Each appendix section explains its local notation and protocol without relying on a deleted transition.
2. Labels and equations are unique; references and figure/table inputs resolve; section labels refer to the right subject after reordering. No bare proposition number is stranded by changed numbering.
3. Both live masters contain scientifically identical prose. A paragraph moved in one is not merely deleted in the other. Legacy masters and PDFs remain recoverable from the dated snapshot.
4. Check all numerical tokens in retained/summarized result sentences against the baseline and committed tables. Audit all new summaries for changed comparison set, denominator, sample unit, or significance language.
5. Compile and inspect the new main/appended boundary, float placement, captions, and all newly condensed tables. Measure the main body from the rendered PDF, not source words or a guessed page count.
6. Review the abstract and conclusion last. They must match the reduced main argument and include its most consequential limitations, rather than advertise every appendix experiment as an equally central contribution.

Final acceptance of the shortening pass remains pending exact-source review.
