# Round 2 report, lens `decision_theory_pomdp`

Manuscript: `paper/full_paper_jair.tex`, working tree on top of `9e6ffde` (uncommitted changes read via `git diff HEAD`). Rendered PDF `paper/full_paper_jair.pdf` dated after the source, 117 pages, Conclusion on p.37, References on p.38.

## 1. Recommendation

**Accept.** Both required changes from round 1 are implemented in the code, the results, and the prose, and every POMCP-derived conclusion I could locate now follows from the rerun numbers. No remaining required changes. Two optional wording suggestions are listed in Section 5.

## 2. What changed and whether it resolves round 1

Round 1 required change 1 (POMCP simulator credited each observation with +cost). `rho_aif/agents/pomcp.py` now charges `-obs_cost` in `_simulate` and `total -= gamma_power * obs_costs[...]` in `_rollout`. Rollouts additionally start from the belief updated along the tree path (`rollout_belief="path"`, the child belief is `belief * obs_models[a][:, o]` renormalized). The two new test files pass, and the full suite passes (492 tests). Every POMCP battery was rerun, and I reproduced two rows of the new `results/results_pomcp.csv` bit for bit from the fixed code under `run_pomcp.py`'s configuration (Section 6). Non-POMCP rows (EFE, Planning, Exact-EFE, MCTS-EFE) in `results_pomcp.csv`, `results_mcts_efe.csv`, and `results_pomcp_exploration_sweep.csv` are numerically identical to HEAD.

Round 1 required change 2 (Diagnosis same-stream shortfall not reproducible on fresh seeds). Instead of the one-sentence qualification I proposed, the authors ran a predeclared fresh-seed replication of all twelve held-out rows (`experiments/run_frontier_fresh_seed_replication.py`, seeds 12 to 21, 100 episodes per seed, nothing refit, lineage replay to 1e-9). The main text (line 676) now reports the replicated count and defers the Diagnosis instability to Appendix `app:frontier_details` (lines 1939-1940), which states plainly that the Diagnosis 0.5 shortfall of -0.76 becomes +0.02 +/- 0.29, that the Diagnosis pair was not blind, and that the intervals "support the aggregate shortfall count and the Tiger and Bandit rows, not the identity of the Diagnosis budgets that fall short." The abstract (line 80) carries the same qualification. This is a stronger resolution than the one I asked for.

The removal of version-history language was flagged by the orchestrator as intentional, and I did not treat it as a defect. The analysis-design disclosures that matter for my lens remain in place: the fitted comparison being added after inspection (line 1935), the selection rule written after an exploratory sweep (line 1604), the non-blind Diagnosis pair (line 1940), and the Tiger rare-event caveat (line 680).

## 3. Do the POMCP conclusions still follow from the new numbers?

Yes, and in several places the new numbers make the conclusions cleaner than before, because the sensing subsidy had been inflating POMCP's observation counts and success rates unevenly across environments.

