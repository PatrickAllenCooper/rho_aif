# Research Plan and Guidance Document

## Project: rho-POMDP Active Inference Framework

**Last Updated**: March 29, 2026  
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
- **RockSampleTreeSearchAgent** (rocksample_agents.py): Proper depth-limited belief-space tree search for interleaved observe-act POMDPs. Parameterized by info_weight: w=0 (Planning), w=1 (EFE), arbitrary w (Planning+IG). Uses factored belief (independent per-rock) with memoization. Replaces the earlier heuristic-based RockSample agents.
- **RockSamplePOMCPAgent** (rocksample_agents.py): POMCP with heuristic greedy rollout policy (bug fixed: no longer exits immediately)
- **RockSampleGreedyAgent** (rocksample_agents.py): Greedy heuristic baseline
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
7. **RockSample** -- Interleaved observe-act POMDP with state transitions. Three instances: RS[5,3], RS[7,4], RS[7,8]. Uses proper depth-limited tree search agents (not heuristics). Promoted to main text Section 5.4 with full results. Validates Proposition 3 (factored observation POMDP extension). Addresses reviewer weaknesses W2 (interleaved experiments) and partially W1 (broader formal result).

### Scaling Analysis
- State space scaling: Tileworld 4x4 to 8x8 (16-64 states)
- Condition scaling: Diagnosis N=2 to N=16
- Computational scaling: MCTS vs exact tree search at varying horizons
- Model robustness: Misspecified observation accuracy experiments

---

## Theoretical Contributions

### Theoretical Contributions

1. **Formal Equivalence (Proposition 1)**: EFE minimization is equivalent to solving a rho-POMDP with rho = information gain, w=1, and Bellman recursion. This holds for any gamma in (0,1]. Established for observe-then-commit POMDPs.
2. **Factored Observation POMDP Extension (Proposition 3, NEW)**: Extends the formal equivalence beyond observe-then-commit to factored observation POMDPs where the hidden state is preserved by information-gathering and navigation actions. Covers interleaved observe-act settings such as RockSample, mobile sensor placement, and sequential testing with spatial access costs. The coupling term Delta_T vanishes for all observation and navigation actions.
3. **w=1 Characterization (Proposition 2)**: Formal analysis using reward asymmetry ratio (alpha) and observation informativeness (eta) to characterize when w=1 is near-optimal vs. when it over-explores.
4. **Discounting Extension**: EFE with gamma < 1 preserves the rho-POMDP equivalence but shifts the effective epistemic-to-pragmatic ratio across planning depths.

### Empirical Contributions

1. **Direct comparison**: EFE vs. reward-only Planning, tuned InfoGain, Thompson sampling, POMCP across six observe-then-commit environments and three RockSample instances
2. **RockSample interleaved experiments (NEW, MAIN TEXT)**: Proper depth-limited belief-space tree search agents on RS[5,3], RS[7,4], RS[7,8]. EFE (w=1) achieves best reward on RS[5,3] and RS[7,4]; +7.82 reward gap over Planning on RS[7,8]. Validates Proposition 3 empirically. Promoted from appendix to main text Section 5.4.
3. **Zero-shot transfer experiment (NEW)**: Demonstrates that w=1 transfers across all four environments without retuning, while per-environment tuned weights transfer catastrophically. EFE achieves best or near-best reward on every target. Added to Discussion as Table.
4. **Scaling evidence**: EFE advantage grows with state space size (Tileworld 8x8: 66.5% vs 2.5%; complete scaling with all agents including Planning+IG) and observation action count (RockSample[7,8]: +7.82 gap)
5. **Robustness**: Model misspecification experiments show graceful degradation; discount sensitivity analyzed with Planning baseline
6. **MCTS scaling**: EFE as leaf heuristic enables practical planning at H=5+
7. **POMCP comparison**: EFE outperforms standard POMCP on multi-observation environments. POMCP on RockSample now uses heuristic rollout (bug fixed).

### Target Venues
- NeurIPS 2026 (initial submission received Borderline Reject; revision in progress addressing paths A, B, C)
  - Path A (broader formal result): Proposition 3 extends equivalence to factored observation POMDPs
  - Path B (stronger interleaved experiments): RS[5,3], RS[7,4], RS[7,8] with proper tree search agents, promoted to main text
  - Path C (canonical weight impact): Zero-shot transfer experiment showing w=1 transfers robustly
- IWAI 2026 (abridged 12-page LNCS version submitted; see paper/paper_iwai2026_abridged.tex)
- UAI, AISTATS (alternatives if NeurIPS resubmission unsuccessful)

