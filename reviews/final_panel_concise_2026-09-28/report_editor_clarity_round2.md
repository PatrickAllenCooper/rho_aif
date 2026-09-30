# Associate-editor report, round 2 (lens: editor_clarity)

Manuscript: `paper/full_paper_jair.tex` (2208 lines) after batches 1 and 2 (`apply_batch1.py` and `apply_batch2.py`, cumulative `batch12.diff`).

What I checked:
- I verified each of my round-1 required changes against the current file text, not the authors' summary.
- I read all 23 changed lines in full.
- I checked every occurrence of the Proposition 3.2 threshold symbols and every unstarred `w_{\mathrm{thresh}}`.
- I extracted text from the rebuilt `paper/full_paper_jair.pdf` to confirm that the rendered text contains the edits and that pagination is unchanged.

## 1. Recommendation

Accept.

## 2. Summary

All three required changes from round 1 are made correctly in the file text, and so is the matching change to the LNCS master. The authors' four deviations from my proposed wording are each correct, and two of them improve on it. The adopted optional suggestions read well. The batches introduced no new cross-reference, notation, or calibration problem that I could find. The diff touches two main-body lines, 428 and 774. The rendered page layout around the end of the main body is identical to the version I reviewed.

One correction to my round-1 report: the Conclusion ends at the top of page 38, not on page 37, and the References begin later on the same page 38. This was already true of the version I reviewed, the batches do not change it, and the main body remains within the 40-page limit.

## 3. Strengths

- Cross-references now resolve to the right material. In round 1, seven pointers sent readers to a Discussion or Methodology that no longer holds the material. Each now names the appendix that does.
- The Proposition 3.2 thresholds are now written consistently as w*_thresh and w*_over. In the LNCS and JAIR masters combined, zero starred `lo`/`hi` threshold symbols remain. The unstarred bracket notation (w_lo, w_hi] of Definition PI-3 (lines 378, 432, and 572) was not touched. The star-dropping convention at line 428 is now scoped to "this corollary and its onset checks". Every unstarred `w_{\mathrm{thresh}}` falls inside that scope: lines 432 and 435, the corollary proof at lines 1755 and 1758, and the onset check at line 1869.
- The appendix wording on when w=1 is a good default now matches the careful wording in the main body and in Appendix Y.
- The audit-trail motivation at line 1511 is now accurate about what "task value" contains at H>1. It does more than my proposed sentence did, which would have claimed a cleaner decomposition than the code implements.

## 4. Required changes

None.

Round-1 disposition, checked against the current text:

1. **Stale cross-references: resolved.**
   - Line 1302 now points to `app:interpretation`. The citing sentence has been rewritten so that it no longer attributes a threshold prediction to Bandit: "a one-step reading would lead one to expect the least from $w{=}1$ ... The two-state threshold formula does not apply to Bandit, so no threshold is computed for it". This matches the target paragraph at line 2136.
   - Line 1511 opens with the audit's own motivation.
   - Line 1562 now reads "the MCTS-EFE comparison below". The paragraph it refers to follows at line 1598.
   - Line 1598 now reads "the UCB1 tree search of Appendix~\ref{app:interpretation}". The design is at line 2144.
   - Line 1958 points to `app:theory_agents`. Line 1745 there defines the information ratio as "the squared expected regret of taking that action divided by the information the action yields about the optimal commit". This is an accurate target, and more direct than `app:ids`, which I had proposed.
   - At line 1965, the leftover transition is deleted, and the paragraph ends on a complete sentence.
   - Line 958 cites Table~\ref{tab:pomcp} and Appendices S and Y. Both targets contain Tileworld POMCP or MCTS-EFE results.
2. **Threshold notation collision: resolved.**
   - Lines 1018, 1302, 1670, 1674, 1680, 1691, 1693, 2094, and 2132 now use w*_thresh and w*_over, the symbols Proposition 3.2 defines (lines 231 to 244).
   - The mapping sentence at line 1670 is gone, and line 2132 now says "written $w^*_{\mathrm{thresh}}$ and $w^*_{\mathrm{over}}$ there and in Table~\ref{tab:alpha_eta}".
   - Keeping the unstarred glyph only for Corollary PI-4 and its onset checks is a sound reading of my request. The convention sentence now states that scope.
   - The LNCS master has zero remaining `w^*_{\mathrm{lo}}` and `w^*_{\mathrm{hi}}`.
3. **Tileworld overgeneralization: resolved.** Line 1018 now reads "the regime in which the two-state interval analysis is most favorable to $w{=}1$. Within that regime, $w{=}1$ lies on the reward-maximizing plateau on Tiger and Diagnosis but is Pareto-dominated by $w{=}20$ on Tileworld". This agrees with `results_pareto_sweep.csv`. On Tileworld, w=20 gives -18.954 and 91.80%, against -21.528 and 72.04% at w=1. Tiger is tied at 5.3264 over [0.01, 20], and Diagnosis at -1.2624 over [0.5, 20].

