# Adversarial audit, batch 1 (ledger 9.17.57)

Auditor scope: every edit in `apply_batch1.py` (R1 to R16 plus the global rename), checked against the current masters, the rebuilt `paper/full_paper_jair.pdf` and `paper/full_paper.pdf`, `results/*.csv`, and `rho_aif/` / `experiments/` code. Line numbers refer to `paper/full_paper_jair.tex` after the batch.

Global checks:
- Both masters received identical edits. `git diff --word-diff=porcelain` changed-token streams for the two files are byte-identical (21 changed lines each, no unrelated changes).
- Both PDFs were rebuilt after the tex (JAIR 19:23:54, LNCS 19:24:23, tex 19:23:37). `pdftotext` shows zero `??` in either PDF. The JAIR log has no undefined-reference warnings. Rendered targets: R5 reads "Appendix S" (POMCP), R4 reads "Appendix Y" (interpretation), and R16 renders as "W.8 Where the Benchmarks Sit on Their Usage Curves".
- `tools/review_pipeline/verify_claims.py`: no hard failures. The 30 REVIEW items are pre-existing numbers on touched lines (for example 11.73 and 13.19 live in `results_rocksample_pomcp_budget.csv`, not the horizon CSV named nearest them, and 1.01/1.44 are threshold and unit-conversion values in `results_thresholds.csv`, Testbed `w_thresh_upper_nats` = 1.0078). None is introduced by this batch.
- Rename counts reconcile exactly. Before, the JAIR master had `lo` 9, `hi` 11, `thresh` 15, `over` 6 (starred). After, it has `thresh` 21, `over` 14, and zero `lo`/`hi` starred. For the lower threshold, 24 combined `thresh`+`lo` occurrences lose 2 in R8a (one of each) and net 1 in R8b (three occurrences become two), leaving 21. For the upper threshold, 17 combined `over`+`hi` occurrences lose 2 in R8a and net 1 in R8c (two become one), leaving 14. LNCS has the same counts.
- No bracket site was renamed. Every unstarred `w_{\mathrm{lo}}`/`w_{\mathrm{hi}}` (Definition PI-3 at line 378, Corollary PI-4 at 432, the staircase caption at 572, and figure producers `build_fig_hero.py` and `run_price_of_information.py`) is unchanged. Every renamed site (1018, 1302, 1670, 1674, 1680, 1691, 1693, 2132) is a Proposition 3.2 threshold, checked against the proposition statement (lines 231 to 244), the proof sketch (1665 to 1667), and `experiments/run_thresholds.py` (`w_thresh_lower`, `w_thresh_upper`). The table is inline tex, so no producer regenerates the old header.
- Style: no semicolons in any new prose, no emphasis added, and the "near-optimal/estimated", "consistent with", and "not the Lagrange multiplier" vocabulary is not violated by any edit.

## Per-edit verdicts

**R1 (Bandit trend, `sec:discussion` to `app:interpretation`): DEFECT (minor).** The target resolves correctly. The Bandit discussion is the paragraph starting "The widening with horizon of the basin..." in Appendix Y (line 2136). However, the unchanged remainder of the sentence says Bandit's "low reward asymmetry predicts only marginal $H{=}1$ sufficiency", and the target paragraph explicitly says the opposite of a prediction: "The formula therefore does not apply to it directly and we do not report a numeric $\alpha$ for it ... although we do not compute its threshold." The new pointer sends the reader to a passage that disclaims the prediction the citing sentence attributes to it. See defect 4.

**R2 (audit motivation): DEFECT (minor).** The new sentence says the Planning+IG score "decomposes each action's value into task value and weighted information gain". That is true only as an immediate-step split. `rho_aif/audit.py` (the `ActionAudit` docstring) states that `expected_task_value` "already embeds any deeper-recursion information bonuses from continuation values", and `planning_infogain.py` line 110 computes it as `total_score - weighted_ig` with only the root step's IG removed. So the "task value" component contains weighted information gain from deeper nodes whenever $H>1$. Before the edit, the paragraph only listed the record's fields, so the batch added a clean-decomposition claim that the code contradicts. See defect 3.