### arXiv Preprint (July 2026)
- paper/paper_arxiv.tex: full non-anonymous version of the IWAI paper (LNCS format, 41 pages) with all appendix experiments (proofs, per-environment results, navigation, scaling, discount sensitivity, model misspecification, extended RockSample, POMCP comparison, MCTS-EFE)
- Authors: Patrick Cooper (primary) and Alvaro Velasquez, University of Colorado Boulder
- Links to the public code repository (github.com/PatrickAllenCooper/rho_aif); acknowledgments section dropped, competing-interests statement retained
- Submission package: paper/arxiv_submission.zip (paper_arxiv.tex, llncs.cls, 12 figure PDFs); verified to compile standalone
- Primary category cs.AI, cross-list cs.LG
- Abstract revised (July 2026) into a narrative structure (problem, insight, theory, evidence, takeaway), dropping the dense per-environment numbers in favor of one scale claim; applied to paper_arxiv.tex, paper_iwai2026.tex, and paper.tex (the submitted IWAI abridged snapshot keeps its original abstract)
- Bibliography audit (July 2026): added natbib author tags to all LNCS bibliographies so \citet resolves (19 citations previously rendered "(author?)"); corrected fehr2018 (M. Fehr), friston2015 (Friston, Rigoli, Ognibene, Mathys, FitzGerald, Pezzulo), benchetrit2025 (title "Anytime Incremental rhoPOMDP Planning in Continuous Spaces", R. Benchetrit), champion2024 (author order; now Neural Computation 38(3):439-469, 2026), maisto2025 (Neurocomputing 623), devries2025 (de Vries, Nuijten, van de Laar, et al.), araya2010 (Araya-Lopez), todorov (NeurIPS 2006); all 45 entries verified against published records; fixes mirrored across paper.tex, paper_arxiv.tex, paper_iwai2026.tex, paper_iwai2026_abridged.tex

### Repository Reorganization for Public Release (July 2026)
In preparation for the arXiv preprint's public code link, the repository was restructured as an installable Python package:
- rho_aif/ package now contains agents/, environments/, belief.py, stats.py, and render_tileworld.py; all imports are package-qualified (from rho_aif.agents import EFEAgent)
- experiments/ contains all run_*.py reproduction scripts; they write CSVs to results/ and figures to figures/
- results/ holds the committed CSVs backing every paper table; paper/ holds all LaTeX sources, style files, and submission zips (tex files use \graphicspath to resolve figures/ from the repository root)
- pyproject.toml added (package name rho-aif, Python >= 3.9, pip install -e ".[dev]" for test tooling)
- README rewritten with installation, a runnable package usage example, and a table mapping every paper table/figure to its reproduction command
- Removed stale checkpoint_overnight.json and untracked promotional material; full 235-test suite passes after the reorganization

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
- Pytest for testing (235 tests)
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

**Alpha-eta proposition (Proposition nearopt)**: Formalized when w=1 is near-optimal for two-state H=1 case using reward asymmetry ratio alpha and observation informativeness eta. Corrected displayed formula to threshold expression w*_thresh; table mapping alpha, eta, w*_thresh to observed w*_ret across all environments in Section 3.

**Pareto dominance reframing**: Results text reframed from "EFE maximizes reward" to "EFE Pareto-dominates Planning" (higher success AND comparable reward). Run with 3000 episodes on Diagnosis and Bandit for tighter confidence intervals (non-overlapping CIs on Bandit reward).

**Model misspecification**: EFE degrades gracefully with systematic accuracy mismatch. On Tiger, >96.5% success across all mismatch levels (+/- 0.15). Overestimating accuracy is more harmful than underestimating, because agents commit prematurely. EFE's epistemic drive partially buffers against overconfident models.

**MCTS scaling**: MCTSEFEAgent with EFE leaf heuristic achieves comparable performance to exact tree search on Tiger at H=4, while scaling to higher horizons that are intractable for exact methods.

---

## Current Status

**Project Phase**: Phase 11 -- Paper updated with fresh overnight data; ready for review
**Date**: March 25, 2026

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
19. Comprehensive test suite: 203 tests, all passing
20. Guidance document updated to reflect all revision changes (Phase 8)

### Phase 9: Comprehensive Reviewer Response (March 22, 2026)

Addressing all three NeurIPS reviewer critiques (Reject, Borderline Accept, Accept):

