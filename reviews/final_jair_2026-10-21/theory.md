# Independent final theory and significance review

Date: 2026-10-21 (America/Denver). Reviewer: `jair_final_theory_20261021`.

Reviewed repository HEAD: `f2d4069234811f1dc8bfa3ef6d35b373aef85553`.

Reviewed JAIR source SHA-256: `db283e6949d6a018a1bbed7fb93c4291b0b5b25dbf0fab63d2b43978da4fb9a9`.

## Recommendation

**ACCEPT for the manuscript's stated, bounded contribution. No required mathematical or theoretical-scope revisions identified.** This is an independent submission recommendation, not a prediction or guarantee of JAIR acceptance. Previous reviewer verdicts did not supply evidence for this judgment. Confidence is high in the checked mathematics and moderate in the journal-level significance judgment.

This recommendation covers the source above. Any subsequent mathematical or scope changes should be checked against their actual final text. The parent reviewer is handling rendered-document checks and the rest of the panel.

## Scope and method

I read the central argument, the complete propositions and proofs, their interpretation in the introduction, results, discussion, conclusion, and checklist, and the retained methodological appendices. I independently reconstructed the arguments rather than relying on tests or earlier reports. I inspected the implementation of the Planning+IG and EFE recursions, comparison tolerances, usage-grid solver, LP reference, dual update and controller, and the relevant existing threshold/equivalence tests. No experiments or tests were run by this reviewer, and no source, figure, result, or code files were edited.

Primary-source spot checks covered Fehr et al.'s Lipschitz hypothesis, Da Costa et al.'s finite-horizon recursive inference result, and the relevance and identity of Walraven et al.'s prior information-gathering work. This was not a new exhaustive audit of every bibliographic record.

## Correctness and scope findings

1. **EFE equivalence, lines 163–218 and 817–833.** The negation and backward induction are valid for the explicitly specified reward-based recursion, shared horizon, exact Bayesian updates, undiscounted objective and common deterministic tie rule. The paper now labels this a notational bridge rather than a reward-optimality result. Terminal actions have no observation or continuation term because the model explicitly excludes reward-conditioned belief updates. The normalizer discussion correctly identifies the possible policy dependence of a per-step `ln Z` on variable-length episodes. It does not claim that an arbitrary normalized preference model implies the empirical reward recursion. The bit/nat conversion is correct: bit-unit weight one is `1/ln(2)` reward units per nat, and nat-canonical weight one corresponds to bit-unit weight `ln(2)`.

2. **Factored extension and its boundary, lines 226–253 and 1046–1080.** Under preservation, the two specified hidden-state posteriors coincide and the KL diagnostic is zero. Navigation has zero information gain only under its explicit no-information assumption. The restriction on exploitation transitions is retained. The perfect-sensor counterexample correctly prevents an unsupported small-drift bound. In the destructive-sensing example, the post-transition state is deterministic before the report, so its information gain is zero; the three distinct values `2-c`, `1-c` and realized `-c` are consistent. The diagnostic is not presented as an additive value correction or error bound.

3. **Expected-use target versus cap, lines 291–307, 548–610 and 775–798.** The calibration requirement is equality in expected usage; the comparison problem is reward maximization under an upper bound. The information-floor optimality inequality follows directly from exact maximization of `R+wI` over a fixed class. It is not applied to the full closed-loop behavior of the implemented receding-horizon planner. The manuscript distinguishes a selected endpoint mixture from the best equality mixture, the best cap-feasible mixture, and a global constrained optimum. The LP implementation optimizes the intended inequality or equality over measured points, with a basic optimum supported on at most two policies. Sampling, approximation and selection limitations are disclosed.

4. **Level set, threshold, bracket and mixtures, lines 319–344.** These are four different objects throughout the checked argument. The final-crossing definition handles a plateau, unattained jump target, multiple crossings and an undefined price. Containment is properly asserted for the closed enclosure, conditional on no missed crossings. The selected solver can remain unbracketed after a final sampled fall below target even when another pair of policies can attain it. The descending-curve example correctly separates general two-policy mixture attainability from this solver's selected upward crossing. The mixture probability is in `(0,1]` for the stipulated strict lower and weak upper straddle and gives the target by linearity. Estimated usages are not silently substituted into a population guarantee.

