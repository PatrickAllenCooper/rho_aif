# Editor (clarity) report, revision round 2

Lens: editor_clarity (JAIR associate editor). Object: the revised `paper/full_paper_jair.tex` (the working tree against HEAD, 41 changed lines), the rebuilt figures, `paper/tables/budget_frontier.tex`, and the new `results/results_budget_frontier_heldout_reference.csv`. I checked every item against the current file text and, where numbers are involved, against the CSVs using read-only Python. I did not rely on the authors' disposition summary.

## 1. Recommendation

**Accept.**

All four required changes from round 1 are resolved in the text, the figures, and the artifacts. Thirteen of the fourteen optional suggestions are applied or reasonably waived. One suggestion the authors list as applied (optional 9, reward-scale notation) is not in the text. The revision also introduces four small wording issues, listed in Section 7. None of them affects a claim's correctness, and all can be handled at copy-edit.

## 2. Summary

The article shows that expected-free-energy (EFE) minimization is exactly a rho-POMDP with information-gain weight w=1, under the article's recursion, and that it coincides with canonical EFE under log scoring. It then treats the weight as the operational shadow price of a sensing budget, supported by usage curves, crossing thresholds estimated by grid brackets, scale equivariance, and a projected dual controller. An extensive battery places w=1 against SARSOP and constrained-POMDP references.

The revision does four things:

- It gives the price a single meaning. w*(B) is now the crossing threshold, the bracket is its grid estimate, and ŵ(B) is the nearest grid point that the figures plot.
- It fixes the Figure 4 caption and the sign in the hero figure's box.
- It replaces the budget-frontier headline with a same-stream paired comparison.
- It adds a one-sentence note on cross-battery differences.

The contribution and fit are unchanged from round 1. The article suits JAIR, and its main claims are now stated once and consistently.

## 3. Strengths (unchanged from round 1, plus the revision's)

- The theory is honest about its reach, and the claim-calibration vocabulary is held throughout.
- Definition 4.1 now separates four objects: level set, crossing threshold (the price), grid bracket (its estimate), and endpoint mixture (the randomized policy). The prose, captions, axis labels, and legends all follow that separation. Earlier the notation was the article's main clarity problem. It is now a model of care.
- The new same-stream reference goes beyond a wording fix. It re-evaluates the saved SARSOP-Lagrangian policies on the held-out episode seeds, so the frontier comparison is paired under common random numbers. It also explains, rather than hides, the old Tiger "above the reference" artifact as a stream effect.
- The retrospective status of the TOST margin is now disclosed plainly (line 703). The n=20 study is identified as the prospective part of the evidence, and "predeclared-margin" is replaced by "fixed-margin" in all four places it occurred.

## 4. Required changes

None.

### Status of the round-1 required changes

1. **Notation for w*(B): resolved.**
   - Line 419 now defines the price as the threshold, "The operational shadow price of this article is this threshold, $w^*(B) := w^{\dagger}(B)$". The bracket is named as "the finite-grid estimate of the threshold".
   - Line 477 introduces ŵ(B) as "the grid weight minimizing $|U - B|$ ... which can sit on the bracket's lower edge or, at a slack budget, below it."
   - Lines 83 and 409 define the price as the crossing weight.
   - The Figure 5 caption (line 642) and its Description (line 644) now read "$(10, 31.6]$" rather than "$w^*\in(10,31.6]$".
   - The Figure 6 and 7 captions (lines 659 and 672) say "Every marker plots the nearest-point solution $\hat{w}(B)$". The rendered `price_staircase_interleaved.png` and `price_shadow_curves.png` carry the y-axis label "Shadow price: estimate ŵ(B), bracket" and the legend entry "slack budget: ŵ(B) below its crossing bracket".
   - I searched for residual "w* ∈ (bracket)" notation. The one remaining hit (line 497, "a single crossing $w^* \in (0, w_{\max})$") is the continuous-domain condition of Proposition 4.5, not a bracket, so it is correct.
