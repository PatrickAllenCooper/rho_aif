# Reviewer 2 — full figure audit, round 3

Date: 2026-09-28. Scope: all 20 figure environments in the 114-page JAIR manuscript after the science corrections accepted in round 2. This is an independent visual and caption audit, not a new experiment campaign. The previous empirical ACCEPT remains the scientific assessment. The figure-polish assessment of the initial rendered state is **MINOR REVISIONS**, with the specific conditions below. No manuscript, producer, or data files were edited by this reviewer.

## Inspected state and method

The inspected PDF is `paper/full_paper_jair.pdf`, SHA-256 `1ed9ecb70554fd651769e7933138174f1ad0c394ceac2d80dc4b4b9c4e26cd42`. All 20 figures were located from the figure environments and the compiled auxiliary labels, then their complete manuscript pages were rendered with Poppler at 130 dpi. Review was at the actual relative manuscript size, including adjacent caption and body text, rather than only enlarged source figures. Selected color-dependent pages (figures 5, 8, 9, 14, 18) were also rendered in grayscale. Producer code and corresponding captions/Descriptions were read where needed to distinguish design issues from intended scientific encodings.

Audit images and machine-readable inventory are in `/Users/pat/Documents/Codex/2026-09-17/plea/work/polish-2026-09-28/figure-audit/`. The `figure-NN-page-PPP.png` images preserve the initially reviewed state even as root modifies the working tree. Parent has already applied some of the communicated findings to producers, but those changes are not accepted merely on the basis of their description. The rebuilt manuscript must be inspected again.

This audit checked labels, ordinary font size, legend density, panel dimensions, annotation collisions, clipping, contrast, redundant identity encodings for grayscale, and figure/caption correspondence. Small mathematical subscripts and extracted font fractions were not treated as ordinary-text font failures. No image showed a materially clipped panel or unreadable overlapping axes. The central problems are concentrated in two over-shrunk figures and a small set of annotations/captions.

## Required corrections

**F1 — Figure 8 is too small at its actual embedding size.** Initial page 56, `fig:distractor`, `figures/distractor_composition.pdf`, producer `experiments/run_distractor_diagnosis.py::plot_composition`. The initial producer authored a 10.5-inch-wide two-column figure, then embedded it at 0.85 of the manuscript line width. Its ordinary legends, tick labels, and titles consequently print much smaller than the surrounding figure conventions. The source width is approximately 750 PDF points. Even at a full 468-point embedding, 9.5/8.5-point source labels reduce to about 5.9/5.3 points, and the actual initial 0.85 embedding shrinks them further. The 16 categorical weight ticks in the left panel are the clearest failure. Redraw at approximately 6.5-inch final width, use two vertically stacked panels and full manuscript line width, and retain ordinary labels near 8–9 points. Preserve the composition values, seed-level SEs, and all weights. Add hatching to the distractor bar segment and a distinct marker/line style to the relevance-weighted curve, so the comparison remains evident in grayscale. Revise caption and Description from left/right to upper/lower. Root reports this implementation is now present; rebuilt-page verification is outstanding.

**F2 — Figure 9 has too-small and too-faint weight labels.** Initial page 60, `fig:pareto`, `figures/fig_pareto.pdf`, producer `experiments/run_pareto.py::plot_pareto`. Five panels initially occupy a 9.6-inch-wide 2-by-3 layout and are reduced to manuscript width. The approximately 686-point source width reduces ordinary 8.5-point text to about 5.8 points and 7.5-point annotations to about 5.1 points. The light-gray weight-range labels are difficult to read, especially in grayscale. Use a 6.5-inch-wide 3-row-by-2-column layout, with a compact legend in the unused sixth cell, and darken/enlarge the weight annotations. Preserve all plotted means, both-axis SEs, tied ranges, and the coincident diamond/star encoding. Root reports this implementation is now present; the increased figure height and caption placement need rebuilt-page verification.

**F3 — Figure 2 labels a bracket as though it were one threshold.** Initial page 38, `fig:collapse`, `figures/price_scale_invariance.pdf`, producer `experiments/run_price_of_information.py::plot_scale_collapse`, initially near line 1063. The right panel draws two bracket endpoints but its initial vertical label says `Crossing bracket w*(B=8)/alpha`. Use a normalized-weight axis, `w/alpha`, and identify the crossing bracket and budget in the panel title. This keeps the display consistent with the operational interval definition. No numerical change is necessary. Root reports this correction is now present.

**F4 — Figure 5's budget annotations lack contrast.** Initial page 43, `fig:costbudget`, `figures/price_cost_budget.pdf`, producer `experiments/run_price_of_information.py::plot_cost_budget`. Yellow/orange budget text on a white/gray background is too pale at printed size, especially `B=19.20 cost` and `B=11.50 cost`; the right-panel reference-cost note is also faint. Use dark text, or sufficiently dark amber with a light backing if needed, while leaving line styles and colors to identify the curves. Keep the budget values and shared crossing bands unchanged. Root reports darkened labels and reference-cost notes are now present.

