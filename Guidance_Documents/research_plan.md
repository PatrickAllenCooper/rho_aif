# Research Plan and Guidance Document

## Project: ρ-POMDP Active Inference Framework

**Last Updated**: February 9, 2026  
**Project Lead**: Patrick Cooper  
**Collaborator**: David Baines

---

## Research Objective

Examine whether **variational free energy**, used as the generalized utility function in ρ-POMDPs, produces superior epistemic foraging behavior compared to standard reward-maximizing POMDP policies and alternative belief-state utility functions.

### Hypothesis

VFE-as-ρ will produce:
1. Faster belief convergence rates
2. More targeted information-seeking actions
3. Superior sample efficiency in partially observable environments

---

## Experimental Prompt

**Primary Research Question:**

"We examine whether variational free energy, used as the generalized utility function in ρ-POMDPs, produces superior epistemic foraging behavior compared to standard reward-maximizing POMDP policies and alternative belief-state utility functions, measured by policy quality, sample efficiency, and belief convergence rate in partially observable environments requiring active information gathering."

---

## Phase 1: Tiger Problem Baseline

### Rationale

The Tiger problem provides a minimal, well-understood testbed that isolates epistemic foraging behavior. Its simplicity allows us to:
- Verify correct implementation of all three agent types
- Establish clear baselines for comparison
- Analyze belief dynamics in detail
- Validate metrics before scaling complexity

### Agent Implementations

#### 1. Standard Reward-Maximizing POMDP Agent
- **Objective**: Maximize expected cumulative reward
- **Planning**: POMDP value iteration or point-based methods
- **No explicit belief utility**: Actions chosen purely for state-reward optimization
- **Role**: Baseline for comparison

#### 2. ρ-POMDP Agent with Information Gain
- **Objective**: Maximize reward + information gain over beliefs
- **Utility Function (ρ)**: Information gain (KL divergence or entropy reduction)
- **Planning**: Belief-space planning with information-theoretic utility
- **Role**: Standard epistemic foraging approach for comparison

#### 3. ρ-POMDP Agent with Variational Free Energy
- **Objective**: Minimize variational free energy as ρ
- **Utility Function (ρ)**: VFE = Expected energy - Entropy of beliefs
- **Planning**: Active inference policy selection
- **Role**: Primary experimental condition

### Evaluation Metrics

#### Primary Metrics
1. **Belief Convergence Rate**
   - Time steps to reach belief confidence threshold
   - KL divergence from true posterior over time
   - Belief entropy reduction curve

2. **Sample Efficiency**
   - Number of observations required to achieve task competence
   - Learning curve steepness
   - Variance in performance across trials

3. **Policy Quality**
   - Expected cumulative reward
   - Success rate on task
   - Optimal action selection frequency

#### Secondary Metrics
- Computational efficiency (planning time per action)
- Robustness to prior misspecification
- Exploration vs. exploitation balance

### Implementation Components

#### Environment and Infrastructure
- Implement Tiger problem environment
- Create evaluation framework
- Establish metrics logging and visualization

#### Standard POMDP Baseline
- Implement standard POMDP solver
- Validate against known Tiger problem solutions
- Establish performance baseline

#### ρ-POMDP Framework
- Create modular ρ-POMDP architecture
- Implement pluggable utility function interface
- Develop belief-space planning algorithms

#### Information Gain Agent
- Implement information gain utility
- Run comparative experiments
- Analyze belief dynamics

#### VFE Agent
- Implement variational free energy utility
- Integrate active inference planning
- Full comparative analysis

#### Analysis and Iteration
- Statistical analysis of results
- Refinement based on findings
- Documentation and visualization

---

## Phase 2: Extended Benchmarks

Upon successful Phase 1 completion, we will extend to:

### Additional POMDP Environments

1. **Multi-Armed Bandit with Hidden Structure**
   - Arms have latent properties to discover
   - Tests epistemic exploration strategies

2. **Partially Observable Navigation**
   - Grid-world with limited visibility
   - Hidden goal locations or obstacles
   - Tests spatial information gathering

3. **Sequential Diagnosis Problem**
   - Medical diagnosis or fault detection scenario
   - Layered uncertainty requiring strategic questioning
   - Tests long-horizon epistemic planning

### Scaling Analysis
- Larger state spaces
- More complex observation models
- Hierarchical belief structures

---

## Theoretical Contributions

### Expected Insights

1. **Empirical Validation**: Direct comparison of VFE vs. information gain in belief-space optimization
2. **Epistemic Foraging Characterization**: Quantitative analysis of information-seeking behavior patterns
3. **Convergence Properties**: Understanding belief convergence dynamics under different utility functions
4. **Practical Guidance**: When and why VFE-based approaches outperform alternatives

### Potential Publications

- Conference paper on Tiger problem results (e.g., UAI, AISTATS)
- Extended journal paper with full benchmark suite (e.g., JMLR, Neural Computation)
- Workshop paper on implementation insights (e.g., ICML Active Inference workshop)

---

## Technical Approach

### Belief Representation
- Discrete probability distributions over states
- Exact Bayesian updates where tractable
- Particle filters for continuous extensions

### Planning Algorithms
- Point-based value iteration for standard POMDP
- Belief-space MDP reduction for ρ-POMDPs
- Variational message passing for VFE agent

### Software Stack
- Python 3.10+
- NumPy/SciPy for numerical computation
- JAX for automatic differentiation (VFE gradients)
- Matplotlib/Seaborn for visualization
- Pytest for testing
- Weights & Biases for experiment tracking

---

## Collaboration Plan

### Patrick Cooper (Implementation Lead)
- Environment development
- Agent implementation
- Experimental execution
- Results analysis and visualization

### David Baines (Theoretical Lead)
- POMDP and ρ-POMDP model formalization
- Active inference integration
- Convergence analysis
- Broader POMDP benchmark curation

### Weekly Meetings
- **Schedule**: Thursdays at 11:00 AM
- **Format**: Progress review, theoretical discussion, planning
- **Platform**: Microsoft Teams / In-person

---

## Success Criteria

### Minimal Success
- Complete implementation of all three agents on Tiger problem
- Clear demonstration of different epistemic foraging patterns
- Reproducible experimental results

### Target Success
- VFE agent shows measurably faster belief convergence
- Statistically significant differences in sample efficiency
- Clear characterization of when VFE outperforms alternatives

### Aspirational Success
- Theoretical explanation of empirical performance differences
- Successful scaling to multiple POMDP benchmarks
- Publication-ready results and insights
- Open-source framework for future ρ-POMDP research

---

## Current Status

**Project Phase**: Initialization  
**Next Steps**:
1. Create project structure and repository setup
2. Implement Tiger problem environment
3. Develop standard POMDP baseline

**Upcoming Meeting**: Thursday, February 13, 2026 at 11:30 AM

---

## Document Evolution

This guidance document will be updated continuously to reflect:
- Implementation decisions and their rationale
- Experimental findings and insights
- Adjustments to research direction
- Technical challenges and solutions
- Progress toward publication

Each significant change should be committed to version control with clear documentation of what changed and why.
