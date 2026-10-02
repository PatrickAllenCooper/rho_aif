# Public-data extension and concision review

Completed 2026-10-01 against the previously reviewed `7b954ce` manuscript. The user requested additional empirical evidence and a shorter, clearer presentation, then selected a public dataset. Both final independent reviewers recommend **ACCEPT with no required revisions**. This is an internal assessment of the stated contribution, not a prediction of the journal's decision.

## Findings and scope

The predeclared UCI Gas Sensor Array Drift study replays real recorded sensor blocks under training-only learned likelihoods. Researcher-defined targets of 2, 4 and 8 accesses were fixed before usage curves were evaluated. The sampled weight family cannot attain two accesses on calibration. Four- and eight-access mixtures use 4.006 and 8.019 accesses within period and pass their conditional half-access criterion, but the all-three-target requirement fails. Their accuracy is lower than matched direct-penalty mixtures and fixed-count information acquisition. Every later batch exceeds both targets. The paper makes these failures explicit and claims neither deployment benefit nor a superior acquisition algorithm.

JAIR references now begin on page 33 rather than 38, with 108 pages overall rather than 111 despite the added study. LNCS decreases from 141 to 136 pages. Secondary results move to appendices, repetitive explanations are removed, Definition PI-3 separates its four mathematical objects, and a compact new figure shows transfer and accuracy separately. Proof assumptions and unfavorable evidence remain. The AI-use statement is unchanged.

## Frozen sequence and data

1. `fb3a9de` commits the protocol and [dated legacy alternative](../../paper/legacy/2026-10-01_pre_external_study/).
2. `e595e8f` commits the independently audited implementation, training-only preparation and concision before calibration/test evaluation.
3. `5a3a79d` commits calibration selections before held-out replay.
4. The final delivery commit adds held-out results, analysis, manuscript integration and the verified package.

The [study README](../../results/real_sensor_2026-10-01/README.md) gives reconstruction commands and archive schemas. The raw source ZIP is restored from UCI and checked against its frozen hash. Complete per-case archives, the fitted model and split, calibration selections, bootstrap draws and seeded mixture realizations are committed. All work used local CPUs. No GPU was allocated. An analysis-column clarification after evaluation changes metadata only, with [initial outputs preserved](initial_analysis/README.md) and numerical identity checked independently.

## Independent reviews

- [Evidence and significance review](independent_evidence_final_review.md): ACCEPT. Its [independent reconstruction](independent_evidence_audit.py) imports no policy or study runner module and checks 106 candidate archives, 549,080 trajectories, 3,392 scalar planning replays, every summary cell and all 2,000 calibration-reselection draws. [Machine-readable findings](independent_evidence_audit.json) and [reviewed hashes](independent_evidence_final_snapshot.json) are retained.
- [Scientific referee](independent_referee.md): ACCEPT. Reviews both masters, proof conditions, primary literature, contribution and practical limits. Its [snapshot](independent_referee_snapshot.json) identifies the reviewed artifacts.
- [Concision audit](concision_audit.md), [pre-evaluation audit](pre_evaluation_audit.md), [numerical investigation](numerics_and_analysis_readiness.md), [new citation verification](new_citation_verification.md) and [figure record](real_sensor_figure_notes.md) document earlier checks.

Theoretical integration remains modest in novelty. The external study uses one fitted model, retrospective observations and researcher-set requirements. These remain explicit limits. Neither final reviewer requires another experiment to seek more favorable outcomes.

## Delivery validation

[Validation output](delivery_validation.json) records exact final source/PDF/ZIP hashes, page counts, unchanged legacy hashes and a clean isolated build of the 39-file Overleaf ZIP. The extracted package produces PDF text identical to the canonical JAIR build. This is a local isolated build, not a hosted Overleaf test or journal submission.

The final test log reports [540 passed with 26 existing warnings](pytest_final.txt). Both manuscript logs contain no overfull boxes, missing characters or undefined references/citations. Changed definition, mathematics, main-study and protocol pages were rendered and inspected. [All 16 mechanical numeric advisories](claims_final_independent_adjudication.json) are resolved against protocol, selections, run timings or DOI prefixes.

The scripts `apply_concision.py` and `integrate_sensor_study.py` are guarded, one-time historical assemblers, not commands to rerun on the final sources. The earlier failed development test log is superseded by the pre-evaluation and final passing suites. Build logs and audit records are kept as evidence, while rendered scratch pages remain outside the committed review archive.

**Final task verdict: PASS.** Statistical failures are retained as results rather than being confused with failure to complete the task.
