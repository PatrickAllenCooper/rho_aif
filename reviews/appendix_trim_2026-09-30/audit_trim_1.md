# Adversarial audit 1 of the appendix trim (scope: A and B proposals, Flat-MC producer and CSV changes)

Auditor: subagent, 2026-09-30. Read-only: no manuscript, code, or result file was edited.

## Scope and method

- Applied proposals audited: A01 to A13, A16 to A21 (A14 and A15 skipped per `skipped.txt`), and B01 to B09, B11 to B35 (B10 skipped). That is 53 edits.
- Every edit was located in the current masters by pre-trim context plus `new` text. Pre-trim copies `/tmp/jair_pre_trim.tex` and `/tmp/lncs_pre_trim.tex` are byte-identical to `HEAD`.
- Parallelism check: the set of differing lines between JAIR and LNCS was compared before and after the trim. The only newly differing line is in the JAIR-only reproducibility checklist, outside this scope. Every A/B passage is identical in both masters.
- Conventions: no semicolon in any new prose, no rhetorical emphasis, no "exact" applied to SARSOP or CPOMDP, no "validates".
- Flat-MC: there are zero matches for `Flat`, `one-ply`, or `flat Monte` in either master or in `paper/tables/`. The remaining hits are in the package (`RockSampleFlatMCAgent` is kept by design), in tests, and in CHANGELOG, CLAUDE.md, and AGENTS.md history.
- The Holm recomputation was checked independently with my own step-down implementation, NaN-excluding, on `p_seed_level` and `p_pooled` within (instance, metric). It matches all five stats CSVs. The removed rows are exactly the Flat-MC pairs: 14 per file on the four instances and 10 on the depth-3 check. Exactly one verdict flips, RS[7,8] Bad, Planning (d=3) vs Rollout only, seed-level p=0.00341. It is 9th in rank, against a threshold of 0.05/13=0.00385, so it now rejects (with 28 tests it did not). No Reward verdict flips and no pooled verdict flips. The table bolding (Reward, seed-level) is unchanged, and `build_rocksample_tables.py` reproduces both committed tables byte-for-byte from the current CSVs.
- Seeding: `run_rocksample.py` calls `np.random.seed(seed)` and builds the agent per (agent, seed), with per-episode env seeds. Dropping Flat-MC therefore does not perturb any other agent's rerun.
- Statistics appendix: "$21$ tests per metric per instance over its seven agents" matches the four instance stats files (C(7,2)=21 per metric). The depth-3 check file has 5 agents (10 per metric, one NaN pair excluded), but it is not "the RockSample table", so the sentence stays accurate.
- `tools/review_pipeline/verify_claims.py`: no hard failures.

## Numbers re-verified against artifacts

- A02: `results_tileworld_scaling.csv` 8x8 gives EFE 0.694 and Planning 0.014.
- A04: `results_summary.csv` gives EpistemicOnly 3.1512 obs and 0.8978 success, the same as Planning.
- A12: `results_summary.csv` gives PyMDP-AIF and InfoGain 3.15, 89.8%, +0.480, and EFE 5.50.
- A16: from `results_nearopt_horizon.csv`, 30 pass at H=1 and recur deeper, 26 pass at all deeper horizons, the exactly-one-deeper cases are environments [2, 42, 63, 95], 14 fail throughout, 56 underclaim, and 0 overclaim. The stratum percentages match `tables/horizon_map.tex`.
- B27: `results_rocksample_cpomdp_frontier.csv` has 12 lambda points in [0, 100], usage 0 or 1, and reward 9.5 or 12.306. EFE RS[7,8] makes 9.842 checks.
- B26: the rewritten gap wording matches main-body line 627 ("small relative to the estimates' standard errors").
- B18: main-body lines 217 to 219 define $Z$ and $-T\ln Z$, so the new pointer is valid.
- B15, B16, B21: the Tiger $[0.01,20]$, Diagnosis $[0.5,20]$, and Testbed $[0.01,0.5]$ brackets remain in Table `tab:alpha_eta`. The Testbed nat/bit separation is discussed after that table (line 1682). The tied-bracket definition now appears at line 1548, before its old location.
- B11: the "exercises this extension" statement survives at line 1699.
- B08: the POMCP behavioral trace that main-body line 2061 points to survives at line 1446.

## Defects

Line numbers refer to the current JAIR master, with the LNCS line in brackets.

1. **A05 reintroduces a section that opens directly on a subsection. This is a JAIR author-instruction violation.** JAIR 1020 to 1023 [LNCS 1333 to 1336].
   - Current text: `\section{Supplementary Figures}` / `\label{app:supp_figs}` / (blank) / `\subsection{EFE Trajectory Decomposition}`.
   - What is wrong: JAIR's author instructions say a section must not begin directly with a subsection. Ledger 9.17.44 (`full_paper_plan.md` line 1311) fixed exactly this appendix ("Supplementary Figures") as one of four such cases by adding a roadmap paragraph, and A05 deleted that paragraph. After the edit this is the only section in the appendix that opens on a subsection.
   - Replacement: after `\label{app:supp_figs}`, insert one short paragraph before the first `\subsection`, in both masters:
     `These figures support the main text but are not needed to follow it.`