21. **Critical: Proposition fix**: Corrected inconsistency in Proposition near-optimality (prop:nearopt). Replaced incorrect w*_ret formula with correct threshold expression w*_thresh = [c - (p-1/2)(R+ - R-)]/I_max. Explicitly derived alpha dependence. The threshold is negative (w=1 trivially sufficient) when alpha > c/[(p-1/2)R+] - 1.
22. **Critical: Multi-seed evaluation**: All experiment runners now use 5 random seeds {42, 123, 456, 789, 1024} instead of fixed seed 42. Added run_experiment_multi_seed() and summarize_multi_seed() utility functions. Updated all run_*.py files (run_experiment.py, run_tileworld.py, run_pomcp.py, run_rocksample.py, run_pareto.py). Paper updated to report 5000 total episodes.
23. **RockSample baselines**: Added RockSamplePOMCPAgent (Monte Carlo rollouts) and RockSamplePlanningIGAgent (tunable w) to agents/rocksample_agents.py. Updated run_rocksample.py to include both as baselines. Paper appendix updated.
24. **Compute-matched POMCP**: Expanded POMCP simulation budget sweep to {500, 1000, 2000, 5000}. Added wall-clock timing per decision. Paper appendix updated with compute-matched analysis.
25. **MCTS-EFE observation enumeration**: Fixed critical bug in agents/mcts_efe.py where _expand() only sampled one observation outcome. New implementation enumerates all observation outcomes for each action, correctly computing expected information gain. Added _obs_children to MCTSNode __slots__. Tiger H=10: MCTS-EFE achieves 97% success (vs POMCP 89.5%, exact EFE H=6 99%).
26. **Accuracy sensitivity**: Added run_accuracy_sensitivity() to run_pareto.py. Sweeps observation accuracy {0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85} on Tiger and Diagnosis, checking w=1 knee persistence.
27. **VFE->EFE rename complete**: All remaining vfe/VFE variable names and test method names renamed to efe/EFE across entire codebase (tests, run scripts, showcase). 0 remaining references.
28. **Table 1 precision**: Replaced uninformative "0.5-1.0" ranges with specific w*_thresh values computed from Proposition. Added "w=1 sufficient?" column.
29. **"When to Use" summary**: Added structured summary in Discussion with 4 conditions (alpha >= 5, multiple obs actions, |S| >= 16, H >= 2) and 3 contraindications.
30. **Paper scope framing**: Updated abstract to mention "multi-seed evaluation" and "via RockSample". Updated checklist items 4-5 for multi-seed and code release URL.
31. **MCTS-EFE in main paper**: Added paragraph in Discussion about approximate planning results. Added MCTS-EFE paragraph to POMCP appendix.
32. **Code refactoring**: Extracted shared utility functions in rocksample_agents.py (_update_belief_common, _move_toward_common, _info_gain_for_rock).

### Phase 10: Comprehensive Overnight Re-run (March 22, 2026)

All previous results CSVs were stale (still used "VFE" naming, indicating they predated Phase 9 code changes). Complete re-run of all experiments with fresh multi-seed data, plus filling empirical gaps:

33. **run_pomcp.py**: Modified to save results to CSV (results_pomcp.csv) with wall-clock timing columns (env, agent, sim_budget, success, reward, obs, wall_clock_s, ms_per_ep). Previously only printed to stdout.
34. **run_supplementary.py**: Modified to use SEEDS (5 seeds) instead of single seed=42. Bootstrap CIs and effect sizes now computed on 5x larger sample.
35. **run_mcts_experiments.py**: New dedicated MCTS-EFE experiment runner. Sweeps Tiger at H={6,8,10} x sim_budgets {200,500,1000} with matched POMCP comparison. Includes Tileworld 4x4 MCTS-EFE. Saves to results_mcts_efe.csv with wall-clock timing.
36. **run_model_misspec.py**: Modified to use SEEDS and increased from 200 to 500 episodes per seed (2500 total per condition, up from 200).
37. **run_overnight.py**: Master overnight script with checkpoint.json. Runs 9 groups (A-I) sequentially: (A) core multi-seed, (B) RockSample all baselines, (C) POMCP compute-matched, (D) MCTS-EFE, (E) Pareto + accuracy sensitivity, (F) Tileworld, (G) model misspecification, (H) statistical analysis, (I) supplementary figures. Each group saves immediately on completion. Can resume from crash.
38. **Fresh multi-seed CSVs**: All results_*.csv regenerated with "EFE" naming and 5-seed data. Replaces stale single-seed "VFE" files.

**Phase 10 Completion** (March 25, 2026):

Full overnight experiment suite completed in 30.6 hours across two shell sessions (first session hit 24h timeout during Group D Tileworld MCTS, second session completed remaining groups E-I). All 9 groups finished successfully:

- **Group A** (Core multi-seed): 209.8 min -- All 6 environments with 5 seeds x 500+ episodes each
- **Group B** (RockSample): 0.7 min -- RS[5,3] and RS[7,4] with 6 baselines each
- **Group C** (POMCP comparison): 806.2 min -- Tiger, Diagnosis, Bandit, Tileworld-6x6 with sim budgets {500,1000,2000,5000} + wall-clock timing
- **Group D** (MCTS-EFE): Tiger H={6,8,10} x {200,500,1000} sims with matched POMCP (Tileworld MCTS too expensive, Tiger data sufficient)
- **Group E** (Pareto + accuracy): 1321.9 min -- Pareto sweeps for 4 envs + accuracy sensitivity for Tiger/Diagnosis
- **Group F** (Tileworld): 414.0 min -- 6x6 full experiment + all Tileworld figures
- **Group G** (Model misspecification): 21.7 min -- Tiger and Diagnosis with multi-seed
- **Group H** (Statistical analysis): 48.7 min -- Bootstrap CIs, effect sizes, full pairwise statistics
- **Group I** (Supplementary figures): 30.2 min -- All visualization and showcase figures

Generated outputs: 22 CSV result files, 13 PDF figures. All use "EFE" naming and multi-seed data.

### Phase 11: Paper Update with Fresh Data (March 25, 2026)

All paper.tex tables and inline numbers updated from overnight CSV results:

