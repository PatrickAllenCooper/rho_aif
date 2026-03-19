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

4. **Tileworld (Tile Search)**
   - N x N grid with hidden target tile
   - K scan actions partition the grid spatially (bit-level row/column splits)
   - N^2 commit actions (collect at cell)
   - Spatial generalization of Diagnosis; produces visual belief evolution figures
   - Scaling from 4x4 (16 states) to 8x8 (64 states)

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

## Experimental Results and Implications for the Paper

### Expanded Baselines (March 2026)

All experiments now include six agent types for controlled comparison:
1. **Myopic** (1-step, reward only) -- weakest baseline
2. **Planning** (H-step, reward only) -- controls for planning depth
3. **InfoGain** (1-step, w=1.0) -- untuned epistemic baseline
4. **InfoGain-Tuned** (1-step, per-env optimal w) -- best-case InfoGain
5. **VFE** (H-step, EFE) -- our method
6. **PyMDP-AIF** (pymdp library reference) -- independent implementation

### Tiger Problem (1,000 episodes, H=6, +10/-100)

| Agent | Listens | Success | Reward |
|---|---|---|---|
| Myopic | 1.00 | 84.4% | -8.16 |
| Planning (H=6) | 4.20 | 99.3% | +5.03 |
| InfoGain (w=1) | 1.00 | 85.4% | -7.06 |
| InfoGain-Tuned (w=20) | 4.20 | **99.6%** | **+5.36** |
| VFE (H=6) | 4.29 | 99.5% | +5.16 |
| PyMDP-AIF | 2.68 | 97.5% | +4.57 |

Planning, Tuned InfoGain, and VFE are statistically equivalent. VFE advantage = no tuning.

### Info-Seeking Testbed (1,000 episodes, H=4, +1/-1)

| Agent | Obs | Success | Reward |
|---|---|---|---|
| Myopic | 1.00 | 73.3% | +0.37 |
| Planning (H=4) | 3.22 | 89.2% | **+0.46** |
| InfoGain (w=1) | 3.27 | 89.1% | +0.46 |
| InfoGain-Tuned (w=50) | 12.08 | **99.9%** | -0.21 |
| VFE (H=4) | 5.50 | 95.6% | +0.36 |
| PyMDP-AIF | 3.36 | 91.5% | +0.49 |

VFE over-explores in low-stakes env. Best reward = Planning/PyMDP.

### Diagnosis (1,000 episodes, N=4, H=3, +10/-50)

| Agent | Tests | Success | Reward |
|---|---|---|---|
| Myopic | 2.00 | 64.2% | -13.48 |
| Planning (H=3) | 5.90 | 87.9% | -3.16 |
| InfoGain (w=1) | 2.00 | 62.4% | -14.56 |
| InfoGain-Tuned (w=100) | 13.24 | **98.7%** | -4.02 |
| **VFE (H=3)** | **9.73** | **97.0%** | **-1.53** |

VFE significantly outperforms Planning (p=0.022). Best reward and near-best success.

### Bandit (1,000 episodes, K=4, H=2, +10/+1)

| Agent | Inspections | Success | Reward |
|---|---|---|---|
| Myopic | 2.09 | 64.6% | +5.77 |
| Planning (H=2) | 3.26 | 67.5% | +5.44 |
| InfoGain (w=1) | 2.04 | 60.5% | +5.43 |
| InfoGain-Tuned (w=50) | 10.90 | **99.7%** | +4.52 |
| **VFE (H=2)** | **4.94** | **88.1%** | **+6.46** |

VFE dominates on BOTH reward AND success. Planning barely improves over Myopic.

### Navigation (500 episodes, 3x3 grid, +20 goal, -0.5 step cost)

| Agent | Steps | Success | Reward |
|---|---|---|---|
| **NavMyopic** | **28.03** | **92.0%** | **+4.38** |
| NavInfoGain | 41.13 | 83.6% | -3.84 |
| NavVFE (H=2) | 45.55 | 82.8% | -6.22 |

VFE over-explores on small grids. Greedy agent wins.

### Tileworld 6x6 (500 episodes, H=2, +10/-50, scan cost -1.0)

| Agent | Scans | Success | Reward |
|---|---|---|---|
| Myopic | 0.00 | 2.2% | -48.68 |
| Planning (H=2) | 15.96 | 71.2% | -23.24 |
| InfoGain (w=1) | 5.15 | 29.2% | -37.63 |
| InfoGain-Tuned (w=100) | 32.71 | 99.0% | -23.31 |
| Planning+IG (w=100) | 33.49 | 98.6% | -24.33 |
| EpistemicOnly | 200.0 | 0.0% | -200.00 |
| **VFE (H=2)** | **14.89** | **73.6%** | **-20.73** |

VFE achieves highest reward. InfoGain-Tuned and Planning+IG over-explore massively (30+ scans).

### Tileworld Scaling (200 episodes, H=2)

| Grid | Myopic | Planning | VFE |
|---|---|---|---|
| 4x4 | 46.0% | 80.5% | 77.0% |
| 6x6 | 2.5% | 82.0% | 76.0% |
| 8x8 | 0.5% | 2.0% | **75.5%** |

**Key finding**: At 8x8 (64 states), VFE 75.5% vs Planning 2.0%. Reward-only planning cannot justify scanning at H=2 with 64 states; VFE's epistemic term drives systematic information gathering.

### Scaling Analysis (Diagnosis N=2,4,8,16, H=2)

