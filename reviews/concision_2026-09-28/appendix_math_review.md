# Final appendix mathematics and notation review

Decision: **ACCEPT** for the assembled sources reviewed below. No required mathematical-consistency correction remains in my assigned appendix scope.

This is an independent manuscript review, not a guarantee of a journal decision. The earlier preservation review in `final_critic_review.md` covers the scientific argument and evidence retained during shortening. This addendum covers the user's subsequent request for consistent mathematical notation and correct rendering, including the changes made after that review.

## Corrections verified in both assembled masters

- Information weights and observation thresholds now use reward units per nat, while the information-to-cost ratio uses nats per reward unit. The threshold table distinguishes those analytic units from the empirical reward-per-bit weight column. The numerical conversions are unchanged.
- The reward-relevant information-gain formula now averages the posterior-to-prior KL divergence over prospective observations and explicitly conditions both distributions on the current belief. Its explanatory sentence also says expected divergence.
- The cap-reference percentage gap explicitly uses the absolute reference reward in its denominator. The recovery estimand defines `T` as the zero-based start of the first qualifying hold, matching the runner, rather than the completion of that hold.
- Both empirical near-optimality descriptions now use `max(0.05 |R_best|, 0.5)` in reward units, with `R_best` defined as the best estimated grid mean. This matches `experiments/run_nearopt_horizon.py` lines 94–98. The locally selected empirical weight uses the reward-optimum subscript.
- The factorization appendix separates observation likelihoods from terminal rewards. State preservation is the structural hypothesis; a nonzero transition diagnostic witnesses its failure, while zero alone does not prove preservation. The taxonomy no longer asserts a converse through its column headings.
- Proper-scoring formulas use natural logarithms and define the true-state symbol. The text now distinguishes categorical OTC scores from Inspection's average across component-wise binary scores and states the numerical probability floor. This was verified against `rho_aif/scoring.py` lines 16–69 and the actual caller in `rho_aif/benchmark.py` lines 330–331. No score or table value changed.
- The revised equivalence proof carries depth through the action values, uses the terminal boundary explicitly, and points to the commit equation for terminal actions. The onset proof and proper-score expression render the indicator with a supported glyph. The companion theory review verifies the main declarations and the destructive-example reward units.

The implementation of my proposed corrections is retained in `appendix_notation_fixes.py`. It uses exact occurrence guards and was tested as a pure source transformation on both masters before integration. It does not modify a legacy copy.

## Mathematical checks

I reread the equivalence induction, the two-state threshold derivation and its stated scope, the state-preservation proof and transition-aware remark, the onset proof, the projected-controller supermartingale and running-average arguments, the IDS information ratio, the reward-rescaling identities, and the empirical score/gap definitions. The signs, information units, horizon/depth roles, and proof-to-statement links are consistent within the reviewed scope. All source labels remain unique in both masters.

The finite-grid and Monte Carlo caveats remain in place. The cap envelope is still a reference estimated from sampled policies, not a certified population bound. Calibration of expected usage is not presented as reward optimality, and controller convergence remains conditional on the stated stationary sign-crossing assumptions. The additional notation work did not strengthen those claims.

## Render checks

I rendered and visually inspected JAIR PDF pages 40, 63, 75, 80, and 98, and LNCS pages 54, 82, 94, 100, and 122. These include the explicit-depth equivalence proof, proper scores and indicator glyph, analytic threshold units, controller inequality, and corrected expected-information-gain formula. In these samples, equations are legible and stay within the text area; subscripts, superscripts, operators, indicator glyphs, and mathematical delimiters render correctly. The render images are saved in `math_render_checks/`.

This is a targeted visual check of the mathematical appendix changes, not a claim that I personally viewed every PDF page. The root and evidence reviewer own the final full-layout/build validation.

## Reviewed artifact identities

- JAIR source SHA-256: `4b498b252df9fde799733bc083f1b2e8626a1a2d2ebeb4aa74699c3e22177f66`
- LNCS source SHA-256: `d08dfbe711b2bbd07dd7006d11e5eb5a81f9f808da67ef66da069f320bca34e8`
- JAIR PDF SHA-256 when rendered: `a2c4451830f16ffb0cb4b9c4bb0e61eefe29dbaa297db6af91f9338f81bd0519`
- LNCS PDF SHA-256 when rendered: `2ce56aff91629fbe4fcb17cc2c0c750b0e41dc7aa524db6d717316ded9d5a58a`

Any subsequent layout-only rebuild can change PDF hashes without changing this source-level judgment. A substantive source change requires checking its effect before reusing this acceptance.

## Final source-hash addendum

After the review above, the destructive-sensing example removed the parenthetical claim that its symmetric-reward testbed was an instance of Proposition 3.2 (whose strict reward-asymmetry hypothesis it does not satisfy). I verified computationally that restoring only that deleted parenthetical reproduces each previously reviewed source hash exactly. This is therefore the sole subsequent source change, and it correctly narrows a cross-reference without changing the example or its mathematics. **ACCEPT remains the final decision**, with no required correction outstanding, on these final sources:

- JAIR: `7d68bf1679830172b0075be57bd7bbcc3f2c0c8b4b9082de4ff67aaf8f4a19f8`
- LNCS: `53262fbeaddab80f9d70d87df81595917c76e8cbfa363bedce5fd3c654293b9b`