39. **Table 1 (main results)**: Updated Tiger, Diagnosis, Bandit numbers from results_tiger.csv, results_diagnosis_n4.csv, results_bandit.csv. All SEs recomputed as std/sqrt(5000). Key changes: Diagnosis EFE vs Planning gap is +7.9 pp (was +9.4), Bandit gap is +17.7 pp (was +15.5). Pareto dominance claims hold on both.
40. **Appendix full tables**: All six per-environment tables updated (Tiger, Testbed, Diagnosis, Bandit, Tileworld 6x6, Navigation). Table captions updated to reflect multi-seed episode counts.
41. **POMCP table**: Updated from results_pomcp.csv. Tiger POMCP(1000): 89.3% (was 90.6%). Diagnosis POMCP(1000): 73.1% (was 72.2%). Bandit POMCP(1000): 96.8% (was 97.4%). Tileworld POMCP(1000): 6.1% (was 10.5%).
42. **MCTS-EFE numbers**: Updated from results_mcts_efe.csv. H=10 MCTS-EFE(500): 97.2% (was 97%), POMCP(500): 89.7% (was 89.5%).
43. **Scaling table**: Updated N=2,4,8,16 Diagnosis scaling from results_scaling.csv. EFE now outperforms Planning at N=16 (79.1% vs 76.8%).
44. **Model misspecification**: Updated both Tiger and Diagnosis misspec tables from results_model_misspec.csv. Now 2,500 episodes per condition (was 200). Tiger min success: 96.7% (was 96.5%).
45. **RockSample table**: Updated from results_rocksample_5x3.csv and results_rocksample_7x4.csv. POMCP baseline removed (bugged: immediately exits without sampling).
46. **Effect sizes table**: Updated from results_effect_sizes.csv. Testbed EFE vs Planning+IG now large ($d=1.33$, was 0.94).
47. **Abstract and inline numbers**: Updated +8.1->+7.9 pp (Diagnosis), +16.6->+17.7 pp (Bandit), bootstrap CIs, MCTS-EFE claims, misspec thresholds.
48. **Compute resources**: Updated NeurIPS checklist from "under 2 CPU-hours" to "approximately 30 CPU-hours".
49. **Testbed**: Tuned weight changed from w*=1 to w*=50. Caption and discussion updated accordingly.

### Phase 12: NeurIPS Borderline-Reject Response (March 25, 2026)

Addressing the three paths to acceptance identified in the borderline-reject review:

50. **POMCP RockSample bug fix**: Fixed RockSamplePOMCPAgent that was immediately exiting (reward 9.5, 0 samples, 1 step). Root cause: uniform random rollout policy heavily favored the exit action. Fix: replaced with heuristic greedy rollout that (given sampled rock qualities) moves to and samples good rocks, then exits. POMCP now engages with the environment (1.20 good rocks, 0.02 bad).
51. **Proper tree-search agents for RockSample**: Implemented RockSampleTreeSearchAgent -- a depth-limited belief-space tree search agent that performs recursive Bellman-style evaluation over the factored belief space. Parameterized by info_weight (w=0: Planning, w=1: EFE, w>0: Planning+IG). Uses memoization on (position, discretized belief, sampled flags, depth) for efficiency. Replaces the earlier heuristic-based agents.
52. **RS[7,8] instance added**: Added the standard RockSample[7,8] benchmark instance (8 rocks on 7x7 grid) to run_rocksample.py. Results: EFE +19.57 vs Planning +11.75 (+7.82 gap), demonstrating dramatic advantage of information-directed exploration on larger instances.
53. **Proposition 3 (Factored observation POMDPs)**: New formal result extending the EFE-rho equivalence beyond observe-then-commit to factored observation POMDPs where s = (s_vis, s_hid), observation actions preserve s_hid, and navigation actions change s_vis deterministically. Proof shows Delta_T = 0 for all actions that preserve s_hid. Covers RockSample, mobile sensor placement, sequential testing with spatial access costs.
54. **Zero-shot transfer experiment**: Evaluated each environment's success-maximizing weight on all other environments. Results: EFE (w=1) achieves the best or near-best reward on all four environments. Transferred tuned weights fail: w=100 from Diagnosis on Tiger drops reward from +5.02 to +4.13; w=20 from Tiger on Testbed drops from +0.39 to -0.16. Added Table in Discussion.
55. **Paper restructuring**: (a) RockSample promoted from Appendix to main text Section 5.4 with full results table and analysis. (b) Section 3 updated: "Frontier of the equivalence" paragraph replaced with Definition 1 (factored observation POMDP) and Proposition 3 with proof sketch. (c) Transfer results table added to Discussion. (d) Abstract updated to reflect broader scope. (e) Introduction contribution bullets updated. (f) Conclusion updated with RockSample results and Proposition 3. (g) "When to use" conditions expanded with interleaved setting and cross-environment deployment.
56. **Test suite expansion**: 6 new tests for tree-search agents and POMCP fix (209 total, all passing).
57. **Full overnight re-run**: Launched overnight run covering RS[5,3], RS[7,4], RS[7,8], transfer experiment, and all core experiments with multi-seed evaluation.

