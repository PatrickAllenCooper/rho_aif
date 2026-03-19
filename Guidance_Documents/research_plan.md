# Research Plan and Guidance Document

## Project: rho-POMDP Active Inference Framework

**Last Updated**: March 19, 2026  
**Project Lead**: Patrick Cooper  
**Collaborator**: David Baines  
**Advisor**: Ashutosh Trehan

---

## Research Questions

**RQ1**: Does expected free energy (EFE) serve as an effective generalized utility function (rho) for rho-POMDPs? This is the foundational question -- can you formally substitute EFE as rho, and does the resulting framework remain tractable and well-defined? This covers the theoretical grounding: showing the mapping is coherent, characterizing what class of policies it induces, and identifying any boundary conditions where it breaks down.

**RQ2**: Do AIF-informed rho-POMDPs produce superior epistemic foraging compared to standard POMDP approaches in partially observable environments? "Superior" is operationalized as faster belief convergence, fewer information-gathering steps before committing to exploitative action, or better final policy quality in environments that require active information seeking. The comparison set is standard reward-maximizing POMDPs and rho-POMDPs with alternative belief-state utilities (e.g., pure information gain, belief entropy, Thompson sampling).

**RQ3**: What does the choice of rho reveal about the relationship between agent constitution and epistemic behavior? If an agent's utility is defined over its own beliefs (EFE as rho), does that produce qualitatively different agent behavior -- not just quantitatively better performance, but a different kind of agency? This connects to alignment interests: agents that are constitutively epistemic may be more interpretable, more robust to distributional shift, or more amenable to value alignment than agents that treat information gathering as purely instrumental.

### Unified Experimental Prompt

We examine whether expected free energy (EFE), used as the generalized utility function in rho-POMDPs, produces superior epistemic foraging behavior compared to standard reward-maximizing POMDP policies and alternative belief-state utility functions, measured by policy quality, sample efficiency, and belief convergence rate in partially observable environments requiring active information gathering.

---

## AIF Algorithm Clarification

Active inference is not a family of competing algorithms the way RL has Q-learning vs. PPO vs. SAC. It is a single objective -- minimize expected free energy -- which naturally decomposes into pragmatic and epistemic terms. Implementation choices arise around the generative model structure and the inference method:

- **Exact Bayesian updates** (discrete state-spaces): Used for experiments on all six observe-then-commit environments. Standard entry point in the AIF literature.
- **Monte Carlo Tree Search (MCTS)**: For scaling beyond exact tree search to higher horizons and larger state spaces. EFE serves as the leaf heuristic.
- **Variational message passing**: For scaled continuous or hierarchical models (future work).
- **Amortized inference**: Neural network approximations for high-dimensional problems (future work).

The project uses discrete state-space models with exact Bayesian updates for the core results, supplemented by MCTS for computational scaling experiments.

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

#### 1. Myopic (myopic.py)
- **Objective**: Maximize expected immediate reward
- **Planning**: One-step lookahead
- **Role**: Weakest baseline

#### 2. Planning (planning.py)
- **Objective**: Maximize expected cumulative reward via recursive Bellman backup
- **Planning**: H-step lookahead, reward only
- **Role**: Controls for planning depth vs. epistemic drive

#### 3. Information Gain (infogain.py)
- **Objective**: Maximize reward + w * information_gain
- **Planning**: One-step with tunable weight w
- **Role**: Standard epistemic foraging baseline (requires per-env tuning)

#### 4. Planning+IG (planning_infogain.py)
- **Objective**: Maximize reward + w * information_gain with recursive planning
- **Planning**: H-step with tunable weight w
- **Role**: Tests whether multi-step IG planning suffices

#### 5. EFE Agent (efe.py) -- PRIMARY CONTRIBUTION
- **Objective**: Minimize expected free energy G(pi), which decomposes into pragmatic value (reward alignment) and epistemic value (information gain) without any tunable weight parameter (w=1 emerges from the derivation)
- **Planning**: Recursive multi-step EFE minimization
- **Role**: Primary experimental condition
- **Supports**: Discount factor gamma, multiple observation actions