2. **A16 removed the prose definitions of "overclaim" and "underclaim", which Table `tab:horizon-map` still uses.** JAIR 1309 [LNCS 1614].
   - Current text: "The remaining 56 fail at $H{=}1$ yet are near-optimal at some deeper horizon, a missed opportunity rather than a risk. No environment in this sample shows the opposite pattern, where $H{=}1$ predicts near-optimality and no deeper horizon delivers it. ... or that such overclaiming is impossible in general".
   - What is wrong: the generated table footer (`tables/horizon_map.tex`) reads "myopic overclaims 0, underclaims 56". Before the trim, the prose defined both terms ("myopic underclaiming", "myopic overclaiming"). Now neither is defined anywhere, and "such overclaiming" appears with no antecedent. This breaks the every-symbol-defined-at-first-use convention.
   - Replacement: "The remaining 56 fail at $H{=}1$ yet are near-optimal at some deeper horizon (the table's myopic underclaims), a missed opportunity rather than a risk. No environment in this sample is a myopic overclaim, where $H{=}1$ predicts near-optimality and no deeper horizon delivers it."

3. **A02: the pointer covers only one of the three agents, and the cross-battery reconciliation was dropped.** JAIR 978 [LNCS 1291], in the Tileworld 8x8 caption.
   - Current text: "The separate spatial-scaling sweep (Figure~\ref{fig:tw_scaling}), with a different per-seed episode count, gives $69.4\%$ for EFE and $1.4\%$ for Planning. Planning, untuned Info Gain, and Epistemic-only take no scans and tie Myopic exactly (mechanism in Appendix~\ref{app:tileworld_details})."
   - What is wrong:
     - Appendix `app:tileworld_details` gives the zero-scan mechanism only for reward-only Planning (the depth-2 lookahead). It says nothing about untuned Info Gain or Epistemic-only. The removed sentence carried the mechanism for all three ("a single noisy scan over 64 states barely narrows the belief").
     - The removed sentence also stated why the table's 69.8/1.8 differ from the sweep's 69.4/1.4. The two pairs are now printed side by side with no reconciliation. The proposal's own rationale said the reconciliation would be kept.
   - Replacement: "The separate spatial-scaling sweep (Figure~\ref{fig:tw_scaling}), with a different per-seed episode count, gives $69.4\%$ for EFE and $1.4\%$ for Planning, gaps consistent with seed-to-seed variation. Planning, untuned Info Gain, and Epistemic-only take no scans and tie Myopic exactly, because a single noisy scan over 64 cells barely narrows the belief (Planning's depth-2 case in Appendix~\ref{app:tileworld_details})."

4. **A04: "Even there" misframes the sentence that follows it.** JAIR 1018 [LNCS 1331].
   - Current text: "The high-asymmetry regime in which the interval analysis favors $w{=}1$ is discussed in Appendix~\ref{app:interpretation}. Even there, $w{=}1$ lies on the reward-maximizing plateau on Tiger and Diagnosis but is Pareto-dominated by $w{=}20$ on Tileworld (Section~\ref{sec:pareto})."
   - What is wrong: "Even there" signals a concession, but its first clause is the favorable result. The pre-trim text read "Within that regime".
   - Replacement: "Within that regime, $w{=}1$ lies on the reward-maximizing plateau on Tiger and Diagnosis but is Pareto-dominated by $w{=}20$ on Tileworld (Section~\ref{sec:pareto})."

5. **A18: the scope of the significance claim is ambiguous and literally false for Tiger.** JAIR 1364 [LNCS 1669].
   - Current text: "The transition between $\gamma{=}0.95$ and $\gamma{=}0.99$ is sharp, and the gaps at $\gamma \geq 0.99$ are significant after Holm correction."
   - What is wrong: the same paragraph opens with Tiger, whose gaps at $\gamma \geq 0.99$ are $0.0$ ($p{=}1.0$) and not starred in Table `tab:discount`. Only Diagnosis and Bandit carry the star.
   - Replacement: "The transition between $\gamma{=}0.95$ and $\gamma{=}0.99$ is sharp, and the Diagnosis and Bandit gaps at $\gamma \geq 0.99$ are significant after Holm correction."

6. **B27: "the same 12-point grid" has no antecedent.** JAIR 1784 [LNCS 2088].
   - Current text: "Applying the same per-observation penalty $\lambda$ over the same 12-point grid to this project's depth-3 tree search on RockSample[7,8]".
   - What is wrong: B26 compressed the preceding paragraph, which no longer mentions a 12-point grid. The grid is defined only later, in Appendix `app:cpomdp_details` (line 1905).
   - Replacement: "Applying the same per-observation penalty $\lambda$ over the 12-point log-spaced grid of Appendix~\ref{app:cpomdp_details} to this project's depth-3 tree search on RockSample[7,8]".