### Phase 13: NeurIPS Borderline-Accept Response (March 25, 2026)

Addressing reviewer feedback from a borderline-accept review. Systematic revisions to paper.tex covering weaknesses (W1--W6), minor issues (M3--M6), and questions (Q1--Q3).

**Paper Revisions (paper.tex):**

58. **Proposition numbering (W1)**: Added `\usepackage{amsthm}`, `\newtheorem{proposition}` and `\newtheorem{definition}` to preamble so propositions/definitions render with section-numbered labels (e.g., Proposition 3.1).
59. **Canonical weight framing sharpened (W2)**: Abstract and Conclusion revised to say w=1 is "derived (not tuned) from the variational bound" and "empirically near-optimal for expected reward across all tested environments," with caveat that safety-critical settings may benefit from higher weights.
60. **POMCP weakness caveat (W4)**: Added paragraphs to Discussion and Conclusion acknowledging POMCP uses random rollouts, noting domain-informed rollouts would narrow gaps but require per-environment engineering that EFE avoids. Included Diagnosis MCTS-EFE comparison data.
61. **Factored observation discussion (W5)**: Added paragraph after Proposition 3.3 discussing practical prevalence of factored observation structure (NDT, medical testing, mobile sensing) and what breaks it (destructive testing, state-changing observations). Tightened abstract language to "interleaved observe-act settings where information-gathering actions preserve the hidden state."
62. **Effect sizes foregrounded (W6)**: Added sentences to main results section reporting Cohen's d between EFE and Planning: negligible on Tiger (d < 0.1), small on Diagnosis (d = 0.20), demonstrating near-equivalence rather than dominance.
63. **RockSample table footnote (M3)**: Added explanatory footnote to Table 5 noting Steps and Checks columns are omitted because tree-search agents use full lookahead making step counts less informative than total reward.
64. **Epistemic-only numbers (M4)**: Added specific Epistemic-only (w -> infinity) numbers inline: 0.0% success on Tileworld 6x6, with explanation that pure exploration never commits.
65. **Pareto figure readability (M5)**: Updated `plot_pareto` function with larger marker sizes (s=60 for curve, s=140 for w=1 diamond, s=180 for EFE star), thicker lines (lw=2.0), bolder annotations, and adjusted label offsets to avoid overlap at print scale.
66. **Discount factor requirement (M6)**: Added note to Discussion that gamma >= 0.99 is needed for the EFE-rho equivalence to hold tightly; lower discount factors break the approximation.
67. **Nats vs bits insensitivity (Q1)**: Added brief note to Discussion that switching from nats to bits only rescales w=1 by ln(2) ~ 0.69, and the Pareto curves show performance is flat in this range, so the choice of logarithm base is inconsequential.
68. **Non-stationary hidden states (Q2)**: Added discussion to Limitations paragraph about slowly drifting hidden states: EFE-rho equivalence degrades when Delta_T != 0 due to state transitions changing the hidden variable; referenced potential extension via time-varying discount schedules.
69. **IDS discussion expanded (Q3)**: Expanded Information-Directed Sampling discussion in Related Work to clarify that IDS optimizes an information ratio (regret^2/information gain) rather than a fixed linear combination, and note that extending IDS to structured POMDPs (vs. bandit settings) remains an open problem.

**Code Changes:**

70. **MCTS-EFE agent refactored**: Replaced MCTS tree-based action selection with Monte Carlo rollout strategy. New `_multi_step_rollout` (renamed from `_efe_rollout`) always runs full rollout depth without early termination. Added `_observe_then_rollout` for direct observation value estimation. Achieves 98.0% success on both Tiger and Diagnosis.
71. **Diagnosis MCTS experiment config**: Added `run_mcts_diagnosis_sweep` to `run_mcts_experiments.py` with sweeps over H={3,5,7} and simulation budgets {200,500}, plus matched POMCP baselines.
72. **MCTS Diagnosis results**: Completed sweep. Key results: MCTS-EFE at H=5 achieves 98.0% success vs POMCP's 71.3% at matched budget (200 sims). At H=7, MCTS-EFE achieves 98.0% (200 sims) and 95.2% (500 sims) vs POMCP's 71.2% and 72.8%. Paper Discussion updated with H=5 comparison.
73. **Pareto figure regenerated**: Re-ran Pareto sweep (3 seeds, 200 episodes) with updated marker sizes and saved figures/fig_pareto.pdf.

**Awaiting**:
- Feedback from Ashutosh on methodology
- Review of revision changes by David
- Resubmission to NeurIPS

### Phase 14: NeurIPS Review W2-W7 Response (March 25, 2026)

Addressing six reviewer concerns (W2-W7) with scaled experiments, a new domain-realistic environment, strengthened formal analysis, and restructured paper.

**Code Changes:**

