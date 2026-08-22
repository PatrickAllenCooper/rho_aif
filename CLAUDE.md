# CLAUDE.md — rho_aif project brain

Research project: **"Expected Free Energy as Belief-Dependent Utility for rho-POMDPs"** (Patrick Cooper, Alvaro Velasquez, CU Boulder). Core results: (1) EFE minimization is exactly a rho-POMDP with information-gain weight w=1 (Props 1–3, exact under log scoring); (2) the *Price of Information* extension recasts w as the operational shadow price w*(B) of a sensing budget B — usage curves, set-valued crossing brackets, exact scale equivariance, online dual control (Definition PI-3, Props PI-1/PI-2/PI-5, Corollary PI-4).

**This file is the operational index. The ledger of record is `Guidance_Documents/`** — read `full_paper_plan.md` (stage plan + review-response ledger, esp. Section 8) and `research_plan.md` (phase log) before substantive work. **Discipline: every change made toward the paper updates the relevant guidance document and commits with a clear message.**

**North star (Pat, 2026-08-19): deep empirical rigor is what this project aspires to.** When choosing between a faster path and a more rigorous one, take the rigorous one: verify data lineage end to end, prefer fresh reruns over trusting committed artifacts, close every "supported but not run" note, predeclare margins and protocols before measuring, and treat every claim in the paper as something a hostile referee will check against the CSVs.

## Publication state (update this block as it changes)

- **Accepted**: abridged 12-page LNCS version at IWAI 2026 (poster + spotlight, Springer CCIS; workshop Oct 14–16, 2026, Madrid).
- **Journal manuscript**: `paper/full_paper_jair.tex` (~63 pp, acmart-based JAIR approximation) passed the internal two-referee simulation loop (Gemini Pro + GPT Sol) with **uniform ACCEPT** on 2026-08-07 (ledger 8.14). **That verdict is now stale** — Stage J's regeneration and reconciliation (below) touched dozens of numbers, tables, and captions since then. A fresh referee-simulation round against the reconciled manuscript is the next step before submission.
- **Blocking manual steps (Patrick only, credential-gated)**:
  1. `twine upload` to TestPyPI then PyPI (`rho-aif` name verified unclaimed); confirm/move local `v1.0.0` tag, push tags. The `pip install rho-aif` claim (README, JAIR checklist) is false until this lands.