**R3 ("above" to "below"): OK.** The MCTS-EFE paragraph (line 1598) follows at line 1562 in the same appendix and does draw the distinction ("simulation-matched, not compute-matched").

**R4 (MCTS-EFE design to `app:interpretation`): OK.** Appendix Y's subsection "Approximate planning with MCTS-EFE" (line 2144) states the design: UCB1, observation-outcome children, in-tree exact IG, max-backup, EFE-greedy leaf, default constant.

**R5 (Tileworld caption to `app:pomcp`): OK.** Appendix S contains Table `tab:pomcp` (Tileworld POMCP at 1,000 simulations) and MCTS-EFE Tileworld-6x6 results: the ablation table, the sweep paragraph's 95.4% ± 0.6 and −22.26 against −25.02. The target is therefore true. The citation is slightly redundant, because `tab:pomcp` is inside `app:pomcp`. The MCTS-EFE Tileworld budget-scaling result (95.4% at 200 and 500 simulations, 32.3 against 14.8 observations) appears only in Appendix Y. See optional polish item b.

**R6 (IDS numerator to `app:theory_agents`): OK.** Appendix U.4 (line 1745) defines the IDS information ratio as "the squared expected regret of taking that action divided by the information the action yields about the optimal commit". This matches `rho_aif/agents/ids.py` (`ratio = delta*delta/info` and `delta = commit_value - (expected_post - cost)`). Appendix N (`app:ids`, line 1460) would also have been valid.

**R7 (leftover transition deleted): OK.** The paragraph at 1965 now ends on "...(reward scale, state count, horizon)." That is a complete sentence. No later text refers to the deleted "follows"/"Discussion after it" transition, and Appendix X begins with its own opener.

**R8a (mapping sentence deleted): OK.** The preceding sentence already names $w^*_{\mathrm{thresh}}$ and $w^*_{\mathrm{over}}$, so nothing depends on the deleted sentence.

**R8b, R8c (interpretation mapping): OK as edits, but the rename left a stale convention statement.** The new sentences read correctly. The deeper problem belongs to the rename and is recorded there.

**Rename (`w^*_lo`/`w^*_hi` to `w^*_thresh`/`w^*_over`): DEFECT.** All renamed sites are correct in meaning. However, two sentences that explained the old split notation now contradict the text:
- Line 428 (main body, just before Corollary PI-4): "We write $w_{\mathrm{thresh}}$ for the $w^*_{\mathrm{thresh}}$ of Proposition~\ref{prop:nearopt}, dropping the star to distinguish it from $w^*(B)$." This is unscoped.
- Line 2094 (Appendix X, Structural Inspection): "(the proposition's $w^*_{\mathrm{thresh}}$, written without the star from Corollary~\ref{cor:pi4} onward)".

Both sentences are unchanged. After the rename, the starred $w^*_{\mathrm{thresh}}$ appears at 1018, 1302, 1665 to 1693, and 2132, all after Corollary PI-4 in document order. The unstarred $w_{\mathrm{thresh}}$ appears at 432, 1755, 1758, 1869, and 2094. The paper therefore now uses both forms for the same quantity after the point where it says the star is dropped. Before the batch, the appendix symbol was $w^*_{\mathrm{lo}}$, a different glyph, so the "without the star from Corollary onward" statement was not contradicted by the same symbol. See defect 1.

**R9 (Tileworld overgeneralization): OK (optional polish).** The claim checks out against `results_pareto_sweep.csv`:
- Tiger's reward is exactly tied at 5.3264 for w in [0.01, 20].
- Diagnosis is tied at −1.2624 for w in [0.5, 20].
- On Tileworld, w=1 gives −21.5284 and 72.04%, while w=20 gives −18.954 and 91.80%. That is Pareto domination, and w=20 is the unique reward argmax.

The `sec:pareto` target (line 767) states exactly this. The phrase "most favorable to $w{=}1$" matches Appendix Y line 2138. Tileworld's α = 5 places it in the asymmetric regime (`tab:alpha_eta`). The only weakness is stylistic: the sentence opens with "There", which refers back to an abstract "regime", and it does not name the dominating weight. See optional polish item a.