**F5 — Figures 6/7 need accurate scale wording and more visible brackets.** Initial pages 44/46, `fig:interleaved` / `fig:stairs`, `figures/price_staircase_interleaved.pdf` / `figures/price_shadow_curves.pdf`, shared producer `experiments/run_price_of_information.py::plot_shadow_price_curves` near lines 279–410. The budget axis is logarithmic, but the price axis is symmetric-log with a linear region near zero. The initial Figure 7 caption describes log-log axes, which is inaccurate because zero is a genuine plotted price; Figure 6 should make the same scale choice explicit. Preserve zero values and the existing adaptive linear threshold. The bracket bars are unnecessarily faint, particularly in pale-colored series: producer alpha is 0.35 for slack and 0.5 for binding. Raise contrast modestly while preserving dotted slack brackets, solid binding brackets, open slack markers, and the meaning of the top-grid caps. Do not turn brackets into statistical error bars. Root has corrected scale wording in caption/Description; final bracket contrast should be checked in the rebuilt pages.

**F6 — Figure 14 confuses an interpolated value crossing with actual discrete commitment.** Initial page 84, `fig:extended_efe`, `figures/fig_extended_efe.pdf`, producer `experiments/run_visualizations.py::fig_extended_efe`, especially lines 556–569. The open-circle crossing is linearly interpolated between the last two sampled values. The dotted vertical line is the actual later discrete commit step. The initial caption says the agent commits at the crossover (open circle), while the Description says the open circle is at the final step. Correct caption/Description to distinguish the interpolated crossing from the commit step, or change the marker to the actual discrete commit point and describe that accurately. The current data and trace do not require alteration.

**F7 — Figure 14 should not identify tests by purple shade alone.** Same location and producer, near lines 584–608. Three test-information curves have the same solid/dot style and use three purple shades; the action strip likewise uses only shades. The grayscale rendering confirms reduced separation of Test 1 and Test 2 and no robust independent cue in the strip. Use distinct line styles/markers for the curves, and a matching label or hatch identity in the action strip. Keep the same test sequence and information values. Root is addressing this with F6.

## Optional useful polish

**O1 — Figure 1.** `experiments/build_fig_hero.py::plot_hero`. The diagram already explains the mechanism clearly. Its six-entry legend repeats long definitions available in the caption. Short labels such as `Usage U(w)`, `Sampled weights`, `Budget B`, `Crossing bracket`, `Endpoint mixture`, and `EFE w=1` would support a slightly larger legend without changing the graphic. Darken the small bracket-edge labels if the legend is revised. No structural redesign is necessary.

**O2 — Figure 10.** `rho_aif/render_tileworld.py::render_agent_comparison`, invoked by `experiments/run_tileworld.py::fig_agent_comparison`. The small pale footer below the comparison duplicates caption explanations. Removing it, or making the necessary symbols part of a concise visible legend, would improve clarity without reducing the 18 useful belief panels. Panel and row labels otherwise remain usable at printed size.

**O3 — Figure 18.** `experiments/run_visualizations.py::fig_efficiency_curves`. Planning and EFE use different colors but the same solid style in the middle/bottom panels. Their gray intensities are distinguishable, but a different dash pattern for one is more robust in grayscale. The other two agents already have dashed/dotted styles. Retain the endpoint markers and conditional-on-still-running interpretation. This is a robustness improvement, not a scientific defect.

## Complete inventory and coverage

1. **Figure 1, page 4, `fig:hero`.** Asset `fig_hero_price_curve_jair.pdf`. Producer `experiments/build_fig_hero.py::plot_hero` (JAIR variant selected at the bottom of that script). Diagram, budget line, bracket, endpoint mixture, and EFE star all clear. See optional O1; otherwise passes.

2. **Figure 2, page 38, `fig:collapse`.** Asset `price_scale_invariance.pdf`. Producer `experiments/run_price_of_information.py::plot_scale_collapse`. Usage curves, scale markers, and bracket endpoint values are clear. Required F3 concerns interval semantics, not curve visibility. The small gray explanatory note can be darkened opportunistically.

3. **Figure 3, page 39, `fig:prop2`.** Asset `price_prop2_jumps.pdf`. Producer `experiments/run_price_of_information.py::plot_prop2_jumps`. Main panels and onset insets are readable. Hatching, threshold markers, and captions agree. Passes; no change required.

4. **Figure 4, page 41, `fig:dualmultiseed`.** Asset `price_dual_multiseed.pdf`. Producer `experiments/run_price_of_information.py::plot_dual_multiseed`. Four panels have clear units, shared series encodings, and readable legends. Passes; no change required.

5. **Figure 5, page 43, `fig:costbudget`.** Asset `price_cost_budget.pdf`. Producer `experiments/run_price_of_information.py::plot_cost_budget`. Both panels and crossing bands are clear; required F4 addresses annotation contrast. Color and grayscale reviewed.

6. **Figure 6, page 44, `fig:interleaved`.** Asset `price_staircase_interleaved.pdf`. Producer `experiments/run_price_of_information.py::plot_shadow_price_curves`. Series line/marker identities are redundant and usable in grayscale. Required F5 addresses scale description and bracket contrast.

