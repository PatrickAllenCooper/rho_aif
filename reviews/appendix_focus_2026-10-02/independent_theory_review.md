# Independent theory and editorial review

**Verdict: ACCEPT. No required revision remains on the reviewed sources.** This is an independent internal assessment of correctness, sufficiency and clarity after the claim-focused reduction, not a guarantee of a JAIR editorial decision.

I read the complete JAIR manuscript, including the main argument, scientific appendices and checklist, and checked the twin LNCS text for propagation. I read the repository instructions and the current guidance ledger. I did not inherit the previous review verdicts. The exact initial and final reviewed source/PDF hashes, preservation checks and visual-review pages are recorded in `independent_theory_source_snapshot.json`.

Final reviewed source hashes:

- `paper/full_paper_jair.tex`: `5efeacb8ad298239224d00ac2f8b8b63a36c0c43c8c668d47a770a9a63b8a1d6`
- `paper/full_paper.tex`: `5aa416969a7c353fb7df686ab637ac5f77ba757adfa418ce20b811bb97872f91`
- `paper/full_paper_jair.pdf`: `2d3647daa3399aaa318988f2e2f250b3ea4e55167a069212d7b753f16c202775`
- `paper/full_paper.pdf`: `48db18915800963ab551db860b3ca54f89d49711fb9f3ab4142eb57fae159666`

## Theory and self-containment

The theory survives the reduction. All six `proof` environments are byte-identical to the frozen `2026-10-02_pre_claim_focused_appendices` baseline in both masters. The separate controller argument, from the definition of the filtration through its convergence and running-average conclusions, is also byte-identical. The complete public-sensor protocol is byte-identical. These checks supplement an actual reading of the statements and arguments rather than substituting for it.

The EFE equivalence is appropriately conditional. The reader is told which reward-based recursion is being negated, why terminal actions carry no continuation, how the finite-horizon induction starts, and why common deterministic tie-breaking gives policy identity. The normalized-preference caveat and bit/nat conversion remain explicit. The paper does not promote this algebraic equivalence into a reward-optimality result.

The factored extension keeps its important boundary: sensing and navigation preserve the hidden component, rewards are not observations, and arbitrary exploitation transitions are outside the proposition. The destructive-sensing example supplies the actual posterior calculation and realized-return failure. The diagnostic is expressly not an additive correction or a decision-error bound. Nothing removed from the surrounding discussion is needed to verify these statements.

The two-state threshold proof is sufficient. It derives the first observation's value difference and the confirming/disconfirming second-observation posteriors. The latter calculation explains why the expected optimal commit reward does not improve after the second observation in this symmetric setting. The horizon restriction, information units, perfect-sensing exclusion in Part (b), and prohibition on extrapolating the interval to longer episodes remain. Removing heuristic numerical extrapolations and the broad random-environment map improves the connection between the theorem and the claims actually made.

The operational price construction distinguishes the level set, final crossing, finite-grid enclosure and randomized endpoint policy. Its straddling and no-missed-crossing conditions are visible. The information-floor observation and the comparative-statics proof are confined to exact maximizers over a fixed class, while the implemented receding-horizon family is explicitly distinguished. Scale equivariance retains the assumptions on all pragmatic quantities and tie tolerance.

The controller proof is complete for its stated scalar setting. Projection gives the drift inequality, the compensated squared error is a nonnegative supermartingale, the sign and separation conditions rule out a nonzero error limit, and the interior limit makes projection eventually inactive. Kronecker's lemma then supplies the average-usage conclusion for the stated harmonic schedule. The manuscript consistently excludes the library's constant-step default, reset heuristic, arbitrary nonmonotone curves and nonstationary shift experiment from that theorem. Gap-budget weight convergence is not confused with convergence of instantaneous expected usage.

## Required findings and their verified disposition

My first whole-paper read found four small but real defects caused by retaining promises after cuts. They would have warranted MINOR revisions on the initial source. All are now fixed:

1. The budget-results roadmap promised additional onset and operating-point checks at the section's end, where they no longer appeared. The stale sentence is removed.
2. The interleaved-results paragraph referred to a plotted lowest RockSample target after removal of that plot. The orphaned sentence is removed without losing the retained nonmonotonicity result.
3. The main RockSample table caption promised complete per-instance step/check counts in an appendix that now provides selected diagnostics. Both the producer and generated caption now point to the committed per-instance CSVs.
4. The held-out calibration paragraph pointed to a main section for its exact 16-point grid and horizons, but that section no longer supplied them. The retained protocol now states zero plus 15 log-spaced weights from 0.001 to 100 and Tiger/Diagnosis/Bandit horizons 6/3/2. I checked this recipe against `make_log_w_grid`, `run_budget_frontier.py` and the benchmark configurations. The main pointer targets the repaired subsection.

