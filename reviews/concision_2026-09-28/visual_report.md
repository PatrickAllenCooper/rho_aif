# LNCS overfull-line review, 2026-09-28

I used the PDF skill for read-only inspection. Source was not edited. I inspected the log `/tmp/rho_concise_lncs.log`, all word/line coordinates from `pdftotext -bbox-layout`, and rendered LNCS PDF pages 12, 23, 53, 77, 91, 114, 126, and 135 at 90 dpi. Page numbers below identify this 153-page build.

The warnings correspond to visible right-margin spills, not clipped physical pages. The normal right text edge is approximately 482pt. The worst line reaches 550.6pt on page 114. Fonts and mathematical glyphs render correctly. These are line-breaking problems and do not require smaller type or scientific edits.

## Recommended minimal batch

First add `\setlength{\emergencystretch}{2em}` in the LNCS preamble, after its existing paragraph/layout settings. This allows the emergency line-breaking pass additional interword stretch only when the normal pass cannot find an acceptable paragraph. It changes no text, font size, or margins. It should resolve most small first-line spills without scattering manual breaks throughout prose. If global scope is undesirable, the identical parameter can be grouped around only the paragraphs listed below as `{\emergencystretch=2em <original paragraph>\par}`.

Then add the following explicit break opportunities. They preserve every rendered character and number. Line numbers refer to current `paper/full_paper.tex`.

1. Line 1949, page 91, 56.58pt spill. Replace
   `\texttt{scipy.stats.entropy}`
   with
   `\texttt{scipy.\allowbreak stats.\allowbreak entropy}`.

2. Line 2212, page 114, 68.31pt spill. Replace
   `\texttt{results\_price\_usage\_curves.csv}`
   with
   `\texttt{results\_\allowbreak price\_\allowbreak usage\_\allowbreak curves.csv}`.
   In that same paragraph, replace
   `\texttt{results\_cpomdp\_baseline.csv}`
   with
   `\texttt{results\_\allowbreak cpomdp\_\allowbreak baseline.csv}`.

3. Line 2294, page 126, 51.89pt spill. Replace the inline grid
   `$\{0.01, 0.1, 0.5, 1, 2, 5, 10, 20, 50, 100, 200\}$`
   with
   `$\{0.01,\allowbreak 0.1,\allowbreak 0.5,\allowbreak 1,\allowbreak 2,\allowbreak 5,\allowbreak 10,\allowbreak 20,\allowbreak 50,\allowbreak 100,\allowbreak 200\}$`.

4. Line 445, page 23, 15.85pt spill. Replace
   `$\{42,123,456,789,1024\}$`
   with
   `$\{42,\allowbreak123,\allowbreak456,\allowbreak789,\allowbreak1024\}$`.
   Line 2104, page 103, 23.04pt spill has the spaced equivalent. Replace
   `$\{42, 123, 456, 789, 1024\}$`
   with
   `$\{42,\allowbreak 123,\allowbreak 456,\allowbreak 789,\allowbreak 1024\}$`.

5. Line 1730, page 76, 24.38pt spill. The first path list contains no break opportunities within its brace expansion. Replace
   `\{5x3,7x4,7x8,11x11\}.csv`
   with
   `\{5x3,\allowbreak7x4,\allowbreak7x8,\allowbreak11x11\}.csv`.
   The second brace expansion already has comma break opportunities. Its observed first-line overflow should respond to emergency stretch.

6. Line 2271, page 123, 3.07pt spill. For consistency with the repository's existing filename treatment, replace
   `\texttt{results\_tiger.csv}`
   with
   `\texttt{results\_\allowbreak tiger.csv}`.

The first four changes address the strongest overflows directly. The remaining filenames in the warning log already contain `\allowbreak` after their components, so adding more component breaks is unlikely to help. Emergency stretch is the less intrusive remedy there.

## If a second pass still reports mathematical spills

Page 12, line 248, 22.90pt: the correct-posterior equation runs across a prose line. Add discretionary break points between product factors by replacing the exact inline expression

`$b'_{o,T}(s') \propto \sum_s T(s'\mid s,a_D)\,O(o\mid s,a_D)\,b(s)$`

with

`$b'_{o,T}(s') \propto \sum_s T(s'\mid s,a_D)\,\allowbreak O(o\mid s,a_D)\,\allowbreak b(s)$`.

Page 53, lines 1188, 1190, and 1192: the three inline equations in the equivalence proof make two lines protrude by 13.61pt and 14.55pt. The cleanest layout-only fallback is to change each of those complete `$...$` equations to its own unnumbered `\[...\]` display. Preserve their exact content and punctuation. This leaves the proof text and mathematics unchanged and adds only display spacing. First try the emergency-stretch pass, which may already fit them.

Page 19, line 388, 7.15pt: the corollary's optional title almost fills a whole line. If emergency stretch does not resolve it, permit a forced title wrap by replacing

`[Proposition~\ref{prop:nearopt}'s onset thresholds are usage-staircase knots]`

with

`[Proposition~\ref{prop:nearopt}'s onset thresholds are\linebreak usage-staircase knots]`.

The LNCS class typesets its optional theorem title as paragraph text, so that break is outside a box and does not change the title. Avoid shortening the theorem title solely to fit it unless preferred editorially.

## Other warning locations covered by emergency stretch

- Line 393 / page 19: final `Appendix U.5` reference, 6.05pt.
- Line 417 / page 21: first line ending `almost-`, 2.34pt.
- Line 452 / page 23: first line ending `cost-denominated`, 12.20pt.
- Line 474 / page 24: first recovery-estimand line, 4.82pt.
- Line 630 / page 35: first same-stream-comparison line, 6.38pt.
- Line 651 / page 37: first relevance-weighting line, 5.60pt.
- Line 723 / page 40: first Pareto summary line, 2.85pt.
- Line 1736 / page 77: the already breakable `rho_aif/agents/rocksample_pomcp.py` path, 31.65pt.
- Line 1742 / page 78: already breakable horizon CSV, 7.34pt.
- Line 2216 / page 115: already breakable reference CSV/script list, 24.60pt.
- Line 2393 / page 135: first appendix-orientation line, 15.90pt.
- Line 2448 / page 140: first observation-scaling line, 6.29pt.

Warnings under 3pt also occur at lines 459, 585, 1849, 1922, 2046, and 2071–2073. They do not clip text but should be included when checking the rebuilt log. Underfull vertical boxes are separate page-balancing warnings and do not justify changing font sizes or margins.

## Validation after application

Recompile LNCS, then inspect the new log and re-render the affected pages, allowing for page-number shifts. Confirm that the filename/grid changes preserve extracted text, allowing only line-wrap whitespace, and that no new table/figure spill is introduced. No source change or candidate build was made by this reviewer, so this report recommends exact fixes rather than asserting they have already removed the warnings.
