"""Assemble the reviewed concision fragments from the frozen legacy masters."""
from pathlib import Path
import re
from appendix_notation_fixes import apply as appendix_notation_fixes
from theory_notation_fixes import apply as theory_notation_fixes

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
LEGACY = ROOT / "paper/legacy/2026-09-28_pre_concision"


def fragment(name):
    return (HERE / f"{name}.tex").read_text().strip() + "\n\n"


def layout_breaks(source):
    """Permit wrapping without changing text, mathematics, type size, or margins."""
    source = source.replace(
        r"\begin{document}",
        "% Emergency paragraph wrapping for long mathematical and artifact names.\n"
        r"\setlength{\emergencystretch}{2em}" + "\n\n" + r"\begin{document}",
        1,
    )
    for old, new in [
        (r"scipy.stats.entropy", r"scipy.\allowbreak stats.\allowbreak entropy"),
        (r"results\_price\_usage\_curves.csv", r"results\_\allowbreak price\_\allowbreak usage\_\allowbreak curves.csv"),
        (r"results\_cpomdp\_baseline.csv", r"results\_\allowbreak cpomdp\_\allowbreak baseline.csv"),
        (r"results\_tiger.csv", r"results\_\allowbreak tiger.csv"),
        (r"\{5x3,7x4,7x8,11x11\}.csv", r"\{5x3,\allowbreak7x4,\allowbreak7x8,\allowbreak11x11\}.csv"),
    ]:
        assert old in source, old
        source = source.replace(old, new)
    for values in [
        "0.01, 0.1, 0.5, 1, 2, 5, 10, 20, 50, 100, 200",
        "42,123,456,789,1024", "42, 123, 456, 789, 1024",
        "-0.10, -0.05, 0.00", "-0.15, +0.05, +0.10",
    ]:
        old = r"\{" + values + r"\}"
        assert old in source, old
        source = source.replace(old, r"\{" + values.replace(",", r",\allowbreak ") + r"\}")
    return source


def assemble():
    main = "".join(fragment(name) for name in [
        "intro_main", "related_main", "theory_main_restored", "evidence_main", "discussion_main"
    ])
    additions = "".join(fragment(name) for name in [
        "theory_appendix_restored", "evidence_appendix", "editorial_appendix"
    ])
    abstract = fragment("abstract").strip()
    for name in ["full_paper_jair", "full_paper"]:
        old = (LEGACY / f"{name}.tex").read_text()
        front = old[:old.index(r"\section{Introduction}")]
        current_abstract = abstract
        keywords = ""
        if name == "full_paper":
            current_abstract = re.sub(r"\\textbf\{[^}]+:\}\s*", "", current_abstract)
            keywords = "\n" + re.search(r"\\keywords\{[^\n]+", front).group()
        front = re.sub(
            r"(?s)(\\begin\{abstract\}).*?(\\end\{abstract\})",
            lambda m: m[1] + "\n" + current_abstract + keywords + "\n" + m[2], front,
        )
        back = old[old.index(r"\paragraph{Competing interests.}"):]
        if name == "full_paper_jair":
            marker = r"\section{Reproducibility Checklist for JAIR}"
        else:
            marker = r"\end{document}"
        assert back.count(marker) == 1
        back = back.replace(marker, additions + marker)
        body = main
        if name == "full_paper":
            body = body.replace("fig_hero_price_curve_jair.pdf", "fig_hero_price_curve.pdf")
            body = body.replace(
                r"Appendix~\ref{app:repro} records the full reproducibility checklist, including all exceptions.",
                "The JAIR version's reproducibility checklist records all exceptions and artifact locations.",
            )
        source = front + body + back
        source = source.replace(
            "This comparison checks consistency between implementations; it does not certify numerical equivalence",
            "This comparison checks consistency between implementations. It does not certify numerical equivalence",
        )
        # Relocated section labels retain their identity; use the correct type
        # of location in every prose pointer, including the original appendices.
        appendix = source.split(r"\appendix", 1)[1]
        app_labels = set(re.findall(r"\\label\{([^}]+)\}", appendix))
        source = re.sub(
            r"\bSection(s?)~(\\ref\{([^}]+)\})",
            lambda m: ("Appendices" if m[1] else "Appendix") + "~" + m[2]
            if m[3] in app_labels else m[0], source,
        )
        source = appendix_notation_fixes(source)
        source = theory_notation_fixes(source)
        source = layout_breaks(source)
        (ROOT / "paper" / f"{name}.tex").write_text(source)
        print(name, len(source.split()), "source words")


if __name__ == "__main__":
    assemble()
