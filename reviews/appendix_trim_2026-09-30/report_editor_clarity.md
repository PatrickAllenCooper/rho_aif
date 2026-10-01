# Editor report (clarity, structure, and JAIR format)

Lens: action editor for the Journal of Artificial Intelligence Research. Manuscript: `paper/full_paper_jair.tex`, rendered `paper/full_paper_jair.pdf` (106 pages, pdfTeX, 30 September 2026).

## 1. Recommendation

Accept with minor revisions.

## 2. Summary

The paper gives an engineer a way to set the information-gain weight of a rho-POMDP policy from an expected sensing-usage target. The price is a crossing of the usage curve, estimated on a finite grid by a bracket, with a per-episode mixture of the bracket endpoints when the target falls in a gap. A second thread shows that a specified recursive, reward-based Expected Free Energy objective is the same family at weight one, under stated structural and scoring assumptions. Experiments separate meeting that usage target from maximizing reward under a cap, and they locate the untuned weight among reward-only planning, tuned information gain, and near-optimal offline references. The scope is stated in the introduction, the discussion, and the conclusion.

## 3. Strengths

The contribution is significant for JAIR's audience. It sits at a real intersection of POMDP planning, belief-dependent rewards, and active inference, and it answers a design question those literatures usually leave as a tuned coefficient. The distinction between an expected-usage target and a usage cap is carried from the abstract through the experiments.

The main body stands alone. References begin on page 38, inside the journal's practical length. A reader who stops there still gets the definitions, the scale and controller results, the held-out calibration table, the core comparison, RockSample and Inspection, and an honest discussion of where the weight fails. Proofs, full agent tables, and robustness studies are appended, and the introduction says so.

The structured abstract uses Background, Objectives, Methods, Results, and Conclusions. The reproducibility checklist is a compiled appendix and is labeled as review material. No section or subsection opens directly on a lower heading. The source has a short lead-in before every subsection I checked.

The figures I inspected are doing editorial work. Figure 1 makes the crossing, the bracket, the mixture, and the weight-one point visually distinct. Figure 7 separates count targets, cost targets, and the cost-per-test ratio, and it states that the ratio has no uncertainty estimate. Table 7 (Structural Inspection) is readable at page width, with bold reserved for the best accuracy and the best reward. The build log has no overfull boxes.

Cross-references I followed land on the promised object: the observe-then-commit schematic is in Appendix U.1, the RockSample constrained-reference failure is in Appendix U.7, the six RockSample differences are in Appendix V, the nat-canonical comparison is in Appendix R, and the Tileworld table and trajectory are in Appendix X.3.

## 4. Required changes

### 4.1 Keep each appendix table inside its own section

Quoted text (`paper/full_paper_jair.tex`, lines 893–896):

```
\section{Full Per-Environment Results}
\label{app:full_tables}

\begin{table}[htbp]
```

Quoted text (lines 996–999):

```
\section{Two-State Testbed}
\label{app:testbed}

\begin{table}[htbp]
```

Quoted text (lines 1458–1459):

```
vanishes. Table~\ref{tab:ids} reports a matched comparison ... and EFE.

\begin{table}[htbp]
```

In the rendered PDF the reading order breaks. On page 41, Tables 8–10 (Tiger, Diagnosis, Bandit) appear first. The heading "B Full Per-Environment Results" is printed only after those tables, and the next line is already "C Two-State Testbed". Appendix C's prose then runs before its own table. Tables 11 and 12, which still belong to Appendix B, and Table 13, the testbed table, follow on page 42. Separately, Table 23 (the IDS comparison, Appendix N) is printed on page 61 inside Appendix O, after the proper-scoring discussion has already started. A referee who follows the appendix letter does not meet the table with the section that discusses it.

Replacement: put a short lead sentence between each of these headings and its first table, change those table placements from `[htbp]` to `[!ht]`, and insert `\FloatBarrier` (package `placeins`) immediately before every later appendix `\section`. After that rebuild, Tables 8–12 must sit under heading B and before heading C, Table 13 under heading C, and Table 23 under heading N and before heading O.

### 4.2 Point the discussion at the appendices that hold the comparisons

Quoted text (line 840):

```
Appendix~\ref{app:interpretation} retains the detailed horizon, transfer, and discount comparisons.
```

Appendix Y (`app:interpretation`) holds the transfer table and a short discussion of planning depth. The horizon study is Appendix J (`app:nearopt_horizon`). The discount sweep is Appendix K (`app:discount`). Appendix Y mentions both and then sends the reader onward. The sentence promises that Y itself retains all three.

Replacement:

```
Appendix~\ref{app:nearopt_horizon} retains the horizon study, Appendix~\ref{app:discount} the discount comparison, and Appendix~\ref{app:interpretation} the weight-transfer results.
```

## 5. Optional suggestions

Appendix Y.3 restates the MCTS-EFE Tiger, Diagnosis, and Tileworld numbers, the ablation, and the exploration-constant sweep that Appendix S already reports, including the same simulation counts and the same attribution to the joint leaf configuration. Keep the design description in one place and leave the other as a pointer.