2. **Figure 4 caption: resolved.** Line 621 now describes the weight "falling from its initial value to about 0.3 within the first few dozen episodes, holding there until the rescale invalidates it, and then climbing about tenfold, to about 2.7". This matches the direction and magnitude of the plotted trajectory. The recovery numbers (51 versus 157, difference 106, interval [97, 115]) are unchanged from the verified round-1 values.
3. **Hero figure sign: resolved.** `experiments/build_fig_hero.py` line 197 now writes "$G(\pi){=}$ pragmatic $-$ epistemic". The rendered `fig_hero_price_curve_jair.png` shows "G(π) = pragmatic − epistemic", and the Description (line 94) says "a pragmatic term minus an epistemic term". All three agree with Eq. 2.
4. **Abstract count: resolved by new evidence.**
   - The abstract (line 70) and conclusion (line 1075) now say the reward "falls short of the reference's estimated feasible envelope on eight of the eleven distinct attainable budgets, with paired 95 percent intervals excluding zero". I recomputed this from `results_budget_frontier_heldout_reference.csv`, using the primary (endpoint-mixture) rows.
   - Tiger shows −0.326 [−0.429, −0.223], −0.722 [−0.890, −0.554], and −1.032 [−1.193, −0.871]. The gap budget coincides with the 0.5 budget.
   - Diagnosis shows −0.757 [−1.186, −0.329] and −1.104 [−1.713, −0.495].
   - Bandit shows −0.571 [−0.830, −0.312], −1.316 [−1.529, −1.103], and −0.587 at the gap budget [−1.132, −0.042].
   - That is nine of twelve budgets and eight of eleven distinct budgets, as line 754 says. The three budgets within sampling error are Diagnosis 0.25 (−0.030 [−0.811, 0.752]), Diagnosis gap (+0.001 [−0.616, 0.618]), and Bandit 0.25 (−0.211 [−0.553, 0.131]).
   - "Up to about a fifth of the reference reward" corresponds to Bandit at 0.75, where 1.316/6.267 = 21 percent.
   - The table columns "Same-stream ref." and "Paired gap" match the CSV to two decimals.
   - One residual caveat on the Tiger intervals remains. It is non-blocking and appears as optional item A in Section 5.

## 5. Optional suggestions

### New items

A. **Tiger's same-stream intervals omit rare-event variance.**
   - Location: line 754 and the Table 7 paired-gap column.
   - What is wrong: the held-out Tiger stream contains no wrong commits by the reference-equivalent policy. The same-stream reference is 5.684 at every budget, which is exactly the reward of the zero-wrong-commit reward-only policy. My round-1 rerun (`scratch_editor_clarity/tiger_wrong_commits.py`) found 0 wrong commits in 500 held-out episodes, against about 0.6 percent implied on the canonical stream. The paired SEs (0.037 to 0.061) therefore reflect only listen-count variance.
   - Why the sign still holds: the mixture plays the 4.316-usage policy or a policy with 1.44 more listens. Its expected gap is about q(−1.44 + 110 p0), which stays negative while the wrong-commit rate p0 is below about 1.3 percent.
   - Why the magnitude may not: at p0 near 0.6 percent, the expected Tiger gaps are roughly half the measured ones, for example about −0.18 rather than −0.33 at the 0.25 budget.
   - Fix: one sentence noting that the held-out Tiger stream contains no wrong commits, so the Tiger intervals do not reflect that rare-event variance, although the sign is robust.
B. **"Every comparison the paper draws is made within one battery" (line 530) is slightly too absolute.** Table 7's committed-reference column and gap still compare held-out rewards with a reference sampled on the canonical stream. Section 6.9 discloses this and now supplements it, but the sentence as written is literally false. Fix: "Every headline comparison is made within one battery, and the one cross-stream column, Table 7's committed reference, is flagged as such in Section 6.9."
C. **Definition 4.1, item two, has grown a 90-word sentence** that restates the "final grid point falls back below B" fallback. The parenthetical in item three states the same thing again. Stating the solver's fallback once, in item three, would make the definition easier to read. The substance is correct.
D. **Cost-budget paragraph (line 633).** Optional 5 is applied: the step shape ("holds at 1.26 from w=0 through w=10 and rises to 1.37 and then 1.41 only at the two largest weights") is stated, and it matches `results_price_cost_curves.csv`. Two small problems remain.
   - The preceding sentences still narrate a graded tilt that "fades as w rises".
   - The following sentence repeats "varies from 1.26 to 1.41".
   - Fix: label the tilt narrative as an interpretation and drop the repeated range.

### Status of the round-1 optional suggestions

1. Length, moving sections, and a cross-battery table: waived with a reason. The rest of the panel asked for no cuts, and moving sections would break the budget-first narrative. I accept the waiver. My view is unchanged that the repeated disclaimers could be consolidated at copy-edit, but this is the authors' call.
2. Abstract readability: applied. The Results sentence is now three sentences (usage accuracy, reward against the envelope, reward against the best feasible member), and the Methods sentence scopes "exact" to the log-scoring identification.
3. Figure 6 and 7 markers: already present in round 1, and now explicit via ŵ(B).
4. Cross-battery note: applied at line 530. The example numbers check out: Tiger EFE uses 4.198 observations in `results_tiger.csv` and 4.3232 in `results_sarsop_baseline.csv`, printed as 4.20 and 4.32. See new item B for the wording.
5. Cost mechanism: applied in substance. See new item D.
6. Figure 18 caption: applied. It now says it averages only surviving episodes and gives Planning+IG's weight provenance ("myopic Info Gain agent's success-tuned weight, selected on 100 tuning episodes and transferred"). The evaluative clause is gone.
7. Figure 17: applied as "one illustrative Diagnosis episode per agent, not chosen to be typical in length". The caption's counts (Planning 14, EFE 29, InfoGain-Tuned 32, all correct) match the rendered panel titles. I accept the ρ=0 disposition, because line 169 defines ρ=0 as recovering the standard POMDP, so the panel label is consistent with the article's notation.
8. Figure 15 Description: applied. The orange and pink lines "hold near 5.6 up to a penalty of about 50", which matches the figure.
9. Reward-scale notation: **not applied**, although the disposition lists it as applied. Appendix Q (line 1706, and the captions at 1711 and 1718) still uses k with no statement that k is Proposition 4.2's α. Fix: add "(Proposition 4.2's α, written k here to avoid a clash with the reward-asymmetry ratio)".
10. Bandit remark (line 1034): applied. The quantitative assertion is withdrawn ("although we do not compute its threshold").
11. Tiger pymdp-AIF row: applied. The Table 8 caption now says it "is bit-identical to Posterior-vote on every reported metric".
12. Testbed caption: applied ("5,000 episodes at 1,000 per seed × 5 seeds").
13. Figure 19 caption: applied ("consistent with multi-step planning amplifying").
14. Figure 10 footer: applied. The rendered footer reads "Scan panels are subsampled evenly per row, and t gives the true step."