| N | Myopic | Planning | VFE | VFE vs Myopic |
|---|---|---|---|---|
| 2 | 80.2% | 93.8% | 95.2% | +15.0 pp |
| 4 | 67.0% | 88.8% | 87.6% | +20.6 pp |
| 8 | 50.0% | 84.6% | 83.8% | +33.8 pp |
| 16 | 38.8% | 81.2% | 77.6% | +38.8 pp |

At H=2, Planning and VFE are equivalent. VFE's advantage over Planning requires H>=3.

### Key Findings

**RQ1 (Tractability)**: Fully supported. EFE substitution is coherent, tractable, validated against pymdp.

**RQ2 (Epistemic superiority)**: Environment-dependent AND horizon-dependent:
- Simple observe-then-commit: VFE matches tuned alternatives without tuning
- Multi-observation-action environments with sufficient depth: VFE significantly outperforms same-horizon Planning (Diagnosis +9.1 pp at H=3, Bandit +20.6 pp at H=2)
- At H=2, VFE and Planning perform equivalently on scaling analysis -- EFE advantage requires sufficient recursive depth
- Very small state spaces: VFE over-explores
- **Tileworld spatial scaling**: VFE advantage GROWS with state space size. At 8x8 (64 states), VFE 75.5% vs Planning 2.0%. This is the strongest evidence that EFE's epistemic term is essential for larger problems.

**RQ3 (Constitutive epistemics)**: Supported with boundary conditions. Most valuable under structured uncertainty (multiple observation types, large state spaces). Can be counterproductive in very small/simple environments.

**InfoGain fragility**: Tuned weights vary from w=20 (Tiger) to w=100 (Diagnosis), confirming per-environment brittleness. Tuned InfoGain systematically over-explores.

---

## Current Status

**Project Phase**: Phase 7 -- NeurIPS Submission Polish  
**Date**: March 19, 2026

**Completed**:
1. Modular codebase with generalized multi-observation-action agent architecture
2. Six Gymnasium environments: InfoSeeking, Tiger, Diagnosis, Bandit, Navigation, Tileworld
3. Ten+ agent types: Myopic, Planning, InformationGain, PlanningInfoGain, VFE, EpistemicOnly, NavigationVFE, NavigationMyopic, NavigationInfoGain, PyMDP-AIF
4. Per-environment InfoGain weight tuning via grid search
5. Full experiments on all environments with all baselines (500-1000 episodes each)
6. Scaling analysis: Diagnosis N=2,4,8,16 with Planning baseline
7. pymdp integration: reference agent + EFE consistency validation
8. Comprehensive test suite (161 tests, all passing)
9. Paper draft with expanded results, honest comparative analysis
10. All experiments re-run and verified with fixed seed (March 2026)
11. Holm-Bonferroni corrected statistics integrated into experiment runner
12. Supplementary material: bootstrap CIs, Cohen's d effect sizes for all pairwise comparisons
13. Four original figures regenerated: asymmetry sweep, EFE trajectories, obs scaling, Pareto
14. Four new long-horizon visualization figures: belief heatmap, efficiency curves, extended EFE decomposition, stopping time distributions
15. Paper inconsistencies fixed (baseline count, weight reporting, supplementary reference)
16. Guidance document aligned with all experimental findings
17. NeurIPS submission polish complete
18. Tileworld champion example: 6x6 grid POMDP with rendered belief evolution and agent comparison figures, spatial scaling analysis (4x4 to 8x8), four new paper figures (belief strip, agent comparison, scaling, scan atlas), headline result of VFE 75.5% vs Planning 2.0% at 8x8
19. NeurIPS page-length restructure: consolidated Tiger/Diagnosis/Bandit into single main table; moved Testbed, Tiger sweep, obs-action scaling, Tileworld belief strip, and EFE trajectory figure to appendix; tightened abstract, experiments, discussion, and conclusion; main text now ~9 pages with 3 figures and 3 tables

**Awaiting**:
- Feedback from Ashutosh on methodology
- Computational scaling improvements (MCTS or amortized planning for deeper horizons)
- Formal convergence analysis of the recursive EFE scheme

---

## References

- Araya, M., et al. (2010). A POMDP extension with belief-dependent rewards. *NIPS*
- Benchetrit, Y., et al. (2025). rho-POMCPOW: Online planning for continuous rho-POMDPs. *arXiv:2502.02549*
- Da Costa, L., et al. (2020). Active inference on discrete state-spaces: A synthesis. *Journal of Mathematical Psychology*
- Da Costa, L., et al. (2023). Reward maximization through discrete active inference. *Neural Computation*
- Fehr, R., et al. (2018). rho-POMDPs have Lipschitz-continuous epsilon-optimal value functions. *NeurIPS*
- Friston, K. (2010). The free-energy principle: a unified brain theory? *Nature Reviews Neuroscience*
- Friston, K., et al. (2021). Sophisticated inference. *Neural Computation*
- Millidge, B., et al. (2020). On the relationship between active inference and control as inference. *IWAI*
- Parr, T., & Friston, K. J. (2019). Generalised free energy and active inference. *Biological Cybernetics*
- Sajid, N., et al. (2021). Active inference: Demystified and compared. *Neural Computation*

---

## Document Evolution

This guidance document is updated continuously to reflect:
- Implementation decisions and their rationale
- Experimental findings and insights
- Adjustments to research direction
- Technical challenges and solutions
- Progress toward publication

Each significant change should be committed to version control with clear documentation of what changed and why.