**R10 (pp unit): DEFECT (minor, style).** `results_tileworld_scaling.csv` at 8x8 gives Planning a success rate of 0.014 with SE 0.00292 and 0.0 scans, and EFE 0.694 with SE 0.0104. `$1.4\% \pm 0.3$pp` matches the appendix house style (for example `$97.7\% \pm 0.5$pp`). But the same sentence then gives EFE as `$69.4\%\pm1.0$` with no unit and different spacing. These are the only two main-body instances of this pattern, and they now disagree within one sentence. See defect 6.

**R11 (informal aside deleted): OK.** "Second, the frozen planning horizon handicapped it." is grammatical and parallels "First, ...". Nothing later depends on the clause. The horizon numbers in the paragraph match `results_rocksample_pomcp_horizon.csv`: 12.516/15.601/15.239/15.615 at 16,384 simulations, 14.002 at 2,048, and H=10 lowest at both budgets. The +13.19 and +11.73 values are in `results_rocksample_pomcp_budget.csv`. One pre-existing nit: "it" follows a paragraph whose subject is "the search tree", so writing "POMCP" would be clearer. This is optional and was not introduced by the edit.

**R12 (price versus bracket): OK.** "the crossing threshold $w^*(B)$, estimated by the bracket of adjacent grid weights between which ... usage crosses that budget" matches Definition PI-3 (line 378). There, $w^*(B) := w^\dagger(B)$, and $w_{\mathrm{hi}}$ is the first grid weight after the largest weight with $U<B$, so the endpoints are adjacent on the grid. The edit does not overclaim, and the "estimated" wording is correct.

**R13 (scale-transfer consistency): DEFECT.** The new wording is "an offline bracket is valid only at a known reward scale". This says that a bracket is valid at any known scale, which Proposition PI-1 (lines 389 to 395) contradicts. Under an α rescaling of rewards and costs, the count-usage curve satisfies $U_\alpha(\alpha w) = U(w)$, so the crossing moves from $w^*$ to $\alpha w^*$. A bracket solved at scale 1 is therefore wrong at a known α unless it is multiplied by α. The original wording, "the scale it was solved at", was literally true. It conflicted with Section 4.6 only by omitting that a known rescaling can be transferred. The replacement swaps that omission for a false reading. Separately, `sec:pi5` (line 445) does not "argue" the stated validity claim. It says only that "a reward-scale change moves the count-budget crossing" and that the controller adjusts "without a fresh grid sweep". See defect 2.

**R14 (discount threshold scope): OK.** `results_discount_stats.csv` confirms it. On Diagnosis, EFE's success advantage over Planning is Holm-significant at γ = 0.99 and 1.0 (p = 1.7e-5 and 4.1e-6) and null at 0.95 and 0.90 (p = 0.96). On Bandit it is significant at 0.99 and 1.0 (p = 4.1e-6 and 2.8e-5) and null at 0.95 and 0.90 (p = 0.95). Neither environment has a Holm-significant reward difference at any γ, so "advantage" means success, as Appendix Y says explicitly. The calibrated wording ("In this benchmark sweep", "appeared only at", "consistent with") matches the Discussion's "not a general regime boundary". The observation counts 9.68 and 5.83 in the same paragraph match the CSV (9.6784 and 5.8328).

**R15 ("confirming" to "consistent with"): OK, but a sibling overclaim in the same paragraph was left.** The Diagnosis +8.3 pp figure matches `results_diagnosis_n4.csv` (0.9716 − 0.8882 = 0.0834). At H=2, `results_scaling.csv` gives EFE and Planning identical at N=2 and N=4, 84.08 against 83.92 at N=8, and 77.12 against 77.36 at N=16, all as the text states. Two sentences later, the same paragraph still reads "confirming that deeper planning is increasingly valuable as state spaces grow". That rests on the same descriptive, single-battery, fixed-H evidence (the EFE-over-Myopic gap grows monotonically from 13.84 to 24.24, 32.96, and 36.28 pp). See defect 5.

