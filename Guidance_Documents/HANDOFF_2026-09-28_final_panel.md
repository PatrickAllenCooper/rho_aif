---
artifact_contract: "ce-handoff/v1"
created_at: "2026-09-28T15:10:00Z"
title: "Handoff: final four-provider JAIR panel and citation pass"
summary: "State after the 2026-09-28 polishing pass: four unqualified JAIR accepts, three new experiments, citations verified, what remains for Pat before submission."
keywords: ["jair", "final-panel", "handoff", "citations", "bracket-stability", "frontier-heldout", "tost-n20"]
cwd: "/Users/pat/code/rho_aif"
resume_focus: "Submission at jair.org; nothing scientific is open"
repository: "PatrickAllenCooper/rho_aif"
repo_root_sha: "4fe295aaa99352c3ef5f06ac6e88f01290b4c7ac"
branch: "main"
head: "3255b68"
---

# Handoff: final four-provider JAIR panel and citation pass (2026-09-28)

Read this first if you are picking up the project after 2026-09-28. The ledger
of record is `Guidance_Documents/full_paper_plan.md` section 9.17.50 (mirrored
in `research_plan.md`). This document orients. The ledger and the committed
artifacts are authoritative wherever they differ.

## Where things stand

- **The manuscript has four unqualified accepts out of four** from a final panel of top models, one per provider:

  | Reviewer | Lens |
  |---|---|
  | Gemini 3.1 Pro | active inference and theory |
  | Fable 5.1 thinking-high | decision theory and POMDPs |
  | Grok 4.7 | JAIR associate editor and clarity |
  | Sol 5.6 | statistics and reproducibility |

  Fable and Sol ran at medium effort, the highest this environment offered for them. Round 1 was two accepts and two minor revisions. Grok accepted in round 2 and Sol in round 3.
- **Citations were checked after all polishing was done.** All 69 entries were verified against primary records and every citing sentence was read. There are zero hallucinated references. There was one field correction: `schmidhuber1991` pages changed to 222--228, per Crossref.
- **Git and build state**:
  - HEAD `3255b68` on `main` is pushed to `origin`, and the working tree was clean at hand-off.
  - JAIR `paper/full_paper_jair.tex` is 114 pp, with one pre-existing 2.9pt overfull box, and the hero figure is on page 4.
  - 486/486 tests pass, and `tools/review_pipeline/verify_claims.py` has no hard failures.
- **No scientific work is open.** What remains is Pat's, listed at the end.

## What this pass changed (pointers, not contents)

**New experiments.** Each protocol was recorded in the ledger before any output was seen.

1. **Frontier reference on the held-out stream**: `experiments/run_frontier_reference_heldout.py`.
   - Outputs: `results/results_cpomdp_frontier_heldout.csv` and `results/results_budget_frontier_heldout_reference.csv`.
   - Result: the family falls short of the estimated envelope on 8 of 11 distinct attainable budgets.
   - Verdict: **PARTIAL**, because of the Tiger rare-event caveat below.
2. **Bracket-selection stability**: `experiments/run_bracket_stability.py`, a seed bootstrap with 2000 resamples.
   - Outputs: `results/results_price_usage_curves_per_seed.csv`, `results/results_price_bracket_stability.csv`, and `results/results_price_bracket_stability_counts.csv`.
   - Result: the reported bracket is recovered in every resample at 19 of 25 budgets, with a minimum agreement of 0.789.
   - Verdict: HOLD.
3. **n=20 TOST per-seed archive**: `results/results_tost_sarsop_n20_robustness_per_seed.csv`.
   - Result: all 17 original summary columns reproduce exactly.
   - The exact command is in the README reproduction table.
   - Verdict: HOLD.

**Manuscript.** Every edit went to both masters, except the JAIR-only abstract, Descriptions, and checklist.

- Notation is settled. w\*(B) := w-dagger(B) is the crossing threshold, (w_lo, w_hi] is its grid estimate, and hat-w(B) is the plotted nearest grid point. Keep it this way in any future edit.
- Proposition PI-5 gains a proved running-average result: Kronecker's lemma under the harmonic schedule, plus projection non-expansiveness for Blum's argument.
- The scale-equivariance paragraph was rewritten so the price and the bracket rescale under different conditions.
- The cost-budget mechanism now leads with the measured step and labels the mechanism as an interpretation.
- Caption and Description fixes were made to Figures 1, 4, 15, 17, 18, and 19. The Holm nominal and defined family sizes are now stated, a cross-battery note was added, and the reason for omitting the pymdp-AIF row is given.
- Figures were regenerated at their producers: three price figures via `run_price_of_information.py --replot-figures`, the hero via `build_fig_hero.py`, and the Tileworld comparison via `render_tileworld.py` plus `run_tileworld.fig_agent_comparison`.

**Code.**
- Docstrings in `rho_aif/budget.py`, `experiments/run_cpomdp_baseline.py`, and `experiments/run_tost_sarsop.py` now use the manuscript's calibrated vocabulary.
- The frontier table producer, `experiments/build_budget_frontier_table.py`, gained same-stream columns.

## The one caveat a hostile referee will raise

