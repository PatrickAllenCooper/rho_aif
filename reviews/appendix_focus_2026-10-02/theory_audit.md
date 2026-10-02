# Theory and protocol appendix proposals

Date: 2026-10-02. Baseline: `paper/legacy/2026-10-02_pre_claim_focused_appendices/`, frozen from `3c1e99a`. Owned sections: Appendix A (`app:proof`), U (`app:theory_details`), and V (`app:experimental_protocol`). No live master, data, experiment, bibliography or figure file was edited.

## Recommendation and guarded output

Apply the eleven replacements in `theory_proposals.json`. `build_theory_proposals.py` constructs them from exact frozen-source spans, verifies each span appears exactly once in each master, and verifies sequential application. No LNCS variant is needed: every owned old/new span is shared verbatim by the two formats.

The replacements remove 1,342 whitespace-delimited source words from U/V, taking 4,141 to 2,799 (32.4%). Appendix A's 177 words are unchanged. These are source-word counts, not a claim about rendered page savings. One auxiliary table and one redundant diagram also disappear. A final build is needed to measure the expected reduction from roughly nine owned pages toward six or seven. No font, table-size, margins or spacing settings change.

The parent explicitly selected retention of Proposition `prop:nearopt` and the onset corollary over the optional removal of that auxiliary strand. All six proof environments across the entire frozen manuscript are byte-identical after these proposals. In particular, the threshold statement and proof are untouched. The complete `app:real_sensor` source, from its subsection title to the next section, also remains byte-identical. The controller's mathematical proof from “Let $\\mathcal{F}_t$” through its closing limitation remains byte-identical, although its duplicate historical introduction is removed.

## Claim/proof map

| Claim | Necessary support retained | Cut or consolidation |
|---|---|---|
| Recursive reward-based EFE equals Planning+IG at weight one under the stated convention | Main formal statement/normalizer and information-unit derivation; complete Appendix A backward induction, terminal boundary and shared tie rule | U's repetition of reward normalization, units and alternative EFE scope becomes a short pointer |
| The observe-then-commit episode alternates paid observations and decisions until commitment | `fig:otc_loop`, caption and accessibility description unchanged | None; main text explicitly promises this schematic |
| Symmetric two-state one-observation onset and two-observation ceiling | Full `prop:nearopt` assumptions, nat units, finite-horizon distinction, perfect-sensing boundary and full proof unchanged | `tab:alpha_eta` and both paragraphs extrapolating across heuristic reductions are removed |
| Consistent discounting preserves the recursion while behavior may change | Displayed discounted recursion and explanation that continuation discounting need not increase sensing | Duplicate Diagnosis observation counts removed; own discount appendix retains the evidence |
| State-preserving observation/navigation yields the stated reduction | Full proof sketch, arbitrary-interleaving qualification, exploitation/payoff-conditioning exclusions and RockSample implementation detail | Generic application paragraph and duplicate posterior/value derivation removed |
| Destructive sensing can reverse the ranking under obsolete beliefs | Complete `ex:destructive` verbatim: observe-then-transition timing, both posteriors, infinite divergence branch, naive `2-c`, transition-aware `1-c`, realized `-c`, cost interval and test pointer | Redundant `fig:state_preservation` and introduction removed |
| The transition diagnostic is a boundary diagnostic, not a correction theorem | Transition-aware prescription; zero diagnostic does not prove preservation; no additive-value or decision-error bound; future-work scope | Remark no longer repeats the example's formula and numerical value |
| One-shot usage onset equals the analytic threshold | Complete onset proof unchanged; unit-test pointer plus zero-versus-at-least-one distinction for receding-horizon episodes | Unit-test numerical walkthrough and refined-grid experimental pointer removed |
| Projected decaying controller has stationary convergence and the scheduled average-usage limit | Full direct supermartingale, drift summation, separation contradiction, inactive-projection and Kronecker argument; stationary/single-crossing boundaries; no claim for constant-step or reset heuristic | Duplicate historical citations removed only from the appendix introduction; main retains attribution |
| Agent comparisons isolate objective/weight with documented tuning | Main Agents already specifies full objectives, tuned grid, counts, seed 7, tie rule, selection noise, reward versus success tuning and posterior-vote caveat; appendix retains implementation and domain-specific Greedy details | Four duplicate paragraphs become one short implementation paragraph |
| Sampled constrained references have a narrower policy class and an important RockSample limitation | Main positioning retains CPOMDP mixture scope/uncertainty, experiment-design relation and no calibration sample-efficiency claim; appendix retains failed 12-point RockSample diagnostic and producer | Six paragraphs repeating prior work and caveats are removed |
| Interleaved benchmarks are specified reproducibly and differ from original RockSample | Full RockSample six-difference paragraph, costs, rewards, sensor formula, step cap and hidden-state count convention; full Inspection parameter paragraph | Repeated Tiger cross-battery example removed |
| Recorded-sensor calibration has conditional within-period evidence and failed transfer | Entire frozen retrospective-sensor protocol unchanged, including adverse model behavior and all scope statements | None |

