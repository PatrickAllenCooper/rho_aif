#!/usr/bin/env python3
"""
Per-test value-of-information audit case study (Section 4.3 of the
review-response plan): a Structural Inspection interpretability artifact, not
a new headline claim. Records every candidate action's task/information
decomposition (rho_aif.audit.ActionAudit) for a handful of representative
episodes and renders the sequence of observation decisions as a readable
table plus a backing CSV.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from rho_aif.agents.inspection_agents import InspectionTreeSearchAgent
from rho_aif.benchmark import get_benchmark

RESULTS = _ROOT / "results"
TABLES = _ROOT / "paper" / "tables"


def run_episode(env, agent, seed: int) -> list:
    """Run one episode with audit recording on; return this episode's decisions."""
    obs, info = env.reset(seed=seed)
    agent.reset()
    start = len(agent.audit_log)
    for _ in range(env.max_steps):
        action = agent.select_action()
        obs, reward, terminated, truncated, info = env.step(action)
        agent.update(action, obs)
        if terminated or truncated:
            break
    return agent.audit_log[start:]


def action_label(env, action: int) -> str:
    if action < env.NUM_MOVE_ACTIONS:
        return f"move({['N','S','E','W'][action]})"
    if action < env.test_action_start + env.num_test_types:
        return f"test{action - env.test_action_start}"
    return f"diagnose({'faulty' if action - env.diagnose_action_start else 'nominal'})"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--instance", default="Inspection-N8")
    p.add_argument("--info-weight", type=float, default=5.0)
    p.add_argument("--seeds", type=int, nargs="*", default=[42, 123, 456])
    args = p.parse_args()

    cfg = get_benchmark(args.instance)
    env = cfg.env_factory()
    agent = InspectionTreeSearchAgent(
        env, info_weight=args.info_weight, max_depth=cfg.tree_depth, record_audit=True
    )

    rows = []
    for ep_i, seed in enumerate(args.seeds):
        decisions = run_episode(env, agent, seed)
        for step_i, decision in enumerate(decisions):
            for c in decision.candidates:
                rows.append(
                    {
                        "episode": ep_i,
                        "seed": seed,
                        "step": step_i,
                        "action": c.action,
                        "action_label": action_label(env, c.action),
                        "kind": c.kind,
                        "sensing_cost": c.sensing_cost,
                        "info_gain_weight": c.info_gain_weight,
                        "expected_info_gain": c.expected_info_gain,
                        "weighted_info_gain": c.weighted_info_gain,
                        "expected_task_value": c.expected_task_value,
                        "total_score": c.total_score,
                        "chosen": c.chosen,
                    }
                )

    df = pd.DataFrame(rows)
    out_csv = RESULTS / "results_audit_case_study.csv"
    df.to_csv(out_csv, index=False)
    print(f"Saved {out_csv} ({len(df)} candidate records across {df['episode'].nunique()} episodes)")

    # Human-readable narrative for one representative episode: only the
    # decisions made while standing on a component (test vs. diagnose
    # candidates), since those are the observation/exploitation choices the
    # VoI audit is meant to explain.
    ep0 = df[df["episode"] == 0]
    interesting_steps = ep0[ep0["kind"].isin(["observe", "commit"])]["step"].unique()
    print(f"\n=== Case study: {args.instance}, info_weight={args.info_weight}, seed={args.seeds[0]} ===")
    for step in sorted(interesting_steps)[:6]:
        sub = ep0[(ep0["step"] == step) & (ep0["kind"].isin(["observe", "commit"]))]
        print(f"\n step {step}:")
        for _, r in sub.sort_values("total_score", ascending=False).iterrows():
            marker = " <== chosen" if r["chosen"] else ""
            print(
                f"   {r['action_label']:16s} kind={r['kind']:8s} "
                f"cost={r['sensing_cost']:6.2f}  IG={r['expected_info_gain']:6.3f} bits  "
                f"w*IG={r['weighted_info_gain']:7.3f}  task_value={r['expected_task_value']:8.3f}  "
                f"total={r['total_score']:8.3f}{marker}"
            )

    # Appendix table: pick the first step where the ranking by total score
    # (cost- and task-value-adjusted) disagrees with the ranking by raw
    # information gain among the observe candidates -- this is exactly the
    # audit trail's interpretive point, so prefer showing it when it occurs
    # rather than an arbitrary step.
    step_for_table = None
    for step in sorted(interesting_steps):
        obs_sub = ep0[(ep0["step"] == step) & (ep0["kind"] == "observe")]
        if len(obs_sub) < 2:
            continue
        top_by_score = obs_sub.sort_values("total_score", ascending=False).iloc[0]["action"]
        top_by_ig = obs_sub.sort_values("expected_info_gain", ascending=False).iloc[0]["action"]
        if top_by_score != top_by_ig:
            step_for_table = step
            break
    if step_for_table is None:
        step_for_table = sorted(interesting_steps)[0]
    sub = ep0[(ep0["step"] == step_for_table) & (ep0["kind"].isin(["observe", "commit"]))]
    sub = sub.sort_values("total_score", ascending=False)
    TABLES.mkdir(parents=True, exist_ok=True)
    lines = [
        "% Auto-generated by experiments/run_audit_case_study.py -- do not edit by hand.",
        "\\begin{table}[t]",
        "\\centering",
        f"\\caption{{Per-action value-of-information audit for one representative decision",
        f" ({args.instance}, info-gain weight $w={args.info_weight:g}$, step {step_for_table} of the",
        " episode seeded at " + str(args.seeds[0]) + "). Total score is the maximized planning",
        " objective (Section 6); the chosen action need not have the largest raw information",
        " gain once sensing cost and downstream task value are accounted for.}",
        "\\label{tab:audit-case-study}",
        "\\small",
        "\\begin{tabular}{lccccc}",
        "\\toprule",
        "Action & Cost & IG (bits) & $w \\cdot$IG & Task value & Total score \\\\",
        "\\midrule",
    ]
    for _, r in sub.iterrows():
        label = str(r["action_label"]).replace("_", "\\_")
        row = (
            f"{label} & {r['sensing_cost']:.2f} & {r['expected_info_gain']:.3f} & "
            f"{r['weighted_info_gain']:.3f} & {r['expected_task_value']:.2f} & "
            f"{r['total_score']:.2f} \\\\"
        )
        if r["chosen"]:
            row = row.rstrip(" \\\\") + " \\\\ % chosen"
        lines.append(row)
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
    out_tex = TABLES / "audit_case_study.tex"
    out_tex.write_text("\n".join(lines))
    print(f"\nSaved {out_tex}")


if __name__ == "__main__":
    main()
