# ρ-POMDP Active Inference Framework

Research exploring whether **variational free energy** (VFE) as a belief-state utility function in ρ-POMDPs produces superior epistemic foraging behavior compared to standard reward-maximizing and information gain approaches.

**Collaboration**: Patrick Cooper (Implementation) & David Baines (Theory)

---

## Research Question

Does VFE as ρ produce measurably different and superior epistemic foraging behavior in partially observable environments requiring active information gathering?

**Evaluation Metrics**: Policy quality, sample efficiency, belief convergence rate

---

## Current Status - Minimal Testbed Complete

### Experiment: Two-State Observation Problem (1,000 episodes each)

**Environment**: 2 hidden states, noisy observations (75% accuracy), observe costs 0.1

**Agents Tested**:
1. Myopic (one-step lookahead baseline)
2. Information Gain (ρ = entropy reduction)
3. VFE (ρ = epistemic_weight × entropy reduction)

### Results

| Agent | Observations | Success Rate | Mean Reward |
|-------|--------------|--------------|-------------|
| Myopic | 1.00 | 75.4% | +0.408 |
| **Info Gain** | **3.17** | **89.8%** | **+0.479** |
| VFE | 1.00 | 76.0% | +0.420 |

**Key Finding**: Information Gain agent significantly outperforms baseline (p < 0.001)
- 217% more exploration
- 19% higher success rate  
- 17% higher reward

**VFE Status**: Currently identical to Myopic (epistemic weight too low, needs tuning)

---

## Next Steps

1. VFE parameter sweep (epistemic_weight: 0.5 → 2.0)
2. Tiger problem implementation
3. Scale to extended POMDP benchmarks

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run minimal testbed experiment
python run_experiment.py
```

---

## Project Structure

```
rho_aif/
├── README.md                           # This file
├── Guidance_Documents/                 # Detailed research plan
├── minimal_epistemic_foraging.ipynb    # Notebook implementation
├── run_experiment.py                   # Production experiment script
├── debug_vfe.py                        # Agent debugging tools
└── requirements.txt                    # Dependencies
```

---

## Theoretical Background

**ρ-POMDPs**: Extend POMDPs with belief-state utility function (ρ) enabling explicit optimization over uncertainty reduction

**Active Inference**: Frames perception and action as unified processes minimizing variational free energy, leading naturally to epistemic foraging

**Epistemic Foraging**: Strategic information-gathering to reduce environmental uncertainty

---

## References

- Araya, M., et al. (2010). A POMDP extension with belief-dependent rewards. *NIPS*
- Friston, K. (2010). The free-energy principle: a unified brain theory? *Nature Reviews Neuroscience*
- Parr, T., & Friston, K. J. (2019). Generalised free energy and active inference. *Biological Cybernetics*

---

**Next Meeting**: Thursday, February 13, 2026 at 11:30 AM
