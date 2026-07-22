"""Console entry point: ``rho-aif-bench``."""

from __future__ import annotations

import argparse
import csv
import os
import sys
from typing import Optional

from rho_aif.benchmark import (
    BENCHMARKS,
    list_benchmarks,
    run_benchmark,
)


def _cmd_list(_args: argparse.Namespace) -> int:
    print(f"{'Name':20s}  {'Family':20s}  {'|S|':>8s}  Description")
    print("-" * 90)
    for name in list_benchmarks():
        cfg = BENCHMARKS[name]
        n_s = str(cfg.num_states) if cfg.num_states is not None else "?"
        print(f"{name:20s}  {cfg.family:20s}  {n_s:>8s}  {cfg.description}")
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    seeds = None
    if args.n_seeds is not None:
        from rho_aif.benchmark import BENCHMARK_SEEDS

        seeds = BENCHMARK_SEEDS[: args.n_seeds]

    print(f"Running {args.env} / agent={args.agent}", flush=True)
    summary = run_benchmark(
        env_name=args.env,
        agent_name=args.agent,
        episodes=args.episodes,
        seeds=seeds,
        info_weight=args.info_weight,
        progress=not args.quiet,
    )

    out_path = args.out
    if out_path is None:
        os.makedirs("results", exist_ok=True)
        safe_agent = args.agent.replace("+", "plus").replace("/", "-")
        out_path = f"results/bench_{args.env}_{safe_agent}.csv"

    # Flatten list fields for CSV
    row = {k: v for k, v in summary.items() if not isinstance(v, (list, tuple))}
    row["seeds"] = ",".join(str(s) for s in summary["seeds"])

    parent = os.path.dirname(out_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        writer.writeheader()
        writer.writerow(row)

    print("Summary:")
    for key in (
        "mean_reward",
        "success_rate",
        "accuracy",
        "mean_log_score",
        "mean_brier",
        "mean_observations",
        "mean_tests",
    ):
        if key in summary:
            val = summary[key]
            if isinstance(val, float):
                print(f"  {key}: {val:.4f}")
            else:
                print(f"  {key}: {val}")
    print(f"Wrote {out_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rho-aif-bench",
        description="Benchmark suite for information-gathering planning (rho-AIF).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List available benchmark environments")
    p_list.set_defaults(func=_cmd_list)

    p_run = sub.add_parser("run", help="Run a canonical (env, agent) evaluation")
    p_run.add_argument(
        "--env",
        required=True,
        choices=list_benchmarks(),
        help="Benchmark environment name",
    )
    p_run.add_argument(
        "--agent",
        default="efe",
        help="Agent short name (efe, planning, myopic, planning+ig, greedy, ...)",
    )
    p_run.add_argument(
        "--episodes",
        type=int,
        default=None,
        help="Episodes per seed (default: protocol value)",
    )
    p_run.add_argument(
        "--n-seeds",
        type=int,
        default=None,
        help="Use the first N canonical seeds (default: all 5)",
    )
    p_run.add_argument(
        "--info-weight",
        type=float,
        default=5.0,
        help="Info-gain weight for planning+ig agents (default: 5.0)",
    )
    p_run.add_argument(
        "--out",
        default=None,
        help="Output CSV path (default: results/bench_<env>_<agent>.csv)",
    )
    p_run.add_argument("--quiet", action="store_true", help="Suppress progress logs")
    p_run.set_defaults(func=_cmd_run)
    return parser


def main(argv: Optional[list] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
