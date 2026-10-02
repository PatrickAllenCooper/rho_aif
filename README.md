# rho-aif: Information-Gathering Planning Benchmark

[![Tests](https://github.com/PatrickAllenCooper/rho_aif/actions/workflows/tests.yml/badge.svg)](https://github.com/PatrickAllenCooper/rho_aif/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](pyproject.toml)

A Gymnasium benchmark suite and agent library for observe-then-commit and factored-observation POMDPs, accompanying the paper *Pricing the Sensing Budget in ρ-POMDPs, with Expected Free Energy as the Canonical Information Weight* by Patrick Cooper and Alvaro Velasquez (University of Colorado Boulder).

An abridged version was accepted at IWAI 2026 (poster and spotlight, Springer CCIS). The full manuscript in `paper/` is the extended version prepared for JAIR submission. See [CHANGELOG.md](CHANGELOG.md) for what changed between releases.

The package provides:

- Canonical environments (Tiger, Diagnosis, Bandit, Tileworld, Structural Inspection)
- Reference agents (EFE, Planning, Planning+IG, Myopic, Thompson, POMCP, MCTS-EFE, IDS, ...)
- Proper scoring rules on terminal beliefs (log score, Brier score)
- A CLI (`rho-aif-bench`) that runs the paper's evaluation protocol

## Install

Requires Python 3.9+.

PyPI publication is planned but not yet live, so `pip install rho-aif` does not work yet. Install from a clone instead:

```bash
git clone https://github.com/PatrickAllenCooper/rho_aif.git
cd rho_aif
python -m venv .venv && source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Quickstart

```bash
# List benchmark environments
rho-aif-bench list

# Run EFE on Tiger (canonical protocol; use fewer seeds/episodes for a smoke test)
rho-aif-bench run --env Tiger --agent efe --n-seeds 1 --episodes 50
```

Or from Python:

```python
from rho_aif import run_benchmark, list_benchmarks

print(list_benchmarks())
summary = run_benchmark("Tiger", agent_name="efe", episodes=50, seeds=[42])
print(summary["mean_reward"], summary["mean_log_score"], summary["mean_brier"])
```

## Benchmark Environments

| Name | Family | \|S\| | Role |
|------|--------|------|------|
| Tiger | observe-then-commit | 2 | Classic listen-or-open |
| Diagnosis | observe-then-commit | 4 | Multi-test diagnosis |
| Bandit | observe-then-commit | 4 | Inspect-then-pull |
| Tileworld-6x6 | observe-then-commit | 36 | Spatial scan-then-collect |
| Inspection-N8 | inspection | 256 | Structural fault detection |
| Inspection-N16 | inspection | 65,536 | Large-scale inspection |

Canonical seeds are `{42, 123, 456, 789, 1024}`. Episode counts and planning horizons follow the paper protocol (see `rho_aif.benchmark.BENCHMARKS`).

## Metrics

| Metric | Meaning | Better |
|--------|---------|--------|
| `mean_reward` | Expected cumulative reward | higher |
| `success_rate` / `accuracy` | Correct commit / diagnoses | higher |
| `mean_log_score` | Log score of terminal posterior vs true state (nats) | higher |
| `mean_brier` | Brier score of terminal posterior | lower |

Log and Brier scores evaluate terminal-belief quality separately from cumulative reward. The log score uses natural logarithms and, by default, floors probabilities at `1e-12` for finite numerical output.

## Agents

| Agent | CLI name | Role |
|-------|----------|------|
| Myopic | `myopic` | H=1, no epistemic bonus |
| Planning | `planning` | Reward-only tree search |
| Info Gain | `infogain` | Myopic IG bonus |
| Planning+IG | `planning+ig` | Tunable IG + depth |
| EFE | `efe` | Information-unit weight w=1 |
| Thompson | `thompson` | Posterior sampling |
| Greedy | `greedy` | Inspection: diagnose without testing |
| POMCP / MCTS-EFE / IDS | (Python API) | Online / adaptive baselines |

## Adding Your Own Agent

For observe-then-commit environments, implement `select_action`, `update_belief`, and `reset` against the shared `BeliefState`, then evaluate with `run_otc_episode` / `summarize_otc` from `rho_aif.benchmark`. For Structural Inspection, track a factored fault belief (see `InspectionBeliefState`) and use `run_inspection_episode`.

```python
from rho_aif.benchmark import get_benchmark, make_otc_agent, run_otc_episode

cfg = get_benchmark("Diagnosis")
env = cfg.env_factory()
agent = make_otc_agent("efe", env, cfg.planning_horizon)
result = run_otc_episode(agent, env)
print(result["log_score"], result["brier_score"], result["total_reward"])
```

## Baseline Results (committed paper runs)

Headline numbers from committed CSVs in `results/` (5 seeds; full protocol). Log/Brier columns are produced by the current package; regenerate with `rho-aif-bench` to obtain them. This table is generated from the CSVs by `experiments/build_readme_table.py`; run `python experiments/build_readme_table.py --check` to verify it against the current results before trusting it.

| Env | Agent | Reward | Success / Acc |
|-----|-------|--------|---------------|
| Tiger | EFE | +5.19 | 99.4% |
| Tiger | Planning | +5.19 | 99.4% |
| Bandit | EFE | +6.27 | 86.9% |
| Bandit | Planning | +5.75 | 71.0% |
| Tileworld 6x6 | EFE | -21.53 | 72.0% |
| Inspection-N8 | EFE w=1 | -20.95 | 91.1% |
| Inspection-N8 | Planning | -17.85 | 73.0% |
| Inspection-N8 | Plan+IG w=5 | -27.98 | 96.3% |

## Repository Layout

```
rho_aif/                 Installable package (agents, envs, scoring, benchmark, CLI)
experiments/             Scripts that reproduce every paper table and figure
results/                 Committed CSV outputs behind the paper tables
figures/                 PDF figures
paper/                   LaTeX sources
tests/                   Pytest suite
Guidance_Documents/      Research plan and project guidance
```

## Reproducing the Paper

The execution environment of record (machine, OS, Python, and the exact package versions that produced every committed result) is documented in `ENVIRONMENT.md`, with the pinned versions in `requirements-lock.txt`. Per-seed metrics are committed for the SARSOP TOST comparison at n=5 and at n=20 (`results_tost_sarsop_per_seed.csv`, `results_tost_sarsop_n20_robustness_per_seed.csv`), the budget-frontier study and its same-stream reference (`results_budget_frontier.csv`, `results_budget_frontier_curve.csv`, `results_cpomdp_frontier_heldout.csv`), the multi-seed dual-control study (`results_price_dual_multiseed.csv`, `results_price_dual_multiseed_metrics.csv`), and the shadow-price staircase curves (`results_price_usage_curves_per_seed.csv`), so the tests on those batteries can be recomputed from the CSVs without rerunning an episode. The other batteries commit per-agent means with seed-level SEs and the computed tests (`*_stats.csv`), from which a Welch statistic can be reconstructed but its inputs not re-derived. Their per-seed values are regenerable exactly by rerunning the producer, since every environment stream is seed-controlled. The main tuned baselines select their weight on one tuning stream, `TUNING_SEED = 7` in `experiments/run_experiment.py`, disjoint from the five evaluation seeds.

Run from the repository root after `pip install -e ".[dev]"`.

| Paper content | Command |
|---------------|---------|
| Core results (Tiger, Diagnosis, Bandit) | `python experiments/run_experiment.py all` |
| Tileworld | `python experiments/run_tileworld.py all` |
| Structural Inspection | `python experiments/run_inspection.py` |
| RockSample battery (four instances plus the RS[11,11] depth-3 check) | `python experiments/run_rocksample.py` (writes `results/results_rocksample_*.csv` and `_stats.csv`). `python experiments/run_rocksample.py --refresh-stats FILE...` recomputes the within-metric Holm columns of committed stats files without running episodes |
| RockSample (regenerated single-source tables) | `python experiments/build_rocksample_tables.py` (reads `results/results_rocksample_*.csv`) |
| POMCP comparison and simulation-budget scaling (POMCP Baseline Comparison appendix, Table `tab:pomcp`) | `python experiments/run_pomcp.py` |
| MCTS-EFE battery with its POMCP reference rows (POMCP Baseline Comparison appendix) | `python experiments/run_mcts_experiments.py` |
| Pareto / transfer / ... | see `experiments/run_*.py` |
| Near-optimality across planning horizons | `python experiments/run_nearopt_horizon.py` then `python experiments/build_horizon_map.py` |
| Price-of-information: full battery (curves, collapse, Prop 2, dual control, cost budgets, interleaved) | `python experiments/run_price_of_information.py --mode full` |
| Price-of-information: one sub-battery | `python experiments/run_price_of_information.py --only {curves,interleaved,cost,scale,prop2,dual-multiseed,efe}` |
| SARSOP near-optimal baseline (requires `tools/build_sarsop.sh`) | `python experiments/run_sarsop_baseline.py` |
| Constrained-POMDP reference at the endogenous budget (Lagrangian SARSOP sweep, requires `tools/build_sarsop.sh`), or recompute the feasible-envelope reference from the saved frontier with no episodes | `python experiments/run_cpomdp_baseline.py` or `python experiments/run_cpomdp_baseline.py --recompute-reference` |
| w* atlas appendix table | `python experiments/run_w_atlas.py` |
| Distractor-robustness experiment (Stage G2) | `python experiments/run_distractor_diagnosis.py` |
| Supplementary battery (Testbed appendix table, bootstrap CIs, effect sizes, full pairwise stats) | `python experiments/run_supplementary.py` |
| Pareto sweep + reward-maximizing weight brackets | `python experiments/run_pareto.py pareto` |
| Nat-canonical weight check, w=ln(2) vs. w=1 under the Pareto sweep protocol on all five swept environments (Section 3.3, reward-to-nats calibration paragraph) | `python experiments/run_nat_canonical_check.py` |
| Bandit w=100 depth comparison (Discussion) | `python experiments/run_bandit_w100_depth_comparison.py` |
| MCTS-EFE component ablation (Discussion, POMCP Baseline Comparison appendix) | `python experiments/run_mcts_efe_ablation.py` then `python experiments/build_mcts_ablation_tables.py` |
| POMCP exploration-constant sweep and informed rollouts (Discussion, POMCP Baseline Comparison appendix) | `python experiments/run_pomcp_exploration_sweep.py` then `python experiments/build_mcts_ablation_tables.py`. To parallelize, run each environment with `--envs X --out part_X.csv` and combine with `--merge part_*.csv`, which recomputes Holm over the whole battery (add `--tuning` to both steps for the tuning study) |
| POMCP exploration-constant selection on disjoint tuning seeds {11, 22, 33}, then the frozen comparison on the canonical seeds (Discussion, POMCP Baseline Comparison appendix) | `python experiments/run_pomcp_exploration_sweep.py --tuning --episodes 100` then `python experiments/select_pomcp_constants.py` |
| Budget-frontier study at calibration-derived target budgets (a predeclared rule on each calibration curve's range and largest jump), calibrated on the canonical seeds and evaluated on held-out seeds {7, 8, 9, 10, 11} (Section 6.9, Table `tab:budget_frontier`) | `python experiments/run_budget_frontier.py`, then `python experiments/run_frontier_reference_heldout.py` (same-stream reference and paired gaps, the Same-stream reference and Paired gap columns), then `python experiments/run_frontier_target_reference.py` (the Target reference and Target gap columns), then `python experiments/build_budget_frontier_table.py` |
| Predeclared fresh-seed replication of the frontier gaps on seeds 12 to 21, nothing refit (Appendix, frontier details) | `python experiments/run_frontier_fresh_seed_replication.py` (`--lineage` first replays the held-out seeds and aborts unless every gap matches) |
| Target-matched frontier reference: subsidized SARSOP policies and the best sampled mixture meeting each target, on held-out and fresh seeds (Appendix, frontier details) | `python experiments/run_frontier_target_reference.py` after the frontier and same-stream reference runs (`--usage-matched` then recomputes the post hoc realized-usage sensitivity from the committed archives, no episodes) |
| Seed-bootstrap stability of the staircase crossing brackets, with per-seed usage curves archived (Section 6.6) | `python experiments/run_bracket_stability.py` |
| SARSOP TOST equivalence, unpaired and paired, with per-seed means archived | `python experiments/run_tost_sarsop.py` |
| SARSOP TOST robustness at n=20 seeds (canonical five plus 2000 to 2014), with per-seed means archived | `python experiments/run_tost_sarsop.py --seeds 42 123 456 789 1024 $(seq 2000 2014) --episodes 500 --out results/results_tost_sarsop_n20_robustness.csv` |
| SARSOP TOST on episode-matched streams, same twenty seeds | `python experiments/run_tost_sarsop.py --episode-seeding --seeds 42 123 456 789 1024 $(seq 2000 2014) --episodes 500 --out results/results_tost_sarsop_episode_paired.csv` |
| Figure 1 (schematic hero figure, no data; one file per master because the equivalence proposition is numbered differently in each) | `python experiments/build_fig_hero.py` (writes both files) |
| Explanatory diagrams (observe-or-commit loop, state preservation, target versus cap, projected feedback) | `python experiments/build_fig_concepts.py` (schematics, no simulations) |
| EFE on the RockSample POMCP diagnostic protocol (Appendix N) | `python experiments/run_rocksample_efe_diagnostic.py` |
| Compute-matched POMCP check | `python experiments/run_pomcp_compute_matched.py` |
| RockSample POMCP: configuration selection on tuning seeds | `python experiments/run_rocksample_pomcp.py tuning` |
| RockSample POMCP: simulation-budget sweep | `python experiments/run_rocksample_pomcp.py budget` (reads the frozen config from the tuning CSV) |
| RockSample POMCP: rollout, discount, belief-mode sensitivity | `python experiments/run_rocksample_pomcp.py sensitivity` |
| Proper-scoring calibration table | `python experiments/run_calibration_table.py` |
| Per-test value-of-information audit case study | `python experiments/run_audit_case_study.py` |
| Destructive-sensing boundary example | `python -m pytest tests/test_destructive_boundary.py -v` |
| Full-length integrated paper | `paper/full_paper.tex` (see the build commands below) |

## Tests

```bash
python -m pytest tests/ -v
```

## Citation

```bibtex
@article{cooper2026efe,
  title={Pricing the Sensing Budget in $\rho$-{POMDP}s, with Expected Free Energy as the Canonical Information Weight},
  author={Cooper, Patrick and Velasquez, Alvaro},
  year={2026}
}
```

## Building the manuscripts

Run from the repository root with pdfLaTeX and Biber available on `PATH` for the JAIR manuscript, and Tectonic for the long LNCS master. Each build uses the shared figures and tables in this checkout; it does not rerun experiments.

```bash
cd paper
pdflatex -interaction=nonstopmode -halt-on-error full_paper_jair.tex
biber full_paper_jair
pdflatex -interaction=nonstopmode -halt-on-error full_paper_jair.tex
pdflatex -interaction=nonstopmode -halt-on-error full_paper_jair.tex
tectonic full_paper.tex
```

The review PDFs are `paper/full_paper_jair.pdf` and `paper/full_paper.pdf`. The final reviewed PDFs are versioned alongside the source, figures, tables, and bibliography. Rebuild them after manuscript changes before delivering a new review version.

The [Overleaf source archive](paper/rho_aif_jair_overleaf_2026-09-28.zip) contains the JAIR manuscript and all project dependencies. Upload it as a new project, select `full_paper_jair.tex` as the main document, and use pdfLaTeX with Biber on a current TeX Live version. Its README includes the build instructions. A fresh local extraction was compiled independently; no hosted Overleaf test or journal submission was performed.

After changing the manuscript or its figures, regenerate that archive with `python tools/build_overleaf_package.py`. The script discovers referenced figures and table inputs from the current source so additions are included automatically.

## Public sensor records with learned likelihoods

The predeclared UCI Gas Sensor Drift extension uses actual recorded observations, training-only categorical likelihoods, fixed researcher targets of 2/4/8 sensor accesses, matched direct-penalty and fixed-count controls, and a frozen chronological transfer test. It retains failures: the sampled weight grid cannot reach 2 accesses, the 4/8 targets transfer within the represented period but lose classification accuracy to both direct controls, and later batches overspend. This is retrospective access to records, not deployment or energy validation.

[Protocol](experiments/protocols/gas_sensor_2026-10-01.md), [reproduction instructions and archive schema](results/real_sensor_2026-10-01/README.md), [all selected-policy summaries](results/results_real_sensor_summary.csv), and [independent reconstruction audit](reviews/extension_2026-10-01/independent_evidence_audit.json). Install the optional experiment dependency with `python -m pip install -e '.[sensor-study]'`. All stages use CPUs.

## License

Repository code and simulation outputs are MIT licensed. See [LICENSE](LICENSE). The external sensor dataset is obtained from UCI under its source terms, as described in the [study README](results/real_sensor_2026-10-01/README.md).
