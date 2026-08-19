# CLAUDE.md — rho_aif project brain

Research project: **"Expected Free Energy as Belief-Dependent Utility for rho-POMDPs"** (Patrick Cooper, Alvaro Velasquez, CU Boulder). Core results: (1) EFE minimization is exactly a rho-POMDP with information-gain weight w=1 (Props 1–3, exact under log scoring); (2) the *Price of Information* extension recasts w as the operational shadow price w*(B) of a sensing budget B — usage curves, set-valued crossing brackets, exact scale equivariance, online dual control (Definition PI-3, Props PI-1/PI-2/PI-5, Corollary PI-4).

**This file is the operational index. The ledger of record is `Guidance_Documents/`** — read `full_paper_plan.md` (stage plan + review-response ledger, esp. Section 8) and `research_plan.md` (phase log) before substantive work. **Discipline: every change made toward the paper updates the relevant guidance document and commits with a clear message.**

**North star (Pat, 2026-08-19): deep empirical rigor is what this project aspires to.** When choosing between a faster path and a more rigorous one, take the rigorous one: verify data lineage end to end, prefer fresh reruns over trusting committed artifacts, close every "supported but not run" note, predeclare margins and protocols before measuring, and treat every claim in the paper as something a hostile referee will check against the CSVs.

## Publication state (update this block as it changes)

- **Accepted**: abridged 12-page LNCS version at IWAI 2026 (poster + spotlight, Springer CCIS; workshop Oct 14–16, 2026, Madrid).
- **Journal manuscript**: `paper/full_paper_jair.tex` (~63 pp, acmart-based JAIR approximation) passed the internal two-referee simulation loop (Gemini Pro + GPT Sol) with **uniform ACCEPT** on 2026-08-07 (ledger 8.14).
- **Blocking manual steps (Patrick only, credential-gated)**:
  1. Submit de-anonymized IWAI camera-ready via OpenReview (prerequisite for JAIR's extended-version policy).
  2. `twine upload` to TestPyPI then PyPI (`rho-aif` name verified unclaimed); confirm/move local `v1.0.0` tag, push tags. The paper's `pip install rho-aif` claim is false until this lands.
- **Resolved 2026-08-19**: the JAIR template reconciliation is done — the author kit is a public download (not Overleaf-gated); `full_paper_jair.tex` now builds on the official `jair.cls` with BibLaTeX/biber (TinyTeX toolchain at `~/Library/TinyTeX/bin/universal-darwin`; build: `pdflatex → biber → pdflatex ×2`). The old tectonic path no longer applies to the JAIR file (still fine for the LNCS `full_paper.tex`).
- **Stage J (in progress, ledger §9)**: the empirical-rigor audit found the OTC environment streams were never seed-controlled (fixed: per-episode `env.reset` seeds), MCTS-EFE was not MCTS (rewritten: UCB1 + max-backup + exact IG rewards), bits/nats inconsistency across agent families (unified on bits), EpistemicOnly leaf bug (fixed), Welch/Student mismatch in stats (fixed). ALL OTC-derived results CSVs and paper tables are being regenerated under the fixed pipeline before submission; do not trust committed OTC numbers against fresh runs mid-regeneration.
- **SECURITY**: JAIR's only legitimate site is `jair.org` (AI Access Foundation). `sub.ifspress.hk` is a documented hijacked-journal clone — never submit, pay, or download templates there.
- **Open decisions**: author list confirmation (Cooper + Velasquez listed; David Baines's role unrecorded as a decision — plan says "confirm author list before submission").

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
- **David Baines** — collaborator, theoretical lead (GitHub davidpantile). Authorship status unconfirmed.
- **Ashutosh Trehan** — advisor.
