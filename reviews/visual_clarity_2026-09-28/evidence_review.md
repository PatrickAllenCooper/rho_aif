# Independent evidence and rendered-layout review

Reviewer: final evidence panel reviewer 2. Date: 2026-09-28. Baseline: `9f19faa`.

**Decision: UNQUALIFIED ACCEPT.** No required changes remain in this visual-clarity, table-typography, and packaging revision. I did not author the changes. This decision follows my own source, saved-data, rendered-PDF, and package checks; it does not rely on the other reviewer's vote.

## Exact final state

- JAIR source SHA-256: `17dac3f19c1664a1b67401bd5dbd56d1463a4b7623808f920b8d64cbce6135ac`
- LNCS source SHA-256: `26043345739d37421e2699272bad41df1102ad40effc463482bf7e0ffdd5e4c4`
- JAIR PDF: 120 pages, SHA-256 `f403869b31320045520a1936d4cf34fea91a6197606c60d7c095fc8d15dc95b5`
- LNCS PDF: 156 pages, SHA-256 `49e99dfbd6771eb52cc970c5073de23c0231239496e2147c84d4ce3628f3c6d3`
- Overleaf ZIP SHA-256: `24df1cc764ce1307c2cc3bd76b238f826f92af494201beb2251453502695b3cc`

I independently verified every hash in `artifact_checks.json` against the final files. The earlier full scientific and figure reviews remain the basis for unchanged content. This pass reviewed the actual working-tree diff, all seven new/revised figure embeddings in both masters, and every rendered table body in both masters.

## Plot data and interpretation

For `plot_scale_collapse` in `experiments/run_price_of_information.py`, I captured the Matplotlib artists and checked them against the saved Diagnosis CSV rows. There are **42 rows, 14 weights at each of three scales**. Both raw-weight and normalized-weight panels preserve every mean, seed-level SE, and positive x-coordinate exactly. The zero points retain the explicitly broken log-axis convention. The matched means and SEs coincide across scales, and the normalized bracket is `(0.1414213562, 0.3228004743]`. The figure and caption distinguish this finite-grid bracket from sampling uncertainty and do not imply a measured policy attaining the target between sampled points. My preliminary message's count of 39 was a manual summary error; the runtime assertions iterated over all rows, and the saved audit record and this report use the verified count of 42.

For `plot_cost_budget`, the 24 archived count/cost rows preserve their means and seed SEs in panels (a) and (b). The 12 values in panel (c) are exactly the ratio of mean sensing cost to mean observation count, spanning approximately 1.260102 to 1.414022. The lower targets are 8.8592 observations and 11.504 cost units, with common bracket `(10,31.6227766]`; the upper targets are 13.7088 and 19.204, with bracket `(31.6227766,100]`. I verified that the plotted row pairing uses those matching brackets.

Removing the ratio's former error bars is a justified correction. The aggregate CSV supplies marginal SEs but no paired cost/count covariance, whereas the previous ratio formula omitted that covariance. The two quantities share trajectories, so independence cannot be presumed. The replacement is explicitly descriptive, and both the final caption and the on-figure note state that no uncertainty estimate is shown for the ratio. Count/cost SEs remain present. The new bracket strip describes grid resolution separately from statistical uncertainty.

For `experiments/run_pareto.py`, I dynamically verified all 55 measured points, all success/reward seed-level error-bar segments, and all 18 annotation leaders. Each leader points to an actual measured point. The revised axes padding and label positions alter presentation only. The tied weight ranges, canonical-weight marker, EFE marker, and caption-named Tileworld point retain their intended meanings.

The four new figures from `experiments/build_fig_concepts.py` are explicitly schematics. They neither read nor alter result files. Their state-preservation and feedback semantics agree with the surrounding text. The target-versus-cap example is arithmetically correct: the selected A–D mixture has usage 4 and reward 3.25, the best equality mixture has reward 4, and C has reward 6 with slack usage 2. Its shading is limited to the cap-feasible portion of the illustrated mixture hull. These illustrations introduce no benchmark measurements or broader empirical guarantee.

There are no changes under `results/`.

## Rendered figures