- Table `tab:pomcp` (lines 1575-1588): POMCP(1000) now trails EFE and Planning on reward and success on all four environments, so the caption-level claim "underperforming both EFE and Planning on reward and success rate on every environment" (line 1594) is true without the earlier Bandit exception. Bandit's POMCP row moved from 7.20 observations and 87.7 percent success to 1.34 and 47.2 percent, which is the direction my round-1 sign check predicted.
- Fidelity paragraph (line 1562): lists two remaining gaps (clairvoyant depth-cap leaf, belief-expected commit credit in rollouts) and correctly describes the path-belief rollout. Both remaining gaps are, as stated, favorable or neutral to POMCP. The ordering claim "gap smallest on Tiger, larger on Diagnosis, Bandit, and Tileworld" checks out at 10.2, 26.7, 39.7, and 69.3 points.
- Simulation-budget scaling (line 1596): every number matches the CSV, including Bandit's non-monotone sweep (50.9, 47.2, 51.6, 62.1 percent) and the 5.7x wall-clock ratio (181.8 / 31.8 ms). "The gap is therefore not a simulation-budget artifact" follows.
- MCTS-EFE paragraph (line 1598): the simulation-matched POMCP(500) figure is now 88.1 percent at H=10, the compute-matched budget is 661 simulations at 13.87 s, and both POMCP configurations remain behind MCTS-EFE at p < 0.0001 on both metrics. The Welch test between POMCP(661) and POMCP(500) (p = 0.89 and 0.85) supports "does not close the gap at this exploration constant."
- Exploration sweep (line 1604, Table `tab:pomcp-sweep`): the round-1 finding "we fail to reject on either metric at c=50" has become "remains behind MCTS-EFE at its default constant on both metrics after Holm correction (p = 0.0002 and 0.002)", and the tuned-against-tuned comparison is now significant on both success (p = 0.0001) and reward (p = 0.0005). The tuning-seed selections stated in prose (MCTS-EFE c=5 on Tiger and Diagnosis, default on Tileworld, POMCP c=50 uniform on Tiger, c=5 uniform on Diagnosis, c=5 info-gain on Tileworld) are exactly what the stated rule produces from `results_pomcp_exploration_tuning.csv`, including the Tiger and Diagnosis MCTS-EFE ties broken by reward. The statement that the evaluation seeds would have picked the same configurations on Tiger and Tileworld and c=2 on Diagnosis is correct. The dagger pattern in the table matches the `_stats` companion (every POMCP row and only Tileworld's MCTS-EFE c=5 row).
- Main-body summaries: line 843 now says "Tuning POMCP's exploration constant narrows the Tiger gap without closing it. With both solvers' constants selected on disjoint tuning seeds, MCTS-EFE remains significantly ahead on Tiger success and reward." That is what the sweep and `results_pomcp_exploration_selected.csv` show (93.2 vs 98.2 percent). Line 750 is a hedged pointer and makes no numerical claim.
- Appendix Y (lines 2146-2156): all POMCP figures updated consistently with the appendix (88.1 +/- 0.2, p = 4.4e-6, Diagnosis 65.5 +/- 2.1 at p = 1.1e-4, Tileworld 2.6 and 3.9 percent at 0.09 scans, p < 1e-9). The gap floors "above twenty-five points on Diagnosis and above eighty points on Tileworld at every swept configuration" hold at the tightest rows (94.2 - 69.1 = 25.1 and 94.9 - 8.2 = 86.7).

## 4. Strengths (unchanged from round 1, briefly)

The Price of Information section is internally consistent on notation (w*(B) crossing threshold, (w_lo, w_hi] grid estimate, hat-w(B) grid point), the feasible-envelope reference is shared by every constrained comparison, the frontier study's calibration/held-out split and now the fresh-seed replication are predeclared and archived, the dual-control comparison is on a restricted estimand with paired intervals, and the POMCP baseline is now a faithful cost-charging, path-belief planner whose remaining departures from Silver and Veness are both stated and favorable to the baseline.

## 5. Optional suggestions (not conditions)

1. Line 750, main body, net-neutral. "A separate sweep selects constants on tuning seeds under a rule recorded before the runs reported here." The appendix (line 1604) discloses that the rule and its grid were written after an exploratory sweep on the canonical seeds had been inspected. The main-text sentence is literally true but reads as prospective. Suggested replacement of equal length: "A separate sweep selects constants on tuning seeds under a rule fixed before these runs, after an exploratory sweep." (Cut "recorded" and "reported here".)
2. Line 1939, appendix. The replication's Diagnosis 0.25 row moves from an interval including zero (-0.03 +/- 0.78) to one excluding it (-0.56 +/- 0.24). The text reports this. One clause could state the symmetric reading, that a five-seed interval can miss a shortfall as well as manufacture one, which strengthens the "seed-set variation" conclusion the paragraph reaches.

The round-1 optional items (U(w*) wording at line 456, the recovery floor of 19 in `dual_details`, the lambda = 0.05 support note, per-seed SD in the frontier table) were not adopted. They remain optional.

## 6. Verification log

Read: `git diff HEAD` for `paper/full_paper_jair.tex` (all 55 hunks, word level), `rho_aif/agents/pomcp.py`, `experiments/run_pomcp.py`, `experiments/run_pomcp_exploration_sweep.py`, `experiments/run_frontier_fresh_seed_replication.py`, `tests/test_pomcp_cost_sign.py`, `tests/test_pomcp_rollout_belief.py`, `paper/tables/pomcp_exploration_sweep.tex`, tex lines 80, 116, 428, 518, 674-682, 750, 843, 1562-1612, 1939-1941, 2146-2158.

Quantitative claims checked against CSVs (all match to the printed precision):

| # | Claim (tex line) | Artifact | Result |
|---|---|---|---|
| 1 | Table tab:pomcp, 12 POMCP cells (1575-1588) | `results_pomcp.csv` | match |
| 2 | Bandit 47.2 +/- 1.0, 86.9 +/- 0.3, +4.58 +/- 0.09, +6.27 +/- 0.04 (1594) | `results_pomcp.csv` | match |
| 3 | POMCP(5000) Diagnosis 71.6 +/- 0.9, 323.6 vs 93.8 ms, Tiger 89.5 +/- 0.3 vs 89.2 +/- 0.2, Bandit 50.9/47.2/51.6/62.1, +5.56 +/- 0.10, 5.7x, Tileworld max 3.8 percent (1596) | `results_pomcp.csv` | match |
| 4 | MCTS-EFE(500) 97.7 percent, 14-16 ms, POMCP 88.1 percent, 11-12 ms, Exact-EFE 99.9 percent at 64 ms (1598, 2146) | `results_mcts_efe.csv` | match |
| 5 | Compute-matched 13.87 s, 661 sims, 32 percent, 88.0 +/- 0.6, -4.80 +/- 0.69, 13.88 s, 88.1 +/- 0.2, -4.67 +/- 0.19, 10.42 s, p = 0.89/0.85, p < 0.0001 (1598) | `results_pomcp_compute_matched.csv` | match |
| 6 | Sweep Table tab:pomcp-sweep, 33 rows, dagger pattern | `results_pomcp_exploration_sweep.csv`, `_stats.csv` | match |
| 7 | c=50 vs MCTS-EFE default p = 0.0002 and 0.002, best-vs-best p = 0.0001 and 0.0005 (1604, 2150) | `_stats.csv`, `results_pomcp_exploration_selected.csv` | match (1.59e-4, 2.07e-3, 1.00e-4, 5.10e-4) |
| 8 | Tuning-seed selections and evaluation-seed counterfactuals (1604) | `results_pomcp_exploration_tuning.csv` | match, rule reproduced by hand |
| 9 | Info-gain rollouts: Diagnosis p = 0.57, Tileworld success p = 0.0002 survives Holm, reward p = 0.012 does not (1604, 2152) | `_stats.csv` | match |
| 10 | Appendix Y p = 4.4e-6, 1.1e-4, < 1e-9 at both Tileworld budgets, 0.09 scans, 91-93 pp (2146, 2156) | `results_mcts_efe.csv` | match |
| 11 | Fresh-seed replication: 9 of 12 rows, 8 of 11 distinct, 11 of 12 negative, Diagnosis -0.82 +/- 0.28, +0.02 +/- 0.29, -0.56 +/- 0.24, -0.46 +/- 0.20, Bandit smallest includes zero, mixture q = 0.94 at w = 0.316, reference 0.91 at lambda = 0 (676, 1939) | `results_budget_frontier_fresh_seed_replication.csv` | match |
| 12 | Gap floors 25 and 80 points at every swept configuration (2154) | sweep CSV | 25.1 and 86.7 at the tightest rows |

Code and lineage:

- `pomcp.py` sign and path-belief logic read in full (lines 100-220). In-tree commit uses the sampled-state reward, rollout commit uses the belief-expected reward (disclosed), depth-cap leaf is clairvoyant (disclosed).
- `python -m pytest tests/ -q`: 492 passed.
- Replay from the fixed code with `run_pomcp.py`'s configuration (scratch `pomcp_round2_replay.py`): Tiger POMCP(1000) success 0.8916, reward -3.5674, obs 1.6434, SE 0.1797/0.0016. Bandit POMCP(1000) 0.4724, 4.5799, 1.3434, SE 0.0854/0.0104. Both identical to `results_pomcp.csv`.
- Non-POMCP rows of `results_pomcp.csv` (8), `results_mcts_efe.csv` (22), `results_pomcp_exploration_sweep.csv` (6) compared to `git show HEAD:` versions on all numeric columns except timings: max absolute difference 0.0.
- PDF: `pdfinfo` 117 pages, "9 Conclusion" on physical page 37, "References" on physical page 38. The rendered text contains the new POMCP figures (1.64, 47.2 percent, 93.2 +/- 0.5) and the replication sentence.

Not checked: the LNCS master `paper/full_paper.tex` (outside this lens's brief), the `select_pomcp_constants.py` script itself beyond reproducing its rule by hand from the tuning CSV.

## 7. Would you recommend unqualified Accept if the required changes were made?

There are no remaining required changes. The recommendation is unqualified Accept as the manuscript stands.
