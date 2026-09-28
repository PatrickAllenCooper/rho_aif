# Independent evidence review, round 1

Reviewer: reviewer2, empirical/statistical claims, reproducibility, and repository usability.

Reviewed state: clean `c211422e82f9bc70150473f1a1ca910f3c74a314`, 2026-09-28. Initial verdict reached before seeing the other review. The earlier four-provider acceptance was treated as history, not evidence. I read AGENTS.md, the dated handoff, ledger 9.17.50 in both guidance documents, the current abstract/conclusion and relevant empirical/checklist sections, the new producers, supporting evaluation and LP code, and the citation reports. I did not edit manuscript, code, or committed data.

## Initial verdict: MINOR REVISIONS

The new data and calculations reproduce. The principal numerical findings are genuine and their major limitations are substantially disclosed. Four focused wording corrections remain necessary. None requires a new experimental campaign, changed results, or a weaker scientific standard. Acceptance remains conditional on inspecting the actual corrected final state, rather than a response summary.

## Required changes

### E1. Name what the new frontier intervals condition on

Locations: `experiments/run_frontier_reference_heldout.py:114-131`; `paper/full_paper_jair.tex:754`; `paper/tables/budget_frontier.tex:5`; abstract at line 70 and conclusion at line 1075. Propagate shared prose to the long master and update the table producer rather than hand-editing its output.

The producer estimates the reference envelope from all five held-out seed means, chooses its policy support and mixture weights `q`, and then computes the standard error of `family_seed - q @ reference_seed` while holding that fitted `q` fixed. Four distinct budgets have a two-policy reference mixture: Diagnosis 0.25, 0.5, gap, and Bandit gap. Their `q` depends on the same estimated usages that determine the envelope. Thus the t intervals are nominal, pointwise, plug-in intervals, and do not incorporate reselection of support, uncertainty in the fitted mixture weights or cap feasibility, or multiplicity across budgets. They are not established 95% coverage intervals for the unknown population constrained frontier.

The text already discloses the maximum-over-noisy-points selection bias, which is valuable, but that sentence does not explicitly describe the conditioning of the displayed SEs or the omitted usage/mixture-weight uncertainty. Abstract/conclusion elevate the eight-of-eleven count with unqualified “paired 95 percent intervals.” Preserve the exact count but call the intervals nominal pointwise (or equivalently explicit wording), explain in the section and caption that the fitted support/weights are held fixed, and say the comparison is descriptive rather than a selection-adjusted claim about the population frontier. Mirror this in the producer docstring. Merely calling them “conditional 95% intervals” would still risk implying selective-inference coverage, which the calculation does not establish.

Evidence: independently recomputed every envelope and all 72 gap/SE/CI rows using a separate SciPy LP invocation and direct t formulas, maximum numerical discrepancy 2.22e-16. An exploratory delta-method check including estimated binding-cap usage changes the four affected SEs (Diagnosis 0.5, for example, 0.15438 to 0.10909), demonstrating that the current SE is a specific plug-in quantity. This is not proposed as a replacement analysis and does not change the local correction needed. The actual data do not force a new experiment.

### E2. Scope the abstract's percentage to Bandit

Location: `paper/full_paper_jair.tex:70`, “a shortfall of up to about a fifth of the reference reward.”

The underlying result is the maximum *absolute reward-unit* shortfall, 1.316, occurring at Bandit's 0.75 budget, whose reference reward is 6.267, so its ratio is 0.20999. Diagnosis has negative reference rewards and relative magnitudes as large as 1.104 / 1.208 = 0.91391. A global “up to” percentage is therefore neither a clear nor correct summary across environments. The body and conclusion already correctly attach the fifth to Bandit. Replace the abstract phrase with, for example, “the largest absolute shortfall occurs on Bandit and is about a fifth of its reference reward,” or simply specify Bandit's largest budget. Do not add percentages for the negative-reward domain.

### E3. Remove the README's belief-reporting attribution to EFE

Location: `README.md:73`, “Under log scoring, EFE at w=1 is the theoretically correct belief reporter (Bernardo 1979).”

