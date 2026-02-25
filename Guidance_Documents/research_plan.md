# Research Plan and Guidance Document

## Project: rho-POMDP Active Inference Framework

**Last Updated**: February 25, 2026  
**Project Lead**: Patrick Cooper  
**Collaborator**: David Baines  
**Advisor**: Ashutosh Trehan

---

## Research Questions

**RQ1**: Does variational free energy serve as an effective generalized utility function (rho) for rho-POMDPs? This is the foundational question -- can you formally substitute VFE (or expected free energy) as rho, and does the resulting framework remain tractable and well-defined? This covers the theoretical grounding: showing the mapping is coherent, characterizing what class of policies it induces, and identifying any boundary conditions where it breaks down.

**RQ2**: Do AIF-informed rho-POMDPs produce superior epistemic foraging compared to standard POMDP approaches in partially observable environments? "Superior" is operationalized as faster belief convergence, fewer information-gathering steps before committing to exploitative action, or better final policy quality in environments that require active information seeking. The comparison set is standard reward-maximizing POMDPs and rho-POMDPs with alternative belief-state utilities (e.g., pure information gain, belief entropy).

**RQ3**: What does the choice of rho reveal about the relationship between agent constitution and epistemic behavior? If an agent's utility is defined over its own beliefs (VFE as rho), does that produce qualitatively different agent behavior -- not just quantitatively better performance, but a different kind of agency? This connects to alignment interests: agents that are constitutively epistemic may be more interpretable, more robust to distributional shift, or more amenable to value alignment than agents that treat information gathering as purely instrumental.

### Unified Experimental Prompt

We examine whether variational free energy, used as the generalized utility function in rho-POMDPs, produces superior epistemic foraging behavior compared to standard reward-maximizing POMDP policies and alternative belief-state utility functions, measured by policy quality, sample efficiency, and belief convergence rate in partially observable environments requiring active information gathering.

---

## AIF Algorithm Clarification

Active inference is not a family of competing algorithms the way RL has Q-learning vs. PPO vs. SAC. It is a single objective -- minimize expected free energy -- which naturally decomposes into pragmatic and epistemic terms. Implementation choices arise around the generative model structure and the inference method:

- **Exact Bayesian updates** (discrete state-spaces): Used for initial experiments on the Tiger problem and minimal testbeds. Standard entry point in the AIF literature.
- **Variational message passing**: For scaled continuous or hierarchical models.
- **Amortized inference**: Neural network approximations for high-dimensional problems.

For this project, we begin with discrete state-space models and exact Bayesian updates, with more elaborate inference methods to follow as environments scale.

Key references: Da Costa et al. (2020), Parr & Friston (2019).

---

## Phase 1: Tiger Problem Baseline

### Rationale

The Tiger problem provides a minimal, well-understood testbed that isolates epistemic foraging behavior. Its simplicity allows us to:
- Verify correct implementation of all three agent types
- Establish clear baselines for comparison
- Analyze belief dynamics in detail
- Validate metrics before scaling complexity

OpenAI Gymnasium is used as the environment interface. This is a well-known standard in the RL community that reviewers will understand immediately, saving paper space for contributions and analysis rather than environment specification.

### Agent Implementations

#### 1. Standard Reward-Maximizing POMDP Agent (Myopic Baseline)
- **Objective**: Maximize expected cumulative reward
- **Planning**: One-step lookahead (myopic)
- **No explicit belief utility**: Actions chosen purely for state-reward optimization
- **Role**: Baseline for comparison

#### 2. rho-POMDP Agent with Information Gain
- **Objective**: Maximize reward + information gain over beliefs
- **Utility Function (rho)**: Information gain (entropy reduction)
- **Planning**: Belief-space planning with information-theoretic utility
- **Role**: Standard epistemic foraging approach for comparison

