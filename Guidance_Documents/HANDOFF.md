# Handoff: JAIR submission review loop

Written 2026-08-31. Read this first if you are picking up this project cold.
It orients you in five minutes; `full_paper_plan.md` has the full narrative
ledger if you need more depth on any specific round.

## One-paragraph summary

Pat asked for an autonomous review loop: spin up independent expert-reviewer
panels against `paper/full_paper_jair.tex` (and its propagated twin
`paper/full_paper.tex`), fix what they find, verify the fixes against the
actual artifacts, and iterate until every reviewer returns accept or the
remaining findings are genuinely minor. Thirteen rounds have run. The
manuscript has improved substantially and the defect rate per round has
fallen by roughly half, but round 13 did not finish (see below) and the loop
has not yet reached the stop condition. Two more phases Pat asked for, figure
polish and a writing-style pass, have not started.

## Where things stand right now

- **HEAD**: the round-14 commit of 2026-08-31 (rounds 13 and 14 applied;
  `git log` is authoritative). Working tree is clean.
- Both manuscripts compile with **zero LaTeX errors, zero undefined
  references**, and **450/450 tests pass**. This has been true and verified
  after every round since round 3.
- Author certification on file (Pat, this session): the two load-bearing
  contributions, the EFE / rho-POMDP equivalence at w=1 and the Price of
  Information framing of w as the shadow price of a sensing budget, are
  certified novel. Reviewers are told not to re-litigate this. They may still
  flag any specific claim a cited source contradicts.
- **Rounds 13 and 14 are complete (2026-08-31, in-place update).** Round 13's
  9 hand-verified claims and round 14's 8 skeptic-sustained findings (of 12
  raw; 4 refuted) are applied to both masters, rebuilt, tested, and
  committed. Round 14 was the first multi-model panel (GPT 5.6 Sol, Gemini
  3.1 Pro, Grok 4.6, Claude Fable 5, Claude Opus 5) and produced the first
  unqualified accept since round 8 (Grok, editor lens). It also caught round
  13's own nat-conversion fix being inverted — reviewer rounds audit prior
  rounds' fixes, which is an argument for keeping the loop running. Full
  narratives in `full_paper_plan.md` sections 9.17.18-9.17.19.
- **Round 15 is complete (2026-08-31).** Four unqualified accepts (statistics
  twice, editor, decision theory) and one accept-with-minor-revisions whose
  three sustained findings were all disclosure gaps in the RockSample/POMCP
  appendix territory (six deviations not five, missing step caps and rock
  maps, undisclosed POMCP departures) — fixed same day, ledger 9.17.20.
  Round 16 is the active phase and tests whether that last territory is
  clean.

## The methodology, distilled

This took twelve rounds to converge on and is worth preserving rather than
rediscovering:

