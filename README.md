# Expected Free Energy as Belief-Dependent Utility for rho-POMDPs

Code accompanying the paper *Expected Free Energy as Belief-Dependent Utility for rho-POMDPs* by Patrick Cooper and Alvaro Velasquez (University of Colorado Boulder).

We bridge rho-POMDPs and active inference by substituting Expected Free Energy (EFE) as the belief-dependent utility rho. We prove this is equivalent to augmenting reward with information gain at a canonical weight w=1 derived from the variational bound, extend the equivalence to factored observation POMDPs (covering interleaved observe-act settings such as RockSample), and evaluate the canonical weight against tuned baselines across eleven environment instances up to |S| = 65,536.

## Repository Structure

```
rho_aif/                 Python package
  agents/                All agents (EFE, planning, info-gain, POMCP, MCTS-EFE, ...)
  environments/          Gymnasium environments (Tiger, Diagnosis, Bandit,
                         Tileworld, RockSample, Inspection, Navigation, ...)
  belief.py              Exact Bayesian belief-state machinery
  stats.py               Bootstrap CIs, Cohen's d, Holm-Bonferroni
  render_tileworld.py    Tileworld episode rendering utilities
experiments/             Scripts that reproduce every table and figure
results/                 CSV outputs backing the paper's tables
figures/                 PDF figures used by the paper
paper/                   LaTeX sources, style files, and submission archives
tests/                   Pytest suite (235 tests)
Guidance_Documents/      Research plan and project guidance
```

## Installation

Requires Python 3.9+.

```bash
git clone https://github.com/PatrickAllenCooper/rho_aif.git
cd rho_aif
python -m venv .venv
source .venv/bin/activate
pip install -e .            # library only
pip install -e ".[dev]"     # library + test/lint tooling
```

## Using the Package

All agents share the same exact Bayesian belief-update machinery and differ only in objective function and planning depth. An agent is constructed from a list of observation models (one `P(obs | state)` matrix per observation action) and an environment config with observation costs and a commit reward matrix.

```python
import numpy as np
from rho_aif.agents import EFEAgent
from rho_aif.environments import TigerEnv

env = TigerEnv()
agent = EFEAgent(
    observation_models=[np.array([[0.85, 0.15], [0.15, 0.85]])],
    env_config={
        "observation_costs": [1.0],
        "commit_reward_matrix": np.array([[-100.0, 10.0], [10.0, -100.0]]),
    },
    planning_horizon=4,
)

obs, info = env.reset()
agent.reset()
total_reward = 0.0
while True:
    action = agent.select_action()
    obs, reward, terminated, truncated, info = env.step(action)
    total_reward += reward
    if terminated:
        break
    agent.update_belief(obs, obs_action=action)

print(f"reward={total_reward:.1f}, correct={info['correct']}")
```

The helpers in `experiments/run_experiment.py` (`make_agent`, `run_episode`, `run_experiment`, `summarize_results`) wrap this loop for batch evaluation.

## Agents

| Agent | rho function | Horizon | Role |
|-------|-------------|---------|------|
| Myopic | rho = 0 | H=1 | Weakest baseline |
| Planning | rho = 0 | H>1 | Controls for planning depth |
| Info Gain | w * I(b) | H=1 | Epistemic bonus (myopic) |
| Planning+IG | w * I(b) | H>1 | IG + planning depth |
| **EFE** | **I_a(b) via EFE** | **H>1** | **Joint objective (Proposition 1)** |
| Epistemic-only | I_a(b) only | H>1 | Ablation: no pragmatic term |
| POMCP | -- | MCTS | Online solver baseline |
| MCTS-EFE | EFE leaf heuristic | MCTS | Scaling beyond exact search |

Environment-specific tree-search variants for RockSample and Structural Inspection live in `rho_aif/agents/rocksample_agents.py` and `rho_aif/agents/inspection_agents.py`.

## Reproducing the Paper

Run every script from the repository root. CSVs are written to `results/` and figures to `figures/`. Main experiments use 1,000 episodes per seed across 5 seeds; expect minutes to hours per script depending on the environment.

| Paper content | Command | Output |
|---------------|---------|--------|
| Core results (Tiger, Diagnosis, Bandit; Table 3) | `python experiments/run_experiment.py all` | `results/results_{tiger,summary,bandit,navigation}*.csv` |
| Diagnosis scaling (N=2..16) | `python experiments/run_experiment.py scaling` | `results/results_scaling.csv` |
| Pareto analysis / canonical w=1 (Fig. 1) | `python experiments/run_pareto.py` | `figures/fig_pareto.pdf` |
| Tileworld tables and figures (Sec. 5.3) | `python experiments/run_tileworld.py all` | `results/results_tileworld_*.csv`, `figures/fig_tileworld_*.pdf` |
| RockSample (Sec. 5.4) | `python experiments/run_rocksample.py` | `results/results_rocksample_*.csv` |
| Structural Inspection (Sec. 5.5) | `python experiments/run_inspection.py` | `results/results_inspection_*.csv` |
| Zero-shot weight transfer (Discussion) | `python experiments/run_transfer.py` | `results/results_transfer.csv` |
| Near-optimality Monte Carlo (Prop. 3, appendix) | `python experiments/run_nearopt_horizon.py` | `results/results_nearopt_horizon.csv`, `figures/fig_nearopt_horizon.pdf` |
| Discount sensitivity (appendix) | `python experiments/run_discount.py` | `results/results_discount.csv` |
| Model misspecification (appendix) | `python experiments/run_model_misspec.py` | `results/results_model_misspec.csv` |
| POMCP comparison (appendix) | `python experiments/run_pomcp.py` | `results/results_pomcp.csv` |
| MCTS-EFE experiments (appendix) | `python experiments/run_mcts_experiments.py` | `results/results_mcts_efe.csv` |
| Showcase figures (asymmetry sweep, EFE traces) | `python experiments/run_showcase.py` | `figures/fig_{asymmetry_sweep,efe_trajectory,obs_scaling}.pdf` |
| Long-horizon visualizations (appendix) | `python experiments/run_visualizations.py` | `figures/fig_{belief_heatmap,efficiency_curves,extended_efe,stopping_times}.pdf` |
| Supplementary statistics (appendix) | `python experiments/run_supplementary.py` | `results/results_{bootstrap_ci,effect_sizes,full_statistics}.csv` |
| Full batch with checkpointing | `python experiments/run_overnight.py` | all of the above |

The committed CSVs in `results/` are the exact runs behind the paper's tables, so you can compare your reproduction directly against them.

## Tests

```bash
python -m pytest tests/ -v
```

The suite covers belief updates, every agent and environment, statistical utilities, and end-to-end episodes.

## Paper

LaTeX sources live in `paper/`:

- `paper_arxiv.tex`: full non-anonymous version (LNCS format) with all appendices; `arxiv_submission.zip` is the corresponding arXiv upload package.
- `paper_iwai2026_abridged.tex`: 12-page IWAI 2026 submission.
- `paper_iwai2026.tex` / `paper.tex`: full anonymized LNCS and NeurIPS-format versions.

Compile from inside `paper/` (figures resolve from the repository root):

```bash
cd paper && tectonic paper_arxiv.tex
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

Released for academic use.
