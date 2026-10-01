# Appendix trim, 2026-09-30: brief for trim scouts

Repository: /Users/pat/code/rho_aif. Two live masters must stay textually parallel:
`paper/full_paper_jair.tex` (JAIR, the submission) and `paper/full_paper.tex` (LNCS, same prose, different class, and no reproducibility checklist). Read `CLAUDE.md` for the project conventions.

## Goal (Pat, 2026-09-30)

"Consider possibilities for trimming the appendix where possible. Remove historical comments regarding failed experiments, we haven't published anything yet, let's put our best foot forward."

The paper is unpublished. The JAIR main body ends before page 38 and must not grow. The appendix, from `\appendix` at about line 870 to the end, is about 50,000 words, and we want it shorter and stronger.

## What to propose

1. **FAILED.** Remove experiments or baselines that did not work, were superseded, or are reported mainly to be dismissed. Also remove narration of attempts ("we attempted", "an initial version", "kept as a reference"), reference baselines that "should not be compared", and diagnostic-only columns described in prose.
   - Keep genuine negative scientific findings that bear on the paper's claims. Examples: the POMCP gap, the RockSample counterexample where a heuristic beats EFE, a scope limitation, or a place where w=1 is Pareto-dominated.
   - Where a failed experiment establishes a scope limit that the paper relies on, compress it to one plain sentence stating the limit. Do not delete the limit.
2. **DUPLICATE.** Remove content stated twice in the appendix, or restated at length from the main body, and keep the stronger copy. Update `\ref`s if you remove a labelled unit.
3. **VERBOSE.** Shorten passages that are much longer than their content needs. Keep every number that the main body, a table, a figure, or another appendix passage relies on.

## Hard constraints

- No main-body edits (text before `\appendix`), except repointing a `\ref` whose target you remove.
- Every `\label` you delete must have no remaining `\ref`, `\Cref`, or `\cref` anywhere in either master. Check with grep.
- Never remove disclosures that are properties of the reported analyses: post hoc comparisons, retrospective TOST margins, non-blind seeds, the selection rule written after an exploratory sweep, simulation-matched rather than compute-matched comparisons, and w*_ret versus w*_succ.
- Never remove the POMCP fidelity-gap statements or statistical protocol statements.
- Do not remove limitations that the main body cites or relies on.
- Tables (`paper/tables/*.tex` or inline tabulars) and figures come from producers. If removing a row, column, or figure is right, list it under `producer_changes` with the producer script (for example `experiments/build_rocksample_tables.py`). Do not edit tables in the tex directly.
- Conventions: no semicolons in prose, no rhetorical italics or bold, "near-optimal/estimated" (never "exact") for SARSOP/CPOMDP references, "exercises" not "validates".
- Each `old` must be an exact substring occurring exactly once in `paper/full_paper_jair.tex` and exactly once in `paper/full_paper.tex`. Verify with Python `str.count`. If the LNCS text differs, give `old_lncs` and `new_lncs` as well. The checklist section is JAIR-only, so set `lncs_count: 0` for it.
- `new` may be the empty string. Make sure the sentence and paragraph flow still reads correctly afterwards.
- Do NOT edit any file except your own proposal file.

## Output

Write a JSON file to `reviews/appendix_trim_2026-09-30/proposals_<SCOPE>.json`:

```json
{"proposals": [{"id": "A01", "category": "FAILED|DUPLICATE|VERBOSE", "old": "...", "new": "...", "old_lncs": null, "new_lncs": null, "lncs_count": 1, "words_saved": 0, "rationale": "...", "labels_removed": [], "refs_repointed": []}],
 "producer_changes": [{"id": "...", "producer": "...", "change": "...", "rationale": "...", "dependent_prose": ["ids of proposals that depend on it"]}],
 "considered_and_kept": [{"passage": "short quote", "reason": "..."}]}
```

Return a short summary: the proposal count by category, total words saved, and the three most valuable cuts. Be ambitious about substance but conservative about rigor. A hostile JAIR referee must not be able to say something load-bearing was hidden.
