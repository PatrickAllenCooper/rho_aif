# Adversarial audit of the panel / AE / frontier / TOST batch (2026-09-30)

Scope: the uncommitted working tree against HEAD `445daf9` in `paper/full_paper_jair.tex` and `paper/full_paper.tex`, the scripts `apply_panel_fixes.py`, `apply_ae_fixes.py`, `apply_frontier_fixes.py`, and `apply_tost_fixes.py`, plus the inline edits made after them, the regenerated tables, the producers, the new CSVs, README, and the `epistemic_only.py` docstring. Every check below was run against the CSVs and code, not the prose. Line numbers are those of the working tree at 21:05 on 2026-09-30. JAIR lines are given as `J`, and LNCS lines as `L`.

## What was verified and holds

- **Target-reference numbers.** Every value added to the abstract, Section 6.9 (J677), the main table `tab:budget_frontier_main` (Target gap column), the appendix table panel 3 (Target reference and Target gap columns), and the appendix paragraph (J1937) matches `results_budget_frontier_target_reference.csv` at printed precision. The checked values are -0.59, -0.50 (SE 0.11), -0.56 (SE 0.24), -0.16 (SE 0.12), +0.08 (SE 0.04), -0.05 (SE 0.16), B=9.53, B=7.72, B=5.51, B=4.72, and the twelve table cells 5.28, 4.93, 4.58, -2.11, -1.35, -2.26, -2.06, 6.22, 5.78, 4.90, and 6.21. The cap-side -1.10 (SE 0.22) is `results_budget_frontier_heldout_reference.csv`.
- **Counts.**
  - Held-out intervals excluding zero against the target reference are Diagnosis B=9.534 (upper end -0.33) and Bandit gap (upper end -0.042), which is two of eleven.
  - Fresh-stream exclusions are Diagnosis B=7.719 (upper end -0.026) and Bandit gap (upper end -0.263), again two. Diagnosis gap includes zero by +0.0002.
  - None of the four is at a slack budget, and only Bandit's gap budget recurs.
  - Against the cap reference, eight of eleven held-out intervals exclude zero.
  - The cap is slack (support `lam=0:q=1`) at exactly Tiger's three distinct budgets, Bandit's three interior budgets, and Diagnosis B=11.349.
- **"At the four binding budgets it coincides with the cap reference."** This holds to all stored digits, with identical supports (Diagnosis 0.25, 0.5, and gap, and Bandit gap). Fresh-stream values at those budgets also equal `results_budget_frontier_fresh_seed_replication.csv`.
- **"its support includes a subsidized policy"** holds at all seven slack budgets. Bandit 0.5 (λ=-0.35, -0.4) and 0.75 (λ=-0.4, -0.475) mix two subsidized policies. The script's original wording, "mixes the unpenalized policy with a subsidized one", would have been false, and the inline correction is right.
- **"no interval excludes zero on either stream" at slack budgets** holds on both streams.
- **"neither the family nor any policy in either reference support makes a wrong commit in the 500 held-out episodes."** This holds. Held-out reward plus usage equals 10.000 for Tiger λ=0, λ=-0.95 (the only subsidized support point), and all three family mixtures. On the fresh stream λ=0 does err (reward plus usage 9.78), and the text correctly restricts the claim to held-out.
- **Episode-matched TOST.** All numbers match `results_tost_sarsop_episode_paired.csv` and recompute from the per-seed file.
  - Paired results: +0.1118 (SE 0.0899) and +0.0435 (SE 0.0313), with p_TOST 3.20e-9 and 4.58e-12.
  - Unpaired results: 3.80e-5 and 1.76e-8.
  - Setup: twenty seeds {42, 123, 456, 789, 1024, 2000..2014}, 500 episodes, and margins 1.0, 1.0, and 0.5.
  - Tiger's per-seed means are identical on all twenty seeds.
  - The `--episode-seeding` code calls `run_otc_episode(agent, env, seed=s*10000+ep)`, which calls `env.reset(seed=...)` and `agent.reset()`. That matches "the same hidden states and the same observation draws for as long as their actions agree" and the frontier `episode_seed` convention.