#### 6. Thompson Sampling (thompson.py)
- **Objective**: Sample-based action selection via posterior sampling
- **Planning**: Per-sample optimal action with majority vote
- **Role**: Strong Bayesian exploration baseline (added in revision)

#### 7. MCTS-EFE (mcts_efe.py)
- **Objective**: Same as EFE but using MCTS for scalable tree search
- **Planning**: Monte Carlo tree search with EFE leaf evaluation
- **Role**: Computational scaling beyond exact tree search (added in revision)

#### 8. Epistemic Only (epistemic_only.py)
- **Objective**: Maximize information gain only (no reward)
- **Role**: Ablation to isolate epistemic contribution

#### 9. Environment-Specific Agents
- **NavigationEFE** (navigation_efe.py): EFE for grid navigation
- **RockSampleEFE** (rocksample_agents.py): EFE for interleaved observe-act POMDPs
- **PyMDP-AIF**: Reference implementation via pymdp library

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

### Environments (All Implemented)

1. **Info-Seeking Testbed** -- 2-state, symmetric rewards, canonical AIF benchmark
2. **Tiger Problem** -- 2-state, extreme reward asymmetry (+10/-100)
3. **Sequential Diagnosis** -- N-condition (N=2..16), K diagnostic tests, hierarchical disambiguation
4. **Multi-Armed Bandit** -- K arms with hidden quality, inspection actions
5. **Navigation** -- Grid-world with limited visibility, hidden goal
6. **Tileworld** -- N x N grid, spatial scan actions, scaling from 4x4 to 8x8
7. **RockSample** -- Interleaved observe-act POMDP with state transitions (added in revision, addresses W2)

### Scaling Analysis
- State space scaling: Tileworld 4x4 to 8x8 (16-64 states)
- Condition scaling: Diagnosis N=2 to N=16
- Computational scaling: MCTS vs exact tree search at varying horizons
- Model robustness: Misspecified observation accuracy experiments

---

## Theoretical Contributions

### Theoretical Contributions

1. **Formal Equivalence (Proposition 3.3)**: EFE minimization is equivalent to solving a rho-POMDP with rho = information gain, w=1, and Bellman recursion. This holds for any gamma in (0,1].
2. **w=1 Characterization**: Formal analysis using reward asymmetry ratio (alpha) and observation informativeness (eta) to characterize when w=1 is near-optimal vs. when it over-explores.
3. **Discounting Extension**: EFE with gamma < 1 preserves the rho-POMDP equivalence but shifts the effective epistemic-to-pragmatic ratio across planning depths.

### Empirical Contributions

1. **Direct comparison**: EFE vs. reward-only Planning, tuned InfoGain, Thompson sampling, POMCP across six environments
2. **Scaling evidence**: EFE advantage grows with state space size (Tileworld 8x8: 66.5% vs 2.5%; complete scaling with all agents including Planning+IG)
3. **Robustness**: Model misspecification experiments show graceful degradation; discount sensitivity analyzed with Planning baseline
4. **MCTS scaling**: EFE as leaf heuristic enables practical planning at H=5+
5. **POMCP comparison**: EFE outperforms standard POMCP on multi-observation environments (Appendix P)
6. **RockSample**: EFE extends to interleaved observe-act POMDPs (Appendix Q)

### Target Venues
- NeurIPS 2026 (initial submission received Weak Reject; revision in progress)
- UAI, AISTATS (alternatives if NeurIPS resubmission unsuccessful)

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
- Expected free energy minimization for EFE agent (no hand-tuned exploration weights)
- Monte Carlo Tree Search with EFE leaf heuristic for computational scaling

### Software Stack
- Python 3.9+
- NumPy/SciPy for numerical computation
- Gymnasium for environment interface
- Matplotlib/Seaborn for visualization
- Pytest for testing (203 tests)
- pandas for experiment results

