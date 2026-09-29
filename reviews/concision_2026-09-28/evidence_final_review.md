# Final evidence and cross-section review

Decision: **ACCEPT** for the content-preserving concision revision. No remaining required change in this review's scope.

Reviewed 2026-09-28 against the integrated sources, after the restoration and root's final local corrections:

- JAIR source SHA-256 `68564de762b5620dbb4fabb9d49a7036ea5db1eed6dc5b817990d98b2d7093f9`.
- LNCS source SHA-256 `2cd4eebdc2a47d9ee46046ce2681b1bc293af9b345473f8cc5ca7a9a35eaecfe`.

This review covers the scientific content preserved through shortening, the newly written evidence summaries, the main theory/editorial sections' claims and qualifications, internal citations, and relocation navigation. Root is responsible for final compiled-page/visual verification. This is an internal recommendation on the revision, not a journal decision or a new full experiment and literature audit.

## Evidence preservation

I prepared the evidence restructuring and then checked the integrated source, with an independent critic also reading the main evidence summary. The evidence union retains every original evidence label, citation key, figure/table input path, and unique decimal string. The new compact frontier table copies its 12 numeric rows from the original generated table's first and third panels. No value was newly estimated or rounded. The complete original three-panel frontier comparison remains in the appendix.

The main narrative preserves the essential caveats: calibration-derived targets rather than application-specified budgets, target versus cap, endpoint selection versus reward-optimal mixtures, 12 rows but 11 distinct budgets, observed usage accuracy rather than guaranteed cap feasibility, same-held-out-stream fitting and nominal pointwise plug-in uncertainty, reference selection bias, Tiger's absent rare errors, and Bandit's within-family counterexample. The restricted controller estimand uses all ten seeds, and the unseeded-run correction and stationary/nonstationary distinction remain explicit.

The n=5/n=20 TOST summary retains the margin, retrospective canonical comparison, prospective added seeds, paired sensitivity check, and suite-limited conclusion. The endogenous cap reference is expressly slack on all three environments. The POMCP summary now names MCTS-EFE as the simulation-count-matched comparator and distinguishes the separate wall-clock control. Original untuned comparisons and the later, retrospectively informed tuning sweep are not conflated.

The restored direct evidence improves readability without hiding adverse findings: cost and interleaved usage curves, staircase/bracket stability, reward-irrelevant sensing and its conditional remedy, the larger-RockSample heuristic's superiority, Inspection's reward/accuracy trade-off, and Tileworld's horizon-limited scaling comparison are visible in main.

## Independent cross-section checks

I read the revised abstract, introduction, related work, main methodology and budget theory, and Discussion/Conclusion alongside the evidence summary. The sign of the EFE equivalence is now explicit in the abstract: minimizing EFE is equivalent to maximizing reward plus information. Reward normalization, log-score exactness versus ordinary-reward convention, bits/nats, hidden-state preservation, rewards not being observations, and the destructive-sensing counterexample remain correctly scoped.

A direct comparison to baseline `2d3bac4` finds the original proposition, definition, corollary, and example statement bodies intact. The only differences in the near-optimality and controller statements are the two sentences naming their new appendix proof locations. In particular, the four controller conditions, gap-budget distinction, fixed-plan monotonicity restriction, and exact crossing/bracket/mixture distinction have not been weakened through shortening.

Internal-reference checks on the integrated JAIR source and its table inputs found no unresolved reference, and all cited bibliography keys exist. Navigation dependent on a previous or next subsection was replaced with explicit references where relocation had made it misleading. The two prose-semicolon issues I identified were corrected in the actual source, including the workflow accessibility description. The ambiguity over which POMCP comparison matches simulation counts was also corrected in the actual source. No further scientific or wording correction is required from this review.

## Limits

No empirical CSV, experiment result, or bibliography was changed by the evidence rewrite. I did not rerun experiments or re-verify all external primary sources, because the revision introduces no new experimental or literature claim requiring that work. The main contribution of this review is preserving the existing evidence and its adverse qualifications during restructuring. The root's build, source-package, and visual checks complete the separate artifact-verification work.