- **1.01±0.18 (J1935).** This recomputes from committed artifacts. The w=0.316 endpoint per-seed rewards in `results_budget_frontier.csv` minus the λ=0 held-out per-seed rewards give -1.008, with SE 0.181.
- **Producer protocol (`run_frontier_target_reference.py`).** It follows the 9.17.58 predeclaration.
  - Subsidy grid: λ=-c·s with s in {0.1,...,0.9, 0.95, 0.98} and c=min cost. All costs within each environment are equal, so "c the observation cost" is accurate.
  - Solver settings: discount 0.999 (`write_pomdp_file_lagrangian` default) and precision 1e-3.
  - Streams: held-out {7..11} and fresh {12..21}, 100 episodes per seed, per-episode seeding.
  - Lineage: an abort on any mismatch with the committed held-out per-seed rewards.
  - Fit: `lp_mixture(..., equality=True)` on held-out means, with the weights q frozen and applied to the fresh per-seed rewards.
  - Intervals: t on n-1 degrees of freedom.
  - The family's fresh-stream rewards it recomputes equal the committed replication CSV.
- **R4.** In bits, the Blahut-Arimoto capacity of every sensor is below its cost: Tiger 0.390 against 1, Diagnosis 0.278 against 1, Bandit 0.278 against 0.5, Tileworld (accuracy 0.80) 0.278 against 1. Because expected information gain per step never exceeds capacity, no observation sequence of any length nets positive. That covers the agents' horizons (6, 3, 2, and 2) and both Tileworld grids. Running `EpistemicOnlyAgent._evaluate` from the initial belief returns a commit with G=0 in all four environments. The new docstring is accurate.
- **Champion et al. 2026.** The arXiv 2402.14460 record defines exactly four formulations: risk over states plus ambiguity, risk over observations plus ambiguity, information gain plus pragmatic value, and expected energy plus entropy. Its IGPV information gain is the expected KL over hidden states, so "the information-gain and pragmatic-value form, with information gain about the hidden state" (J213, J1650) is accurate.
- **Success sweep and w=1 run.** These were checked against `results_pareto_sweep.csv`.
  - Success maxima at w=200 on all five environments.
  - The dip from 0.5 to 1 occurs on Bandit (0.8944 to 0.8692) and Tileworld (0.7476 to 0.7204) only.
  - w=1 lies in the reward-maximizing tied run on Tiger, Diagnosis, and Bandit ({1, 2}), and not on Testbed or Tileworld.
  - No reward-tied "bracket" remains in either master.
- **New RockSample caption claim.** "not significantly different from EFE on RS[5,3] and RS[7,4] and earns more on RS[7,8] and RS[11,11]" matches the stats CSVs: p=0.29 and 0.65, not significant, and 0.00046 and 0.000028, Holm-significant.
- **Mirroring.** Every added or removed line in one master has its counterpart in the other. The only differences are the abstract's `\textbf{Results:}` prefix and the JAIR-only checklist item on RockSample.
- **Style.** No prose semicolons on any changed line. No "exact" is applied to SARSOP or CPOMDP references. No version or defect history is narrated in the new text.
- **References and length.** A fresh build of the current source in a scratch copy gives zero undefined references or citations and no overfull boxes. The JAIR PDF has 111 pages with "References" on page 38, and the LNCS master compiles clean under tectonic. Every pointer target added by the panel script exists: `app:nearopt_horizon`, `app:discount`, `app:interpretation` (which contains "Zero-Shot Weight Transfer"), and `app:full_tables`, whose five tables match the new lead sentence. `verify_claims.py` reports no hard failures.

## Defects

### D1. Stale column pointer in Section 6.9 (both masters)
- File and line: `full_paper_jair.tex` J675, `full_paper.tex` L641.
- Text: "The final column of Table~\ref{tab:budget_frontier_main} pairs each seed's mixture reward with its reference reward on the same episode seeds."
- Why it is wrong: the main table's final column is now "Target gap". The paragraph describes the same-stream cap comparison, which is the "Cap gap" column.
- Fix: "The Cap gap column of Table~\ref{tab:budget_frontier_main} pairs ...".

### D2. Stale column pointer in the frontier appendix (both masters)
- File and line: J1931, L2235.
- Text: "(the last two columns of Table~\ref{tab:budget_frontier}, \texttt{experiments/\allowbreak run\_\allowbreak frontier\_\allowbreak reference\_\allowbreak heldout.py}, ...)".
- Why it is wrong: panel 3 now ends with "Target reference" and "Target gap". The same-stream intervals are in the "Same-stream reference" and "Paired gap" columns.
- Fix: "(the Same-stream reference and Paired gap columns of Table~\ref{tab:budget_frontier}, ...)".