## 6. Verification log

| # | Check | Artifact | Result |
|---|---|---|---|
| 1 | Definition 4.1 sets w*(B) := w†(B), the bracket is the estimate, and ŵ(B) is the nearest point | tex lines 83, 409, 419, 477 | consistent |
| 2 | Staircase figures label ŵ(B) and brackets | `price_staircase_interleaved.png`, `price_shadow_curves.png` | match captions |
| 3 | Figure 4 caption direction (falls to about 0.3, climbs about tenfold to about 2.7) | caption at line 621 against the rendered figure | match |
| 4 | Hero box sign | `build_fig_hero.py` line 197, `fig_hero_price_curve_jair.png`, Description at line 94 | pragmatic minus epistemic in all three |
| 5 | Eight of eleven distinct budgets with intervals excluding zero, and three within sampling error | `results_budget_frontier_heldout_reference.csv` (primary rows) | 9/12, 8/11, 3 within, match |
| 6 | Largest shortfall is about a fifth of the reference | Bandit 0.75: 1.316 / 6.267 | 21%, match |
| 7 | Table 7 same-stream columns | `paper/tables/budget_frontier.tex` against the CSV | match to 2 dp |
| 8 | Tiger same-stream reference equals the zero-wrong-commit reward-only value | CSV heldout_reference 5.684 at every Tiger budget | confirmed (new item A) |
| 9 | Holm families are 107 (Tiger) and 83 (Diagnosis) after dropping undefined p-values (line 1436) | `results_tiger_stats.csv` 108 rows with 107 defined; `results_diagnosis_n4_stats.csv` 84 rows with 83 defined | match |
| 10 | TOST survives Holm across the three environments (line 707) | p = 0.0010, 0.0130, 0.0458, Holm-adjusted 0.003, 0.026, 0.0458 | all below 0.05 |
| 11 | CPOMDP caption's usage-matched weights 0.00, 0.45, 1.07 lie inside the stated flat runs | caption at line 724 | inside [0, 19.3], [0.316, 19.3], [0.72, 1.64] |
| 12 | Cost-per-test step shape | `results_price_cost_curves.csv` (round 1), line 633 | match |
| 13 | Cross-battery example 4.20 against 4.32 | `results_tiger.csv` 4.198, `results_sarsop_baseline.csv` 4.3232 | match |
| 14 | Figure 17 caption counts | `fig_belief_heatmap.png` panel titles (29, 14, 32, all correct) | match |
| 15 | Figure 10 footer semicolon | `fig_tileworld_comparison.png` | removed |
| 16 | Prose semicolons and vocabulary regressions in the revised text | `scratch_editor_clarity/style_scan.py` | no semicolons. The only vocabulary hits are "invalidates" and three existing uses of "validated" in a hedged or negated sense |
| 17 | "predeclared-margin" fully replaced | grep on both masters | 0 remaining. "fixed-margin" appears 4 times in JAIR |
| 18 | Propagation to `full_paper.tex` | grep for the w†, ŵ(B), eight-of-eleven, and cross-battery sentences | present in both masters |
| 19 | Appendix Q notation | tex lines 1706, 1711, 1718 | still k with no link to α (optional 9 not applied) |

## 7. Unresolved or newly introduced

- **Unresolved:** optional 9. Appendix Q's k is not tied to Proposition 4.2's α, contrary to the disposition.
- **Newly introduced, minor:** line 530 says "Every comparison the paper draws is made within one battery", which is too absolute given Table 7's committed-reference column (item B). Definition 4.1's item-two fallback sentence is long and duplicated (item C).
- **Residual, minor:** the Tiger same-stream intervals do not reflect wrong-commit variance, because the held-out stream contains none. The sign is robust, but the magnitudes may be overstated by up to about a factor of two (item A). The cost-budget paragraph keeps a graded-tilt narrative next to the step data, and repeats a range (item D).
- **Round 1 carry-over, waived:** length and section moves (optional 1), accepted as the authors' decision.

## 8. Would I give an unqualified Accept?

Yes. Nothing in the revised manuscript is wrong in a way that changes a conclusion, and every number I rechecked matches its artifact. The items in Section 7 are one-sentence edits suitable for copy-editing and do not need another review round.