The sensor protocol intentionally remains relatively long because it supports the empirical extension rather than peripheral theory. It retains training/calibration/test splitting, exposure-dependence caveat, later batch counts, training-only transforms, seeds and k-means settings, smoothing, model misspecification, real encoded row reveals, acquisition equation, stopping/index/class tie rules, no reacquisition, both grids, subsidies, base-return scoring, equality/cap sampled LP distinction, selected crossings and monotonicity failure, all controls, analytic and realized mixtures, complete per-case archives, bootstrap reselection and pairing, coverage and all-target failure rule, conditional uncertainty, and CPU timing/memory/provenance.

## References and main-text repairs for the coordinator

Only two labels are removed: `tab:alpha_eta` and `fig:state_preservation`. All owned appendix labels and formal-result labels remain.

Required main repairs, outside this agent's owned spans:

1. At baseline JAIR line 228, remove the discussion of “tabulated comparisons,” Diagnosis/Tileworld heuristic reductions and the Testbed boundary. The table is no longer offered. Suggested replacement of that paragraph: “A two-state calculation separates the weight needed to buy a first observation at $H=1$ from the weight that buys an unnecessary second observation at $H=2$ (Proposition~\\ref{prop:nearopt}, Appendix~\\ref{app:theory_thresholds}). The first threshold is negative when observation is already strictly instrumentally worthwhile. The second bounds a near-optimality interval under the proposition's symmetric two-state assumptions. The interval is not a guarantee for longer receding-horizon episodes. Discounting preserves the algebraic equivalence when applied consistently to both recursions, with behavioral effects reported in Appendix~\\ref{app:discount}.”
2. At line 261, replace “Appendix~\\ref{app:theory_factored} gives the complete example and Figure~\\ref{fig:state_preservation}.” with “Appendix~\\ref{app:theory_factored} gives the complete calculation.” The substantive destructive-sensing claims remain supported verbatim.
3. At line 290, change the final pointer from “gives the full specifications and ablation interpretation” to “gives implementation details.” Baseline specifications/tuning remain in the same main section. Removal of IDS/PyMDP elsewhere is owned by the early reviewer/coordinator.
4. At line 439, replace the promise that `app:theory_positioning` “gives the detailed comparisons, including sequential experimental design” with “reports this RockSample diagnostic.” The main preceding paragraphs already contain the prior-art comparison.
5. At line 919, the early-appendix reviewer was informed that the Testbed `tab:alpha_eta` reference must go. They plan to retain the measured adverse result without the heuristic extrapolation.

No repair is needed for the main formal-equivalence scope pointer to `app:theory_setup`: it still hosts the diagram and now explicitly points to the main unit/normalization derivation and Related Work. The main onset proof/check pointer still resolves and accurately describes the retained proof and implementation distinction. If the late reviewer removes `sec:prop2exp`, this theory proposal already removes its one owned reference.

## Visual and integrity assessment

I inspected the existing full-resolution PNGs corresponding to the two figures. The OTC figure is legible, directly explains the episode structure and honors an explicit main-text promise, so it is retained unchanged. The destructive timeline is also legible, but its two branches exactly restate the immediately preceding example. Its removal is a substantive cut, not a visual-quality repair. The full example stays at its original length so readers do not need the removed diagram to follow the timing.

The threshold table is not needed to verify the threshold proof and does not support a general empirical explanation: three of its four domain rows fall outside the strict assumptions or use unproved reductions. Direct empirical evidence about the canonical weight remains in the main paper and relevant retained appendix results. Removing the table therefore reduces a peripheral interpretive strand rather than hiding a central adverse result.

Checks performed: exact old-span uniqueness in both frozen masters; successful sequential guarded replay; all six proof environments byte-identical; full sensor subsection byte-identical; unchanged Appendix A; removed-label inventory; inspected both schematic images. Source-count results are printed by the generator. The coordinator still needs to apply the proposals, repair external pointers, compile both masters, and inspect the changed page flow.