### D3. README frontier row is stale and gives a broken run order
- File and line: `README.md`, Budget-frontier row (around line 160).
- Text: "then `python experiments/run_frontier_reference_heldout.py` (same-stream reference and paired gaps, the table's last two columns), then `python experiments/build_budget_frontier_table.py`".
- Why it is wrong:
  - Those are no longer the last two columns.
  - `build_budget_frontier_table.py` now reads `results_budget_frontier_target_reference.csv`, so it must run after `run_frontier_target_reference.py`.
  - The target producer itself reads `results_budget_frontier.csv` and `results_cpomdp_frontier_heldout.csv`.
  - The separate target-reference row does not state this dependency.
- Fix:
  - Change the parenthetical to "the Same-stream reference and Paired gap columns".
  - Insert `python experiments/run_frontier_target_reference.py` (the Target reference and Target gap columns) before the build step.
  - Note in the target row that it requires the frontier and held-out reference CSVs.

### D4. Overgeneralized subsidy effect (both masters)
- File and line: J1937, L2241.
- Text: "SARSOP is solved at eleven subsidized penalties $\lambda=-c\,s$, ... so net observation reward stays negative while usage rises above the unpenalized level."
- Why it is wrong: per `results_cpomdp_frontier_subsidy.csv`, usage does not rise for small subsidies.
  - Diagnosis s=0.1 to 0.6 gives held-out usage 9.72 to 9.82, below the unpenalized 9.888.
  - Bandit s=0.1 (λ=-0.05) gives 5.110, below 5.198.
  - Tiger s≤0.6 gives exactly the unpenalized 4.316.
  - Only the larger subsidies raise usage.
- Fix: "... so net observation reward stays negative. The larger subsidies raise usage above the unpenalized level, to at most $7.17$ on Tiger, $16.58$ on Diagnosis, and $11.59$ on Bandit on the held-out seeds, while the smaller ones leave it unchanged or slightly lower." Both clauses come from the subsidy CSV.

### D5. Main-text equivalence gloss on the Diagnosis B=9.53 shortfall conflicts with the matched held-out data (both masters)
- File and line: J677, L643.
- Text: "Diagnosis's held-out shortfall at $B{=}9.53$ mostly pairs the $w{=}1$ usage-plateau policy with the unpenalized SARSOP policy at nearly equal usage, a pair that is equivalent within the margin on episode-matched streams (Section~\ref{sec:sarsop})."
- Why it is wrong, first part: on the five held-out seeds, which are themselves episode-matched (per-episode seeds 10^4 s + e), this pair differs by 1.01±0.18 (J1935). That exceeds the 1.0 margin. Equivalence was established only by the twenty-seed episode-matched check.
- Why it is wrong, second part: "the $w{=}1$ usage-plateau policy" is in fact w=0.316, which the mixture plays with probability 0.94. Its behavioral identity with w=1 is inferred from identical per-seed calibration usage and reward from w=0.316 to 19.3 in `results_budget_frontier_curve.csv`. It is not checked on the held-out stream in any committed artifact, and the ledger's exploratory `/tmp/r1/diag.py` checked EFE against Planning+IG at w=1 only.
- As written, the sentence reads as explaining the shortfall away.
- Fix: "Diagnosis's held-out shortfall at $B{=}9.53$ mostly pairs a policy on the usage plateau containing $w{=}1$ with the unpenalized SARSOP policy at nearly equal usage. The twenty-seed episode-matched check of Section~\ref{sec:sarsop} finds that pair equivalent within the margin, although on these five held-out seeds it differs by $1.01\pm0.18$ (Appendix~\ref{app:frontier_details})."

### D6. The Tiger rare-event sensitivity was deleted, but claims that depended on it remain unqualified (both masters)
- File and line: J679/L645 (deletion), J677/L643, and J1935/L2239.
- Text kept: "Under that fitted comparison, negative $95\%$ intervals exclude zero at eight of eleven distinct budgets" (J677), and "The plug-in intervals therefore support the aggregate shortfall count and the Tiger and Bandit rows" (J1935).
- Text deleted from J679: "If the reference retained that rate while the family never erred, the smallest-budget shortfall would reverse and the middle-budget shortfall would nearly vanish. Only the largest Tiger shortfall is robust to that sensitivity calculation."
- Why it is wrong: the arithmetic still holds. The cap gaps -0.33, -0.72, and -1.03, plus the 0.66 that a 0.6 percent error rate is worth, give +0.33, -0.06, and -0.37. Three of the eight cap shortfalls are Tiger rows, two of which do not survive the paper's own sensitivity calculation. J1935 now asserts support for "the Tiger rows" without that qualification. J679 keeps only a generic "rare-event uncertainty the nominal intervals do not capture".
- Fix, either option:
  - Restore one sentence at J679/L645: "Under that rate, the smallest-budget cap shortfall would reverse and the middle one nearly vanish."
  - Or change J1935/L2239 to "support the aggregate shortfall count, Bandit's rows, and Tiger's largest-budget row".

