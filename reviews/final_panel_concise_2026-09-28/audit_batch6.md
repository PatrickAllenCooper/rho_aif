# Adversarial audit, batch 6 (history removal, batch 5 fixes, clean timing rerun, ledger 9.17.57)

Auditor scope:

- `apply_batch6.py` (H1 to H14, 16 guarded edits) and the three inline removals of "under the fixed pipeline".
- The four batch 5 defect fixes and the restored disclosure sentence in the POMCP appendix.
- The timing updates from the reruns of `run_pomcp.py` and `run_mcts_experiments.py`.
- An exhaustive sweep of both masters, `paper/tables/*.tex`, figure captions, and Description blocks for history language.
- `README.md` and `CHANGELOG.md`.

Masters were read as they stood at 2026-09-30 05:18, with PDFs built at 07:38. Both logs show zero undefined references. `verify_claims.py` has no hard failures.

## 1. Timing rerun and lineage

- **Outcome columns.** In both `results/results_pomcp.csv` (24 rows) and `results/results_mcts_efe.csv` (40 rows), every column except `wall_clock_s` and `ms_per_ep` equals `parts/results_pomcp.csv` and `parts/results_mcts_efe.csv` exactly. Headers and row order also match. OK.
- **Cited timings.** All match `ms_per_ep`:
  - Diagnosis POMCP(5000) is 323.6 ms against EFE's 93.8 ms.
  - Bandit POMCP(5000)/POMCP(1000) is 181.8/31.8 = 5.72, so "roughly 5.7 times" is right.
  - Tiger MCTS-EFE(500) at H=6/8/10 runs 14.0, 13.9, and 15.8 ms, so "14--16" is right.
  - Tiger POMCP(500) runs 11.6, 11.0, and 11.4 ms, so "11--12" is right.
  - Exact-EFE at H=6 runs 63.9 ms, which rounds to 64.
  - The concurrency caveat is gone from both masters.
- **The cited timings are clean.** `run_pomcp.py` ran from 14:12:32 to 16:02:14, after every p2 battery had ended at 14:01. `run_mcts_experiments.py` started at 16:02:14. Cumulative wall-clock puts the Tiger rows at 16:02 to 16:07 and the Diagnosis rows at 16:07 to 16:17.
- **The Tileworld rows are not clean (advisory A1).** `pmset -g log` shows the machine entering Sleep/DarkWake cycling from 16:24:56 onward, which is during the Tileworld rows. Those timings are inflated by factors of roughly 3 to 190 relative to the concurrent run:
  - Tileworld-4x4 POMCP(200): 1091.1 ms against 5.8 ms.
  - Tileworld-4x4 MCTS-EFE(500): 10204 ms against 583 ms.
  - Tileworld-6x6 MCTS-EFE(500): 17060 ms against 1631 ms.

  The run finished at 05:15. The manuscript cites none of these values.
- **H12, H13, H14 and the restored sentence.** `experiments/select_pomcp_constants.py` was last committed in `08140f0` (2026-09-18) and is unchanged in the working tree. The tuning and sweep CSVs have `generated_utc` 2026-09-29T15:08Z, and the selected CSV records the rule "max success on tuning seeds, ties by reward" with tuning seeds 11|22|33. So "a rule recorded before the runs reported here" is literally true. The restored sentence "The rule and its candidate grid were written after an exploratory sweep on the canonical seeds had been inspected" is also true: that sweep is ledger 9.17.28 (2026-09-05/06), which predates the 09-18 rule.
- **H1.** Checked against `results_price_dual_multiseed_metrics.csv`:
  - The decay `readapt` values are 152, 180, 141, 133, NaN, 145, 151, 137, 174, and 180. Reset's are 47, 64, 43, 41, 64, 44, 55, 48, 52, and 54.
  - Decay is slower on every seed. The paired differences are 105, 116, 98, 92, 116, 101, 96, 89, 122, and 126, so the smallest is 89, as stated.
  - Seed 105 does not recover (NaN).
  - The cap is 200 − 20 = 180, so seeds 102 and 110 recover at the cap.
  - Restricted means are 157.3 and 51.2. The conditional decay mean is 1393/9 = 154.8. All match the text.
- **H3a.** The runner's `readaptation_episodes` docstring confirms that the rolling mean is built from post-rescale episodes only. OK.
- **H11.** The code matches the replacement text: `_best_commit_reward(state)` is the leaf, the child belief is `belief * obs_models[a][:, obs]` (normalized), and the tree step and rollout both charge `-obs_cost`. `tests/test_pomcp_cost_sign.py` and `tests/test_pomcp_rollout_belief.py` pass (6 passed).
- **Batch 5 defects 1 to 4.** All four were applied verbatim in both masters: the Appendix Y 1/36 sentence, "within sampling error of its 89.2 ± 0.2%", "The success-rate gap", and "close to the 1/36 rate ... plausibly because". OK.

