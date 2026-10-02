# Independent empirical-integrity review

Verdict: **ACCEPT. No required empirical corrections remain in the reviewed source.**

I independently reviewed all 12 early and 18 late empirical consolidation groups against the archived `c5125ab` manuscript, the applied live text, and the primary CSV/code records. This verdict concerns the scientific integrity of the shortened appendices. It does not inherit any earlier review verdict or predict JAIR's editorial decision. Exact source hashes are in `independent_evidence_snapshot.json`. Final PDF and Overleaf delivery checks are recorded separately by the coordinating agent.

## High-level assessment

The cuts are appropriate. Most removed text repeated numerical table readings, generic interpretations, or descriptions of illustrative trajectories. The remaining appendices still supply the protocol exceptions, inferential restrictions, negative controls, and failure cases needed to judge the main paper. No source data, experiment implementation, test, or bibliography entry has changed. The text before `\appendix` is byte-identical to the archived baseline in both masters. The complete public-sensor protocol subsection is also byte-identical in both masters.

The strongest unfavorable results remain visible: posterior-vote ties or beats EFE on relevant tasks, misspecification has no EFE-specific buffering, Navigation has no demonstrated epistemic advantage, POMCP can benefit from different computation and tuning, its standalone RockSample rollout can outperform search, the MCTS ablations do not detect success/reward effects, Inspection remains synthetic with a shared heuristic, and learned sensor policies overspend under chronological transfer. Nothing in the consolidation justifies stronger claims of universal superiority, cap optimality, deployment relevance, or controller tracking guarantees, and the final text does not make those claims.

The deletion of redundant figures is defensible because their distinctive observations and qualifications remain in prose or stronger retained figures. The removed figure PDFs remain in the repository. The set of external table inputs is unchanged. No removed graphic carried a unique indispensable uncertainty estimate that is now unavailable.

## Three regressions identified and corrected

1. **Wrong agent assigned to the low-penalty Tiger reward gap.** The initial condensed paragraph attributed a 1.6 reward loss to EFE. At penalty 1, the actual rewards are Planning 7.196, EFE 6.988 and tuned myopic Info Gain 5.610. The 1.586 difference belongs to the latter comparison. Both final masters now name tuned myopic Info Gain and the tested penalty explicitly. The pre-trim baseline had left the actor ambiguous, so this review also resolves that ambiguity.
2. **False belief-representation contrast with POMCP.** The initial condensed paragraph added beliefs to the architectural differences from exact EFE. `rho_aif/agents/pomcp.py` samples from the exact Bayesian root belief and updates rollout path beliefs by exact Bayes. The final comparison correctly retains tree enumeration, leaf values and commit values without that extra distinction.
3. **Untested weight included in a sampled optimum.** The initial Pareto summary said the Testbed maximizing run included zero. The actual eleven-point sweep begins at 0.01, and its maximizing sampled weights are 0.01, 0.1 and 0.5. Both masters now state the sampled range 0.01–0.5, agreeing with the main text and CSV.

In addition, both showcase summaries now state their 100 episodes per seed over five seeds explicitly. The earlier shorthand of 500 episodes was numerically correct but could be read as a per-seed count. Producer comments on the two compacted numerical tables were restored without affecting layout.

## Independent numerical checks

`independent_evidence_checks.py` reads the committed CSVs directly and does not import experiment or policy modules. Its output is `independent_evidence_checks.json`. I checked the following evidence beyond comparing old and new prose:

- All nine additional-core baseline rows and the 12 pooled reward SEs retained for main-table agents match the primary environment CSVs. The distinction between pooled and seed-level uncertainty remains explicit.
- All 24 effect-size matrix cells reproduce from the original pooled `cohens_d` fields with the appropriate comparison direction. The condensed table does not substitute inflated five-seed effect sizes.
- The paired discount layout preserves every outcome from the original 24 agent rows. Grouped settings really are identical. Percentage-point gaps use unrounded estimates, explaining the apparently inconsistent rounded Diagnosis and Bandit cells. The correction family remains 24 tests.
- Controller conditional recovery means and normal intervals recompute from the nine recovering decay runs and all ten reset runs. Restricted means recompute as 157.3 and 51.2 across all ten pairs, with paired mean difference 106.1 and Student interval [96.7701, 115.4299]. The minimum improvement is 89 episodes. Reset has lower final error on five seeds, ties on four and is worse on one. Conditional descriptives, the primary restricted estimand, and censoring remain distinct.
- CPOMDP selected weights reproduce from the baseline CSV, with finite-grid plateau endpoints from the usage-curve CSV. Neither table gap nor finite-grid equality is promoted to a certified population claim.
- The partition-study reward p-value independently reconstructed from means and seed SEs is 0.243363. Scan counts 15.565 and 2.695 produce the reported 15.57 and 2.70 under ordinary decimal half-up rounding. They are precision-detector artifacts, not changed outcomes.
- The matched RockSample diagnostic reward is 16.895, conventionally rounded to 16.90. The larger-instance heuristic earns 28.658 and collects 5.216 good rocks, supporting the reported 28.66 and 5.22. These arise from different, explicitly identified battery files than the nearest CSV detected mechanically.
- The target-reference negative intervals identify Diagnosis's middle target and Bandit's gap target on held-out data, and Diagnosis's smallest target plus Bandit's gap target on fresh data. Thus the shortfall count repeats while only Bandit's identity repeats. The final prose preserves both fitted-reference uncertainty omissions and non-blind Diagnosis qualifications.

## Mechanical advisories and scope preservation

`claims_initial.txt` contained **94 numerical advisory occurrences**, not only the first 58: 58 nearby-CSV mismatches plus 36 unresolved-number occurrences across the two masters. `numeric_adjudications.json` records a source and resolution for each occurrence. The two mirrored occurrences of the erroneous low-penalty actor claim required the correction above. All remaining numbers resolve to the appropriate primary source, a transparent conversion, a recomputed summary, or conventional decimal rounding. The two separate hard table-content messages were lexical false positives for “ordered rows.” The final source instead names the row order directly.

The saved protocols still distinguish calibration-derived targets from application requirements, target equality from a usage cap, prospective checks from post-inspection amendments, shared seed labels from episode matching, conditional uncertainty from total uncertainty, and non-rejection from equivalence. The frontier's plug-in and rare-event limits, the baseline fidelity qualifications, and the public-data study's fixed-model retrospective scope survive the consolidation. Those distinctions are more important than retaining every explanatory repetition.

No new experiment is needed for this editorial consolidation. The retained evidence remains traceable and sufficient for the bounded contribution. I support the shortened version on empirical and reproducibility grounds.