7. **B24: the grammar of the scope sentence is off, with an intuition "requiring" arguments.** JAIR 1771 [LNCS 2075].
   - Current text: "The standard intuition that the iterate instead stays in a step-size-dependent neighborhood of $w^*$, which would let the controller re-adapt after a shift, would require constant-step tracking arguments that we do not develop."
   - Replacement: "The standard intuition is that the iterate instead stays in a step-size-dependent neighborhood of $w^*$, which would let the controller re-adapt after a shift, but making that precise requires constant-step tracking arguments that we do not develop."

8. **B35: a comma is missing before a nonrestrictive "which".** JAIR 1611 [LNCS 1915].
   - Current text: "built from source by \url{tools/build_sarsop.sh} which applies and documents four compatibility patches".
   - Replacement: "built from source by \url{tools/build_sarsop.sh}, which applies and documents four compatibility patches".

9. **"genuine POMCP" is leftover wording from the removed Flat-MC contrast. This is optional and low severity.** The instances:
   - JAIR 1432 [LNCS 1737]: "including the genuine POMCP at its tuned frozen configuration".
   - JAIR 1438 [LNCS 1743]: "A genuine POMCP for RockSample is reported here (...)".
   - JAIR 2043 [LNCS 2347]: "POMCP is a genuine search-tree solver".
   - The producer captions in `build_rocksample_tables.py`: "the genuine POMCP at" (extended) and "POMCP is the genuine search-tree solver" (main).
   - What is wrong: with Flat-MC gone, "genuine" implies that a non-genuine POMCP existed. That is the kind of history the trim aims to remove, and Pat's 2026-09-29 rule says not to narrate earlier versions.
   - Replacements:
     - Line 1432: "including POMCP at its tuned frozen configuration".
     - Line 1438: "The RockSample POMCP (\texttt{rho\_\allowbreak aif/\allowbreak agents/\allowbreak rocksample\_\allowbreak pomcp.py}) builds a search tree ..." (merge the first two sentences).
     - Line 2043: "POMCP is a search-tree solver".
     - Producer captions: drop "genuine" and regenerate. "search-tree" is enough to contrast it with Rollout only.

10. **Producer: `refresh_stats`, and the CSV rewrite, perturb every kept row's floats. This is not a manuscript defect.**
    - What is wrong: the kept rows in all ten RockSample CSVs differ from HEAD in the last digits, with a maximum relative change of 1.2e-13 (for example, `se_bad_seed_level` 0.05147815070493507 became 0.051478150704935). The cause is `pd.read_csv` with the default float parser. I verified that `float_precision="round_trip"` makes the read-then-write round trip byte-identical on HEAD's `results_rocksample_7x8.csv` and `_stats.csv`. No printed number changes, but the files are no longer the untouched battery output apart from the removed rows, and git diffs show spurious changes on every line.
    - Fix: in `experiments/run_rocksample.py` `refresh_stats`, use `df = pd.read_csv(path, float_precision="round_trip")`. Then regenerate the ten CSVs from HEAD, dropping the Flat-MC rows with a round-trip read (or by line filtering), and rerun `--refresh-stats`. Also consider a unit test for `apply_holm` (none exists).

## Checked and found acceptable

- A01: the reason the two agents are absent ("observe-then-commit agents") was dropped, contrary to the rationale, but the absence itself is still stated. Not load-bearing.
- A03 and A04: the success-tuned trade-off is kept in the prose.
- A04 also removed the "one environment where posterior-vote ties the best" remark, which main-body line 748 and `app:core_details` still cover.
- A06 to A13, A17, A19 to A21, B05 to B09, B12 to B14, B17, B19 to B23, B25, B28 to B34: meaning is preserved, the cut boundaries read correctly, and the pointers resolve.
- B33 keeps the required disclosure that the selection rule and candidate grid were written after the exploratory sweep. The six-test family and the script remain named in the preceding sentence. Only "over the same candidate grid" was lost, which is minor.
- B31 correctly removes a causal attribution that the same appendix explicitly withholds.
- B02 and B03, with the producer changes: no dangling pointer.

## Process notes, outside this audit's pass/fail

- The ledger (`full_paper_plan.md`, `research_plan.md`) and CHANGELOG have no entry yet for the Flat-MC removal, the new `apply_holm` and `--refresh-stats`, or the RS[7,8] Bad flip.
- README's reproduction table lists `build_rocksample_tables.py` but not the `run_rocksample.py --refresh-stats` step that now sits in the lineage of the stats CSVs.
- The Overleaf ZIP (`paper/rho_aif_jair_overleaf_2026-09-28.zip`) still contains the old RockSample tables and the pre-trim source, so it needs a rebuild.