I rendered and visually inspected the exact final PDF pages, including captions, in both formats:

- Observe/commit loop: JAIR 12, LNCS 16.
- State preservation versus destruction: JAIR 23, LNCS 30.
- Target versus cap: JAIR 27, LNCS 36.
- Projected feedback loop: JAIR 32, LNCS 43.
- Raw versus normalized reward scaling: JAIR 40, LNCS 54.
- Count, cost, ratio, and bracket panels: JAIR 46, LNCS 62.
- Pareto panels: JAIR 65, LNCS 86.

All pass. Labels, leader endpoints, panel divisions, and captions are legible and consistent. The cost/count target labels sit outside the curves, with the ratio and brackets clearly separated. The Pareto labels remain inside their panels without colliding with points or panel borders. The diagrams use position, shape, arrows, or line style in addition to color. No reviewed figure is cropped, no caption is detached by an oversized float, and the diagrams occur near their explanatory sections. The narrower LNCS figures remain readable. Unchanged figure assets and embeddings retain the earlier accepted treatment; I do not represent this bounded pass as a new visual inspection of every unchanged figure.

During preflight I found the cost figure's stale two-panel caption/Description. I reported this required correction before freeze, and verified its resolution in both final sources and both rendered figures. No such condition remains.

## Table values, physical fonts, and widths

I reassembled all 15 original frontier rows from the three new continued panels and compared them with the baseline. Every numerical cell and unattainability status is preserved. For the other eight generated table files, all ampersand-delimited row content is unchanged after normalizing the font macro. I reviewed the producer diffs: they change layout/font declarations, not the computations of reported values.

For the inline tables, I reconstructed all 13 environment-specification rows from the two panels in each master; the original fields are preserved. Outside that reflow, the numeric sequences in 254 JAIR and 256 LNCS ampersand-delimited source rows match the baseline. This is a propagation/preservation check, not a claim that all historical experiments were rerun.

I independently located and measured **all 38 rendered table bodies in each PDF** (35 numbered tables plus continued panels), using their booktabs rules to delimit the bodies. Every body uses 9 TeX points, measured as approximately 8.97 PDF points. The only smaller glyphs are ordinary mathematical scripts: approximately 6.58 PDF points in JAIR and 5.98 in LNCS. There are no residual scaled table bodies, inconsistent body-size commands, or smaller ordinary table labels in those regions.

I also rendered every one of the 76 table bodies at two pixels per PDF point and visually inspected all crops without shrinking them. Headers, continued-panel identities, multirow labels, numerical columns, and bottom rows are readable. No overlapping or cropped cells were found. The widest measured bodies are 308.33 PDF points in JAIR and 338.54 in LNCS, within their respective text areas. A separate full-document character-boundary scan found **zero off-page glyphs** in either final PDF. Mathematical subscripts being smaller is normal typesetting, not a violation of the consistent-body-font request.

The independent layout JSONs and visual crops are under `/Users/pat/Documents/Codex/2026-09-17/plea/work/visual-review-2026-09-28/`. They were produced before consulting the table author's font-audit report.

## Packaging

I inspected `tools/build_overleaf_package.py` and invoked it twice from `/tmp` with distinct output paths. The outputs were byte-identical and match the final delivered ZIP hash above. Its discovered dependency set has exactly 38 files: 24 referenced figure PDFs, nine table inputs, the JAIR source, bibliography and class, plus README and Latexmk configuration. All four new diagrams are included. All 36 canonical source/asset archive members match the final repository bytes. ZIP integrity, path safety, source-only scope, compiler/main-document instructions, and standard-package assumptions pass.

The root's additional extraction build is recorded separately in `artifact_checks.json`: 120 pages, identical extracted text on every page, and no repository inputs in the recorder. I independently tested deterministic generation and final dependency/file closure in this pass; I did not duplicate that final extraction compilation. The earlier independent package review already established the same pdfLaTeX/Biber isolation workflow. Neither review claims an actual hosted Overleaf test.

Confidence is high within the stated scope. There are no outstanding required or optional corrections from this review, and no new experiment campaign is warranted by these presentation changes.
