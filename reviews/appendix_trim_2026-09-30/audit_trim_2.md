# Adversarial audit of the appendix trim, C and X proposals (audit 2)

Date: 2026-09-30. Auditor scope: the 70 applied proposals whose ids start with C or X
(`proposals_C.json`, `proposals_X.json`, minus `skipped.txt`). No manuscript, code, or result
file was edited. Line numbers are current `paper/full_paper_jair.tex` lines.

Applied C ids: C01, C02, C05-C19, C22-C27, C29, C30, C32-C47, C50-C52, C55, C56, C62.
Applied X ids: X01, X03-X13, X19, X20, X22, X25-X28, X33, X35, X36, X38.

## Method

1. For each applied id, compared the proposal's `old` text (pre-trim `/tmp/jair_pre_trim.tex`,
   `/tmp/lncs_pre_trim.tex`) with the current text of both masters.
2. For every sentence removed, grepped both masters and `paper/tables/*.tex` for its numbers and
   claims to find a surviving copy, and read that copy to check it was not itself condensed away.
3. Checked rewritten numbers against the CSVs and producers (`results_rocksample_*.csv` and
   `_stats`, `results_cpomdp_frontier.csv`, `results_w_atlas.csv`, `experiments/run_w_atlas.py`,
   `tables/budget_frontier.tex`, `tables/discount*.tex`).
4. Checked every main-body pointer into an edited appendix subsection for what it promises
   (sec:collapse 501, dual 514, SARSOP 601, CPOMDP 608, frontier 672/676/680, distractor 693,
   atlas 706, Pareto 767, Tileworld 772/774, RockSample 791, Inspection 796, horizon 833,
   interpretation 840).
5. Parity. Differencing JAIR against LNCS gives the same result before and after the trim,
   except for the checklist line, which exists only in JAIR (C62). The main body is unchanged
   in both masters.
6. Conventions. Scanned all new texts for semicolons, prose colons, `\emph`, `\textit` and
   `\textbf`, "exact", "validat", "dissolv" and "honest". None was introduced. Every
   remaining "exact" is either a structural statement or appears in the retained phrase
   "near-optimal ... rather than exact/certified exact".

## Result

No finding, number, protected disclosure, or limitation was lost from the paper as a whole.
Every removed number has a surviving copy that I located and read. There is one partial
exception: the explicit statement that w*_succ spans 10 to 50 no longer appears in prose.
The values are still in the tables and at line 341 (defect 3). The protected disclosures all
survive:

- post hoc additions (frontier LP comparators, same-stream comparison)
- the retrospective TOST margin (1890)
- non-blind seeds
- the selection rule (X06 and the main body)
- simulation-matched POMCP comparisons (2124)
- w*_ret versus w*_succ
- POMCP fidelity gaps (1594-1596)

The Discussion's pointer for the roughly 21% failure rate (line 833) now resolves correctly to
`app:nearopt_horizon` (1299), where the criterion and the failure rate live. The defects below
are all local: lost antecedents, garbled sentences, two misdirected or over-stated clauses, and
one lost multiplicity qualifier.

## Defects

### 1. X04, line 1591 (moderate: lost antecedents)

Current text:
"we use MCTS-EFE, the UCB1 tree search defined in Appendix~\ref{app:interpretation}, where its
simulation-matched Tiger comparison against POMCP is reported. Exact EFE reaches $99.9\%$
success on Tiger at $H{=}6$ ($64$ ms per episode) under the MCTS battery's own
200-episodes-per-seed protocol rather than Table~\ref{tab:main}'s battery. The two solvers
differ in more than the leaf, so the two components that distinguish this search from a UCT
tree are ablated below."

What is wrong:
- The clause "which uses EFE as the leaf heuristic rather than random rollouts" was cut, so
  "the leaf" no longer has an antecedent.
- The POMCP numbers were moved away, so "The two solvers" no longer has one either.
- The exact-EFE sentence is left without anything to compare against.

Replacement:
"we use MCTS-EFE, the UCB1 tree search defined in Appendix~\ref{app:interpretation}, which uses
EFE as the leaf heuristic rather than random rollouts, and whose simulation-matched Tiger
comparison against POMCP is reported there. As a reference point, exact EFE reaches $99.9\%$
success on Tiger at $H{=}6$ ($64$ ms per episode) under the MCTS battery's own
200-episodes-per-seed protocol rather than Table~\ref{tab:main}'s battery. MCTS-EFE and POMCP
differ in more than the leaf, so the two components that distinguish this search from a UCT
tree are ablated below."

