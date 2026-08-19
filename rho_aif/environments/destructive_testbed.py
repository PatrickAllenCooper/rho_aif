"""
Destructive two-state testbed as a Gymnasium environment (study stage DS-B, E1).

Generalizes the JAIR manuscript's destructive-sensing counterexample
(Example ex:destructive in paper/full_paper_jair.tex) into a parameterized
observe-then-commit POMDP, per the predeclared study design in
docs/ideation/2026-08-19-destructive-sensing-design.md (Section 4, E1).

A unit is HEALTHY or FAULTY. One destructive test reads the unit with
accuracy p, but the act of testing can destroy it: with probability delta
if the unit is faulty and delta/2 if it is healthy, the unit moves to an
absorbing DESTROYED state in which both commit actions pay -R+ (the
unit's value is lost; see the design doc's E1 amendment) -- the option
value of a correct commit is gone, the design doc's "two currencies"
framing (Section 1). Two commit actions ACCEPT / REJECT end
the episode with reward R+ for a correct call and R- = -alpha * R+ for an
incorrect call.

Timing convention (NORMATIVE, inherited from the paper's Delta_T definition
and Example ex:destructive): the test observation is emitted from the
PRE-transition hidden state, and only afterwards does the destruction
transition act. The state-preserving posterior b'_o corresponds to the
identity coupling s' = s; the correct joint transition-observation
posterior is b'_{o,T}(s') proportional to sum_s T(s'|s) O(o|s) b(s), which
get_transition_models() exposes to the transition-aware agents.

Modeling note: the paper's example is the extreme two-state case where
drilling destroys with probability 1 for every state and the destroyed
condition coincides with state 0, whose commit reward is still live. This
testbed instead follows the design doc's absorbing-'destroyed' framing
(mirrored by E2's "absorbing worse state" and E3's damage flips): the
destroyed condition is a third state with lost-unit commit value, so partial
destruction (delta < 1) is expressible and a destroyed unit carries no
residual option value. The paper example's exact arithmetic is reproduced
from the example's own matrices in tests/test_transition_aware.py.
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Optional, Tuple, Dict, Any, List


# Hidden states.
HEALTHY = 0
FAULTY = 1
DESTROYED = 2

# Actions.
TEST = 0
ACCEPT = 1
REJECT = 2

# Observations.
OBS_READS_HEALTHY = 0
OBS_READS_FAULTY = 1
NULL_OBS = 2


class DestructiveTestbedEnv(gym.Env):
    """
    Destructive two-state testbed POMDP (design doc E1).

    Observation space: Discrete(3) -- OBS_READS_HEALTHY, OBS_READS_FAULTY, NULL_OBS
    Action space: Discrete(3) -- TEST, ACCEPT, REJECT

    Parameters:
        accuracy: test accuracy p; P(reads the pre-transition state correctly).
        destruction_prob: delta; P(destroy | faulty). Healthy units are
            destroyed with probability delta/2 (design doc Section 4, E1).
        alpha: reward asymmetry; incorrect commits pay R- = -alpha * R+.
        test_cost: cost c charged per destructive test.
        correct_reward: R+; reward scale for a correct commit.

    The unit starts HEALTHY or FAULTY with equal probability (uniform prior,
    as in the paper example); it never starts DESTROYED. DESTROYED is
    absorbing and pays zero for either commit.

    RNG discipline: every stochastic draw comes from self.np_random (never
    global np.random). A TEST step consumes exactly two draws in a fixed
    order -- (1) the pre-transition observation emission, (2) the
    destruction draw (consumed even when it cannot destroy, so the stream
    shape is identical across states) -- making seeded streams reproducible.
    """

    metadata = {"render_modes": []}

    def __init__(
        self,
        accuracy: float = 0.85,
        destruction_prob: float = 0.1,
        alpha: float = 1.0,
        test_cost: float = 1.0,
        correct_reward: float = 1.0,
    ):
        super().__init__()

        if not 0.0 <= accuracy <= 1.0:
            raise ValueError(f"accuracy must be in [0, 1], got {accuracy}")
        if not 0.0 <= destruction_prob <= 1.0:
            raise ValueError(f"destruction_prob must be in [0, 1], got {destruction_prob}")

        self.accuracy = accuracy
        self.destruction_prob = destruction_prob
        self.alpha = alpha
        self.test_cost = test_cost
        self.correct_reward = correct_reward
        self.incorrect_penalty = -alpha * correct_reward

        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Discrete(3)

        self._true_state: Optional[int] = None
        self._test_count = 0
        self._cost_paid = 0.0

    @property
    def observation_accuracy(self) -> float:
        return self.accuracy

    @property
    def observation_cost(self) -> float:
        return self.test_cost

    def get_observation_model(self) -> np.ndarray:
        """
        P(obs | pre-transition state) for the destructive test, shape (3, 2).

        The observation is emitted from the PRE-transition state (the
        paper's Example ex:destructive timing convention). A DESTROYED unit
        carries no signal about {healthy, faulty}, so its reading is
        uniform -- an implementation decision the paper does not constrain
        (its example never re-tests a destroyed unit).
        """
        p = self.accuracy
        return np.array([
            [p, 1.0 - p],       # HEALTHY
            [1.0 - p, p],       # FAULTY
            [0.5, 0.5],         # DESTROYED (uninformative reading)
        ])

    def get_observation_models(self) -> List[np.ndarray]:
        return [self.get_observation_model()]

    def get_observation_costs(self) -> List[float]:
        return [self.test_cost]

    def get_commit_reward_matrix(self) -> np.ndarray:
        """
        Reward for each (commit_action_index, state) pair, shape (2, 3).

        commit_action_index 0 = ACCEPT (correct on HEALTHY),
        commit_action_index 1 = REJECT (correct on FAULTY).
        Both commits pay -R+ on a DESTROYED unit: the unit's value is lost
        (design doc E1 amendment of Aug 19, 2026 -- zero here would let a
        transition-aware agent launder catastrophic-wrong risk by
        destroying ambiguous units, contaminating the over-testing
        hypotheses; -R+ keeps the domain-faithful ordering
        R+ > -R+ > -alpha R+ for alpha > 1).
        """
        r_plus = self.correct_reward
        r_minus = self.incorrect_penalty
        r_destroyed = -self.correct_reward
        return np.array([
            [r_plus, r_minus, r_destroyed],   # ACCEPT
            [r_minus, r_plus, r_destroyed],   # REJECT
        ])

    def get_transition_models(self) -> List[np.ndarray]:
        """
        Per-observation-action transition kernels T_k for the
        transition-aware agents (one per observation action; here just the
        destructive test).

        Convention: T[s, s'] = P(s' | s, TEST) -- rows index the
        pre-transition state, matching the observation model's row
        convention. The kernel acts AFTER the observation is emitted (the
        paper's pre-transition emission convention). At delta = 0 the
        kernel is exactly the identity, so the transition-aware agents
        reduce exactly to their state-preserving counterparts.
        """
        d = self.destruction_prob
        t_test = np.array([
            [1.0 - d / 2.0, 0.0, d / 2.0],   # HEALTHY
            [0.0, 1.0 - d, d],               # FAULTY
            [0.0, 0.0, 1.0],                 # DESTROYED (absorbing)
        ])
        return [t_test]

    def get_initial_belief(self) -> np.ndarray:
        """Uniform prior over {HEALTHY, FAULTY}; a unit never starts DESTROYED."""
        return np.array([0.5, 0.5, 0.0])

    def reset(
        self, *, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None
    ) -> Tuple[int, Dict[str, Any]]:
        """Reset the unit. options={'true_state': s} forces the initial
        state (any of HEALTHY/FAULTY/DESTROYED; used by dynamics tests)."""
        super().reset(seed=seed)
        if options is not None and "true_state" in options:
            forced = int(options["true_state"])
            if forced not in (HEALTHY, FAULTY, DESTROYED):
                raise ValueError(f"true_state must be 0, 1, or 2, got {forced}")
            self._true_state = forced
        else:
            self._true_state = int(self.np_random.choice([HEALTHY, FAULTY]))
        self._test_count = 0
        self._cost_paid = 0.0
        return NULL_OBS, {"true_state": self._true_state}

    def step(self, action: int) -> Tuple[int, float, bool, bool, Dict[str, Any]]:
        if action == TEST:
            pre_state = self._true_state

            # Draw 1: observation emitted from the PRE-transition state
            # (normative timing convention of Example ex:destructive).
            obs = self._emit_observation(pre_state)

            # Draw 2: destruction transition, applied AFTER emission.
            # Always consumed so the stream shape is state-independent.
            destruction_draw = float(self.np_random.random())
            if pre_state == FAULTY and destruction_draw < self.destruction_prob:
                self._true_state = DESTROYED
            elif pre_state == HEALTHY and destruction_draw < self.destruction_prob / 2.0:
                self._true_state = DESTROYED
            # DESTROYED is absorbing: the draw is ignored.

            self._test_count += 1
            self._cost_paid += self.test_cost
            info = {
                "true_state": self._true_state,
                "pre_transition_state": pre_state,
                "destroyed_this_step": pre_state != DESTROYED
                and self._true_state == DESTROYED,
                "test_count": self._test_count,
                "test_cost_paid": self._cost_paid,
            }
            return obs, -self.test_cost, False, False, info

        # Commit actions end the episode.
        correct = (action == ACCEPT and self._true_state == HEALTHY) or (
            action == REJECT and self._true_state == FAULTY
        )
        if self._true_state == DESTROYED:
            reward = 0.0  # option value forfeited; neither commit is correct
        else:
            reward = self.correct_reward if correct else self.incorrect_penalty

        info = {
            "true_state": self._true_state,
            "committed": action,
            "correct": correct,
            "test_count": self._test_count,
            "total_reward": reward - self._cost_paid,
        }
        return NULL_OBS, reward, True, False, info

    def _emit_observation(self, pre_state: int) -> int:
        """Noisy reading of the pre-transition state (one np_random draw)."""
        if pre_state == DESTROYED:
            return (
                OBS_READS_HEALTHY
                if self.np_random.random() < 0.5
                else OBS_READS_FAULTY
            )
        correct_reading = (
            OBS_READS_HEALTHY if pre_state == HEALTHY else OBS_READS_FAULTY
        )
        wrong_reading = (
            OBS_READS_FAULTY if pre_state == HEALTHY else OBS_READS_HEALTHY
        )
        if self.np_random.random() < self.accuracy:
            return correct_reading
        return wrong_reading
