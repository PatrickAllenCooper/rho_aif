# Independent final theory review, round 1

Date: 2026-09-28. Reviewed revision: `c211422` (clean HEAD at assignment).
Reviewer lens: theoretical soundness, notation, attribution, scope, and exposition.

**Verdict: MINOR REVISIONS.** The main results survive this audit. Four local correction groups below are required before I can give an unqualified accept. None requires a new experiment, a changed headline result, a new benchmark, or a different title. In particular, the newly added harmonic-schedule running-average result is mathematically sound.

## Scope and independence

I read `AGENTS.md`, the September 28 handoff, the relevant 9.17.48–9.17.50 ledger entries, the manuscript's main theory (Sections 3 and 4), its introduction and related-work positioning, the conclusion and relevant Discussion passages, the equivalence-proof appendix, and the proper-scoring appendix. I inspected the manuscript diff from `9e2666d`, the scale-comparison implementation in `planning_infogain.py` and `efe.py`, `scoring.py`, and all three citation-audit slices plus their bibliography crosscheck. Prior acceptance votes were not treated as evidence. I have not read the other member of this two-agent panel's review or received its findings.

This is not an exhaustive independent re-verification of all 69 bibliography entries, every experiment, or every manuscript number. I checked primary-source material for the critical stochastic-approximation attribution, the proper-scoring distinction, SAC's automatic-temperature update, and the recent Bethe-information-constraint comparison. The original Robbins–Monro paper was available in full. Project Euclid's Blum and Bernardo endpoints returned access/challenge pages, so I do not claim to have independently read those full papers in this round. I independently derive the mathematical convergence conclusion below rather than treating unavailable source text as verified. No manuscript, code, or experiment artifact was edited by this reviewer.

The root reviewer separately asked me to examine a README belief-reporting assertion. That is the only externally prompted finding in this report, and I checked its content and propagation independently. It is not a finding supplied by the other panel member.

## Required corrections

### R1. Correct the direct attribution of PI-5's current hypotheses to Robbins–Monro

Location: `paper/full_paper_jair.tex:497` and especially `:500`, with the same correction in the long master. Confidence: high. Severity: minor, attribution/proof presentation, not a false convergence result.