### 2. C37, line 1986 (moderate: non-sequitur and a garbled closing sentence)

Current text (1):
"The success-maximizing weight lies at the sweep's upper endpoint, $w{=}200$, on all five
environments, so $w{=}1$ is near-optimal for reward on three of them, not for success rate,"

What is wrong: success peaking at w=200 does not imply that w=1 is reward-near-optimal on
three environments. The cut removed the premise, which was that w=1 sits inside the
reward-maximizing tied bracket on three of five.

Replacement (1):
"The success-maximizing weight lies at the sweep's upper endpoint, $w{=}200$, on all five
environments, so $w{=}1$, although near-optimal for reward on three of them, is not
near-optimal for success rate,"

Current text (2):
"Within the same eleven-weight grid, the reward-maximizing bracket therefore moves from at most
$0.5$ on Testbed to $20$ on Tileworld, the grid search that the derived weight replaces on the
three environments where it attains the swept reward maximum."

What is wrong: the appositive "the grid search" attaches to "Tileworld" or to "the bracket",
and neither parse makes sense. The contribution statement it condensed is now ungrammatical.

Replacement (2):
"Within the same eleven-weight grid, the reward-maximizing bracket therefore moves from at most
$0.5$ on Testbed to $20$ on Tileworld. On the three environments where it attains the swept
reward maximum, the derived weight replaces that grid search."

### 3. X19, line 2084 (minor: conflation, and a lost range)

Current text:
"$w{=}1$ is tuned to neither the reward criterion $w^*_{\text{ret}}$ nor the success criterion
$w^*_{\text{succ}}$ used for Planning+IG in the main tables."

What is wrong: w*_ret and w*_succ are weights, not criteria. The prose statement that the
success-tuned weights span 10 to 50 was also dropped. The values survive only in the tables and
at line 341.

Replacement:
"$w{=}1$ is tuned to neither criterion, unlike the reward-maximizing weight $w^*_{\text{ret}}$
or the success-maximizing weight $w^*_{\text{succ}}$ ($10$ to $50$) used for Planning+IG in the
main tables."

### 4. C11, line 1896 (minor: misdirected pointer, undefined referent)

Current text:
"SARSOP's usage of $4.32$ sits just below the family's usage floor of $4.37$ (within one
seed-level SE, Table~\ref{tab:collapse-breadth}),"

What is wrong:
- `tab:collapse-breadth` contains neither the 4.37 floor nor its SE.
- The floor (4.368, SE 0.112) and the step (19.3, 43.9] are in `results_w_atlas.csv` and
  `tab:w-atlas`, which is built from `results_price_usage_curves.csv`.
- "The family's" is undefined within this subsection.

Replacement:
"SARSOP's usage of $4.32$ sits just below the Planning+IG usage curve's floor of $4.37$ (within
one seed-level SE, Table~\ref{tab:w-atlas}),"

### 5. C19, line 1922 (minor: dangling "also")

Current text:
"Diagnosis at $B{=}11.35$ and Bandit at $B{=}5.51$ also lie above the usage that reward alone
justifies,"

What is wrong: the sentences that established the other budgets lying above that usage (Tiger,
and Bandit at 7.79 and 10.07) were cut from this subsection, so "also" has no referent. The
cut content itself survives at line 670.

Replacement:
"Like Bandit's two larger interior budgets, Diagnosis at $B{=}11.35$ and Bandit at $B{=}5.51$
lie above the usage that reward alone justifies,"

### 6. X01, line 1450 (minor: lost antecedent)

Current text:
"On RS[7,8], the heavier weight's extra checking (57.47 steps, 18.26 checks per episode, versus
$w{=}5$'s 40.27/14.19)"

What is wrong: no "heavier weight" is named in the preceding sentence, which is about both
tuned weights on RS[7,4]. The numbers are correct against `results_rocksample_7x8.csv`
(57.468/18.262 versus 40.272/14.192, good rocks up 0.536, steps up 17.196).

Replacement:
"On RS[7,8], $w{=}10$'s extra checking (57.47 steps, 18.26 checks per episode, versus
$w{=}5$'s 40.27/14.19)"

### 7. C45, line 2049 (minor: lost multiplicity qualifier and a lost referent)

Current text:
"with $w{=}10$ falling to $+20.55$ on RS[7,8] ($p{=}0.003$) ... so this identifies the best of
three sampled weights rather than a grid-searched argmax, and we make no claim that $w{=}5$ is
the reward-maximizing weight over a denser sweep."

