# Research Plan and Guidance Document

## Project: rho-POMDP Active Inference Framework

**Last Updated**: July 20, 2026  
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
- Figure 12 fix (July 2026): fig_nearopt_horizon.pdf had a hardcoded y-axis floor (ylim 40-102) that clipped all data below 40%, rendering the plot essentially blank, and a LaTeX-escaped percent sign in the y-label that printed a literal backslash; regenerated with ylim 0-102, corrected label, and legend moved to upper left. The stale figure also predated the current CSV: the Monte Carlo study was rerun with the paper's stated configuration (100 environments, H in {1,2,3}) and the near-optimality numbers updated in all four tex files (overall 11% -> 21% -> 38%; alpha >= 10: 14% -> 19% -> 37%), replacing the old 9%/22%/32% figures
- Final polish (July 2026): removed the last italics from prose (definitional emphasis included; the only remaining italics are class-driven theorem/definition/heading styling and bibliography venue names) and re-merged over-fragmented paragraphs (canonical weight and MCTS-EFE fairness note rejoined, conclusion consolidated to two paragraphs with the practitioner message folded in); applied identically to paper_arxiv.tex, paper_iwai2026.tex, and paper.tex
- Clarity pass (July 2026): clarified vague antecedents (what fixes the weight in the intro), glossed jargon at first use (nats, PWLC), restructured the contribution list under Theory/Evidence/Practical guidance labels, added topic sentences, and broke the five longest paragraphs (core results, canonical weight, MCTS-EFE, limitations, conclusion) into readable units; applied identically to paper_arxiv.tex, paper_iwai2026.tex, and paper.tex
- Prose style pass (July 2026): removed all prose semicolons (~50) and rhetorical italics (~30) from abstract, main text, captions, and appendices, keeping only definitional first-use italics (observe-then-commit, factored observation POMDP, sophisticated inference, value of information) and bibliography venue names; broke up long sentences for varied rhythm; added explicit relevance statements (near-optimality discussion and conclusion now state directly that in high-asymmetry domains like medical diagnosis and fault detection the weight deploys with no per-task search); applied identically to paper_arxiv.tex, paper_iwai2026.tex, and paper.tex
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

## Phase: IWAI 2026 review response

**Status**: Implemented (July 20, 2026)  
**Date**: July 20, 2026

Full response to IWAI reviews (uscY, ieKV, NbgT) across all four LaTeX versions and supporting code/experiments.

### Theory and claims
1. **Prop.~2 thresholds** — `experiments/run_thresholds.py` regenerates `results/results_thresholds.csv`. Corrected Tiger/Diagnosis thresholds ($\approx -138.7$, $\approx -88.2$ nats). Added upper over-observation threshold $w^*_{\mathrm{hi}}$; Bandit dropped from two-state table; Testbed over-exploration explained via proximity to $w^*_{\mathrm{hi}}\approx 1.01$.
2. **Reward–nats calibration** — Explicit $\beta{=}1$ per reward unit; keeping $w$ fixed while scaling rewards by $k$ rescales effective weight by $1/k$ (equivalently $w^*_{\mathrm{ret}}(k)\propto k$); Bernardo (1979) log-scoring exactness; bits vs nats noted.
3. **Prop.~1 positioning** — Corollary/notational bridge of Da Costa et al. sophisticated-inference Bellman optimality; deterministic tie-break shared with Planning+IG($w{=}1$).
4. **Softened $w{=}1$ language** — Derived relative coefficient; exact under log scoring; robust default under shared reward convention; not scale-invariant.
5. **Over-claim fixes** — Pareto-dominates restricted to Diagnosis/Bandit vs Planning; Inspection/RS bolding honest; Diagnosis EFE $-1.52$.

### New experiments
6. **Reward rescaling** — `experiments/run_reward_scaling.py`, `figures/fig_reward_scaling.pdf`, Appendix `app:reward_scaling`. Bandit $w^*_{\mathrm{ret}}$ tracks $k$ exactly ($0.1,1,10$).
7. **IDS baseline** — `rho_aif/agents/ids.py`, `experiments/run_ids.py`, Appendix `app:ids`. IDS competitive on Tiger; over-explores on Diagnosis/Bandit relative to EFE.
8. **Reward-tuned transfer** — `experiments/run_transfer.py` reports $w^*_{\mathrm{ret}}$ and $w^*_{\mathrm{succ}}$. Success-tuned transfer harms reward; moderate reward-tuned weights transfer better; $w{=}1$ remains a robust default.
9. **Seed-level stats** — `rho_aif/stats.py`: `seed_level_ttest`, `hierarchical_bootstrap_ci`; documented in stats appendix.

