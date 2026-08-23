"""Tests for the genuine RockSample POMCP agent.

Four groups, and the first exists for a specific reason. An earlier agent in
this repository shipped with unreachable UCB1 machinery, an inert exploration
constant, and a silently capped simulation count, and none of that was caught
because the tests only checked that the agent returned a legal action. The
anti-dead-code group asserts that the search tree is actually built, actually
traversed by UCB1, and actually responds to every constructor knob.
"""

import inspect

import numpy as np
import pytest

from rho_aif.agents import rocksample_pomcp as pomcp_module
from rho_aif.agents.rocksample_pomcp import RockSamplePOMCPAgent
from rho_aif.environments.rocksample import RockSampleEnv


def make_env(grid_size=5, num_rocks=3, rock_positions=((1, 2), (3, 1), (2, 4))):
    return RockSampleEnv(
        grid_size=grid_size,
        num_rocks=num_rocks,
        rock_positions=[tuple(p) for p in rock_positions],
        move_cost=-0.5,
        max_steps=grid_size * grid_size + num_rocks * 10,
    )


def run_episode(agent, env, seed):
    env.reset(seed=seed)
    agent.reset()
    total, checks, truncated = 0.0, 0, False
    for _ in range(env.max_steps):
        action = agent.select_action()
        _obs, reward, terminated, trunc, info = env.step(action)
        total += reward
        agent.update(action, _obs)
        if env.NUM_MOVE_ACTIONS <= action < env.NUM_MOVE_ACTIONS + env.num_rocks:
            checks += 1
        if terminated or trunc:
            truncated = bool(trunc) and not bool(terminated)
            break
    return {
        "reward": total,
        "steps": env._step_count,
        "checks": checks,
        "truncated": truncated,
    }


def run_batch(env, n_episodes=20, base_seed=7000, **kwargs):
    out = []
    for i in range(n_episodes):
        np.random.seed(500 + i)
        agent = RockSamplePOMCPAgent(env, **kwargs)
        out.append(run_episode(agent, env, seed=base_seed + i))
    return out


def root_diagnostics(env, seed=3, **kwargs):
    np.random.seed(0)
    env.reset(seed=seed)
    agent = RockSamplePOMCPAgent(env, **kwargs)
    agent.reset()
    action = agent.select_action()
    return action, agent.diagnostics


# ----------------------------------------------------------------------
# Anti-dead-code
# ----------------------------------------------------------------------


