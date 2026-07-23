"""
Stage F: tests for the SARSOP .pomdp exporter and alpha-vector policy agent.

These tests do not require the pomdpsol binary; they cover the export format,
the policy XML parser, and greedy alpha-vector action selection.
"""

import numpy as np
import pytest

from run_sarsop_baseline import (
    AlphaVectorAgent,
    parse_policy,
    write_pomdp_file,
)
from rho_aif.benchmark import get_benchmark, get_obs_models, make_env_config


class TestPomdpExport:
    def test_tiger_export_shape_and_contents(self, tmp_path):
        env = get_benchmark("Tiger").env_factory()
        path = tmp_path / "tiger.pomdp"
        info = write_pomdp_file(env, path)
        assert info["n_states"] == 2
        assert info["n_commit"] == 2
        assert info["n_obs_actions"] == 1
        text = path.read_text()
        assert "states: s0 s1 done" in text
        assert "actions: obs0 commit0 commit1" in text
        assert "observations: o0 o1 onull" in text
        # Uniform start over hidden states, zero on done
        assert "start: 0.5000000000 0.5000000000 0.0000000000" in text
        # Listen cost and commit payoffs present (commit0 = open door 0,
        # which is wrong when the tiger is behind door 0).
        assert "R: obs0 : s0 : * : * -1.0000000000" in text
        assert "R: commit0 : s0 : * : * -100.0000000000" in text
        assert "R: commit0 : s1 : * : * 10.0000000000" in text

    def test_diagnosis_observation_rows_are_distributions(self, tmp_path):
        env = get_benchmark("Diagnosis").env_factory()
        path = tmp_path / "diag.pomdp"
        write_pomdp_file(env, path)
        # For each obs action and hidden state, O-probabilities sum to 1.
        probs = {}
        for line in path.read_text().splitlines():
            if line.startswith("O: obs"):
                parts = line.split()
                key = (parts[1], parts[3])
                probs.setdefault(key, 0.0)
                probs[key] += float(parts[-1])
        for key, total in probs.items():
            assert total == pytest.approx(1.0), key


class TestPolicyParsing:
    POLICY_XML = """<?xml version="1.0" encoding="ISO-8859-1"?>
<Policy version="0.1" type="value">
<AlphaVector vectorLength="3" numObsValue="1" numVectors="2">
<Vector action="0" obsValue="0">1.0 2.0 0.0 </Vector>
<Vector action="2" obsValue="0">5.0 -3.0 0.0 </Vector>
</AlphaVector>
</Policy>
"""

    def test_parse_policy(self, tmp_path):
        path = tmp_path / "test.policy"
        path.write_text(self.POLICY_XML)
        alphas = parse_policy(path)
        assert len(alphas) == 2
        assert alphas[0][0] == 0
        np.testing.assert_allclose(alphas[1][1], [5.0, -3.0, 0.0])

    def test_alpha_vector_agent_argmax(self, tmp_path):
        path = tmp_path / "test.policy"
        path.write_text(self.POLICY_XML)
        alphas = parse_policy(path)
        env = get_benchmark("Tiger").env_factory()
        agent = AlphaVectorAgent(get_obs_models(env), make_env_config(env), alphas)
        # Uniform belief: values are 1.5 (action 0) vs 1.0 (action 2).
        agent.reset()
        assert agent.select_action() == 0
        # Belief concentrated on state 0: 1.0 vs 5.0 -> action 2.
        agent.belief.belief = np.array([1.0, 0.0])
        assert agent.select_action() == 2