**R16 (duplicate atlas heading): OK.** The W.8 title is distinct from T.3 "The $w^*$ Atlas". The label `sec:w_atlas` is kept, and it has zero `\ref` uses in either master. Every atlas citation points to `app:w_atlas`. The first sentence of the paragraph ("records where each benchmark sits on its own usage curve") matches the new title.

## Defects and exact proposed replacements

All replacements are exact strings, unique (count 1) in each master, and should be applied identically to `paper/full_paper_jair.tex` and `paper/full_paper.tex`.

1. **Rename left a contradicted star convention (required).** Line 2094 (Appendix X):
   - Old: `drives the lower threshold $w_{\mathrm{thresh}}$ downward (the proposition's $w^*_{\mathrm{thresh}}$, written without the star from Corollary~\ref{cor:pi4} onward), and`
   - New: `drives the lower threshold $w^*_{\mathrm{thresh}}$ downward, and`

   Line 428 (main body, net +18 words, fits on the existing line budget):
   - Old: `We write $w_{\mathrm{thresh}}$ for the $w^*_{\mathrm{thresh}}$ of Proposition~\ref{prop:nearopt}, dropping the star to distinguish it from $w^*(B)$.`
   - New: `In this corollary and the onset checks that test it (Appendices~\ref{app:theory_budget_proofs} and~\ref{sec:prop2exp}), we write $w_{\mathrm{thresh}}$ for the $w^*_{\mathrm{thresh}}$ of Proposition~\ref{prop:nearopt}, dropping the star to distinguish it from $w^*(B)$.`

   Both labels exist in both masters. If main-body length is frozen, apply the 2094 change alone. The remaining unscoped sentence at 428 is then a mild inconsistency rather than a contradiction.

2. **R13 states a scale-transfer claim that Proposition PI-1 contradicts (required).** Line 1882:
   - Old: `Section~\ref{sec:pi5} argued that an offline bracket is valid only at a known reward scale, so a deployed controller must re-adapt online after an unannounced rescale, and it left the speed of that re-adaptation to be measured.`
   - New: `Section~\ref{sec:pi5} noted that a reward-scale change moves the count-budget crossing. Proposition~\ref{prop:pi1} carries an offline bracket across a known reward-and-cost rescaling by multiplying it by the scale factor, but not across an unannounced one, so a deployed controller must then re-adapt online. That section left the speed of that re-adaptation to be measured.`

3. **R2 asserts a clean task/information decomposition that the code does not implement (minor).** Line 1511:
   - Old: `The Planning+IG score decomposes each action's value into task value and weighted information gain, but nothing in the main results exposes that decomposition directly.`
   - New: `At the root of each decision, the Planning+IG score of an observation action is its weighted immediate information gain plus an expected task value that carries the sensing cost and the value of continuing, including any information bonuses deeper in the tree, but nothing in the main results exposes that decomposition directly.`

4. **R1 now points to a passage that disclaims the prediction attributed to it (minor).** Line 1302:
   - Old: `where the low reward asymmetry predicts only marginal $H{=}1$ sufficiency yet multi-step EFE performs well in practice.`
   - New: `where a one-step reading would lead one to expect the least from $w{=}1$ yet multi-step EFE performs well in practice (the two-state threshold formula does not apply to Bandit, so no threshold is computed for it).`

5. **R15 left a sibling "confirming" overclaim in the same paragraph (minor).** Line 1240:
   - Old: `confirming that deeper planning is increasingly valuable as state spaces grow`
   - New: `consistent with deeper planning becoming more valuable as state spaces grow`

6. **R10 made the units inconsistent within one sentence (minor, style, main body, length-neutral).** Line 774:
   - Old: `while EFE achieves $69.4\%\pm1.0$.`
   - New: `while EFE achieves $69.4\% \pm 1.0$pp.`

## Optional polish (not defects)

a. R9, line 1018. Replace `is Pareto-dominated on Tileworld (Section~\ref{sec:pareto}).` with `is Pareto-dominated by $w{=}20$ on Tileworld (Section~\ref{sec:pareto}).`, and replace `$w{=}1$. There $w{=}1$ lies on` with `$w{=}1$. Within that regime, $w{=}1$ lies on`.

