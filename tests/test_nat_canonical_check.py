"""The nat-canonical weight check must reproduce the Pareto sweep's protocol.

experiments/run_nat_canonical_check.py exists to close one specific gap: the
Pareto sweep never evaluated w = ln(2), the weight at which the bit-computing
implementation coincides with Proposition 1's nat-stated identity. Its result
is only comparable to the sweep's reward-maximizing tied brackets if it runs
the same environments at the same parameters and horizons. This test pins
the weight and the protocol, and reads run_pareto.py's source so a change to
the sweep's environment parameters that is not mirrored here fails loudly.
"""
import math
import re
from pathlib import Path

import pytest

from run_nat_canonical_check import ENVS, W_NAT_CANONICAL

ROOT = Path(__file__).resolve().parents[1]
PARETO_SRC = (ROOT / "experiments" / "run_pareto.py").read_text()


def test_weight_is_exactly_ln2():
    assert W_NAT_CANONICAL == math.log(2)
    assert abs(W_NAT_CANONICAL - 0.6931471805599453) < 1e-15


@pytest.mark.parametrize(
    "env_name, horizon, literals",
    [
        ("Tiger", 6, ["listen_accuracy=0.85", "listen_cost=1.0",
                      "correct_reward=10.0", "incorrect_penalty=-100.0"]),
        ("Testbed", 4, ["observation_accuracy=0.75", "observation_cost=0.1",
                        "correct_reward=1.0", "incorrect_penalty=-1.0"]),
        ("Diagnosis", 3, ["num_conditions=4", "test_accuracy=0.80", "test_cost=1.0",
                          "correct_reward=10.0", "incorrect_penalty=-50.0"]),
        ("Bandit", 2, ["num_arms=4", "inspect_accuracy=0.80", "inspect_cost=0.5",
                       "correct_reward=10.0", "small_reward=1.0"]),
        ("Tileworld", 2, ["TileworldEnv(grid_size=6)"]),
    ],
)
def test_protocol_matches_pareto_sweep(env_name, horizon, literals):
    env, h = ENVS[env_name]
    assert h == horizon
    # The sweep's __main__ block constructs each environment with these exact
    # literals; if run_pareto.py drifts, this check no longer reproduces it.
    for lit in literals:
        assert lit in PARETO_SRC, f"{lit!r} no longer appears in run_pareto.py"
    # And the horizon the sweep uses for this environment.
    block = re.search(rf'"{env_name}": \(\s*\w+Env\(.*?\),\s*(\d+)\s*\)',
                      PARETO_SRC, re.DOTALL)
    assert block is not None, f"could not locate {env_name} in run_pareto.py envs_config"
    assert int(block.group(1)) == horizon


def test_env_objects_carry_the_sweep_parameters():
    tiger, _ = ENVS["Tiger"]
    assert tiger.listen_accuracy == 0.85 and tiger.listen_cost == 1.0
    assert tiger.correct_reward == 10.0 and tiger.incorrect_penalty == -100.0
    diag, _ = ENVS["Diagnosis"]
    assert diag.num_conditions == 4 and diag.test_accuracy == 0.80
    bandit, _ = ENVS["Bandit"]
    assert bandit.num_arms == 4 and bandit.inspect_accuracy == 0.80
    assert bandit.inspect_cost == 0.5 and bandit.small_reward == 1.0
    tw, _ = ENVS["Tileworld"]
    assert tw.grid_size == 6
    tb, _ = ENVS["Testbed"]
    assert type(tb).__name__ == "InfoSeekingEnv"
    assert tb.observation_accuracy == 0.75 and tb.observation_cost == 0.1


def test_all_five_swept_environments_are_covered():
    assert set(ENVS) == {"Tiger", "Testbed", "Diagnosis", "Bandit", "Tileworld"}
