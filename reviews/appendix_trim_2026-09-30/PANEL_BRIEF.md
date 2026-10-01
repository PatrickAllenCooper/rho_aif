# JAIR referee panel, 2026-09-30: brief

You are an independent referee for the Journal of Artificial Intelligence Research (JAIR). The submission is at `/Users/pat/code/rho_aif/paper/full_paper_jair.tex`, with the rendered PDF at `paper/full_paper_jair.pdf` (106 pages, references starting on page 38, bound appendices after). The title is "Pricing the Sensing Budget in rho-POMDPs, with Expected Free Energy as the Canonical Information Weight".

You have full artifact access to the repository:
- `rho_aif/` is the package, `experiments/` holds the producers, and `results/` holds the CSVs behind every number.
- `paper/tables/` holds the generated tables. `tests/` is the test suite.
- `README.md` has the reproduction table.

Verify claims against the CSVs and code yourself. Do not trust the prose.

## Context for fair review

- JAIR's practical norm keeps the main body under about 40 pages. Required changes must not grow the main body beyond the references starting on page 38. Additions to the appendix are acceptable in moderation.
- This is an unpublished manuscript. It states current methods and results. Do not ask for version history.
- The following are deliberate disclosures, not defects:
  - comparisons added after results were inspected are labelled post hoc;
  - some TOST margins are retrospective;
  - one pair is non-blind on replication seeds;
  - the POMCP selection rule was written after an exploratory sweep.
- Project conventions:
  - no semicolons in prose;
  - SARSOP and constrained-POMDP references are called near-optimal or estimated, never exact;
  - w is not presented as the Lagrange multiplier of the usage constraint.

## Your output

Write your report to `reviews/appendix_trim_2026-09-30/report_<LENS>.md` with these sections:
1. **Recommendation.** Exactly one of: Accept, Accept with minor revisions, Major revisions, Reject.
2. **Summary** of the contribution in your own words.
3. **Strengths.**
4. **Required changes.** Each item needs the quoted current text, its JAIR source line, what is wrong, and a concrete replacement. Only include items that block your recommendation.
5. **Optional suggestions.**
6. **What you verified.** List the claims you checked against which files, and the result of each check.

Hold the manuscript to JAIR's standard: correctness, significance, clarity, reproducibility, and honest scoping. Recommend Accept only if you would sign that decision as it stands. Do not edit any file except your report. Return your recommendation and your required changes.