### Citations and clarity
10. Bernardo 1979; Spaan et al. 2015 (POMDP-IR); Satsangi et al. 2018; Walraven et al. 2024.
11. Tuning criterion stated; Greedy defined; Myopic instrumental VoI explained.

- **Prose tightening (July 20, 2026, evening).** A cross-version style pass removed prose semicolons (math `\;` kept), prose `\emph`/`\textbf` (table-cell best-metric bold and "Bold: best" legends retained), and one-sentence fragment paragraphs; the abstract was rewritten as a lean narrative (not results-stuffed) with varied sentence rhythm; Broader impact was merged into Limitations; contribution and discussion itemize labels were unbolded. Changes originated in `paper_arxiv.tex` and were propagated analogously to `paper.tex` (NeurIPS; plain `Keywords:`), `paper_iwai2026.tex` (shared prose aligned with arxiv, anonymity preserved), and `paper_iwai2026_abridged.tex` (same style and lean abstract, without expanding length).

### OpenReview camera-ready author responses (July 20, 2026)

Post-decision replies for IWAI 2026 submission #4 (Accept: Poster + Spotlight). Paste into OpenReview as replies under each review. All promised revisions are already implemented in the working sources and will ship in the camera-ready PDF.

#### Note to Program Chairs

We thank the chairs and reviewers. The camera-ready repositions the w=1 claim (derived coefficient under a shared reward convention, exact under log scoring, not scale-invariant), corrects the Proposition 2 thresholds, makes headline comparisons and bolding honest against tuned Planning+IG, adds the missing citations plus an IDS baseline and a reward-rescaling experiment, and links public code.

#### Reviewer NbgT

Thank you for the Accept and the fair critique. Camera-ready: we reposition w=1 as a derived relative coefficient (exact under log scoring, Bernardo 1979) rather than canonical, present Proposition 1 as a corollary of Da Costa et al.'s Bellman result, and add an IDS baseline (competitive on Tiger, over-explores on Diagnosis/Bandit). SARSOP/POMCPOW remain future work rather than cited-as-run. Public code accompanies the final version.

#### Reviewer uscY

Thank you for an exceptionally precise review. You are right on the central point: identifying reward with the pragmatic term fixes beta implicitly, so w=1 is not scale-invariant. The camera-ready drops the canonical/automatically-calibrated language, states beta=1 per reward unit, cites Bernardo (1979), and adds a rescaling experiment confirming w*_ret(k) proportional to k. We restate the conclusion as yours: moderate untuned weights are robust within a shared reward convention, and success-tuned weights overfit.

Concrete fixes: Table 1 thresholds were wrong and are regenerated from code (Tiger −138.7, Diagnosis −88.2 nats), with an added over-observation bound; Diagnosis EFE is unified to −1.52; a shared tie-break makes the Figure 1 star and diamond coincide as Proposition 1 requires; bolding and Pareto-domination claims are restricted to where the tables support them; tuning criteria (w*_ret vs w*_succ) are stated everywhere, and the transfer table reports both. Greedy and Myopic are defined, missing details filled in, and Spaan, Satsangi, Walraven, and Bernardo are cited with repositioning against POMDP-IR. Code is released.

#### Reviewer ieKV

Thank you for the clear revision requirements, which we adopt in full. (1) Calibration: we state the exp(beta R) identification with beta=1 per reward unit, acknowledge non-invariance to reward rescaling, cite Bernardo (1979), and add a rescaling sweep confirming w*_ret scales with k. (2) Reproducibility: Table 1 is corrected to the formula's values (−138.7, −88.2 nats) and regenerated from a public script, and every tuned weight is labeled reward- or success-tuned, resolving the Table 1 vs Table 2 discrepancy. (3) Headlines: comparisons are drawn against tuned Planning+IG, non-EFE winners are bolded, and Pareto-domination is restricted to Diagnosis/Bandit versus same-horizon Planning. The transfer table now includes reward-tuned weights alongside success-tuned ones.

### Citation audit (July 20, 2026)

All 49 bibliography entries across the four paper variants were verified against the published record. Three corrections were applied to every variant containing the affected entries:

