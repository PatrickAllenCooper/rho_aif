# ρ-POMDP Active Inference Framework

A research implementation exploring the intersection of active inference and ρ-POMDPs (rho-Partially Observable Markov Decision Processes) for epistemic foraging in partially observable environments.

## Research Overview

This project investigates whether **variational free energy** (VFE), when used as the generalized utility function in ρ-POMDPs, produces superior epistemic foraging behavior compared to standard reward-maximizing POMDP policies and alternative belief-state utility functions.

### Core Research Question

**Does variational free energy as ρ produce measurably different and superior epistemic foraging behavior in partially observable environments requiring active information gathering?**

We evaluate this across three key metrics:
- Policy quality
- Sample efficiency  
- Belief convergence rate

## Theoretical Background

### ρ-POMDPs (Rho-POMDPs)

Rho-POMDPs extend traditional POMDPs by incorporating a **belief-state utility function** (ρ) that allows agents to value belief states themselves, not just states of the world. This enables explicit optimization over uncertainty reduction and information-seeking behavior.

### Active Inference

Active inference frames perception and action as unified processes of minimizing variational free energy. Agents don't just infer the state of the world—they actively sample observations to reduce uncertainty about their environment, leading naturally to epistemic foraging (information-seeking) behavior.

### Epistemic Foraging

The strategic exploration and information-gathering behavior exhibited by agents seeking to reduce uncertainty about their environment. This project examines whether VFE provides a principled measure for guiding such behavior in partially observable settings.

## Experimental Design

### Phase 1: Tiger Problem Baseline

We begin with a **controlled comparison** using the classic Tiger problem variant, which provides a minimal testbed for isolating epistemic foraging behavior.

#### Three Agent Conditions

1. **Standard POMDP Agent**
   - Reward-maximizing policy
   - No explicit belief-state utility
   - Baseline for comparison

2. **ρ-POMDP Agent with Information Gain**
   - Uses information gain as belief-state utility (ρ)
   - Explicitly values uncertainty reduction
   - Comparison to standard information-theoretic approaches

3. **ρ-POMDP Agent with Variational Free Energy**
   - Uses VFE as belief-state utility (ρ)
   - Active inference approach
   - **Primary experimental condition**

#### Evaluation Metrics

- **Belief convergence speed**: How quickly agents arrive at correct beliefs about hidden states
- **Information-seeking efficiency**: Quality of observation actions chosen
- **Task performance**: Ultimate reward obtained
- **Sample efficiency**: Learning speed and data requirements

### Phase 2: Extended POMDP Benchmarks

Following successful Tiger problem validation, we will scale to more complex partially observable environments including:
- Multi-armed bandit variants with hidden structure
- Partially observable navigation tasks
- Sequential decision problems with layered uncertainty

## Project Structure

```
rho_aif/
├── README.md                    # This file
├── Guidance_Documents/          # Research plan and design documentation
├── src/                         # Core implementation
│   ├── agents/                  # Agent implementations
│   │   ├── standard_pomdp.py
│   │   ├── rho_pomdp_ig.py     # Information gain ρ
│   │   └── rho_pomdp_vfe.py    # VFE ρ
│   ├── environments/            # Problem environments
│   │   ├── tiger.py
│   │   └── ...
│   ├── inference/               # Belief updating and inference
│   ├── planning/                # Policy optimization
│   └── utils/                   # Shared utilities
├── experiments/                 # Experimental scripts and configurations
├── tests/                       # Unit and integration tests
├── notebooks/                   # Analysis and visualization notebooks
└── results/                     # Experimental outputs
```

## Research Collaboration

This project is a collaboration between:
- **Patrick Cooper** - Implementation and experimental design
- **David Baines** - POMDP and ρ-POMDP model development, theoretical framework

## Implementation Roadmap

### Immediate Priorities

1. Implement Tiger problem environment
2. Develop standard POMDP baseline agent
3. Create ρ-POMDP framework with pluggable utility functions
4. Implement information gain and VFE utility functions
5. Design comprehensive evaluation suite

### Future Extensions

- Additional POMDP benchmark problems
- Scalability analysis for larger state/observation spaces
- Theoretical analysis of convergence properties
- Comparative analysis with other belief-space planning approaches

## Getting Started

```bash
# Clone repository
git clone git@github.com:PatrickAllenCooper/rho_aif.git
cd rho_aif

# Install dependencies
pip install -r requirements.txt

# Run Tiger problem baseline
python experiments/tiger_baseline.py

# Run comparative analysis
python experiments/compare_agents.py
```

## References

### Active Inference
- Friston, K. (2010). The free-energy principle: a unified brain theory? *Nature Reviews Neuroscience*
- Parr, T., & Friston, K. J. (2019). Generalised free energy and active inference. *Biological Cybernetics*

### ρ-POMDPs
- Araya, M., et al. (2010). A POMDP extension with belief-dependent rewards. *NIPS*

### Epistemic Foraging
- Friston, K., et al. (2015). Active inference and epistemic value. *Cognitive Neuroscience*

## License

[To be determined]

## Contact

For questions or collaboration inquiries, contact Patrick Cooper.
