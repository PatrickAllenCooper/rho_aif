# Polish brief: what changed in the bug-fix and accept sessions (2026-10-01)

Covers ledger 9.17.57 and 9.17.58 (2026-09-28 to 09-30). The current state is five unqualified Accepts from five providers (Gemini, Sol, Grok, Opus, Fable).

## 1. The POMCP bug (ledger 9.17.57, release v2.1.0)

Fable found two real defects in the observe-then-commit POMCP baseline (`rho_aif/agents/pomcp.py`).

- **Cost sign.** The planner added observation costs where every other planner subtracts them, so it planned as if sensing were subsidized. Fixed. `tests/test_pomcp_cost_sign.py` guards it.
- **Root-belief rollouts.** Every rollout started from the root belief, so observing earned no credit. Rollouts now start from the belief along the simulated path (`rollout_belief="path"`). A test guards this too.
- **Reruns.** Every POMCP battery was rerun: the main table, the exploration sweep with its tuning and selection, compute-matched, and the MCTS-EFE rows. Every non-POMCP agent reproduced bit-identically. Timings were rerun alone, uncontended.
- **Changed findings.**
  - POMCP now trails EFE and Planning on success and reward in every environment (Tiger 89.2, Diagnosis 70.5, Bandit 47.2, Tileworld 2.6 percent).
  - Bandit's old POMCP success lead was an artifact of the sign bug.
  - Tuned POMCP is now significantly below MCTS-EFE on Tiger, so "recovers most of the gap" and "fail to reject" were withdrawn.

## 2. Diagnosis frontier robustness (9.17.57)

- A predeclared fresh-seed replication (seeds 12 to 21, `run_frontier_fresh_seed_replication.py`) again finds eight of eleven distinct budgets short of the cap reference.
- Which Diagnosis budgets fall short changes. The paper says so.
- The replication seeds are disclosed as not fully blind, because one Diagnosis pair had already been evaluated on them.

## 3. No error history in the manuscript (Pat, 2026-09-29)

- The manuscript states current methods and results only. Correction notes, superseded numbers, "earlier version" and "referee" framing, and legacy references were removed.
- **Kept on purpose:** post hoc, retrospective, and non-blind disclosures, and the AI-use statement.
- The history lives in the ledger, `CHANGELOG.md`, and `reviews/`.

## 4. Appendix trim (ledger 9.17.58)

- 123 audited edits removed duplication and failed-attempt narration.
- The Flat-MC baseline was dropped from RockSample, with Holm recomputed.
- Every appendix section now starts with `\FloatBarrier`, and ten subsection headings are title-cased.

## 5. Two new predeclared experiments (answering the hostile associate editor)

### Episode-matched SARSOP equivalence

`run_tost_sarsop.py --episode-seeding`, 20 seeds:

| Environment | Paired difference | Paired p_TOST |
|---|---|---|
| Diagnosis | +0.11 +- 0.09 | 3.2e-9 |
| Bandit | +0.04 +- 0.03 | 4.6e-12 |
| Tiger | identical policies | not applicable |

- Equivalence holds.
- The held-out Diagnosis -1.01 +- 0.18 is explained as seed-set variation, about 2.8 SE away.
- Locations: Section 6.6, the SARSOP appendix, and the frontier appendix.

### Target-matched frontier reference

`run_frontier_target_reference.py`:

- **Construction:** subsidized SARSOP policies, combined by an equality-constrained LP so the reference's usage equals B.
- **Shortfalls:** 2 of 11, on both held-out and fresh seeds (previously 8 of 11 against the cap reference). Only Bandit's gap budget recurs.
- **Cap shortfalls explained:** six of the eight held-out shortfalls were at slack budgets. Seven of the eleven distinct budgets were slack. **Correction, 2026-10-01:** the original brief conflated those counts; the manuscript already stated the seven-budget fact correctly.
- **Post hoc sensitivity:** `--usage-matched` matches the reference to realized held-out usage and replays the fitted reference on fresh seeds. It makes Tiger's held-out mean gaps zero and Bandit's held-out recurrence marginal. **Correction, 2026-10-01:** the fresh Tiger mean gaps are not zero, and fresh realized reference usage need not equal the fitting target.
- **Locations:** the abstract, the Introduction, Section 6.9, the frontier table (new Target reference and Target gap columns), and the frontier appendix.

## 6. Smaller referee fixes (9.17.58)

- **Epistemic-only outcome.** Explained as forced by units: the maximum one-step information gain (0.39 bits on Tiger, 0.278 on the others) is below the cost.
- **RockSample.** RS[11,11] is scoped to the leaf rule. The RockSample caption gives each pairwise outcome.
- **Bandit and Tileworld.** Their success dip from w=0.5 to w=1 is stated.
- **Diagnosis B=9.53.** The shortfall is attributed to the w=1 usage-plateau policy versus unpenalized SARSOP.
- **POMCP appendix.** "exact beliefs" is no longer listed as a difference from POMCP, which also uses exact beliefs.

## Guardrails for the polish pass

1. **Length.** JAIR is 111 pp with references on page 38, and the main body must stay within 40 pages. LNCS is 142 pp. Both have zero overfull boxes.
2. **Both masters.** Mirror every edit in `paper/full_paper_jair.tex` and `paper/full_paper.tex`. The checklist is JAIR-only.
3. **Numbers are locked.** Do not change a figure without its CSV. Run `python tools/review_pipeline/verify_claims.py`.
4. **No history.** Do not reintroduce correction or version narration.
5. **Calibration words.** SARSOP and CPOMDP references are "near-optimal/estimated", never "exact". Use "exercises", not "validates". w is not the Lagrange multiplier.
6. **Style.** No semicolons in prose, and no rhetorical italics or bold.
7. **Overleaf package.** Refresh it after any edit: `python tools/build_overleaf_package.py --output paper/rho_aif_jair_overleaf_2026-09-28.zip`.
