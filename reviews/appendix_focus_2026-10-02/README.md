# Final claim-focused appendix reduction — 2026-10-02

The scientific appendices now occupy about 15 JAIR pages, down from 42. The complete submission decreases from 80 to 52 pages; the companion LNCS manuscript decreases from 101 to 65. References begin on JAIR page 33, scientific appendices on page 35, and the submission checklist on page 49. Boundary pages are shared, so these occupied-page counts are not additive.

The comparison is the measured median of 13 pages and mean of 11.29 among the 17 articles with scientific appendices in JAIR Volume 84 (2025). That is a one-volume descriptive benchmark, not a journal-wide norm or acceptance threshold. Its per-paper sources and methodology are archived in `../appendix_consolidation_2026-10-02/`.

The accepted 80-page alternative was frozen before edits in `paper/legacy/2026-10-02_pre_claim_focused_appendices/`, from `3c1e99a`, and committed/pushed as `51168bd`. Both dated legacy archives pass their original hash manifests.

## What changed

Peripheral studies and their dependent main-text claims were removed. These include the exploratory random-horizon map, proper-score/inspection demonstrations, broad IDS comparison, reward-optimal scale table, weight atlas, illustrative traces and redundant transfer/result tables. Supporting methods and adverse findings are organized around the claims still made. Seven further figures and eight external table inputs are omitted from the document; all their data, producers, figure files and table files remain in the repository. The final paper has 11 figures and six tables, including its one external table input.

All six proof environments, the separate controller proof, the full learned-sensor protocol, and both preambles are byte-identical to the frozen baseline. No smaller fonts, margins or table text were used. The twins have identical scientific appendices. All 26 checklist questions and verdicts remain, including three Partially answers. Negative controls, unattainable targets, overspending, accuracy losses, reference-selection limitations and solver failures remain visible.

The guarded assembler applies 87 JAIR groups and 85 LNCS groups. This includes main-text withdrawal of orphaned claims, audited reference repairs and two whitespace-only cleanups. Three bibliography entries used only by removed material are pruned; all 69 remaining entries are cited and no citation is missing. No bibliographic record was otherwise changed.

## Independent review

- `independent_theory_review.md` and `independent_theory_source_snapshot.json`: **ACCEPT**, no required revisions remaining. Reviews the complete scientific argument, proof dependencies, checklist, twins and rendered mathematical pages.
- `independent_evidence_review.md` and `independent_evidence_snapshot.json`: **ACCEPT**, no required empirical revisions remaining. Checks retained statements against primary data and producers, including all 24 mechanical numeric advisories.

The reviewers found and verified corrections to stale promises, the omitted RockSample counts pointer, the missing explicit calibration grid and POMCP configuration, the scope of three high-budget non-rejections, and an overstrong claim that every endogenous cap was slack. The final wording says the cap does not lower the maximum sampled reference reward; Tiger's selected reference lies exactly on its cap. Both reviewers independently confirmed the final whitespace-only freeze. These are internal scientific decisions, not a guarantee of JAIR acceptance.

## Verification and delivery

`delivery_validation.json` records exact hashes, both archive checks, proof/protocol/typography preservation, complete label and citation checks, unchanged results and algorithm source, unchanged RockSample table cells, final reviewer-source identity and fresh package compilation. The 17-file Overleaf ZIP has 11 figures and one table input. It compiles using only its extracted files and yields identical PDF text to the delivered JAIR PDF. No hosted Overleaf session or journal submission was performed.

`pytest_full.txt` records **541 passed** with 26 existing warnings. `claims_final.txt` has no hard failures; numeric advisories are independently resolved in the evidence report. Both build logs have no overfull boxes, undefined references/citations or missing-character diagnostics. `visual_review.md` records the final inspection.

The cuts exposed a historical-context defect in the claim checker. It is fixed and covered by a new regression that deletes historical fixtures from the working tree. `claim_checker_fix.md` explains the failure and repair. The only experimental producer change corrects the RockSample caption's data pointer; algorithms and result files are unchanged. No experiments or GPU jobs were run.

## Audit files

`high_level_audit.md`, the early/late/theory audits and guarded proposal JSONs record the claim-to-evidence decisions. `apply_focus.py` assembles them from the frozen baseline and refuses to overwrite unrelated later edits. `root_proposals.json` contains the dependent repairs. The `build_*_proposals.py` files record initial proposal construction; do not rerun them over the subsequently audited JSONs. `pre_whitespace_freeze.json` preserves the exact initially accepted text for the final normalization check. Initial failed/advisory records are retained as history rather than relabeled as successful checks.

Final stage verdict: **PASS**. The remaining approximately 15-page scientific appendix is a clarity-and-rigor compromise near the measured sample, with no obviously dispensable multi-page block identified by the final theory reviewer.
