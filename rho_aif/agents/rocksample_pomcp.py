"""
POMCP (Partially Observable Monte-Carlo Planning) for RockSample.

A genuine implementation of Silver and Veness (2010) for the interleaved
observe-act RockSample domain: a search tree over action-observation
histories, UCB1 node selection with mean (UCT) backup, and Monte Carlo
rollouts from newly expanded leaves. This replaces the flat one-ply
evaluator that previously carried the POMCP name in this repository (now
correctly labelled ``RockSampleFlatMCAgent``).

Three design points are load-bearing and are documented here because each
one was measured, not assumed:

  1. ``RockSampleEnv.exit_action`` is position-independent: exit grants
     ``exit_reward + move_cost`` from any cell. So ``+9.50`` (under the
     paper's parameterisation) is an unconditional, zero-variance outside
     option available at every step, and every other action must beat it.
     The leaf value at the depth bound must therefore be that same
     continuation value. With a leaf value of zero the agent exits at step
     one in every configuration tested, because the tree's exit branch is
     worth +9.50 while every truncated branch is worth 0.

  2. The rollout policy must be a function of the simulated *history*, not
     of the sampled rock-quality particle. A state-conditioned ("hindsight")
     rollout reproduces the Flat-MC pathology exactly (check-spam and no
     exit), and it breaks the history-measurability condition Silver and
     Veness's convergence result assumes. The rollout here carries a
     simulated factored belief down the simulation and reads only that. The
     hindsight variant is retained behind ``rollout_policy="hindsight"`` as
     a documented ablation.

  3. Backup is mean (UCT), not max. ``rho_aif/agents/mcts_efe.py`` uses
     max-backup for a different purpose; copying that here would make this a
     sparse-sampling Bellman search rather than the faithful POMCP baseline
     the manuscript needs.

The belief over rock qualities factorises exactly in this domain (the prior
is independent per rock, a check on rock k depends only on rock k, sampling
yields no observation, and hidden state never transitions). The default
``belief_mode="exact"`` therefore samples root particles i.i.d. from the
exact factored posterior and particle depletion is structurally impossible.
``belief_mode="particle"`` runs the literal unweighted particle filter with
rejection sampling and reinvigoration, for the sensitivity row.
"""

import math
import time
from typing import Dict, List, Optional, Tuple

import numpy as np

from rho_aif.agents.rocksample_agents import (
    RockSampleBeliefState,
    _bayes_check,
    _move_toward_common,
    _update_belief_common,
)


class RockSamplePOMCPNode:
    """A node in the RockSample POMCP search tree.

    Action statistics live in ``children`` (keyed by action) and history
    children live in ``obs_children`` (keyed by ``(action, observation)``).
    Position and the sampled-rock set are deterministic functions of the
    action prefix, so they are threaded down the recursion as arguments
    rather than stored here.
    """

    __slots__ = ["visit_count", "value_sum", "children", "obs_children", "particles"]

    def __init__(self):
        self.visit_count = 0
        self.value_sum = 0.0
        self.children: Dict[int, "RockSamplePOMCPNode"] = {}
        self.obs_children: Dict[Tuple[int, int], "RockSamplePOMCPNode"] = {}
        self.particles: List[Tuple[int, ...]] = []

    @property
    def value(self) -> float:
        if self.visit_count == 0:
            return 0.0
        return self.value_sum / self.visit_count


