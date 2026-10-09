# IWAI 2026 spotlight

Four slides for a three-minute presentation by Patrick Cooper and Alvaro Velasquez. The final design uses only black, white and gray, native grid diagrams, a native data chart and editable text. It contains no generated imagery, animations, linked media or Internet dependencies.

## Ready to upload

- `output/iwai2026_spotlight_2026-10-09.pptx`: presentation with the spoken script and source notes embedded in all four slides.
- `output/iwai2026_spotlight_2026-10-09.pdf`: four-page slide PDF.
- `output/iwai2026_spotlight_script_2026-10-09.pdf`: two-page rehearsal script, 331 spoken words.
- `output/iwai2026_spotlight_script_2026-10-09.md`: editable rehearsal text.

The schedule allocates 28, 49, 51 and 46 seconds, finishing at 2:54. These are rehearsal targets, not measured speech durations. Rehearse aloud before uploading. No upload or email has been performed.

## Scientific basis

The title and conceptual contribution come from the accepted `paper/paper_iwai2026_abridged.tex`. Current qualifications and corrected results come from `paper/full_paper_jair.tex`.

The 4×4 Tileworld illustration shows a stationary hidden target. An 80%-accurate row-half scan, starting from a uniform prior, gives posterior cell probabilities 0.1 in the indicated half and 0.025 in the other half. Dot areas encode these exact probabilities. This is an illustrative belief update, not a recorded episode, and Tileworld has no robot movement.

Slide 3 uses the 8×8, H=2 rows of `results/results_tileworld_scaling.csv`. The high information weight is fixed at 100, not selected by tuning in this battery. The chart displays descriptive success means. Labels also disclose mean scans and net reward, including scan costs. The narrow planning-horizon comparison does not establish superiority over arbitrary-depth planning.

Slide 4 identifies subsequent work. Its summary comes from the twelve attainable mixture rows in `results/results_budget_frontier.csv`, covering Tiger, Diagnosis and Bandit, not Tileworld. Targets come from calibration curves. The schematic mixture shows a calibration construction and makes no hard-cap, held-out guarantee or reward-optimality claim. The spoken script mentions the later-batch overspending in the public-sensor study. Detailed source and uncertainty notes are embedded in the PPTX.

## Rebuild on this host

`content.json` stores the exact script and verbatim CSV rows. `build.mjs` uses the bundled `@oai/artifact-tool`, generates native objects, runs the required package/font/geometry/native-chart/workbook gates and converts the finalized PPTX to PDF with bundled LibreOffice. `build_script.py` uses ReportLab and locally installed Arial fonts. The runtime and skill paths are explicit at the top of the source. They are build dependencies only, not presentation dependencies.

```sh
/Users/pat/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node presentations/iwai2026_spotlight/build.mjs v8
/Users/pat/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 presentations/iwai2026_spotlight/build_script.py
```

Use a new version suffix for each finalized candidate. Inspect its four PNGs, PDF and native PowerPoint rendering before copying it to the canonical output filenames. Private drafts and renders live in ignored `.build/`. The delivered files are byte-identical copies of validated v7.

## Verification

Two independent reviewers checked the script, scientific scope and all slide/PDF renders. Both report no required revisions. The native chart preserves exact CSV success values with an embedded workbook. All four notes match the script. The four-slide package has no media parts or external relationships. Root inspected the slides in Microsoft PowerPoint, corrected the top data label's headroom, and inspected the final PDF. Repository tests pass, 541/541. Reports and hashes are under `reviews/spotlight_2026-10-09/`.
