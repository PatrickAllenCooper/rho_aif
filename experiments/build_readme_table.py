#!/usr/bin/env python3
"""
Generate the README "Baseline Results" markdown table from committed CSVs.

The README table drifted from the CSVs once before (a tuned-baseline row was
hand-copied as EFE); regenerating it from the artifacts removes that failure
mode. Run from the repository root and paste the output into README.md, or
use --check to diff the current README against the generated table.
"""

import sys
import pandas as pd

ROWS = [
    # (env label, csv path, csv agent label, display agent)
    ("Tiger", "results/results_tiger.csv", "EFE", "EFE"),
    ("Tiger", "results/results_tiger.csv", "Planning", "Planning"),
    ("Bandit", "results/results_bandit.csv", "EFE", "EFE"),
    ("Bandit", "results/results_bandit.csv", "Planning", "Planning"),
    ("Tileworld 6x6", "results/results_tileworld_6x6.csv", "EFE", "EFE"),
    ("Inspection-N8", "results/results_inspection_n8.csv", "EFE w=1 (d=3)", "EFE w=1"),
    ("Inspection-N8", "results/results_inspection_n8.csv", "Planning (d=3)", "Planning"),
    ("Inspection-N8", "results/results_inspection_n8.csv", "Plan+IG w=5 (d=3)", "Plan+IG w=5"),
]


def load_row(env, csv_path, agent_label):
    df = pd.read_csv(csv_path, index_col=0)
    if agent_label in df.index:
        row = df.loc[agent_label]
    else:
        df = pd.read_csv(csv_path)
        matches = df[df["agent"] == agent_label]
        if matches.empty:
            return None
        row = matches.iloc[0]
    reward = row.get("mean_reward")
    success = row.get("success_rate", row.get("accuracy"))
    return reward, success


def build_table():
    lines = [
        "| Env | Agent | Reward | Success / Acc |",
        "|-----|-------|--------|---------------|",
    ]
    for env, csv_path, agent_label, display in ROWS:
        try:
            got = load_row(env, csv_path, agent_label)
        except FileNotFoundError:
            got = None
        if got is None:
            lines.append(f"| {env} | {display} | (missing) | -- |")
            continue
        reward, success = got
        reward_s = f"{reward:+.2f}" if pd.notna(reward) else "--"
        success_s = f"{100 * success:.1f}%" if pd.notna(success) else "--"
        lines.append(f"| {env} | {display} | {reward_s} | {success_s} |")
    return "\n".join(lines)


if __name__ == "__main__":
    table = build_table()
    print(table)
    if "--check" in sys.argv:
        readme = open("README.md").read()
        stale = [
            line for line in table.splitlines()[2:]
            if line not in readme and "(missing)" not in line
        ]
        if stale:
            print("\nREADME drift detected: the following generated rows are "
                  "absent from README.md:", file=sys.stderr)
            for line in stale:
                print("  " + line, file=sys.stderr)
            sys.exit(1)
        print("\nREADME table matches generated values.")
