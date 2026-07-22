"""CLI smoke tests for rho-aif-bench."""

import csv
from pathlib import Path

import pytest

from rho_aif.cli import main


def test_list_exits_zero(capsys):
    assert main(["list"]) == 0
    out = capsys.readouterr().out
    assert "Tiger" in out
    assert "Inspection-N8" in out


def test_run_tiger_smoke(tmp_path, capsys):
    out_csv = tmp_path / "tiger.csv"
    rc = main(
        [
            "run",
            "--env",
            "Tiger",
            "--agent",
            "myopic",
            "--n-seeds",
            "1",
            "--episodes",
            "3",
            "--out",
            str(out_csv),
            "--quiet",
        ]
    )
    assert rc == 0
    assert out_csv.is_file()
    with open(out_csv) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 1
    assert "mean_log_score" in rows[0]
    assert "mean_brier" in rows[0]
    assert rows[0]["environment"] == "Tiger"


def test_run_unknown_agent_raises():
    with pytest.raises(ValueError):
        main(
            [
                "run",
                "--env",
                "Tiger",
                "--agent",
                "not-an-agent",
                "--n-seeds",
                "1",
                "--episodes",
                "1",
                "--quiet",
            ]
        )
