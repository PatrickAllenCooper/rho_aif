# Main-text structural concision review, 2026-10-01

The main argument can lose about six pages before the new study is added, while retaining the central calibration mathematics, headline evidence and negative findings. I recommend nine guarded edit groups in `main_concision_proposals.json`, with one optional table relocation if the new study needs a full three pages. The proposals are not applied to either manuscript.

Baseline: commit `7b954ce`. The reviewed sources match the final acceptance hashes: JAIR `73f6ee1feb9bf2202bc141dadf52ae557816a8934ecfa0db47a1836b07b4a44c`, LNCS `25a9eaa30eac01e354775cd33f8018685dc171cc932e5f5e5fc1ba6a0aeb0a44`. I read `AGENTS.md`, the current guidance-ledger entries, the main body and relevant appendix destinations in both masters, and the two final acceptance reports under `reviews/polish_2026-10-01/`. I also read the earlier concision review to identify relocation mistakes to avoid.

The recommended structure keeps the route from the inspection requirement to the calibrated policy short. The main reader needs the policy family, the EFE anchor with its unit convention, the crossing and mixture construction, the scale and controller results, and the experiments that show both achievement and failure. The full two-state threshold derivation, destructive-test arithmetic, second staircase display and endogenous-usage reference tables are supporting material. They are useful, but need not all precede the primary target study.

## Exact proposals

Each group contains verbatim `old` and `new` strings, an expected occurrence count of one, a SHA256 guard, source lines in both masters, a rationale, an explicit evidence-retention plan and protected claims/labels. The groups were applied only to in-memory strings and scratch files. All changes within a group are atomic because removing a main-text block without its paired appendix insertion would lose support.

- MC01 moves the full two-state threshold proposition to `app:theory_thresholds`, beside its proof. The main text retains the distinct H=1/H=2 purposes, the limited empirical applicability and the lack of a longer-horizon guarantee. The proposition's hypotheses, formulas, strict interval endpoints and perfect-sensing exclusion move unchanged.
- MC02 moves the worked destructive-sensing example and timeline to `app:theory_factored`. The main text keeps the sign reversal, the realized loss from following obsolete observations, the state-preservation boundary and the distinction from transition-aware EFE. The diagnostic remains explicitly unproved as a value correction or decision-error bound.
- MC03 reduces the heterogeneous-cost study to the changing test mix and the observed coincidence of both bracket pairs. Its complete body and four-panel figure move into new subsection `app:cost_details`. The negative bracket finding remains visible in the main text.
- MC04 reduces the interleaved study to its extension and the RockSample[5,3] nonmonotone counterexample. Its full grids, episode protocols and second staircase figure move into `app:interleaved_details`. The five-domain staircase remains in the main text. One existing margin-rule pointer is redirected to the new appendix destination.
- MC05 keeps the fixed-margin SARSOP equivalence result, retrospective-margin disclosure, prospective additional-seed scope and episode-matched check. It moves the auxiliary reward/usage table to `app:sarsop_details`, which already contains the omitted p-values and intervals.
- MC06 keeps the literal usage penalty and sampled-envelope method, but moves the endogenous-usage cap table to `app:cpomdp_details`. All three caps are slack in this comparison. The main text keeps that fact and the limitation of the reference to small domains. The primary held-out target table stays in the main text.
- MC07 removes the repeated PWLC/Lipschitz discussion immediately after the equivalence theorem. The precise restrictions remain in Related Work and the scope appendix. The normalizer and bit/nat paragraphs are unchanged.
- MC08 consolidates the repeated positioning discussion. It retains the distinction between an episode-level information weight and a usage-cap multiplier, sampled-reference uncertainty, the failed shallow RockSample reference, the cost of a sweep and the fact that scale transfer also applies to directly tuned weights.
- MC09 makes Discussion interpret the results rather than repeat their full exposition. It retains the random two-state failure rate, negative Navigation and model-mismatch findings, the largest RockSample failure, horizon and sensor limitations, the scoped null ablation, known-model/synthetic scope and unresolved transition-aware budget control.
- MC10 is an optional reserve. It moves the Inspection table into the existing Inspection appendix, while leaving the entire main Inspection paragraph unchanged, including its accuracy/reward trade-off, non-significant reward difference, synthetic setting and shared-leaf limitation.

## What remains prominent

The hero, engineering workflow and target-versus-cap figures remain. They are superficially repetitive but serve different purposes: geometry, operational sequence and objective choice. Removing them merely to reduce figure count would make the shortened paper harder to understand. The two other staircase figures do use the same display for secondary instances, so the interleaved one is the better relocation.

