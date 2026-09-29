# Empirical mathematics and final LNCS layout review

Scope: empirical main text and empirical appendices, including usage/cost units, target notation, uncertainty, recovery estimands, constrained-reference mixtures, and rendering of the LNCS paragraphs flagged in the earlier audit. Formal theorem/proof and other supplementary mathematics are reviewed by the other assigned agents.

## Rendering result

The rebuilt `/tmp/rho_layout_lncs.log` and `/tmp/rho_layout_jair2.log` contain no overfull-box, missing-glyph, or undefined-reference warnings. I regenerated LNCS line coordinates and inspected fresh renders of pages 12, 19, 23, 53, 77, 91, 114, 126, and 135. The previous mathematical, filename, and grid spills are resolved. Equations and subscripts remain legible, the long grids wrap without losing entries, and there is no clipping or overlap. The LNCS output remains 153 pages. No font or margin reduction was needed. A 2pt-scale optical protrusion on the line ending `scipy.` is not an overfull box and does not impair the page.

## Empirical notation findings

Five local corrections were reported to root for the requested mathematics consistency pass:

1. The detailed distractor appendix writes an outcome-specific KL divergence as the expected information gain `\tilde I_a(b)`. This is an inherited omission of the expectation over future observations. `rho_aif/agents/planning_infogain.py`, method `_expected_value_of_observe`, computes the posterior entropy weighted by `prob_obs` at every outcome. The correct equation is
   `\tilde{I}_a(b) = \mathbb{E}_{o\mid b,a} D_{\mathrm{KL}}[Q(s_{\mathrm{rel}}\mid o,b,a)\|Q(s_{\mathrm{rel}}\mid b,a)]`.
   The following prose should likewise say “expected divergence.” This aligns notation with the existing implementation and main expected-IG definition, with no numerical result change.
2. The endogenous CPOMDP table explicitly defines its raw gap as reference minus EFE, but does not define its percentage denominator. `experiments/run_cpomdp_baseline.py:241` uses `100*gap/abs(ref)`. Its caption should state that formula, particularly because Diagnosis has a negative reference reward. The frontier table's opposite sign, mixture minus reference, is already explicitly defined and is internally consistent.
3. The concise recovery paragraph uses `min(T,180)` while defining T only implicitly through the preceding recovery criterion. It should explicitly identify T as the number of post-rescale episodes to recovery. The precise runner convention is the zero-based start index of the first qualifying hold, with 180 the last admissible start. The appendix already distinguishes recovery from censoring. This also avoids confusion with the transition kernel T used elsewhere.

4. The near-optimality tolerance is written as `max(5%,0.5)` in two appendix passages. This compares incompatible units. `experiments/run_nearopt_horizon.py:94–98` uses `gap <= max(0.05*abs(best_reward),0.5)`. The corrected mathematical statement must define the grid-estimated best mean reward and identify 0.5 as reward units. No measured value or criterion changes.
5. The proper-scoring appendix gives categorical joint-state formulas without stating that Structural Inspection uses mean component-level binary scores. `rho_aif/benchmark.py:330–331` calls `factored_log_score` and `factored_brier_score`, whose definitions in `rho_aif/scoring.py:46–69` average the binary scores across components. The implementation also floors the probability used in the natural-log score at 1e-12. These are reporting qualifications, not new scores or numerical changes.

## Other consistency checks

- Count usage `U_count`, cost usage `U_cost`, count targets B, and cost targets `B_cost` are explicitly separated. The ratio in the heterogeneous-cost figure is a ratio of means and has no unsupported uncertainty estimate.
- The scale experiment changes both reward/cost and information weight by the same alpha. It uses count usage, so normalized collapse does not incorrectly apply the count identity to unnormalized monetary cost.
- `B_EFE` denotes the implicit usage of weight one and is distinct from the calibration-derived targets.
- The controller comparison uses the common restricted recovery estimand for all ten seeds. Its paired t interval, descriptive ratio of means, conditional recovered-only summaries, normal-approximation intervals, and median/interquartile trajectory bands are not conflated.
- Main uncertainty is seed-level SE. TOST uses a 90% difference interval at alpha=0.05. Frontier intervals are nominal pointwise fitted-reference summaries and do not claim support-selection, mixture-weight, feasibility, or multiplicity coverage.
- Endpoint probability q selects the upper bracket endpoint, whereas the target-optimal and cap-feasible LP mixtures can select different weights. The code/reference convention and the Bandit counterexample remain consistent.
- Usage brackets measure grid resolution, not sampling confidence. The nearest plotted grid solution `\hat w(B)` is explicitly distinguished from the population crossing `w^*(B)`.
- The LP reference caps are at-most constraints. Negative endogenous estimated gaps, slack caps, same-stream fitting, and Tiger rare-event uncertainty are all disclosed. No interpolated equal-usage reference is substituted for the feasible envelope.
- N and K are locally defined for each environment (conditions, grid side, components, tests, or arms) rather than asserted to denote one universal count. The symbols' different domain roles do not create contradictory mathematical equations.

This review was read-only. All five reported corrections are now verified in both assembled sources, together with the companion expected-divergence prose and generated proper-scoring table caption. The correction module uses guarded replacements, and no empirical data or numeric table cells changed.


## Final closure — ACCEPT

The final builds in `/tmp/rho_math_jair2.log` and `/tmp/rho_math_lncs.log` complete successfully with no overfull boxes, missing characters, undefined references, or TeX errors. The outputs are 117 JAIR pages and 155 LNCS pages. Fresh rendered inspections cover LNCS pages 24 (scale and recovery), 34 (cap-reference percentage), 82 (component-level proper scoring), 122 (expected information-gain equation), and 139 (near-optimality criterion), plus JAIR page 63 (proper scoring and indicator rendering). Each inspected expression is complete, legible, and inside its text area.

I give an unqualified ACCEPT for the empirical notation and rendering changes in this review scope. This is an internal revision assessment, not a journal decision or a claim that every experiment was rerun. The broader theoretical/supplementary proof audit is assigned to the other panel reviewers.

Verified SHA-256 values:

- `paper/full_paper_jair.tex`: `4b498b252df9fde799733bc083f1b2e8626a1a2d2ebeb4aa74699c3e22177f66`
- `paper/full_paper.tex`: `d08dfbe711b2bbd07dd7006d11e5eb5a81f9f808da67ef66da069f320bca34e8`
- `paper/full_paper_jair.pdf`: `a2c4451830f16ffb0cb4b9c4bb0e61eefe29dbaa297db6af91f9338f81bd0519`
- `paper/full_paper.pdf`: `2ce56aff91629fbe4fcb17cc2c0c750b0e41dc7aa524db6d717316ded9d5a58a`


## Final source addendum — ACCEPT

The final source differs from the accepted version only by deletion of the destructive-example parenthetical `(the Proposition~\ref{prop:nearopt} testbed)`. I verified this exactly by restoring that phrase in memory and reproducing both previously accepted source SHA-256 hashes. This accurately removes an association with a proposition whose strict reward-asymmetry hypothesis is not satisfied by the example's symmetric ±1 rewards. No empirical statement, result, or formula changes. My ACCEPT remains in force. Final build logs `/tmp/rho_final_jair2.log` and `/tmp/rho_final_lncs.log` again contain no overfull boxes, missing characters, undefined references, or TeX errors.

- `paper/full_paper_jair.tex`: `7d68bf1679830172b0075be57bd7bbcc3f2c0c8b4b9082de4ff67aaf8f4a19f8`
- `paper/full_paper.tex`: `53262fbeaddab80f9d70d87df81595917c76e8cbfa363bedce5fd3c654293b9b`
