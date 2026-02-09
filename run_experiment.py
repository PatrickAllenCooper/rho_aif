#!/usr/bin/env python3
"""
Execute the minimal information-seeking testbed experiment.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import pandas as pd
from scipy.stats import entropy
from scipy import stats

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)
np.random.seed(42)

# ============================================================================
# ENVIRONMENT IMPLEMENTATION
# ============================================================================

class Action(Enum):
    """Available actions in the environment."""
    OBSERVE = 0
    COMMIT_A = 1
    COMMIT_B = 2

class State(Enum):
    """Hidden states of the world."""
    A = 0
    B = 1

class Observation(Enum):
    """Observations that hint at the true state."""
    SIGNAL_A = 0
    SIGNAL_B = 1

@dataclass
class EnvConfig:
    """Configuration for the information-seeking environment."""
    observation_accuracy: float = 0.75  # P(correct observation | true state)
    observation_cost: float = 0.1       # Cost per observation
    correct_reward: float = 1.0         # Reward for correct commitment
    incorrect_penalty: float = -1.0     # Penalty for incorrect commitment
    
class MinimalInfoSeekingEnv:
    """Two-state partially observable environment for epistemic foraging."""
    
    def __init__(self, config: EnvConfig = EnvConfig()):
        self.config = config
        self.true_state = None
        self.done = False
        self.total_reward = 0.0
        self.observation_count = 0
        
    def reset(self) -> None:
        """Reset environment with random true state."""
        self.true_state = np.random.choice([State.A, State.B])
        self.done = False
        self.total_reward = 0.0
        self.observation_count = 0
        
    def step(self, action: Action) -> Tuple[Optional[Observation], float, bool]:
        """Execute action and return (observation, reward, done)."""
        if self.done:
            raise ValueError("Episode already terminated. Call reset().")
        
        if action == Action.OBSERVE:
            obs = self._generate_observation()
            reward = -self.config.observation_cost
            self.observation_count += 1
            self.total_reward += reward
            return obs, reward, False
        
        elif action in [Action.COMMIT_A, Action.COMMIT_B]:
            committed_state = State.A if action == Action.COMMIT_A else State.B
            correct = (committed_state == self.true_state)
            reward = self.config.correct_reward if correct else self.config.incorrect_penalty
            self.total_reward += reward
            self.done = True
            return None, reward, True
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def _generate_observation(self) -> Observation:
        """Generate noisy observation based on true state."""
        if np.random.random() < self.config.observation_accuracy:
            return Observation.SIGNAL_A if self.true_state == State.A else Observation.SIGNAL_B
        else:
            return Observation.SIGNAL_B if self.true_state == State.A else Observation.SIGNAL_A
    
    def get_observation_model(self) -> np.ndarray:
        """Return observation model: P(obs | state)."""
        acc = self.config.observation_accuracy
        return np.array([
            [acc, 1-acc],      # State A
            [1-acc, acc]       # State B
        ])

# ============================================================================
# BELIEF STATE TRACKING
# ============================================================================

class BeliefState:
    """Maintains probability distribution over hidden states."""
    
    def __init__(self, initial_belief: Optional[np.ndarray] = None):
        self.belief = initial_belief if initial_belief is not None else np.array([0.5, 0.5])
        self.history = [self.belief.copy()]
        
    def update(self, observation: Observation, obs_model: np.ndarray) -> None:
        """Bayesian update given observation."""
        obs_idx = observation.value
        likelihood = obs_model[:, obs_idx]
        posterior = likelihood * self.belief
        posterior = posterior / posterior.sum()
        self.belief = posterior
        self.history.append(self.belief.copy())
    
    def entropy(self) -> float:
        """Calculate entropy of current belief."""
        return entropy(self.belief, base=2)
    
    def most_likely_state(self) -> State:
        """Return most likely state under current belief."""
        return State.A if self.belief[0] > self.belief[1] else State.B
    
    def confidence(self) -> float:
        """Return confidence in most likely state."""
        return np.max(self.belief)
    
    def reset(self) -> None:
        """Reset to uniform belief."""
        self.belief = np.array([0.5, 0.5])
        self.history = [self.belief.copy()]

# ============================================================================
# AGENT IMPLEMENTATIONS
# ============================================================================

class BaseAgent:
    """Base class for all agents."""
    
    def __init__(self, env: MinimalInfoSeekingEnv):
        self.env = env
        self.belief = BeliefState()
        self.obs_model = env.get_observation_model()
        
    def reset(self) -> None:
        self.belief.reset()
    
    def select_action(self) -> Action:
        raise NotImplementedError
    
    def update_belief(self, observation: Observation) -> None:
        self.belief.update(observation, self.obs_model)
    
    def get_commit_action(self) -> Action:
        return Action.COMMIT_A if self.belief.most_likely_state() == State.A else Action.COMMIT_B
    
    def expected_reward_of_commit(self) -> float:
        confidence = self.belief.confidence()
        return (confidence * self.env.config.correct_reward + 
                (1 - confidence) * self.env.config.incorrect_penalty)

class MyopicAgent(BaseAgent):
    """Agent that only considers immediate expected reward."""
    
    def select_action(self) -> Action:
        commit_value = self.expected_reward_of_commit()
        observe_value = self._expected_value_of_observe()
        
        if observe_value > commit_value:
            return Action.OBSERVE
        else:
            return self.get_commit_action()
    
    def _expected_value_of_observe(self) -> float:
        expected_value = -self.env.config.observation_cost
        
        for obs in [Observation.SIGNAL_A, Observation.SIGNAL_B]:
            prob_obs = (self.belief.belief * self.obs_model[:, obs.value]).sum()
            temp_belief = BeliefState(self.belief.belief.copy())
            temp_belief.update(obs, self.obs_model)
            confidence = temp_belief.confidence()
            commit_reward = (confidence * self.env.config.correct_reward + 
                           (1 - confidence) * self.env.config.incorrect_penalty)
            expected_value += prob_obs * commit_reward
        
        return expected_value

class InformationGainAgent(BaseAgent):
    """ρ-POMDP agent using information gain as utility."""
    
    def __init__(self, env: MinimalInfoSeekingEnv, info_gain_weight: float = 1.0):
        super().__init__(env)
        self.info_gain_weight = info_gain_weight
    
    def select_action(self) -> Action:
        commit_value = self.expected_reward_of_commit()
        observe_value = self._expected_value_of_observe_with_info_gain()
        
        if observe_value > commit_value:
            return Action.OBSERVE
        else:
            return self.get_commit_action()
    
    def _expected_value_of_observe_with_info_gain(self) -> float:
        current_entropy = self.belief.entropy()
        expected_value = -self.env.config.observation_cost
        expected_future_entropy = 0.0
        expected_future_reward = 0.0
        
        for obs in [Observation.SIGNAL_A, Observation.SIGNAL_B]:
            prob_obs = (self.belief.belief * self.obs_model[:, obs.value]).sum()
            temp_belief = BeliefState(self.belief.belief.copy())
            temp_belief.update(obs, self.obs_model)
            future_entropy = temp_belief.entropy()
            expected_future_entropy += prob_obs * future_entropy
            confidence = temp_belief.confidence()
            commit_reward = (confidence * self.env.config.correct_reward + 
                           (1 - confidence) * self.env.config.incorrect_penalty)
            expected_future_reward += prob_obs * commit_reward
        
        info_gain = current_entropy - expected_future_entropy
        total_value = expected_value + expected_future_reward + self.info_gain_weight * info_gain
        
        return total_value

class VFEAgent(BaseAgent):
    """ρ-POMDP agent using variational free energy.
    
    Simplified formulation: VFE agent should commit when the value of
    reducing uncertainty is less than the cost of observation.
    """
    
    def __init__(self, env: MinimalInfoSeekingEnv, prior: Optional[np.ndarray] = None,
                 epistemic_weight: float = 0.5):
        super().__init__(env)
        self.prior = prior if prior is not None else np.array([0.5, 0.5])
        self.epistemic_weight = epistemic_weight  # Weight on uncertainty reduction
    
    def select_action(self) -> Action:
        """Select action based on value of observation vs commitment."""
        # Value of committing now
        commit_value = self.expected_reward_of_commit()
        
        # Expected value of observing then committing
        observe_value = self._expected_value_after_observe()
        
        # Compare values (observe_value includes observation cost)
        if observe_value > commit_value:
            return Action.OBSERVE
        else:
            return self.get_commit_action()
    
    def _expected_value_after_observe(self) -> float:
        """Expected value of observing once more, then committing optimally.
        
        This includes:
        1. Immediate observation cost
        2. Expected pragmatic value (reward after observation)
        3. Expected epistemic value (uncertainty reduction)
        """
        current_entropy = self.belief.entropy()
        expected_value = -self.env.config.observation_cost
        expected_future_entropy = 0.0
        expected_future_reward = 0.0
        
        # For each possible observation
        for obs_idx in range(2):
            prob_obs = (self.belief.belief * self.obs_model[:, obs_idx]).sum()
            
            if prob_obs < 1e-10:
                continue
            
            # Posterior after this observation
            likelihood = self.obs_model[:, obs_idx]
            posterior = likelihood * self.belief.belief
            posterior = posterior / posterior.sum()
            
            # Entropy of posterior
            posterior_safe = posterior + 1e-10
            posterior_entropy = -np.sum(posterior * np.log2(posterior_safe))
            expected_future_entropy += prob_obs * posterior_entropy
            
            # Expected reward from committing after this observation
            confidence = np.max(posterior)
            commit_reward = (confidence * self.env.config.correct_reward + 
                           (1 - confidence) * self.env.config.incorrect_penalty)
            expected_future_reward += prob_obs * commit_reward
        
        # Information gain (epistemic value)
        info_gain = current_entropy - expected_future_entropy
        
        # Total value = pragmatic value + weighted epistemic value - cost
        total_value = expected_future_reward + self.epistemic_weight * info_gain + expected_value
        
        return total_value

# ============================================================================
# EVALUATION FRAMEWORK
# ============================================================================

@dataclass
class EpisodeResult:
    """Results from a single episode."""
    agent_name: str
    num_observations: int
    final_belief_entropy: float
    final_confidence: float
    success: bool
    total_reward: float
    belief_history: List[np.ndarray]
    true_state: State
    committed_state: State

def run_episode(agent: BaseAgent, env: MinimalInfoSeekingEnv) -> EpisodeResult:
    """Run a single episode with the agent."""
    env.reset()
    agent.reset()
    
    while not env.done:
        action = agent.select_action()
        obs, reward, done = env.step(action)
        
        if not done:
            agent.update_belief(obs)
        else:
            committed_state = State.A if action == Action.COMMIT_A else State.B
            success = (committed_state == env.true_state)
            
            return EpisodeResult(
                agent_name=agent.__class__.__name__,
                num_observations=env.observation_count,
                final_belief_entropy=agent.belief.entropy(),
                final_confidence=agent.belief.confidence(),
                success=success,
                total_reward=env.total_reward,
                belief_history=agent.belief.history,
                true_state=env.true_state,
                committed_state=committed_state
            )

def run_experiment(agent_class, env: MinimalInfoSeekingEnv, 
                  num_episodes: int = 1000, **agent_kwargs) -> List[EpisodeResult]:
    """Run multiple episodes with an agent."""
    agent = agent_class(env, **agent_kwargs)
    results = []
    
    # Log progress every 10%
    log_interval = max(1, num_episodes // 10)
    
    for i in range(num_episodes):
        result = run_episode(agent, env)
        results.append(result)
        
        # Progress logging
        if (i + 1) % log_interval == 0 or (i + 1) == num_episodes:
            pct = ((i + 1) / num_episodes) * 100
            print(f"    Progress: {i+1}/{num_episodes} ({pct:.0f}%)", flush=True)
    
    return results

def summarize_results(results: List[EpisodeResult]) -> Dict:
    """Compute summary statistics from episode results."""
    return {
        'agent': results[0].agent_name,
        'mean_observations': np.mean([r.num_observations for r in results]),
        'std_observations': np.std([r.num_observations for r in results]),
        'mean_final_entropy': np.mean([r.final_belief_entropy for r in results]),
        'mean_confidence': np.mean([r.final_confidence for r in results]),
        'success_rate': np.mean([r.success for r in results]),
        'mean_reward': np.mean([r.total_reward for r in results]),
        'std_reward': np.std([r.total_reward for r in results])
    }

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("MINIMAL INFORMATION-SEEKING TESTBED EXPERIMENT")
    print("="*80 + "\n")
    
    # Create environment
    config = EnvConfig(
        observation_accuracy=0.75,
        observation_cost=0.1,
        correct_reward=1.0,
        incorrect_penalty=-1.0
    )
    env = MinimalInfoSeekingEnv(config)
    
    # Run experiments
    num_episodes = 1000
    
    print(f"Configuration:")
    print(f"  Episodes per agent: {num_episodes}")
    print(f"  Observation accuracy: {config.observation_accuracy}")
    print(f"  Observation cost: {config.observation_cost}")
    print(f"  Correct reward: {config.correct_reward}")
    print(f"  Incorrect penalty: {config.incorrect_penalty}\n")
    
    print("Running experiments...\n")
    
    print("Agent 1/3: Myopic Agent")
    myopic_results = run_experiment(MyopicAgent, env, num_episodes)
    print("  ✓ Myopic Agent complete\n")
    
    print("Agent 2/3: Information Gain Agent")
    ig_results = run_experiment(InformationGainAgent, env, num_episodes, info_gain_weight=1.0)
    print("  ✓ Information Gain Agent complete\n")
    
    print("Agent 3/3: VFE Agent")
    vfe_results = run_experiment(VFEAgent, env, num_episodes)
    print("  ✓ VFE Agent complete\n")
    
    # Summarize results
    all_results = {
        'Myopic': summarize_results(myopic_results),
        'InformationGain': summarize_results(ig_results),
        'VFE': summarize_results(vfe_results)
    }
    
    # Display summary
    print("\n" + "="*80)
    print("RESULTS SUMMARY")
    print("="*80 + "\n")
    
    summary_df = pd.DataFrame(all_results).T
    print(summary_df.to_string())
    print("\n" + "="*80)
    
    # Statistical analysis
    print("\nSTATISTICAL COMPARISONS")
    print("="*80 + "\n")
    
    myopic_obs = [r.num_observations for r in myopic_results]
    ig_obs = [r.num_observations for r in ig_results]
    vfe_obs = [r.num_observations for r in vfe_results]
    
    print("Number of Observations (t-tests):")
    print("-" * 80)
    
    t_stat, p_val = stats.ttest_ind(myopic_obs, ig_obs)
    print(f"  Myopic vs Information Gain: t={t_stat:.3f}, p={p_val:.6f}")
    
    t_stat, p_val = stats.ttest_ind(myopic_obs, vfe_obs)
    print(f"  Myopic vs VFE: t={t_stat:.3f}, p={p_val:.6f}")
    
    t_stat, p_val = stats.ttest_ind(ig_obs, vfe_obs)
    print(f"  Information Gain vs VFE: t={t_stat:.3f}, p={p_val:.6f}")
    
    myopic_reward = [r.total_reward for r in myopic_results]
    ig_reward = [r.total_reward for r in ig_results]
    vfe_reward = [r.total_reward for r in vfe_results]
    
    print("\nTotal Reward (t-tests):")
    print("-" * 80)
    
    t_stat, p_val = stats.ttest_ind(myopic_reward, ig_reward)
    print(f"  Myopic vs Information Gain: t={t_stat:.3f}, p={p_val:.6f}")
    
    t_stat, p_val = stats.ttest_ind(myopic_reward, vfe_reward)
    print(f"  Myopic vs VFE: t={t_stat:.3f}, p={p_val:.6f}")
    
    t_stat, p_val = stats.ttest_ind(ig_reward, vfe_reward)
    print(f"  Information Gain vs VFE: t={t_stat:.3f}, p={p_val:.6f}")
    
    # Key findings
    print("\n" + "="*80)
    print("KEY FINDINGS")
    print("="*80 + "\n")
    
    myopic_mean_obs = all_results['Myopic']['mean_observations']
    ig_mean_obs = all_results['InformationGain']['mean_observations']
    vfe_mean_obs = all_results['VFE']['mean_observations']
    
    print("1. EPISTEMIC FORAGING BEHAVIOR")
    print(f"   - Myopic agent observes {myopic_mean_obs:.2f} times on average")
    print(f"   - Information Gain agent observes {ig_mean_obs:.2f} times on average")
    print(f"   - VFE agent observes {vfe_mean_obs:.2f} times on average")
    
    if ig_mean_obs > myopic_mean_obs:
        print(f"   → Info Gain explores {((ig_mean_obs/myopic_mean_obs - 1)*100):.1f}% more than Myopic")
    if vfe_mean_obs > myopic_mean_obs:
        print(f"   → VFE explores {((vfe_mean_obs/myopic_mean_obs - 1)*100):.1f}% more than Myopic")
    if abs(vfe_mean_obs - ig_mean_obs) > 0.01:
        direction = "more" if vfe_mean_obs > ig_mean_obs else "less"
        pct = abs((vfe_mean_obs/ig_mean_obs - 1)*100)
        print(f"   → VFE explores {pct:.1f}% {direction} than Information Gain")
    else:
        print(f"   → VFE and Information Gain show nearly identical exploration behavior")
    
    print("\n2. EXPECTED UTILITY")
    for name in ['Myopic', 'InformationGain', 'VFE']:
        mean_reward = all_results[name]['mean_reward']
        success_rate = all_results[name]['success_rate']
        print(f"   - {name:17s}: {mean_reward:+.3f} reward, {success_rate:.1%} success rate")
    
    print("\n3. BELIEF CONVERGENCE")
    for name in ['Myopic', 'InformationGain', 'VFE']:
        entropy = all_results[name]['mean_final_entropy']
        confidence = all_results[name]['mean_confidence']
        print(f"   - {name:17s}: {entropy:.3f} bits entropy, {confidence:.1%} confidence at decision")
    
    print("\n" + "="*80)
    
    # Save results
    summary_df.to_csv('results_summary.csv')
    print("\nResults saved to: results_summary.csv")
    print("\n")