class RockSamplePOMCPAgent:
    """POMCP for RockSample.

    Follows the duck-typed RockSample agent contract used throughout
    ``rho_aif/agents/rocksample_agents.py``: ``__init__(env, ...)``,
    ``select_action()``, ``update(action, observation)``, ``reset()``.

    Parameters
    ----------
    num_simulations
        Simulations per decision. This is the compute axis the budget sweep
        varies. Values below 1024 are not informative on this domain.
    exploration_constant
        UCB1 exploration constant c. Selected on tuning seeds disjoint from
        the evaluation seeds.
    planning_horizon
        Depth bound D of the search tree plus rollout.
    discount
        Per-step discount. Defaults to 1.0, matching the undiscounted return
        the RockSample harness reports and every other RockSample agent. At
        0.95 the agent collapses to immediate exit, because the
        position-independent exit makes +10 now dominate +10 later.
    rollout_policy
        One of "preferred", "approach", "random", "hindsight". Only
        "hindsight" reads the sampled quality vector, and it exists as an
        ablation. The default is "approach", which walks to a rock before
        spending a check, because "preferred" checks at long range under this
        parameterisation and is worth less than the unconditional exit, so an
        agent built on it correctly exits at step one. The configuration the
        manuscript reports is selected by the tuning sweep in
        experiments/run_rocksample_pomcp.py, not by this default.
    root_criterion
        "value" selects the max-Q root action, "visits" the most-visited.
    belief_mode
        "exact" (default) samples root particles from the exact factored
        posterior. "particle" runs the literal particle filter.
    reuse_subtree
        Retain the subtree under the realised (action, observation) as the
        next root. Off by default: under a fixed depth bound, statistics
        accumulated at depth 1 would be credited with a full horizon after
        promotion, and the exact belief removes reuse's usual justification.
    budget_aware_horizon
        Shrink D as the episode's step cap approaches, so a receding-horizon
        planner cannot dither for free near the cap.
    leaf_value
        "exit" (default) values a truncated branch at the guaranteed
        continuation ``exit_reward + move_cost``. "zero" reproduces the
        exit-at-step-one collapse and is retained as a regression witness.
        "greedy_belief" uses the tree-search agent's greedy heuristic.
    seed
        ``None`` draws from the global ``np.random`` stream, which the
        RockSample harness seeds before constructing each agent. An integer
        gives the agent its own ``RandomState``.
    """

    ROLLOUT_POLICIES = ("preferred", "approach", "random", "hindsight")
    LEAF_VALUES = ("exit", "zero", "greedy_belief")
    ROOT_CRITERIA = ("value", "visits")
    BELIEF_MODES = ("exact", "particle")

    # Belief threshold above which the preferred rollout policy will sample a
    # rock it is standing on, and accuracy thresholds at which it will spend a
    # check. Fixed on literature grounds rather than tuned (see the tuning
    # protocol in experiments/run_rocksample_pomcp.py).
    ROLLOUT_SAMPLE_THRESHOLD = 0.85
    ROLLOUT_WRITE_OFF_THRESHOLD = 0.15
    ROLLOUT_CHECK_ACCURACY_PREFERRED = 0.6
    ROLLOUT_CHECK_ACCURACY_APPROACH = 0.85

    def __init__(
        self,
        env,
        num_simulations: int = 2048,
        exploration_constant: float = 5.0,
        planning_horizon: int = 15,
        discount: float = 1.0,
        rollout_policy: str = "approach",
        root_criterion: str = "value",
        belief_mode: str = "exact",
        num_particles: int = 4096,
        reuse_subtree: bool = False,
        budget_aware_horizon: bool = True,
        leaf_value: str = "exit",
        seed: Optional[int] = None,
        collect_diagnostics: bool = True,
    ):
        if rollout_policy not in self.ROLLOUT_POLICIES:
            raise ValueError(f"rollout_policy must be one of {self.ROLLOUT_POLICIES}")
        if leaf_value not in self.LEAF_VALUES:
            raise ValueError(f"leaf_value must be one of {self.LEAF_VALUES}")
        if root_criterion not in self.ROOT_CRITERIA:
            raise ValueError(f"root_criterion must be one of {self.ROOT_CRITERIA}")
        if belief_mode not in self.BELIEF_MODES:
            raise ValueError(f"belief_mode must be one of {self.BELIEF_MODES}")

        self.env = env
        self.num_simulations = int(num_simulations)
        self.exploration_constant = float(exploration_constant)
        self.planning_horizon = int(planning_horizon)
        self.discount = float(discount)
        self.rollout_policy = rollout_policy
        self.root_criterion = root_criterion
        self.belief_mode = belief_mode
        self.num_particles = int(num_particles)
        self.reuse_subtree = bool(reuse_subtree)
        self.budget_aware_horizon = bool(budget_aware_horizon)
        self.leaf_value = leaf_value
        self.seed = seed
        self.collect_diagnostics = bool(collect_diagnostics)

        self._rng = np.random if seed is None else np.random.RandomState(int(seed))

        self.belief = RockSampleBeliefState(env.num_rocks)
        self._rock_positions: Optional[List[Tuple[int, int]]] = None
        self._acc_cache: Dict[Tuple[Tuple[int, int], int], float] = {}
        self._t = 0
        self._root: Optional[RockSamplePOMCPNode] = None
        self._particles: List[Tuple[int, ...]] = []
        self._num_reinvigorations = 0

        self.diagnostics: Dict = {}
        self.diagnostics_history: List[Dict] = []

        self.reset()

    # ------------------------------------------------------------------
    # Agent contract
    # ------------------------------------------------------------------

    def reset(self):
        self.belief.reset()
        # Rock positions are only available once the environment has been
        # reset, and the RockSample harness constructs agents before the
        # first env.reset(), so resolve them lazily.
        self._rock_positions = None
        self._acc_cache = {}
        self._t = 0
        self._root = None
        self._num_reinvigorations = 0
        self.diagnostics = {}
        self.diagnostics_history = []
        if self.belief_mode == "particle":
            self._particles = [
                tuple(int(b) for b in self._rng.randint(0, 2, self.env.num_rocks))
                for _ in range(self.num_particles)
            ]
        else:
            self._particles = []

    def _ensure_rock_positions(self):
        if self._rock_positions is None:
            self._rock_positions = self.env.get_rock_positions()

    def select_action(self) -> int:
        t0 = time.perf_counter()
        self._ensure_rock_positions()
        depth_bound = self._depth_bound()
        pos = self.env._agent_pos

        root = self._root if (self.reuse_subtree and self._root is not None) else RockSamplePOMCPNode()

        stats = {
            "max_tree_depth": 0,
            "num_history_nodes": 0,
            "num_ucb_calls": 0,
            "num_rollouts": 0,
        }

        sampled0 = self.belief.rock_sampled
        bel0 = self.belief.rock_beliefs

        for _ in range(self.num_simulations):
            quals = self._sample_particle()
            self._simulate(root, quals, pos, sampled0, bel0, 0, depth_bound, stats)

        self._root = root
        action = self._select_root_action(root, pos, sampled0)

        if self.collect_diagnostics:
            self.diagnostics = {
                "max_tree_depth": stats["max_tree_depth"],
                "num_history_nodes": stats["num_history_nodes"],
                "num_ucb_calls": stats["num_ucb_calls"],
                "num_rollouts": stats["num_rollouts"],
                "num_simulations_run": self.num_simulations,
                "planning_horizon_used": depth_bound,
                "root_visit_counts": {
                    a: n.visit_count for a, n in root.children.items()
                },
                "root_q_values": {a: n.value for a, n in root.children.items()},
                "num_reinvigorations": self._num_reinvigorations,
                "planning_ms": (time.perf_counter() - t0) * 1000.0,
            }
            self.diagnostics_history.append(self.diagnostics)

        return action

    def update(self, action: int, observation: int):
        self._t += 1
        self._ensure_rock_positions()
        _update_belief_common(self.belief, self.env, action, observation)
        if self.belief_mode == "particle":
            self._update_particles(action, observation)
        if self.reuse_subtree:
            self._advance_root(action, observation)
        else:
            self._root = None

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def _depth_bound(self) -> int:
        if not self.budget_aware_horizon:
            return self.planning_horizon
        remaining = int(self.env.max_steps) - self._t
        return max(1, min(self.planning_horizon, remaining))

    def _simulate(self, node, quals, pos, sampled, bel, depth, depth_bound, stats) -> float:
        if depth >= depth_bound:
            return self._leaf_estimate(pos, bel, sampled)

        if depth > stats["max_tree_depth"]:
            stats["max_tree_depth"] = depth

        if node.visit_count == 0:
            node.visit_count = 1
            stats["num_rollouts"] += 1
            value = self._rollout(quals, pos, sampled, bel, depth, depth_bound)
            node.value_sum = value
            return value

        actions = self._legal_actions(pos, sampled)
        action = self._ucb_select(node, actions, stats)
        reward, obs, pos2, sampled2, bel2, terminal = self._sim_step(
            action, quals, pos, sampled, bel
        )

        if terminal:
            total = reward
        else:
            key = (action, obs)
            child = node.obs_children.get(key)
            if child is None:
                child = RockSamplePOMCPNode()
                node.obs_children[key] = child
                stats["num_history_nodes"] += 1
            if self.belief_mode == "particle":
                child.particles.append(tuple(int(q) for q in quals))
            total = reward + self.discount * self._simulate(
                child, quals, pos2, sampled2, bel2, depth + 1, depth_bound, stats
            )

        action_node = node.children.get(action)
        if action_node is None:
            action_node = RockSamplePOMCPNode()
            node.children[action] = action_node
        action_node.visit_count += 1
        action_node.value_sum += total

        node.visit_count += 1
        node.value_sum += total
        return total

    def _ucb_select(self, node, actions, stats) -> int:
        stats["num_ucb_calls"] += 1
        log_n = math.log(max(1, node.visit_count))
        best_action = None
        best_ucb = -float("inf")

        for action in actions:
            child = node.children.get(action)
            if child is None or child.visit_count == 0:
                return action
            ucb = child.value + self.exploration_constant * math.sqrt(
                log_n / child.visit_count
            )
            if ucb > best_ucb:
                best_ucb = ucb
                best_action = action

        return best_action if best_action is not None else actions[0]

    def _select_root_action(self, root, pos, sampled) -> int:
        actions = [a for a in self._legal_actions(pos, sampled) if a in root.children]
        if not actions:
            return self.env.exit_action
        if self.root_criterion == "visits":
            return int(max(actions, key=lambda a: root.children[a].visit_count))
        return int(max(actions, key=lambda a: root.children[a].value))

    def _legal_actions(self, pos, sampled) -> List[int]:
        """Legal actions from observable quantities only.

        Position and the sampled-rock set are both fully observable, so this
        mask imports no hidden-state information. It removes wall bumps
        (a pure move_cost loss), checks on already-sampled rocks (which
        cannot change any decision), and samples where no unsampled rock
        sits.
        """
        env = self.env
        actions = []
        for a in range(env.NUM_MOVE_ACTIONS):
            if self._apply_move(pos, a) != pos:
                actions.append(a)
        for k in range(env.num_rocks):
            if not sampled[k]:
                actions.append(env.NUM_MOVE_ACTIONS + k)
        for k in range(env.num_rocks):
            if not sampled[k] and self._rock_positions[k] == pos:
                actions.append(env.sample_action)
                break
        actions.append(env.exit_action)
        return actions

    def _sim_step(self, action, quals, pos, sampled, bel):
        """One simulated step. Mirrors RockSampleEnv.step exactly.

        Returns ``(reward, observation, pos', sampled', bel', terminal)``.
        Arrays are copied only on the branches that mutate them.
        """
        env = self.env
        if action < env.NUM_MOVE_ACTIONS:
            return env.move_cost, 2, self._apply_move(pos, action), sampled, bel, False

        if action < env.NUM_MOVE_ACTIONS + env.num_rocks:
            k = action - env.NUM_MOVE_ACTIONS
            accuracy = self._check_accuracy(pos, k)
            true_q = int(quals[k])
            obs = true_q if self._rng.random() < accuracy else 1 - true_q
            bel2 = bel.copy()
            bel2[k] = _bayes_check(bel[k], obs, accuracy)
            return env.move_cost, obs, pos, sampled, bel2, False

        if action == env.sample_action:
            reward = env.move_cost
            sampled2 = sampled
            bel2 = bel
            for k in range(env.num_rocks):
                if self._rock_positions[k] == pos and not sampled[k]:
                    sampled2 = sampled.copy()
                    sampled2[k] = True
                    bel2 = bel.copy()
                    bel2[k] = 0.5
                    reward += env.good_rock_reward if quals[k] == 1 else env.bad_rock_penalty
                    break
            return reward, 2, pos, sampled2, bel2, False

        return env.move_cost + env.exit_reward, 2, pos, sampled, bel, True

    def _rollout(self, quals, pos, sampled, bel, depth, depth_bound) -> float:
        total = 0.0
        gamma_power = 1.0
        for _ in range(depth, depth_bound):
            action = self._rollout_action(quals, pos, sampled, bel)
            reward, _obs, pos, sampled, bel, terminal = self._sim_step(
                action, quals, pos, sampled, bel
            )
            total += gamma_power * reward
            gamma_power *= self.discount
            if terminal:
                return total
        return total + gamma_power * self._leaf_estimate(pos, bel, sampled)

    def _rollout_action(self, quals, pos, sampled, bel) -> int:
        """Rollout policy.

        Every mode except "hindsight" reads only the simulated belief ``bel``,
        which is a deterministic function of the simulated history and is
        therefore history-measurable in the sense Silver and Veness's
        convergence argument requires.
        """
        env = self.env
        if self.rollout_policy == "random":
            actions = self._legal_actions(pos, sampled)
            return int(actions[self._rng.randint(0, len(actions))])

        if self.rollout_policy == "hindsight":
            scores = np.asarray(quals, dtype=float)
            check_floor = self.ROLLOUT_CHECK_ACCURACY_PREFERRED
        else:
            scores = bel
            check_floor = (
                self.ROLLOUT_CHECK_ACCURACY_APPROACH
                if self.rollout_policy == "approach"
                else self.ROLLOUT_CHECK_ACCURACY_PREFERRED
            )

        for k in range(env.num_rocks):
            if (
                not sampled[k]
                and self._rock_positions[k] == pos
                and scores[k] >= self.ROLLOUT_SAMPLE_THRESHOLD
            ):
                return env.sample_action

        best_target = None
        best_dist = float("inf")
        for k in range(env.num_rocks):
            if sampled[k] or scores[k] < self.ROLLOUT_SAMPLE_THRESHOLD:
                continue
            dist = abs(pos[0] - self._rock_positions[k][0]) + abs(
                pos[1] - self._rock_positions[k][1]
            )
            if dist < best_dist:
                best_dist = dist
                best_target = k
        if best_target is not None:
            return _move_toward_common(env, pos, self._rock_positions[best_target])

        # Only rocks that are still unresolved are worth a check. A rock whose
        # belief has fallen below the write-off threshold is treated as bad and
        # abandoned. Without that cutoff the policy checks written-off rocks
        # forever and never reaches the exit, which is the same step-cap
        # truncation the Flat-MC baseline exhibits.
        best_k = None
        best_score = 0.0
        for k in range(env.num_rocks):
            if sampled[k] or not (
                self.ROLLOUT_WRITE_OFF_THRESHOLD
                <= scores[k]
                < self.ROLLOUT_SAMPLE_THRESHOLD
            ):
                continue
            dist = abs(pos[0] - self._rock_positions[k][0]) + abs(
                pos[1] - self._rock_positions[k][1]
            )
            score = scores[k] / (1.0 + dist)
            if score > best_score:
                best_score = score
                best_k = k

        if best_k is not None:
            if self.rollout_policy == "hindsight":
                return _move_toward_common(env, pos, self._rock_positions[best_k])
            if self._check_accuracy(pos, best_k) >= check_floor:
                return env.NUM_MOVE_ACTIONS + best_k
            return _move_toward_common(env, pos, self._rock_positions[best_k])

        return env.exit_action

    def _leaf_estimate(self, pos, bel, sampled) -> float:
        """Value of a branch truncated at the depth bound.

        The default is the exact value of the guaranteed continuation "exit on
        the next step", which is available from any cell because
        ``RockSampleEnv.exit_action`` is position-independent. It requires no
        rock knowledge, so it imports no advantage the other agents lack, and
        it is consistent between the tree bound and the rollout tail. An
        inconsistency there is what produced the exit-at-step-one collapse.
        """
        if self.leaf_value == "zero":
            return 0.0
        if self.leaf_value == "greedy_belief":
            return self._greedy_belief_value(pos, bel, sampled)
        return self.env.exit_reward + self.env.move_cost

    def _greedy_belief_value(self, pos, bel, sampled) -> float:
        env = self.env
        value = 0.0
        sim_pos = pos
        sim_sampled = np.asarray(sampled).copy()

        for _ in range(env.num_rocks):
            best_k = None
            best_score = -float("inf")
            for k in range(env.num_rocks):
                if sim_sampled[k]:
                    continue
                ev = bel[k] * env.good_rock_reward + (1 - bel[k]) * env.bad_rock_penalty
                if ev <= 0:
                    continue
                dist = abs(sim_pos[0] - self._rock_positions[k][0]) + abs(
                    sim_pos[1] - self._rock_positions[k][1]
                )
                score = ev - dist * abs(env.move_cost)
                if score > best_score:
                    best_score = score
                    best_k = k
            if best_k is None:
                break
            dist = abs(sim_pos[0] - self._rock_positions[best_k][0]) + abs(
                sim_pos[1] - self._rock_positions[best_k][1]
            )
            ev = bel[best_k] * env.good_rock_reward + (1 - bel[best_k]) * env.bad_rock_penalty
            value += env.move_cost * dist + ev + env.move_cost
            sim_pos = self._rock_positions[best_k]
            sim_sampled[best_k] = True

        return value + env.exit_reward + env.move_cost

    # ------------------------------------------------------------------
    # Model helpers
    # ------------------------------------------------------------------

    def _apply_move(self, pos, action) -> Tuple[int, int]:
        env = self.env
        r, c = pos
        if action == env.MOVE_N:
            r = max(0, r - 1)
        elif action == env.MOVE_S:
            r = min(env.grid_size - 1, r + 1)
        elif action == env.MOVE_E:
            c = min(env.grid_size - 1, c + 1)
        elif action == env.MOVE_W:
            c = max(0, c - 1)
        return (r, c)

    def _check_accuracy(self, pos, rock_idx) -> float:
        key = (pos, rock_idx)
        cached = self._acc_cache.get(key)
        if cached is not None:
            return cached
        env = self.env
        rock_pos = self._rock_positions[rock_idx]
        dist = math.sqrt(
            (pos[0] - rock_pos[0]) ** 2 + (pos[1] - rock_pos[1]) ** 2
        )
        accuracy = env.check_base_accuracy * (
            0.5 ** (dist / env.half_efficiency_distance)
        )
        accuracy = max(0.5, min(accuracy, env.check_base_accuracy))
        self._acc_cache[key] = accuracy
        return accuracy

    # ------------------------------------------------------------------
    # Belief representation
    # ------------------------------------------------------------------

    def _sample_particle(self) -> np.ndarray:
        if self.belief_mode == "particle":
            if not self._particles:
                return (self._rng.random(self.env.num_rocks) < 0.5).astype(np.int8)
            idx = self._rng.randint(0, len(self._particles))
            return np.asarray(self._particles[idx], dtype=np.int8)
        return (self._rng.random(self.env.num_rocks) < self.belief.rock_beliefs).astype(
            np.int8
        )

    def _update_particles(self, action, observation):
        """Literal POMCP particle update by rejection sampling.

        Only check actions carry information. Particles are filtered against
        the realised observation, topped back up by rejection sampling from
        the pre-observation set, and reinvigorated if the set has collapsed.
        """
        env = self.env
        if not (
            env.NUM_MOVE_ACTIONS <= action < env.NUM_MOVE_ACTIONS + env.num_rocks
        ):
            return

        k = action - env.NUM_MOVE_ACTIONS
        accuracy = self._check_accuracy(env._agent_pos, k)
        pool = self._particles

        survivors = [p for p in pool if self._obs_matches(p, k, accuracy, observation)]
        if not survivors:
            self._particles = self._reinvigorate_from_belief()
            return

        attempts = 0
        max_attempts = 20 * self.num_particles
        while len(survivors) < self.num_particles and attempts < max_attempts:
            attempts += 1
            candidate = pool[self._rng.randint(0, len(pool))]
            if self._obs_matches(candidate, k, accuracy, observation):
                survivors.append(candidate)

        if len(survivors) < max(1, self.num_particles // 4):
            survivors = self._reinvigorate(survivors)

        self._particles = survivors[: self.num_particles]

    def _obs_matches(self, particle, k, accuracy, observation) -> bool:
        true_q = int(particle[k])
        simulated = true_q if self._rng.random() < accuracy else 1 - true_q
        return simulated == observation

    def _reinvigorate(self, survivors) -> List[Tuple[int, ...]]:
        self._num_reinvigorations += 1
        K = self.env.num_rocks
        out = list(survivors)
        marginals = self.belief.rock_beliefs
        while len(out) < self.num_particles:
            base = list(survivors[self._rng.randint(0, len(survivors))])
            for k in range(K):
                if 0.02 <= marginals[k] <= 0.98 and self._rng.random() < 1.0 / K:
                    base[k] = 1 - base[k]
            out.append(tuple(base))
        return out

    def _reinvigorate_from_belief(self) -> List[Tuple[int, ...]]:
        self._num_reinvigorations += 1
        return [
            tuple(
                int(b)
                for b in (self._rng.random(self.env.num_rocks) < self.belief.rock_beliefs)
            )
            for _ in range(self.num_particles)
        ]

    def _advance_root(self, action, observation):
        if self._root is None:
            return
        self._root = self._root.obs_children.get((action, observation))
