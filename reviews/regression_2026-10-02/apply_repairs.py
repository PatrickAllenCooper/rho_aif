"""Mirror the confirmed regression-audit repairs in both live masters."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPAIRS = [
    (
        r"A single stationary policy with expected usage $B$ at a gap budget requires the endpoint mixture of Definition~\ref{def:pi3}.",
        r"The per-episode endpoint mixture of Definition~\ref{def:pi3} gives a fixed randomized policy with expected usage $B$ when its endpoints straddle the target.",
    ),
    (
        "A separate rerun with the former absolute tie tolerance produced byte-identical CSVs, so the tolerance change did not affect these measured points.",
        "The archived results are byte-identical under absolute and relative tie tolerances, so this comparison rule does not alter these measured points.",
    ),
    (
        r"The segment marks grid resolution, not a confidence interval or a policy attaining $B$; the curve between grid points is unresolved.",
        r"The segment marks grid resolution, not a confidence interval or a policy attaining $B$. The curve between grid points is unresolved.",
    ),
    (
        r"Test intervals have $98.333\%$ conditional bootstrap coverage with calibration reselection; later intervals are nominal $95\%$ with selections fixed.",
        r"Test intervals have $98.333\%$ conditional bootstrap coverage with calibration reselection. Later intervals are nominal $95\%$ with selections fixed.",
    ),
    (
        r"The fixed $B=2$ request has no calibration crossing and fails the all-target criterion; it is stated here rather than plotted as a measurement.",
        r"The fixed $B=2$ request has no calibration crossing and fails the all-target criterion. It is stated here rather than plotted as a measurement.",
    ),
    (
        "The right panel shows two negative paired accuracy gaps per target against a direct equality mixture and exact-count conditional-information acquisition; all four intervals lie below zero.",
        "The right panel shows two negative paired accuracy gaps per target against a direct equality mixture and exact-count conditional-information acquisition. All four intervals lie below zero.",
    ),
    (
        "Panel (a) error bars are seed-level SE; panel (b) shows mean scan counts without uncertainty bars.",
        "Panel (a) error bars are seed-level SE. Panel (b) shows mean scan counts without uncertainty bars.",
    ),
]

for name in ("full_paper_jair.tex", "full_paper.tex"):
    path = ROOT / "paper" / name
    text = path.read_text()
    for before, after in REPAIRS:
        count = text.count(before)
        if count != 1:
            raise ValueError(f"{name}: expected one match, found {count}: {before}")
        text = text.replace(before, after, 1)
    path.write_text(text)
    print(f"{name}: {len(REPAIRS)} guarded repairs")