1. **Panels sample, they don't enumerate.** Five reviewers reading a 70-page
   manuscript will keep finding roughly 8-15 new things per round for a very
   long time, because they're sampling a defect pool rather than covering it.
   The move that broke this was **exhaustive class sweeps**: audit every
   instance of one claim type against its artifact, not five reviewers'
   worth of attention spread thin. Classes swept and closed:
   - Every universal quantifier and completeness claim (217 checked, 58 wrong)
   - Every cross-reference target (184 checked, 23 wrong)
   - Every protocol/provenance claim (148 checked, 16 wrong)
   - Every numeric value in prose (451 checked, 2 wrong — the numeric layer
     is essentially clean)
   - Every figure caption/body description/alt-text (114 checked, 11 wrong)
   - Committed artifacts re-derived against current code (105 checked, 4
     wrong, including a real one: a shadow-price CSV predating a solver fix,
     violating the paper's own Definition PI-3)
   - Every claim about cited prior work, checked by fetching the actual
     source (77 checked, 15 wrong — this is the highest-value class; it
     caught a false novelty claim, see below)

2. **Verify every applied batch, always.** This is the single most important
   discipline and it was learned the hard way. Two audited batches: 19 of 80
   corrections wrong, then 9 of 46 wrong. A large correction batch has its
   own defect rate comparable to what it's fixing. Concretely this means:
   after applying any batch of fixes, run a fresh adversarial pass that
   re-checks each change against its artifact and its neighboring sentences,
   before calling the round done.

3. **The self-inflicted defect rate is real and it compounds.** Across
   rounds 9-12, roughly half of what the *next* panel found was collateral
   damage from the *previous* fix: a duplicated sentence from a non-idempotent
   string replacement, a case split left non-disjoint after a partial edit, a
   dangling anaphor left behind when a sentence was trimmed, a reviewer's
   `suggested_fix` text applied verbatim into the manuscript body instead of
   being read and adapted. `tools/review_pipeline/safe_apply.py` is a guarded
   replacement helper written in response to this: it refuses a replacement
   whose new text already fully appears in the file (catches non-idempotent
   double-application), and it refuses replacement text that pattern-matches
   an instruction rather than prose (catches the leaked-suggested-fix
   failure). **Use it, or something like it, for any future batch apply.**
   It is plain Python, no dependencies beyond the standard library.

4. **The panel construction that works**: five reviewers with distinct
   expertise identities (POMDP planning, active inference, decision theory,
   statistics, senior generalist/editor), each required to verify claims
   against the actual CSVs/code rather than just reading prose, each
   returning `required` (blocks accept) vs `suggestion` (does not) findings
   under explicit accept-means-zero-required-changes semantics. Then an
   adversarial skeptic re-checks every `required` finding independently
   (these have refuted a small number of findings across the rounds, which
   is healthy — it means the skeptics aren't rubber-stamping). Then an AE
   adjudicates and writes a consolidated decision. `tools/review_pipeline/
   panel_template.js` is round 13's actual script (last one authored) and is
   a faithful template: it has the full prompt scaffolding, the JSON schemas
   for structured findings, and the parallel/verify/adjudicate phase
   structure. To run a new round, copy it, update the "Context you may use
   but must not defer to" block to describe what changed since the last
   round (this is important, it stops the panel re-finding fixed things),
   and launch via the `Workflow` tool.

5. **Different model families catch different things.** Round 5 ran on Opus
   5 after rounds 1-4 ran on Fable 5, and it immediately found a defect
   (a mischaracterization of the original RockSample benchmark's cost
   structure) that four consecutive same-family panels had missed. If
   reviewer agents are available on more than one model, rotating matters.

## Round-by-round history (compact)

| Round | Verdict spread | Required findings | Notable |
|---|---|---|---|
| 1-3 | unanimous accept-with-minor-revisions | 30, 21, 21 | initial submission-readiness pass, panel construction established |
| 4 | 5x accept-with-minor-revisions | 6 clusters | first "unqualified accept" bar attempt; found the class-sweep approach was needed |
| 5 | 5x accept-with-minor-revisions | 10 (1 refuted) | first Opus 5 round; caught a defect 4 Fable 5 rounds missed |
| 6 | 5x accept-with-minor-revisions | 15 | a git-traceable stale constant found |
| — | (six class sweeps run here) | 97 violations found, 80 corrections, then 19/80 of those corrections found wrong on audit | this is where the methodology pivoted from panel-only to sweep+panel |
| 7 | 3 reviewers survived (2 lost to machine sleep) | 11 | first citation-verification-against-primary-source findings |
| — | (three more class sweeps: numbers/figures/staleness) | 670 checked, 17 wrong (2.5%) | numeric layer confirmed clean |
| 8 | 1x accept, 4x accept-with-minor-revisions | 10 | **first unqualified accept from any reviewer.** Also caught a genuinely unseeded battery (`run_tileworld.py` partition-sensitivity), reseeded and rerun, which **reversed** a reported finding |
| 8-verify | — | 9 of 46 corrections wrong on audit | includes a knife-edge error in a hypothesis I'd added to Corollary PI-4 |
| 9 | 5x accept-with-minor-revisions | 7 | 3 of 7 were text-duplication artifacts from my own non-idempotent edits (motivated `safe_apply.py`) |
| 10 | 5x accept-with-minor-revisions | 8 | my own round-9 "sixth RockSample deviation" was itself found wrong (a false claim about the original benchmark's sensor) |
| 11 | 5x accept-with-minor-revisions | 7 | found a **third** error in the same RockSample-deviation sentence (rounds 5, 9, 11), plus two real citation misattributions (Araya-Lopez PWLC claim, Boutilier belief-dependent-reward claim) |
| — | (cited-work sweep) | 77 checked, 15 wrong | found the manuscript falsely claiming to generalize Araya-Lopez et al.'s formulation, which already covers it; also found a leaked reviewer suggested_fix in the manuscript body and a mislabeled "Thompson sampling" baseline (it's actually majority-vote, renamed "Posterior-vote") |
| 12 | 5x accept-with-minor-revisions | 7 | the biggest single fix: Section 3.1's formal rho-POMDP definition was action-independent while every downstream use (including Prop 1 itself) needed the action-dependent form — this was collateral damage from withdrawing the false generalization claim in the cited-work sweep |
| 13 | 5x accept-with-minor-revisions | 9 (all survived hand-verification) | verify+AE phases died to spend limit mid-round, completed by hand 2026-08-31 (ledger 9.17.18) |
| 14 | **1x accept (Grok), 4x accept-with-minor-revisions** | 8 sustained, 4 refuted by skeptics | first multi-model panel (GPT/Gemini/Grok/Fable/Opus) + adversarial-skeptic phase; caught round 13's own nat-conversion fix being inverted (ledger 9.17.19) |
| 15 | **4x accept, 1x accept-with-minor-revisions (Opus)** | 3 sustained (all RockSample/POMCP disclosure), 3 refuted | statistics clean across two model families with zero findings; deepest theory verification yet (Prop 2 re-derived by hand); the RockSample deviation sentence produced its fourth-round finding (5, 9, 11, 15) — now six deviations (ledger 9.17.20) |

## Resuming round 13 (RESOLVED 2026-08-31 — kept for the record, do not redo)

The reviewer phase finished; only skeptic-verification and AE-adjudication
failed. The five raw reviewer JSON payloads (unverified, undeduped) are
saved at `tools/review_pipeline/round13_raw_findings_UNVERIFIED.json`. Do
**not** apply these directly. Per the methodology above, each needs to be
independently checked against its cited artifact before touching the
manuscript. Deduped, there are about 9 distinct claims. The three most
likely to be real (spot-checked while writing this handoff, but not yet
fixed):

1. **Dangling anaphor, high confidence.** `full_paper_jair.tex` line ~673
   (Section 7.1, curve collapse) ends "...resolving that discrepancy rather
   than merely narrowing it." No discrepancy is stated anywhere in either
   manuscript (`grep -c discrepanc` returns exactly 1 hit in each file, this
   sentence itself). This is leftover text from a round-10 edit that trimmed
   the sentence's opening half but left the closing clause referring to what
   used to precede it. Same defect, mirrored in `full_paper.tex` line ~627.
2. **Same-defect-different-location repeat.** The Conclusion (line ~901)
   still says "on Tiger, Diagnosis, and Bandit... further increases buy only
   marginal accuracy at substantial reward cost." Round 12 fixed the
   near-identical claim in the Discussion (line ~836) to exclude Bandit,
   where `results/results_pareto_sweep.csv` shows w=5 buys +9.84pp accuracy
   for only -0.41 reward, not a "substantial cost." The Conclusion has the
   same overclaim and was missed because it's a different location.
3. **Internal contradiction in the POMCP appendix.** Line ~1591 says
   "POMCP's random rollout policy cannot evaluate which test to run," while
   line ~1559 of the same appendix states the rollout is semi-informed and
   explicitly not random. Likely correct as reported; verify the exact
   quotes are still live (line numbers drift between commits) before fixing.

To actually resume: either (a) wait for the spend limit reset (Sept 2,
midnight America/Denver, per the error text — this is an unvalidated
third-party string, treat as informational not authoritative) and use
`Workflow({scriptPath: '<path-to-panel_template.js>', resumeFromRunId:
'wf_8ccad6af-bfa'})` to resume the verify+AE phases from cache (the five
reviewer results will replay instantly, only verify+AE re-run), or (b) if
that run ID is no longer resumable, take the 9 deduped claims from the raw
findings file, verify each by hand against the named artifact, apply what
survives with `safe_apply.py`, rebuild both PDFs, run `pytest tests/ -q`,
then launch a fresh round 14 as verification.

## Phase 2: figure polish pass (not started)

Pat asked for this after the accept-loop converges, but the audit was
already run so it's here for whenever you get to it. A full visual/legibility
audit (as-rendered, not correctness) of all 19 figures is saved at
`tools/review_pipeline/figure_audit_2026-08-30.json`: **111 issues, 23
blocking, 63 notable, 25 polish.**

The single highest-leverage fix is systemic and already diagnosed: most
figures are authored at a matplotlib canvas width far larger than the box
they're printed into (`\includegraphics[width=...]`), so `figstyle.py`'s
9.5pt/8.5pt rcParams get silently shrunk to 3-6pt on the actual page. The
JAIR text width is 452.295pt = 6.26in. Affected producers and their current
oversized canvases: `run_price_of_information.py` (figsize up to
(10.5, 6.0)), `run_visualizations.py` (up to (14, 4.5)), `run_tileworld.py`
((11.5, 3.4)), `run_pareto.py`, `run_showcase.py`, `run_distractor_diagnosis.py`.
Fix: author each figure at (or very close to) its actual printed width times
the include fraction (e.g. a figure included at `0.78\linewidth` should be
authored at `0.78 * 6.26 ≈ 4.88in` wide), not a wide canvas scaled down.

One genuine production error, not just a sizing issue: `fig_efe_trajectory`
panels (a) "Short episode" and (b) "Medium episode" show the **same episode**
(both 4 steps, pixel-identical apart from antialiasing) — the episode
selection logic in `run_showcase.py` picks by list index into a
length-sorted list and two indices collided. Needs distinct-length selection.

Other blocking items worth reading directly from the JSON before starting:
`fig_tileworld_comparison` has 756 illegible per-cell numbers and no
colorbar/legend at all; `price_shadow_curves` draws 6 of 25 crossing brackets
detached from their own bracket with no visual cue; `price_prop2_jumps`'s
onset bracket, the entire point of the figure, is sub-pixel wide (0.74% of
the axis). Full list and fixes-in-progress-notes are in the JSON's
`blocking` array.

## Phase 3: writing-clarity pass (not started)

Pat's exact instructions, worth quoting verbatim since they're precise:
keep language academic and technical where required but otherwise as simple
and straightforward as possible; vary sentence length; avoid colons except
where necessary; avoid semicolons except where necessary; avoid em dashes
except where necessary; make sure the manuscript flows together elegantly
and the thesis is clearly and cleanly supported throughout.

This should run **after** the accept-loop and figure pass are done, not
before or during, because rewriting prose mid-loop invalidates reviewers'
line-number references and risks reintroducing exactly the kind of drift the
class sweeps just spent thirteen rounds eliminating. A style/mechanics sweep
similar to the earlier "prose colon / semicolon / em dash" check (done once
already, see `git log --grep="em dash"` for precedent) plus a holistic
read-for-flow pass is the right shape. Verify the applied batch afterward,
same as every other phase.

## Two blocking manual steps (Pat only, unrelated to the review loop)

From `CLAUDE.md`, unchanged and still outstanding:
1. `twine upload` to TestPyPI then PyPI (`rho-aif` name verified unclaimed).
   Confirm/move local `v1.0.0` tag, push tags. The `pip install rho-aif`
   claim in the README and JAIR checklist is false until this lands.
2. (IWAI camera-ready and JAIR template issues are both already resolved
   per `CLAUDE.md`'s Publication state block — only the PyPI step remains.)

## File map

- `paper/full_paper_jair.tex`, `paper/full_paper.tex` — the two live
  manuscripts. Every prose fix lands in both identically (propagation rule).
  Frozen snapshots (`paper.tex`, `paper_arxiv.tex`, `paper_iwai2026*.tex`)
  are never touched.
- `Guidance_Documents/full_paper_plan.md` — the full narrative ledger,
  section 9.17.x. Note: **rounds 8 through 12's individual narratives were
  not backfilled into this ledger** (the commit messages on `4d1b609`,
  `8483a8a`, `17473dd`, `926ff68`, `109d407`, `23c740a`, `d6fb0f5` are the
  authoritative detailed record for that stretch; `git log <commit> -1`
  reads like a ledger entry). If you want the ledger fully current, that
  backfill is a reasonable next task, low urgency.
- `tools/review_pipeline/` — this handoff's durable artifacts:
  `safe_apply.py` (guarded batch-edit helper), `panel_template.js` (round-13
  panel script, reusable as a template), `round13_raw_findings_UNVERIFIED.json`,
  `figure_audit_2026-08-30.json`.
- `tests/` — 450 tests, run with `python -m pytest tests/ -q` from repo root
  inside `.venv`.
- Build: `pdflatex → biber → pdflatex ×2` for the JAIR file (TinyTeX at
  `~/Library/TinyTeX/bin/universal-darwin`), `tectonic paper/full_paper.tex`
  for the LNCS master.

## Recommended next action

1. Verify the three high-confidence round-13 claims above by hand, apply
   with `safe_apply.py`, rebuild, test, commit.
2. Either resume round 13's verify+AE phase (if the run is still resumable)
   or take the rest of the deduped raw findings through manual verification.
3. Launch round 14 as a fresh check. If it returns a genuinely thin set of
   findings (no wrong numbers, no contradicted claims, no misdescribed
   sources, nothing but wording/formatting suggestions), that is the stop
   condition Pat described. Say so plainly and move to Phase 2.
4. Figure polish pass using the existing audit.
5. Writing-clarity pass per Pat's style rules, verified afterward like every
   other batch.
