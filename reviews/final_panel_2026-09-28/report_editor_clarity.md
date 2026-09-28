# Report, lens `editor_clarity` (JAIR associate editor)

Manuscript: `paper/full_paper_jair.tex` (1872 lines, 112 pp as built; main text through the Conclusion ends on printed page 74, appendices A to U follow). Read in full, including every appendix, every `\input` table under `paper/tables/`, and all 20 included figures, opened as PNG and checked against caption and `\Description`. The PNG of `fig_obs_scaling` is older than its PDF, so I also rendered the PDF. The two are identical in content.

## 1. Recommendation

Accept with minor revisions.

## 2. Summary

The article argues that the weight on an information-gain utility in a rho-POMDP is best treated as the operational shadow price of a stated sensing budget, estimated from a simulated usage curve. The weight is reported as a grid crossing bracket, attained inside usage gaps by an endpoint mixture, and adjusted online by a projected decaying-step dual controller. The price is exactly scale equivariant for the receding-horizon planner (Proposition 4.2). The article also shows that minimizing the reward-based recursive EFE objective it specifies is exactly a rho-POMDP with information-gain weight w=1, which makes active inference's weight one canonical, untuned point on that price curve. The empirical program is broad: observe-then-commit benchmarks, a cost-modified RockSample, Structural Inspection, and SARSOP and Lagrangian-SARSOP references, with TOST equivalence tests and a predeclared held-out budget study. The contribution is real and fits JAIR. The claims are carefully calibrated, and every number I checked against the committed CSVs matches. What stands between this version and acceptance is small. One symbol, w*(B), denotes three different objects. One figure caption contradicts its figure. The lead figure writes the EFE decomposition with the wrong sign relative to Eq. 2. And the abstract's headline "eleven of the twelve" count depends on a rare-event outcome in the Tiger held-out stream that the text does not disclose. The article is also very long for its contribution. That is not blocking, but it is the most valuable optional change.

## 3. Strengths

- A clear, useful reframing. Replacing a hand-tuned weight with a designer-stated expected sensing budget is a practical idea, and the article is candid that this is calibration within a policy family, not constrained-POMDP optimization. The held-out budget study (Section 6.9) quantifies that difference instead of just asserting it.
- Claim calibration is unusually disciplined. SARSOP and CPOMDP references are called near-optimal and estimated throughout. Proposition 4.5 is limited to stationary convergence, and the reset-on-shift variant is explicitly placed outside it. w is repeatedly and correctly distinguished from the Lagrange multiplier of the usage cap (lines 411, 413, 509). Equivalence claims rest on predeclared-margin TOST, with a paired analysis and an n=20 robustness check. Shadow prices are reported as crossing brackets.
- Agreement between tables, prose, and artifacts is excellent. All 20 quantitative spot-checks in Section 6 below match the committed CSVs at the printed precision, including derived quantities (paired differences, spreads, rounding of differences).
- The figures are mostly well matched to their captions and Descriptions. The Pareto, staircase, distractor, Tileworld, and scale-collapse figures reproduce exactly what the prose says, and the accessibility Descriptions are detailed.
- The style conventions hold. A scripted scan of the prose outside math found no semicolons. Bold appears only in the structured-abstract labels, theorem-part labels, table-best cells, and the checklist, and italics only at definitional first use.
- Reproducibility is exemplary: one producer per table, provenance stamps in the CSVs, the per-episode seeding rules stated, and a completed JAIR checklist.

## 4. Required changes