## 5. Optional suggestions

1. **Appendix W.3, line 1882.**
   - Quote: "Proposition~\ref{prop:pi1} carries an offline bracket across a known reward-and-cost rescaling by multiplying it by the scale factor"
   - Issue: this is true of the count-budget bracket that the previous sentence names. For a cost budget, Proposition 4.2 also rescales the target itself: w*_cost(B; alpha) = alpha w*_cost(B/alpha; 1).
   - Fix: write "an offline count-budget bracket".
   - Placement: appendix.
2. **Appendix J, line 1302.**
   - Quote: "Proposition~\ref{prop:nearopt} bounds $w^*_{\mathrm{thresh}}$ at $H{=}1$ and $w^*_{\mathrm{over}}$ at $H{=}2$."
   - Issue: the proposition derives these thresholds in closed form rather than bounding them. The wording predates this batch.
   - Fix: use "derives".
   - Placement: appendix.
3. **Appendix P, line 1511.**
   - Issue: the new opening sentence is accurate but runs to 58 words.
   - Fix: split it after "deeper in the tree".
   - Placement: appendix.

Round-1 optional suggestions 6 (Figure 11 caption) and 8 (appendix roadmap) were declined. That is reasonable. Neither affects correctness.

## 6. Verification log

Diff scope and mirroring:
- `git diff --stat` shows 46 insertions and 46 deletions in each master.
- Both masters have the same 23 changed JAIR lines: 428, 774, 958, 1018, 1240, 1302, 1447, 1511, 1562, 1598, 1670, 1674, 1680, 1691, 1693, 1695, 1747, 1882, 1958, 1962, 1965, 2094, and 2132.
- No table or figure file changed, and no CSV changed.

Rendered PDF:
- `pdftotext` of the committed `paper/full_paper_jair.pdf` contains the new text. Probes found "multiplying it by the scale factor", "Where the Benchmarks Sit", "Pareto-dominated by", "handicapped POMCP", "Appendices S and Y", and the scoped convention sentence (which the extraction splits across a line-number break).
- The PDF contains no "??".
- Pages 36 to 38 are laid out the same as in `manuscript_jair.txt` from round 1: 118 pages, with the Conclusion finishing and the References starting on page 38.
- The PDF's modification time is 25 seconds earlier than the tex file's. The authors' audit reports a fresh rebuild whose extracted text is identical to the committed PDF, and my probes agree.

Notation:
- The combined count of `w^*_{\mathrm{lo}}` and `w^*_{\mathrm{hi}}` across the JAIR and LNCS masters is 0.
- Unstarred `w_{\mathrm{thresh}}` appears only at lines 428, 432, 435, 1755, 1758, and 1869, all inside the scope stated at line 428.
- Definition PI-3's bracket (w_lo, w_hi] at lines 378, 432, and 572 is unchanged.

Pointer targets:
- `app:interpretation` holds the Bandit paragraph (line 2136) and the MCTS-EFE design (line 2144).
- `app:theory_agents` begins at line 1739, and the IDS definition is at line 1745.
- `app:pomcp` holds `tab:pomcp` and the MCTS-EFE ablation.
- The retitled subsection "Where the Benchmarks Sit on Their Usage Curves" (line 1962, `sec:w_atlas`) no longer duplicates "The $w^*$ Atlas" (`app:w_atlas`, line 1624).

Numbers on edited lines:
- Line 774: Tileworld 8x8 gives Planning 1.4 ± 0.3 pp and EFE 69.4 ± 1.0 pp, from `results_tileworld_scaling.csv` (0.014 with SE 0.0029, and 0.694 with SE 0.0104). The units are now consistent within the sentence.
- Line 1240: the EFE-over-Myopic gap of +13.8 pp to +36.3 pp is now phrased as "consistent with".
- Line 1018: the Pareto values are as listed under section 4.

Calibration of the edits:
- Line 1695 now reads "In this benchmark sweep, EFE's advantage ... appeared only at $\gamma \geq 0.99$". This agrees with main-body line 840.
- Line 1747 now reads "the crossing threshold $w^*(B)$, estimated by the bracket of adjacent grid weights". This matches Definition PI-3.
- Line 1882 is consistent with Proposition 4.2 for count budgets (see optional suggestion 1).

Style: none of the changed lines adds a semicolon in prose or any new emphasis.

## 7. Would you recommend unqualified Accept if the required changes were made?

Yes. All required changes from round 1 are made correctly, no new required issue arose, and the remaining suggestions are optional wording polish.