### D7. Positive Tiger target gaps are pure usage error, and the slack-budget conclusion needs that caveat (both masters)
- File and line: J1937/L2241, and the table cells.
- Text: "The held-out target gaps there run from $-0.16\pm0.12$ (Bandit, $B{=}5.51$) to $+0.08\pm0.04$ (Tiger, $B{=}4.72$)".
- Why it is misleading: on the held-out stream every Tiger sampled reference point and every Tiger family mixture satisfies reward = 10 - usage, which the zero-wrong-commit check above confirms. So the target reference at B is exactly 10 - B, and each Tiger target gap equals B - U, the mixture's usage shortfall.
  - B=4.719 and U=4.642 give gap 0.077.
  - B=5.070 and U=5.038 give gap 0.032.
  - B=5.421 and U=5.348 give gap 0.073.
  - The top of the reported range therefore reflects under-spending the target, not efficiency.
- The reference meets B exactly, but the family meets it only within its usage error, so the target gap mixes usage error into reward. The auditor's exploratory check, not for citation, re-solved the equality LP at each row's realized held-out usage:
  - All Tiger gaps become 0.000.
  - Diagnosis B=9.53 still excludes zero (upper end -0.30).
  - Bandit's gap-budget interval reaches +0.001.
- The predeclared readout at B stands, but the reader should know this.
- Fix: add after the range sentence: "Because every Tiger policy here earns $10$ minus its usage, Tiger's target gaps equal the mixture's usage shortfall below $B$ and measure no reward efficiency."

### D8. The target reference is called a single policy (both masters, abstract and introduction)
- File and line: J81/L50 and J121/L87.
- Text: abstract, "Against the best sampled reference policy that meets the same target". Introduction, "relative to spending less or to the best sampled policy meeting the same target".
- Why it is wrong: at every budget the reference is a per-episode mixture of two sampled policies, for example Tiger B=4.72 is λ=0 with q=0.86 plus λ=-0.95. No single sampled policy has usage equal to any target. Section 6.9 and the appendix correctly say "best sampled mixture".
- Fix: "Against the best mixture of sampled reference policies that meets the same target" (abstract). "or to the best sampled reference mixture meeting the same target" (introduction).

### D9. "Unconstrained reward optimum" without estimate qualification (both masters)
- File and line: J677, L643.
- Text: "the cap is slack and the reference is the unconstrained reward optimum."
- Why it is wrong: the reference is the unpenalized SARSOP policy evaluated on five seeds. The project vocabulary requires "near-optimal or estimated" for SARSOP references, and the appendix (J1931) says "near-optimal and estimated rather than exact".
- Fix: "the reference is the unpenalized SARSOP policy, the estimated unconstrained reward optimum."

### D10. Checklist per-seed archive list omits the new archives (JAIR only)
- File and line: J2173.
- Text: "per-seed means for the SARSOP TOST comparison at $n{=}5$ and at $n{=}20$ (... `results_tost_sarsop_per_seed.csv`, `results_tost_sarsop_n20_robustness_per_seed.csv`), per-seed usage and reward for every budget-frontier row ... and for its same-stream reference (`results_cpomdp_frontier_heldout.csv`), ...".
- Why it is wrong: three new per-seed archives cited in the text are missing.
  - `results_tost_sarsop_episode_paired_per_seed.csv`.
  - `results_cpomdp_frontier_subsidy.csv`, with per-seed rewards on both streams.
  - `results_budget_frontier_target_reference.csv`, with per-seed gaps on both streams.
- The fresh-seed replication's `per_seed_gap` column is also absent. That omission predates this batch, but it is now adjacent to the new entries.
- Fix: extend the list with "the episode-matched TOST (`results_tost_sarsop_episode_paired_per_seed.csv`)" and "the subsidized reference points and target-matched gaps on held-out and fresh seeds (`results_cpomdp_frontier_subsidy.csv`, `results_budget_frontier_target_reference.csv`, `results_budget_frontier_fresh_seed_replication.csv`)".