1. **One symbol, w*(B), denotes three different objects, including the object Definition 4.1 says is not a price.**
   - Location, first: abstract, line 70, "We reformulate the information weight as the operational shadow price $w^*(B)$ of a sensing budget $B$, the weight at which the agent's expected sensing usage meets $B$". Also Introduction, line 83, the same gloss.
   - Location, second: Definition 4.1 (PI-3), line 419, "the \emph{crossing bracket} $w^*(B) = (w_{\mathrm{lo}}, w_{\mathrm{hi}}]$ is the finite-grid estimate of the threshold".
   - Location, third: Section 4.4, line 477, "we solve $w^*(B)$ by grid search minimizing $|U - B|$ and report the crossing bracket rather than a bisection root".
   - What is wrong: the abstract and introduction define w*(B) as a scalar weight, "the exact price" that the bracket estimates. Definition 4.1 defines w*(B) as the bracket itself, a grid interval, while it names the scalar threshold w†(B). Line 477 uses w*(B) for the nearest-grid-point solution. Figures 6 and 7 plot "Shadow price w*(B)" as scalar step values, and those values are nearest-point solutions: at RockSample[7,4] B≈3 and Inspection-N=8 B≈14.5 the plotted marker sits at w_lo, outside the half-open bracket (w_lo, w_hi]. Section 6.4 (line 636) and the Figure 5 caption write "brackets $w^*$ in $(10, 31.6]$", again treating w* as a scalar. The separation of threshold, bracket, and mixture is the article's stated methodological contribution (abstract, contribution list at line 99), so overloading the symbol undercuts exactly the distinction the article is built to make.
   - Evidence checked: every occurrence of `w^*(B)` in the tex (lines 70, 83, 394, 419, 477, 482, 650, 667, 992), `rho_aif/budget.py` as cited, and the rendered `price_staircase_interleaved.png` and `price_shadow_curves.png`.
   - Concrete fix: reserve w*(B) for one object. The least invasive option keeps the abstract and introduction reading, defines w*(B) := w†(B) (the crossing threshold) in Definition 4.1, gives the bracket its own symbol (for example W(B) = (w_lo, w_hi]), and writes "w*(B) ∈ (10, 31.6]" or "W(B) = (10, 31.6]" consistently. At line 477, name the nearest-grid-point solution separately (for example ŵ(B)). In Figures 6 and 7, relabel the y-axis and state in each caption that the step values are the nearest-grid-point solution ŵ(B) and that the vertical bars are W(B).

2. **The Figure 4 caption describes the weight trajectory backwards.**
   - Location: Section 6.3, Figure 4 caption (`fig:dualmultiseed`), line 621, "The top row plots the controlled weight $w$ itself, median trajectory with interquartile band, dropping after the rescale invalidates the pre-rescale weight and climbing back as the controller re-adapts."
   - What is wrong: in `figures/price_dual_multiseed.png` the median weight falls from about 1 to about 0.27 in the first ~20 episodes, holds flat until the rescale at episode 200, and then rises to about 2.7. After the rescale it does not drop, and it does not "climb back" to a previous level: it climbs to a new level about ten times higher, which is exactly what Proposition 4.2 predicts for a ×10 rescale. The figure's own `\Description` (line 623) describes the trajectory correctly, so the caption and the Description contradict each other. What drops after the rescale is usage (bottom row), not the weight.
   - Evidence checked: the PNG, the Description, and Section 6.3's text.
   - Concrete fix: replace the clause with something like "falling from its initial value to about 0.27 before the rescale, then rising about tenfold to about 2.7 after it, as Proposition 4.2 predicts for a ×10 rescale." In the same caption, "the dashed budget line $B{=}8$ the controller tracks" would read better as "targets", given the article's own vocabulary rule for Proposition 4.5.

3. **Figure 1's boxed statement of the central identity has the opposite sign to Eq. 2.**
   - Location: Introduction, Figure 1 (`fig:hero`, lines 89 to 96). The text is drawn by `experiments/build_fig_hero.py` line 197, `"$G(\\pi){=}$ pragmatic $+$ epistemic"`. Compare Eq. 2 at line 177, `\mathcal{G}(\pi) = \underbrace{...}_{\text{Pragmatic value}} - \underbrace{...}_{\text{Epistemic value}}`.
   - What is wrong: Eq. 2 labels the positive expected KL divergence "Epistemic value" and subtracts it, and the prose after it says "It enters with a minus sign." The lead figure, which most readers see first, writes G(π) = pragmatic + epistemic. A reader who compares the two finds a sign error in the article's headline identity.
   - Evidence checked: the rendered `fig_hero_price_curve_jair.png`, the producer line, and Eq. 2 with its surrounding prose.
   - Concrete fix: change the producer string to "G(π) = pragmatic − epistemic", or to "pragmatic cost − information gain", and regenerate both hero variants. The Description's wording "a pragmatic term plus an epistemic term" (line 95) needs the same change.

