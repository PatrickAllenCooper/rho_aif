# Hand-edit notes before JAIR submission

Written 2026-09-05 after the confirmation round (ledger `full_paper_plan.md`
9.17.27). This file collects everything left for Pat's hand-edit in one
committed place. The earlier pointer in `HANDOFF.md` went to a session
scratchpad file that no longer exists, which is why this lives in the repo.
Line numbers are JAIR-master lines at commit `3a96064` and may drift by a
line or two after edits. Every prose edit goes to both masters
(`paper/full_paper_jair.tex` and `paper/full_paper.tex`). `\Description`
and checklist edits go to the JAIR master only.

## Where the manuscript stands

- Round 18 (2026-08-31) returned five unqualified accepts. Two batches then
  landed unreviewed (figure pass, writing pass). The final review
  (2026-09-04, 9.17.26) found 22 defects in those batches and 17 required
  changes, all applied. The confirmation round (2026-09-05, 9.17.27) then
  audited that batch (43 changes, 2 defects, both fixed in `67e673c`) and
  ran a fresh five-reviewer panel: four unqualified accepts and one
  accept-with-minor-revisions (POMDP planning). The AE consolidated to five
  required changes, all applied in `5e955f6` and re-derived from the
  artifacts before applying. The batch audit of `5e955f6` found two more
  (fixed in `53a55d6`), six skeptics cleared that fix, and a completeness
  critic over the whole batch found the staircase figures drawing grid-top
  brackets as open when Definition PI-3 closes them at 100 (fixed at the
  producer, figures regenerated, `bff4155`). All recorded in 9.17.27.
- Both masters compile with zero errors, zero undefined references, zero
  float warnings. Tests 455/455.
- Nothing below is required for acceptance by any reviewer or the AE. Each
  item is a precision or clarity improvement a referee might raise.

## A. Non-blocking suggestions from the confirmation round (AE, 22 items)

`[checked]` means the AE verified the item personally. The rest were
reviewer-verified and passed through.

1. `[checked]` Proposition 1 assumption (iv) or the last sentence of its
   proof. Add "under a common tie-breaking rule". Raised independently by two
   reviewers. `efe.py` and `planning_infogain.py` share a lower-index
   tie-break and the Pareto caption already says so.
2. `[checked]` Line 183, the Champion et al. sentence. Rephrase so the
   recursion reads as this article's sophisticated-inference extension rather
   than part of Champion's taxonomy, for example "this is the
   information-gain-plus-pragmatic-value formulation, which we evaluate
   recursively over belief trajectories following sophisticated inference".
   Same item as B.7.
3. `[checked]` Line 115. $Q(\pi) \propto \exp(-\mathcal{G}(\pi))$ drops the
   precision the manuscript later calls $\kappa$. "takes a softmax form in
   $-\mathcal{G}(\pi)$" suffices.
4. Example ex:destructive and Remark rem:transition-aware (about lines 281 to
   292). One clause tying "by construction" to the article's
   observe-then-transition timing convention.
5. Abstract line 72 and line 87. "exactly scale equivariant for the
   implemented receding-horizon agent" holds under the proposition's
   tie-break assumption while Section 4.2 discloses the 1e-12 epsilon.
   Optional qualifier, the body already carries the caveat.
6. Corollary PI-4 (lines 402 to 408). State the population step
   $U(w) = \mathbb{1}[w > w_{\mathrm{thresh}}]$ and drop "the stated crossing
   bracket" from the proof. Overlaps B.12.
7. `[checked]` Lines 72, 87 and 93. "stationary convergence guarantee" could
   carry "for its projected form", which Section 4.5 already discloses. Same
   item as B.11.
8. `[checked]` Line 571. "(within 1 SE at both scales" should read "within
   one standard error of the difference at both scales" to match the
   Discussion. At 6x6 the 1.7pp gap exceeds each agent's own SE (1.0pp and
   1.5pp) but sits inside the SE of the difference (1.8pp).
9. Line 819. "roughly a 3-SE gap" computes to 3.4 to 3.5 SEs of the
   difference.
10. Line 766. The Tiger TOST row is degenerate (identical per-seed means,
    difference 0.0). One clause saying the two policies coincide episode by
    episode there.
11. `[checked]` Line 886. "every transferred success-tuned weight costs
    reward relative to $w{=}1$" is literally true, but Bandit $w{=}20$ and
    Testbed $w{=}10$ are native (`results_transfer.csv`, `is_native_succ`).
    "every success-tuned weight, native or transferred" is the complete
    statement.
12. Table tab:transfer row labels (about lines 857 to 861). Reward-tuned
    weights are labeled as points while Section 5.2 reports tied brackets.
    Label rows as inside the bracket.
13. `[checked]` Line 1452. "the worst setting tested at both" is a
    point-estimate ranking. At 2,048 simulations H=10 is lowest (12.813
    against 14.002, 13.25, 12.973) but no H=10 comparison is significant
    there. "lowest point estimate at both budgets, significantly so only at
    16,384 simulations".
