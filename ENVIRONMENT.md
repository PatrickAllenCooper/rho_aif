# Execution environment of record

The simulation batteries use the configuration below. The recorded-sensor study
has separate platform metadata, listed after the table. Bitwise reproduction is
tied to the recorded platform and pinned packages because floating-point results
can differ across processors and system math libraries.

| Item | Value |
|---|---|
| Machine | Apple M5 Max, 36 GB RAM (single machine, no GPU used) |
| OS | macOS 26.6.2 |
| Python | 3.9.6 (`.venv`) |
| Pinned packages | `requirements-lock.txt` (`pip freeze` of the venv that produced the artifacts) |
| Minimum versions | `pyproject.toml` |
| SARSOP solver | `tools/sarsop/src/pomdpsol` (APPL, built from source, patched for Apple Silicon as described in the manuscript's SARSOP appendix) |
| Seeds | canonical `{42, 123, 456, 789, 1024}`. The benchmark, budget, RockSample, Structural Inspection, distractor, budget-frontier, and dual-control runners seed `env.reset` per episode as `10^4 * seed + episode`. The SARSOP, constrained-POMDP, TOST, and calibration-table runners (`run_sarsop_baseline.py`, `run_cpomdp_baseline.py`, `run_tost_sarsop.py`, and the observe-then-commit half of `run_calibration_table.py`) seed the stream once per outer seed and let it continue across that seed's episodes, except that `run_tost_sarsop.py --episode-seeding` seeds each episode as `10^4 * seed + episode`. The near-optimality horizon study derives its outer seed from the environment index and horizon. Deviations from the canonical seed set are stated per battery in the manuscript's reproducibility checklist |
| Provenance | the core-environment, Tileworld, Structural Inspection, transfer, IDS, scaling, discount, navigation, MCTS-EFE ablation, POMCP exploration (sweep and tuning), budget-frontier, Pareto, and nat-canonical CSVs carry `seed_list`, `episodes_per_seed`, `git_sha`, and `generated_utc` from `experiments/run_experiment.py:provenance_fields`. The RockSample instance CSVs carry the seed list and episodes per seed only. Offline-reference, statistics, and trace CSVs (SARSOP, CPOMDP, TOST, calibration, atlas, `*_stats.csv`, the dual-control traces) state their protocol in the manuscript captions and prose instead |

## Recorded-sensor study

The calibration and evaluation manifests at
`results/real_sensor_2026-10-01/calibration/complete.json` and
`results/real_sensor_2026-10-01/evaluation/complete.json` record macOS 27.0 on
arm64, Python 3.9.6, NumPy 2.0.2, SciPy 1.13.1 and scikit-learn 1.6.1. The package
versions match `requirements-lock.txt`. Both manifests record `OMP_NUM_THREADS`,
`OPENBLAS_NUM_THREADS`, `MKL_NUM_THREADS` and `VECLIB_MAXIMUM_THREADS` set to one. They also store timestamps, source hashes and
the Git revision for each stage. These platform records qualify the simulation
environment above rather than inheriting its OS version.

## Reproduction

To reproduce from scratch, install `requirements-lock.txt` into a Python 3.9
environment and follow the reproduction table in `README.md`. Per-seed metrics
are committed for the batteries listed in the README's reproduction section
(SARSOP TOST at n=5, n=20, and episode-matched n=20, budget frontier with its same-stream,
fresh-seed, and target-matched references, subsidized reference points, multi-seed dual
control, shadow-price staircase curves), whose tests can be recomputed without
rerunning an episode. The other batteries commit aggregates, seed-level SEs,
and computed tests (`*_stats.csv`), and their per-seed values are regenerable
exactly by rerunning the producer.