1. **duff2002** — the PhD thesis "Optimal learning: Computational procedures for Bayes-adaptive Markov decision processes" (UMass Amherst, 2002) is single-authored by M. O. Duff (Barto was the advisor, not a coauthor). Author list and label corrected from "Duff and Barto" to "Duff".
2. **millidge2020** — the IWAI 2020 paper "On the Relationship Between Active Inference and Control as Inference" has four authors: Millidge, Tschantz, Seth, and Buckley. Seth was missing and has been added. The in-text claim that the paper "proved formal equivalence" was overstated (the paper provides a formal comparison and shows the frameworks differ in how value is encoded); the sentence was corrected in the three full variants.
3. **walraven2024** — the journal's version of record is Autonomous Agents and Multi-Agent Systems 39(1), article 3, 2025 (published online November 2024). Year and issue number corrected; the citation key is unchanged.

All remaining entries (venues, volumes, page ranges, author lists, arXiv identifiers) were confirmed accurate, including the recently updated champion2024 entry (Neural Computation 38(3):439–469, 2026) and benchetrit2025 (arXiv:2502.02549). All four variants recompile cleanly and the three submission zips were refreshed with the corrected sources.

## Phase: Inspection Benchmark Release (July 22, 2026)

**Status**: Code and release prep implemented; public PyPI publish deferred to next venue submission  
**Goal**: Publish `rho-aif` as a pip-installable benchmark for information-gathering planning (Structural Inspection + observe-then-commit suite), with proper scoring rules as the new capability.

### Delivered (code / release prep done)
1. **MIT LICENSE** — replaces informal "academic use" wording; `pyproject.toml` license/classifiers updated.
2. **Public API** — `InspectionEnv` and `POMCPAgent` exported; `rho_aif/benchmark.py` holds canonical configs (`Tiger`, `Diagnosis`, `Bandit`, `Tileworld-6x6`, `Inspection-N8`, `Inspection-N16`), seeds, and runners.
3. **Scoring rules** — `rho_aif/scoring.py` (log score, Brier score; factored variants for inspection). Wired into `EpisodeResult` / `summarize_results` and the inspection runner (`mean_log_score`, `mean_brier`).
4. **CLI** — console script `rho-aif-bench` (`list`, `run --env ... --agent ...`).
5. **Docs / CI** — README rewritten as benchmark quickstart; GitHub Actions for pytest (3.9–3.12) and sdist/wheel build.
6. **Tests** — `test_scoring.py`, `test_benchmark.py`, `test_cli.py`; full suite 275 passed.
7. **Local packaging** — `python -m build` produces sdist/wheel; `twine check` passed; local tag `v1.0.0` on commit `bf81000`.

### Out of scope (v1)
Per-test VoI audit records, SARSOP/POMCPOW baselines, public leaderboard, RockSample as a headline track (remains research code).

### Deferred until next venue submission
Public TestPyPI verification and PyPI upload of `rho-aif` are **not** a free-floating someday task. They are a required item on the next-paper submission checklist (alongside uploading the paper PDF / OpenReview / journal portal). Do this when preparing that submission so the camera-ready or preprint can cite a stable `pip install rho-aif` URL.

```bash
python -m build
twine upload --repository testpypi dist/*
# verify in a clean venv:
#   pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple rho-aif
#   rho-aif-bench list
twine upload dist/*
git push origin main --tags
```

### Next-venue submission checklist (package)
- [ ] Rebuild and `twine check` the current tree
- [ ] Upload to TestPyPI and verify `pip install` + `rho-aif-bench list` in a clean venv
- [ ] Upload to PyPI (`rho-aif`)
- [ ] Push `main` and tag `v1.0.0` (or bump version if the tree has moved on)
- [ ] Point the next-venue paper / README install instructions at the live PyPI package

## Phase: Price of Information (July 22–23, 2026)

**Status**: Presentation fixes complete; three headline claims HOLD with interval-valued framing; first paper draft at `paper/price_of_information.tex`  
**Goal**: Recast the Planning+IG weight `w` as an operational shadow price of a sensing budget `B`, with offline solve and online dual control. Theory notes: `Guidance_Documents/price_of_information.md`.

