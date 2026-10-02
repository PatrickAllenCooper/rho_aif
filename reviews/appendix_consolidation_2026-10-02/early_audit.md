# Early empirical appendix audit

Scope: JAIR appendices B–S, mirrored in the LNCS master. Baseline `c5125ab` is preserved before editing at `paper/legacy/2026-10-02_pre_appendix_consolidation/`. This report and its JSON propose changes only. Neither master was edited by this reviewer.

## High-level judgment

There is substantial safe compression available without weakening the case for the paper. The largest sources of avoidable length are repeated readings of tables, multiple illustrations of the same stopping mechanism, and diagnostic narratives that restate conclusions after each number. Protocol exceptions and unfavorable comparisons are the material to preserve. They are not the principal source of excess length.

The early appendices do useful work beyond the main text. Testbed and Navigation prevent a universal-benefit interpretation. The misspecification study shows no special EFE buffering. POMCP's implementation and tuning limitations are essential to interpret its inferior headline numbers. The null MCTS ablations block a stronger mechanism claim. RockSample's standalone rollout beating search and its budget–horizon interaction are especially important. All of those remain in the proposals.

## Proposed consolidation

`early_proposals.json` contains twelve guarded replacements. Every `old` matches exactly once in the JAIR source. The corresponding old block or explicit `old_lncs` matches exactly once in LNCS. Two venue-specific replacements preserve LNCS figure width and omit JAIR-only accessibility descriptions. The generator `build_early_proposals.py` only writes this JSON and must not be rerun after application against changed masters.

1. Three core results tables become a single additional-baseline table. The twelve central means already appear in the main table. Their twelve alternative pooled SEs remain as an ordered compact record, and every additional baseline retains all three outcomes and its uncertainty. The two full Tileworld tables are left intact.
2. Six supplementary figures become one. The adaptive-test decomposition has a distinctive explanatory role and stays. Tiger stopping traces, observation-action scaling, asymmetry, a Diagnosis belief trace, and episode-survival plots are represented by their distinctive findings, qualifications, and saved artifact paths. The six-figure section currently repeats nearly every caption in body prose.
3. Navigation retains its complete table, every significant comparison and correction scope, and the explicit lack of epistemic superiority. Repeated table readings and an untested mechanistic explanation are removed.
4. The single-step PyMDP consistency check becomes one short paragraph with the same numbers and its limits.
5. The 24-row effect-size table becomes a four-row matrix containing exactly the same 24 effects. All statistical protocol paragraphs and correction-family definitions remain.
6. The secondary reward-rescaling plot is removed from the PDF. Its six-row optimal-weight table remains. The main usage-collapse figure is the stronger and more direct equivariance display. The finite-grid/tie caveats stay.
7. The information-unit check retains all exact ties, the direct off-grid Bandit check, adverse Testbed result, and the Tileworld policy change with proper correction scope.
8. The discount table combines 24 agent rows into eight rows of paired EFE/Planning values. Repeated discount settings are grouped only when all displayed outcomes and p-values match. Every original value remains, and a rounding note explains apparent gaps that cannot be recovered from already-rounded percentages.
9. Tiger misspecification has only two unique outcome groups shared by both agents. They replace its redundant table. The full twelve-row Diagnosis table is retained.
10. RockSample diagnostics are organized around implementation, budget–horizon interaction, and comparison scope. The extended table remains. Negative findings and the exact correction families are retained, including matched-protocol failure to detect a reward gap and post-hoc selection limits.
11. IDS keeps its complete matched table and both departures from canonical IDS. Its conclusion is explicitly limited to the tested adaptation and instances.
12. POMCP keeps all three complete tables. Repeated prose readings are removed while preserving both fidelity gaps, seeding and battery differences, computation matching, null ablations, non-blind rule construction, tuning selections, the lower-edge grid limitation, and informed-rollout correction scope.

The combined replacements reduce whitespace-delimited source tokens from 9,886 to 4,833 and remove six rendered figures in total. This suggests roughly 9–12 JAIR pages, but float behavior and typesetting determine actual savings. No font reduction, margin change, asset deletion, result change, or experiment rerun is proposed.

## Verification and retained anchors

- All section-level appendix anchors are retained, including the former supplementary subsection anchors as aliases to the consolidated appendix.
- Removed figure labels have no references outside their replaced section. The removed Tiger misspecification table label is likewise local. Simulated application to both complete sources leaves no references to any removed label.
- `tab:effect_sizes`, `tab:discount`, `tab:misspec-diag`, `tab:reward_scaling`, and all search-baseline table labels remain.
- The one retained adaptive-test figure's caption and accessibility description remain unchanged in JAIR. LNCS keeps its original full-width presentation.
- Statistical families remain as stated in the baseline. Failure to reject is not rewritten as equivalence.
- `rho_aif/agents/ids.py` confirms that the fallback is expected state-entropy reduction, so the shorter “state-entropy gain” wording is accurate.
- `experiments/run_showcase.py` confirms 500 episodes per sweep point split over the five canonical seeds. The asymmetry summary preserves this total rather than inflating it to 500 per seed.
- Environment specifications, the complete near-optimality-horizon study, proper-scoring table, per-action audit record, and two-state boundary case were not trimmed because their remaining content is mostly distinctive protocol or evidence.

## Integration risks to check

The paired discount table and effect-size matrix need rendered width checks in both venues. They use the existing table body size and should wrap/restructure if necessary, rather than shrink. The broader later-appendix consolidation may make some cross-references redundant, but all anchors referenced by these proposals should either remain or receive explicit mappings. Filenames in compact prose may need the repository's `\allowbreak` conventions for clean line wrapping.

The full claim checker will flag reflowed numeric passages even where values are unchanged. Those should be judged against the baseline and source CSVs, not treated as newly estimated results. No new research conclusion or new significance claim is intended.

Verdict: **Proceed with the twelve proposals, followed by independent applied-diff and rendered-PDF review.** These are editorial proposals, not an acceptance judgment on a final manuscript that does not yet exist.