- **Resolved 2026-08-21 (Pat confirms)**: the IWAI camera-ready is recorded on OpenReview and accepted — this is no longer a blocking step. JAIR's extended-version prerequisite is satisfied.
- **Resolved 2026-08-19**: the JAIR template reconciliation is done — the author kit is a public download (not Overleaf-gated); `full_paper_jair.tex` now builds on the official `jair.cls` with BibLaTeX/biber (TinyTeX toolchain at `~/Library/TinyTeX/bin/universal-darwin`; build: `pdflatex → biber → pdflatex ×2`). The old tectonic path no longer applies to the JAIR file (still fine for the LNCS `full_paper.tex`).
- **Stage J: complete (ledger §9, closed 2026-08-20)**: the empirical-rigor audit found the OTC environment streams were never seed-controlled (fixed: per-episode `env.reset` seeds), MCTS-EFE was not MCTS (rewritten: UCB1 + max-backup + exact IG rewards), bits/nats inconsistency across agent families (unified on bits), EpistemicOnly leaf bug (fixed), Welch/Student mismatch in stats (fixed). Every results CSV behind the paper has been regenerated under the fixed, provenance-stamped pipeline (386/386 tests passing), and an independent 13-agent re-verification pass (blind to the prior reconciliation) found and fixed roughly 20 additional stale/incorrect claims that survived the first reconciliation round (see commit `d9fd3a0` for the itemized list). Both manuscripts compile clean. Do not assume this closes the book on manuscript accuracy — treat it as the current best state, still subject to the fresh referee round below.
- **Fresh referee round + gap closure (ledger §9.7–9.8, 2026-08-20)**: a 3-referee panel (statistics/theory/narrative) found 8 verified issues (an internal 37%-vs-79% contradiction, a proposition asserting more than its proof covers, two more "exact"/"validate" convention violations, four unbacked "statistically tied" claims) — all fixed (`724e655`). The statistics referee's MAJOR_REVISIONS driver — RockSample and Structural Inspection lacking seed-level statistics (pooled-SE only, no uncertainty measure at all for Inspection's accuracy) — was then closed for real, not just disclosed: both environments now compute seed-level SE and companion Welch-test `_stats.csv` files matching the other environments (`53aa457`). This also caught and fixed a real bolding bug in `build_rocksample_tables.py` (a "within max-SE-of-any-row" heuristic, not a real test, had produced a wrong tie/win call on RS[7,8]).
- **Third referee round (ledger §9.10, 2026-08-20)**: found 5 more major issues, the same "silent single-source/persistence gap" pattern twice more — a single-seed discount sweep masquerading as the canonical 5-seed protocol (fixed, and the real 5-seed data changed the finding: Diagnosis/Bandit's small positive gaps at low γ turned out to be statistically null) and a POMCP appendix silently discarding already-computed seed-level SE (one-line fix) — plus a copy-paste digit error and two tables missing a cited row. All fixed, `d6cfc1c`.
- **Fourth referee round (ledger §9.11, 2026-08-20/21)**: first round with **zero MAJOR_REVISIONS verdicts** (all three lenses returned MINOR_REVISIONS). Two majors fixed: the Introduction's "advantage grows with the number of observation actions" claim was contradicted by RockSample[11,11]'s zero gap (the same overclaim also survived inside the RockSample results section itself, one paragraph before its own counterexample — both fixed); the JAIR checklist falsely claimed the package is "distributed on PyPI" when that upload is still an outstanding credential-gated step. Plus 5 minor fixes. Committed `b1c734a`. **Manuscript is now assessed as at or near the practical ceiling of referee-simulation improvement** — remaining path to submission is the two credential-gated manual steps below, not further automated rounds.
- **Deep citation-completeness check (ledger §9.12, 2026-08-21)**: all 62 bibliography entries now individually re-verified against a primary source (was 14/62 before this pass); 0 factual discrepancies found, 2 harmless key-vs-year labeling mismatches noted (`todorov2007`, `walraven2024` — printed years are both correct). A 4-angle 2024–2026 literature sweep added 5 genuinely load-bearing new citations (Kouw 2026's Bethe-Lagrangian EFE reformulation — the most important find, directly adjacent to this project's own "w is not the Lagrange multiplier" claim — plus Stocco et al. 2024, Wei 2024, Sweeney et al. 2026, Laouar et al. 2026) with distinguishing prose in both manuscripts; 8 more candidates were considered and deliberately excluded as not central enough. Both manuscripts recompile clean, 386/386 tests passing.
- **Deep weakness-hardening pass (ledger §9.13, 2026-08-21)**: worked through nine self-identified weaknesses with real fixes, not softer prose — a formalized Remark on destructive-sensing scope, a direct rebuttal of the "w=1 needs arbitrary normalization" critique, an attempted (and honestly reported, structurally-negative) extension of the exact CPOMDP reference to RockSample[7,8], a mechanistic explanation unifying RockSample's non-monotonic advantage, a genuine compute-matched POMCP check (result unchanged: 88.9% vs. simulation-matched 88.8%), an n=20 statistical-power robustness check on the SARSOP TOST equivalence (evidence got *stronger*, p-values tightened 3-5 orders of magnitude), and closure of three previously-deferred referee nitpicks. Two new experiment scripts and their CSVs committed. Caught and fixed one real near-incident along the way: the n=20 TOST run's hardcoded output path briefly overwrote the canonical n=5 CSV (caught via `git status`, restored via `git checkout --`, script fixed with a `--out` flag). Also closed a genuine citation gap found via JAIR-editorial-board research (Boutilier 2002's belief-dependent-reward POMDP predecessor) and fixed a stale "distributed on PyPI" claim in the drafted JAIR cover letter. Both manuscripts compile clean (JAIR: 65pp), 386/386 tests passing.
- **Fifth referee round + full statistical-claims audit (ledger §9.15, 2026-08-21/22)**: fifth referee round found 4 more narrow issues (all fixed — a recurring "stats computed then silently discarded" bug, one "exact" calibration-word regression, two more unfixed instances of the "advantage grows with |S|" overclaim pattern). Separately, Pat commissioned a full audit: "Are all claims within the paper that are made fully statistically validated to a high standard? If not, proceed with experiments." A 48-agent audit found 38 more confirmed gaps, ~2/3 tracing to one systemic bug (seed-level stats computed via `summarize_results()` but silently dropped before reaching disk) recurring independently across ~6 experiment scripts — fixed by rerunning roughly a dozen full experiment batteries under the canonical protocol, not by softening prose. Also caught two real errors: a stale pre-code-fix table in the Testbed appendix (tuned weight was claimed as 50, current code actually selects 20/10 — full battery rerun and rewritten with a dated correction note) and a RockSample comparative claim ("unlike RS[5,3]/RS[7,4]...") directly contradicted by the paper's own stats. A bonus discovery: the Pareto sweep script never persisted a CSV at all; instrumenting it revealed Tiger/Testbed/Diagnosis's reward-maximizing weights are exactly tied across wide ranges, not single points — now reported as brackets per the paper's own shadow-price convention. Both manuscripts recompile clean (66pp), 386/386 tests passing.
- **SECURITY**: JAIR's only legitimate site is `jair.org` (AI Access Foundation). `sub.ifspress.hk` is a documented hijacked-journal clone — never submit, pay, or download templates there.
- **Resolved 2026-08-21 (Pat confirms)**: author list is Cooper + Velasquez only. David Baines is off the project (contributed nothing); the "open decision" flagged here previously is closed. No open author-list decisions remain.

## Repository map

```
rho_aif/              Installable package: agents/, environments/, belief.py, budget.py,
                      stats.py, scoring.py, benchmark.py, audit.py, CLI rho-aif-bench
experiments/          run_*.py scripts; each paper table/figure has exactly one producer
results/              Committed CSVs backing every paper number ("one battery, one table")
figures/              PDF/PNG figures
paper/                LaTeX. LIVE: full_paper.tex (long master), full_paper_jair.tex (JAIR).
                      FROZEN snapshots: paper.tex, paper_arxiv.tex, paper_iwai2026*.tex
tests/                Pytest suite (target: all passing; was 347/347 on 2026-08-07)
Guidance_Documents/   research_plan.md, full_paper_plan.md, price_of_information.md,
                      poster_content.md — the ledger of record
docs/ideation/        Dated ideation documents with verifier-checked rankings
```

## Commands

```bash
source .venv/bin/activate
python -m pytest tests/ -q                  # full suite before any commit touching code
tectonic paper/full_paper_jair.tex          # both manuscripts must compile clean
tectonic paper/full_paper.tex
python experiments/run_experiment.py all    # core envs; see README reproduction table
```

Every paper number must be regenerable via the README "Reproducing the Paper" table. Run experiments from the repo root. Canonical seeds `{42, 123, 456, 789, 1024}`.

## Writing conventions (enforced on all live .tex)

- No semicolons in prose (math `\;` allowed). No rhetorical italics/bold — italics only for definitional first use, theorem-class styling, bibliography venue names. Table best-metric bold stays.
- Topic sentences on long paragraphs; every symbol defined at first use; jargon glossed (nats, PWLC).
- Abstract: lean narrative, no dense per-environment numbers, budget-first framing (sensing budget / shadow price leads; EFE/active-inference vocabulary follows as mechanism). JAIR version uses structured abstract.
- Limitations foregrounded in intro AND conclusion, not just a back section.
- natbib author tags on all bibliography entries so `\citet` resolves.
- **Propagation rule**: every prose/claim fix is applied identically to `full_paper.tex` AND `full_paper_jair.tex`. Frozen snapshots are never edited. New masters are assembled from sources, not edited in place.
- Claim-calibration vocabulary: "near-optimal/estimated" (never "exact") for SARSOP/CPOMDP references; "stationary convergence plus empirically demonstrated re-adaptation" (never "tracking guarantee") for Prop PI-5; "operationalized" (not "dissolved"); "exercises" (not "validates") for empirical agreement with theory. w is NOT the Lagrange multiplier of the usage-cap constraint; no universal closed form w*(R, γ, |S|, H) is claimed.

## Citation policy

Every new citation is verified against the publisher or arXiv record BEFORE entering the bibliography, with the check (date + source) recorded in `price_of_information.md`'s table or `full_paper_plan.md` §8.4. Specifics: SAC auto-temperature cites arXiv:1812.05905 (not the ICML paper); use published year not citation-key year.

## Statistics protocol

- 5 seeds `{42,123,456,789,1024}`; deviations enumerated in the reproducibility checklist. Agents with internal RNG (POMCP) get per-run seeds (`vary_agent_seed`).
- Seed-level Welch t-tests on per-seed means + seed-level SE are PRIMARY in main tables; pooled episode-level SE in appendices; Holm–Bonferroni over seed-level p-values.
- NEVER report seed-level Cohen's d (n=5 inflates |d| by orders of magnitude). Never claim pooled/seed-level sign agreement as evidence (guaranteed by construction under balanced seeds).
- Equivalence claims require TOST with predeclared margins (one sensing action's cost per environment); otherwise say "within sampling error".
- Shadow prices reported as crossing brackets (w_lo, w_hi] with SEs, never points at gap budgets.
- Reward-tuned vs success-tuned baselines always disclosed (w*_ret vs w*_succ). POMCP comparisons labeled simulation-matched, not compute-matched.
- When a committed CSV disagrees with a fresh run under the stated protocol, the fresh run is authoritative and the correction is flagged in text, never silently overwritten.

## Process rules

- **Stage verdicts**: every development/experiment stage gets an acceptance criterion and a HOLD/PARTIAL/FAIL verdict recorded in `full_paper_plan.md` and mirrored in `research_plan.md`. Failures become scoped limitations with numbers, never hidden.
- **Review ledger**: reviewer/referee feedback is folded point-by-point into `full_paper_plan.md` §8 with a disposition per item (implemented or explicitly waived with reason). Verify every actionable point against manuscript, code, and CSVs before editing.
- **Referee simulation**: before submission, independent referee subagents review the manuscript; iterate rounds until uniform ACCEPT; referees re-verify fixes against file text, not change summaries.
- **Availability claims**: verify public links from a logged-out fetch before claiming them (this caught the repo being private while cited as public).
- Experiment scripts create parent dirs defensively before checkpoint writes (a relative-path crash once destroyed ~35 min of compute).
- Errors in guidance docs are corrected in place with dated correction notes, never deleted.

## People

- **Patrick Cooper** — project lead, implementation, primary author (paco0228@colorado.edu, GitHub PatrickAllenCooper).
- **Alvaro Velasquez** — co-author (CU Boulder).
- **Ashutosh Trehan** — advisor.
- **[Correction, 2026-08-21]** David Baines was previously listed here as a collaborator with unconfirmed authorship status. Pat confirms he is off the project and contributed nothing — not an author, not a collaborator. Removed from the author list and this roster.