Properness of a log score concerns truthful reporting of a predictive probability distribution. It does not make the EFE action-selection policy uniquely or especially the correct belief reporter: the released planners share Bayesian belief updates, and a reward-only planner can report its posterior correctly too. The manuscript's substantive link is between expected information gain and expected utility under log scoring, not an EFE-only reporting theorem. Rephrase this README sentence to that link and/or say the score columns evaluate terminal beliefs. This is a small but real scientific overclaim in the user-facing artifact.

### E4. Separate population optimality from a noisy measured reward

Location: `paper/full_paper_jair.tex:739`, “Since a true optimum cannot lie below EFE's measured reward, a negative estimated gap indicates reference-frontier noise rather than a real violation.” Mirror in `full_paper.tex`.

The true optimum cannot lie below the reward of a feasible EFE policy **in expectation**. It can lie below that policy's finite-sample measured reward. Moreover the SARSOP reference is approximate, so a negative empirical gap can reflect approximation error or sampling error on either side, rather than only “reference-frontier noise.” The surrounding paragraph already explains Monte Carlo uncertainty, making a precise local replacement straightforward. State that the population constrained optimum dominates a feasible policy's population reward, whereas the negative estimated gap is consistent with simulation uncertainty and the reference's approximation. Do not imply a certified bound from either measured reward.

## Independent verification evidence

### Same-stream frontier and rare Tiger events

I reran the entire new reference producer against all committed policy files, redirecting only its output directory to a temporary audit directory. This freshly evaluated 36 policies under both the canonical lineage-check stream and the held-out stream. Every canonical reward and usage reproduced within the producer's 1e-9 gate. All 36 held-out reference rows (12 non-provenance columns) and all 72 gap rows (17 non-provenance columns) are exactly identical to the committed files, excluding only git SHA and generation time. Temporary output: `/var/folders/rp/5fry8hzd6r79lbs65w92n8b00000gn/T/rho-final-evidence-frontier-if60hmql`.

Separately, from the archived seed values and a fresh LP calculation, the endpoint-mixture gaps/SEs reproduce as follows (reward units):

- Tiger 0.25: -0.326 / 0.037229; 0.5: -0.722 / 0.060531; 0.75: -1.032 / 0.058086. Gap duplicates the 0.5 budget.
- Diagnosis 0.25: -0.029508 / 0.281583; 0.5: -0.757358 / 0.154377; 0.75: -1.104 / 0.219217; gap: +0.001198 / 0.222308.
- Bandit 0.25: -0.211 / 0.123100; 0.5: -0.571 / 0.093185; 0.75: -1.316 / 0.076851; gap: -0.586736 / 0.196328.

Exactly 9 of 12 rows, or 8 of 11 distinct budgets, have the recorded pointwise upper t endpoint below zero. The maximum observed absolute usage-target error is 0.123 observations, correctly rounded as within 0.13. Calibration/held-out seeding and independently seeded per-episode mixture draws match the stated protocol. The family is frozen on calibration data; the new reference envelope is selected on the evaluation means, motivating E1.

