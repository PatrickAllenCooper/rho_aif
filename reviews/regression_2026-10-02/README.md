# Historical correction regression audit

2026-10-02. Baseline `7e6653055909bbb4d4e28608054c68c83731956c`.

Pat asked whether shortening had reversed earlier corrections. Three independent
reviewers compared the live sources with the correction ledger, frozen longer
manuscripts, primary result archives and implementation. The principal
scientific corrections survive. The audit identified small regressions from the
latest clarity pass and two inherited reproducibility defects, all repaired.

## Repairs

1. PI-5's discussion said a stationary policy meeting a gap target *requires*
   the selected endpoint mixture. It now states a sufficient construction when
   the endpoints straddle the target, preserving the possibility of other
   mixtures. This necessity overstatement entered in the latest polish, not in
   the appendix removals.
2. The scale paragraph again narrated unpublished tolerance-change history,
   contrary to Pat's earlier instruction, and reversed the rerun chronology.
   It now reports only the measured agreement under both comparison rules.
3. Five caption/description semicolons introduced by the latest figure pass
   are split into sentences, retaining all statistical qualifications.
4. The sensor manifests record macOS 27.0 on arm64, whereas the checklist and
   environment document presented the earlier simulation OS, 26.6.2, as
   universal. Both masters and `ENVIRONMENT.md` now distinguish the platforms.
5. An inherited lockfile typo split `fastjsonschema==2.21.2` into
   `fastjoblib==1.5.3` and `jsonschema==2.21.2`. The correct package names,
   `fastjsonschema==2.21.2` and `joblib==1.5.3`, are restored using installed
   metadata and Git history. No installed package or scientific version changes.

## Independent evidence

- [Theory audit](theory.md): preserves the price objects, closed enclosure,
  mixture distinctions, target/cap separation, normalizer restrictions,
  count/cost scaling, controller conditions, perfect-sensor cases and drift
  limitations. All six proof environments and the separate controller proof
  are unchanged from the frozen 80-page version.
- [Empirical audit](empirical.md): independently reproduces recovery metrics
  from 8,000 episode records, sampled cap envelopes, frontier counts, the
  better alternative Bandit mixture and paired TOST. The recovery means remain
  157.3/51.2 with paired difference 106.1. Adverse controls, failed sensor
  targets, transfer failures and post-inspection selection disclosures remain.
- [Editorial audit](editorial.md): checks dependent claims after cuts, all ten
  retained figures, reference graphs, bibliography corrections, all 26
  checklist questions/verdicts and 106 candidate plus two row archive hashes.

Some numbers differ from early chat messages because later documented bug fixes
and reruns superseded them, especially the corrected POMCP results. Restoring
those old numbers would itself introduce a regression. The audit follows the
latest supported result in each correction chain.

## Validation

Both live masters receive matching scientific edits. JAIR remains 52 pages and
LNCS 66. Both builds have zero overfull-box, undefined-reference/citation,
missing-character or LaTeX-error diagnostics. Changed controller, sensor
protocol and checklist pages were rendered and inspected. The mechanical claim
checker has no hard failures, and all eight numeric notices are adjudicated in
the empirical report.

Sixteen focused historical-defect tests pass. The full 541-test suite passed at
the preceding baseline and was not rerun for this prose/environment correction.
No experimental algorithm, result archive, figure asset or bibliography changes.
The package implementation and result directories are unchanged since the
108-page pre-consolidation baseline `c5125ab`.

All 107 dependency pins match the installed environment, with unique normalized
names. The offline resolver dry run and `pip check` pass. This is not a fresh
network installation. The 16-file Overleaf ZIP builds after fresh extraction
without repository inputs and produces identical text to the canonical PDF.

Exact hashes and checks are in [integrity.json](integrity.json),
[environment_validation.json](environment_validation.json) and
[delivery_validation.json](delivery_validation.json). The package validator is
[validate_delivery.py](validate_delivery.py). `apply_repairs.py` records the
initial guarded replacements and is not meant to be rerun on repaired sources.

## Scope

This is a historical regression audit, not a guarantee against every possible
error or a prediction of the journal's decision. The personal brain archive was
unavailable because `/Volumes/Aux` denied access. The audit used this chat,
repository ledgers, saved reviews, immutable archives and current artifacts.
No long simulation battery, sensor refit, external citation search, hosted
Overleaf test or GPU job was run.
