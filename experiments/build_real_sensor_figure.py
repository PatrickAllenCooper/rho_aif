#!/usr/bin/env python3
"""Publication figure from the frozen real-sensor study's archived summaries.

No model fitting, policy selection, resampling, or evaluation occurs here.
The unavailable target is reported in the text and caption; it has no plotted
estimate or interval.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rho_aif import figstyle

SUMMARY = ROOT / "results/results_real_sensor_summary.csv"
STUDY = ROOT / "results/real_sensor_2026-10-01"
PROTOCOL = ROOT / "experiments/protocols/gas_sensor_2026-10-01.json"
DEFAULT_OUTPUT = ROOT / "figures/real_sensor_transfer"
NOTES = ROOT / "reviews/extension_2026-10-01/real_sensor_figure_notes.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_inputs(summary: Path, study: Path, protocol: Path):
    required = [summary, study / "analysis.json", study / "selection.json", protocol]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("The completed study is required before plotting: " + ", ".join(missing))
    cfg = json.loads(protocol.read_text())
    analysis = json.loads((study / "analysis.json").read_text())
    selection = json.loads((study / "selection.json").read_text())
    if analysis["selection_sha256"] != sha(study / "selection.json"):
        raise RuntimeError("Analysis and frozen selection hashes differ")
    if analysis["protocol_sha256"] != cfg["protocol_sha256"]:
        raise RuntimeError("Analysis and protocol hashes differ")
    with summary.open(newline="") as handle:
        source_rows = list(csv.DictReader(handle))
    rows = {(row["partition"], row["method"]): row for row in source_rows}
    if len(rows) != len(source_rows):
        raise ValueError("Summary contains repeated partition/method rows")
    return cfg, analysis, selection["selected"], rows


def number(row, key):
    value = row.get(key, "")
    return None if value in ("", None) else float(value)


def bounds(interval):
    if interval is None or interval.get("lower") is None or interval.get("upper") is None:
        return None
    lo, hi = float(interval["lower"]), float(interval["upper"])
    if not np.isfinite([lo, hi]).all() or lo > hi:
        raise ValueError("Invalid archived interval")
    return lo, hi


def draw_vertical_interval(ax, x, estimate, interval, *, color, marker):
    """Draw actual bounds even if a percentile interval excludes its estimate."""
    limits = bounds(interval)
    if limits is not None:
        lo, hi = limits
        ax.vlines(x, lo, hi, color=color, linewidth=1.15, zorder=3)
        ax.hlines([lo, hi], x - .035, x + .035, color=color, linewidth=1.15, zorder=3)
    ax.plot(x, estimate, color=color, marker=marker, linestyle="none", markersize=5, zorder=4)


def draw_horizontal_interval(ax, y, estimate, interval, *, color, marker):
    limits = bounds(interval)
    if limits is not None:
        lo, hi = np.asarray(limits) * 100
        ax.hlines(y, lo, hi, color=color, linewidth=1.2, zorder=3)
        ax.vlines([lo, hi], y - .035, y + .035, color=color, linewidth=1.2, zorder=3)
    ax.plot(100 * estimate, y, color=color, marker=marker, linestyle="none", markersize=5, zorder=4)


def build_figure(cfg, analysis, selected, rows, output: Path):
    figstyle.apply()
    # At 6.5in manuscript width, these fonts remain above 9pt after scaling.
    plt.rcParams.update({"font.size": 9.5, "axes.labelsize": 9.5,
                         "axes.titlesize": 10, "xtick.labelsize": 9.5,
                         "ytick.labelsize": 9.5, "legend.fontsize": 9.5,
                         "savefig.bbox": None})
    fig, (usage_ax, gap_ax) = plt.subplots(1, 2, figsize=(6.7, 3.45))
    fig.subplots_adjust(left=.10, right=.985, bottom=.27, top=.82, wspace=.34)
    targets = cfg["targets"]
    unavailable = [budget for budget in targets
                   if selected[f"crossing_B{budget}"]["weights"] is None]
    plotted_targets = [budget for budget in targets if budget not in unavailable]
    periods = ["test"] + [f"batch{b}" for b in cfg["shift_batches"]]
    x = np.arange(len(periods), dtype=float)
    styles = [(figstyle.ORANGE, "s"), (figstyle.GREEN, "^")]
    usage_handles, usage_extents, conditional = [], [0.0], []
    margin = cfg["usage_margin"]
    usage_ax.axhspan(-margin, margin, color=".91", zorder=0)
    usage_ax.axhline(0, color=".35", linestyle="--", linewidth=1, zorder=1)
    usage_ax.axvline(.5, color=".65", linestyle=":", linewidth=.9, zorder=1)
    for index, budget in enumerate(plotted_targets):
        color, marker = styles[index % len(styles)]
        method = f"crossing_B{budget}"
        usage_handles.append(Line2D([], [], color=color, marker=marker,
                                    linewidth=0, label=f"$B={budget}$"))
        for period_index, period in enumerate(periods):
            row = rows[(period, method)]
            usage = number(row, "usage")
            if usage is None:
                continue
            estimate = usage - budget
            if period == "test":
                interval = analysis["bootstrap"][str(budget)]["usage_error_interval"]
            else:
                shift = analysis["shift_intervals"][period.removeprefix("batch")]
                interval = shift.get(str(budget), {}).get("usage_error")
            if interval is not None and interval.get("failed_replicates", 0):
                conditional.append(f"{period}/{method}/usage: {interval['failed_replicates']} failed replicates")
            limits = bounds(interval)
            usage_extents.append(estimate)
            if limits is not None:
                usage_extents.extend(limits)
            draw_vertical_interval(usage_ax, x[period_index], estimate, interval, color=color, marker=marker)
    lower, upper = min(usage_extents + [-margin]), max(usage_extents + [margin])
    pad = max(.12, .11 * (upper - lower))
    usage_ax.set_ylim(lower - pad, upper + pad)
    usage_ax.set_xlim(-.30, len(periods) - .7)
    usage_ax.set_xticks(x)
    usage_ax.set_xticklabels(["Test"] + [f"B{b}" for b in cfg["shift_batches"]])
    usage_ax.set_xlabel("Within-period test and later batches")
    usage_ax.set_ylabel("Mean sensor accesses minus target")
    usage_ax.set_title("(a) Usage exceeds both targets after transfer", loc="left", pad=10)

    references = [("direct_target", "Direct equality", figstyle.BLUE, "o", -.12),
                  ("cmi", "Exact-count CMI", figstyle.ORANGE, "s", .12)]
    gap_handles, gap_extents = [], [0.0]
    gap_ax.axvline(0, color=".35", linestyle="--", linewidth=1, zorder=1)
    for reference, label, color, marker, offset in references:
        gap_handles.append(Line2D([], [], color=color, marker=marker, linewidth=0, label=label))
        for index, budget in enumerate(plotted_targets):
            method = f"crossing_B{budget}"
            main_row = rows[("test", method)]
            reference_row = rows[("test", f"{reference}_B{budget}")]
            a, b = number(main_row, "correctness"), number(reference_row, "correctness")
            if a is None or b is None:
                gap_ax.text(.03, index + offset, f"{label} unavailable", transform=gap_ax.get_yaxis_transform(),
                            fontsize=9.5, va="center", color=".4")
                continue
            gap = a - b
            interval = analysis["bootstrap"][str(budget)]["comparisons"][reference]["correctness"]
            if interval.get("failed_replicates", 0):
                conditional.append(f"test/{method}/{reference}: {interval['failed_replicates']} failed replicates")
            limits = bounds(interval)
            gap_extents.append(100 * gap)
            if limits is not None:
                gap_extents.extend(100 * np.asarray(limits))
            draw_horizontal_interval(gap_ax, index + offset, gap, interval, color=color, marker=marker)
    span = max(gap_extents) - min(gap_extents)
    pad = max(.5, .12 * span)
    gap_ax.set_xlim(min(gap_extents) - pad, max(gap_extents) + pad)
    gap_ax.set_ylim(len(plotted_targets) - .6, -.45)
    gap_ax.set_yticks(np.arange(len(plotted_targets)))
    gap_ax.set_yticklabels([f"$B={b}$" for b in plotted_targets])
    gap_ax.set_xlabel("Crossing − reference accuracy (pp)")
    gap_ax.set_title("(b) Crossing loses accuracy on held-out cases", loc="left", pad=10)
    gap_ax.grid(False, axis="y")
    gap_ax.grid(True, axis="x", alpha=.25, linewidth=.6)
    fig.legend(handles=usage_handles, loc="lower left", bbox_to_anchor=(.06, .025), ncol=2,
               columnspacing=.9, handlelength=1.2, handletextpad=.4, borderaxespad=0)
    fig.legend(handles=gap_handles, loc="lower left", bbox_to_anchor=(.58, .025), ncol=1,
               handlelength=1.2, handletextpad=.4, borderaxespad=0)
    for ax in (usage_ax, gap_ax):
        figstyle.style_axis(ax)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output.with_suffix(".pdf"))
    fig.savefig(output.with_suffix(".png"), dpi=300)
    plt.close(fig)
    return unavailable, conditional


def write_notes(cfg, analysis, selected, rows, output, unavailable, conditional, notes):
    caption = (
        "Retrospective sensor acquisition on UCI Gas Sensor Drift with fixed researcher-defined "
        "expected-access targets $B\\in\\{2,4,8\\}$. (a) Realized mean usage of the frozen crossing-endpoint "
        "mixture minus its target on unseen cases from batches 1--6 (Test) and separately on later batches "
        "7--10. Zero denotes exact mean attainment, and the gray band is the predeclared $\\pm0.5$ "
        "access tolerance. Collection-period positions are categorical. Test intervals are Bonferroni-adjusted "
        "98.333\\% conditional bootstrap intervals, with calibration selection repeated in each replicate. "
        "Later-batch intervals are nominal 95\\% paired case-bootstrap intervals with the original "
        "calibration selections fixed. (b) Held-out accuracy differences in percentage points between "
        "the crossing mixture and the direct usage-penalty equality mixture or exact-count greedy "
        "conditional-information acquisition (CMI). Intervals are nominal 95\\% paired bootstrap intervals "
        "including calibration reselection. Positive differences favor the crossing mixture. The fitted "
        "direct equality mixture need not attain exactly $B$ on held-out cases. All intervals condition "
        "on one trained observation model and exchangeability within batch/class strata."
    )
    if unavailable:
        caption += (" The fixed $B=2$ request has no calibration crossing and no plotted estimate; "
                    "it fails the declared all-target criterion.")
    if conditional:
        caption += " Where reselection failed, plotted intervals summarize successful replicates and the failure counts are archived."
    description = (
        "Two panels plot the available four- and eight-access crossing mixtures. The left panel shows "
        "usage minus target across within-period held-out cases and four later collection batches as separate "
        "points with intervals, a horizontal zero line, and a gray half-sensor tolerance band. Both series "
        "overshoot in every later batch. The right panel plots negative paired held-out accuracy differences "
        "from direct equality and exact-count information acquisition, with interval bars and a vertical zero line. "
        "The unavailable two-access request is stated in the caption and prose, not plotted as a measurement."
    )
    lines = ["# Real-sensor publication figure", "", f"PDF: `{output.with_suffix('.pdf').relative_to(ROOT)}`",
             f"PNG: `{output.with_suffix('.png').relative_to(ROOT)}`", "",
             "The authored width is 6.7 inches. All text is at least 9.5pt, remaining above 9pt at a 6.5-inch printed width.",
             "No table is generated because the paired-gap panel already carries the primary comparison.", "",
             "## Suggested caption", "", caption, "", "## Suggested Description", "", description, "",
             "## Displayed held-out values", ""]
    for budget in cfg["targets"]:
        method = f"crossing_B{budget}"
        if selected[method]["weights"] is None:
            lines.append(f"- B={budget}: crossing unavailable on calibration.")
            continue
        row = rows[("test", method)]
        entry = analysis["bootstrap"][str(budget)]
        lines.append(f"- B={budget}: mean usage {float(row['usage']):.6g}, accuracy {100 * float(row['correctness']):.6g}%. "
                     f"Usage-error interval {entry['usage_error_interval']}.")
        for reference in ("direct_target", "cmi"):
            lines.append(f"  - Accuracy gap against {reference}: {entry['comparisons'][reference]['correctness']} (probability units).")
    lines += ["", "## Missing-selection audit", "", *(conditional or ["No displayed interval has a failed replicate."]), "",
              "## Input hashes", ""]
    for path in [SUMMARY, STUDY / "analysis.json", STUDY / "selection.json", PROTOCOL]:
        lines.append(f"- `{path.relative_to(ROOT)}`: `{sha(path)}`")
    notes.parent.mkdir(parents=True, exist_ok=True)
    notes.write_text("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    cfg, analysis, selected, rows = load_inputs(SUMMARY, STUDY, PROTOCOL)
    unavailable, conditional = build_figure(cfg, analysis, selected, rows, args.output)
    write_notes(cfg, analysis, selected, rows, args.output, unavailable, conditional, NOTES)
    print(json.dumps({"pdf": str(args.output.with_suffix('.pdf')), "png": str(args.output.with_suffix('.png')),
                      "notes": str(NOTES), "unavailable_targets": unavailable, "conditional_intervals": conditional}))


if __name__ == "__main__":
    main()
