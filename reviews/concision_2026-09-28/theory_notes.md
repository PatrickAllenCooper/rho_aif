# Theory and methodology concision proposal

Scope: replace the original JAIR source from `\section{Methodology}` through the end of Budgeted ρ-POMDPs, before `\section{Experiments}`. The baseline is commit `2d3bac4`. No master or figure producer was edited by this agent.

## Integration

- `theory_main.tex` is the replacement main-body chunk.
- `theory_appendix.tex` is one new appendix section, `app:theory_details`, with seven labeled subsections.
- Keep the existing equivalence proof at `app:proof`. It was not copied into the new appendix.
- Strip the JAIR-only `\Description` fields when mirroring to the LNCS master, following that master's convention.
- Some previously main-body labels now refer to appendix material. Rewrite prose references to the moved sections as necessary, without renaming those labels.

The main chunk contains approximately 5,570 whitespace-delimited source words, versus 16,842 before this pass. Another 7,636 words are retained in the new appendix. These are source counts, not PDF page estimates. The reduction removes repeated explanations of already-defined objects and moves derivations and extended qualifications. Every formal statement stays in the main text, so the main section is below the initial 7,000–8,500-word target without abbreviating hypotheses.

## Exact moves

1. **Observe-then-commit schematic (`fig:otc_loop`)** moves to `app:theory_setup`. The introductory engineering figure and the main definition already describe the loop. The appendix also retains the alternative-EFE-formulation scope, full reward-normalizer derivation, unit conversion, and nat-canonical comparison.
2. **Near-optimality proof and descriptive threshold table (`tab:alpha_eta`)** move to `app:theory_thresholds`, together with the full Tiger/Testbed/multistate scope discussion and discounting discussion. The complete proposition remains in main, followed immediately by its non-generalization caveats.
3. **Factored-state proof, destructive-sensing example (`ex:destructive`), diagram (`fig:state_preservation`), transition-aware remark (`rem:transition-aware`), and taxonomy (`tab:taxonomy`)** move to `app:theory_factored`. Main retains the full definition and proposition, posterior/diagnostic formulas, exact-preservation requirement, rewards-not-observations rule, support-dependent drift warning, and the limitation on interpreting the diagnostic.
4. **Extended agent explanations and tuning procedure** move to `app:theory_agents`. Main retains the agent table, receding-horizon protocol, critical baseline relationship, ablation action rule, posterior-vote naming correction, and actual tuning grids/seeds/episodes and selection criterion.
5. **Scale-equivariance, comparative-statics, and onset-corollary proofs** move to `app:theory_budget_proofs`. Their statements and interpretations remain in main. The numerical onset check follows its proof, with the single-decision versus receding-horizon episode distinction preserved.
6. **Controller proof and feedback schematic (`fig:dual_feedback`)** move to `app:theory_controller`, with the original implementation/default/reset descriptions. Main keeps the complete four-condition proposition, harmonic running-average conclusion, projected algorithm, all reported controller settings, and the unproved-default/reset caveats.
7. **Detailed prior-art comparisons and unsuccessful RockSample reference** move to `app:theory_positioning`. Main retains the central comparisons and the calibration-versus-optimality and no-sampling-saving limitations.

The target-versus-cap diagram (`fig:target_vs_cap`) and agent table (`tab:agents`) stay in main. No figure has been deleted from the complete manuscript, no table value has changed, and no empirical result file has been altered.

## Preserved rigor

- All nine original formal statements are byte-identical except the two pointers directing their proofs to appendices. This includes Proposition 2's perfect-sensing boundary, its sign-conditional reward claim, and its distinct horizons.
- PI-3 still separates the level set, population threshold, grid bracket, and endpoint mixture. It retains the closed enclosure, no-missed-crossings assumption, tolerance, non-straddling fallback, descending-curve counterexample, and attainability by arbitrary mixtures versus the selected mixture.
- Target calibration remains distinct from reward maximization under a cap. The information-floor multiplier is not the usage-cap multiplier. The floor-optimality statement explicitly requires an exact maximizer and nonnegative weight over a fixed class.
- Count and cost equivariance remain distinct. Grid brackets require rescaled grids. Directly tuned weights share the same equivariance. Floating-point equality is a measured claim rather than part of the theorem.
- PI-5 preserves all four hypotheses, interior crossing and separation, conditional mean/noise assumptions, weight-versus-pointwise-usage distinction, and harmonic-schedule running-average guarantee. The default and reset heuristic remain outside the theorem.
- EFE's reward convention, normalized-preference limitation, exact log-score case, bits/nats conversion, and specified-recursion scope remain adjacent to the equivalence in main.
- State preservation remains exact. Main defines the observation-before-transition timing and compares posteriors on the same hidden-state space. Exploitation rewards are not conditioned on. Δ_T remains a diagnostic rather than a correction or error bound.
- The reference-policy sentence distinguishes selection as feasible from simulated usage estimates from a certified population-feasibility or optimum guarantee, following the independent critic's recommendation.

## Audit and outstanding integration checks

`python3 reviews/concision_2026-09-28/audit_theory_chunks.py` checks the baseline against the proposed chunks. It passes: all 34 old labels occur exactly once; all 26 citation keys survive; no new reference is unresolved relative to the full baseline plus the new chunks; all nine statements match apart from the two proof pointers.

The independent concision critic read the complete new main chunk. It found no strengthening of the normalizer, exact-optimizer, equivariance, or theorem-scope claims. Its one suggested precision correction, feasibility from simulated usage, was applied.

Root still needs to compile the integrated masters, inspect floats and page count, reconcile numbered proposition references embedded in figure artwork, and run the repository's claim checker. Moving the destructive example and remark changes the shared theorem counter before the budget results, even though their label-based references remain valid. The root's global Section/Appendix reference audit must include newly relocated `tab:alpha_eta`, `ex:destructive`, and `rem:transition-aware`. No claim is made here about final rendered length or completed full-manuscript validation.

## Selective main-text restoration after the first compiled measurement

The root's first integrated compile placed references on page 28, leaving room to restore useful arguments and a worked boundary case while approaching the requested 40-page body. The approved restoration is supplied as **`theory_main_restored.tex` and `theory_appendix_restored.tex`**. Use this pair instead of the initial pair. The preparation script is `restore_theory_evidence.py`.

The complete destructive-sensing example (`ex:destructive`) and state timeline (`fig:state_preservation`) now appear in main immediately after the factored-observation scope statement. This restores a concrete calculation showing why preservation matters. The short scale-equivariance and comparative-statics proofs now appear directly under their propositions. All four blocks were removed from the appendix, not copied. The full transition-aware remark, taxonomy, near-optimality proof/table, and controller proof remain appended.

The selected restoration adds 688 source words and one figure to main (6,256 main / 6,939 appendix). Its final page effect must be measured by compilation. The main statements and all hypotheses remain unchanged. `audit_theory_chunks.py --restored` passes the same label, citation, and statement checks.

Integration notes for root:

- Main now refers directly to Example `ex:destructive` rather than describing it as appended. The discussion's pointer should distinguish this main example from the full scope discussion in `app:theory_details` or `app:theory_factored`.
- PI-1/PI-2 no longer point to the appendix for their proofs. The `app:theory_budget_proofs` subsection now contains only the onset corollary proof and numerical check and is retitled accordingly.
- The example returns to its original position before the budget results, but the transition-aware remark remains appended. Shared theorem numbers therefore still require checking against figure artwork.
- Global Section/Appendix reference rewriting from the integrated master must be applied to the new chunks just as it was to the first pair (for example the empirical staircase section is now appended).
