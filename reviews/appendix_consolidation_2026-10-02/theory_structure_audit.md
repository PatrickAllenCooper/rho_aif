# Theory and appendix-structure audit — 2026-10-02

Scope: appendix A, appendix T, appendix U, and the appendix hierarchy of the archived `c5125ab` manuscript. This is a proposal-stage assessment, not acceptance of edits that have not yet been assembled and compiled. No live manuscript, experimental code, or data was changed by this agent.

The current mathematical content can be made substantially shorter without omitting proof steps. Most recoverable space is repeated explanation, not essential derivation. Twenty-five guarded replacements are in `theory_proposals.json`. They replace approximately 5,482 whitespace-delimited source words with 1,783, a reduction of 3,699, and remove two redundant schematics and a generic taxonomy table. This is not a measured page saving. The actual saving must be read from a clean combined build.

## What the batch preserves

- The complete finite-horizon equivalence proof in appendix A is unchanged.
- The scale-equivariance and comparative-statics proofs and all assumptions in the main text are unchanged.
- The state-preservation proof is unchanged. The destructive-sensing example retains its complete transition/observation model, obsolete and correct posteriors, infinite KL diagnostic, ranking reversal and realized-policy loss. Its useful state-timing figure remains.
- The usage-onset proof is unchanged. Its numerical check still distinguishes the one-shot theorem from complete receding-horizon episodes.
- The supermartingale and Kronecker arguments for the controller are unchanged. Stationarity, independent episode noise, bounded usage, interior sign-consistent crossing, and separation from the budget away from that crossing remain explicitly in the main theorem. No constant-step or reset-tracking guarantee is added.
- The two-state threshold statement retains both horizons, all model hypotheses, units, threshold-sign cases and perfect-sensing exclusion. Its compressed proof adds the explicit calculation showing that the second observation has zero expected instrumental value in the stated symmetric model. This replaces an assertion with its short derivation.
- Normalized preferences, conditional reward-based equivalence, and the empirical bit convention remain separate. The full normalizer derivation and nat/bit conversion already occur in the main text, so the appendix points there rather than reproducing them.
- Formal versus heuristic threshold applications, the Testbed boundary case, longer-horizon limitation, and adverse Testbed/Tileworld findings remain.
- Agent definitions and tuning details are untouched.
- All primary citations in the detailed related-work comparison remain, together with the distinctions from constrained-POMDP policy randomization, rational inattention, SAC, sequential design, internal Bethe constraints, and per-node dual methods.
- The failed shallow RockSample reference and the absence of a sampling advantage over direct tuning remain explicit.

## What is consolidated

U.1 repeats the main normalizer, reward-unit and alternative-EFE discussion almost verbatim. U.3 repeats the main explanation of exploitation actions and the limits of the coupling diagnostic. U.6 repeats the controller parameter/default/reset scope already stated beside its theorem. U.7 repeats and expands the main positioning discussion. These repetitions can be replaced by compact statements with precise cross-references while retaining the complete proofs.

The observe-then-commit loop and projected-controller schematic have no incoming prose references elsewhere in either master. They illustrate mechanisms already shown or fully specified in the main method. Their removal does not remove evidence. Keep the source producers and figure files in the repository. The destructive-state figure is retained because it makes an easy-to-misread timing distinction visible.

The application taxonomy is a list of examples, not data. Its broad labels such as environmental monitoring and mobile sensor networks can misleadingly suggest that an application name establishes a structural assumption. A short conditional statement about preserving the measured quantity over the decision horizon is more accurate and takes less space.

## Hierarchy and float barriers

The baseline has 26 appendix sections in JAIR, beginning on page 36. The checklist starts on page 104 and the PDF ends at 108. Thus the research appendices occupy approximately 68 pages before the checklist. Appendix T begins on 65 and U on 66, with V beginning on 77. Section U is the largest concentrated source of theory repetition.

The `FloatBarrier` commands are not explicit page breaks. Several successive appendix sections begin on the same page: A/B on page 36, C/D on 39, H/I on 47, and R/S on 59. They therefore cannot be credited with anything close to the entire 20–30-page target. A barrier can leave unused space when it flushes a large queued float, but that cost depends on the final float queue. Retain them for the first combined build, because they prevent figures and tables from drifting into unrelated appendices. Measure remaining sparse pages after content reduction. Remove or move a barrier only where adjacent material is being genuinely consolidated and its floats still remain legible and correctly associated.

A more coherent eventual hierarchy would use six or seven broad appendices:

1. Mathematical results and boundary cases: current A and U's theory/proofs.
2. Environments, agents and protocols: current E and V, plus U's agent-selection details and T's solver build.
3. Complete performance results: current B/C/F/G and X, with one home for each result rather than parallel full-table and extended-result narrations.
4. Sensitivity, calibration and diagnostics: current D/H/I/J/K/L/O/P/Q/R.
5. Budget calibration and references: current T's factorization/atlas and W.
6. Planning baselines and tree-search controls: current M/N/S/Y.
7. Reproducibility checklist: current Z, JAIR only.

This regrouping is optional and primarily improves navigation. It should not be used as a page-saving trick, and it adds relabeling/float-order risk if performed alongside a large prose edit. Existing label keys can remain stable even if their enclosing section number changes. References saying “Appendix” remain understandable for an appendix subsection such as A.2. Main-text references, statement/proof numbering, figure ordering and the package dependency list must still be checked after any regrouping.

The largest safe reductions should come from eliminating duplicate result narration, generic schematics and repeated protocol exposition, while preserving primary result tables, adverse results, uncertainty, selection history, complete proofs and runnable provenance. If those cuts meet the page target, no typography, margin, spacing or global float changes are justified.

## Guard checks

Every `old` block in all 25 proposals occurs exactly once in BOTH masters. Applying them sequentially in memory succeeds. No special LNCS variants are needed. Removed labels are only `fig:otc_loop`, `fig:dual_feedback` and `tab:taxonomy`, and neither proposed master contains a remaining reference to any of them. All proof/proposition/example/remark/figure/table environments remain balanced. `theory_self_audit.json` records baseline and proposed source hashes. The proposals introduce no new primary citation, experiment, numerical result or empirical claim. The added Bayes-factorization equation and second-observation accuracy calculation merely make the existing proofs explicit.

During self-audit, an initially unnormalized displayed posterior in the condensed destructive example was corrected before delivering proposals. The final expression uses proportionality followed by the normalized point-mass conclusion. The proposal generator is retained for reproducibility and was run only against the unchanged archived baseline.

A separate applied-batch audit must still inspect these edits in context, and a clean build must verify equation wrapping and float placement. Acceptance of the assembled manuscript should depend on that audit, not this proposal-stage assessment.