I also read the centrally applied repairs that narrow the RockSample diagnostic non-rejection to its three deeper high-budget configurations, restore the frozen POMCP configuration and tuning-artifact pointer, and replace the overly strong cap-slack claim by the claim that the cap does not lower maximum sampled reference reward. Their final wording is coherent with the paper's theory and comparison scope. The empirical reviewer owns the detailed numerical audit.

No further unsupported promise, missing mathematical dependency or required theoretical correction was found in the final sources.

## Checklist, paired manuscripts and scope

All 26 enumerated checklist questions and their Yes/Partially verdicts are unchanged from the baseline, including all three Partially answers. The explanatory text still acknowledges incomplete episode-level simulation archives, information units stated in surrounding text, and the restricted controller proof. Its seeding exceptions and conditional sensor bootstrap remain explicit. Removing archive descriptions of omitted experiments does not misrepresent the retained paper's scope. The full sensor protocol retains failures, fitted-model conditioning, calibration reselection, non-independent laboratory-exposure caveats and the distinction between recorded access and physical sensing.

The scientific appendices are byte-identical between the masters. The main-text differences are presentation-specific: hero filename, the JAIR checklist pointer, and the sensor figure's JAIR accessibility description. The statements and scientific interpretation agree.

## Clarity, length and remaining material

The reduction is substantive rather than typographic. The JAIR build has 52 pages. Scientific appendix material occupies pages 35 through 49, inclusive, with references also on page 35 and the checklist beginning on page 49. Thus 15 occupied pages is a conservative physical-page count, not 15 full pages of scientific appendix text. That is a reasonable near-benchmark compromise against the supplied one-volume conditional mean of 11.29 pages and median of 13, especially compared with the frozen 42-page appendix. The benchmark is descriptive and does not require an exact page target.

The retained material is mostly doing necessary work: formal proofs, the destructive boundary case, unit sensitivity, adverse task/model controls, solver limitations, exact protocols and reference sensitivity. The shorter paragraphs generally explain one point at a time. They do not achieve the saving by turning the old tables into long numerical catalogs. The public-sensor protocol is the longest concentrated methods passage, and its detail is justified by the new study and its conditional inference.

There is no remaining multi-page block that I would call obviously dispensable while preserving the current main claims. Further substantial cuts would require deliberately reducing those claims and removing entire comparison branches, for example the Navigation/discount/model-sensitivity discussion, rather than merely condensing their evidence. Tiny redundancies remain, such as some reminders about objective scope and the unused efficiency shorthand in the two-state proposition, but these are optional copy-edit opportunities and do not justify another broad reduction pass. Preserving the current clarity and proof scope is preferable to forcing the appendix to exactly 13 pages.

## Rendered review and limits of this assessment

I rendered and inspected the final JAIR pages 35, 41-44, 46 and 49-52, covering the equivalence proof, threshold proposition and proof, destructive example, state-preservation argument, onset proof, controller proof, restored usage-grid description and checklist. The equations, text and schematic are legible, without clipping or overlap. I also inspected LNCS pages 54-55 and 58. Its ordinary float placement interrupts the threshold proposition across pages 54-55, but all content is readable and the issue is nonblocking. No font or spacing reduction is needed.

The theory is bounded and substantially elementary, and the empirical comparisons retain known limitations of small seed counts, fitted reference envelopes and solver configurations. The manuscript states those limitations candidly. My ACCEPT is based on that bounded contribution and the now-sufficient supporting text. It does not certify every empirical scalar independently, future reproducibility on other machines, personal author attestations, or an actual journal outcome.

## Final source freeze confirmation

On 2026-10-02 at 19:58 UTC, I independently compared the final sources with the full prior text in `pre_whitespace_freeze.json`. I first verified that this stored text hashes to the exact sources reviewed above. The only changes are removal of one trailing space on each of JAIR lines 516 and 518 and LNCS lines 482 and 484. Line counts and all non-whitespace content are unchanged. No scientific wording, mathematics, protocol or claim changed.

**Final verdict remains ACCEPT, with no required revision remaining**, on these final source hashes:

- JAIR: `22bda90c6403a2d54bf91aef3b87b9071d1e6683ddd69b79e39c00204e113a6d`
- LNCS: `58034a6fd6d4505ca346ebf8966995d773b7d8513f2e572afe65bae20f241d08`

The independently inspected PDF hashes recorded above remain the evidence for visual review. This source-only confirmation does not substitute newly rebuilt PDF hashes or claim another visual inspection. The exact comparison is appended to `independent_theory_source_snapshot.json`. The root reports 541 passing tests and a matching-text isolated 17-file Overleaf build; those additional checks are not represented as independently rerun in this theory review.