---

## Collaboration Plan

### Patrick Cooper (Implementation Lead)
- Environment development (Gymnasium-wrapped)
- Agent implementation (Myopic, Info Gain, EFE)
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
- EFE agent shows measurably faster belief convergence
- Statistically significant differences in sample efficiency
- Clear characterization of when EFE outperforms alternatives

### Aspirational Success
- Theoretical explanation of empirical performance differences
- Successful scaling to multiple POMDP benchmarks
- Publication-ready results and insights
- Open-source framework for future rho-POMDP research

---

## Experimental Results and Implications for the Paper

### Expanded Baselines (March 2026)

All experiments now include seven+ agent types for controlled comparison:
1. **Myopic** (1-step, reward only) -- weakest baseline
2. **Planning** (H-step, reward only) -- controls for planning depth
3. **InfoGain** (1-step, w=1.0) -- untuned epistemic baseline
4. **InfoGain-Tuned** (1-step, per-env optimal w) -- best-case InfoGain
5. **EFE** (H-step, EFE minimization) -- our method
6. **Thompson Sampling** (posterior sampling, 100 samples) -- Bayesian exploration baseline (added in revision)
7. **PyMDP-AIF** (pymdp library reference) -- independent implementation

### Tiger Problem (1,000 episodes, H=6, +10/-100)

| Agent | Listens | Success | Reward |
|---|---|---|---|
| Myopic | 1.00 | 84.4% | -8.16 |
| Planning (H=6) | 4.20 | 99.3% | +5.03 |
| InfoGain (w=1) | 1.00 | 85.4% | -7.06 |
| InfoGain-Tuned (w=20) | 4.20 | **99.6%** | **+5.36** |
| EFE (H=6) | 4.29 | 99.5% | +5.16 |
| PyMDP-AIF | 2.68 | 97.5% | +4.57 |

Planning, Tuned InfoGain, and EFE are statistically equivalent. EFE advantage = no tuning.

### Info-Seeking Testbed (1,000 episodes, H=4, +1/-1)

| Agent | Obs | Success | Reward |
|---|---|---|---|
| Myopic | 1.00 | 73.3% | +0.37 |
| Planning (H=4) | 3.22 | 89.2% | **+0.46** |
| InfoGain (w=1) | 3.27 | 89.1% | +0.46 |
| InfoGain-Tuned (w=50) | 12.08 | **99.9%** | -0.21 |
| EFE (H=4) | 5.50 | 95.6% | +0.36 |
| PyMDP-AIF | 3.36 | 91.5% | +0.49 |

EFE over-explores in low-stakes env. Best reward = Planning/PyMDP.

### Diagnosis (1,000 episodes, N=4, H=3, +10/-50)

| Agent | Tests | Success | Reward |
|---|---|---|---|
| Myopic | 2.00 | 64.2% | -13.48 |
| Planning (H=3) | 5.90 | 87.9% | -3.16 |
| InfoGain (w=1) | 2.00 | 62.4% | -14.56 |
| InfoGain-Tuned (w=100) | 13.24 | **98.7%** | -4.02 |
| **EFE (H=3)** | **9.73** | **97.0%** | **-1.53** |

EFE significantly outperforms Planning (p=0.022). Best reward and near-best success.

### Bandit (1,000 episodes, K=4, H=2, +10/+1)

| Agent | Inspections | Success | Reward |
|---|---|---|---|
| Myopic | 2.09 | 64.6% | +5.77 |
| Planning (H=2) | 3.26 | 67.5% | +5.44 |
| InfoGain (w=1) | 2.04 | 60.5% | +5.43 |
| InfoGain-Tuned (w=50) | 10.90 | **99.7%** | +4.52 |
| **EFE (H=2)** | **4.94** | **88.1%** | **+6.46** |

EFE dominates on BOTH reward AND success. Planning barely improves over Myopic.

### Navigation (500 episodes, 3x3 grid, +20 goal, -0.5 step cost)

