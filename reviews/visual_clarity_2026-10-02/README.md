# Writing and figure-clarity pass (2026-10-02)

Pat requested a complete prose-quality review with an independent reviewer, and
specific changes to the former Figures 2, 4, 7, and 10. The current masters are
`paper/full_paper_jair.tex` and `paper/full_paper.tex`; historical masters and
legacy archives were left intact.

The independent reader audited the complete JAIR source for concept timing,
transitions, proof motivation, ambiguous vocabulary, and figures. The audit
identified twelve prose issues and, after the initial edits, two residual
figure/claim issues. Both rounds were resolved and rechecked against the final
sources and saved results. Its final verdict is **CLEAN, with no required
writing or visual edits remaining**. This is an internal clarity assessment,
not a journal decision.

## Disposition

- Removed the engineering-workflow figure from both manuscripts and repaired
  its reference. Its source asset remains available in the repository.
- Rebuilt the scale figure from saved CSVs. Raw crossing brackets now make the
  tenfold shift visible; one normalized curve represents the 14 exactly
  coincident Diagnosis grid points at all three scales. No line bridges the
  unresolved bracket, and the caption distinguishes the bracket from a
  measured deterministic crossing. The final print layout places its section
  explanation above the figure.
- Removed the unavailable two-access request from the sensor figure's data
  panels and legends. The text and caption still report the failed target.
  The gray tolerance band and classification gaps are explained directly.
- Reduced the Tileworld scaling figure to success and scan use for the three
  agents that expose the fixed-depth mechanism. Reward and omitted agents
  remain in the CSV and caption. Corrected the sweep's 6x6 scan mean to 15.57
  rather than borrowing 15.64 from the separate main battery.
- Clarified the operational-price introduction, reward/nat convention before
  Proposition 1, the one-step threshold before its corollary, the four
  controller assumptions and two conclusions, the three frontier comparisons,
  the sensor acquisition notation, and the statistical convention. Renamed
  the conditional two-state interval to describe its actual behavior.
- Applied every scientific/prose change to both live masters. Guarded edit
  scripts and the figure application manifest are retained in this directory.

The numeric results and saved experimental CSVs are unchanged. Figures were
regenerated from those CSVs and the archived real-sensor summaries. No
episodes, model fits, GPU allocations, or new statistical tests were run.

## Verification

- Full suite: **541 passed**, 26 existing warnings.
- Mechanical claim checker: no hard failures. Its two review-only notices
  concern `98.333%`, the Bonferroni-adjusted coverage computed from three
  targets rather than a numerical CSV cell.
- JAIR and LNCS builds succeed at **52 and 66 pages**. Logs have no overfull
  boxes, undefined references/citations, missing characters, or LaTeX errors.
- Final figures were inspected at printed size. Independent review verified
  the scale-point identity and Tileworld values against committed CSVs, the
  unplotted sensor failure, and the absence of the removed figure in both
  masters.
- The dated Overleaf ZIP has 16 members: 10 figures and one table input.
  `validate_delivery.py` compiles a fresh extraction without repository
  inputs and compares its PDF text to the current JAIR PDF. Exact hashes and
  outcome are in `delivery_validation.json`.

The ZIP was locally verified, not uploaded to Overleaf or submitted to JAIR.
