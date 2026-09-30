# Associate-editor report (lens: editor_clarity)

Manuscript: `paper/full_paper_jair.tex` (2208 lines), rendered text `reviews/final_panel_concise_2026-09-28/manuscript_jair.txt` (118 pages).
Reviewer role: JAIR associate editor. I read the whole source, including all 26 appendices (A to Z) and every `\input` table. I viewed all 12 main-body figures and a sample of the appendix figures, and I checked quantitative claims against the committed CSVs using read-only Python.

## 1. Recommendation

Accept with minor revisions.

## 2. Summary

The paper makes two contributions. First, it shows that a specified recursive, reward-based EFE objective is a rho-POMDP with information weight w=1 under stated structural, horizon, and unit assumptions (Proposition 3.1). Second, it gives an operational way to set that weight: calibrate it to an expected sensing-usage target. The price is a crossing threshold w*(B), estimated by a grid bracket (w_lo, w_hi]. An endpoint mixture meets gap budgets in expectation. Scale equivariance holds, and a projected decaying-step controller converges to a stationary point. The empirical program is broad and honest about its limits. Held-out calibration meets targets to within 0.13 observations but gives up reward against a sampled constrained reference. Separately, w=1 is reward-maximizing on three of five swept environments and beaten on two. The concision pass succeeded. The main body ends on page 37 and references begin on page 38, under the 40-page limit. The main text reads as a self-contained paper with 12 figures and seven tables, and the abstract, introduction, and conclusion state the claims and their limits in the same calibrated vocabulary. Every main-body figure matches its caption. Every table I checked matches its CSV, and every number repeated between the main body and an appendix is consistent. The defects that remain are all in the appendices, and all come from the shortening. Several cross-references still point to the Discussion or Methodology for material that now lives in appendices. One appendix symbol collides with the paper's central bracket notation. One appendix sentence generalizes beyond the paper's own Tileworld evidence. None of these fixes adds a line to the main body.

## 3. Strengths

- Fit and contribution. The problem suits JAIR well: sensing budgets in POMDP planning, with a clear operational interpretation of the information weight. The paper separates what is proved (the equivalence, equivariance, and stationary convergence) from what is measured (the usefulness of w=1 and the reward cost of calibration).
- The main body stands alone. The Introduction's contribution list, the budget theory (Definition PI-3, Propositions 4.2, 4.3, and 4.5), the held-out frontier study, and the EFE battery all fit in 37 pages. Where the main text defers detail, it says what it is deferring and why.
- The claim vocabulary follows the project conventions throughout the main body:
  - SARSOP and CPOMDP are "near-optimal" or "estimated". The CPOMDP envelope is "neither a certified population bound nor the full constrained frontier".
  - PI-5 is stationary convergence, and re-adaptation is labelled an empirical result.
  - "The information weight w is not that multiplier" appears in Section 6.7 (line 606), with the same point made in Related Work (line 151).
  - No closed form for w* is claimed. The w* Atlas says explicitly that no closed-form relationship should be inferred from it.
- Notation in the main body is defined before use:
  - w*(B) as the crossing threshold, (w_lo, w_hi] as its bracket, and the endpoint mixture q all appear in Definition PI-3.
  - hat-w(B) is defined in Section 4.4 before the staircase figures use it.
  - The figure legends use exactly this notation, for example "Shadow price: estimate hat-w(B), bracket" and "bracket (w_lo, w_hi]".
- Statistics are reported to the declared protocol. Main tables use seed-level Welch tests with Holm correction. Equivalence is claimed only under TOST with predeclared margins, and the retrospective margin choice is disclosed. The paired frontier intervals are labelled "nominal pointwise", and their omission of reference-selection uncertainty is stated in the abstract.
- Limitations appear in the Introduction (last paragraph), the Discussion, and the Conclusion. They are not confined to a back section.
- Style: prose contains no semicolons (the only two are inside display math at lines 405 and 406). Italics appear only for definitional first use (line 378 and elsewhere), and bold appears only in tables and theorem part labels.

## 4. Required changes

All three are appendix-only. None changes a number, table, figure, or main-body line.