On the held-out Tiger stream neither the family nor any reference policy in the
envelope's support commits wrongly. Every per-seed reward is 10 minus the number of
observations, so the Tiger gaps measure only extra listening.

On the canonical stream the reference commits wrongly at 0.6 percent (success 0.994).
A wrong commit costs 110 reward units against a correct one, so that rate is worth
about 0.66 of expected reward. In the extreme case, the 0.25 shortfall reverses and
the 0.5 shortfall nearly vanishes. Only Tiger's 0.75 shortfall is robust.

This is disclosed in the frontier section, the JAIR abstract, and both conclusions.
Do not drop that sentence to save words. The auditor independently confirmed it by
placing one wrong commit in each held-out seed in turn.

## Decisions and waivers (do not reopen without new reason)

- **Grok's length cut and moving sections to appendices: waived.** No other referee asked for it, and the moves would break the budget-first narrative. A one-sentence cross-battery note was added instead of a battery-map table.
- **Figure 17 panel b keeps "rho=0".** It matches the paper's agent notation.
- **Gemini's ln Z footnote: waived.** The normalizer qualification is already stated up front (ledger 9.17.48).
- **Three of Sol's optional items: waived.**
  - Seed bootstrap for secondary CIs: those intervals are secondary and labelled episode-level.
  - Lineage manifest: the producer stamps and the README table already carry that mapping.
  - Tuned-weights provenance columns: adding them would need a tuning-battery rerun, and the protocol is stated in the manuscript, checklist, README, and code.
- **JAIR paragraph layout.** Two JAIR paragraphs that carry long file names use a local `{\emergencystretch=3em ...\par}` group rather than a global setting. A global setting reflows floats, and the hero figure has a known float hazard (ledger 9.17.48).
- **LNCS master overfull boxes: accepted.** `paper/full_paper.tex` has 81 overfull boxes against HEAD-before-pass 75, all from unbreakable `\texttt` file names in the long master, which is not the submission file.

## Process lessons from this pass

- **Audits caught 11 defects across four audits.** The audits were batch, theory and notation, full re-audit, and two follow-ups. Each audit report was read in full, not just its summary line, and that rule held. The reports are in `reviews/final_panel_2026-09-28/audit*.md`.
- **One of my own edits overclaimed, and the auditor caught it.** A new Discussion sentence said the random-environment study measures the value of observing. It measures reward-gap near-optimality. The same overclaim was then found and fixed in that study's appendix paragraph.
- **An experiment first ran without writing its CSV.** `run_bracket_stability.py`'s reproduction check matched weights by exact float equality and aborted before writing its CSV. It now keys on 10 significant digits. The per-seed CSV is written before the check, so `--from-per-seed` recovers without rerunning episodes.
- **Some background jobs died.** Jobs launched with `nohup ... &` inside the shell tool died silently. Launch long runs as backgrounded shell commands and smoke-check the log once.
- **Two caveats came from referees, not from the protocol.** The Tiger rare-event caveat came from a referee's second round, and the "every comparison is within one battery" overclaim came from my own new sentence. Keep re-reviewing after fixes.

## Where the record lives

- `reviews/final_panel_2026-09-28/`: the committed review record.
  - Briefs: `REVIEWER_BRIEF.md`, `AUDIT_BRIEF.md`, `AUDIT2_BRIEF.md`, `CITATION_BRIEF.md`.
  - Referee reports: `report_*.md`, with round 2 and 3 in `*_round2.md`.
  - Audit reports: `audit_*.md`, `audit2_report.md`.
  - Citation reports: `citations_slice_{A,B,C}.md`, `citations_crosscheck.md`.
  - Scripts: `apply_batch*.py`, the guarded edit scripts for the first two batches.
- **Not committed (gitignored).** Regenerate them if needed.
  - `reviews/*/manuscript_jair.txt`: regenerate with `pdftotext -layout paper/full_paper_jair.pdf`.
  - `reviews/*/batch_full_jair.diff`: regenerate from `git diff`.
  - `logs/`: run logs. Provenance lives in each CSV's `git_sha` and `generated_utc` stamps.
- `CLAUDE.md` and `AGENTS.md` publication-state blocks carry a "Final four-provider panel (ledger 9.17.50)" bullet.

## What remains (all Pat's, none scientific)

1. **Publish to PyPI.** Run `twine upload` to TestPyPI and then PyPI, which is credential-gated. Until then, the `pip install rho-aif` claim in the README and JAIR checklist is false.
2. **Confirm the attestations.** Confirm the acknowledgments' AI-disclosure author attestation and the contact email (see CLAUDE.md, "Submission-readiness canvass").
3. **Submit.** Paste the submission-form answers from `full_paper_plan.md` 8.9.1 and submit at **jair.org only**. `sub.ifspress.hk` is a hijacked clone.
4. **Version bump (optional).** If a release tag is wanted for the submitted state, bump `pyproject.toml` and `rho_aif/__init__.py` together and record it in `CHANGELOG.md`. This pass changed only docstrings and a figure footer in the package, so no bump was made.

If anyone edits the manuscript again, the standing rules still apply:
- Every change goes to both masters.
- Run `verify_claims.py`.
- Put the batch through an adversarial audit before trusting it.
- Rerun the citation check if the bibliography changes.
