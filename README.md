# Expected Free Energy as Belief-Dependent Utility for rho-POMDPs

Code accompanying the paper *Expected Free Energy as Belief-Dependent Utility for rho-POMDPs*, submitted to NeurIPS 2025.

We bridge rho-POMDPs and active inference by substituting Expected Free Energy (EFE) as the belief-dependent utility rho. We prove this is equivalent to augmenting reward with information gain at a canonical weight w=1 derived from the variational bound, and evaluate this canonical choice against five baselines across five discrete POMDP environments.

---

## Repository Structure

```
rho_aif/
  paper.tex                        # Main paper (NeurIPS 2025 format)
  neurips_2025.sty                 # NeurIPS style file
  Guidance_Documents/              # Research plan and project guidance
  environments/
    info_seeking.py                # Two-state testbed (Gymnasium)
    tiger.py                      # Tiger problem (Gymnasium)
    diagnosis.py                  # Sequential diagnosis (Gymnasium)
    bandit.py                     # Structured bandit (Gymnasium)
    navigation.py                 # Grid navigation (Gymnasium)
  agents/
    base.py                       # BaseAgent with exact Bayesian belief updates
    myopic.py                     # Myopic baseline (rho = 0, H=1)
    planning.py                   # Planning baseline (rho = 0, H>1)
    info_gain.py                  # Information Gain (rho = w * I(b), H=1)
    planning_infogain.py          # Planning+IG (rho = w * I(b), H>1)
    vfe.py                        # VFE agent (rho = EFE, H>1)
    epistemic_only.py             # Epistemic-only ablation
    navigation_vfe.py             # Navigation-specific VFE variant
    navigation_baselines.py       # Navigation-specific baselines
    pymdp_agent.py                # pymdp wrapper for validation
  belief.py                       # BeliefState with Bayesian updates
  stats.py                        # Bootstrap CIs, Cohen's d, Holm-Bonferroni
  run_experiment.py                # Main experiment runner (all environments)
  run_pareto.py                    # Pareto analysis (weight sweep)
  run_showcase.py                  # Reward sweep, EFE trajectories, obs scaling
  run_visualizations.py            # Long-horizon visualization figures
  run_supplementary.py             # Supplementary statistics tables
  figures/                         # Generated PDF figures for the paper
  tests/                           # Pytest suite (130 tests)
```

---

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run experiments

```bash
python run_experiment.py info       # Two-state testbed
python run_experiment.py tiger      # Tiger problem
python run_experiment.py diagnosis  # Sequential diagnosis
python run_experiment.py bandit     # Structured bandit
python run_experiment.py navigation # Grid navigation
python run_experiment.py scaling    # Diagnosis scaling analysis (N=2..16)
python run_experiment.py all        # All of the above
```

### Generate figures

```bash
python run_showcase.py              # Asymmetry sweep, EFE trajectories, obs scaling
python run_pareto.py                # Pareto analysis (weight sweep)
python run_visualizations.py        # Belief heatmap, efficiency curves, extended EFE, stopping times
```

### Run tests

```bash
python -m pytest tests/ -v
```

---

## Agents

All agents share the same exact Bayesian belief-update machinery and differ only in their objective function and planning depth.

| Agent | rho function | Horizon | Role |
|-------|-------------|---------|------|
| Myopic | rho = 0 | H=1 | Weakest baseline |
| Planning | rho = 0 | H>1 | Controls for planning depth |
| Info Gain | w * I(b) | H=1 | Epistemic bonus (myopic) |
| Planning+IG | w * I(b) | H>1 | IG + planning depth |
| **VFE** | **I_a(b) via EFE** | **H>1** | **Joint objective (Proposition 1)** |
| Epistemic-only | I_a(b) only | H>1 | Ablation: no pragmatic term |

---

## Environments

All environments follow an observe-then-commit structure implemented as OpenAI Gymnasium environments.

| Environment | States | Obs. Actions | Commit Actions | Key Feature |
|-------------|--------|-------------|----------------|-------------|
| Tiger | 2 | 1 (listen) | 2 | Extreme reward asymmetry (+10/-100) |
| Testbed | 2 | 1 | 2 | Mild penalty (+1/-1) |
| Diagnosis | N | K tests | N | Multi-test selection |
| Bandit | K | K inspections | K | Multi-arm inspection |
| Navigation | 9 | 4 (move) | implicit | Spatial information gathering |

---

## Key Results

- **EFE = canonical w=1**: VFE is equivalent to Planning+IG with w=1 (Proposition 1), confirmed empirically on all environments.
- **w=1 is near-Pareto-optimal**: Sits at the success-reward knee without per-environment search.
- **Multi-observation-action advantage**: VFE significantly outperforms reward-only planning on Diagnosis (+9.4 pp) and Bandit (+15.5 pp) where the agent must choose which information to gather.
- **Pragmatic term is essential**: Epistemic-only ablation collapses on all environments.

---

## Citation

If you use this code, please cite:

```bibtex
@inproceedings{anonymous2025efe,
  title={Expected Free Energy as Belief-Dependent Utility for $\rho$-{POMDP}s},
  author={Anonymous},
  booktitle={Advances in Neural Information Processing Systems},
  year={2025}
}
```

---

## License

This project is released for academic use. See the paper for full details.