1. **Section: Appendices B, J, P, S, and W (cross-references left stale by the concision).**
   - Quotes and line numbers:
     - Line 1302: "This is the same trend reported for Bandit in Section~\ref{sec:discussion}, where the low reward asymmetry predicts only marginal $H{=}1$ sufficiency"
     - Line 1511: "Section~\ref{sec:discussion} argues that the epistemic value term supports interpretable decisions"
     - Line 1598: "we implement MCTS-EFE, the UCB1 tree search of Section~\ref{sec:discussion}"
     - Line 1562: "the same distinction drawn for the MCTS-EFE comparison above"
     - Line 1958: "That numerator is the squared expected regret of taking the observation action (Section~\ref{sec:methodology})"
     - Line 1965: "the EFE benchmark battery (Section~\ref{sec:results}) follows. The Discussion after it draws the results together, beginning with the reward convention"
     - Line 958: "reported in Table~\ref{tab:pomcp} and Section~\ref{sec:discussion}"
   - What is wrong: each target no longer contains the material described. The shortened Discussion (lines 824 to 851) does not discuss Bandit's low asymmetry. It does not argue that the epistemic term supports interpretable decisions, and it does not describe the MCTS-EFE design or report its Tileworld numbers. The Bandit discussion is now in Appendix Y, `app:interpretation`, at line 2136, and the MCTS-EFE design is also in Appendix Y at line 2144. The IDS numerator is defined in Appendix N, `app:ids`, at line 1460, not in Methodology. The MCTS-EFE paragraph cited as "above" at line 1562 comes later, at line 1598. Line 1965 is a leftover main-body transition. It sits at the end of Appendix W, which is followed by Appendix X, not the Results. The Discussion now opens with "What a sensing target determines", not with the reward convention.
   - Evidence checked: the full text of Section 8, the Discussion (lines 824 to 851), `app:interpretation` (lines 2096 to 2155), `app:ids` (lines 1457 to 1498), and the rendered appendix order in `manuscript_jair.txt`.
   - Fix:
     - Lines 1302, 1598, and 958: point to `app:interpretation`.
     - Line 1511: open with the audit's own motivation, for example "The Planning+IG score decomposes each action's value into task value and weighted information gain, but nothing in the main results exposes that decomposition directly."
     - Line 1562: change "above" to "in the MCTS-EFE paragraph below".
     - Line 1958: point to `app:ids`.
     - Line 1965: delete the last two sentences.
   - Placement: appendix.

2. **Section: Appendices C, J, U, and Y (threshold notation collides with the bracket notation).**
   - Quote, line 1302: "Proposition~\ref{prop:nearopt} bounds $w^*_{\mathrm{lo}}$ at $H{=}1$ and $w^*_{\mathrm{hi}}$ at $H{=}2$."
   - What is wrong: Proposition 3.2 defines w*_thresh and w*_over. The appendices rename them w*_lo and w*_hi, at lines 1018, 1302, 1670, 1674, 1680, 1691, 1693, and 2132. Meanwhile (w_lo, w_hi] is the paper's crossing bracket of w*(B) (Definition PI-3 at line 378, and lines 432 and 572). A reader can easily take w*_hi to mean the upper edge of a price bracket. The first two uses, at lines 1018 and 1302, come before the renaming is explained at line 1670. The paper itself flags the overloading at line 1747 ("which share the star notation").
   - Evidence checked: every occurrence found by grep for `w^*_{\mathrm{lo}}` and `w^*_{\mathrm{hi}}` (8 lines), against the Definition PI-3 notation and the brief's notation convention.
   - Fix: use the proposition's own symbols, w*_thresh and w*_over, in `tab:alpha_eta` (caption and header) and at the six prose sites. Then delete the two mapping sentences at lines 1670 and 2132. Mirror the change in `full_paper.tex` (lines 1331, 1608, 1974, 1978, 1984, 1995, 1997, and 2436).
   - Placement: appendix.