### Delivered
1. **Theory notes** — budgeted rho-POMDP, information-floor dual vs sensing-budget operational inverse, Prop 2 boundary reading, SAC-style dual control. Citations verified (Sims 2003; Matějka and McKay 2015; Haarnoja et al. 2018 arXiv:1812.05905; Altman 1999 CMDPs).
2. **`rho_aif/budget.py`** — `estimate_usage_curve` with per-seed SEs, `crossing_bracket` (set-valued shadow price), `solve_shadow_price_from_curve` step brackets, `identifiable_budgets`.
3. **`DualWeightAgent`** — projected update with optional `lr_decay` and Polyak `w_avg`.
4. **Upgraded experiments** — curve-collapse scale test with interval brackets; refined Prop 2 onset brackets; powered staircases; dual with decay + mid-run rescale; `--replot` path.
5. **Paper draft** — `paper/price_of_information.tex` (LLNCS), three core figures.
6. **Tests** — full suite **301 passed**.

### Protocol upgrades (after quick battery failed; then presentation fixes)
- **Scale**: plot `U` vs `w/α` (curve collapse); right panel is the **crossing bracket in `w/α`**, not point `w*` (B=8 sits in a usage gap).
- **Prop 2**: positive-threshold Testbeds; refined grid near threshold; report onset bracket `(last U≈0, first U>0.5]`.
- **Curves**: dense grid, 5 seeds × 100 episodes (OTC); identifiable budgets; staircase + brackets.
- **Dual**: `lr0=0.05`, decay `0.02`, 400 episodes; windowed raw `w` ratio; shaded crossing-bracket band (not point `curve w*`).

### Full-battery verdicts (`--mode full`, 5 seeds × 100 episodes; presentation fix 2026-07-22)
| Claim | Verdict | Evidence |
|---|---|---|
| Curve collapse | **HOLD** | Diagnosis/Bandit: 100% matched `w/α` points within 2·SE; max spread ≤0.48. Crossing brackets in `w/α` **coincide** across α∈{0.1,1,10} (Diagnosis `(0.141,0.323]`, Bandit `(3.84,8.76]`). |
| Prop 2 onset | **HOLD** | Refined grid: both Testbeds onset in `(w_thresh, 1.03·w_thresh]` (upper rel 3%). `U=0` at and below threshold. |
| Dual rescale | **HOLD** | Usage pinned at 8.1 both halves. Windowed `w` 0.29 → 2.71 after ×10 rescale (ratio **9.3 ≈ 10**). Re-adaptation **157 → 45** with lr reset-on-shift (reset at ep 217). |
| Shadow staircases | **PARTIAL** | Bandit/Inspection roughly monotone; Tiger/Diagnosis/Tileworld local non-monotonicity — report brackets+SEs. |

Implicit EFE budgets `B_EFE=U(w=1)`: Tiger 4.21±0.07, Diagnosis 9.68±0.15, Bandit 5.03±0.17, Tileworld-6x6 14.83±0.22, Inspection-N8 18.24±0.19.

Artifacts: `results/results_price_*.csv`, `results/results_price_of_information_summary.json`, `figures/price_*.{png,pdf}`, `paper/price_of_information.tex`.

### Design notes forced by data
- `U(w)` is only roughly monotone; default solver is log-grid + step brackets with SEs.
- Budgets below `U(0)` are unachievable with nonnegative `w` (instrumental sensing).
- Gap budgets make `w*` set-valued; report `crossing_bracket`, not a single argmin.
- Environments have a usage ceiling `U_max` (belief saturation / episode caps).
- H=1 Prop 2 closed form predicts zero observing for `w ≤ w_thresh`; multi-step onset is just above (3% after grid refinement; previously 32% was a coarse-grid artifact).
- Dual lr decay stabilizes the steady state but slows re-adaptation after reward rescale; lr reset-on-shift (window=20, k=3) recovers in 45 vs 157 episodes.

### Still open
- [ ] Optional: cost-usage (`usage_kind='cost'`) curves alongside count usage
- [x] Full battery confirms the scale story
- [x] Presentation fixes (interval brackets, Prop 2 refinement, dual band)
- [x] Start paper draft (`paper/price_of_information.tex`)
- [x] LR reset-on-shift experiment (157→45 re-adaptation; figure `price_dual_reset`)
- [ ] Revise / expand paper draft toward a submission venue → superseded by the Full-Length Paper phase below

## Phase: Full-Length Paper (July 23, 2026 –)

**Status**: Stages A–H complete (propositions, interleaved curves, multi-seed dual, cost budgets, collapse breadth, SARSOP baseline, w* atlas, distractor robustness, targeted scientific additions, related-work positioning, and paper assembly), verdicts HOLD (Tileworld collapse PARTIAL, explained as budget-at-knot noise); Stage G2 verdict DONE; `paper/full_paper.tex` assembled and compiling; only Stage I (venue gate, submission checklist, anonymized-repo work — explicitly deferred) remains open