Appendices M and X.4 are both titled as RockSample interleaved observe-act results. M is the POMCP diagnostic. X.4 is the leaf rule, depth check, and heuristic comparison. Distinct titles would match the split the main text already describes.

Definition 4.1 is a single paragraph that defines the level set, the crossing threshold, the grid bracket, the tolerance, and the endpoint mixture. A displayed list, one object per item, would make the main-text argument easier to check. Figure 9's caption repeats much of that machinery. The plot is legible. A shorter caption would return space to the staircase.

Several appendix subsections are sentence case ("Observe-then-commit structure and EFE scope", "The information-unit weight and tuning", "Zero-shot weight transfer"). JAIR's final-preparation instructions ask for capitalized section and subsection titles. That can wait for camera-ready.

## 6. What you verified

| Claim or requirement | Where checked | Result |
| --- | --- | --- |
| Structured abstract with the five JAIR headings | `full_paper_jair.tex` lines 76–82 | Present |
| Reproducibility checklist compiled as an appendix and excluded from the accepted version | lines 2133–2136; PDF page 103, Appendix Z | Present and labeled correctly |
| No section opens on a subsection | Heading scan of `full_paper_jair.tex` | Every section has prose before its first subsection |
| References start near page 38, main body within the practical limit | PDF pages 37–38 | Conclusion, competing interests, and acknowledgments end on page 38. References begin on that page |
| Appendix B/C reading order | PDF pages 41–42 | Tables 8–10 precede heading B. Heading C follows heading B with no B prose between them. Tables 11–13 follow C's prose |
| IDS table stays in Appendix N | PDF page 61, raw text around Table 23 | Table 23 is printed after Appendix O has begun |
| Discussion pointer for horizon, transfer, and discount | line 840; PDF page 37, "Appendix Y"; heading map J, K, Y | Y holds transfer. Horizon is J. Discount is K |
| Schematic of the observe-then-commit loop | line 166; Appendix U.1, `fig:otc_loop` | Present where promised |
| Shallow RockSample reference limitation | line 468; Appendix U.7 | Reported there, with the depth-3 check and the zero-or-one-rock outcome |
| Six RockSample differences | line 483; Appendix V | Appendix V states the cost, map, discount, exit, frozen quality, and sensor-range differences |
| Tileworld full comparison and trajectory | lines 773 and 1991–2020 | `tab:tileworld` and `fig:tw_comparison` are inside `app:tileworld_details` |
| Tiger appendix row matches the CSV | Table 8; `results/results_tiger.csv` EFE row | Listens 4.198 prints as 4.20, success 0.9944 as 99.4%, reward 5.186 as +5.19 |
| Held-out usage within 0.13 observations | Abstract; Table `tab:budget_frontier_main` | Largest absolute gap among the twelve attainable rows is 0.12 (Diagnosis at B = 11.35) |
| Figure and table rendering | PDF pages 2, 22, 25, and 36 | Figure 1, Figure 7, Figure 9, and Table 7 are legible. No overfull boxes in `full_paper_jair.log` |
| Dangling `\ref` targets | Label scan, including `\input` table files | Every cited label resolves. Nine table labels live in `paper/tables/` and are input by the master |

## Re-review (2026-09-30)

**Revised recommendation: Accept.** No remaining required changes.

I checked the source and the PDF rebuilt at 20:57 MDT the same day (111 pages). Both required changes are in the rendered article, and the ten sentence-case appendix subsections are now title case.

**4.1, float order.** `placeins` is loaded, and after `\appendix` every `\section` is redefined to emit `\FloatBarrier` first. Appendix B opens with the sentence "This appendix reports the full agent set for Tiger, Diagnosis, Bandit, and the two Tileworld grids, one table per environment." In the PDF the order is heading B, that sentence, Tables 8 through 12, then heading C. Table 13 follows heading C and precedes the next appendix. The IDS table (Table 23) follows heading N and the paragraph that introduces it, and the IDS discussion closes before heading O. Table 13 still floats to the top of the next page and splits one sentence of Appendix C. It stays inside C, so the required placement holds.

**4.2, discussion pointer.** Line 841 now reads: "Appendix~\ref{app:nearopt_horizon} retains the horizon study, Appendix~\ref{app:discount} the discount comparison, and Appendix~\ref{app:interpretation} the weight-transfer results." The PDF prints that as Appendix J, Appendix K, and Appendix Y. Those letters are Near-Optimality across Planning Horizons, Discount Factor Sensitivity, and Additional Interpretation and Tree-Search Controls.

**Title case.** The ten subsections named in the optional note now print as Observe-then-Commit Structure and EFE Scope, Two-State Thresholds and Their Empirical Scope, State-Preservation Proof and Destructive Sensing, Agent Specifications and Weight Selection, Proof and Numerical Check of the Usage-Onset Corollary, Proof and Implementation Scope of the Online Controller, Relationship to Constrained Planning and Experimental Design, The Information-Unit Weight and Tuning, Zero-Shot Weight Transfer, and Approximate Planning with MCTS-EFE.

**Length after the other referees' edits.** The conclusion is on page 37 and References still begins on page 38, so the main body remains inside the practical limit. The added pages are in the appendix.
