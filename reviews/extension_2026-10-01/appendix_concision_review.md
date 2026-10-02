# Appendix concision review, 2026-10-01

The appendix can lose approximately 4,600 whitespace-delimited source tokens through substantive compression, with no relocation into another appendix. I propose 26 changes containing 29 exact guarded replacements in `appendix_concision_proposals.json`. The optional final change removes one duplicated Tileworld illustration. The other 25 compress prose. This is an editorial proposal set, not an applied manuscript revision or an acceptance verdict.

The source-token measure includes TeX commands and, for the optional figure deletion, accessibility description text. It is not a rendered word count or a page estimate. Compiling the combined manuscript will determine the page reduction.

## Snapshot and scope

Reviewed both live masters after reading `AGENTS.md`, the latest ledger entries in `Guidance_Documents/full_paper_plan.md` and `research_plan.md`, and the final reports under `reviews/polish_2026-10-01/`. The prior acceptance judgments were not treated as evidence that a proposed cut is safe.

- JAIR source SHA256: `73f6ee1feb9bf2202bc141dadf52ae557816a8934ecfa0db47a1836b07b4a44c`.
- Twin source SHA256: `25a9eaa30eac01e354775cd33f8018685dc171cc932e5f5e5fc1ba6a0aeb0a44`.
- No manuscript master, experiment, result CSV, producer, or bibliography was edited.
- No previous assembler was run. The new JSON contains the full old and new text, with per-file uniqueness guards.

The audit examined the complete appendix structure and concentrated exact cuts on duplicated experimental explanations, methods that were described twice, and repeated interpretations immediately beside their tables. The JSON records the preserved qualifications and evidence locations for every change.

## Highest-value cuts

- **AC13, agent specifications and tuning:** about 640 source tokens. Keeps every agent distinction, the PWLC citation boundary, the misleading historical posterior-vote CSV label, the own-class tuning grid, single-stream noise, seed reset and tie rules, and the seed-7 overlap disclosure.
- **AC21, six RockSample departures:** about 350 source tokens. Keeps every departure from the published benchmark, finite-range sensor floor, re-sampling behavior, anytime exit, hidden-state assumptions, and non-comparable returns/state counts.
- **AC20, OTC environment definitions:** about 300 source tokens. Describes each environment once without re-explaining binary partitions. All rewards, accuracies, costs, and terminal-action semantics remain.
- **AC23, TOST design:** about 270 source tokens. Retains the retrospective five-seed margin choice, prospective added seeds, exact operational margins, per-seed Welch unit, covariance formula, and the distinction between pairing by seed and matching episodes. The actual five-seed, twenty-seed, and episode-matched results remain untouched.
- **AC24–25, core results and effect sizes:** about 510 source tokens together. Keeps null/negative controls, all chance rates, measured rather than structural Tiger identity, two uncertainty levels, guaranteed sign agreement under balanced aggregation, and the non-interpretation of inflated seed-level Cohen's d.
- **AC06 and AC19, statistical/protocol repetition:** about 470 source tokens together. Keeps correction-family sizes, zero-variance exclusions, every family exception, pooled equal-variance-test disclosure, canonical counts, cross-battery seeding cautions, and computational-versus-sensing budgets.

The remaining cuts preserve local counterexamples rather than merely forwarding readers elsewhere. In particular, AC01 retains Testbed over-observation and the horizon/unit boundary, AC05 retains the weak PyMDP control, AC07–08 retain the horizon sweep's lenient criterion and descriptive status, AC09–10 retain the discount and misspecification failures, and AC18 retains the fact that offline budget calibration saves no sampling relative to direct tuning.

## Optional redundant figure removal

**AC26 is an atomic group and depends on AC20.** Remove the standalone `fig:tw_belief` strip and retain `fig:tw_comparison`.

This is a true repeated illustration. Both `fig_belief_evolution` and `fig_agent_comparison` in `experiments/run_tileworld.py` select the same EFE episode with the same deterministic seed search, environment, horizon, and scan limits. Both renderers select the same five scan positions through the same `linspace` rule. Text extracted from the committed PDFs confirms steps 1, 4, 8, 11, and 15, followed by a correct commit at step 16 for reward −5.0. The comparison figure adds Planning and InfoGain-Tuned. Its caption already states the uniform prior that the standalone strip draws separately.

The JSON supplies separate JAIR/LNCS figure guards because only JAIR has a `Description`, plus two prose-reference repairs. AC20 removes the third pointer from the Tileworld definition. In the combined dry run no reference to the removed figure remains. The existing `app:tw_belief` subsection label may remain attached to Belief Evolution, which still contains the Diagnosis illustration. Keep the unused PDF and its producer in the repository for reproducibility. Let the normal source packager discover the reduced dependency set.

I do **not** recommend deleting the full result tables as duplicates of main tables. They retain additional agents or different uncertainty levels. In particular, the two Tileworld presentations distinguish pooled episode uncertainty from seed-level uncertainty. Nor should the Diagnosis trajectory/decomposition figures be removed merely because both concern belief evolution: they expose different decisions and the recursive-score qualification. The standalone Tiger trajectory is compact and communicates the commit crossover directly.

## Validation and boundaries

An in-memory sequential application verifies that every proposed old span occurs exactly once in its specified current master and that the proposals do not overlap. The dry run also confirms:

- Every formal proof environment is byte-identical, and the direct controller proof outside a proof environment is byte-identical.
- All 29 displayed-mathematics blocks remain.
- Main text, theorem assumptions there, AI disclosure, and the complete JAIR reproducibility checklist remain byte-identical.
- Citation-key sets are unchanged. Attributions inside the shortened passages retain their original scope.
- No new undefined reference is introduced when included-table labels are accounted for. The only removed label is `fig:tw_belief`, with no surviving reference.
- No prose semicolon is introduced.

I read the adjacent tables and relevant archives for the cuts involving scaling, horizon rates, discounting, misspecification, proper scores, the audit example, and illustration provenance. A direct recount of `results_nearopt_horizon.csv` reproduces 30, 58, and 79 passes among 100 environments at the three horizons. This is not an independent rerun of every historical result.

The fitted-reference and fresh-seed frontier paragraphs are left intact because they carry distinct retrospective/non-blind and nominal-interval qualifications. Likewise, the RockSample/POMCP solver fidelity controls, shared-leaf limitation, negative Navigation finding, distractor failure, and full state-preservation/destructive-sensing discussion are retained. The proposal set does not trade these limitations for apparent brevity.

After integration, audit the actual combined diff against the then-current sources, run the claim verifier, and build both PDFs. A stale guard should trigger a manual rebase of that individual proposal, never reconstruction from an older assembler. The root task owns the guidance-ledger update and commit for any applied batch.
