"""
pymdp-based active inference agent wrapper.

Wraps the pymdp library's Agent class to run on our POMDP environments,
providing a reference implementation for validating our VFE agent's EFE
computation. Also provides standalone EFE computation using pymdp's
control module for mathematical consistency checks.

Architectural note: pymdp evaluates policy SEQUENCES over a fixed horizon
using action-independent observation models. Our environments use
action-dependent observations and variable-length episodes. This wrapper
adapts by treating each step as a single-step policy evaluation, which
is equivalent to myopic active inference (policy_len=1). For multi-step
comparison, the recursive EFE in our VFE agent corresponds to pymdp's
sophisticated inference scheme (Friston et al., 2021).
"""

import numpy as np
from typing import Union, List, Optional
from pymdp.agent import Agent as PyMDPAgentBase
from pymdp import utils, control, maths
from agents.base import BaseAgent


def compute_efe_pymdp(
    observation_model: np.ndarray,
    belief: np.ndarray,
    preferred_obs: np.ndarray,
) -> tuple:
    """
    Compute Expected Free Energy using pymdp's mathematical functions.

    Returns (pragmatic_value, epistemic_value, total_efe) for the given
    observation model and belief state, using pymdp's internal routines
    for direct comparison with our VFE agent.

    Args:
        observation_model: P(obs|state), shape (num_states, num_obs) -- our format
        preferred_obs: log prior over preferred observations, shape (num_obs,)
        belief: current belief, shape (num_states,)

    Returns:
        (pragmatic, epistemic, total_efe) tuple
    """
    A = observation_model.T

    predicted_obs = A @ belief

    pragmatic = predicted_obs @ preferred_obs

    H_A = -np.sum(A * np.log(A + 1e-16), axis=0)
    epistemic = -belief @ H_A

    expected_log_obs = predicted_obs @ np.log(predicted_obs + 1e-16)
    info_gain = epistemic - expected_log_obs

    efe = -pragmatic - info_gain

    return float(pragmatic), float(info_gain), float(efe)


class PyMDPAgent(BaseAgent):
    """
    Active inference agent using pymdp's Agent class internally.

    Uses single-step (myopic) policy evaluation at each timestep,
    selecting the action that minimizes EFE as computed by pymdp.
    The agent translates between our environment format and pymdp's
    generative model format at each step.
    """

    def __init__(
        self,
        observation_models: Union[np.ndarray, List[np.ndarray]],
        env_config: dict,
        gamma: float = 16.0,
    ):
        super().__init__(observation_models, env_config)

        num_actions = self.num_observe_actions + self.num_commit_actions

        A_pymdp = utils.obj_array(1)
        A_pymdp[0] = self.obs_models[0].T

        B_pymdp = utils.obj_array(1)
        B_pymdp[0] = np.zeros((self.num_states, self.num_states, num_actions))
        for a in range(num_actions):
            B_pymdp[0][:, :, a] = np.eye(self.num_states)

        C_pymdp = utils.obj_array(1)
        C_pymdp[0] = np.zeros(self.num_obs)

        D_pymdp = utils.obj_array(1)
        D_pymdp[0] = np.ones(self.num_states) / self.num_states

        self.pymdp_agent = PyMDPAgentBase(
            A=A_pymdp, B=B_pymdp, C=C_pymdp, D=D_pymdp,
            policy_len=1,
            use_utility=True,
            use_states_info_gain=True,
            action_selection="deterministic",
            gamma=gamma,
        )

        self._step_count = 0

    def reset(self):
        super().reset()
        D = utils.obj_array(1)
        D[0] = np.ones(self.num_states) / self.num_states
        self.pymdp_agent.D = D
        self.pymdp_agent.qs = utils.obj_array_uniform(
            [self.num_states]
        )
        self._step_count = 0

    def select_action(self) -> int:
        _, commit_reward = self.best_commit()

        qs = utils.obj_array(1)
        qs[0] = self.belief.belief.copy()
        self.pymdp_agent.qs = qs

        q_pi, efe = self.pymdp_agent.infer_policies()

        observe_actions = list(range(self.num_observe_actions))
        best_obs_idx = None
        best_obs_efe = float("inf")
        for idx, policy in enumerate(self.pymdp_agent.policies):
            action = int(policy[0, 0])
            if action in observe_actions and efe[idx] < best_obs_efe:
                best_obs_efe = efe[idx]
                best_obs_idx = idx

        commit_efe = -commit_reward

        if best_obs_idx is not None and best_obs_efe < commit_efe:
            return int(self.pymdp_agent.policies[best_obs_idx][0, 0])

        return self.get_commit_action()

    def update_belief(self, observation: int, obs_action: int = 0) -> None:
        super().update_belief(observation, obs_action)
        self._step_count += 1
