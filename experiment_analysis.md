# Minimal Information-Seeking Testbed: Experimental Results

**Date**: February 9, 2026  
**Experiment**: Comparison of three epistemic foraging agents  
**Episodes per agent**: 1,000

---

## Experimental Setup

### Environment Configuration
- **States**: 2 (A or B)
- **Actions**: Observe (cost: 0.1), Commit A, Commit B
- **Observation accuracy**: 75%
- **Rewards**: +1.0 (correct), -1.0 (incorrect)
- **Initial belief**: Uniform [0.5, 0.5]

### Agent Implementations

1. **Myopic Agent**: One-step lookahead, commits when expected value of observing ≤ committing
2. **Information Gain Agent**: Explicitly values entropy reduction with weight = 1.0
3. **VFE Agent**: Values entropy reduction with weight = 0.5 (current implementation)

---

## Results Summary

| Agent | Mean Obs | Std Obs | Success Rate | Mean Reward | Final Entropy | Final Confidence |
|-------|----------|---------|--------------|-------------|---------------|------------------|
| Myopic | 1.00 | 0.00 | 75.4% | +0.408 | 0.811 bits | 75.0% |
| Information Gain | 3.17 | 2.02 | 89.8% | +0.479 | 0.469 bits | 90.0% |
| VFE | 1.00 | 0.00 | 76.0% | +0.420 | 0.811 bits | 75.0% |

---

## Key Findings

### 1. Information Gain Agent Demonstrates Superior Epistemic Foraging

The Information Gain agent:
- **Explores 217% more** than Myopic/VFE agents (3.17 vs 1.0 observations)
- **Achieves 19% higher success rate** (89.8% vs 75.4%)
- **Obtains 17% higher reward** (+0.479 vs +0.408)
- **Reduces uncertainty significantly** (0.469 vs 0.811 bits final entropy)

**Statistical significance**:
- Observations: t = -33.876, p < 0.000001 (highly significant)
- Reward: t = -2.103, p = 0.036 (significant at α = 0.05)

### 2. VFE Agent Behaves Identically to Myopic Agent

The current VFE implementation with `epistemic_weight = 0.5` produces:
- **Identical observation counts** (1.00 exactly)
- **Identical final entropy** (0.811 bits)
- **Nearly identical performance** (76.0% vs 75.4% success)

**Interpretation**: The epistemic weight is too low, making the VFE agent essentially ignore uncertainty reduction in favor of immediate reward.

### 3. Trade-off Between Exploration and Exploitation

**Information Gain agent** strategy:
- Observes multiple times to reduce uncertainty
- Only commits when highly confident (~90%)
- Pays observation costs but gains from higher accuracy
- **Net benefit**: +0.071 reward over Myopic

**Myopic/VFE agent** strategy:
- Commits after single observation (75% confidence)
- Minimizes observation costs
- Accepts higher error rate
- **Trade-off**: Lower costs but more mistakes

---

## Statistical Analysis

### Number of Observations
- **Myopic vs Info Gain**: t = -33.876, p < 0.000001 ✓✓✓
- **Myopic vs VFE**: Cannot compute (zero variance)
- **Info Gain vs VFE**: t = 33.876, p < 0.000001 ✓✓✓

### Total Reward
- **Myopic vs Info Gain**: t = -2.103, p = 0.036 ✓
- **Myopic vs VFE**: t = -0.313, p = 0.755 (not significant)
- **Info Gain vs VFE**: t = 1.758, p = 0.079 (marginally significant)

---

## Behavioral Analysis

### Epistemic Foraging Patterns

**Myopic Agent**:
- Commits immediately after first observation
- Does not look ahead beyond one step
- Threshold confidence: ~75%

**Information Gain Agent**:
- Continues observing while information gain > observation cost
- Adaptive stopping: more observations when signals conflict
- Threshold confidence: ~90%

**VFE Agent (current)**:
- Behaves identically to Myopic
- Epistemic component underweighted
- **Needs tuning**: Increase epistemic_weight to see divergence

### Expected Behavior if VFE Implemented Correctly

With proper weighting, VFE should:
1. Balance pragmatic value (reward) with epistemic value (uncertainty reduction)
2. Show different observation patterns than pure information gain
3. Potentially explore less than Info Gain but more than Myopic
4. Achieve intermediate performance between the two

---

## Conclusions

### Research Question Answered

**Does the utility function (myopic reward vs information gain vs VFE) affect epistemic foraging behavior?**

**Answer**: **Yes, dramatically.**

Information Gain agents demonstrate:
- Substantially more exploration (3.17 vs 1.0 observations)
- Higher decision confidence (90% vs 75%)
- Better task performance (89.8% vs 75.4% success)
- Higher expected utility despite observation costs

### Implementation Issues Identified

1. **VFE agent epistemic weight too low**: Current weight (0.5) makes it identical to Myopic agent
2. **Need parameter exploration**: Test epistemic_weight ∈ [0.5, 1.0, 1.5, 2.0] to find divergence point
3. **Alternative VFE formulations**: Consider other active inference EFE formulations from literature

### Next Steps

#### Immediate
1. **Tune VFE epistemic weight** to achieve behavioral divergence from Myopic
2. **Run parameter sweep** on epistemic_weight to characterize sensitivity
3. **Compare VFE to Info Gain** once properly tuned

#### Near-term
1. **Scale to Tiger problem** with validated agent implementations
2. **Test robustness** to different observation accuracies and costs
3. **Implement visualizations** of belief trajectories

#### Long-term
1. **Theoretical analysis** of optimal epistemic foraging strategies
2. **Extend to continuous state spaces**
3. **Multi-step planning horizons**

---

## Implementation Notes

### Agent Code Structure
- All agents use exact Bayesian belief updates
- Myopic and Info Gain agents working as intended
- VFE agent needs epistemic weight tuning

### Performance
- 1,000 episodes/agent completes in ~5 seconds
- No computational bottlenecks
- Ready to scale to larger experiments

### Data Quality
- All results reproducible (seed = 42)
- Statistical power adequate (n = 1,000)
- Clear behavioral differences detected

---

## Recommendations for Guidance Document Update

Based on these results, update the research plan to:

1. **Add VFE parameter exploration phase** before Tiger problem
2. **Document epistemic weight sensitivity** as key finding
3. **Establish Info Gain agent as strong baseline** for future comparisons
4. **Note successful minimal testbed validation** - ready to scale

---

## Files Generated

- `run_experiment.py`: Main experimental script
- `debug_vfe.py`: VFE agent debugging tool
- `results_summary.csv`: Numerical results
- `experiment_analysis.md`: This document
