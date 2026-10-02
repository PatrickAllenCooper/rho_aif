# Independent numerical and analysis readiness assessment

Date: 2026-10-01. Recommendation: ready for the root task's bounded training smoke and frozen evaluation after its required code commit and complete test run. No calibration or held-out policy outcomes were used in this assessment.

## Scope and resolved defects

I inspected `experiments/run_real_sensor_study.py`, `experiments/analyze_real_sensor_study.py`, the frozen Markdown/JSON protocol, and the model API. The runner and analysis were authored by the parent task. I authored the sensor model and its separate hand-oracle tests, so this is an independent review of the runner/analysis and a direct numerical check of my own model, not an independent review of that model's source.

The following findings were sent to the parent and their corrections verified in source before evaluation:

- The original `U12` split array truncated the 13-character `shift_overlap` label. The corrected width preserves later overlap flags and the inclusive sensitivity set.
- Checkpoint reuse originally validated only case count. The run now binds checkpoints to model, prepared data, protocol, code, policy, and row identities, and verifies archived hashes before reuse/analysis.
- H1 success now requires an available original crossing, as well as successful bootstrap draws and interval containment. An unattainable original target cannot become a reported success merely because bootstrap selections exist.
- Mixture validation now rejects unknown candidate names, negative/nonfinite mass, and mass that does not sum to one.
- Empty later batches after overlap exclusions are explicitly unavailable, and are not fed to a zero-case bootstrap or a complete equal-batch mean.
- The crossing procedure strictly preserves the predeclared no-bracket failure, even at an exact lower-edge plateau. The separate equality LP can still represent a directly attainable plateau.

The model uses the protocol's global relative tolerance, rather than a nontransitive sequence of pairwise near-tie comparisons. Its padded path field matches the runner. The saved class list is a one-dimensional list, compatible with the analysis's explicit label-to-posterior-column mapping.

## Inference audit

The within-period bootstrap draws calibration and test counts independently within their original batch/class strata. Each calibration resample is shared across every target and family. It reselects crossing brackets, probabilities, and equality/cap LP mixtures on that resample. Each test resample is shared across candidate policies, preserving paired comparisons. Both stages use actual per-case cached outcomes. The procedure does not refit the observation model and does not represent independent training replications.

Null selections produce missing bootstrap values and counted failures. H1 cannot pass with failed draws. Intervals with failed draws remain summaries of valid selections, with valid and failed counts explicitly attached. That qualification must remain visible in the results narrative. Later-batch intervals retain the original calibration selection. They do not reselect a best method on a later batch or estimate population variability across independent devices.

The mixture estimand is an episode-level random choice of a complete policy. Expected accuracy, sensor use, return, log loss, and Brier score correctly average component outcomes. Averaging terminal posteriors first and then scoring the averaged distribution would instead evaluate a different ensemble predictor. The seeded mixture artifact is a separate realization and does not manufacture additional independent cases.

Thirteen additional fixture tests in `tests/test_real_sensor_analysis.py` pass. They cover component-score mixture semantics with deliberately unsorted class IDs, changed trajectory/row/model/run identities, malformed mixture weights, counted unavailable bootstrap draws, and rejection of H1 success for an originally unavailable crossing. They use only tiny synthetic arrays. The other independent reviewer owns split, equality-versus-cap, and per-resample reselection tests.

## Training numerical warning investigation

The CPU environment uses Python 3.9.6, NumPy 2.0.2 linked to Apple Accelerate, SciPy 1.13.1, and scikit-learn 1.6.1. The frozen model hash is `316d5ffe75610b3f0f4c0b19d8ef1a89660e71b260dc3dce0f60b2022cd5a7f5`. No model refit was performed during this audit.

`audit_training_numerics.py` selects only the stored 3,550 training rows, checks their IDs against model provenance, and compares BLAS arithmetic against independent `einsum(..., optimize=False)` and elementwise summation. The complete evidence is in `training_numerics_audit.json`.

- All sixteen standardized sensor blocks and centroids are finite. Maximum standardized magnitude is 58.9602933733, below the training-size bound sqrt(3550).
- BLAS products differ from independent summation by at most 9.09494701773e-13.
- Scikit-learn squared distances differ from direct broadcast-and-sum distances by at most 1.81898940355e-12.
- All 56,800 sensor assignments agree. Their counts exactly reconstruct every stored smoothed likelihood row. The independent assignments also equal the frozen encoder output.
- Every reconstructed cluster inertia is finite. BLAS versus independent inertia differs by at most 9.09494701773e-13.
- The tested training calculations reproduce 144 divide-by-zero/overflow/invalid warnings while returning the finite, independently verified results above.
- Identity matrices of sizes 15, 16, and 64 reproduce the same three warnings and return the exact identity. Sizes 2 and 14 do not warn. These controls contain no experimental data and no arithmetic magnitude capable of producing overflow.

This evidence supports a platform floating-point-status warning issue in the tested operations rather than overflow in the sensor data. NumPy's primary release notes document an Accelerate/M4 warning fix, and its issue tracker reproduces the same warning with identity-matrix multiplication. Those records corroborate the local diagnosis without replacing the arithmetic checks. [NumPy 2.3.1 release notes](https://numpy.org/doc/stable/release/2.3.1-notes.html), [NumPy issue 29820](https://github.com/numpy/numpy/issues/29820).

No warnings were globally suppressed. The audited results justify retaining the frozen model. The root may use explicit multiply-and-sum or unoptimized einsum for simple analysis reductions to avoid warning spam while preserving the stated arithmetic. The audit does not certify all possible BLAS calls or reconstruct every intermediate Lloyd iteration. Standard shape, probability, and finiteness checks remain required throughout the run.

## Remaining interpretation limits

This readiness decision concerns protocol fidelity, data separation, and verified arithmetic. It predicts no favorable usage or accuracy result. Learned sensor independence remains an approximation. Case-resampling intervals remain conditional on one fitted model and exchangeability within represented strata. Researcher-selected access targets, retrospective masking, and later-period transfer cannot be described as a stakeholder requirement, physical sensing savings, or deployment.
