# Independent JAIR clarity and editorial review — 2026-10-21

## Recommendation

**ACCEPT within the prose, exposition and visual-clarity remit. No scientific-clarity revision is required for this recommendation.** Three small editorial repairs are recommended below and have been passed to the coordinating reviewer. They do not alter a theorem, empirical claim or acceptance conclusion. This is a fresh reading of the current manuscript, not an inference from earlier internal accept decisions. It is not a prediction of JAIR's actual decision or a substitute for the independent theory and empirical reviews.

## Exact version and scope

The initial repository HEAD is `f2d4069234811f1dc8bfa3ef6d35b373aef85553`; the initial working tree was clean. The journal source is the October 2 manuscript:

- `paper/full_paper_jair.tex` SHA256 `db283e6949d6a018a1bbed7fb93c4291b0b5b25dbf0fab63d2b43978da4fb9a9`.
- `paper/full_paper_jair.pdf` SHA256 `d58a747617d214afdcdd8116f390d436bb4899c55b60d44b549a352e26933592`.
- PDF: 52 pages, generated October 2, 2026, 15:32:52 MDT.

Read the complete 1,290-line source, the included RockSample table, and the relevant project instructions and correction ledger. Extracted the PDF and visually inspected every figure and table at manuscript size, plus the title page, principal formal definitions/propositions, controller proof, sensor protocol and checklist. Rendered evidence is saved as `clarity_page_*.png`; the extracted text is `clarity_pdf_text.txt`. Pages inspected: 1, 2, 7, 9, 10, 11, 13, 14, 17, 18, 20, 21, 22, 24, 26, 27, 28, 29, 30, 31, 37, 42, 43, 44, 45, 50, 52. No source, data, experiment or figure producer was edited by this reviewer. No experiment was run.

## Findings supporting the recommendation

1. **The design problem is intelligible before the formalism.** The Introduction explains why an expected sensing amount might be a requirement and immediately distinguishes it from both a per-episode hard limit and reward maximization under a cap. Section 4.1 restates the calibration problem before introducing the constrained comparator. Figure 2 gives a usable geometric explanation of the distinction. The conclusion preserves it rather than advertising constrained reward optimality.

2. **The potentially confusing objects are separated.** Definition 4.1 distinguishes the level set, population crossing threshold, finite-grid bracket and per-episode endpoint mixture. The text explains the closed enclosure, unbracketed cases, estimation error and why the selected crossing pair is more restrictive than arbitrary mixing. The numerical tolerance is not presented as a bracket guarantee. The information-unit default is consistently a level-set member, not the recovered threshold.

3. **Dense arguments have a reason to exist.** The EFE recursion is introduced as a specification of one policy family and its units, followed by a direct explanation of what the equivalence does and does not establish. The scale proof is motivated by changing reward units. The comparative-statics proposition is immediately separated from a claim about sensing-count monotonicity. Controller assumptions are in the proposition and the Appendix H.6 proof announces its two steps before using the supermartingale and running-average arguments. The main text explains why the two-state appendix thresholds are relevant and where they cease to apply.

4. **Methods/results transitions make the paper's two questions clear.** Section 5 distinguishes calibration from evaluating the information-unit default. Section 6's same-stream, cap-reference, target-reference and fresh-stream sequence is complex but motivated in the order needed. It explicitly exposes selection uncertainty and the rare-error issue. Section 7 then evaluates the default without treating its algebraic equivalence as empirical reward optimality.

5. **Adverse results are readable and prominent.** The abstract, Introduction and conclusion retain the real-sensor failure at two accesses, failure under later collection batches, and better classification from simpler controls. The paper also states the Tileworld, Testbed, largest-RockSample, irrelevant-sensing, unit-convention and search-architecture limitations. Nothing in this editorial reading requires restoring long discarded appendix material to understand these claims.

6. **The figures communicate their intended claims.** All ten figure pages are legible. The scale plot shows shifted raw brackets and one normalized curve, with explicit explanation of identical measurements. Controller panels separate weight and usage and place the legend outside the data. The sensor-transfer plot distinguishes target-error tolerance from uncertainty and omits an invented measurement for the unavailable target. Pareto leaders avoid the former label collisions. Tileworld pairs success with sensing counts to explain the fixed-depth failure. The target/cap schematic and decision loop are readable without decorative imagery. The staircase figure is necessarily the densest, but its marker/bracket distinction and legend are decipherable at print size.

