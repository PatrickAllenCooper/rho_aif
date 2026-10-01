"""Editor-referee fixes (report_editor_clarity.md 4.1, 4.2, heading case)."""
from pathlib import Path

HEADINGS = {
    "Observe-then-commit structure and EFE scope": "Observe-then-Commit Structure and EFE Scope",
    "Two-state thresholds and their empirical scope": "Two-State Thresholds and Their Empirical Scope",
    "State-preservation proof and destructive sensing": "State-Preservation Proof and Destructive Sensing",
    "Agent specifications and weight selection": "Agent Specifications and Weight Selection",
    "Proof and numerical check of the usage-onset corollary": "Proof and Numerical Check of the Usage-Onset Corollary",
    "Proof and implementation scope of the online controller": "Proof and Implementation Scope of the Online Controller",
    "Relationship to constrained planning and experimental design": "Relationship to Constrained Planning and Experimental Design",
    "The information-unit weight and tuning": "The Information-Unit Weight and Tuning",
    "Zero-shot weight transfer": "Zero-Shot Weight Transfer",
    "Approximate planning with MCTS-EFE": "Approximate Planning with MCTS-EFE",
}
EDITS = [
    ("Appendix~\\ref{app:interpretation} retains the detailed horizon, transfer, and discount comparisons.",
     "Appendix~\\ref{app:nearopt_horizon} retains the horizon study, Appendix~\\ref{app:discount} the discount comparison, and Appendix~\\ref{app:interpretation} the weight-transfer results."),
    ("\\label{app:full_tables}\n\n\\begin{table}",
     "\\label{app:full_tables}\n\nThis appendix reports the full agent set for Tiger, Diagnosis, Bandit, and the two Tileworld grids, one table per environment.\n\n\\begin{table}"),
    ("\\appendix\n",
     "\\appendix\n\\let\\appendixsection\\section\n\\renewcommand{\\section}{\\FloatBarrier\\appendixsection}\n"),
]
for name, pkg_anchor in (("full_paper_jair.tex", "\\usepackage{enumitem}\n"),
                         ("full_paper.tex", "\\usepackage{enumitem}\n")):
    p = Path("paper") / name
    t = p.read_text()
    edits = EDITS + [(pkg_anchor, pkg_anchor + "\\usepackage{placeins}\n")]
    edits += [("{" + a + "}", "{" + b + "}") for a, b in HEADINGS.items()]
    for old, new in edits:
        n = t.count(old)
        assert n == 1, (name, old[:60], n)
        t = t.replace(old, new)
    p.write_text(t)
    print(name, "ok", len(edits))