## 2. Parallelism and conventions

- Every added line in the JAIR diff appears verbatim in LNCS, and the reverse. The only exceptions are the JAIR structured abstract and the checklist item, which are JAIR-only by design, and the LNCS plain abstract.
- There are no prose semicolons in added lines. The only emphasis in added lines is `\textbf{Results:}` and `\textbf{Yes.}`, both structural. No "exact" is attached to SARSOP or CPOMDP references.
- Pre-existing and not from this batch: a prose colon at JAIR 1920 / LNCS 2224 ("rather than a mixture: the $\lambda{=}0$ policy"). See A6.
- `paper/tables/*.tex` contain no history language. The only hit is "Holm--Bonferroni correction". Figure captions and Description blocks are clean. The "no longer exists" in Figure 306's caption and "no longer correspond" at 2048 are physical descriptions.
- Legitimate statistical and descriptive uses were left alone: Holm "correction" and "corrected", "fixed margin", "correct commit", "original RockSample/APPL" (the published benchmark and solver), "the earlier tables/comparison" (in-paper back-references), "retrospective", and "post hoc".

## 3. Defects (13)

1. **JAIR 608 / LNCS 574. Dangling reference to removed content.**
   - Quoted text: "Appendix~\ref{app:cpomdp_details} discusses these limitations and the diagnostic interpolation retained in the CSV."
   - What is wrong: H5 and H6b deleted every discussion of the interpolation diagnostic column from the CPOMDP and frontier appendices, so the appendix no longer discusses it. The phrase also implies an older lookup method.
   - Replacement: "Appendix~\ref{app:cpomdp_details} discusses these limitations."
2. **JAIR 499 / LNCS 465. Implementation history.**
   - Quoted text: "The CSVs regenerated under the relative comparison tolerance of Section~\ref{sec:pi1} are byte-identical to those generated under the earlier absolute tolerance, which did not bind at these points."
   - What is wrong: "regenerated" and "earlier absolute tolerance" describe an earlier implementation.
   - Replacement: "These CSVs are byte-identical under an absolute comparison tolerance, which does not bind at these points."
3. **JAIR 1864 / LNCS 2168. Same pattern.**
   - Quoted text: "The collapse CSVs were regenerated under the relative comparison tolerance of Section~\ref{sec:pi1} and are byte-identical to those produced under the earlier absolute tolerance, which did not bind at any swept point."
   - Replacement: "The collapse CSVs are byte-identical under an absolute comparison tolerance, which does not bind at any swept point."
4. **JAIR 1557 / LNCS 1861. Implies an earlier basis for the claim.**
   - Quoted text: "That conclusion now rests on a direct run of the nat-canonical agent rather than on reading between two grid points."
   - Replacement: "That conclusion rests on a direct run of the nat-canonical agent rather than on reading between two grid points."
5. **JAIR 339 / LNCS 305. Implies a mislabel was kept.**
   - Quoted text: "It is not Thompson sampling, despite the preserved CSV label \texttt{ThompsonSamplingAgent}."
   - Replacement: "It is not Thompson sampling, although the committed CSVs label it \texttt{ThompsonSamplingAgent}."
6. **JAIR 1745 / LNCS 2049. Same pattern.**
   - Quoted text: "The committed CSVs record it under the legacy label \texttt{ThompsonSamplingAgent}, retained so the artifacts stay stable."
   - Replacement: "The committed CSVs record it under the label \texttt{ThompsonSamplingAgent}."
7. **JAIR 2192 only (checklist). Implies earlier versions.**
   - Quoted text: "every table and figure reporting experimental results in this version was produced under them."
   - Replacement: "every table and figure reporting experimental results in this article was produced under them."
8. **JAIR 1899 / LNCS 2203. Implies a published earlier version.**
   - Quoted text: "The test itself was added after an earlier comparison of the same two policies on the same canonical seeds, one without any equivalence test, had already been reported, so the margin was chosen with that comparison known"
   - What is wrong: "had already been reported" implies an earlier reported version. The retrospective disclosure should stay, and it should read like its main-text twin at 599 ("had been inspected").
   - Replacement: "The test itself was added after an earlier comparison of the same two policies on the same canonical seeds, one without any equivalence test, had been inspected, so the margin was chosen with that comparison known"
