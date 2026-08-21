# rho-aif: Information-Gathering Planning Benchmark

A Gymnasium benchmark suite and agent library for observe-then-commit and factored-observation POMDPs, accompanying the paper *Expected Free Energy as Belief-Dependent Utility for rho-POMDPs* by Patrick Cooper and Alvaro Velasquez (University of Colorado Boulder).

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
pip install -e ".[dev]"
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

Under log scoring, EFE at `w=1` is the theoretically correct belief reporter (Bernardo 1979). Scoring-rule columns are the benchmark differentiator alongside reward.

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

Run from the repository root after `pip install -e ".[dev]"`.

| Paper content | Command |
|---------------|---------|
| Core results (Tiger, Diagnosis, Bandit) | `python experiments/run_experiment.py all` |
| Tileworld | `python experiments/run_tileworld.py all` |
| Structural Inspection | `python experiments/run_inspection.py` |
| RockSample (regenerated single-source tables) | `python experiments/build_rocksample_tables.py` (reads `results/results_rocksample_*.csv`) |
| Pareto / transfer / POMCP / MCTS / ... | see `experiments/run_*.py` |
| Near-optimality across planning horizons | `python experiments/run_nearopt_horizon.py` then `python experiments/build_horizon_map.py` |
| Price-of-information: full battery (curves, collapse, Prop 2, dual control, cost budgets, interleaved) | `python experiments/run_price_of_information.py --mode full` |
| Price-of-information: one sub-battery | `python experiments/run_price_of_information.py --only {curves,interleaved,cost,scale,prop2,dual-multiseed,efe}` |
| SARSOP near-optimal baseline (requires `tools/build_sarsop.sh`) | `python experiments/run_sarsop_baseline.py` |
| w* atlas appendix table | `python experiments/run_w_atlas.py` |
| Distractor-robustness experiment (Stage G2) | `python experiments/run_distractor_diagnosis.py` |
| Proper-scoring calibration table | `python experiments/run_calibration_table.py` |
| Per-test value-of-information audit case study | `python experiments/run_audit_case_study.py` |
| Destructive-sensing boundary example | `python -m pytest tests/test_destructive_boundary.py -v` |
| Full-length integrated paper | `paper/full_paper.tex` (compile with `tectonic paper/full_paper.tex`) |

## Tests

```bash
python -m pytest tests/ -v
```

## Citation

```bibtex
@article{cooper2026efe,
  title={Expected Free Energy as Belief-Dependent Utility for $\rho$-{POMDP}s},
  author={Cooper, Patrick and Velasquez, Alvaro},
  year={2026}
}
```

## License

MIT. See [LICENSE](LICENSE).