14. `[checked]` Line 1456, first sentence. "$+15.6$ at 530 ms, still short
    of EFE at 1.76 ms" compares the 5-seed by 100-episode diagnostic with the
    10-seed by 500-episode main battery with no test. Add "a cross-battery
    point comparison".
15. `[checked]` Figures fig:interleaved and fig:stairs (lines 724 to 726 and
    737 to 739) and the `slack budget` legend label in `plot_shadow_price_curves`
    (`experiments/run_price_of_information.py`). The
    legend entry "slack budget" marks any budget whose $|U-B|$ grid argmin
    lies below the crossing bracket, including budgets where the constraint
    binds. Rename or define it in one clause so it is not read as constraint
    slack.
    Note that the same figures' grid-top brackets were redrawn as capped
    bars in `bff4155`, so the legend now has exactly two glyph entries.
16. Captions of fig:sweep and fig:obs_scaling. A reviewer reports the
    episode count reads as 500 without saying 100 per seed times 5 seeds.
    The AE's grep did not match the reviewer's wording, so locate the two
    captions and confirm before editing.
17. `[checked]` Spelling and quoted-checklist policy. "generalised free
    energy" at lines 115 and 183 is the cited paper's own term (Parr and
    Friston 2019) and was left deliberately. Line 1639 carries a semicolon
    and line 1659 "optimisation" inside reproduced JAIR checklist wording.
    Decide explicitly whether quoted checklist text is exempt.
18. `[checked]` Line 698, Description of fig:dualmultiseed. "Top row." then
    "Bottom row:" should use one separator. Overlaps B.18.
19. CLOSED 2026-09-05. `results_price_of_information_summary.json` key
    `verdict.shadow_staircases` was a fossil string contradicting Section 6.6
    and `results_price_usage_curves.csv`. Fixed at the producer (the verdict
    is now a pure function of the CSV, refreshed on every run, with a
    `--refresh-summary` flag and a regression test that the committed JSON
    agrees with the committed CSV).
20. Table-internal italics at lines 1162 and 1291 and
    `paper/tables/horizon_map.tex` regime headers. Structural sub-headings,
    leave or switch to plain text if the house rule is read literally.
21. `[checked]` Line 1594 opening sentence "To disentangle EFE's information
    valuation from the planning mechanism" reads more accurately as "from
    exact enumeration", since the sampled tree is what replaces the exact
    recursion.
22. Optional experiment. If you prefer data over hedging for the MCTS-EFE
    attribution (required change 4 of 9.17.27), a canonical 5-seed ablation
    (MCTS-EFE with mean backup, and MCTS-EFE with the in-tree information
    reward removed) added to `results_mcts_efe.csv` would let the Discussion
    make a positive attribution rather than a hedged one. Not required.

## B. Non-blocking suggestions from the final review (AE, 21 items)

Status as of 2026-09-05. Items marked closed need nothing.

1. Line 358 "is a \emph{calibration} of this policy family" is contrastive
   emphasis, not a definitional first use ("calibration" is an ordinary word
   at 89 and 836). Under the house rule the italics should go. Two reviewers
   flagged it.
2. RS[11,11] POMCP diagnostic (JAIR 1454 and 596, LNCS 1738). "The deeper
   tree does see the collection tour" reads against
   `results_rocksample_pomcp_horizon_11x11.csv`, where `mean_tree_depth`
   only moves from 4.9 to 6.3 plies as H goes 10 to 40 while `mean_checks`
   goes 1.6 to 143.9. Say "the longer-horizon search (its rollouts, since
   the tree itself stays near six plies deep)" and consider attributing the
   H=40 behavior to check-spamming under mean backup with thin sampling at
   2,048 simulations. The quoted numbers are all correct. This is the most
   substantive open item.
3. Definition PI-3 (362). Name the endpoint that receives probability q.
   The formula holds only if q is the probability of running the w_hi
   policy.
4. Section cpomdp (775). "supported points of the achievable region"
   overstates a point-based approximate solver. "achievable (near-supported)
   points" is accurate, and `results_cpomdp_frontier.csv` shows the symptom
   (Diagnosis usage rises from 9.707 at lambda=0 to 9.817 at lambda=0.107).
   The lower-bound conclusion is unaffected.
5. Equation (2) at 148. The first underbrace includes the leading minus
   sign, so the quantity labeled "Pragmatic value" is its negative. Move the
   minus outside the brace or relabel.
6. Line 115. "pragmatic value (divergence from preferred observations)"
   glosses the risk term. Under the paper's own Eq. (2) pragmatic value is
   the expected log preference. Write "(expected log preference over
   outcomes)".
7. Line 183. Split the Champion sentence so the recursion is attributed to
   sophisticated inference rather than to Champion's taxonomy. Same as A.2.
8. Proposition 1 (177). "not by stipulation but because the episode
   terminates" describes a construction of the observe-then-commit class.
   "by construction of the observe-then-commit class, in which" is more
   accurate. Also state, in the proposition or Appendix A, that both
   recursions restrict depth-H nodes to commit actions, which the
   implementation enforces (`efe.py` returns the best commit EFE at the
   horizon).