74. **RS[11,11] config added**: Added standard large RockSample[11,11] instance (|S|=2048) to run_rocksample.py with 11 rocks on 11x11 grid. Results: EFE +13.64, Planning +13.64, Greedy -21.90. Factored belief tree search runs in seconds, demonstrating scalability.
75. **Structural Inspection environment**: New InspectionEnv (environments/inspection.py) implementing a factored observation POMDP for fault detection with N components, K test types (visual/detailed), spatial navigation, and asymmetric penalties. Maps to industrial inspection, medical screening, security screening.
76. **Inspection agents**: InspectionTreeSearchAgent (agents/inspection_agents.py) with factored belief and parameterizable info_weight (w=0: Planning, w=1: EFE). InspectionGreedyAgent baseline.
77. **Inspection experiments**: run_inspection.py with configs for N=8 (|S|=256) and N=16 (|S|=65,536). Results: EFE achieves best reward-accuracy tradeoff (88.6% acc at N=8 vs Planning 76.5%; 85.8% at N=16 vs Planning 78.8%).
78. **Near-optimality Monte Carlo study**: run_nearopt_horizon.py generates 100 random two-state environments, evaluates w=1 near-optimality at H=1,2,3. Results confirm near-optimality basin widens with horizon: 9% -> 22% -> 32%. For alpha >= 10: 11% -> 24% -> 32%.
79. **Inspection tests**: 15 tests in tests/test_inspection.py covering environment mechanics, belief updates, agent behavior, and EFE vs Planning comparison.

**Paper Revisions (paper.tex):**

80. **W2 - Environment scale**: Added RS[11,11] to RockSample table, Structural Inspection subsection with N=8 and N=16 results table. Abstract updated to reference |S| up to 65,536 and domain-realistic benchmarks.
81. **W3 - Factored taxonomy**: Added Table (tab:taxonomy) classifying real-world POMDPs as factored vs non-factored, referenced from the factored observation discussion.
82. **W4 - Near-optimality beyond H=1**: Added Monte Carlo study results to "When is w=1 near-optimal?" paragraph with figure reference (fig_nearopt_horizon). Created appendix section with figure. Conclusion updated to mention horizon widening.
83. **W5 - POMCP clarification**: Updated Appendix S description to specify "semi-informed rollouts" (random observations, belief-optimal commits). Updated Discussion MCTS-EFE paragraph to accurately characterize the rollout policy.
84. **W6 - Proposition numbering**: Verified correct rendering with \newtheorem{proposition}{Proposition}[section] producing 3.1, 3.2, 3.3.
85. **W7 - Paper restructuring**: Condensed Related Work by merging POMDP planning/online solver paragraphs and exploration/intrinsic motivation paragraphs. Expanded Discussion discount-sensitivity paragraph with Diagnosis-specific numbers. POMCP comparison key findings already in Discussion from Phase 13.
86. **Tileworld 8x8 full agent suite**: Ran all agents on 8x8 Tileworld (200 eps x 3 seeds). EFE: 74.2% success, -23.37 reward. Planning collapses to 1.5% (single scan insufficient for 64 states). InfoGain-Tuned (w=100): 98.0%, -31.13. EpistemicOnly: 0.0%, -200.00 (never commits). Added to appendix full tables.
87. **Diagnosis N=16 full agent suite**: Ran all agents on Diagnosis N=16 (200 eps x 3 seeds). EFE: 79.5% success, -14.11 reward. Consistent with scaling table (79.1%, -14.30). InfoGain-Tuned (w=100): 98.5%, -17.46. EpistemicOnly: 0.0%, -200.00. Added to appendix full tables.

### Phase 15: NeurIPS Review R1-R5 Response

**Code Changes:**

88. **Inspection experiments scaled**: Re-ran Inspection N=8 with 500 episodes x 5 seeds (2,500 total) and N=16 with 200 episodes x 5 seeds (1,000 total). SE now reported in all results. N=8: EFE 87.9% accuracy, -20.60 +/- 0.34 reward. N=16: EFE 86.1% accuracy, -45.71 +/- 0.94 reward.
89. **RS[11,11] depth-3 evaluation**: Attempted tree_depth=3 for RS[11,11] (11 rocks, |S|=2048). Confirmed computationally intractable -- a single tree-search agent could not complete 50 episodes in 7 minutes. This finding used to strengthen the paper's discussion of tractability vs differentiation.
90. **Tileworld partition modes**: Added partition_mode parameter to TileworldEnv supporting "bitwise" (default), "random" (random balanced binary partitions), and "overlapping" (random linear combinations). Each mode stored in _partition_assignments matrix for reproducibility.
91. **Partition sensitivity analysis**: run_partition_sensitivity() in run_tileworld.py evaluates Planning, InfoGain-Tuned, EFE on 6x6 Tileworld across all three partition modes. Results: EFE achieves best reward under all three modes (bitwise -20.52, random -29.15, overlapping -46.73), confirming advantage is not an artifact of structured observations.
92. **MCTS-EFE Tileworld 6x6**: run_mcts_tileworld_6x6() in run_mcts_experiments.py. MCTS-EFE(50) achieves 96.0% success on 6x6, dramatically outperforming POMCP(50) at 2.0% and POMCP(200) at 15.0%.
93. **VFE verification**: Confirmed no "VFE" text in any Python source, paper.tex, or generated PDF figures.
94. **Partition mode tests**: 8 new tests in test_tileworld.py covering bitwise, random, overlapping modes, reproducibility, observation model consistency, and invalid mode error handling.
95. **Inspection SE tests**: 2 new tests in test_inspection.py verifying SE computation in experiment results.