b. R5, line 958. The MCTS-EFE Tileworld budget-scaling result is only in Appendix Y. To cover it, write `reported in Table~\ref{tab:pomcp} and Appendices~\ref{app:pomcp} and~\ref{app:interpretation}.`

c. R11, line 1447. `handicapped it.` could be `handicapped POMCP.`, because the preceding paragraph's subject is the search tree.

## Batch 2 audit

Scope: the ten guarded replacements in `apply_batch2.py` (D1a, D1b, D2 to D6, Pa to Pc), checked against the current masters, `batch12.diff`, a fresh rebuild, `rho_aif/audit.py`, `rho_aif/agents/planning_infogain.py`, `rho_aif/agents/efe.py`, `rho_aif/agents/inspection_agents.py`, Proposition PI-1 (JAIR lines 384 to 395), and the CSVs. Line numbers refer to `paper/full_paper_jair.tex`.

Global checks:
- **Both masters are identical.** The changed-token streams (`git diff --word-diff=porcelain`) of the two files are byte-identical, 46 changed lines each. Every new string occurs exactly once in each master. `batch12.diff` is byte-identical to the current `git diff` of the two masters.
- **The PDFs match the current source.** The masters' modification time (19:38:12) is later than the committed PDFs (JAIR 19:37:47, LNCS 19:37:50). I therefore rebuilt both from the current source in a scratch copy under `/tmp`: JAIR with pdfLaTeX, Biber, and two more pdfLaTeX passes; LNCS with Tectonic. Neither build has an undefined reference. JAIR is 117 pages. For both, the `pdftotext` output of the fresh build is identical to that of the committed PDF, so the committed PDFs reflect the current source.
- **Style.** No semicolons appear in any added prose. There is no added emphasis, and the edits do not violate the project's claim-calibration vocabulary.

### Star convention for the Proposition 3.2 lower threshold

The convention is now consistent everywhere the Proposition 3.2 lower threshold appears.
- **Unstarred `w_{\mathrm{thresh}}`.** This form appears only at 428 (the convention sentence), 432 (Corollary PI-4), and 435 (its proof sentence). It also appears at 1755 and 1758, in "Proof and numerical check of the usage-onset corollary", which is the corollary's proof and implementation check. The last site is 1869, in `sec:prop2exp`, the onset check on the positive-threshold instances. All of these fall inside "this corollary and its onset checks". The main body has no unstarred use outside 428 to 435.
- **Starred `w^*_{\mathrm{thresh}}`.** Every other occurrence is starred: the proposition itself (231 to 244), the proof sketch and threshold appendix (1665 to 1693), 1302, 2094, and 2132. None of these sits in the corollary or an onset check.
- **Figures.** The only rendered threshold glyph is the unstarred `w_{\mathrm{thresh}}` legend in `run_price_of_information.py` line 1304, which draws the onset-check figure (`fig:prop2`, inside `sec:prop2exp`). It is therefore in scope.
- **Stale convention sentences.** The old "written without the star from Corollary onward" sentence is gone, and no other sentence states a star convention.

### Per-edit verdicts

**D1a (line 2094): OK.** The sentence now reads "drives the lower threshold $w^*_{\mathrm{thresh}}$ downward, and once that threshold falls below zero". The continuation ("that threshold", "the interval's lower endpoint") still reads correctly.

**D1b (line 428, shortened scoping phrase): OK.** "In this corollary and its onset checks" covers every unstarred site listed above. The phrase refers forward, because the corollary begins on the next line, but the sentence directly introduces it, so the reference is unambiguous. The main-body length cost is 6 words.

**D2 (line 1882): OK.** It is true against Proposition PI-1. Scaling rewards and costs by α and the weight by α preserves the action at every belief, so $U_{\mathrm{count},\alpha}(\alpha w) = U_{\mathrm{count}}(w)$. A count-usage bracket $(w_{\mathrm{lo}}, w_{\mathrm{hi}}]$ therefore becomes $(\alpha w_{\mathrm{lo}}, \alpha w_{\mathrm{hi}}]$ at a known α. The sentence scopes itself to the count-budget crossing, which matches the experiment (Diagnosis, count target $B{=}8$, ×10 reward-and-cost rescale).
- "Section~\ref{sec:pi5} noted that a reward-scale change moves the count-budget crossing" quotes line 445 almost verbatim.
- "That section left the speed of that re-adaptation to be measured" matches line 461, which says that `sec:dual_multiseed` evaluates recovery empirically and that the proposition does not justify resets.
- No other sentence in either master still carries the old "valid only at" wording.

