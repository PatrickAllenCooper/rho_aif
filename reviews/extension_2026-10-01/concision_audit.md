# Applied concision audit, 2026-10-01

Recommendation: ACCEPT after the single minor prose repair below. I found no numerical, mathematical or evidence-preservation blocker in the assembled batch. All 20 numerical advisories are resolved. They represent ten distinct claims repeated across the two masters, not 20 unique claims.

Reviewed sources:

- `paper/full_paper_jair.tex`, SHA256 `6412713253e3e1dab83b3e1a96f0a8c9d78246c80f42eba658daa3f847e2863c`.
- `paper/full_paper.tex`, SHA256 `8ba9b26d3c233e61322b7de9b50fccbceb6d6af9eb7c439dea2f041295176b3c`.
- Baseline: `7b954ce`.

I reviewed all 26 appendix groups against their original passages, the nine main groups, the actual assembled source and its surrounding locatives, the claim advisories, selected result rows and producers, and the final acceptance reports. I authored the main proposals but did not author the appendix proposals. This report is an independent applied-batch check of the latter and a re-audit of the combined result. No master was edited.

## Required minor repair

R1. Name the proposition in the reset-scope sentence. In JAIR line 1739 and LNCS line 2044, the paragraph subject is the reset heuristic, but the final sentence starts “It also requires.” This can attach the sign-consistent-crossing requirement to the heuristic rather than the stationary theorem. The requirement belongs to the proposition. Replace the following exact string once in each master:

```tex
It also requires one sign-consistent budget crossing and is silent on curves with multiple crossings, which Proposition~\ref{prop:pi2}'s discussion shows can occur.
```

with:

```tex
The proposition also requires one sign-consistent budget crossing and is silent on curves with multiple crossings, which Proposition~\ref{prop:pi2}'s discussion shows can occur.
```

This is a local clarity repair. The theorem itself, its assumptions and its exclusion of resetting are already correct. No numerical or mathematical change is needed.

## Complete numerical-advisory adjudication

All entries below apply to the matching advisory in both masters.

1. **0.789 bracket agreement.** `results/results_price_bracket_stability.csv`, row `env=Inspection-N8`, `budget=14.043466666666664`, has `frac_reported=0.789`, `frac_modal=0.789`, `n_boot=2000`. The verifier selected the counts companion rather than this summary file. Supported exactly.
2. **Bandit weight 0.139.** `results/results_price_usage_curves.csv`, Bandit row `w=0.13894954943731375`, rounds to 0.139. The nearby bracket-bootstrap counts file is unrelated to the weight grid. Supported.
3. **Bandit usage 6.19.** The same row has `mean_usage=6.192`, which rounds to 6.19. Supported.
4. **Bandit usage 5.11.** The Bandit row `w=0.7196856730011522` has `mean_usage=5.108`, which rounds to 5.11. Supported.
5. **Bandit weight 0.72.** That row's weight rounds to 0.72. Supported.
6. **Lower crossing endpoint 1.64.** `results/results_price_shadow_curves.csv`, Bandit `budget=5.874479999999999`, has `w_lo=1.6378937069540649`, `usage_lo=5.108`, `bracketed=True`. The corresponding usage-curve row agrees apart from serialization of the final digit. Supported.
7. **Upper crossing endpoint 3.73.** The same shadow-curve row has `w_hi=3.7275937203149416`, `usage_hi=7.318`. Thus the budget is above the lower endpoint usage and below the upper endpoint usage, and the printed bracket `(1.64,3.73]` is supported. The earlier crossing is also real: usage 6.192 at weight 0.13894954943731375 exceeds this budget before the later dip to 5.108.
8. **Implemented nat-denominated weight 1.44.** This is an algebraic conversion, not a Pareto-sweep observation. One reward unit per bit equals `1/log(2) = 1.4426950408889634` reward units per nat. The unchanged main unit-convention paragraph supplies the conversion. Supported.
9. **Tiger core usage 4.20.** `results/results_tiger.csv`, the `EFE`/`EFEAgent` row, has `mean_observations=4.198`, `episodes_per_seed=1000`, `n_seeds=5`. It rounds to 4.20 and is the source of Table `tab:main`. The frontier-reference file selected by the verifier is a different battery. For the adjacent comparison, `results/results_sarsop_baseline.csv`, Tiger `EFE (w=1)`, has `usage=4.3232`, supporting 4.32. The paragraph correctly warns that these estimates are not interchangeable.
10. **Testbed pooled reward effect 0.69.** `results/results_summary_stats.csv` uses `env=InfoSeeking` for Testbed. For `metric=Reward`, both `(agent_a=InfoGain-Tuned, agent_b=EFE)` and `(agent_a=Planning+IG, agent_b=EFE)` have `cohens_d=-0.6925229106242805`. Reversing to the manuscript's EFE-first comparison gives `+0.6925229106242805`, which rounds to 0.69. These are pooled episode-level values. The much larger seed-level column is not being interpreted. The verifier attached the preceding Tileworld file, which is not the source. Supported.

No advisory remains unresolved, and none requires a changed number. This conclusion comes from the source rows and conversion above, not the verifier's zero exit status.

## Mathematical and evidential preservation

I independently replayed all 26 appendix groups and all nine recommended main groups against `git show 7b954ce:<master>`, then applied the root's “strictly instrumentally worthwhile” clarification. The result is byte-identical to each live master at the hashes above. There are no unexplained extra manuscript edits.