4. **The abstract's "eleven of the twelve" count depends on a rare event that did not occur in the Tiger held-out stream, and the text does not say so.**
   - Location: abstract, line 70, "on eleven of the twelve attainable budgets its reward falls short of the estimated feasible envelope of a near-optimal constrained reference". Repeated in the Conclusion (line 1075). The underlying comparison is Section 6.9, line 754: "On Tiger the mixture's reward is $0.34$ above the envelope at the smallest budget and $0.05$ and $0.36$ below it at the two larger ones."
   - What is wrong: in `results/results_budget_frontier.csv`, every Tiger held-out per-seed reward equals exactly 10 minus the per-seed usage, for all six policies and all five held-out seeds. The held-out Tiger stream therefore contains no wrong commits. I reproduced this with a read-only rerun (`scratch_editor_clarity/tiger_wrong_commits.py`). The w=0 policy on held-out seeds 7 to 11 made 0 wrong commits in 500 episodes (mean reward 5.684, as in the CSV). The same policy on the calibration seeds made 1 wrong commit in 500 episodes (5.412, as in the CSV's calibration note). The constrained reference, 5.016 at usage 4.324, implies about a 0.6 percent wrong-commit rate. One wrong commit (−110) moves a 500-episode mean by 0.22, which is larger than the −0.05 shortfall and about two-thirds of the +0.34 excess. The printed seed-level SEs (0.08 to 0.14) reflect only listen-count variance, because the rare-event tail never appeared. Tiger's position relative to the envelope is therefore not resolved by this sample. The one exception in "eleven of the twelve", and one of the eleven, are artifacts of the held-out draw. The section's general caveat ("compare estimates from different evaluation streams") is true but does not tell the reader this.
   - Evidence checked: per-seed columns of `results_budget_frontier.csv` (all 24 Tiger policy rows), `results_cpomdp_baseline.csv` (Tiger reference 5.016 at U=4.324), `experiments/run_budget_frontier.py` (all policies share episode seeds, `episode_seed(s, ep)`), and the scratch rerun.
   - Concrete fix: in Section 6.9, add one sentence noting that the Tiger held-out stream contains no wrong commits, so held-out Tiger reward equals 10 minus usage and its SEs omit the rare-event tail, and that Tiger's comparison with the envelope is therefore unresolved at this sample size. Rephrase the abstract and Conclusion accordingly, for example "on every Diagnosis and Bandit budget its reward falls short of the estimated feasible envelope ... (Tiger's comparison is unresolved at this sample size)". The within-stream Tiger comparisons (mixture against best feasible member) are unaffected, because all policies share episode seeds, and they can stay as they are.

## 5. Optional suggestions