| Agent | Steps | Success | Reward |
|---|---|---|---|
| **NavMyopic** | **28.03** | **92.0%** | **+4.38** |
| NavInfoGain | 41.13 | 83.6% | -3.84 |
| NavEFE (H=2) | 45.55 | 82.8% | -6.22 |

EFE over-explores on small grids. Greedy agent wins.

### Tileworld 6x6 (500 episodes, H=2, +10/-50, scan cost -1.0)

| Agent | Scans | Success | Reward |
|---|---|---|---|
| Myopic | 0.00 | 2.2% | -48.68 |
| Planning (H=2) | 15.96 | 71.2% | -23.24 |
| InfoGain (w=1) | 5.15 | 29.2% | -37.63 |
| InfoGain-Tuned (w=100) | 32.71 | 99.0% | -23.31 |
| Planning+IG (w=100) | 33.49 | 98.6% | -24.33 |
| EpistemicOnly | 200.0 | 0.0% | -200.00 |
| **EFE (H=2)** | **14.89** | **73.6%** | **-20.73** |

EFE achieves highest reward. InfoGain-Tuned and Planning+IG over-explore massively (30+ scans).

### Tileworld Scaling (200 episodes, H=2, All Agents)

| Grid | Myopic | Planning | InfoGain-Tuned | Planning+IG | EFE |
|---|---|---|---|---|---|
| 4x4 | 35.0% | 71.0% | 98.5% | 98.5% | 81.0% |
| 6x6 | 3.5% | 70.0% | 99.5% | 98.5% | 75.5% |
| 8x8 | 2.0% | 2.5% | 96.5% | **98.0%** | 66.5% |

