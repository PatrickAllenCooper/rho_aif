# Independent theory and reproducibility audit

Date: 2026-10-02. Baseline: `c5125abf3f4467271a414661ccca4741645d9161`.

**Decision: ACCEPT. No required revisions remain within this review's scope.**

I independently reviewed all 25 proposed theory edits, the full checklist replacement, the actual resulting sources in both formats, and their baseline counterparts. I did not use previous acceptance decisions as evidence. This is an audit of the appendix consolidation and the mathematical/reproducibility claims it changes, not a fresh re-execution of every experiment or a prediction of JAIR's editorial decision.

## Preservation and mathematical completeness

Both source prefixes before `\appendix` are byte-identical to the baseline. All six proof environments remain in each master. Only the two-state threshold proof changes; the five other proof environments are identical. The controller's direct supermartingale and running-average argument, although not in a proof environment, also remains substantively complete. All six archived artifact hashes match the legacy manifest, so the prior sources, PDFs, bibliography and Overleaf archive are recoverable unchanged.

The shorter distractor argument gives the Bayes factorization explicitly. Summing over the nuisance factor leaves the condition marginal unchanged, conditional on the factored prior and the single-factor likelihood. The symmetric claim, no reward observations, and exclusion of correlated beliefs survive. This is a clearer proof than the repeated verbal account.

The threshold proposition retains the uniform two-state model, positive cost, reward signs and strict asymmetry, information in nats, distinct one-observation and two-observation horizons, and the perfect-sensing boundary. The new proof correctly computes the first observation's advantage as `(p-1/2)(R+ - R-) - c + w I_max`. After one observation, the confirming and disconfirming branches have expected posterior maximum `p² + p(1-p) = p`, so the second observation has zero instrumental value. I independently checked this identity over 999 sensor accuracies, with maximum floating-point residual 1.11e-16. The resulting `c/I(b)` ceiling and stated loss when immediate commitment is preferable follow. The text explicitly restricts the interval to the stated horizons, excludes perfect sensing from the upper ratio, identifies Testbed as a boundary case, and keeps Diagnosis/Tileworld reductions heuristic. Nat versus bit units remain explicit in the table and surrounding interpretation.

The destructive-sensing example retains the observe-then-transition timing, the obsolete posterior, the correct post-transition posterior, the infinite divergence on the report-1 branch, and all three distinct quantities: naive value `2-c`, transition-aware value `1-c`, and realized return `-c` from acting on the obsolete report. The action-ranking reversal for `1<c<2` is intact. The shortened remark does not turn the diagnostic into an additive correction or a decision-error bound. The proof of state-preserving interleaving still excludes arbitrary exploitation transitions and states the no-payoff-conditioning restriction.

The scope consolidation keeps the distinction between an exact log-score case, a conditional reward-based recursion, and the implementation's reward-per-bit convention. The full normalizer derivation remains in the unchanged main text. No alternative EFE formulation acquires an unsupported equivalence claim. The controller's stationarity, martingale-noise, single-crossing and separation hypotheses remain in its unchanged proposition, and the appendix continues to exclude the constant-step default and reset heuristic. The running-average argument retains the particular decaying schedule it needs. The shortened positioning text preserves the distinction between an information weight and a usage-cap multiplier, the sampled and noisy reference envelope, the narrower episode-mixture policy family, and the lack of computational savings from offline calibration.

## Checklist and reproducibility

Every checklist question and response category remains, including all three `Partially` answers. The revision does not turn incomplete simulation trajectories into a claim of complete raw-data coverage. It distinguishes the archived dual/TOST/frontier/usage records from other regenerable aggregates, and the complete sensor candidate/model/split/selection/bootstrap archives from the externally obtained UCI measurements. The generated-data license remains distinct from the source-data terms.

I checked the shortened seed descriptions against `ENVIRONMENT.md`, `rho_aif/benchmark.py`, the SARSOP/TOST/CPOMDP runners, the horizon-map code, POMCP main and exploration runs, the compute-matched and MCTS scripts, and the sensor analysis. The per-episode versus once-per-stream distinction remains correct, as do the explicit episode-seeded TOST mode and the fixed internal planner-seed exceptions. The canonical, tuning, held-out and fresh-seed sets are retained or pointed to where their battery is reported. Sensor bootstrap draws remain conditional case resamples rather than independent fitted-model repetitions. CPU-only execution, environment pinning and processor-dependent numerical reproduction are retained.

## Issues discovered and verified resolved

1. Removing the observe-then-commit schematic left the unchanged main text promising it. The final source restores the figure in both masters and records theory-06 as declined. This resolves the false pointer while preserving the main text byte-for-byte.
2. The shortened seeding sentence initially omitted the meanings of `s` and `i` in `10^4 s+i`. The final checklist restores outer seed and episode index explicitly.
3. As optional layout polish, the redundant final sentence about the three inline `Partially` explanations was removed. The explanations themselves remain.

## Clarity and visual assessment

The consolidation removes repeated scope defenses and duplicate walkthroughs while retaining the information needed to follow the equations. The explicit threshold proof and Bayes identity improve auditability. I inspected rendered JAIR pages 56, 58–59, 62 and 78–81 at the intermediate post-correction build, including the added factorization, threshold proof, destructive example, controller argument and checklist. Mathematics, tables and text were legible and unclipped. The last two checklist lines initially occupied a nearly empty final page; the optional deletion above addresses that layout issue. Final build/package checks are separately owned by the coordinating agent.

The retained theory is modest in scope but internally coherent. I find no mathematical or disclosure regression that warrants withholding acceptance of this revision. Future strengthening of operational validation or planning breadth is not a required condition for this bounded manuscript.

## Exact audited source hashes

- `paper/full_paper_jair.tex`: `a62650127b1914aebe7929ffe7d579c40759433873f6a704957b4739b4b2568a`
- `paper/full_paper.tex`: `f777cdce6bd684eb9cb49587255bccd42bc2fcef60aa7427e23e553b8a88a60a`

Machine-readable preservation checks are in `independent_theory_snapshot.json`.

## Final build confirmation

The final source hashes above include the restored producer comments above the compact effect-size and discount tables. These comments do not alter rendered content. The final JAIR PDF is 80 pages and the LNCS companion is 101 pages. I inspected the final JAIR checklist pages 79–80 and confirmed the explicit outer-seed/episode-index definition, complete final paragraph, and removal of the nearly empty page. Earlier inspected mathematical pages retain their content and layout. No visual defect remains in the inspected pages. This review does not independently certify the separate Overleaf ZIP.

- `paper/full_paper_jair.pdf`: `2115da07825e839bdba0e0235a687a35d7dec923a1b06160d373cc5068cb3286`
- `paper/full_paper.pdf`: `4ce73cb7d6c51d476c64d96f8a348be014fc5df6dbc9c2f2d530568b24fd418f`