### D11. Checklist seeding item and ENVIRONMENT.md misdescribe the TOST runner and omit seed sets (JAIR only, plus ENVIRONMENT.md)
- File and line: J2176. Also `ENVIRONMENT.md` lines 19 and 25.
- Text: "The SARSOP, constrained-POMDP, TOST, and calibration-table runners (... `run_tost_sarsop.py`, ...) seed the stream once per outer seed and let it continue across that seed's episodes".
- Why it is wrong: under `--episode-seeding`, which the paper now reports, `run_tost_sarsop.py` seeds `env.reset` per episode at 10^4 s + e. The checklist's enumerated deviations also omit the n=20 seed set {2000..2014} and the fresh seeds {12..21} that the replication and the target-matched reference use. ENVIRONMENT.md line 19 repeats the same TOST statement, and its line 25 archive list lacks the episode-matched and target-reference files.
- Fix:
  - Append to the TOST clause: ", except that `run_tost_sarsop.py --episode-seeding` seeds each episode at $10^4 s + i$".
  - Add to the deviations: "the fifteen added seeds $\{2000,\dots,2014\}$ of the $n{=}20$ and episode-matched SARSOP checks, and the fresh seeds $\{12,\dots,21\}$ at $100$ episodes/seed of the frontier replication and target-matched reference".
  - Mirror both changes in ENVIRONMENT.md.

### D12. Provenance stamps point to a commit without the producer, and the subsidized policies are untracked
- Files: `results/results_cpomdp_frontier_subsidy.csv` and `results/results_budget_frontier_target_reference.csv`.
- Text: `git_sha` = `445daf9` in every row.
- Why it is wrong:
  - `445daf9` is HEAD, and `experiments/run_frontier_target_reference.py` is untracked. HEAD's `build_budget_frontier_table.py` and `run_tost_sarsop.py` also lack the changes these outputs depend on. This is the same stamp-lineage defect that ledger 9.17.57 fixed by restamping.
  - The 33 subsidized SARSOP `.pomdp` and `.policy` pairs in `results/sarsop_models/` are untracked, and the producer's `solve_sarsop` uses a 120 s timeout. A different machine could therefore produce a different policy. The episode-matched TOST CSVs carry no provenance at all, which is consistent with the TOST convention, but they have no stamp to check.
- Fix: commit the producer and policies, then restamp both CSVs to the commit that contains the producer, recording the restamp in the ledger. Alternatively, rerun after committing.

### D13. Table producer stamps omit the new producer
- File and line: `paper/tables/budget_frontier.tex` (panel 3 comment), J645/L611 (main-table comment), and `experiments/build_budget_frontier_table.py` (the comment string).
- Text: "%% Numbers produced by experiments/run_budget_frontier.py and experiments/run_frontier_reference_heldout.py".
- Why it is wrong: the Target reference and Target gap cells come from `run_frontier_target_reference.py`. Per-table producer stamps are the project's structural fix for propagation drift.
- Fix: add `experiments/run_frontier_target_reference.py` to the stamp string in the builder, regenerate the table, and update the hand comment at J645/L611.

### D14. The ledger, CHANGELOG, and edit record are incomplete (process)
- Files: `Guidance_Documents/full_paper_plan.md` 9.17.58, `CHANGELOG.md`, and `apply_frontier_fixes.py`.
- Why it is wrong:
  - 9.17.58 records both predeclarations but no outcomes and no HOLD/PARTIAL/FAIL verdict, as the stage-verdict process rule requires. Nor does it note that the main-body Diagnosis sentence at J677 and the D5 claim rest on values derived post hoc.
  - CHANGELOG [Unreleased] does not mention `run_tost_sarsop.py --episode-seeding` or the new producer and CSVs.
  - `apply_frontier_fixes.py` no longer reproduces the manuscript. It still writes "mixes the unpenalized policy with a subsidized one". Three inline edits appear in no script: the D5 sentence at J677, "its support includes a subsidized policy", and the bracket-to-run pass.
- Fix: record outcomes and verdicts in 9.17.58, add CHANGELOG entries, and record the inline replacements in a script or in the ledger.

### D15. Main-body overstatement of episode matching (both masters)
- File and line: J602, L568.
- Text: "A predeclared twenty-seed check reseeds every episode so both policies face the same episodes."
- Why it is wrong: after the two policies' actions diverge, they no longer face the same observation draws. The appendix (J1903) states this correctly: "the same hidden states and the same observation draws for as long as their actions agree".
- Fix: "... reseeds every episode so both policies face the same hidden states and, while their actions agree, the same observation draws."

## Count

15 defects. D1 to D9 and D15 are manuscript defects mirrored in both masters, D10 and D11 are JAIR-checklist defects (D11 also covers ENVIRONMENT.md), and D3 and D12 to D14 are artifact, README, and process defects. The most consequential for a hostile referee are D5, D6, and D7. In those, the new text either contradicts the paper's own matched held-out number or hides that a reported gap is a usage error. D1 and D2 are mechanical pointer errors created by the new table column.
