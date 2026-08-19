# Post-JAIR Directions: Ideation Refresh

**Date**: August 19, 2026
**Status**: Draft ranking, produced at the start of the continuous-development phase. Supersedes the ordering (not the content) of `2026-07-22-rho-aif-extensions-ideation.html`, whose Rank 1 (price of information) is now fully executed as the headline of the JAIR manuscript, whose Rank 3 (benchmark release) is executed in substance pending the PyPI upload, and whose Rank 5 baseline debt (SARSOP, POMCPOW decision) is retired.
**Method note**: Rankings below start from the July 22 verifier-checked ideation, updated for what execution taught us. Confidence figures are carried or adjusted with reasons stated. Per the project's citation policy, no new citation enters any paper from this document without a verification check recorded in `price_of_information.md` or `full_paper_plan.md` 8.4.

## Standing context

The integrated manuscript (`paper/full_paper_jair.tex`) is at uniform internal referee accept. Its Discussion names four open directions (state-changing observations, drifting hidden states, MCTS-EFE tree policies, model learning), and execution surfaced two boundaries the July ideation could not see: the distractor result (budgets cap wasted sensing but do not redirect it, Stage G2) and Tiger's flat usage curve (no usable budget dial on saturating-instrumental-sensing environments).

## Ranked directions

### 1. The price of destructive information (sequel paper) — carried from Rank 2, confidence up 75% -> 80%

Destructive sensing is the most-flagged open problem in the manuscript's own Discussion, has a running start in the repo (Example ex:destructive, the transition-aware corrected operator, `tests/test_destructive_boundary.py`), and gains a synergy the July ideation could not price: with shadow prices done, sensing that destroys state spends two currencies at once — the sensing budget and future option value. The quasi-option-value framing becomes a budgeted rho-POMDP where w*(B) splits into an information price and an irreversibility premium.

Deliverables: corrected Bellman operator folded into the factored reduction; over/under-testing characterization; a destructive variant of Structural Inspection (tests that damage the inspected component); usage curves and dual control under destruction. Entirely on existing discrete infrastructure. Empirical-rigor note: design the environment battery and predeclare the comparison protocol before running anything.

### 2. Reward-conditional information measure (short paper or sequel section) — new, earned by Stage G2

The distractor experiment showed the budget framing caps waste without redirecting it, and the in-repo IDS is not a clean immune baseline (distractor fraction 0.311, comparable to Planning+IG at large w). A genuinely reward-conditional information measure — value only for information that changes the optimal decision, without the raw-entropy fallback — closes this boundary, pre-empts the most likely real-referee probe on the JAIR submission, and is publishable standalone or as a section of Direction 1. Candidate operationalizations to scope: decision-entropy (entropy over argmax-action posterior), expected value of sample information (EVSI-style), and myopic policy-divergence weighting; the audit-trail machinery (`rho_aif/audit.py`) already logs per-test VoI, giving a measurement harness for free.

### 3. Budgeted question-asking for LLM agents — carried from Rank 4, confidence held at 55%, scoop-risk gate

The executed work upgrades the pitch from "Prop 2 bands" to something operational: give an LLM agent a question budget B, derive its exploration weight by dual descent on the measured usage curve. The dual controller and usage-curve code exist. Scope: fast workshop paper on a twenty-questions testbed with ground-truth posteriors. HARD GATE before any commitment: redo the prior-art scan (BED-LLM, AutoDiscovery, InfoReasoner landscape is 13 months stale; the field moves fast).

### 4. Continuous-space budget theory — carried from Rank 5, re-scoped, heaviest lift

The remaining novelty after the POMCPOW NO-GO: do PI-1 exact scale equivariance, usage curves, and dual control survive particle beliefs and entropy estimation, plus IG-governed progressive widening for MCTS-EFE. Also owed here: the optimality-gap estimate on large factored environments that the paper twice defers. Justified only after Directions 1-2.

### 5. Cheap compounding wins (current submission)

- **Dual control against a cost-denominated target**: the accounting supports it (Stage D), it was never run — the last "supported but not run" note in the manuscript. One experiment; closes a disclosed gap. First in the queue under the empirical-rigor north star.
- **PyPI upload** (Patrick, credential-gated): unblocks the paper's own `pip install rho-aif` claim.
- **Benchmark announcement** (leaderboard-less), after the upload.

### 6. Low priority / standing rejections

Adaptive-submodularity certificates (45% confidence, negative-result risk, though the horizon-depth map provides free scaffolding). Model learning / BAMDP-EFE: the July verifier's prior-art collision stands; the paper's "important future work" phrasing does not commit us to it. All 15 rejection-table entries from July 22 remain in force.

## Immediate work queue derived from this ranking

1. Run the cost-denominated dual-control experiment (Direction 5a) and integrate into both manuscripts if clean.
2. Prototype the destructive-sensing environment battery design doc (Direction 1) — protocol predeclared before code.
3. Prior-art re-scan for Direction 3 (web, dated, recorded) before any further investment.
4. Keep the JAIR submission package current as reruns land (propagation rule).