### Review feedback folded in (July 23, 2026)
NeurIPS 2026 submission 30092 reviews (three rejects plus PAT automated feedback) were mapped point-by-point into a review-response ledger — `full_paper_plan.md` Section 8. Highlights: the universal w=1 scale objection is exactly the pivot this phase already made (PI-1, shadow price), and the requested reward-scale sensitivity sweep was already run at full power (Stage E); the five citation errors Reviewer vnDs flagged were verified as already fixed in the current tex sources, with two residues (prose still misnames Benchetrit et al. as "rho-POMCPOW"; Gymnasium used but uncited — Towers et al. 2024 verified). New work items: Stage G2 distractor-robustness experiment (Reviewer 8Evk's question about reward-irrelevant uncertainty), the convexity-claim correction (IG is concave; PWLC does not survive), threshold-table regeneration, single-source-of-truth table builders, and reviewer-question answers to write into the draft. Stage H and I acceptance criteria now include walking the ledger.
**Goal**: One integrated full-length publication merging the IWAI 2026 workshop paper (EFE-as-rho, Props 1–3) with the Price of Information extension (w as operational shadow price), turning the conceded w-scale limitation into the new headline contribution. Venue deliberately open; decision gate after the science is settled.

The complete plan — thesis, source-material inventory, gap analysis (new budgeted-rho-POMDP proposition, interleaved and multi-seed experiments, SARSOP/POMCPOW baseline debt, w* atlas appendix, merged related work), assembly outline for `paper/full_paper.tex`, milestones M1–M6 broken into development/experiment stages A–I with acceptance criteria, and the submission checklist (including the deferred PyPI release above) — lives in `Guidance_Documents/full_paper_plan.md`. That document is the living guide for this phase; update it with every change.

### Stage A delivered (July 23, 2026)
Formal propositions PI-1 to PI-4 drafted in `price_of_information.md` Section 9. Headline: scale equivariance (PI-1) is an exact theorem for the implemented receding-horizon Planning+IG agent — curve collapse is provable, and `B_EFE(alpha) = U(1/alpha)` gives the precise sense in which w=1 is not scale-invariant. Monotonicity (PI-2) holds exactly only for cumulative IG of exact maximizers, which formally explains the rough count staircases and the grid-plus-brackets solver default. PI-4 makes Prop 2's closed form the first knot of the H=1 usage staircase; verified by the new `TestProp2OnsetExact` unit test. No new citations. Full suite: 305 passed.

### Stage B delivered (July 23, 2026)
`estimate_usage` gained a `rocksample` family (depth-limited `RockSampleTreeSearchAgent`, check actions as usage); new `--only interleaved` protocol in `run_price_of_information.py`. Full run: RS[5,3], RS[7,4], Inspection-N16, four bracketed budgets each with SEs. Verdict **HOLD**, and stronger than the OTC battery: U(w) is cleanly nondecreasing at every sampled point on all three interleaved settings (no local dips). Instrumental floors are large (RS[5,3] 3.81, RS[7,4] 2.00, Inspection-N16 22.42 checks at w=0). Artifacts: `results/results_price_interleaved_{curves,prices}.csv`, `figures/price_staircase_interleaved.{png,pdf}`. Full suite: 307 passed.

### Stage C delivered (July 23, 2026)
`run_dual_multiseed` (`--only dual-multiseed`) sweeps 10 controller seeds per variant on the Diagnosis ×10 mid-run rescale protocol. Verdict **HOLD** with disjoint 95% CIs: re-adaptation reset-on-shift 53.3 [48.7, 57.9] (10/10 recovered, one reset each) vs decay-only 126.8 [90.5, 163.0] (8/10 recovered — two seeds never re-adapted). Post-rescale steady-state |U−B|: 0.11 vs 0.50. Artifacts: `results/results_price_dual_multiseed{,_metrics}.csv`, `figures/price_dual_multiseed.{png,pdf}`.

### Stage D delivered (July 23, 2026)
Heterogeneous sensing costs end to end: `DiagnosisEnv(test_costs=[0.5, 2.5])`, `run_otc_episode` records actual `sensing_cost` paid, `episode_sensing_usage` prefers the explicit cost. New `--only cost` protocol. Verdict **HOLD**: mean cost per test varies 1.21–1.39 with w (13.5% relative spread; the agent shifts toward the expensive test at high w), and cost-denominated brackets disagree with count-denominated ones (B_cost=11.15 → `(3.16, 10]` vs B_count=8.64 → `(10, 31.6]`). Artifacts: `results/results_price_cost_{curves,prices}.csv`, `figures/price_cost_budget.{png,pdf}`. Full suite: 311 passed.

### Stage E delivered (July 23, 2026)
Collapse test extended to Tiger (B=4) and Tileworld-6x6 (B=15) via `make_scaled_tiger`/`make_scaled_tileworld` and per-env scale budgets. Diagnosis/Bandit re-confirm (100% within 2·SE, brackets coincide). Tiger passes trivially: usage flat ~4.2 over w/α∈[0,20] — instrumental sensing saturates, no usable budget dial there (paper-worthy caveat). Tileworld **PARTIAL**: 90% within 2·SE; α=10 bracket adjacent to α∈{0.1,1} bracket sharing knot w/α=5.8 where U straddles B=15 within one SE — budget-at-knot noise, consistent with the PI-1 theorem. Since PI-1 proves collapse exactly, the empirical test is now a sanity check, not primary evidence.

### Stage F delivered (July 23, 2026)
SARSOP baseline debt retired. APPL `pomdpsol` built from source (`tools/build_sarsop.sh`, four patches for modern clang/Apple Silicon); `experiments/run_sarsop_baseline.py` exports the OTC suite to .pomdp, solves to 1e-3, and evaluates the alpha-vector policy through `run_otc_episode`. Verdict **HOLD**: EFE (w=1) is statistically indistinguishable from the SARSOP near-optimal reference on all three OTC benchmarks — identical action-for-action on Tiger (5.061±0.158), within 0.6 SE on Diagnosis (−1.217±0.184 vs −1.452±0.336), within noise on Bandit (6.261±0.112 vs 6.280±0.134). POMCPOW: NO-GO — it targets continuous spaces (Sunberg and Kochenderfer, ICAPS 2018, verified); our discrete suite is covered by SARSOP plus the existing POMCP RockSample baselines. Artifacts: `results/results_sarsop_baseline.{csv,json}`, `results/sarsop_models/`, `tests/test_sarsop_export.py`. Full suite: 315 passed.

### Stage G delivered (July 23, 2026)
w* atlas assembled by `experiments/run_w_atlas.py` from saved curves plus fresh B_EFE for the interleaved three (RS[5,3] 4.90±0.08, RS[7,4] 5.49±0.14, Inspection-N16 33.46±0.19). Verdict **HOLD**: all eight instances have rows (usage range, B_EFE±SE, two canonical-budget brackets); Tiger's low budget honestly unbracketed (flat curve). No meta-model claimed. Artifacts: `results/results_w_atlas.csv`, `paper/tables/w_atlas.tex`.

### Stage G2 delivered (July 23, 2026)
Distractor-robustness experiment for Reviewer 8Evk's reward-irrelevant-uncertainty question. New `DistractorDiagnosisEnv` (8 joint states: 4-way condition × binary nuisance), one distractor test proved and unit-tested to carry exactly zero condition information. Verdict **DONE**: Planning+IG's distractor fraction is 0 for w≤3.16, rises to 0.242±0.005 at w=10, saturates at 0.331±0.005 for w≥31.6 — IG is reward-blind, the budget caps waste but does not redirect it. IDS was checked and found not to be a clean immune contrast: its `info_state` fallback lets nuisance information through (distractor fraction 0.311±0.005, comparable to Planning+IG). Artifacts: `results/results_distractor_diagnosis.csv`, `figures/distractor_composition.{png,pdf}`, `tests/test_distractor_diagnosis.py` (13 tests).

### Phase 4 (targeted scientific additions) delivered (July 23, 2026)
Five bounded additions to the integrated paper: (1) dual-controller convergence — Proposition PI-5 (Robbins-Monro conditions for stationary convergence; reset-on-shift stated as an empirical nonstationary tracking mechanism, not a theorem) in `price_of_information.md`; (2) proper-scoring calibration table (`experiments/run_calibration_table.py`, log/Brier scores for EFE, Planning, and SARSOP/Planning+IG on the core OTC environments and Structural Inspection); (3) per-test value-of-information audit trail — optional structured logging in `PlanningInfoGainAgent`/`EFEAgent`/`InspectionTreeSearchAgent` via `rho_aif/audit.py`, with a Structural Inspection case study (`experiments/run_audit_case_study.py`); (4) a minimal destructive-sensing boundary counterexample (two-state, one-step, `tests/test_destructive_boundary.py`) showing naive EFE can rank actions incorrectly when observation actions alter the hidden state; (5) a horizon-depth map (`experiments/build_horizon_map.py`) comparing H=1 against H≥2 agreement across reward-asymmetry, informativeness, and cost regimes. All five landed in `paper.tex`/`paper_arxiv.tex` and therefore in `full_paper.tex`.

### Phase 5 (related-work positioning) delivered (July 23, 2026)
`price_of_information.tex`'s constrained-MDP paragraph expanded to constrained POMDPs (Kim et al. 2011, IJCAI) distinguishing exogenous offline-solved cost constraints from this paper's online-tracked epistemic-usage budget; a new sequential-Bayesian-experimental-design paragraph (Foster et al. 2021 DAD, ICML) distinguishes SBED's expected-information-gain design objective from the budgeted task-reward objective here. Every new citation verified against publisher/arXiv record (table in `full_paper_plan.md` Section 8.4).

### Stage H delivered (July 23, 2026)
`paper/full_paper.tex` assembled from `paper_arxiv.tex` plus the merged `price_of_information.tex` content: new theory section (Definition PI-3, Propositions PI-1/PI-2/PI-5, Corollary PI-4) and new experiments section (curve collapse, Prop 2 onset, multi-seed dual control, cost budgets, interleaved settings, SARSOP, distractor robustness, w* atlas) inserted; Discussion/Conclusion/Related work updated for the merged narrative; three appendix sections consolidated into one to avoid a LaTeX 26-letter section-counter overflow. Closed the one remaining review-ledger residue (the "why observe-then-commit" motivation sentence, 8Evk) in all three tex sources. `tectonic` compiles `paper.tex`, `paper_arxiv.tex`, `price_of_information.tex`, and `full_paper.tex` cleanly (zero errors, zero undefined references). README "Reproducing the Paper" table expanded to cover every Stage A-G2 and Phase 3-5 artifact. Full test suite: **347 passed**, 0 failed (up from 315 at Stage F). Verdict **HOLD**.

### Poster content prepared (August 3, 2026)
[Correction, August 4, 2026: this entry originally stated the integrated manuscript was accepted into *Minds and Machines*. That was a misstatement — the only acceptance is the abridged LNCS version at IWAI 2026 (Poster + Spotlight). `paper/full_paper.tex` is unpublished and everything beyond the IWAI paper, in particular the entire budgeted ρ-POMDP / price-of-information half, counts as new contributions for the next venue submission. Stage I (venue gate) is therefore live, not moot.] Ahead of poster design, `Guidance_Documents/poster_content.md` was written as a comprehensive, over-inclusive raw-material reference: publication metadata, plain-language and formal statements of every proposition/definition/corollary (equivalence, near-optimality thresholds, factored extension, destructive-sensing counterexample, scale equivariance, monotone comparative statics, usage-staircase knots, dual-controller convergence/tracking), every headline results table and number from both experiment batteries (core environments, Pareto analysis, Tileworld scaling, RockSample, Structural Inspection, discount/misspecification/POMCP/MCTS-EFE appendices, curve collapse, Prop 2 onset, multi-seed dual control, cost budgets, interleaved usage curves, SARSOP parity, distractor robustness, w* atlas), a full figure inventory with suggested poster roles, a limitations panel, and three candidate narrative arcs. Two load-bearing citations (Bernardo 1979; Champion et al. 2026) and the abstract's "+7.34" RockSample[7,8] figure were checked against source and reconciled (it is EFE minus reward-only Planning, flagged explicitly for the editorial pass). No paper source files were changed; this is purely a poster-prep artifact, editorial selection and layout deferred.

### Poster content expanded with every figure and every data table (August 3, 2026)
Following a follow-up request to include all rendered data, all 24 figures in `figures/` (15 previously PDF-only) were rasterized to PNG (`pdftoppm -png -r 150`) and embedded inline in two new sections of `poster_content.md`: Section 19 pairs every figure with its exact generating script/function and, where one is persisted, the full CSV backing it (or an explicit note when a script plots directly from a live, fixed-seed simulation with no intermediate CSV); Section 20 is a complete data appendix covering the other 45 of 65 `results/*.csv` files, grouped by the manuscript claim/table they support, with files under 20KB embedded in full inside collapsible blocks and larger files (`results_nearopt_horizon.csv`, `results_audit_case_study.csv`, `results_price_dual_descent.csv`, `results_price_dual_reset.csv`, `results_price_dual_multiseed.csv`, `results_full_statistics.csv`) given head/tail previews plus summary statistics. One exploratory/superseded file pair (`results_diagnosis_n16*.csv`) was flagged as not traced to any cited table rather than silently included as if it were. The document is now ~300KB / ~4,230 lines by design. No paper or experiment source files were modified.

### IWAI 2026 conference requirements added (August 3, 2026)
Clarified that the poster is being presented at IWAI 2026 (7th International Workshop on Active Inference), where this paper's abridged 12-page LNCS version (`paper/paper_iwai2026_abridged.tex`) was separately submitted and accepted as submission #4, decision Accept: Poster + Spotlight (per the existing OpenReview camera-ready record in this document). Added Section 21 to `poster_content.md` with everything fetched and cross-checked from the official IWAI 2026 CFP site and the most recent prior edition's site (2026-08-03): workshop identity/theme/organizers, venue (CSIC Central Auditorium, Madrid) and dates (October 14-16, 2026), registration costs and cancellation policy, full-paper submission/format/anonymization/License-to-Publish requirements, and poster-specific physical format and on-site logistics (A0 portrait, 2-minute spotlight, install/removal timing, first-come-first-served station allocation) explicitly flagged as carried forward from IWAI 2025 since IWAI 2026 has not yet published its own poster instructions. Added a design-implications subsection translating these constraints for the editorial pass, plus a pointer near the top of the document and a note in Section 17's narrative-arc guidance. No paper or experiment source files were modified.

### Publication-status correction and resubmission-readiness audit (August 4, 2026)
The Minds and Machines acceptance recorded on August 3 was a misstatement and has been corrected here and in `poster_content.md` (title, metadata, scope notes, Section 21). Actual status: only the abridged LNCS version is accepted (IWAI 2026, Poster + Spotlight, CCIS proceedings); `paper/full_paper.tex` (66 pages, LNCS master, compiles cleanly, 347 tests passing) is unpublished, and the entire budgeted ρ-POMDP / price-of-information half is new, unreviewed material. Consequence: no sequel paper is needed for the next venue submission — the integrated manuscript itself is the candidate, and Stage I (venue gate) is live. Readiness audit against the Stage I / Section 8.7 checklist: DONE — science complete (Stages A-H, all verdicts recorded), review ledger walked, README reproduction map, citation verification, limitations foregrounded in intro and conclusion. OPEN — (1) venue decision and the derived venue version (conference cut of 8-10 pages + appendix in the venue's template, or journal formatting; the master is venue-agnostic LNCS); (2) prior-publication positioning: the CCIS paper is archival, so the derived version must lead with the unpublished budgeted half, compress Props 1-3 to cited background, and disclose the overlap per the target venue's policy (JAIR explicitly welcomes extended versions; conference CFPs must be checked individually); (3) anonymization of the derived version plus the anonymized artifact link verified from a logged-out browser (deferred since the review response); (4) PyPI release of `rho-aif` per the M6 checklist (build, TestPyPI verify, upload, clean-venv install test); (5) abstract editorial pass for the derived version — it already opens POMDP-native but Section 8.7 asks it to lead with the budgeted-sensing/shadow-price headline, which currently arrives in the second half. Venue research (August 4, verified deadlines): AAMAS 2027 abstract Oct 1 / paper Oct 8, 2026 (official CFP); ICAPS 2027 abstract Dec 7 / paper Dec 13, 2026; ICML 2027 abstract Jan 16 / paper Jan 22, 2027 (aggregator); UAI 2027 ~Feb 12, 2027 (pattern-predicted, reconfirm); AISTATS 2027 ~Oct 8, 2026 (aggregator, official CFP not posted); JAIR/JMLR/TMLR rolling. Best-fit assessment recorded from discussion: UAI 2027 first (decision-theoretic POMDP reviewer pool, realistic runway), ICAPS 2027 second (ρ-POMDP community home, earlier deadline), JAIR as the deadline-free extended-version route; NeurIPS/ICML main tracks judged worst risk-adjusted fit given the prior NeurIPS reviews.

---

## Document Evolution

This guidance document is updated continuously to reflect:
- Implementation decisions and their rationale
- Experimental findings and insights
- Adjustments to research direction
- Technical challenges and solutions
- Progress toward publication

Each significant change should be committed to version control with clear documentation of what changed and why.