3. **Section: Appendix C, Two-State Testbed (generalization contradicted by the paper's own Tileworld result).**
   - Quote, line 1018: "have asymmetric penalties ($|R^-|/|R^+| \gg 1$), precisely the regime where $w{=}1$ is well-calibrated (Tiger, Diagnosis)."
   - What is wrong: Tileworld also has asymmetric penalties (alpha = 5 in `tab:alpha_eta`), yet w=1 is Pareto-dominated there by w=20. The main body says so (lines 760 and 766), and so does Appendix U at line 1693 ("On Tileworld it is not"). The careful version of this sentence already exists at line 2138: "the regime where the interval analysis is most favorable to w=1 ... not a guarantee of near-optimality."
   - Evidence checked: `results_pareto_sweep.csv`. Tileworld at w=1 gives reward -21.528 and success 72.04%. At w=20 it gives reward -18.954 and success 91.80%. Tiger and Diagnosis place w=1 on the tied reward-maximizing plateau.
   - Fix: replace the clause with "the regime in which the two-state interval analysis is most favorable to $w{=}1$ (it lies on the reward-maximizing plateau on Tiger and Diagnosis but is Pareto-dominated on Tileworld)".
   - Placement: appendix.

## 5. Optional suggestions

1. **Appendices T and W, duplicated subsection.**
   - Quote, lines 1624 and 1963: "\subsection{The $w^*$ Atlas}"
   - Issue: two subsections with the same title. The first carries the table and the second the interpretation, and a reader following "Appendix T" or "Appendix W" lands on half of it.
   - Fix: merge them under `app:w_atlas`, keeping `sec:w_atlas` as a second label on the merged subsection so nothing breaks.
   - Placement: appendix.

2. **Appendix U, discounting.**
   - Quote, line 1695: "On environments with several observation actions EFE's advantage requires $\gamma \geq 0.99$"
   - Issue: the main body (line 840) says this threshold "is not a general regime boundary".
   - Fix: "In this benchmark sweep, EFE's advantage on environments with several observation actions appeared only at $\gamma \geq 0.99$."
   - Placement: appendix.

3. **Section 7.3, Tileworld.**
   - Quote, line 772: "achieves $1.4\%\pm0.3$ percentage points success"
   - Issue: the units are mixed.
   - Fix: write "$1.4 \pm 0.3\%$ success" (the CSV gives 0.014 with SE 0.0029).
   - Placement: main body, net-neutral.

4. **Appendix M.**
   - Quote, line 1447: "and we say so because we measured it rather than because a referee asked"
   - Issue: the register is informal.
   - Fix: delete the clause.
   - Placement: appendix.

5. **Appendix U, tuning criteria.**
   - Quote, line 1747: "reading it off a sensing budget as the bracket of adjacent grid weights"
   - Issue: the sentence equates the price with its grid estimate.
   - Fix: "reading it off a sensing budget as the crossing threshold $w^*(B)$, estimated by the bracket of adjacent grid weights".
   - Placement: appendix.

6. **Figure 11 caption.**
   - Quote, line 760: "on Tileworld $w{=}20$ dominates them on both axes"
   - Issue: in `results_pareto_sweep.csv`, the w=0.01 to 0.5 plateau (74.8%, -20.82) and w=10 (78.6%, -20.19) also sit nominally above and to the right of w=1. Appendix R reports that the low-weight difference is not significant (p=0.34 for reward, p=0.07 for success).
   - Fix: consider "w=20 dominates them on both axes, and smaller nominal improvements appear at other weights".
   - Placement: main body, net-neutral.

7. **Appendix W, dual-control subsection.**
   - Quote, line 1882: "argued that an offline bracket is valid only at the reward scale it was solved at"
   - Issue: Section 4.6 (line 472) says scale equivariance transfers calibrated weights across known rescalings.
   - Fix: "valid only at a known reward scale".
   - Placement: appendix.

8. **Appendix order.**
   - Issue: the 26 appendices split related material. The proofs are in A and U, RockSample in M and X, and POMCP in S and Y.
   - Fix: add a short roadmap paragraph at `\appendix`, or reorder the appendices.
   - Placement: appendix.

## 6. Verification log

Length and structure:
- In `manuscript_jair.txt`, the Conclusion ends on page 37 and the References begin on page 38. The main body is under 40 pages.
- There are 26 appendices, A to Z. Proposition numbers in the PDF are 3.1 (equivalence), 3.2 (near-optimality), 3.4 (factored), 4.2 (scale equivariance), 4.3 (comparative statics), and 4.5 (controller). The hero figure's "Prop. 3.1" label is therefore correct.

Figures viewed against their captions and Descriptions. All matched.
- Main body, all 12 figures:
  - hero price curve
  - engineering workflow
  - state preservation
  - target versus cap. Arithmetic rechecked: endpoint mixture R=3.25 and best target mixture R=4.
  - scale invariance. The shared bracket (0.141, 0.323] and plateaus of about 5.9 and 9.77 match `results_price_scale_invariance.csv`.
  - dual multiseed. Pre-shift w is about 0.28 and post-shift about 2.7. No iterate exceeds 3.1.
  - cost budget. The four brackets (10, 31.6] and (31.6, 100] were recomputed from the plotted means. The ratio stays at 1.26 through w=10.
  - interleaved staircase. There are 4 budgets per series, and the one slack marker is on RS[5,3].
  - observe-then-commit staircases. The figure shows 9 slack markers, 7 of them at w=0, one at w=0.316 (Diagnosis), and one at w=0.139 (Bandit), exactly as the caption states.
  - distractor composition. Onset (3.5, 4.0], saturation near one third.
  - Pareto. Labels and tied ranges match the CSV.
  - Tileworld scaling. 69.4%, 97.8%, and 1.4% match.
- Appendix figures viewed: obs scaling, rendered from the PDF into the scratch folder because the PNG is older than the PDF. Its caption gaps (0, -0.6, and +13.2 pp) match `results_showcase_obs_scaling.csv`. Also viewed: prop2 jumps and nearopt horizon (30, 58, and 79%; strata n=7, 12, and 81).

Quantitative spot-checks against CSVs. Every item matched.
1. `tab:main` against `results_tiger.csv`, `results_diagnosis_n4.csv`, and `results_bandit.csv`. All 12 rows match observation counts, success, reward, and seed SE, for example Diagnosis EFE 9.66, 97.2%, and -1.37 ± 0.18.
2. Line 746: Diagnosis p = 4.0e-8 (success) and 0.002 (reward), and Bandit p = 2.1e-5 and 0.001, all Holm-significant, against the `_stats.csv` files (3.958e-8, 2.016e-3, 2.137e-5, 1.091e-3).
3. Posterior-vote on Bandit: 6.32 against 6.27, p = 0.58, and success p = 0.97, against `results_bandit_stats.csv` (Thompson row: 6.3205, p = 0.582, 0.971).
4. TOST p-values of 0.0010, 0.0458, and 0.0130, and paired p-values of 0.016 and 3.6e-5, against `results_tost_sarsop.csv`.
5. `tab:sarsop`, all cells, against `results_sarsop_baseline.csv`.
6. `tab:cpomdp` gaps of -0.041 (-3.27%) and -0.005 (-0.08%), and the usage-matched weights 0.00, 0.45, and 1.07, against `results_cpomdp_baseline.csv`.
7. Frontier text at line 638, against `results_budget_frontier.csv`:
   - Mixture errors are at most 0.123, which supports "within 0.13".
   - Bandit's gap error is 0.092/0.069 = 1.34 SE.
   - Endpoint misses are 0.331 to 1.105 on Tiger and 0.162 to 3.634 elsewhere.
   - Best-feasible-member usage is 0.178 to 4.734 below target, and below it in all 12 rows.
   - The mixture exceeds B in 3 rows (Diagnosis 0.75, Diagnosis gap, Bandit 0.25), by at most 0.123.
8. Dual control: restricted means of 157.3 and 51.2, difference 106.1, decay-only recovering on 9 of 10 seeds (seed 105 censored), all ten differences favouring reset. Checked against `results_price_dual_multiseed_metrics.csv`.
9. Bracket stability: reported bracket recovered in 19 of 25 budgets at 1.0, 21 at 0.99 or above, minimum 0.789 (Inspection-N8). The only non-adjacent alternative is one Tileworld resample. Checked against the stability CSVs.
10. Pareto sweep:
    - Testbed: +6.44 pp success at a reward cost of 0.111.
    - Tileworld: w=20 gives -18.954 and 91.8%, against -21.528 and 72.0% at w=1.
    - Success is maximized at w=200 in all five environments.
    - Tied plateaus: [0.01, 20], [0.5, 20], and [1, 2].
11. Tileworld 6x6: -21.53 against -21.39 (p = 0.82), 72.0% against 73.8% (p = 0.17), and 14.75 against 15.64 scans (p = 8.8e-5). Scaling at 8x8: Planning 1.4 ± 0.3%, EFE 69.4 ± 1.0%, Planning+IG 97.8%.
12. Distractor:
    - Distractor fractions 0.103 and 0.233.
    - At w=100: 6.456 distractor tests (6.46), a 33.15% share (33.2%), and reward -10.48 against -3.64.
    - The variant's 13.16 task tests against 9.77.
13. Collapse and atlas: brackets (0.141, 0.323], (3.84, 8.76], and (5.80, 20.0], Tiger flat at 4.368, and the atlas rows, against `results_price_scale_invariance.csv` and `results_w_atlas.csv`.
14. Near-optimality: 30, 58, and 79% by horizon (21% failing at H=3), and the horizon-map strata (8 of 9 rising), against `results_nearopt_horizon.csv` and `tables/horizon_map.tex`.
15. RockSample and POMCP numbers in the text:
    - Heuristic 28.66 ± 0.83.
    - POMCP 12.94.
    - Rollout-only 16.67, which is 3.93 above POMCP's 12.74.
    - 7.5 against 13.5 steps.
    - Checked against `tables/rocksample_extended.tex`.
16. The nat-canonical check is bit-identical on four environments. On Tileworld, the Welch p-values are 0.34 (reward) and 0.07 (success), against `results_nat_canonical_check.csv`.

Internal consistency between the main body and appendices:
- The Bandit gap bracket (0.06, 0.14] matches the atlas (0.0611, 0.139].
- The Tiger usage figures 4.20, 4.32, and 4.37 come from different batteries, and line 1812 discloses this.
- Frontier interval counts (9 of 12, and 8 of 11 distinct) agree between the abstract, Introduction, and Section 6.8.
- The Pareto claims agree between the Results, the Discussion, the Conclusion, and `tab:alpha_eta`.

Style:
- A programmatic scan for prose semicolons (with math stripped) found none.
- `\emph`, `\textit`, and `\textbf` appear only at definitional first use, in theorem part labels, and in tables.

## 7. Would you recommend unqualified Accept if the required changes were made?

Yes. The three required changes are mechanical appendix corrections (cross-references, one symbol rename, and one sentence of calibration), and nothing in the main body, figures, tables, or data needs to change.