**Key finding**: At 8x8 (64 states), EFE 66.5% vs Planning 2.5%. Planning+IG at w=100 achieves 98.0% but at substantial reward cost (-31.40 vs EFE's -27.54). EFE Pareto-dominates Planning at every scale (higher success AND best reward). The gap between w*_ret and w*_succ widens with |S|.

### Scaling Analysis (Diagnosis N=2,4,8,16, H=2)

| N | Myopic | Planning | EFE | EFE vs Myopic |
|---|---|---|---|---|
| 2 | 80.2% | 93.8% | 95.2% | +15.0 pp |
| 4 | 67.0% | 88.8% | 87.6% | +20.6 pp |
| 8 | 50.0% | 84.6% | 83.8% | +33.8 pp |
| 16 | 38.8% | 81.2% | 77.6% | +38.8 pp |

At H=2, Planning and EFE are equivalent. EFE's advantage over Planning requires H>=3.

### Key Findings

**RQ1 (Tractability)**: Fully supported. EFE substitution is coherent, tractable, validated against pymdp.

**RQ2 (Epistemic superiority)**: Environment-dependent AND horizon-dependent:
- Simple observe-then-commit: EFE matches tuned alternatives without tuning
- Multi-observation-action environments with sufficient depth: EFE significantly outperforms same-horizon Planning (Diagnosis +9.1 pp at H=3, Bandit +20.6 pp at H=2)
- At H=2, EFE and Planning perform equivalently on scaling analysis -- EFE advantage requires sufficient recursive depth
- Very small state spaces: EFE over-explores
- **Tileworld spatial scaling**: EFE advantage GROWS with state space size. At 8x8 (64 states), EFE 75.5% vs Planning 2.0%. This is the strongest evidence that EFE's epistemic term is essential for larger problems.
- **Model misspecification**: EFE degrades gracefully with +/- 0.15 accuracy mismatch; overestimating accuracy is more harmful than underestimating

**RQ3 (Constitutive epistemics)**: Supported with boundary conditions. Most valuable under structured uncertainty (multiple observation types, large state spaces). Can be counterproductive in very small/simple environments.

**InfoGain fragility**: Tuned weights vary from w=20 (Tiger) to w=100 (Diagnosis), confirming per-environment brittleness. Tuned InfoGain systematically over-explores.

### Revision-Specific Findings (March 2026)

**Thompson Sampling comparison**: Thompson matches EFE on Tiger but underperforms on multi-observation-action environments (Diagnosis, Bandit) where EFE's recursive planning exploits observation structure.

**Discount sensitivity (with Planning baseline)**: EFE is robust across gamma in {0.9, 0.95, 0.99, 1.0} on Tiger. On Diagnosis and Bandit, heavy discounting (gamma=0.9) erases EFE's advantage over Planning; both agents become myopic. At gamma=0.99+, EFE's advantage emerges sharply: +7.0 pp on Diagnosis, +22.0 pp on Bandit. The relative gap between EFE and Planning depends on gamma preserving sufficient effective horizon.

**RockSample (interleaved observe-act)**: EFE extends naturally to environments with state transitions. The RockSampleEFE agent outperforms a Greedy baseline on RS[5,3] (+8.86 vs +5.12 reward) and RS[7,4] (+8.82 vs +1.34) by checking rock quality before sampling. Formal analysis of where Proposition 3.3 breaks under state transitions added to Section 3 (transition-observation coupling term).

**POMCP comparison**: Standalone POMCP agent implemented and compared on all environments. POMCP substantially underperforms EFE on multi-observation environments: Tiger 90.6% vs 99.2%, Diagnosis 72.2% vs 96.6%, Tileworld 10.5% vs 73.0%. On Bandit, POMCP achieves 97.4% success but at extreme reward cost (+3.03 vs EFE's +6.42). POMCP's random rollout cannot evaluate differential informativeness of observation actions.

**Alpha-eta proposition (Proposition 3.X)**: Formalized when w=1 is near-optimal for two-state H=1 case using reward asymmetry ratio alpha and observation informativeness eta. Table mapping alpha, eta to predicted and observed w*_ret across all environments added to Section 3.

**Pareto dominance reframing**: Results text reframed from "EFE maximizes reward" to "EFE Pareto-dominates Planning" (higher success AND comparable reward). Run with 3000 episodes on Diagnosis and Bandit for tighter confidence intervals (non-overlapping CIs on Bandit reward).

**Model misspecification**: EFE degrades gracefully with systematic accuracy mismatch. On Tiger, >96.5% success across all mismatch levels (+/- 0.15). Overestimating accuracy is more harmful than underestimating, because agents commit prematurely. EFE's epistemic drive partially buffers against overconfident models.

**MCTS scaling**: MCTSEFEAgent with EFE leaf heuristic achieves comparable performance to exact tree search on Tiger at H=4, while scaling to higher horizons that are intractable for exact methods.

---

## Current Status

**Project Phase**: Phase 8 -- NeurIPS Revision (addressing reviewer comments)  
**Date**: March 19, 2026

### Initial Submission (Phases 1-7)

1. Modular codebase with generalized multi-observation-action agent architecture
2. Six Gymnasium environments: InfoSeeking, Tiger, Diagnosis, Bandit, Navigation, Tileworld
3. Multiple agent types: Myopic, Planning, InformationGain, PlanningInfoGain, EFE, EpistemicOnly
4. Per-environment InfoGain weight tuning via grid search
5. Full experiments on all environments with all baselines (500-1000 episodes each)
6. Scaling analysis: Diagnosis N=2,4,8,16 with Planning baseline
7. pymdp integration: reference agent + EFE consistency validation
8. Paper draft submitted to NeurIPS; received Weak Reject

### NeurIPS Revision (Phase 8, March 2026)

Addressing reviewer weaknesses W1-W6 and minor issues:

9. **W1 (Naming)**: Renamed "VFE" agent to "EFE" throughout entire codebase and paper to avoid confusion with variational free energy
10. **W5 (Baselines)**: Implemented Thompson Sampling agent as new Bayesian exploration baseline; integrated into all experiment runners
11. **W4 (Discounting)**: Added discount parameter (gamma) to EFE and Planning agents; extended Proposition 3.3 for gamma < 1; ran experiments with gamma in {0.9, 0.95, 0.99, 1.0}; added appendix table with BOTH EFE and Planning rows, plus relative-gap analysis
12. **W3 (Computational scaling)**: Implemented MCTSEFEAgent using EFE as leaf heuristic in MCTS framework; enables planning at H=5+ and larger state spaces
13. **W2 (Observe-then-commit restriction)**: Implemented RockSample environment with interleaved observe-act structure; redesigned RockSampleEFEAgent with deliberate information gathering; added formal analysis of where Prop 3.3 breaks under state transitions (transition-observation coupling term in Section 3); added RockSample appendix with results
14. **W6 (w=1 justification)**: Formalized alpha-eta characterization as Proposition 3.X in Section 3 with explicit expression for w*_ret at H=1; added table mapping alpha, eta to predicted vs observed w*_ret across all environments
15. **Robustness**: Added model misspecification experiments testing agents with wrong observation accuracy (+/- 0.15 mismatch); results show graceful degradation
16. **Paper updates**: Reframed results as Pareto dominance (not reward maximization); ran 3000 episodes on Diagnosis/Bandit for tighter CIs; standard errors in main table; observe-then-commit flagged in abstract; Cohen's d caveats removed (now using CIs); sophisticated inference clarification
17. **POMCP baseline**: Implemented standalone POMCP agent (agents/pomcp.py) with UCB1 tree search and particle belief; compared on Tiger, Diagnosis, Bandit, Tileworld; EFE outperforms POMCP on all multi-observation environments; added appendix table and discussion
18. **Tileworld scaling**: Added Planning+IG and InfoGain-Tuned to scaling analysis across all grid sizes (4x4, 6x6, 8x8); updated paper with complete data and analysis of w*_ret vs w*_succ at large scale
19. Comprehensive test suite expanded to 203 tests, all passing
20. Guidance document updated to reflect all revision changes

**Awaiting**:
- Feedback from Ashutosh on methodology
- Review of revision changes by David
- Resubmission to NeurIPS (or alternative venue)

---

## References

- Araya, M., et al. (2010). A POMDP extension with belief-dependent rewards. *NIPS*
- Benchetrit, Y., et al. (2025). rho-POMCPOW: Online planning for continuous rho-POMDPs. *arXiv:2502.02549*
- Silver, D., & Veness, J. (2010). Monte-Carlo Planning in Large POMDPs. *NeurIPS*
- Da Costa, L., et al. (2020). Active inference on discrete state-spaces: A synthesis. *Journal of Mathematical Psychology*
- Da Costa, L., et al. (2023). Reward maximization through discrete active inference. *Neural Computation*
- Fehr, R., et al. (2018). rho-POMDPs have Lipschitz-continuous epsilon-optimal value functions. *NeurIPS*
- Friston, K. (2010). The free-energy principle: a unified brain theory? *Nature Reviews Neuroscience*
- Friston, K., et al. (2021). Sophisticated inference. *Neural Computation*
- Heins, C., et al. (2022). pymdp: A Python library for active inference in discrete state spaces. *JOSS*
- Maisto, D., et al. (2025). Active inference tree search in large POMDPs. *arXiv*
- Millidge, B., et al. (2020). On the relationship between active inference and control as inference. *IWAI*
- Parr, T., & Friston, K. J. (2019). Generalised free energy and active inference. *Biological Cybernetics*
- Sajid, N., et al. (2021). Active inference: Demystified and compared. *Neural Computation*
- Smith, T. & Simmons, R. (2004). Heuristic search value iteration for POMDPs. *UAI* (RockSample benchmark)

---

## Document Evolution

This guidance document is updated continuously to reflect:
- Implementation decisions and their rationale
- Experimental findings and insights
- Adjustments to research direction
- Technical challenges and solutions
- Progress toward publication

Each significant change should be committed to version control with clear documentation of what changed and why.
