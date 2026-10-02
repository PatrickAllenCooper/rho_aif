# Independent pre-evaluation study audit, 2026-10-01

**Decision: proceed with the bounded training-only smoke and, if its measured compute gate passes, the frozen calibration/evaluation.** The reviewed design and corrected code implement the intended retrospective sensor-access study. No remaining blocker was found in my scope. This assesses readiness to measure the predeclared questions, not their empirical success or publication significance. Final artifacts and inferential claims still require an outcome audit.

## Scope and independence

I read the frozen protocol at commit `fb3a9de`, its JSON, the runner, the learned-model/replay module, and the bootstrap/analysis code available during development. I independently opened the primary UCI page. I added `tests/test_real_sensor_study.py` and ran artificial fixtures only. I did not download, fit, calibrate, evaluate, or inspect policy performance on any real calibration, test, or later-batch record. I did not change the model, runner, analysis, or manuscript.

Exact reviewed source hashes are in `pre_evaluation_audit_snapshot.json`. The source files were being actively developed, so this report does not silently certify later amendments. The final bounded test command was:

```text
.venv/bin/python -m pytest tests/test_real_sensor.py tests/test_real_sensor_study.py -q
```

Result: **32 passed**, 14 existing dependency warnings, 0.33 seconds. Fourteen tests in my new file concern parsing, partitioning, selection, and inference plumbing. Eighteen model tests maintained by the design agent exercise hand-computable policy and fitting invariants.

## Source and design assessment

The primary record supports the important structural choices: 13,910 observations from sixteen sensors, six gas identities, consecutive eight-descriptor sensor blocks, ten coarse collection batches, and a correction to batch 10. It also makes clear that each feature block summarizes an already recorded sensor response. Treating block access as an acquisition therefore supports retrospective information-access accounting, not measured energy savings or physically turning sensors off. [UCI Gas Sensor Array Drift Dataset, ID 224](https://archive.ics.uci.edu/dataset/224/gas+sensor+array+drift+dataset).

The frozen design is credible for its bounded purpose. Training-only quantization and categorical likelihood fitting give a learned model, while actual recorded categories drive replay. Calibration and within-period evaluation are disjoint, and later batches remain a distinct frozen-transfer test. Exact early duplicates stay in one partition, including cross-batch and conflicting-label groups. Later overlap is flagged for exclusion plus inclusive sensitivity. This addresses direct duplicate leakage without claiming that laboratory trials are independent or that random within-period splits simulate a new device.

The matched-depth comparison is also appropriately limited. Information-weighted and direct-penalty policies share the learned model, observation mask, action/tie conventions, cases, and terminal decision rule. Direct penalties may subsidize acquisition to span equality targets. Fixed-count conditional-information and fixed-order baselines ask whether calibration offers anything beyond counting acquisitions. All-sensor inference is a learned classifier, not an oracle. The cost and targets remain researcher-defined benchmark choices.

## Findings corrected before evaluation

1. **Replay archive API mismatch.** The first runner used `result.order` while the dataclass exposed `acquisition_order`. The runner now uses the canonical field, and the model also supplies a compatibility alias. This prevented the first trajectory-save failure.
2. **Global versus sequential tie rule.** Sequential pairwise comparisons can disagree with the frozen global-maximum tolerance rule when near ties form a chain. The model now computes the global score scale, gives stop priority, and chooses the lowest eligible sensor index. A dedicated hand fixture distinguishes these algorithms.
3. **Later-overlap partition truncation.** The design agent found that a 12-character NumPy dtype truncated `shift_overlap`. The runner now retains the complete category. My independent duplicate fixture explicitly checks that later overlap remains identifiable and outside the ordinary `shift` group.
4. **Protocol and checkpoint binding.** The runner now verifies the JSON against the frozen Git object as well as the Markdown hash. Evaluation checks the selection's calibration/protocol binding. Immutable run identities include model, prepared-data, runner/module, policy-registry, row-ID, and selection hashes rather than trusting checkpoint row counts alone.
5. **Exact-minimum crossing exception.** The first helper returned a single policy at an exactly attained minimum even when the shared crossing routine marked it unbracketed. The frozen H1 says every unbracketed target fails. Root chose to honor that declaration literally: all unbracketed cases now return no crossing policy. The equality LP can still report an attainable plateau separately. A test covers usages `[2,2,4]` at target `2` and verifies that the crossing method retains the failure.
6. **Original-selection feasibility in H1.** H1 now requires a feasible original crossing selection as well as zero failed bootstrap draws and simultaneous interval containment. Bootstrap reselection cannot turn an unavailable original method into a reported calibration success.

These corrections were made without examining real held-out performance. They align implementation with the frozen design rather than adapting the method to measured outcomes.

## Independent fixture coverage

The parser fixture reverses feature-token order, verifies source feature indices and original line identities, and rejects missing or repeated descriptors. Partition fixtures verify deterministic 60/20/remainder stratum allocation, whole duplicate-group assignment across early batches, conflicting-label counts, later overlap, and pairwise disjoint train/calibration/test descriptor sets.

The crossing fixture has multiple upward crossings and verifies that the last one is selected, its mixture weights are valid, and its expected usage is exactly the target. Other fixtures retain below-range, above-range, descending-tail, and exact-minimum unbracketed failures. The LP fixture makes sensing uniformly costly so equality references must spend the target while cap references optimally spend zero. This demonstrates that the two comparators answer different questions.

Bootstrap fixtures verify fixed stratum mass, shared per-case weights across policies, a fresh calibration selection for each replicate, and visible failure accounting. A deliberately failed calibration draw remains in the denominator and prevents H1 success. Grid tests independently reconstruct every frozen information weight and direct penalty from the declared formulas.

## Inference and reporting constraints that remain in force

The within-period bootstrap includes calibration reselection but conditions on one fitted model and within-stratum exchangeability. It does not cover retraining variation, trial dependence, new instruments, or between-batch population variation. Later-period intervals retain the original selections and describe each period separately. Equal-batch means are descriptive summaries, not new independent samples.

The analysis records failed bootstrap replicates and H1 fails if any crossing replicate is unavailable. The quantile routine nevertheless calculates numerical intervals from the feasible replicates. If any primary H2 comparison has failures, its interval must be labeled conditional on feasibility, or categorical shortfall inference must be withheld. Reporting only that conditional interval as the planned unconditional result would be misleading. The archive's failure counts must accompany the affected comparisons.

Frozen mixtures are equality-matched on calibration, not automatically on new cases. Report paired realized usage differences beside accuracy/return gaps. A confidence interval overlapping zero is not equivalence. The planned six primary accuracy contrasts need Holm correction only if inferential p-values are introduced; nominal paired intervals alone are the predeclared interval analysis.

No GPUs are needed. The training-only smoke must document throughput, candidate evaluations, memory, and the extrapolated full-grid cost before the full run. Final verification must check row/model/selection lineage, all three targets including failures, mixture realization versus analytical expectations, four later batches and overlap sensitivity, and the complete required artifact set. A failed H1 or a worse decision trade-off is a valid study outcome.