1. **Length relative to contribution (the most valuable optional change).**
   - Location: the whole manuscript. The main text runs 74 printed pages before the appendices, against a published-JAIR median near 40 pages total (the project's own 24-article sample).
   - What is wrong: much of the length is repeated qualification rather than new content. For example, "not the Lagrange multiplier" appears at lines 411, 413, and 509 and again in the Discussion. The near-optimal-not-exact disclaimer recurs in every reference subsection. Several secondary studies sit in the main text.
   - Fix: move Section 6.4 (cost-denominated budgets), Section 6.5 (interleaved staircases), the Tileworld partition-sensitivity paragraphs (lines 912 to 916), and the IDS paragraphs of Section 6.8 to appendices, each with a one-sentence summary left in place. State each standing disclaimer once, in Section 4.1 and Section 6.7, and refer back to it elsewhere.
2. **Abstract and conclusion readability.**
   - Location: the abstract's Results sentence (line 70, 110 words, beginning "At target budgets set by a predeclared rule") and the matching Conclusion sentence (line 1075, 113 words).
   - Fix: split each into three sentences: usage accuracy, reward against the envelope, and reward against the best feasible member.
   - A related point in the abstract's Methods: "is exactly equivalent to ..., exactly under log scoring rules" uses "exactly" twice with different scopes. Say instead that the equivalence is exact for the specified recursion and coincides with canonical nat-denominated EFE under log scoring.
3. **Figures 6 and 7 do not say what the filled markers are.**
   - Location: captions at lines 659 and 672.
   - Fix: state that the filled markers are nearest-grid-point solutions, and that a marker can sit on w_lo, which is outside the half-open bracket (RockSample[7,4] B≈3, Inspection-N=8 B≈14.5). This follows directly from required change 1.
4. **The same agent's figures differ across batteries, and no single place explains why.**
   - Location: Table 8 (main results), Table 5 (SARSOP), Table 6 (CPOMDP), Table 35 (atlas), and Section 7.2.
   - What is wrong: Tiger EFE usage is 4.20 in Table 8, 4.23 in the Pareto sweep, 4.32 in the SARSOP and CPOMDP studies, and 4.37 in the atlas. Its reward is 5.19, 5.33, 5.06, and 5.02 across the same batteries. Diagnosis usage is 9.66, 9.68, 9.73, 9.82, and 9.77. Each is correct for its own protocol, but only the Tileworld paragraphs (lines 898 and 914) say so.
   - Fix: add a short battery-map table (battery, seeds, episodes per seed, producer), or one sentence in Section 5 noting that figures differ across batteries by protocol.
5. **The cost-budget mechanism narrative is not what the data show.**
   - Location: Section 6.4, line 633, "At low weights the price tilts the choice between them toward the cheap test".
   - What is wrong: `results_price_cost_curves.csv` shows the mean cost per test fixed at exactly 1.26 at every w from 0 to 10, and rising only at w = 31.6 and 100, where count usage also jumps (7.82 to 11.40 to 14.75). The data show a flat plateau followed by a jump concurrent with extra tests, not a graded tilt that fades as w rises.
   - Fix: describe the observed shape and label the mechanism as an interpretation.
6. **Figure 18 caption (efficiency curves).**
   - Location: Appendix D.
   - What is wrong: "EFE commits at the right time" is evaluative and unsupported. Panel (c) is a mean over episodes still running, which is why Planning's curve jumps upward at step 16, and the caption does not say so. The caption also does not give Planning+IG's weight.
   - Fix: state all three, and drop the evaluative clause.
7. **Figure 17 (belief heatmap).**
   - What is wrong: the caption calls the episodes "representative", but EFE takes 29 observations against a battery mean of 14.4 at K=3 (`results_showcase_obs_scaling.csv`). Separately, panel (b) is titled "Planning (ρ=0)", while the article uses ρ for the belief-dependent reward and w=0 for Planning.
   - Fix: use "illustrative", and retitle panel (b) with w=0, at the producer.
8. **Figure 15 `\Description` (asymmetry sweep, line 1285).**
   - What is wrong: it says the blue, orange, pink, and vermillion lines decline "together from about 7 to about 4". The orange and pink lines start near 5.6 and stay flat until large penalties.
   - Fix: correct the Description.
9. **Notation for reward scale.**
   - What is wrong: Appendix Q uses k for the reward scale that Proposition 4.2 calls α, and α also denotes reward asymmetry (a clash the text acknowledges at line 982).
   - Fix: use α in Appendix Q, or state that k is Proposition 4.2's α.
10. **Bandit remark in the Discussion (line 1034).**
    - What is wrong: the paragraph says Proposition 3.2's formula "does not apply to it directly", then asserts that "the $H{=}1$ threshold would make $w{=}1$ only barely enough to justify observing at all".
    - Fix: compute the quantity, or drop the quantitative assertion.
11. **Tiger's pymdp-AIF row.**
    - Location: the Table 8 caption excludes "Tiger's pymdp-AIF row", and the row does not appear in the appendix tables either. No reason is given.
    - What is wrong: in `results_tiger.csv` that row is bit-identical to Posterior-vote (2.6448 observations, 96.76 percent, 3.7912).
    - Fix: state why the row is omitted.
12. **Testbed table caption.**
    - Location: Table 18, Appendix C.
    - What is wrong: "5{,}000 episodes" omits the seed breakdown, which is 1,000 per seed × 5 (`results_summary.csv`), unlike every other table caption.
13. **Figure 19 caption (line 1493).**
    - What is wrong: "confirming that multi-step planning amplifies the value of observation" is stronger than a single-seed, 50-episode-per-cell descriptive sweep supports.
    - Fix: "consistent with".
14. **Figure 10 footer semicolon.**
    - What is wrong: the in-figure footer ("Scan panels are subsampled evenly per row; t gives the true step.") contains a semicolon. This is trivial, but the article otherwise holds the no-semicolon rule everywhere.
    - Fix: change it at the producer.

## 6. Verification log

Every row was checked with read-only Python against the committed CSVs, except where noted.

| # | Claim (location) | Artifact | Result |
|---|---|---|---|
| 1 | Moving Tiger and Diagnosis to w=50 costs 1.07 and 2.41 reward and buys at most 1.8pp (Section 7.2) | `results_pareto_sweep.csv`: 5.3264→4.2536, −1.2624→−3.676, +0.32pp and +1.80pp | match |
| 2 | Bandit gains 9.8pp for 0.41 reward at w=5 | 96.76−86.92, 6.242−5.8356 | match |
| 3 | On Tileworld, w=20 gives −18.95 and 91.8% against w=1's −21.53 and 72.0% | same CSV | match |
| 4 | Testbed +6.4pp (96.4 vs 89.9) for −0.11 reward | 96.36/89.92, 0.3713/0.4826 | match |
| 5 | Success-maximizing weight is w=200 on all five swept environments | same CSV | match |
| 6 | Table 8 rows (EFE, Planning, Planning+IG, Myopic on three environments), +8.3pp and +15.9pp | `results_tiger.csv`, `results_diagnosis_n4.csv`, `results_bandit.csv` | match |
| 7 | Posterior-vote: 6.32, 87.0%, 5.01 on Bandit, −2.78 on Diagnosis, +3.79 on Tiger | same CSVs (Thompson rows) | match |
| 8 | Dual control: restricted means 157.3 and 51.2, paired difference 106.1, smallest paired difference 89, 9/10 recover, conditional mean 154.8, post-steady error 0.39 vs 0.06, 5 tighter / 4 tied / 1 looser | `results_price_dual_multiseed_metrics.csv` | match |
| 9 | Distractor: 0.103±0.001 and 0.233±0.003, saturation at 0.330–0.332, reward pairs, 6.46 tests and 33.2%, 99.2% vs 98.4%, 13.16 vs 9.77, IDS 0.305±0.005 | `results_distractor_diagnosis.csv` | match |
| 10 | Budget frontier: mixture rewards and usage errors, best-member rewards, best-target-mixture reward 5.94, envelope gaps (Table 7 and prose) | `results_budget_frontier.csv` | match (the Tiger rare-event issue is required change 4) |
| 11 | Tiger held-out wrong commits | fresh rerun, `scratch_editor_clarity/tiger_wrong_commits.py`: 0/500 held-out (5.684), 1/500 calibration (5.412) | reproduced CSV exactly |
| 12 | SARSOP TOST: paired p 0.016 and 3.6e-5, unpaired 0.046 and 0.013, SEs 0.24/0.03 and 0.38/0.18, Tiger CI ±0.41 | `results_tost_sarsop.csv` | match |
| 13 | Table 5 (SARSOP) rewards and usages (5.061, −1.452/−1.217, 6.280/6.261) | same CSV (means) | match |
| 14 | Figure 15 caption numbers: 2.7→5.8, 4.37, 5.77, about 1.6 reward | `results_showcase_asymmetry.csv` (1.586) | match |
| 15 | Figure 13 caption gaps: 0, −0.6pp, +13.2pp | `results_showcase_obs_scaling.csv` | match. The PDF render is identical to the older PNG |
| 16 | Nat-canonical check: bit-identical on four environments; Tileworld −20.81, 74.7%, 15.64, p = 9.5e-5 / 0.34 / 0.070 | `results_nat_canonical_check.csv` | match |
| 17 | w* atlas table rows (Table 35) | `results_w_atlas.csv` | match |
| 18 | Tileworld scaling: 1.4±0.3%, 69.4±1.0%, 97.8%, −49.16 for both Planning and Myopic | `results_tileworld_scaling.csv` | match |
| 19 | Inspection N=8: 91.1% vs 73.0%, +18.0pp, −20.95±0.30, −17.85 | `results_inspection_n8.csv` (18.045 unrounded) | match |
| 20 | Cost per test from 1.26 to 1.41, a 12.0% spread relative to the grid mean | `results_price_cost_curves.csv` (0.1539/1.2824) | match |
| 21 | Near-optimality rates 30 / 58 / 79% | `results_nearopt_horizon.csv` | match |
| 22 | All 20 figures against their captions and Descriptions | PNGs under `figures/` | match except Figure 4's caption (required change 2), Figure 1's box sign (required change 3), and the minor Description and caption items in optional suggestions 6 to 8 and 14 |
| 23 | Style conventions (prose semicolons, rhetorical emphasis, "exact" applied to SARSOP or CPOMDP, "tracking guarantee", Lagrange-multiplier statements) | scripted scan, `scratch_editor_clarity/style_scan.py` | match (no violations found) |

Could not verify: the Figure 10 and Figure 16 per-episode belief values (0.47, 0.73, 0.98). These come from single illustrative episodes that no CSV records. The figures are internally consistent with their captions.

## 7. Would you recommend unqualified Accept if the required changes were made?

Yes. All four required changes are wording, notation, or figure-producer fixes with the evidence already in hand, and once they are made I see nothing that would block acceptance.
