# Independent empirical and reproducibility review — 2026-10-21

## Recommendation

**ACCEPT. No required empirical or reproducibility revision identified in the reviewed source.** This is a referee-style recommendation for the manuscript's bounded contribution, not a forecast of the journal decision or a claim that every implementation is ideal. I did not use previous acceptance decisions as evidence.

The paper supports a specific calibration procedure for an already chosen information-weighted policy family. It does not claim that matching an expected-use target solves constrained reward optimization, guarantees a hard cap, establishes superiority over modern POMDP solvers, or produces robust deployment behavior. The empirical evidence supports that restricted claim and directly reports several unfavorable results. Those restrictions are material to my recommendation.

Reviewed repository HEAD: `f2d4069`. Last manuscript commit: `86fe27c`, October 2, 2026 at 15:38:13 MDT. Initial reviewed JAIR source SHA256: `db283e6949d6a018a1bbed7fb93c4291b0b5b25dbf0fab63d2b43978da4fb9a9`. Line references below refer to that source. A final-source check should follow any edits by the other reviewers.

## Work performed

I read the current manuscript, including its supplementary specifications, statistical conventions, baseline controls, sensor protocol and reproducibility checklist. I read the project guidance to identify reporting conventions, then checked methods against producer code and saved records. No new experimental episodes, model fits, bootstrap draws, full test suites or GPU work were run.

`evidence_recompute.py` is a read-only independent recalculation from saved CSV/NPZ records. Its results are in `evidence_recompute.json`. The cap/equality checks enumerate one- and two-policy mixtures instead of invoking the repository LP routine, avoiding circular confirmation of that routine. Sensor summary checks average archived candidate outcomes directly, instead of rerunning the analysis producer.

## Verified numerical and design claims

1. **Usage target versus cap reference (lines 545–607, 1180–1191).** All three endogenous reference values reproduce: Tiger 5.016, Diagnosis −1.2653333333, Bandit 6.3143333333. The maximum-reward sampled policy is feasible in each case. Tiger is exactly on its cap; the current manuscript correctly says the cap does not lower the maximum sampled reward, rather than calling every cap strictly slack. The common `rho_aif/budget.py` routine uses an inequality-constrained dual-simplex LP, and its support invariant is asserted. No old equal-usage interpolation is being presented as the cap reference.

2. **Held-out calibration (lines 557–594).** The 12 attainable rows have maximum absolute usage error 0.123 observations, and three overspend in their held-out means. The endpoint mixture is not a general reward-optimal family member. All same-stream cap-envelope values and paired SEs independently reproduce from saved seed rows. Eight of 11 distinct budgets have a negative nominal cap-gap interval. Equality-envelope values reproduce from the subsidized reference points. Two target-gap intervals exclude zero on each stream, with Diagnosis's budget changing and only Bandit's gap target recurring. The source retains the plug-in/selection, finite-grid, cap-feasibility, multiplicity, fresh-usage and Tiger rare-event caveats. Those caveats are essential; the calculations do not provide population constrained-optimality certificates.

3. **Recovery estimand (lines 485–496).** Independent rolling-window calculation from all 8,000 episode records reproduces the 20 restricted recovery times. Means are 157.3 and 51.2, the paired difference is 106.1, and the Student-t interval is [96.7701442, 115.4298558]. All ten differences favor the reset heuristic. There are nine observed recoveries in the decay arm and ten in the reset arm. Two decay recoveries occur exactly at 180, separate from the one censored case. Thus the restricted estimand is handled correctly. Maximum archived weight is 3.0896813, consistent with the stated inactive upper projection. Runner code explicitly passes the per-episode seed through the rescale. The theorem is not asserted to cover the reset heuristic or nonstationary experiment.

4. **SARSOP equivalence (lines 534–543, 1176–1178).** The 60 episode-matched per-seed records reproduce Diagnosis +0.1118 with SE 0.0899125 and paired TOST p=3.2031e−9, Bandit +0.0435 with SE 0.0313284 and p=4.5772e−12, and identical Tiger means. The zero-variance Tiger branch is appropriate for identical differences within the margin. Retrospective initial margins, additional-seed timing, solver approximation and different stream conventions are stated. Equivalence is restricted to the specified margins and environments.

5. **POMCP controls (lines 939–961).** Independent selection from the tuning CSV reproduces all six solver/environment choices. Recalculated Welch p-values agree with the selected-comparison CSV, and all six comparisons survive its Holm family. The current Tiger comparison is 98.2% versus 93.2%, and reward 4.326 versus 0.391. The source discloses prior inspection of the canonical sweep before choosing the selection rule/grid. Code inspection confirms subtraction of simulated observation cost and updated-path rollout belief. The clairvoyant depth leaf and belief-expected rollout payoff remain explicitly disclosed rather than being represented as fully faithful POMCP. General solver superiority and isolated architectural causation are not claimed.

6. **Real sensor study (lines 613–637, 1129–1157).** Reconstructed 345 usage, accuracy and reward cells from saved per-case candidate outcomes with a maximum discrepancy of 1.78e−15. Verified 106 candidate archive hashes. Recomputed the adjusted usage-error intervals from saved bootstrap arrays: B=4 [−0.2096901, 0.2553966], B=8 [−0.3617954, 0.4108571], and B=2 unavailable in all 2,000 replicates. The headline test usages, accuracies, direct-policy controls and fixed-count controls match. The analysis code independently resamples calibration/test within batch-class strata and reselects calibration policies on each draw. It explicitly conditions on one fitted model. The later-batch selections remain frozen. The failed B=2 request, failed all-target criterion, classification disadvantage, and later overspending remain visible in the main text and conclusion.

   The protocol was committed as `fb3a9de` on October 1 at 18:41:25 MDT, before data preparation and policy evaluations in the saved manifests. Calibration ran October 2 at 00:59:41–00:59:43 UTC and held-out replay at 01:00:27–01:00:41 UTC (October 1 locally). This supports the independence-of-usage-curves disclosure. Researcher-defined targets are not misrepresented as operational requirements. The 13,910-case count and 3,550/1,175/1,208/7,977 split agree with the archived manifest.