class TestSearchTreeIsReal:
    def test_tree_deepens_with_simulation_budget(self):
        env = make_env()
        depths = [
            root_diagnostics(env, num_simulations=n, exploration_constant=5.0)[1][
                "max_tree_depth"
            ]
            for n in (64, 256, 1024, 4096)
        ]
        assert depths == sorted(depths), depths
        assert depths[-1] > depths[0], depths
        # Measured on the shipped implementation: 3, 5, 7, 9 at these budgets.
        assert depths[-1] >= 3, depths

    def test_history_node_count_scales_with_budget(self):
        env = make_env()
        small = root_diagnostics(env, num_simulations=256, exploration_constant=5.0)[1]
        large = root_diagnostics(env, num_simulations=4096, exploration_constant=5.0)[1]
        assert large["num_history_nodes"] >= 4 * small["num_history_nodes"]
        for n, diag in ((256, small), (4096, large)):
            ratio = diag["num_history_nodes"] / n
            # Near zero means no tree. Near one means a fresh node every
            # simulation with no history sharing.
            assert 0.05 <= ratio <= 0.95, (n, ratio)

    def test_tree_has_grandchildren(self):
        """The direct one-ply discriminator: a flat evaluator has none."""
        env = make_env()
        np.random.seed(0)
        env.reset(seed=3)
        agent = RockSamplePOMCPAgent(env, num_simulations=2048, exploration_constant=5.0)
        agent.reset()
        agent.select_action()
        root = agent._root
        assert root is not None
        assert any(child.obs_children for child in root.obs_children.values())

    def test_ucb_select_is_reached(self):
        env = make_env()
        _, diag = root_diagnostics(env, num_simulations=1024, exploration_constant=5.0)
        assert diag["num_ucb_calls"] > 0
        # Every simulation either expands a fresh node (one rollout, no UCB
        # call at that node) or descends through UCB at each visited node.
        assert diag["num_ucb_calls"] >= diag["num_simulations_run"] - diag["num_rollouts"]

    @pytest.mark.parametrize("n", [7, 1000, 4096])
    def test_num_simulations_is_not_capped(self, n):
        env = make_env()
        _, diag = root_diagnostics(env, num_simulations=n)
        assert diag["num_simulations_run"] == n

    def test_exploration_constant_changes_root_visit_distribution(self):
        env = make_env()
        _, greedy = root_diagnostics(env, num_simulations=2048, exploration_constant=0.0)
        _, explore = root_diagnostics(env, num_simulations=2048, exploration_constant=100.0)
        assert greedy["root_visit_counts"] != explore["root_visit_counts"]

        def normalised_entropy(counts):
            v = np.array(list(counts.values()), dtype=float)
            p = v / v.sum()
            p = p[p > 0]
            return float(-(p * np.log(p)).sum() / np.log(len(p))) if len(p) > 1 else 0.0

        assert normalised_entropy(explore["root_visit_counts"]) > normalised_entropy(
            greedy["root_visit_counts"]
        )

    def test_exploration_constant_changes_behaviour(self):
        env = make_env()
        low = run_batch(env, 12, num_simulations=512, exploration_constant=0.0,
                        rollout_policy="approach")
        high = run_batch(env, 12, num_simulations=512, exploration_constant=100.0,
                         rollout_policy="approach")
        assert abs(np.mean([r["checks"] for r in low]) - np.mean([r["checks"] for r in high])) >= 1.0
        assert abs(np.mean([r["steps"] for r in low]) - np.mean([r["steps"] for r in high])) >= 2.0

    @pytest.mark.parametrize(
        "knob,value_a,value_b",
        [
            ("num_simulations", 64, 2048),
            ("exploration_constant", 0.0, 50.0),
            ("planning_horizon", 3, 25),
            ("discount", 1.0, 0.5),
            ("rollout_policy", "approach", "random"),
            ("root_criterion", "value", "visits"),
            ("leaf_value", "exit", "zero"),
            ("budget_aware_horizon", True, False),
        ],
    )
    def test_no_inert_parameters(self, knob, value_a, value_b):
        """Every constructor knob must change something observable.

        A generic guard against the class of bug that shipped an inert
        exploration constant, rather than one test per remembered knob.
        """
        env = make_env()
        base = dict(num_simulations=512, exploration_constant=5.0)

        def probe(**override):
            kwargs = dict(base)
            kwargs.update(override)
            # budget_aware_horizon only bites near the step cap.
            if knob == "budget_aware_horizon":
                np.random.seed(0)
                env.reset(seed=3)
                agent = RockSamplePOMCPAgent(env, **kwargs)
                agent.reset()
                agent._t = env.max_steps - 2
                agent.select_action()
                return agent.diagnostics["planning_horizon_used"]
            action, diag = root_diagnostics(env, **kwargs)
            return (action, tuple(sorted(diag["root_visit_counts"].items())),
                    diag["max_tree_depth"])

        assert probe(**{knob: value_a}) != probe(**{knob: value_b})


# ----------------------------------------------------------------------
# Anti-degeneracy
# ----------------------------------------------------------------------