9. **JAIR 2073 / LNCS 2377. Design history.**
   - Quoted text: "The heuristic already in Table~\ref{tab:rocksample}, originally added for the POMCP comparison, settles which one holds"
   - Replacement: "The heuristic already in Table~\ref{tab:rocksample}, POMCP's approach-then-check rollout rule run standalone, settles which one holds" (this matches line 2061's description of the "Rollout only" row).
10. **JAIR 750 / LNCS 716. "Original" wording, and the retrospective disclosure is missing from the main text.**
    - Quoted text: "The original POMCP comparisons use untuned exploration constants. A separate sweep selects constants on tuning seeds under a rule recorded before the runs reported here."
    - What is wrong:
      - "Original" reads as a version history.
      - The main body now reads as fully prospective. It drops the property Pat listed as one that must remain (the rule and grid were written after the canonical-seed sweep had been inspected), which survives only in the POMCP appendix at 1604. The canonical seeds are the evaluation seeds, so this bears on the Tiger claim.
    - Replacement: "The POMCP comparisons outside the exploration sweep use untuned exploration constants. A separate sweep selects constants on tuning seeds under a rule recorded before the runs reported here and written after an exploratory sweep on the canonical seeds had been inspected."
11. **JAIR 2150 / LNCS 2454. Same missing disclosure (Appendix Y).**
    - Quoted text: "under a rule recorded before the runs reported here."
    - Replacement: "under a rule recorded before the runs reported here and written after an exploratory sweep on the canonical seeds had been inspected."
12. **JAIR 518 / LNCS 484. H1 logic and grammar.**
    - Quoted text: "Decay-only recovers more slowly on every seed, and on one of the ten not within the window."
    - What is wrong: the sentence asserts recovery "on every seed" and then says one seed does not recover. The elided verb also makes the second clause hard to parse.
    - Replacement: "Decay-only is slower than reset-on-shift on every seed, and on one of the ten it does not recover within the window."
13. **JAIR 1931 / LNCS 2235. Grammar left by H6a.**
    - Quoted text: "Two further policies were added after the first results had been inspected, and are disclosed as such in the producer's docstring."
    - What is wrong: after the clause was deleted, the comma splits a compound predicate.
    - Replacement: "Two further policies were added after the first results had been inspected and are disclosed as such in the producer's docstring."

## 4. Advisories (not counted)

- **A1. Sleep-contaminated Tileworld timings.**
  - The Tileworld rows of `results/results_mcts_efe.csv` are inflated by system sleep from 16:24:56 on 2026-09-29 (see Section 1). The ledger's "the reported timings are uncontended" (`full_paper_plan.md` line 1593) is true for every cited value but not for the committed file as a whole.
  - Either rerun the Tileworld rows under `caffeinate -i`, or restore those two columns from `parts/` and record which rows came from which run. Qualify the ledger sentence in either case.
  - The manuscript is unaffected.
- **A2. Git stamps name pre-fix code.** The rerun sweep and tuning CSVs are stamped `git_sha=9e6ffde`, but they were produced with the uncommitted `rho_aif/agents/pomcp.py` fix. Checking out `9e6ffde` reproduces the pre-fix planner. After committing, record the lineage in the ledger (the stamp mechanism in `run_experiment.py` has no dirty flag) or regenerate the stamps. The checklist claims git-revision provenance for batteries in general.
- **A3. README appendix letters.** The new README rows cite "Appendix R", which is LNCS numbering. In JAIR, `app:pomcp` is Appendix S and the tree-search controls are Appendix Y. This matches the README's existing LNCS-numbered convention ("Section 6.9", "Section 6.6"), but a JAIR reader will look in the wrong place.
- **A4. CHANGELOG wording.** "the planner was paid twice the cost for every observation it simulated" is imprecise. It was credited +cost instead of charged −cost, a swing of twice the cost. Suggested wording: "credited each simulated observation its cost instead of charging it, a swing of twice the cost". Everything else in the 2.1.0 entry matches the code and tests: `rollout_belief="path"` is the default, `"root"` is retained, `--merge` and `--out` exist, and `--lineage` exists in the fresh-seed runner. The version is 2.1.0 in both `pyproject.toml` and `__init__.py`.
- **A5. AI-use statement.** JAIR 863 says the AI tools were used for "generating simulated referee reviews". This is a process disclosure, not an error history, so keeping it is Pat's call.
- **A6. JAIR 1920 wording.** The line has a pre-existing prose colon ("rather than a mixture: the"), which should become ", the ... policy on Diagnosis" or a new sentence. "We report the current resolution" could read "the present resolution", which is optional.
- **A7. JAIR 1929 / LNCS 2233.** "The study was predeclared in the producer's docstring before any result was inspected" sits beside the two post hoc additions (1931, 1935). The main text at 632 is more precise ("Its original design was recorded..."). Suggested: "The study's original design was predeclared ...".
- **A8. JAIR 2052 (H9).** The sentence is redundant with the preceding paragraph's p = 0.24 statement but harmless.
- **A9. Code history.** A code comment ("pre-2026-09-29 behavior") and a test name (`test_root_mode_keeps_legacy_behavior`) carry history. This is code, not manuscript, and it is consistent with the CHANGELOG allowance.