All formal proof environments are byte-identical. The main scale-equivariance and comparative-statics statements and arguments remain byte-identical, as do the stationary-controller statement and surrounding convergence qualifications. The direct scalar supermartingale and running-average argument in `app:theory_controller` is intact. Definition PI-3 retains the level-set/crossing distinction, last-crossing convention, closed-enclosure qualification, no-missed-crossing condition, unbracketed fallbacks and mixture-attainment conditions.

The root's threshold-summary change is correct. A strictly positive instrumental net value gives a negative onset threshold, while exact indifference would give zero. The complete two-horizon proposition, including the strict interval endpoints and perfect-sensing exclusion, remains bound beside its proof. The state-preservation example, its sign reversal and its diagnostic limitations likewise remain bound and summarized in the main text.

The appendix cuts retain the negative controls and statistical distinctions that matter. Testbed's over-observation, weak PyMDP control, horizon failures, discount and sensor-mismatch boundaries, posterior-vote comparison, Epistemic-only behavior, proper-score versus calibration distinction, six RockSample departures, retrospective TOST margin choice, prospective added seeds, episode-matching scope and pooled-versus-seed uncertainty all survive. The source retains the exact PWLC restriction on the POMDP-IR equivalence citation. The frontier plug-in, reference-selection, rare-event, post hoc and partially non-blind qualifications are untouched.

Additional artifact checks beyond the advisories:

- `results/results_nearopt_horizon.csv` has 300 rows. Recomputing the stated `best_reward - w1_reward <= max(0.05*abs(best_reward), 0.5)` rule gives 30, 58 and 79 passes among 100 environments at H=1,2,3. The four H=1 passes that recur at exactly one deeper horizon are IDs 2, 42, 63 and 95. `results/results_horizon_map_agreement.csv` confirms 30 recurring passes, 14 persistent failures, zero myopic overclaims and 56 underclaims. AC07–08 preserve the descriptive status and do not turn the sample pattern into a horizon theorem.
- `results/results_discount_stats.csv` confirms that the success p-values 0.9621993157756052 on Diagnosis and 0.9465068730573218 on Bandit apply at both gamma=0.90 and gamma=0.95. The success gaps at gamma=0.99 and 1.0 survive Holm correction. The shortened passage therefore does not accidentally extend a p-value to a different discount. It does not claim corrected reward significance at those larger discounts.
- The Testbed reward comparison used in AC01 has seed-level p=1.0683575774183727e-05 in `results/results_summary_stats.csv`, supporting the printed 1.1e-5. Its chance-level and over-observation interpretation remains qualified by the two-step versus H=4 distinction.

No scientific restoration of removed prose is required.

## Figures, numbering and locatives

The only removed label is `fig:tw_belief`. No surviving reference points to it, no label is duplicated, and all source references resolve after included-table labels are considered. All citation keys present at baseline remain cited. The retained `app:tw_belief` subsection label is harmless, although it now contains only the Diagnosis illustration. The main-to-appendix moves keep their original table and figure labels, and the new cost/interleaved appendix destinations are defined and used consistently.

AC26 removes a repeated illustration rather than a distinct experiment. `experiments/run_tileworld.py` functions `fig_belief_evolution` and `fig_agent_comparison` both use `TileworldEnv(grid_size=6)`, EFE horizon 2, the same deterministic seed search and scan bounds, and a reseeded episode. `rho_aif/render_tileworld.py` uses the same five-index `linspace` selection in both layouts. The retained comparison caption states the uniform prior and distinguishes each row's true scan times. The producer and removed standalone PDF remain in the repository.

The new Diagnosis paragraph's 14/29/32 observations agree with the retained figure caption and Description. Its non-typical-episode qualification remains explicit. The phrase “maximizes a recursive score” initially warranted a check, but is not a sign error: `experiments/run_visualizations.py::fig_extended_efe` explicitly plots `-G` in reward units. Its caption still says that the recursive choice need not maximize the one-step information gain in panel (b). No repair to that sentence is required.

The hero producer, `experiments/build_fig_hero.py`, hardcodes “Prop. 3.1” for JAIR and “Prop. 1” for LNCS. The clean JAIR auxiliary file still resolves `prop:equivalence` to 3.1, and the clean LNCS PDF prints Proposition 1 for that result. Thus the static hero references remain correct. The relocated threshold and example become U.1 and U.2 in this JAIR build, and their textual references use labels. Other retained figure captions were not rewritten by this batch. No caption producer needs updating for the accepted changes.

## Build checks and limits of this audit

I built copies of the exact reviewed sources in `/tmp/rho-applied-concision-audit-2026-10-01`, using the repository's unchanged class, bibliography, figure and table files. The JAIR pdfLaTeX/Biber cycle succeeds at 104 pages, with references starting on page 32. It has zero overfull boxes, undefined references/citations and missing characters. The LNCS build succeeds with the documented Tectonic route at 132 pages. Its output has underfull-layout warnings but no overfull, undefined-reference or missing-character warnings. An initial attempt to use this TinyTeX installation for LNCS lacked `aliascnt.sty`, so I used the documented tool rather than altering the environment.

This is a source, artifact and compilation audit. I did not perform a complete page-by-page visual inspection or rerun the underlying empirical batteries. Final visual QA, source-package regeneration and the new external-data experiment remain separate work. The one required prose clarification above does not affect the numerical conclusions or anticipated layout.
