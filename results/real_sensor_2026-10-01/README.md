# Public sensor-access study

This study replays actual cases from [UCI Gas Sensor Array Drift, ID 224](https://archive.ics.uci.edu/dataset/224/gas+sensor+array+drift+dataset). Each acquisition reveals the eight recorded descriptors of one of sixteen sensors. It measures retrospective access to stored records, not physical energy or time saved by operating sensors selectively.

The [frozen protocol](../../experiments/protocols/gas_sensor_2026-10-01.md) and JSON were committed as `fb3a9de` before calibration or test policies were evaluated. Targets 2, 4, and 8 are researcher-defined and independent of usage curves. One model is fitted on batches 1–6 training rows. Within-period calibration and test rows are separate, and batches 7–10 are a locked transfer test. No model is fitted or adjusted on the later batches.

## Reproduce

Use Python 3.9.6 with the repository's `requirements-lock.txt`, or install the experiment extra with `python -m pip install -e '.[sensor-study]'`. The recorded environment uses NumPy 2.0.2, SciPy 1.13.1, and scikit-learn 1.6.1. New CPU architectures may differ at numerical ties. The checked-in model and per-case archives fix the reported realization.

From the repository root, the following restores the raw data and encoded inputs from the archived model and split, without refitting:

```sh
python experiments/run_real_sensor_study.py prepare
```

The source archive is downloaded to `data/raw/gas_sensor_224.zip`. Its SHA256 must be `91e8f466f202e7a093d657673ce47311c3e90416f7df3057966058961c351fe4`. Source-file, row, model, and reconstructed encoding hashes are checked. The raw data remain at their primary source rather than being redistributed in this repository.

For a fresh execution, first preserve this entire result directory and the local `data/processed/gas_sensor_224.npz` under a different name, then run:

```sh
python experiments/run_real_sensor_study.py prepare
python experiments/run_real_sensor_study.py smoke
python experiments/run_real_sensor_study.py calibrate
python experiments/run_real_sensor_study.py evaluate
python experiments/analyze_real_sensor_study.py
```

The stages refuse to overwrite a completed run. Interrupted policy replay can resume only when the model, encoded records, protocol, source modules, registry, and frozen selections match its checkpoint identity. The first command fits only the training rows when no archived model exists. The smoke uses at most 128 training cases and checks the CPU time envelope. No GPU is used.

To recompute summaries from the archived policy trajectories, preserve `analysis.json`, `bootstrap*.npz`, `seeded_mixture_realizations.npz`, `per_class.csv`, and `results/results_real_sensor_summary.csv`, then run the analysis command. It validates trajectory, row, and model hashes before computing summaries. Re-analysis does not run episodes or refit the model.

## Archive schema

- `dataset_manifest.json`, `split_manifest.csv`, and `model.json` give the source, row partitions, training-only transforms, and likelihoods. Original row identity is batch plus source line number, bound to the dataset SHA256.
- Each `calibration/` or `evaluation/` candidate NPZ aligns with that directory's `rows.npz`. It contains correctness, sensor usage, base return, prediction, final posterior, acquired sensor order, observed categories, and candidate-evaluation counts. Paths use zero-based sensor/category indices and `-1` padding after stopping. Posterior columns follow `model.json`'s class order. `complete.json` binds every archive hash to the policy registry and measured batch runtime.
- `selection.json` gives calibration-only endpoint or LP probabilities. Its null weights retain unattainable or unbracketed requests. Direct penalties include subsidies to span equality targets. The cap and equality LPs are separate sampled-family references, not globally optimal constrained policies.
- `analysis.json` and `bootstrap*.npz` hold the fixed analysis and conditional case-resampling intervals. Within-period intervals reselect calibration brackets and LP supports. Shift intervals keep the original selection. Failed bootstrap fits are counted, and intervals with failures are conditional on feasibility.
- `seeded_mixture_realizations.npz` is a separate randomized implementation check. Reported means integrate the per-case endpoint randomness analytically. Repeated policies and bootstrap replicates are not independent cases or model fits.
- `per_class.csv` records class-specific accuracy and usage. The top-level `results_real_sensor_summary.csv` includes balanced accuracy, expected usage, base return, log loss, and Brier score for every selected policy and data partition.

The record count does not certify independence of laboratory exposures. Uncertainty is conditional on one trained model and exchangeability within batch/class strata. It excludes retraining, unobserved trial dependence, and new instruments or sites. Later-period rows reflect both measurement and class-composition changes.

Training produced NumPy/Accelerate warnings on this host. Independent broadcast-distance and non-BLAS checks recovered all 56,800 training sensor assignments and likelihood counts exactly. Identity-matrix controls reproduced the warnings while returning exact identities. The [numerical audit](../../reviews/extension_2026-10-01/numerics_and_analysis_readiness.md) records the evidence and avoids silently treating warnings as model failure or ignoring them.