7. **Other headline empirical boundaries.** All 52 scale-collapse records have zero usage spread across scales. The 25-budget bracket-stability archive gives 19 perfect-agreement budgets, 21 at or above 99%, and minimum agreement 0.789. The Pareto archive reproduces the sampled reward maxima: Tiger weights 0.01–20, Diagnosis 0.5–20, Bandit 1 and 2, Testbed 0.01–0.5, Tileworld 20. Thus the three-of-five statement is accurate. The source preserves the unfavorable Testbed, Tileworld, RS[11,11], Inspection reward, navigation, misspecification and sensor-transfer findings. Core-table values were compared with their relevant summary CSVs; these checks did not reveal a conflicting number.

8. **Reproducibility scope (lines 1257–1288).** The checklist says Partially for complete raw simulation records and names the actual per-seed/per-case archives. The referenced sensor outputs and candidate trajectories exist. The environment document agrees with the manuscript's separate simulation and sensor platform disclosures. The public sensor reproduction instructions specify source checksum, fitted-model and row identities, package versions and preservation before rerunning. Publication to PyPI is described as planned. I found no claim that all batteries have complete episode-level archives or that a new machine must reproduce floating-point decisions bit-for-bit.

## Optional wording improvements

These are not scientific acceptance conditions and should not trigger further experiments.

- **Line 921, Statistical Conventions:** “since episodes within a seed are not independent” is stronger than necessary across runners with fresh per-episode resets. Prefer “Primary inference uses per-seed means to reflect variability across the independently seeded runs.” This explains the chosen inferential unit without asserting dependence for every battery. The primary tests are already conservative seed-level analyses, so this does not change their numbers or conclusions.
- **Line 1281, checklist:** “estimates the optimality gap directly” could be made fully consistent with Section 6 by saying “reports the measured reward gap to the sampled cap-feasible reference.” The same sentence already says it is not a certified bound, and the body clearly limits the reference, so I do not regard this as an unresolved overclaim.

## Scope limits and final interpretation

This is an empirical/source-artifact audit, not a fresh full reproduction, a physical-sensor validation, or a new literature-wide novelty search. I did not re-download UCI, rebuild SARSOP, rerun simulation batteries, rerun bootstrap resampling, reverify every bibliography entry, or independently certify historical hardware metadata. Full render/build and formal theorem review belong to the parallel reviewers. I do not infer external availability from local file existence.

My acceptance recommendation rests on the calibration construction and its carefully delimited evidence, including informative negative results. A reviewer seeking a new general-purpose acquisition algorithm or broad solver improvements would not find those claims established here, and the manuscript appropriately declines them. Within its actual scope, no new empirical study is necessary to make the present manuscript defensible.


## Final-source confirmation — 2026-10-21

**Final recommendation: ACCEPT, with no required revisions remaining within this review's scope.** I inspected the actual final source diff, not only the change summary. The common replication-unit sentence is correctly mirrored into LNCS; the sampled-reference wording is correctly confined to JAIR's checklist. The controller's bounded-cost and positive-step qualifications, simplified symmetric threshold, proof pointers and clearer running-average argument do not change the audited empirical claims. Publication placeholders are removed without adding a claimed publication decision. No experiment, implementation, test or result file differs from HEAD.

Both optional empirical wording suggestions are now resolved. The saved-data recalculation passes again on the final source. Final source SHA256:

- JAIR: `bc8871292a3070c36c015cbca4b2e7229dd4bb737fe752c989ff2604e5672bcd`
- LNCS: `10b6a0c8921de1c0840ad76b8f93c92e6db93b3f15215ebb754768eb52b8347a`

I also reviewed the revised guidance Section 8.9.1. The cover's AI-use paragraph matches the manuscript acknowledgments exactly. Question 1 is 123 whitespace-separated words and Question 2 is 144, both below the recorded 150-word limit. The target/cap distinction and stated EFE assumptions are preserved. Question 3 now identifies the recorded-sensor extension, independent target choice, controls, unavailable target and transfer failures without importing an unsupported operational validation claim. The coverage exceptions remain delegated to the checklist rather than claiming per-seed archives for every result. These checks establish consistency of the drafts with the manuscript, not a new verification of JAIR's unavailable live form or an author attestation about use of tools, prior publication, or submission history.


## Delivery-hash confirmation — 2026-10-21

**ACCEPT remains unchanged.** The final JAIR-only cleanup adds an empty-DOI guard, a PDF-string definition for rho, and an optional short running title. Removing exactly those additions from the delivered source reproduces my preceding reviewed JAIR hash byte-for-byte (`bc887129…`). Thus the complete scientific body and evidence reviewed above are unchanged, not merely similar. LNCS remains at the preceding hash. Final delivery JAIR SHA256 is `c260180b50f5845132a6aeba50150373cf5ae5f74331feb9d5490aeae77d65c2`. No statistical recalculation was necessary for these metadata-only edits.