#### 3. rho-POMDP Agent with Expected Free Energy
- **Objective**: Minimize expected free energy G(pi)
- **Utility Function (rho)**: G(pi) = pragmatic value + epistemic value, derived from a single objective without tunable weighting parameters
- **Pragmatic value**: Cross-entropy between expected and preferred observations
- **Epistemic value**: Expected mutual information between states and observations
- **Planning**: Active inference policy selection via argmin G(pi)
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

### Target Venues
- NeurIPS (primary target, per David's paper formatting commitment)
- UAI, AISTATS (alternatives)
- ICML Active Inference Workshop

---

## Technical Approach

### Environment Framework
- OpenAI Gymnasium interface for all environments
- Discrete observation and action spaces
- Configurable environment parameters
- Standard reset/step API for reviewer familiarity and RL tooling compatibility

### Belief Representation
- Discrete probability distributions over states
- Exact Bayesian updates where tractable
- Particle filters for continuous extensions

### Planning Algorithms
- One-step lookahead for myopic baseline
- Belief-space planning with information-theoretic utility for info gain agent
- Expected free energy minimization for VFE agent (no hand-tuned exploration weights)

### Software Stack
- Python 3.10+
- NumPy/SciPy for numerical computation
- Gymnasium for environment interface
- JAX for automatic differentiation (future VFE gradient extensions)
- Matplotlib/Seaborn for visualization
- Pytest for testing
- Weights & Biases for experiment tracking

---

## Collaboration Plan

### Patrick Cooper (Implementation Lead)
- Environment development (Gymnasium-wrapped)
- Agent implementation (Myopic, Info Gain, VFE with proper EFE)
- Experimental execution
- Results analysis and visualization

### David Baines (Theoretical Lead)
- POMDP and rho-POMDP model formalization
- NeurIPS paper formatting and drafting
- Convergence analysis
- Broader POMDP benchmark curation

### Ashutosh Trehan (Advisor)
- Theoretical review and feedback
- AIF methodology guidance

### Communication
- **Weekly meetings**: Thursdays (time varies)
- **Async updates**: Email thread for weeks when meetings are missed
- **Shared doc**: Running to-do list and open questions
- **Repository**: GitHub (David added as collaborator, gh: davidpantile)

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
- Open-source framework for future rho-POMDP research

---

## Current Status

**Project Phase**: Implementation Overhaul  
**Date**: February 25, 2026

**Completed**:
1. Project structure and repository setup
2. Minimal two-state information-seeking testbed
3. Three initial agent implementations (Myopic, Information Gain, VFE stub)
4. Experimental framework with 1,000 episodes per agent
5. Statistical analysis and initial results documentation

**Key Findings from Minimal Testbed**:
- Information Gain agent significantly outperforms Myopic baseline (p < 0.001): 217% more exploration, 19% higher success rate, 17% higher reward
- VFE agent is non-functional: behaves identically to Myopic due to flawed implementation (weighted info gain, not true EFE). Requires full rewrite, not parameter tuning.

**In Progress**:
1. Guidance document and paper.tex alignment with email thread and research questions
2. Code restructure: extracting monolithic run_experiment.py into modular architecture
3. Gymnasium integration for all environments
4. VFE agent rewrite with proper Expected Free Energy formulation
5. Tiger Problem implementation
6. Comprehensive test suite

**Blocked / Awaiting**:
- NeurIPS paper formatting (David)
- POMDP use cases for testing context (David)

---

## References

- Araya, M., et al. (2010). A POMDP extension with belief-dependent rewards. *NIPS*
- Da Costa, L., et al. (2020). Active inference on discrete state-spaces: A synthesis. *Journal of Mathematical Psychology*
- Friston, K. (2010). The free-energy principle: a unified brain theory? *Nature Reviews Neuroscience*
- Parr, T., & Friston, K. J. (2019). Generalised free energy and active inference. *Biological Cybernetics*

---

## Document Evolution

This guidance document is updated continuously to reflect:
- Implementation decisions and their rationale
- Experimental findings and insights
- Adjustments to research direction
- Technical challenges and solutions
- Progress toward publication

Each significant change should be committed to version control with clear documentation of what changed and why.