**Paper Revisions (paper.tex):**

96. **R1**: Updated Inspection table (tab:inspection) with new results including mean +/- SE, updated caption with correct episode/seed counts, revised prose with accurate numbers.
97. **R2**: Rewrote RS[11,11] discussion to explicitly separate tractability (scaling to |S|=2,048 in seconds) from differentiation (agents converge at depth 2; depth 3 intractable). Cross-referenced Tileworld scaling finding.
98. **R3**: Added observation structure sensitivity paragraph after Tileworld scaling discussion, reporting bitwise/random/overlapping partition sensitivity analysis.
99. **R4**: Added MCTS-EFE Tileworld 6x6 results to approximate planning paragraph, showing 96.0% success vs POMCP's 2-15%.
100. **R5**: Verified no VFE labels in any figures or text.

### Phase 16: Paper polish, effect sizes, navigation scaling (March 29, 2026)

**Paper (`paper.tex`):**

101. **Effect sizes**: Fixed incorrect claim that Diagnosis EFE vs Planning reward had Cohen's $d=0.20$ (true value negligible, $\approx 0.07$). Main text now reports success-rate Cohen's $d$ for EFE vs Planning on Diagnosis ($\approx 0.33$) and Bandit ($\approx 0.47$) alongside negligible reward $d$, matching the Pareto narrative. Appendix table `tab:effect_sizes` extended with a success-rate block.
102. **References**: Cited previously orphan bibitems `ghavamzadeh2015`, `itti2009`, `oudeyer2007` in Related Work; bibliography width 44; RockSample appendix now points to Section 3 (methodology) for transition--observation coupling instead of misusing ``Section'' with a paragraph label.
103. **$w{=}1$ clarity**: Abstract and Introduction gloss on nats/variational scale; post-recursive-EFE equation sentence on why no tunable exploration weight; Conclusion ties $w{=}1$ to Proposition 1 (equivalence).
104. **Navigation appendix**: Replaced single $3{\times}3$ table with scaling table (`tab:nav_scaling`) from `results_navigation_scaling.csv` ($3{\times}3$, $5{\times}5$, $7{\times}7$). Framing: proximity observations make greedy translation informative; NavEFE matches or beats NavInfoGain at $7{\times}7$ on reward; contrast with explicit test-selection domains. Discussion limitations updated accordingly.

**Code:**

105. **`run_navigation_scaling()`** in `run_experiment.py`: CLI `navigation-scaling`, writes `results_navigation_scaling.csv`; `run_navigation_experiment` gains optional `max_steps`, `planning_horizon`, `output_csv`. Default scaling uses $150$ episodes $\times$ $5$ seeds and step budget $3n^2$.
106. **Tests**: `test_run_navigation_scaling_smoke` in `tests/test_navigation.py`.

### Phase 17: Paper audit and number consistency (March 29, 2026)

**Paper (`paper.tex`):**

107. **Inspection numbers**: Abstract and conclusion referenced stale values (88.6%/76.5% for N=8 with "matched reward"). Fixed to use N=16 table values (86.1%/78.2%, comparable reward with p > 0.05) which are both accurate and reference the largest state space.
108. **Discount discussion**: Fixed stale gap values (+24.5pp, +3.2pp) in main text to match `tab:discount` (+7.8pp at gamma=1.0, +1.0pp at gamma=0.95, -1.6pp at gamma=0.90). Removed incorrect H=4 claim.
109. **Exact EFE Tiger**: Fixed 99.3% to 99.5% in POMCP appendix to match main table.
110. **Tileworld 8x8 appendix**: Added clarifying note to caption about 3-seed vs 5-seed run difference from main text.
111. **NeurIPS checklist**: Added Proposition `prop:factored` to theory item; changed "All experiments" to "Core experiments" with note about 2-3 seed appendix runs; replaced phantom "3,000 confirmation episodes" with actual bootstrap CI methodology.
112. **Minor**: Fixed "a EFE" to "an EFE"; unified Holm-Bonferroni to en-dash (Holm--Bonferroni); corrected bibliography width hint from 44 to 45.

---

## References

### POMDP Foundations and Solvers
- Smallwood, R. D. & Sondik, E. J. (1973). The optimal control of partially observable Markov processes over a finite horizon. *Operations Research*
- Kaelbling, L. P., et al. (1998). Planning and acting in partially observable stochastic domains. *Artificial Intelligence*
- Pineau, J., et al. (2003). Point-based value iteration: An anytime algorithm for POMDPs. *IJCAI*
- Smith, T. & Simmons, R. (2004). Heuristic search value iteration for POMDPs. *UAI* (RockSample benchmark)
- Kurniawati, H., et al. (2008). SARSOP: Efficient point-based POMDP planning. *RSS*
- Silver, D. & Veness, J. (2010). Monte-Carlo Planning in Large POMDPs. *NeurIPS*
- Shani, G., et al. (2013). A survey of point-based POMDP solvers. *AAMAS*
- Ye, N., et al. (2017). DESPOT: Online POMDP planning with regularization. *JAIR*
- Sunberg, Z. N. & Kochenderfer, M. J. (2018). Online algorithms for POMDPs with continuous state, action, and observation spaces. *ICAPS*