What is wrong:
- The disclosure "significant under the per-metric Holm family" was dropped.
- "This identifies" lost its referent, which was the removed sentence saying that w=5 attains
  the highest reward of the three weights on RS[7,8] and is not significantly different from
  w=1.
- Without that sentence, the closing "no claim that w=5 is the reward-maximizing weight"
  refers to a claim the paragraph no longer makes.

Replacement:
"with $w{=}10$ falling to $+20.55$ on RS[7,8] ($p{=}0.003$, significant under the per-metric
Holm family) ... so on RS[7,8], where $w{=}5$ attains the highest reward of the three weights
we ran and is not significantly different from $w{=}1$, this identifies the best of three
sampled weights rather than a grid-searched argmax, and we make no claim that $w{=}5$ is the
reward-maximizing weight over a denser sweep."

### 8. C14, line 1909 (minor: overclaim)

Current text:
"so a negative estimated gap reflects sampling or approximation error rather than a violation
of that bound."

What is wrong: the pre-trim text read "can reflect". The measured gap cannot establish which
error produced it, so the current wording asserts more than the evidence supports.

Replacement:
"so a negative estimated gap can reflect sampling error on either side or approximation error
in the reference rather than a violation of that bound."

### 9. C12, line 1901 (minor: definition turned into a non-definition)

Current text:
"A constrained POMDP is solved for the best reward attainable under a bound on an expected
cost, here sensing usage."

What is wrong: the pre-trim text defined the term ("is a POMDP solved for"). The current
sentence reads as a claim about a procedure, and the term is no longer defined at first use.

Replacement:
"A constrained POMDP is a POMDP solved for the best reward attainable under a bound on an
expected cost, here sensing usage."

### 10. C32, line 1959 (minor: agent-as-subject)

Current text:
"They ask whether EFE's untuned epistemic term buys anything over reward-only planning at the
same depth, and whether it gives anything up against a tuned information bonus."

What is wrong: "They" refers to the four agents, and agents do not ask questions.

Replacement:
"Together they test whether EFE's untuned epistemic term buys anything over reward-only
planning at the same depth, and whether it gives anything up against a tuned information
bonus."

### 11. C41, line 2026 (cosmetic: implicit figure reference)

Current text: "The figure's two weighted series are not tuned the way the main tables' weighted
agents are."

What is wrong: the nearest preceding paragraph does not name the figure.

Replacement: "Figure~\ref{fig:tw_scaling}'s two weighted series are not tuned the way the main
tables' weighted agents are."

## Checked and clean (selected)

- **X07.** The Diagnosis two-plateau finding and the harm from overestimation survive in full in
  `app:misspec`.
- **X25.** The atlas claims match `run_w_atlas.py` and `results_w_atlas.csv`:
  - The budgets sit at the floor plus 15% of the range and at the ceiling minus 15%.
  - B_EFE is at the floor on Tiger, near it on Tileworld, and partway up on Diagnosis and
    Bandit.
  - The inputs are `results_price_usage_curves.csv` and `results_price_interleaved_curves.csv`.
- **X01.** The RS[7,4] values 15.96, 14.27 and 14.56, with p of 3.2e-6 and 2.7e-7, are
  correct. POMCP on RS[7,8] is 15.07 versus 12.31, p=0.0016. POMCP on RS[11,11] has p >= 0.36
  against the family.
- **C19 cut content.** The best-target-mixture result at Bandit's gap budget (5.94 +/- 0.19
  versus 5.62 +/- 0.21, usage error 0.18 versus 0.09, not attributable to planning depth)
  survives at line 670 and in `tables/budget_frontier.tex`.
- **C14.** "B_EFE exceeds every sampled usage" is true. The maximum sampled usage is 9.817 on
  Diagnosis against 9.824, and 5.199 on Bandit.
- **C62.** The checklist still answers "No" with a justification, and it is JAIR-only.
  Section `sec:experiments` (line 483) points to `app:experimental_protocol`, which states all
  six differences.
- **Main-body pointers.** Every promise at 501, 514, 601, 608, 672-680, 693, 706, 767,
  772-774, 791, 796 and 840 resolves to retained content.
- **Formatting.** Runs of consecutive blank lines remain at the cut sites (1923, 1943-1947,
  2026-2029, 2045, 2072, 2118). LaTeX ignores them.
- **Parity.** All eleven defects above are present identically in `paper/full_paper.tex`, so
  each fix must be applied to both masters.