The proof says that conditions (iii) and (iv) are the sign and separation conditions imposed directly by Robbins and Monro (1951), and presents the whole proof as a mapping onto the cited theorems. The original source does permit a discontinuous regression function and does not require equality at the crossing in its first result. But it does **not** state the general annulus-separation hypothesis now used here as its convergence theorem. Its Theorem 1 (p. 404) assumes a uniform positive separation from the target on both sides, condition (5'), and a step sequence of its specified “type 1/n.” Its Theorem 2 (pp. 404–405) instead assumes nondecreasing M, equality at the root, and a strictly positive derivative there. On p. 405, weakening its hypotheses toward the sign-only condition is discussed as a possible extension. The manuscript's condition (iv) is the later, weaker local-annulus condition, rather than the hypotheses of those original theorems.

Concrete distinction: on `[0,2]`, let `w*=1`, `B=1`, and `U(w)=1+(w-1)^3`. This satisfies the manuscript's sign and annular separation conditions but not the original Theorem 1's uniform gap or Theorem 2's positive derivative. Thus the current sentence cannot literally be justified by the original theorem even though the desired conclusion is true.

Primary source inspected: [Robbins and Monro, A Stochastic Approximation Method, pp. 400–407](https://oa.ee.tsinghua.edu.cn/~ouzhijian/pgm/pgm-pdf/Robbins%26Monro1951_a%20stochastic%20approximation%20method.pdf), especially pp. 401, 404, and 405. The citation audit's slice C labels this exact sign/separation attribution appropriate without documenting the theorem-level comparison. That blanket finding should receive a dated correction or addendum rather than remaining the final word.

A straightforward repair is to retain Robbins–Monro as the origin of the recursion, identify Blum as the classical almost-sure extension without claiming that the current hypotheses are literally those in Robbins–Monro, and give the short direct argument for this bounded projected scalar case. For example, writing `e_t=w_t-w*`, `M(w)=U(w)-B`, and `F_t` for the history, bounded usage and projection non-expansiveness give

`E[e_{t+1}^2 | F_t] <= e_t^2 - 2 a_t e_t M(w_t) + C a_t^2`.

Here `e_t M(w_t)>=0`, including when `w_t=w*` although `M(w*)` need not vanish. Consequently `e_t^2 + C sum_{k>=t} a_k^2` is a nonnegative supermartingale. It converges almost surely and the sum of the nonnegative drift terms is finite. If the limiting squared error were positive, compactness plus condition (iv) would bound `e_t M(w_t)` away from zero eventually, contradicting `sum a_t=infinity`. Hence `e_t -> 0` almost surely. This proof also directly handles the jump and projection, with no continuity assumption or appeal to a continuous projected ODE at a discontinuity.

The newly added Kronecker step after convergence is correct and should be retained.

### R2. Qualify the universal constant-step nonconvergence sentence

Location: `paper/full_paper_jair.tex:500`, sentence beginning “Under a constant step.” Confidence: high. Severity: minor.

The sentence says the recursion does not converge to a point under a constant step. That is not true without a nondegeneracy assumption on the noise or a restriction to gap budgets. A bounded, deterministic counterexample even uses a staircase: take `w_max=2`, `B=1`, `U(w)=0` below 1, `U(1)=1`, and `U(w)=2` above 1. With constant step `a=1/2` and `w_0=1/2`, the recursion moves to 1 and remains there forever. It satisfies the single-crossing and separation assumptions, has bounded per-episode usage, and converges to a point.

Change the statement to “need not converge to a point” (or explicitly condition a persistent-fluctuation claim on nonvanishing noise). The following paragraph already labels the neighborhood/tracking discussion as intuition rather than a proved result, so no additional theory is needed.

### R3. State the positive correct-reward hypothesis used by Proposition 2

Location: `paper/full_paper_jair.tex:235` and `:241`. Confidence: high. Severity: minor.

The proposition assumes `R^-<0` and `|R^-|>R^+`, but never states `R^+>0`, even though it defines `alpha=|R^-|/R^+` and rearranges an inequality by dividing by `(p-1/2)R^+`. The superscript “+” names the correct outcome but is not a mathematical sign hypothesis, particularly since the wrong reward's negative sign is specified explicitly.

At `R^+=0` the ratio is undefined while the written hypotheses hold. A strict counterexample to the claimed negative-threshold condition is `p=3/4`, `c=1/2`, `R^+=-1`, `R^-=-2`. The written assumptions hold and `alpha=-2 > -3 = c/[(p-1/2)R^+]-1`, but the threshold numerator is `1/2-(1/4)(1)=1/4>0`, so the threshold is positive, not negative.

The intended and sufficient fix is just “correct reward `R^+>0`.” All tabulated applications already have positive correct rewards. The closed forms and experimental findings need no change.

### R4. Separate proper belief reporting, belief quality, and action-selection weights

Locations: `README.md:73`; `rho_aif/scoring.py:3–5`; `paper/full_paper_jair.tex:1688` and `:1692`, with corresponding manuscript propagation. Confidence: high. Severity: minor.

The README asserts that under log scoring EFE at `w=1` is the theoretically correct belief reporter, attributed to Bernardo. The identical assertion appears in the `scoring.py` module docstring. Properness makes truthful reporting of the conditional distribution optimal given the information available. It does not select an action-planning coefficient. A reward-only planner and an EFE planner that both update the same exact Bayesian model both report their correct conditional posteriors, despite collecting different amounts of information. The root's proposed replacement with a narrow description of the log/Brier belief-quality metrics is justified, and it should include the module docstring.

The manuscript appendix makes a related, smaller terminology error. Line 1688 says a well-calibrated posterior should assign more mass in expectation to the state that turns out true, and line 1692 calls a proper-score improvement “calibration-dominated” and refers to SARSOP's “near-optimal calibration.” Proper scores assess overall predictive quality, and their improvement does not isolate calibration. A uniform posterior before any observation and an exact point-mass posterior after a perfect observation are both calibrated, although the latter has better expected log and Brier scores. Their difference is information/sharpness, not necessarily calibration. Indeed, the appendix's eventual conclusion, “better-informed terminal beliefs,” is the appropriate claim.

Use “better-informed” or “higher-quality terminal beliefs” in the first passage, “dominated on both terminal-belief scores” in the second, and “terminal-belief scores” for the SARSOP comparison. No numerical analysis changes. Renaming the appendix title is optional, since “proper-scoring calibration” can serve as a conventional study label if the text makes clear what was measured.

Primary source inspected: [Gneiting and Raftery (2007), Strictly Proper Scoring Rules, Prediction, and Estimation](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jasa.pdf), p. 359, which defines strict propriety and distinguishes sharpness from calibration. The manuscript already cites this source, so a new bibliography entry is unnecessary.

## Findings that passed

- **PI-5 conclusion and running average.** The four conditions do imply almost-sure convergence of the projected scalar iterates, including a discontinuous single crossing; the direct argument in R1 verifies it. The added harmonic running-average proof is valid. Interior convergence and bounded usage eventually remove projection. The tail series `sum a_t(B-U_t)` then converges by telescoping. Applying Kronecker with denominator `1/a_t` yields `a_n sum_{t<n}(B-U_t)->0`; since `n a_n -> eta_0/delta>0`, ordinary average observed usage tends to B. This makes no false claim that `U(w_t)` converges pointwise to B across a jump. Reset-on-shift and nonstationarity are appropriately outside the theorem.
- **Scale equivariance.** The induction and homogeneous comparison tolerance preserve candidate order under simultaneous positive reward/cost/weight scaling. The manuscript distinguishes real-arithmetic identity from floating-point rounding. The revised price-versus-grid language is correct: the population threshold transforms without a grid hypothesis, the reported grid bracket only under a correspondingly scaled grid, and a fixed cost budget requires comparison to `B/alpha` rather than B on the base curve.
- **Threshold/level set/bracket/mixture separation.** Definition PI-3 now distinguishes all four correctly. The closed-enclosure qualification handles a threshold at the half-open bracket's excluded lower endpoint. The missed-crossing and no-upcrossing qualifications are necessary and present. A budget attainable by arbitrary mixing need not admit the particular last-upcrossing endpoint construction; the descending-curve counterexample is acknowledged.
- **PI-2 and information floor.** Adding the two optimality inequalities proves information is nondecreasing with w and reward nonincreasing for a fixed set of exact maximizers. The paper correctly does not infer monotone observation counts or claim the same trajectory-level property for receding-horizon replanning. The floor-optimality argument at `I(pi_w)` is valid for `w>=0`; the operational price is explicitly not the usage-cap multiplier.
- **EFE equivalence and normalization scope.** Negation of the adopted reward-based recursion does give the stated Bellman recursion, with the same horizon and terminal convention. The normalized-preference caveat for variable-length paths is explicit. Bits-versus-nats and the corresponding implementation weight `ln 2` are stated. The factored extension is confined to hidden-state-preserving observation/navigation actions. Destructive sensing and infinite divergence under tiny support-changing drift are handled with the necessary support caveat, and the coupling divergence is not advertised as an error bound.
- **Primary-source checks of close prior art.** [SAC Algorithms and Applications](https://arxiv.org/html/1812.05905v2), Section 5 / Equation 17, supports the automatic-temperature dual-gradient-descent attribution, with the correct applications paper cited. [Kouw's Bethe-information-constraint paper](https://arxiv.org/html/2608.17167v1), Section 3 and Lemma 2, supports the information-floor/KKT comparison and the distinguished unit multiplier. The paper appropriately keeps that internal information constraint distinct from its own operational sensing-usage target.
- **Claim scope.** The abstract/conclusion retain the gap between usage calibration and constrained reward maximization, the same-stream frontier selection caveat, the Tiger rare-event caveat, the empirical character of re-adaptation, and the lack of universal or scale-free optimality of `w=1`. I have no title, length, or new-benchmark condition.

## Acceptance path

Apply the four local groups, propagate manuscript corrections to both live masters, and let this reviewer inspect the actual revised text. A direct PI-5 proof should receive particular attention for filtration, projection, and the summable-error supermartingale step. I expect these local corrections to be sufficient, but an unqualified acceptance vote is reserved until I have verified the revision.
