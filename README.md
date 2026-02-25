# rho-POMDP Active Inference Framework

Research exploring whether **variational free energy** (VFE) as a belief-state utility function in rho-POMDPs produces superior epistemic foraging behavior compared to standard reward-maximizing and information gain approaches.

**Collaboration**: Patrick Cooper (Implementation) & David Baines (Theory)

---

## Research Questions

- **RQ1**: Does VFE serve as an effective generalized utility function (rho) for rho-POMDPs?
- **RQ2**: Do AIF-informed rho-POMDPs produce superior epistemic foraging?
- **RQ3**: What does the choice of rho reveal about agent constitution and epistemic behavior?

**Evaluation Metrics**: Policy quality, sample efficiency, belief convergence rate

---

## Results

### Two-State Information-Seeking Testbed (1,000 episodes)

| Agent | Observations | Success Rate | Mean Reward |
|-------|-------------|--------------|-------------|
| Myopic | 1.00 | 74.6% | +0.392 |
| **Info Gain** | **3.24** | **91.8%** | **+0.512** |
| VFE | 5.51 | 96.4% | +0.377 |

### Tiger Problem (1,000 episodes)

| Agent | Listens | Success Rate | Mean Reward |
|-------|---------|--------------|-------------|
| Myopic | 1.00 | 86.5% | -5.850 |
| Info Gain | 1.00 | 83.5% | -9.150 |
| **VFE** | **4.31** | **99.1%** | **+4.700** |

### Key Findings

**Info-seeking testbed**: Info Gain agent achieves the best reward by balancing exploration cost against information value. VFE agent achieves the highest success rate (96.4%) but the additional observation costs reduce net reward.

**Tiger problem**: VFE agent is the **only agent with positive mean reward**. The extreme reward asymmetry (+10 vs -100) makes information gathering critical. Myopic and Info Gain agents both listen only once and suffer catastrophic losses. VFE's multi-step EFE planning naturally drives sufficient exploration (4.31 listens) without hand-tuned weights.

**Cross-environment robustness**: The VFE agent works across both environments without parameter tuning. The Info Gain agent requires its weight to be tuned per-environment (weight=1.0 is insufficient for Tiger's reward scale).

---

## Architecture

```
rho_aif/
  paper.tex                      # Paper: VFE as rho in rho-POMDPs
  Guidance_Documents/             # Research plan and guidance
  environments/
    info_seeking.py              # Two-state testbed (Gymnasium)
    tiger.py                     # Tiger problem (Gymnasium)
  agents/
    base.py                      # BaseAgent with belief management
    myopic.py                    # Myopic baseline (rho = 0)
    info_gain.py                 # Info Gain (rho = entropy reduction)
    vfe.py                       # VFE (rho = Expected Free Energy)
  belief.py                      # BeliefState with Bayesian updates
  run_experiment.py              # Experiment runner
  tests/                         # Pytest suite (69 tests)
```

---

## Quick Start

```bash
pip install -r requirements.txt
python run_experiment.py          # Info-seeking testbed
python run_experiment.py tiger    # Tiger problem
python run_experiment.py all      # Both experiments
python -m pytest tests/ -v        # Run test suite
```

---

## Agents

**Myopic** (baseline): One-step lookahead maximizing expected reward. No belief utility.

**Information Gain**: rho-POMDP with rho = weighted entropy reduction. One-step lookahead with tunable `info_gain_weight` parameter.

**VFE**: Minimizes Expected Free Energy with recursive multi-step planning. No tunable weights. EFE decomposes into pragmatic value (goal alignment via log-preferences) and epistemic value (intrinsic information gain). Exploration-exploitation balance emerges from the objective.

---

## References

- Araya, M., et al. (2010). A POMDP extension with belief-dependent rewards. *NIPS*
- Da Costa, L., et al. (2020). Active inference on discrete state-spaces. *J. Math. Psych.*
- Friston, K. (2010). The free-energy principle. *Nature Reviews Neuroscience*
- Kaelbling, L. P., et al. (1998). Planning and acting in partially observable stochastic domains. *AI*
- Parr, T., & Friston, K. J. (2019). Generalised free energy and active inference. *Biol. Cybernetics*