9. Line 262. The reason exploitation actions carry rho=0 is a modeling
   choice (the sample outcome emits no informative observation and a
   collected rock plays no further role), not that they are
   "reward-bearing". Say so directly rather than "exactly as for commit
   actions".
10. Line 449. One sentence noting that Kouw's information-floor multiplier
    is the Bethe-side counterpart of the paper's own information-floor
    reading at 358 would position the contribution more sharply.
11. Lines 87 and 93. "stationary convergence guaranteed" could carry "for
    the projected update", matching Section 4.5 and the checklist.
    Optionally note at 425 that `DualWeightAgent` already exposes
    `max_weight`, so the projected variant is available in the released
    code. Same as A.7.
12. Notation. Proposition nearopt writes $w^*_{\mathrm{thresh}}$, Corollary
    PI-4 and Section prop2exp write $w_{\mathrm{thresh}}$. Pick one. In the
    corollary's proof, "giving the stated crossing bracket" refers to a
    bracket the statement does not name. Overlaps A.6.
13. Line 356. "the Planning+IG-optimal policy at weight $w$" reads as a
    global maximizer. "the receding-horizon Planning+IG policy at weight
    $w$" matches Section pi2.
14. CLOSED, no change required. Line 387 / LNCS 347. The AE and the skeptic
    agree the current direction (non-monotonicity is the reason for a
    bracket rather than a level set) is the paper's consistent position. If
    you want a smoother sentence, "Because $U$ may be a non-monotone step
    function, we define $w^*(B)$ as a bracket rather than as a level set,
    which could be empty or multi-valued" covers both cases.
15. Descriptions at 568 and 1117 quote belief values (0.98, 0.47, 0.73) the
    regenerated heatmaps no longer print. Either drop the decimals or say
    they are read from the episode trace.
16. Line 701. "six of the ten seeds" is the right count, but seed 110 is a
    tie at 0.20 to display precision and three seeds favor decay. Say so.
17. Line 836. "the reward stays flat between $w{=}1$ and that point" is
    loose. The Pareto CSV has reward flat through w=20 and dropping at w=50
    itself.
18. Descriptions at 652, 698 and 1138 use prose colons ("Left:", "Bottom
    row:"). Cosmetic, but easy to align with the house rule. Overlaps A.18.
19. `results_tiger.csv` and `results_bandit.csv` carry mixed `git_sha`
    stamps across rows. Numbers are consistent, but one stamp per file is
    easier to defend under the checklist's regeneration claim. A repo
    artifact, not manuscript text.
20. CLOSED, no change required. fig_tileworld_belief (1114) and
    fig_belief_heatmap (1122) are 0.78-authored and included at \linewidth.
    They fit their pages (no float warning) and print legibly. If you want
    uniform type size across the appendix figures, re-author all four at
    figsize(1.0, ...) rather than shrinking these two.
21. Optional. The mixed British/American residue in producer docstrings
    (`run_reward_scaling.py` "scale-normalised") is outside the manuscript.

## C. How to hand-edit safely (both AEs, merged)

- Work from the artifacts, not from memory of the figures or the numbers.
  Open each PNG beside its `\Description` when touching one. When a hand
  edit touches any number, re-check it against the CSV named in the
  table's producer stamp rather than against the surrounding prose.
- Apply prose fixes to both masters and `\Description` fixes to the JAIR
  master only, then grep both files for each corrected phrase to confirm
  parity.
- Give every paragraph you touch one cold read looking for "that", "this",
  "there" and "it" whose antecedent is more than a sentence away. That is
  how the dangling anaphor at line 183 arose in the previous fix batch.
- Rebuild with pdflatex, biber, pdflatex twice (TinyTeX at
  `~/Library/TinyTeX/bin/universal-darwin`), then run
  `grep -a "Float too large" paper/full_paper_jair.log` (plain grep is
  silent on this log). Rebuild the LNCS master with tectonic.
- Grep the live files for em dashes, prose semicolons, "exact", "validate"
  and "recovers". Rerun the British-spelling grep on both masters and leave
  "generalised free energy" alone.
- Run the test suite before committing anything that touches code. After
  running ANY producer, diff `results/` against HEAD before staging.
  `run_price_of_information.py --replot` is not figure-only. Figure-only
  rebuilds are `--replot-figures`, and summary-only refreshes are
  `--refresh-summary`.
- Record dispositions in `full_paper_plan.md` section 9.17 and mirror in
  `research_plan.md`. Correct errors in guidance documents in place with
  dated notes, never by deletion.

## D. Pat-only items, credential-gated or destructive

- `twine upload` to TestPyPI then PyPI (`rho-aif` verified unclaimed),
  confirm or move the local `v1.0.0` tag, push tags. The
  `pip install rho-aif` claim in the README and the JAIR checklist is false
  until this lands.
- Decide the git-trailer question. 135 of 231 public-repo commits carry
  Co-Authored-By trailers naming AI models. Rewriting history is
  destructive and orphans every `git_sha` provenance stamp in the results
  CSVs. Alternatives are a fresh-history public mirror or leaving it.
- Optional experiment A.22 (MCTS-EFE ablation) if you want a positive
  attribution in the Discussion.