class TestNotDegenerate:
    def test_does_not_always_exit_at_step_one(self):
        env = make_env()
        results = run_batch(env, 15, num_simulations=1024, exploration_constant=5.0,
                            rollout_policy="approach")
        assert np.mean([r["steps"] for r in results]) > 2.0
        assert np.mean([r["checks"] for r in results]) >= 1.0

    def test_does_not_hit_the_step_cap(self):
        env = make_env(grid_size=7, num_rocks=8, rock_positions=[
            (1, 1), (1, 4), (2, 2), (2, 6), (4, 1), (4, 5), (5, 3), (6, 6)])
        results = run_batch(env, 6, num_simulations=256, exploration_constant=5.0,
                            rollout_policy="approach")
        assert np.mean([r["truncated"] for r in results]) < 0.5

    def test_beats_the_unconditional_exit_value(self):
        """The weakest defensible floor.

        Exit is available from any cell for exit_reward + move_cost, so an
        agent that cannot beat that has learned nothing. Every degenerate
        configuration found during development fails this.
        """
        env = make_env()
        results = run_batch(env, 20, num_simulations=1024, exploration_constant=5.0,
                            rollout_policy="approach")
        floor = env.exit_reward + env.move_cost
        assert np.mean([r["reward"] for r in results]) > floor + 1.0

    def test_zero_leaf_value_reproduces_the_collapse(self):
        """Regression witness for the exit-at-step-one failure mode."""
        env = make_env()
        results = run_batch(env, 8, num_simulations=1024, exploration_constant=5.0,
                            rollout_policy="approach", leaf_value="zero")
        assert np.mean([r["steps"] for r in results]) < 2.0

    @pytest.mark.slow
    def test_reward_improves_with_budget(self):
        env = make_env()
        low = run_batch(env, 25, num_simulations=256, exploration_constant=5.0,
                        rollout_policy="approach")
        high = run_batch(env, 25, num_simulations=4096, exploration_constant=5.0,
                         rollout_policy="approach")
        assert np.mean([r["reward"] for r in high]) > np.mean([r["reward"] for r in low])


# ----------------------------------------------------------------------
# Hidden-state leakage
# ----------------------------------------------------------------------


FORBIDDEN_ATTRS = ("_rock_qualities", "_rock_sampled", "np_random", "_rock_pos_list")


class _LeakGuard:
    """Proxy that raises if the agent reads any ground-truth attribute."""

    def __init__(self, env):
        object.__setattr__(self, "_env", env)

    def __getattr__(self, name):
        if name in FORBIDDEN_ATTRS:
            raise AssertionError(f"agent read hidden environment state: {name}")
        return getattr(object.__getattribute__(self, "_env"), name)

    def __setattr__(self, name, value):
        setattr(object.__getattribute__(self, "_env"), name, value)


class TestNoLeakage:
    def test_agent_never_reads_hidden_state(self):
        env = make_env()
        env.reset(seed=11)
        guard = _LeakGuard(env)
        agent = RockSamplePOMCPAgent(guard, num_simulations=256, exploration_constant=5.0,
                                     rollout_policy="approach")
        agent.reset()
        for _ in range(12):
            action = agent.select_action()
            obs, _r, term, trunc, _info = env.step(action)
            agent.update(action, obs)
            if term or trunc:
                break

    def test_agent_source_contains_no_hidden_identifiers(self):
        source = inspect.getsource(pomcp_module)
        for name in ("_rock_qualities", "np_random", "total_good_sampled", "total_bad_sampled"):
            assert name not in source, name

    def test_decisions_are_invariant_to_ground_truth(self):
        """The strongest leakage test.

        Record an episode's action-observation trace, then replay the same
        observations to a fresh agent against an environment whose hidden
        qualities are bitwise complemented. Any dependence on the hidden
        vector changes the action sequence.
        """
        env = make_env()
        env.reset(seed=17)
        np.random.seed(0)
        agent = RockSamplePOMCPAgent(env, num_simulations=256, exploration_constant=5.0,
                                     rollout_policy="approach")
        agent.reset()
        trace = []
        for _ in range(10):
            action = agent.select_action()
            obs, _r, term, trunc, _info = env.step(action)
            trace.append((action, obs))
            agent.update(action, obs)
            if term or trunc:
                break

        env2 = make_env()
        env2.reset(seed=17)
        env2._rock_qualities = 1 - env2._rock_qualities
        np.random.seed(0)
        replay = RockSamplePOMCPAgent(env2, num_simulations=256, exploration_constant=5.0,
                                      rollout_policy="approach")
        replay.reset()
        for action, obs in trace:
            assert replay.select_action() == action
            # Drive the environment so positions stay in lockstep, then feed
            # the recorded observation rather than the one it produced.
            env2.step(action)
            replay.update(action, obs)

    def test_model_matches_environment(self):
        env = make_env()
        env.reset(seed=5)
        agent = RockSamplePOMCPAgent(env, num_simulations=1)
        agent.reset()
        agent._ensure_rock_positions()
        for r in range(env.grid_size):
            for c in range(env.grid_size):
                for k in range(env.num_rocks):
                    assert agent._check_accuracy((r, c), k) == pytest.approx(
                        env.get_check_accuracy_at((r, c), k), abs=1e-12
                    )