7. **Tables and notation render cleanly in the inspected pages.** All six tables have legible consistent body sizing, and the inspected equations, indicators, sums, bounds and reference labels render correctly. Bolding conventions that differ between tables are explicitly stated. No clipped mathematical content, unresolved reference, overlaid legend or obstructed figure label was observed.

## Recommended small editorial repairs

These are local improvements, not grounds for withholding acceptance.

- **Stale navigation phrase, source line 191.** The paragraph before Proposition 3.1 says normalized preferences need “the qualification following the proof.” The full proof now resides in Appendix A, whereas the qualification follows the proposition in Section 3.3. Replace with “the qualification following the proposition.”
- **Identify the target of the proof sketch, source line 1072 / PDF page 43.** A destructive-sensing example immediately precedes an environment headed only “Proof sketch.” It proves the factored-observation proposition (`prop:factored`, rendered as Proposition 3.3), not the example. Replace `\begin{proof}[Proof sketch]` with `\begin{proof}[Proof sketch for Proposition~\ref{prop:factored}]`.
- **Split the last Kronecker sentence, source line 1115 / PDF page 44.** The current sentence embeds the limiting schedule property inside a long chain. Suggested replacement: “Since $1/a_t = (1 + \delta t)/\eta_0$ increases to infinity, Kronecker's lemma gives $a_n \sum_{t<n} (B - U_t) \to 0$ almost surely. Under the harmonic schedule, $n\,a_n \to \eta_0/\delta > 0$. Dividing by $n\,a_n$ therefore gives $\frac{1}{n}\sum_{t<n} (B - U_t) \to 0$ almost surely.” The preceding argument and the final scope restrictions remain intact.

## Submission metadata observation

The initial PDF visibly prints placeholder DOI `10.1613/jair.1.xxxxx`, volume/article 1, and August 2026 publication metadata. This is a template-state issue rather than a scientific claim, but clearing unassigned fields and displaying “Manuscript prepared for JAIR review.” would be clearer before submission. I have no editorial objection to the coordinator's proposed class-supported `printacmref=false` and local footer adjustment, provided `jair.cls` stays unchanged and the rebuilt title/continuation pages are checked. This report does not independently establish the live submission portal's present requirements.

## Final-repair re-review

The first repair build has been independently re-reviewed against the actual source diff and newly rendered PDF, rather than the coordinator's summary. All three editorial repairs are correctly applied. The source now names the factored-proposition proof dynamically, so the rendered number is correct. The unused crossing alias is removed, the symmetric model's upper threshold is simplified to its applicable finite expression, the controller's positive initial step and count/cost bounds are explicit, and the statistical/checklist wording avoids stronger claims than the stated analysis supports. These changes preserve the argument and improve local precision.

The 51-page repair build's ten figure pages and six table pages, revised proof pages, and checklist were visually inspected. No clipped text, collision, lost figure, broken equation or unresolved reference was observed. The one-page reduction follows removal of unassigned publication metadata and resulting float reflow, without smaller type or lost scientific content. The supplied JAIR class remains unchanged. The first repair build retained a two-line running title and an empty DOI label. Both were subsequently corrected in the final metadata-only build verified below.

## Final frozen-version confirmation

The final metadata-only build was checked on October 21, 2026. Its first page and an ordinary continuation page were independently rendered and visually inspected (`clarity_final_metadata_page_01.png` and `clarity_final_metadata_page_03.png`). The unassigned DOI label and false volume/article/publication fields are absent. The short running title fits on one line, and both the first-page and continuation footers correctly read “Manuscript prepared for JAIR review.” No overlap, clipping or other visual harm is present. The PDF metadata includes “rho” in the title. The earlier body/figure/table review remains applicable because this final change is confined to metadata and running matter.

Final SHA256 hashes:

- JAIR source: `c260180b50f5845132a6aeba50150373cf5ae5f74331feb9d5490aeae77d65c2`.
- JAIR PDF: `1261bf34b7fb71b3697806a7c87fdc163a84d6032b5d401a7e36f625f5ff3689`.
- Unmodified `jair.cls`: `b203f8fe198a82afececa5fc5c2641fa529e3aa05b82b329bcf5891be339fc68`.
- PDF: 51 pages; generated October 21, 2026, 10:11:50 MDT.

**Final recommendation: ACCEPT. There are no outstanding required revisions within the prose, exposition and visual-clarity remit.**
