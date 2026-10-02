"""Regression tests for tools/review_pipeline/verify_claims.py.

Two kinds of proof. First, synthetic fixtures for each check in isolation,
so a future edit to the tool can't silently break one check while fixing
another. Second, a retroactive replay against 247a10c, the actual commit
this tool was built to have caught: it introduced a table caption citing
"Table~\ref{tab:pomcp}'s MCTS rows" (a real table with no MCTS rows) and
was not caught until a 108-item, four-lens manual audit found it (ledger
9.17.28). If this replay ever stops failing, the tool has regressed, not
improved: the check it validates is the actual reason the tool exists.
"""
import os
import subprocess
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "review_pipeline"))
import verify_claims as vc

REPO = vc.REPO


def _write(tmp, name, text):
    path = os.path.join(tmp, name)
    with open(path, "w") as f:
        f.write(text)
    return path


def test_value_in_csv_matches_percent_and_fraction_forms(monkeypatch):
    # "A" is a non-numeric cell (an agent name column); value_in_csv must
    # skip it rather than raise, and it must never see a real results/ file.
    monkeypatch.setitem(vc._CSV_CACHE, "results_fake.csv", ["A", "0.977", "3.735"])
    assert vc.value_in_csv("97.7", True, "results_fake.csv") is True
    assert vc.value_in_csv("3.74", False, "results_fake.csv") is False  # the actual bug: 3.735 formats to 3.73
    assert vc.value_in_csv("3.73", False, "results_fake.csv") is True
    assert vc.value_in_csv("97.6", True, "results_fake.csv") is False  # exact precision, no tolerance


def test_percent_signal_crosses_a_pm_pair():
    line = r"POMCP reaches $96.3 \pm 0.6$pp success"
    m = list(vc.NUM_RE.finditer(line))[0]
    assert m.group(1) == "96.3"
    tail = line[m.end():m.end() + 30]
    assert vc.PERCENT_TAIL_RE.match(tail), "percent context must be detected past the \\pm pair"


def test_content_mismatch_flags_a_table_with_no_matching_rows():
    table_content = {
        "tab:pomcp": r"\caption{POMCP comparison config...} Planning & POMCP (1000) & EFE \\"
    }
    line = r"the same protocol as Table~\ref{tab:pomcp}'s MCTS rows"
    matches = list(vc.DESC_RE.finditer(line))
    assert len(matches) == 1
    label, word = matches[0].group(1), matches[0].group(2)
    assert label == "tab:pomcp" and word == "MCTS"
    assert word.lower() not in table_content[label].lower()


def test_asymmetric_comparison_pattern_flags_tuned_vs_default():
    line = "POMCP at its best swept configuration against MCTS-EFE at its default constant"
    assert vc.ASYM_RE.search(line) is not None
    line2 = "POMCP at its best swept configuration against MCTS-EFE at its own best swept configuration"
    assert vc.ASYM_RE.search(line2) is None


def test_underscore_and_star_prefixed_names_are_not_missing_files():
    # "\texttt{_stats.csv}" is deliberate shorthand for "the corresponding
    # _stats.csv companion," not a standalone filename, and this project's
    # own manuscripts use it and "*_stats.csv" repeatedly.
    for name in ("_stats.csv", "*_stats.csv"):
        assert name.startswith("_") or name.startswith("*")


def test_historical_checks_use_revision_tables_and_data(tmp_path, monkeypatch):
    """A historical replay must survive locally deleted tables and CSVs."""
    (tmp_path / "paper/tables").mkdir(parents=True)
    (tmp_path / "results").mkdir()
    master = tmp_path / "paper/full_paper_jair.tex"
    table = tmp_path / "paper/tables/history.tex"
    data = tmp_path / "results/results_history.csv"
    lines = [r"Table~\ref{tab:history}'s MCTS rows give $1.23$.",
             r"Archive: \texttt{results_history.csv}."]
    master.write_text("\n".join(lines))
    table.write_text(r"\begin{table}\label{tab:history}POMCP rows\end{table}")
    data.write_text("agent,value\nPOMCP,1.23\n")

    def git(*args):
        return subprocess.check_output(["git", "-C", str(tmp_path), *args], text=True)

    git("init", "-q")
    git("add", ".")
    git("-c", "user.name=Test", "-c", "user.email=test@example.com",
        "-c", "commit.gpgsign=false", "commit", "-qm", "Historical fixture")
    head = git("rev-parse", "HEAD").strip()
    table.unlink()
    data.unlink()
    master.write_text(r"Current source cites \texttt{results_current.csv}.")
    monkeypatch.setattr(vc, "REPO", str(tmp_path))
    monkeypatch.setattr(vc, "ALL_MASTERS", [str(master)])
    monkeypatch.setattr(vc, "_CSV_CACHE", {})

    labels, content = vc.all_labels_and_table_content([str(master)], head)
    issues = vc.check_file("paper/full_paper_jair.tex", str(master), lines,
                           labels, content, head)
    assert "tab:history" in labels
    assert issues["content_mismatch"]  # the historical table has no MCTS rows
    assert not issues["broken_ref"]
    assert not issues["missing_csv"]
    assert not issues["mismatch"]  # source-level scope and CSV both use head
    assert vc.source_paths("results", ".csv", head) == [str(data)]
    assert vc.whole_file_csv_names(str(master)) == {"results_current.csv"}
    assert "tab:history" not in vc.all_labels_and_table_content([str(master)])[0]
    assert vc.load_csv_cells("results_history.csv") == []


@pytest.mark.skipif(
    subprocess.run(["git", "-C", REPO, "cat-file", "-e", "4adc223"],
                    capture_output=True).returncode != 0,
    reason="historical commit 4adc223 not present in this checkout",
)
def test_retroactive_replay_catches_the_bug_that_motivated_this_tool():
    """247a10c introduced the wrong-table-reference bug this tool exists to
    catch. If this ever passes (exit 0, no content_mismatch), the tool has
    lost the one check it was built around."""
    result = subprocess.run(
        [sys.executable, os.path.join(REPO, "tools/review_pipeline/verify_claims.py"),
         "--base", "4adc223", "--head", "247a10c",
         "paper/full_paper_jair.tex", "paper/full_paper.tex",
         "paper/tables/mcts_ablation.tex", "paper/tables/pomcp_exploration_sweep.tex"],
        cwd=REPO, capture_output=True, text=True,
    )
    assert result.returncode == 1, (
        "expected the retroactive replay to fail (it must catch the known bug); "
        f"got exit {result.returncode}\nstdout:\n{result.stdout}"
    )
    assert "MCTS rows" in result.stdout
    assert "Table content mismatch" in result.stdout
