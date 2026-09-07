# Changelog

All notable changes to this project are documented here. Format loosely
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [2.0.0] - 2026-09-07

The JAIR-submission release. Everything in `v1.0.0` was the IWAI-era
benchmark package; everything here rebuilds it under a substantially
stricter empirical-rigor standard, closes an 18-round multi-model referee
loop, and verifies every citation and number-bearing claim in the
accompanying paper against primary sources. 255 commits since `v1.0.0`.

### Breaking

- `rho_aif/agents/rocksample_pomcp.py`'s `RockSamplePOMCPAgent` (a flat
  one-ply Monte Carlo policy with no search tree or UCB1, previously
  mislabeled `POMCP`) is now `RockSampleFlatMCAgent` in
  `rho_aif/agents/rocksample_agents.py`, with a genuine tree-search POMCP
  implementation added alongside it. Code importing the old name breaks.
- `MCTSEFEAgent` (`rho_aif/agents/mcts_efe.py`) was rewritten from
  dead-code masquerading as tree search into a real UCB1 tree with
  max-backup and exact per-node information gain. Existing callers get
  materially different action selection and results, not just a bugfix.

### Added

- `MCTSEFEAgent` gains `backup="max"|"mean"` and
  `in_tree_info_gain=True|False` switches; `POMCPAgent` gains
  `rollout_policy="uniform"|"info_gain"`. Used by three new experiment
  producers: `experiments/run_mcts_efe_ablation.py`,
  `experiments/run_pomcp_exploration_sweep.py`, and
  `experiments/run_rocksample_efe_diagnostic.py`.
- `tools/review_pipeline/verify_claims.py`, a mechanical pre-check that
  diffs a manuscript against a base commit and verifies every cited CSV
  file exists, every table/figure reference resolves, every "Table X's Y
  rows" claim matches what that table contains, and every decimal number
  matches its stated precision in the CSV named nearest it.
- `experiments/build_mcts_ablation_tables.py`, generating
  `paper/tables/mcts_ablation.tex` and `paper/tables/pomcp_exploration_sweep.tex`
  from their CSVs.
- Seed-level standard errors and Welch-test companions for every core
  battery (previously pooled-SE only in several places).
- `run_price_of_information.py --refresh-summary` and `--replot-figures`
  flags for regenerating derived output without re-running episodes.

### Fixed

- OTC environment streams were never seed-controlled; every experiment
  script now seeds `env.reset` per episode, making every reported number
  bitwise reproducible under the canonical seed set.
- Bits/nats unit inconsistency across agent families, unified on bits.
- `EpistemicOnlyAgent`'s leaf evaluation contradicted its own stated
  semantics.
- `stats.py` used Student's t where the stated methodology is Welch's.
- A per-row provenance-stamping bug (`git rev-parse` re-run per agent
  row) could split one results CSV across two git revisions if a commit
  landed mid-battery; provenance is now read once per process.
- The price-of-information summary JSON carried a stale monotonicity
  verdict contradicting its own backing CSV; it is now a pure function of
  that CSV, recomputed on every run.
- A committed shadow-price CSV predated a solver fix and violated the
  paper's own bracket definition; regenerated.
- Roughly 60 additional stale or overclaimed prose statements found and
  fixed across an 18-round multi-model referee loop, five exhaustive
  class sweeps (every quantifier, cross-reference, protocol claim,
  numeric value, and figure description checked against its artifact),
  and a full bibliography re-verification (68/68 entries checked against
  Crossref, arXiv, or publisher records; zero hallucinated references,
  three real corrections).

### Changed

- Statistics protocol: seed-level Welch t-tests on per-seed means are now
  primary everywhere; pooled episode-level SE is appendix-only; TOST
  equivalence testing with predeclared margins replaces informal "not
  significantly different" claims; Holm-Bonferroni correction applied
  within each declared comparison family.
- The accompanying manuscript (`paper/full_paper_jair.tex`,
  `paper/full_paper.tex`) went from a workshop-length draft to an 81-page
  JAIR submission, assessed against a 24-article sample of published JAIR
  papers (median 39.5 pages) and brought down via an adversarially-judged
  concision pass (48 verified cuts, ~1,130 words) after the readers found
  the remaining content was dense supporting evidence rather than
  padding.

### Publication milestones

- Abridged 12-page version accepted at IWAI 2026 (poster + spotlight,
  Springer CCIS).
- Full manuscript passed 18 rounds plus a confirmation round of
  independent multi-model referee review with unqualified accepts across
  every reviewer lens (statistics, active inference, POMDP planning,
  decision theory, editorial).

## [1.0.0] - 2026-07-22

Initial installable release: the Gymnasium benchmark suite, reference
agents (EFE, Planning, Planning+IG, Myopic, Thompson, POMCP, IDS), proper
scoring rules, and the `rho-aif-bench` CLI, alongside the IWAI 2026
camera-ready submission.