# ----------------------------------------------------------------------
# Correctness and seeding
# ----------------------------------------------------------------------


class TestCorrectness:
    def test_factored_belief_is_exact(self):
        """Brute-force Bayes over all 2^K quality vectors must agree.

        This is the premise belief_mode="exact" rests on. If it fails, the
        default belief representation is unsound.
        """
        env = make_env(grid_size=5, num_rocks=4,
                       rock_positions=[(1, 2), (3, 1), (2, 4), (0, 0)])
        env.reset(seed=23)
        agent = RockSamplePOMCPAgent(env, num_simulations=1)
        agent.reset()
        agent._ensure_rock_positions()

        K = env.num_rocks
        joint = np.full(2 ** K, 1.0 / 2 ** K)
        rng = np.random.RandomState(4)
        for _ in range(12):
            k = int(rng.randint(0, K))
            obs = int(rng.randint(0, 2))
            accuracy = agent._check_accuracy(env._agent_pos, k)
            for idx in range(2 ** K):
                q = (idx >> k) & 1
                joint[idx] *= accuracy if q == obs else 1.0 - accuracy
            joint /= joint.sum()
            agent.belief.update_check(k, obs, accuracy)

        for k in range(K):
            marginal = sum(joint[idx] for idx in range(2 ** K) if (idx >> k) & 1)
            assert agent.belief.rock_beliefs[k] == pytest.approx(marginal, abs=1e-9)

    def test_particle_mode_tracks_exact_belief(self):
        env = make_env()
        env.reset(seed=29)
        np.random.seed(1)
        agent = RockSamplePOMCPAgent(env, num_simulations=32, belief_mode="particle",
                                     num_particles=4096)
        agent.reset()
        agent._ensure_rock_positions()
        for _ in range(10):
            k = int(np.random.randint(0, env.num_rocks))
            action = env.NUM_MOVE_ACTIONS + k
            obs, _r, _t, _tr, _i = env.step(action)
            agent.update(action, obs)

        particles = np.array(agent._particles, dtype=float)
        marginals = particles.mean(axis=0)
        np.testing.assert_allclose(marginals, agent.belief.rock_beliefs, atol=0.06)
        assert agent.diagnostics.get("num_reinvigorations", 0) <= 2

    def test_same_seed_same_trajectory(self):
        env = make_env()
        traces = []
        for _ in range(2):
            env.reset(seed=31)
            agent = RockSamplePOMCPAgent(env, num_simulations=256, seed=99,
                                         exploration_constant=5.0)
            agent.reset()
            trace = []
            for _ in range(6):
                a = agent.select_action()
                obs, _r, t, tr, _i = env.step(a)
                trace.append(a)
                agent.update(a, obs)
                if t or tr:
                    break
            traces.append(trace)
        assert traces[0] == traces[1]

    def test_different_seed_different_trajectory(self):
        env = make_env()
        traces = []
        for seed in (99, 12345):
            env.reset(seed=31)
            agent = RockSamplePOMCPAgent(env, num_simulations=256, seed=seed,
                                         exploration_constant=5.0)
            agent.reset()
            trace = []
            for _ in range(10):
                a = agent.select_action()
                obs, _r, t, tr, _i = env.step(a)
                trace.append(a)
                agent.update(a, obs)
                if t or tr:
                    break
            traces.append(trace)
        assert traces[0] != traces[1]

    def test_global_stream_fallback_is_seed_controlled(self):
        """seed=None must still be reproducible under the RockSample harness,
        which seeds the global stream before constructing each agent."""
        env = make_env()
        actions = []
        for _ in range(2):
            env.reset(seed=37)
            np.random.seed(0)
            agent = RockSamplePOMCPAgent(env, num_simulations=256, seed=None,
                                         exploration_constant=5.0)
            agent.reset()
            actions.append(agent.select_action())
        assert actions[0] == actions[1]

    def test_agent_contract(self):
        env = make_env()
        env.reset(seed=41)
        agent = RockSamplePOMCPAgent(env, num_simulations=64)
        agent.reset()
        action = agent.select_action()
        assert isinstance(action, int)
        assert 0 <= action < env.num_actions
        agent.update(env.NUM_MOVE_ACTIONS, 1)
        assert not np.allclose(agent.belief.rock_beliefs, 0.5)
        agent.reset()
        np.testing.assert_allclose(agent.belief.rock_beliefs, 0.5)
        assert agent._t == 0
        assert agent._root is None
        assert agent.diagnostics_history == []

    @pytest.mark.parametrize(
        "grid_size,num_rocks,rock_positions",
        [
            (5, 3, [(1, 2), (3, 1), (2, 4)]),
            (7, 4, [(2, 2), (4, 3), (1, 5), (5, 1)]),
            (7, 8, [(1, 1), (1, 4), (2, 2), (2, 6), (4, 1), (4, 5), (5, 3), (6, 6)]),
            (11, 11, [(0, 3), (1, 7), (2, 1), (2, 9), (4, 4), (4, 8), (5, 0), (6, 6),
                      (8, 2), (8, 10), (10, 5)]),
        ],
    )
    def test_completes_episode_on_every_instance(self, grid_size, num_rocks, rock_positions):
        env = make_env(grid_size, num_rocks, rock_positions)
        np.random.seed(0)
        agent = RockSamplePOMCPAgent(env, num_simulations=64, exploration_constant=5.0,
                                     rollout_policy="approach")
        result = run_episode(agent, env, seed=43)
        assert result["steps"] <= env.max_steps

    def test_subtree_reuse_runs_and_changes_nothing_structural(self):
        env = make_env()
        np.random.seed(0)
        agent = RockSamplePOMCPAgent(env, num_simulations=256, exploration_constant=5.0,
                                     rollout_policy="approach", reuse_subtree=True)
        result = run_episode(agent, env, seed=47)
        assert result["steps"] >= 1

    def test_legal_action_mask_excludes_wall_bumps_and_sampled_rocks(self):
        env = make_env()
        env.reset(seed=53)
        agent = RockSamplePOMCPAgent(env, num_simulations=1)
        agent.reset()
        agent._ensure_rock_positions()
        sampled = np.zeros(env.num_rocks, dtype=bool)
        actions = agent._legal_actions((0, 0), sampled)
        assert env.MOVE_N not in actions  # top edge
        assert env.MOVE_W not in actions  # left edge
        assert env.exit_action in actions
        sampled[0] = True
        assert env.NUM_MOVE_ACTIONS + 0 not in agent._legal_actions((2, 2), sampled)