**D3 (line 1511): OK.** It matches the code.
- In `planning_infogain.py`, `_expected_value_of_observe` computes `-obs_costs[k] + sum_o p(o) * discount * continuation_value + w * info_gain`. The continuation comes from the recursive `_evaluate`, whose observe branches carry their own `w * IG` terms. `_decision_candidates` records `expected_task_value = total_score - weighted_ig`, subtracting only the root step's IG. So the task value carries the sensing cost and the (discounted) continuation, including deeper information bonuses, exactly as stated.
- `efe.py` uses the same split, with `total_score = -G` and `expected_task_value = total_score - info_gain`. `audit.py`'s docstring states the embedding explicitly.
- The sentence is scoped to observation actions, which is correct: commit and move candidates have zero IG and task value equal to the total.
- The following sentences (the record's fields and "components sum correctly") remain accurate.

**D4 (line 1302): OK.** The new sentence matches the target paragraph in Appendix Y (line 2136). There, the one-step analysis "would lead one to expect the least from $w{=}1$", "the formula therefore does not apply to it directly", "we do not compute its threshold", and multi-step EFE reaches 86.9% (`results_bandit.csv`, as in Table `tab:main`). The deviation from my proposed wording, which splits the disclaimer into its own sentence, is fine. The split sentence avoids a parenthesis and is not ambiguous.

**D5 (line 1240): OK.** The claim is consistent with `results_scaling.csv`. The EFE-over-Myopic success gap is 13.84, 24.24, 32.96, and 36.28 pp at N = 2, 4, 8, and 16, which is monotone, and the endpoints are the stated +13.8 and +36.3. The rest of the sentence ("independent of whether EFE or reward-only Planning supplies that depth") still holds, since EFE and Planning are identical or within SE at H=2.

**D6 (line 774): OK.** Both values in the sentence now use the `$x\% \pm y$pp` form. Checked against `results_tileworld_scaling.csv` at 8x8: EFE has a success rate of 0.694 with SE 0.0104, and Planning 0.014 with SE 0.0029. The edit is length-neutral.

**Pa (line 1018): OK.** Checked against `results_pareto_sweep.csv`. On Tileworld, w=20 gives −18.954 and 91.80% against −21.5284 and 72.04% at w=1, so w=20 is better on both axes. Tiger is tied at 5.3264 over [0.01, 20], and Diagnosis is tied at −1.2624 over [0.5, 20]. "Within that regime" now refers clearly to the asymmetric-penalty regime of the previous sentence.

**Pb (line 958): OK.** Appendix S (`app:pomcp`) holds Table `tab:pomcp`, the ablation, and the exploration sweep. Appendix Y (`app:interpretation`) holds the MCTS-EFE Tileworld-6x6 budget-scaling result: 95.4% at 200 and 500 simulations, 32.3 against 14.8 observations, and POMCP at 10.7% and 5.6%. The rendered caption reads "Appendices S and Y".

**Pc (line 1447): OK.** The subject is now explicit. The rest of the paragraph ("the frozen $H{=}10$", "make POMCP worse") agrees with it.

### Batch 2 defect list

None.

## Batch 3-4 audit

Scope: `apply_batch3.py` (G1 to G3) and `apply_batch4.py` (F1 to F3), as applied to both masters in the working tree. POMCP hunks ignored. Line numbers are JAIR (`full_paper_jair.tex`), with LNCS lines in parentheses. Numbers were recomputed from `results/results_budget_frontier_fresh_seed_replication.csv` (per-seed gaps, SEs, and t(0.975, 9) intervals all recompute to the stored columns), the held-out columns it copies from `results_budget_frontier_heldout_reference.csv`, `results_budget_frontier.csv`, `results_budget_frontier_curve.csv`, and `results_cpomdp_frontier_heldout.csv`. No experiment was rerun.

### Per-edit verdicts

**G1 (line 1882, LNCS 2186): OK.** Proposition PI-1 (line 390) gives U_count,alpha(alpha w) = U_count(w), so a count-budget crossing and its bracket scale by alpha. A cost-budget bracket would also need B rescaled, so "count-budget" is the correct and tighter qualifier. It also matches the preceding sentence's "count-budget crossing".

**G2 (line 1302, LNCS 1608): OK.** Part (a) of Proposition `prop:nearopt` gives a closed form for w*_thresh (line 233), so "derives" is accurate, and "bounds" was not. The same verb is used at line 1555.

**G3 (line 1511, LNCS 1816): OK.** The three sentences carry the same content as the original. The antecedent of "That task value" is unambiguous.

**F1 (line 676, LNCS 642): OK.** The fresh CSV has 9 of 12 rows with `fresh_ci_hi < 0` and 8 of 11 after dropping Tiger's gap row, which duplicates its 0.5 row (same budget 5.07, same mixture, identical per-seed gaps). Held-out Diagnosis shortfalls are 0.5 and 0.75. Fresh Diagnosis shortfalls are 0.25 and 0.75. "Changes which Diagnosis budgets fall short" is true. The deleted sentence's list of zero-including rows still appears in the appendix (line 1935), and nothing later in the main body depended on it. `app:frontier_details` resolves to the subsection that contains F3.

**F2 (line 80, LNCS 49): DEFECT (D1).** "Two Tiger comparisons are sensitive to rare errors" is supported by the main body's sensitivity calculation (line 678: the smallest shortfall reverses, the middle one nearly vanishes). Dropping "absent from the held-out episodes" is also fine. See the note below. The problem is "individual Diagnosis rows do not [replicate]": see D1.

**F3 (line 1939, LNCS 2243): DEFECTS (D1 to D5).** Verified as correct:
- Seeds 12 to 21, 100 episodes, 9 degrees of freedom. This matches `FRESH_SEEDS = range(12, 22)`, `EPISODES = 100`, and `tcrit = t.ppf(0.975, len(FRESH_SEEDS) - 1)`. The held-out intervals use 4 df: for example, the Diagnosis 0.25 half-width 0.782 equals 2.776 times its SE of 0.28.
- The lineage replay to 1e-9 is recorded in the ledger (`full_paper_plan.md`, "Diagnosis frontier robustness"). It is not independently reproducible here without running episodes.
- Nothing is refit. The script reads the committed (w_lo, w_hi, q) and asserts that the reference support matches.
- 9 of 12 rows, 8 of 11 distinct budgets, and 11 of 12 negative means. The only positive mean is Diagnosis 0.5, at +0.0206.
- All three Tiger shortfalls and all three Bandit shortfalls (0.5, 0.75, gap) replicate. Bandit 0.25 includes zero, with CI [-0.319, +0.093].
- Diagnosis 0.5 is -0.757 held-out and +0.0206 ± 0.288 fresh. Diagnosis 0.25 is -0.0295 held-out (CI hi +0.75) and -0.560 ± 0.236 fresh. The ± convention is SE, matching line 1935's "-0.03 ± 0.28".
- The 0.5 mixture has w_lo = 0.139, w_hi = 0.316, and q = 0.938. `run_weight` plays w_hi with probability q, so "plays w=0.316 with probability 0.94" is correct. The calibration curve's Diagnosis usage is 9.772 at every grid weight from 0.316 to 19.31, which contains w=1.
- The reference support is lam=0 with q=0.9112 and lam=0.489 with q=0.0888. Line 1916 says lambda=0 is the ordinary SARSOP solve.
- A wrong diagnosis is -50 against +10 (`diagnosis.py`), which is 60 relative to a correct one.
- There are no semicolons, no emphasis, and no use of "exact" or "validates". The text is identical in both masters. I checked by `diff` of the F1, F2 (minus the `\textbf{Results:}` prefix), and F3 lines.

Note (inference, not a defect): Tiger fresh seed 17 has per-seed gaps of -0.30 at 0.25 but +0.24 and -0.08 at 0.5 and 0.75, against typical values of -0.7 and -1.05. All Tiger rows share the same lam=0 reference per seed, and a correct-commit episode cannot raise family reward by about 94 units per 100 episodes. The likeliest explanation is one reference wrong commit on seed 17, with the 0.25 mixture also erring once. The rare event therefore appears to occur in the fresh Tiger episodes, and the 0.5 and 0.75 shortfalls replicate anyway. The CSV has no success column, so this cannot be confirmed without episodes. "The Tiger rare-event qualification above still applies" is not false, but the qualification's premise (no wrong commit in the 500 held-out episodes) is specific to the held-out stream. Optional: add a success or wrong-commit column in a future run of the script.

### Batch 3-4 defect list

1. **D1 (substantive), JAIR 1939 / LNCS 2243, and abstract JAIR 80 / LNCS 49.** "Diagnosis's rows do not replicate individually." and "individual Diagnosis rows do not". Diagnosis's 0.75 shortfall replicates: held-out -1.104 (CI hi -0.495), fresh -0.818 ± 0.280 (CI [-1.451, -0.185]). The gap row includes zero on both streams. Only the 0.5 and 0.25 rows change classification. A reader will take both sentences to say that no Diagnosis row replicates.
   - Appendix replacement: `Diagnosis's rows replicate only in part. Its $0.75$ shortfall replicates at $-0.82 \pm 0.28$, but its $0.5$ shortfall of $-0.76$ becomes $+0.02 \pm 0.29$,` (the rest of the sentence unchanged).
   - Abstract replacement: `The count replicates on fresh seeds but individual Diagnosis rows do not,` becomes `The count replicates on fresh seeds but not every Diagnosis row does,`.
2. **D2 (disclosure), JAIR 1939 / LNCS 2243.** "The count replicates. Intervals exclude zero at nine of the twelve rows, again eight of the eleven distinct budgets". The Diagnosis gap row's fresh interval is [-0.9267, +0.00019]. It includes zero by 0.0002, with a mean of -0.46, so the matching count of eight depends on that margin. One flip gives nine of eleven. Replacement: after `now excludes it at $-0.56 \pm 0.24$`, insert `, and its gap target includes zero only narrowly, at $-0.46 \pm 0.20$`.
3. **D3 (overclaim), JAIR 1939 / LNCS 2243.** "A wrong diagnosis costs $60$, so a few rare errors move a five-seed mean, and the replication attributes the discrepancy to that seed-set variation." A non-blind replication (the paragraph itself says so two sentences later) cannot attribute a discrepancy to a cause. Error counts are also not recorded in the CSV. "Costs 60" is relative to a correct diagnosis (-50 against +10, `diagnosis.py`), matching the Tiger wording "110 ... against a correct one". Replacement: `A wrong diagnosis costs $60$ relative to a correct one, so a few errors can move a five-seed mean, and the replication is consistent with seed-set variation as the source of the discrepancy.`
4. **D4 (minor clarity), JAIR 1939 / LNCS 2243.** "measures how far these intervals depend on the five held-out seeds". The paragraph directly above ("The reading is therefore this") contains no intervals. The same-stream intervals are two paragraphs up. Replacement: `measures how far the same-stream paired intervals above depend on the five held-out seeds`.
5. **D5 (minor wording), JAIR 1939 / LNCS 2243.** "against a reference that is $0.91$ of the unpenalized SARSOP policy" can be read as a reward ratio. The CSV's `reference_support` is `lam=0:q=0.9112|lam=0.489:q=0.0888`, a mixture weight. Replacement: `against a reference that plays the unpenalized SARSOP policy with probability $0.91$`. Relatedly, "Its $0.5$ shortfall of $-0.76$" signs a shortfall that the paragraph at line 1935 reports as the positive "$0.76$". The D1 replacement's `$-0.76$` can instead read `Its $0.5$ paired gap of $-0.76$`.

G1, G2, G3, and F1 carry no defects. All five defects are in F3, and D1 also touches F2. No file outside this directory was modified.
