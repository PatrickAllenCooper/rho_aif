# Reviewer 2 — additional numeric-claim flags

The final claim-check log contains 58 warnings, 29 instances per master. The round-2 report verified the earlier 19 instances per master. I independently checked the additional 10 instances per master against the committed source CSVs. All are valid; the checker resolved the nearby CSV name to a different experiment, or did not calculate a difference/ratio. These are not hard failures.

1. `13.2` percentage points is the K=3 EFE-versus-Planning success difference in `results/results_showcase_obs_scaling.csv`: `(0.960 - 0.828) * 100 = 13.2`. It is not a `results_tiger.csv` claim.
2. Diagnosis POMCP(5000) success `75.5%` comes from `results/results_pomcp.csv`: success `0.7546`, seed-level SE `0.005963220606350234`, giving `75.5 ± 0.6%`.
3. Diagnosis EFE success `97.2%` in the same CSV is `0.9716`, SE `0.002694`; the stated `97.2 ± 0.3%` is correct.
4. Diagnosis POMCP(5000) `311.9 ms/episode` in that CSV is `311.9115476131439`.
5. Tiger POMCP(5000) success `90.3%` is `0.9028`, SE `0.003136877428271627`, giving `90.3 ± 0.3%`.
6. Bandit POMCP(2000) reward `5.90` is `5.8964`, with SE `0.05119140552866268`, giving `5.90 ± 0.05`.
7. Bandit Planning reward `5.75` is `5.7495`.
8. Bandit POMCP(5000) success `97.2%` is `0.9720`, with SE `0.0017888543819998333`, giving `97.2 ± 0.2%`.
9. Bandit POMCP(5000) reward `5.18` is `5.1844`, with SE `0.044646780399038834`, giving `5.18 ± 0.04`.
10. Bandit POMCP(5000)/POMCP(1000) compute ratio is `932.2165602207184 / 135.924773 = 6.858327123558999`, correctly reported as about `6.9` times. The numerator is also correctly summarized as about `0.93` seconds per episode.

The nine POMCP instances belong to `results_pomcp.csv`, not the exploration-constant sweep CSV selected by the checker. No numeric manuscript correction is needed. `git diff --numstat -- results` is empty at verification. The additional local Figure 14 prose correction is separately supported by `reviewer_figure14_verification.json`, obtained from an independent deterministic replay with zero difference from the archived trace.

The subsequent heading cleanup caused one further instance per master to be checked, bringing the total to 60. The ablation paragraph's `p=0.0014` is correct. `results/results_mcts_efe_ablation_stats.csv`, line 7, contains Tiger / observations / full versus no-tree-ig, with `p_seed_level=0.0013564590999689118` and `significant_hb_seed_level=True`. The printed p-value is the rounded seed-level Welch p-value; the text separately states that the comparison survives Holm correction. No correction is required.

The final filename-wrapping pass expands the checker's diff-based scope to 254 warnings because adding `\allowbreak` touches many otherwise unchanged numeric paragraphs. This does **not** represent 254 newly verified empirical claims. The 60 pre-wrap warning instances were explicitly triaged across rounds 2 and 4. I read `wrap_paths.py`: its only source substitutions insert `\allowbreak` after escaped underscores, slashes, and CSV-list commas inside `\texttt`, and it asserts byte-identical source before/after when `\allowbreak` and its swallowed whitespace are removed. This supports treating the additional warnings as newly selected unchanged prose, rather than changed values. The separate table-note `\shortstack` change reflows existing words/numbers. No additional empirical campaign or blanket claim of rechecking every old paragraph is implied.

The frozen delivery log, `claim-check-delivery.log`, contains **256** warning entries and no hard failures. Two further warnings arose when trailing-space cleanup selected two old numeric paragraphs. The final partition is therefore **60 explicitly triaged substantive/edit-context instances plus 196 formatting-only instances**, matching `artifact_manifest.json`. The latter are not being represented as 196 fresh empirical recomputations.