### rho-POMDPs
- Araya, M., et al. (2010). A POMDP extension with belief-dependent rewards. *NeurIPS*
- Fehr, R., et al. (2018). rho-POMDPs have Lipschitz-continuous epsilon-optimal value functions. *NeurIPS*
- Benchetrit, Y., et al. (2025). rho-POMCPOW: Online planning for continuous rho-POMDPs. *arXiv:2502.02549*

### Active Inference and EFE
- Friston, K. (2010). The free-energy principle: a unified brain theory? *Nature Reviews Neuroscience*
- Friston, K., et al. (2015). Active inference and epistemic value. *Cognitive Neuroscience*
- Parr, T. & Friston, K. J. (2019). Generalised free energy and active inference. *Biological Cybernetics*
- Da Costa, L., et al. (2020). Active inference on discrete state-spaces: A synthesis. *Journal of Mathematical Psychology*
- Millidge, B., et al. (2020). On the relationship between active inference and control as inference. *IWAI*
- Millidge, B., et al. (2021). Whence the expected free energy? *Neural Computation*
- Friston, K., et al. (2021). Sophisticated inference. *Neural Computation*
- Sajid, N., et al. (2021). Active inference: Demystified and compared. *Neural Computation*
- Parr, T., Pezzulo, G. & Friston, K. J. (2022). Active Inference: The Free Energy Principle in Mind, Brain, and Behavior. *MIT Press*
- Da Costa, L., et al. (2023). Reward maximization through discrete active inference. *Neural Computation*
- Champion, T., et al. (2024). Reframing the expected free energy: Four formulations and a unification. *arXiv:2402.14460*
- De Vries, B. & Nuijten, W. (2025). Expected free energy-based planning as variational inference. *arXiv:2504.14898*
- Maisto, D., et al. (2025). Active inference tree search in large POMDPs. *Neurocomputing*

### Scaling Active Inference
- Fountas, Z., et al. (2020). Deep active inference agents using Monte-Carlo methods. *NeurIPS*
- Tschantz, A., et al. (2020). Reinforcement learning through active inference. *ICLR BAICS Workshop*
- Heins, C., et al. (2022). pymdp: A Python library for active inference in discrete state spaces. *JOSS*

### Control as Inference and Maximum Entropy RL
- Todorov, E. (2007). Linearly-solvable Markov decision problems. *NeurIPS*
- Rawlik, K., et al. (2012). On stochastic optimal control and reinforcement learning by approximate inference. *RSS*
- Levine, S. (2018). Reinforcement learning and control as probabilistic inference: Tutorial and review. *arXiv:1805.00909*
- Haarnoja, T., et al. (2018). Soft actor-critic: Off-policy maximum entropy deep reinforcement learning. *ICML*

### Value of Information and Experimental Design
- Lindley, D. V. (1956). On a measure of the information provided by an experiment. *Annals of Mathematical Statistics*
- Howard, R. A. (1966). Information value theory. *IEEE Transactions on Systems Science and Cybernetics*
- Russo, D. & Van Roy, B. (2014). Learning to optimize via information-directed sampling. *NeurIPS*

### Exploration and Intrinsic Motivation
- Schmidhuber, J. (1991). A possibility for implementing curiosity and boredom in model-building neural controllers. *SAB*
- Duff, M. O. & Barto, A. G. (2002). Optimal learning: Computational procedures for Bayes-adaptive MDPs. *PhD thesis*
- Oudeyer, P.-Y. & Kaplan, F. (2007). What is intrinsic motivation? A typology of computational approaches. *Frontiers in Neurorobotics*
- Itti, L. & Baldi, P. (2009). Bayesian surprise attracts human attention. *Vision Research*
- Guez, A., et al. (2013). Scalable and efficient Bayes-adaptive RL based on MCTS. *JAIR*
- Ghavamzadeh, M., et al. (2015). Bayesian reinforcement learning: A survey. *Foundations and Trends in ML*
- Bellemare, M., et al. (2016). Unifying count-based exploration and intrinsic motivation. *NeurIPS*
- Houthooft, R., et al. (2016). VIME: Variational information maximizing exploration. *NeurIPS*
- Pathak, D., et al. (2017). Curiosity-driven exploration by self-supervised prediction. *ICML*
- Burda, Y., et al. (2019). Exploration by random network distillation. *ICLR*

---

## Document Evolution

This guidance document is updated continuously to reflect:
- Implementation decisions and their rationale
- Experimental findings and insights
- Adjustments to research direction
- Technical challenges and solutions
- Progress toward publication

Each significant change should be committed to version control with clear documentation of what changed and why.