5. **Scale equivariance, lines 346–371.** Positive rescaling preserves the recursion's action ranking when pragmatic rewards, observation costs and the information weight are scaled together, with an invariant tie convention. Count usage is unchanged; monetary/cost usage gains a factor of alpha. The two threshold transformations use the corresponding target units correctly. The code's relative tolerance is homogeneous before floating-point rounding; the manuscript correctly treats bit-identical recorded results as a measurement rather than a guarantee about numerical arithmetic. Directly tuned weights receive the same equivariance benefit, as explicitly stated.

6. **Monotone comparative statics, lines 373–398.** The two optimality inequalities imply nondecreasing information and nonincreasing reward for exact maximizers over the fixed plan set. They do not imply monotone count, and the text does not extend them to the implemented episode-level policy family. The single-observation onset is the supremum threshold even when the commit-favoring rule assigns the threshold itself to zero usage. Its relationship to an estimated grid bracket is correctly limited.

7. **Two-state thresholds, lines 1005–1038.** The first observation has advantage `(p-1/2)(R+ - R-) - c + w Imax`. The second independent symmetric observation at posterior `(p,1-p)` has zero instrumental value because the expected maximum posterior remains `p`. Hence the upper threshold in this model is `c/I(b)`, and the stated one-observation interval follows. Perfect sensing is covered in Part (a) with the entropy convention and excluded in Part (b), where the denominator vanishes. Longer receding-horizon episodes are explicitly outside the result.

8. **Stationary controller, lines 405–436 and 1106–1115.** The squared-distance/projection inequality and nonnegative supermartingale are valid. Bounded usage supplies the required conditional second-moment bound. The sign condition and uniform separation outside neighborhoods rule out a positive limiting squared distance. At an interior limit, bounded increments and vanishing step sizes make projection eventually inactive. The telescoping weighted discrepancy series then converges; Kronecker's lemma plus `n a_n` tending to a positive constant establishes average observed usage convergence for the harmonic schedule, including gap targets. Neither pointwise usage convergence nor arbitrary-curve convergence is inferred. The constant-step library default, resets and nonstationary experiment remain outside this theorem.

## Novelty and significance for JAIR

The individual mathematical ingredients are modest: the EFE identity is an algebraic correspondence, scale homogeneity is elementary, two-policy mixing follows from convexity, and the scalar controller uses classical stochastic approximation. I would not accept a claim that these are individually a new general planning theory or a new solution to the constrained-POMDP problem. The manuscript does not make that claim.

The positive case for a journal contribution is the complete operational and empirical account of an otherwise easily misunderstood design choice. It identifies what can and cannot be controlled by an information weight in a receding-horizon family, provides a reproducible crossing-and-mixture procedure for usage gaps, carries the units through scale changes, and supplies a conditional online result. Its comparisons distinguish three materially different explanations of reward loss: spending beyond the unconstrained optimum, selecting an inferior mixture within the same family, and limitations of the policy family itself. The distractor, destructive-sensing and recorded-sensor results make the boundary conditions concrete rather than merely listing caveats. The negative results are informative: target matching does not select a generally superior acquisition policy, and frozen calibration need not survive collection shift.

I therefore judge the integrated contribution sufficient to recommend submission to JAIR as a careful study of calibration and the limits of an information-weighted planning family. This is more persuasive as a technical and empirical account than as a general algorithmic advance. A JAIR editor could still judge the incremental novelty or operational significance insufficient, particularly because the external targets are researcher-defined and the recorded-sensor controls classify better. Those are disclosed limitations and editorial risks, not hidden validity defects or a reason to demand an unmotivated additional experiment before submission.