Every evaluated Tiger family row has per-seed reward exactly `10 - observations`, as does the support reference. Adding one wrong reference commit (110 reward units over 100 episodes = 1.1 to one seed's family-minus-reference gap) in each of the five possible seeds makes both smaller-budget intervals cross zero. The 0.75 interval remains negative in all five placements (upper endpoints range from -0.257 to -0.068). The manuscript's rare-event caveat is real, sufficiently prominent, and must remain. No additional Tiger campaign is required for the explicitly bounded claim.

### Bracket-selection bootstrap

I recomputed the bootstrap independently from the archived per-seed matrix, without invoking the production solver: draw the same joint seed indices in the stated environment order, average usage at every weight, find the last strictly below-budget sample and the first following at-or-above sample, otherwise return no bracket. All 25 complete bracket-frequency distributions match the long-form counts exactly, not just their summary extrema.

The reported bracket appears in all 2000 resamples at 19 of 25 budgets and in at least 99% at 21. Minimum agreement is 0.789 at Inspection-N8's lowest budget. Tiger's two edge-budget agreements are 0.8455 and 0.9065, with the alternatives unbracketed. The mean usage curves reproduce to 1.78e-15 and their seed SEs to 6.39e-16. Seeds are resampled jointly across weights, correctly preserving common random-number dependence. The result is appropriately descriptive and is not a population confidence guarantee. The archived per-seed data and both summary/count files are tracked.

### TOST archive and numerical claims

I independently reconstructed the unpaired Welch TOST from all per-seed means at n=5 and n=20, including both one-sided tails, Welch degrees of freedom, SE and 90% interval. Maximum error is 1.11e-16 for n=5 and 8.33e-17 for n=20. I also independently verified paired TOST probabilities and SEs for both seed counts, including the zero-difference Tiger degeneracy.

At n=20, p_TOST is 4.47739e-10 (Tiger), 6.82288e-7 (Diagnosis), and 6.02062e-11 (Bandit), as reported. Tiger's 90% interval is [-0.208664, 0.208664]. All 17 pre-existing n=20 summary columns are exactly unchanged from commit 9e2666d, and the new 60-row per-seed file makes those results recomputable. The fixed margins, retrospective n=5 chronology, and pre-fixed added n=20 seeds are disclosed. Positive sample covariance supports the stated conservative comparison with the unpaired analysis on the observed data. The three n=5 unpaired tests pass the stated Holm procedure.

### Availability and usability

Current `README.md:22` explicitly says PyPI publication is not live and gives clone/editable-install instructions. Current checklist `paper/full_paper_jair.tex:1848` explicitly says distribution is planned, not published. The handoff and AGENTS publication note claiming those files still falsely advertise PyPI are stale guidance, not defects in those current documents. Root is independently checking installation/build commands and reconciling that stale guidance; I did not duplicate the source-install smoke test.

A fresh unauthenticated browser fetch of [the repository](https://github.com/PatrickAllenCooper/rho_aif) identifies it as Public and renders the current README. A fetch of the [PyPI project API](https://pypi.org/pypi/rho-aif/json) returns 404. The required SARSOP policy artifacts, newly archived data, and producers are tracked. The new reference replay requires no local solver build because it reads the committed policy files. The checklist appropriately labels unaggregated data availability “Partially.”

### Citations

Read all three citation-slice reports and the cross-check, including the scope limitations and benign exceptions; did not infer source validity from their verdict lines alone. Independently fetched current Crossref records for [Schuirmann 1987](https://api.crossref.org/works/10.1007/BF01068419) and [Schmidhuber 1991](https://api.crossref.org/works/10.7551/mitpress/3115.003.0030). The former is 15(6):657–680 and the latter 222–228, matching the corrected bibliography. Web rendering of the API URLs failed, but direct unauthenticated HTTPS JSON fetches succeeded. I did not repeat all 69 external lookups and do not represent this round as a second exhaustive citation audit. No newly hallucinated number or reference was found. E3 concerns what a valid source is claimed to support.

## Optional polish, not conditions of acceptance

- In the staircase paragraph, the new bootstrap discussion makes “On these two domains” less clear: its intended antecedent is Bandit and Tileworld, but the immediately preceding discussion names Inspection and Tiger. Naming Bandit and Tileworld explicitly would remove that ambiguity (`paper/full_paper_jair.tex:667`).
- The primary body could foreground the same-stream comparison and move the earlier cross-stream numbers to an artifact-history note. Current disclosure is honest, so this is readability only.
- A future confirmatory reference experiment could freeze reference support/mixture weights on separate data or propagate envelope selection and usage estimation in its inference. That is not required for the descriptive, explicitly qualified result requested in E1.

## Scope and confidence

High confidence in the numerical recomputations, replay lineage, and four narrow required corrections. Medium-high confidence in overall empirical suitability within the paper's explicitly limited scope. I did not rerun the entire legacy experiment suite, re-prove the theoretical propositions, or inspect every rendered page; the other reviewer/root own those complementary checks. This verdict does not depend on their outcome or on obtaining an acceptance vote. The changed paper can earn an unqualified ACCEPT once these concrete scientific wording defects are closed and no regressions are introduced.