7. **Figure 7, page 46, `fig:stairs`.** Asset `price_shadow_curves.pdf`. Same producer as Figure 6. Clear staircase structure and zero/open markers; required F5 addresses the same shared scale and bracket treatment.

8. **Figure 8, page 56, `fig:distractor`.** Asset `distractor_composition.pdf`. Producer `experiments/run_distractor_diagnosis.py::plot_composition`. Required F1. Color and grayscale reviewed.

9. **Figure 9, page 60, `fig:pareto`.** Asset `fig_pareto.pdf`. Producer `experiments/run_pareto.py::plot_pareto`, with CSV replay available. Required F2. Color and grayscale reviewed. No need to rerun episodes or change the frontier data.

10. **Figure 10, page 62, `fig:tw_comparison`.** Asset `fig_tileworld_comparison.pdf`. Producer `experiments/run_tileworld.py::fig_agent_comparison` and `rho_aif/render_tileworld.py::render_agent_comparison`. Eighteen small belief maps are intentionally comparative. The main rows, steps, commit outcomes, and shared color scale remain interpretable. Optional O2 only.

11. **Figure 11, page 63, `fig:tw_scaling`.** Asset `fig_tileworld_scaling.pdf`. Producer `experiments/run_tileworld.py::fig_scaling_replot` (also `fig_scaling` for experiment plus plot). Three panels have readable axes and shared legend, distinct marker/line identities, and visible uncertainty. Passes; no change required.

12. **Figure 12, page 82, `fig:traj`.** Asset `fig_efe_trajectory.pdf`. Producer `experiments/run_showcase.py::plot_efe_trajectories`. Three episodes remain distinguishable with circle/square action-value markers and dashed entropy on the secondary axis. Repeated secondary axes clarify the scale. Passes; no change required.

13. **Figure 13, page 83, `fig:obs_scaling`.** Asset `fig_obs_scaling.pdf`. Producer `experiments/run_showcase.py::plot_obs_action_scaling`. Two panels with readable axes, distinct agent styles, and a clear four-agent legend. Caption matches the battery. Passes; no change required.

14. **Figure 14, page 84, `fig:extended_efe`.** Asset `fig_extended_efe.pdf`. Producer `experiments/run_visualizations.py::fig_extended_efe`. Four vertically aligned panels and commit-line alignment are otherwise clear. Required F6/F7. Color and grayscale reviewed.

15. **Figure 15, page 85, `fig:sweep`.** Asset `fig_asymmetry_sweep.pdf`. Producer `experiments/run_showcase.py::plot_reward_asymmetry_sweep`. Three panels plus the relevant zoom have legible labels and uncertainty. Dense error bars at high stakes reflect the data and are still interpretable. Passes; no change required.

16. **Figure 16, page 86, `fig:tw_belief`.** Asset `fig_tileworld_belief.pdf`. Producer `experiments/run_tileworld.py::fig_belief_evolution` and `rho_aif/render_tileworld.py::render_belief_evolution`. Seven panels, true-tile stars, final commitment ring, and shared square-root color scale are clear. Passes; no change required.

17. **Figure 17, page 87, `fig:belief_heatmap`.** Asset `fig_belief_heatmap.pdf`. Producer `experiments/run_visualizations.py::fig_belief_heatmap`. Three belief histories have clear state labels, a labeled/arrow-marked true state, commit indicators, and common scales. Blank post-episode regions are consistent with the caption. Passes; no change required.

18. **Figure 18, page 88, `fig:efficiency`.** Asset `fig_efficiency_curves.pdf`. Producer `experiments/run_visualizations.py::fig_efficiency_curves`. Three stacked panels and shared time axis are readable, with the conditional survivor means explained. Optional O3 improves style redundancy. Color and grayscale reviewed.

19. **Figure 19, page 92, `fig:nearopt_horizon`.** Asset `fig_nearopt_horizon.pdf`. Producer `experiments/run_nearopt_horizon.py::plot_nearopt`. Horizon values, uncertainty, and distinct success criteria are readable. Light connecting lines are appropriately subordinate to the observations. Passes; no change required.

20. **Figure 20, page 103, `fig:reward_scaling`.** Asset `fig_reward_scaling.pdf`. Producer `experiments/run_reward_scaling.py::plot_scaling`. Two panels have clear scale labels, shared legend, distinct line/marker identities, and identifiable selected-weight markers. Caption correctly describes reward-maximizing grid selection. Passes; no change required.

## Acceptance conditions and confidence

The required work is figure presentation and two precise caption/label corrections. None warrants a new experiment. Redraw from committed data or the existing deterministic illustrative traces, preserve numerical records, rebuild both manuscript masters, and inspect the final JAIR embeddings of every changed figure. Also recheck the inventory after pagination changes so each of the 20 figures remains present and captions/Descriptions match layout and glyphs. Producer changes should be limited to rendering, replay support, and faithful caption wording.

Confidence is high for the observed visual defects and caption mismatches, and high that focused revisions suffice. The final figure vote remains MINOR REVISIONS until the rebuilt output is inspected. A claimed fix or a larger source PDF alone is insufficient if the final manuscript shrinks it back down.