The closest prior-work claims are appropriately restrained. [Fehr et al. (2018)](https://papers.nips.cc/paper_files/paper/2018/file/de7f47e09c8e05e6021ababdf6bc58e7-Paper.pdf) explicitly require Lipschitz rewards for their guarantee; manuscript line 124 retains that qualification. [Da Costa et al.](https://arxiv.org/abs/2009.08111) connect recursive inference and finite-horizon Bellman optimality; the manuscript distinguishes that limiting construction from the fixed-weight identity. [Walraven et al.'s institutional publication record](https://research.tudelft.nl/en/publications/information-gathering-in-pomdps-using-active-inference/) establishes a prior active-inference/POMDP bridge; the present paper cites it and locates its contribution in usage calibration rather than claiming that bridge originated here. The linked Walraven full text returned HTTP 403, so this review does not claim a new full-text comparison with it.

## Optional refinements, not acceptance conditions

- **Lines 1020–1027:** Replace the piecewise upper-threshold display by `w_over = c/I(b)` after stating the symmetric-model identity `VoI2(b)=0`. Its alternative branch is unreachable under the stated assumptions, and removing it would make the proposition easier to parse without changing its domain. Do not generalize the proposition to other observation/reward models as part of this cleanup.
- **Lines 419–422:** Explicitly write `eta_0>0` as well as `delta>0` when describing the harmonic schedule. Positive step sizes are conventional and implicit here, but naming the initial-step sign removes a small avoidable ambiguity. Similarly, “per-episode usage is uniformly bounded (by the step cap for counts)” would distinguish the boundedness needed by the proof from the literal count bound if readers apply the controller to costs.
- **Line 329:** The alias `w^dagger(B)` is unused elsewhere. It may be removed to reduce notation, with `w*(B)` retained consistently.

These are local clarity improvements, not discovered counterexamples to the central claims. My ACCEPT recommendation does not depend on their adoption.

## Final-source re-review, 2026-10-21

**Final verdict: ACCEPT, with no outstanding required revisions.** I inspected the actual changes against `f2d4069` in both live masters and read the resulting mathematical paragraphs in context. This verdict applies to these exact final sources:

- JAIR, `paper/full_paper_jair.tex`: SHA-256 `bc8871292a3070c36c015cbca4b2e7229dd4bb737fe752c989ff2604e5672bcd`.
- LNCS, `paper/full_paper.tex`: SHA-256 `10b6a0c8921de1c0840ad76b8f93c92e6db93b3f15215ebb754768eb52b8347a`.

The optional mathematical refinements above were adopted correctly and consistently. The upper threshold now states `(c-VoI2(b))/I(b)=c/I(b)` under the already-stated symmetric model, retaining the exclusion of perfect sensing from Part (b). This removes an unreachable branch without expanding the theorem. The controller explicitly requires positive initial step size, separates count and cost bounds, and retains the exact conditions needed by the unchanged supermartingale argument. The revised Kronecker passage separates two valid steps without changing their content. Removing the unused threshold alias does not change the definition or its boundary cases.

The EFE normalizer pointer now leads to the qualification following the proposition, and the factored proof sketch names its proposition. The revised statistics wording identifies seeded runs as replication units without universally asserting dependence among episodes. The JAIR checklist now states a measured gap to a sampled reference rather than an optimality-gap guarantee. These edits improve precision and introduce no stronger theoretical or empirical claim. The JAIR-specific metadata/footer changes do not affect scientific content; rendered appearance is outside this source re-review.

I also inspected revised submission-form section 8.9.1. Question 1 accurately identifies a specified policy family, an expected-usage target, conditional convergence and the reward-based EFE convention. Its recommendation is restricted to cases where expected usage is itself a requirement. Its scope matches the manuscript and it is below the saved 150-word limit. Question 3 removes stale proposition numbers and correctly includes the recorded-sensor extension with independently fixed targets, controls and transfer failures. The AI-use statement in the comments for the editor matches the manuscript acknowledgment verbatim. This verifies textual consistency, not the authors' personal factual attestation or a new check of the live form requirements.

No new experiment or test was run for this re-review. No new required or optional manuscript edits are requested. The independent novelty/significance assessment above remains unchanged.

## Delivery-hash confirmation

The final JAIR preamble additionally guards an empty DOI label, supplies a short running title, and maps rho to plain text in PDF metadata. I inspected the actual preamble. Mechanically removing only those three additions reconstructs the immediately preceding reviewed JAIR hash `bc887129…` exactly, confirming no other text changed during this step.

The **delivery JAIR source SHA-256 is `c260180b50f5845132a6aeba50150373cf5ae5f74331feb9d5490aeae77d65c2`**. LNCS remains `10b6a0c8921de1c0840ad76b8f93c92e6db93b3f15215ebb754768eb52b8347a`. The final recommendation remains **ACCEPT, with no outstanding required revisions**, for these delivery sources.