The proposed batch leaves Definition PI-3 intact. Its distinction between the level set, crossing threshold, half-open reported bracket, closed enclosure and endpoint mixture has survived repeated mathematical review. It also keeps the no-missed-crossing condition, non-straddling fallbacks and the difference between a bracket and uncertainty. A later readability pass could lay out its four objects more clearly, but should not shorten away a condition while trying to save a fraction of a page.

The scale theorem, comparative-statics theorem and their proofs are unchanged. The stationary-controller statement retains every crossing/noise/separation condition, the distinction between weight convergence and instantaneous usage at a jump, and the harmonic-schedule running-average result. Its reset heuristic remains explicitly outside the theorem.

The primary target results are untouched. This protects the 0.13 usage error, cap-versus-target gap distinction, nominal plug-in interval scope, reference-selection uncertainty, frozen fresh-seed replay, changing Diagnosis shortfall identity, Bandit mixture counterexample and Tiger rare-event sensitivity. The bracket-selection bootstrap is also untouched. These qualifications support the paper's central claim and should not become collateral cuts when new results are added.

The distractor study, Pareto figure, Tileworld horizon qualification, largest RockSample counterexample and standalone heuristic comparison stay in the main body. The core performance table remains. MC10, if used, preserves the Inspection interpretation verbatim and moves only its full numerical support.

## Word and page accounting

For the nine recommended groups, the JAIR main source decreases from 18,472 to 15,303 whitespace tokens after removing accessibility Description lines and full-line comments, a reduction of 3,169. This metric includes LaTeX and table tokens and is not a rendered prose word count. Both masters have the same absolute reduction. The LNCS pre-appendix count also includes its inline bibliography, so its absolute before/after totals should not be compared directly with JAIR.

Main figures decrease from 12 to 9. Inline main tables decrease from 6 to 4, with the separate RockSample table input retained. Every original figure/table remains bound in the document. Unique supporting content is relocated rather than erased, so whole-document source savings are only 361 tokens. This is a substantive main-structure reduction, not a claim that the complete document is now much shorter. Total-document shortening should come from the independent appendix duplication pass.

The scratch JAIR build uses the unchanged class, bibliography, tables and figures. Its bibliography begins on page 32 rather than page 38, and the complete PDF has 110 pages rather than 111. Two pages of new main-text material would therefore plausibly put references near page 34. Three pages may require MC10 or a further small reduction. These are planning estimates for the combined manuscript, since new floats and appendix changes can alter pagination.

The exact proposal file records per-group word deltas. The largest main reductions are MC03 and MC01, followed by MC04 and MC02. The smaller MC07–MC09 cuts remove actual repetition rather than relocating it.

## Validation and remaining integration work

The dry run checks exact occurrence guards for both masters, sequential application without overlap, complete retention of baseline labels and citation keys, no duplicate labels and no unresolved source references after including table inputs. The relocated threshold proposition changes printed proposition numbers, which LaTeX resolves through the preserved labels. No new bibliography entry, equation, measurement, statistical conclusion, semicolon or rhetorical emphasis was introduced in the new prose.

The scratch JAIR build completes with no overfull boxes, missing characters or undefined references/citations. Existing class/header/PDF-string warnings remain. This is a source and compilation check, not a full rendered-page visual audit or a fresh experimental rerun. The LNCS candidate was checked structurally but not compiled by this review. The parent should run the required claim verifier and adversarial batch audit after combining all accepted proposals, then inspect both final PDFs and the source package.

Preserve the dated legacy source before installing a new assembled pair. Existing dated legacy files were not touched. The new experimental study needs its own main protocol and evidence, including independent target choice, uncertainty and unfavorable outcomes. Do not relabel the old calibration-derived targets as application-specified. Update MC09's current application/known-model limitations only to the extent the new study actually addresses them, and revise the abstract and conclusion from completed results rather than anticipated ones.

No master, result CSV, figure producer, bibliography, guidance ledger or commit was changed by this review. The integrating agent should record the accepted disposition in the guidance documents and commit the eventual mirrored batch.

Final scratch confirmation: the nine recommended groups give references on page 32 and 110 pages total. Adding optional MC10 also leaves references on page 32 and gives 111 pages total because the appendix float repaginates. MC10 therefore did not buy a whole reference-start page in this isolated build and should remain optional, chosen only for the combined manuscript layout. Both builds have zero overfull boxes, undefined references/citations and missing characters.

Static hero-number check: `experiments/build_fig_hero.py` hardcodes `Prop. 3.1` for JAIR and `Prop. 1` for LNCS. The scratch JAIR auxiliary file confirms that `prop:equivalence` remains 3.1, and it remains the first proposition in LNCS. No hero change is needed for these proposals. The moved threshold becomes U.1 and the destructive example U.2 in the isolated JAIR candidate. Other proposition/example references resolve through their preserved labels.
