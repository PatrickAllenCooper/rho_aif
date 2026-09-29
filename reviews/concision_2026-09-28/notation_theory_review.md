# Final mathematics and notation audit — 2026-09-28

**Verdict: ACCEPT. No remaining required mathematics or notation corrections identified.**

This is the dedicated follow-up to `final_theory_review.md`. The earlier scientific-preservation ACCEPT stands. This follow-up checks the assembled main mathematical sections and their proof counterparts in both masters, and verifies the rendered equations affected by the notation corrections. I authored the theory concision fragments and the guarded correction module, so this is a verification of those changes rather than an independent authorship claim. The other agents reviewed the broader scientific and empirical changes independently.

## Source consistency

The main chunk from Methodology to Experiments is byte-identical between the two masters, as are Appendix A's equivalence proof and the moved detailed-theory appendix. I re-read the formal statements against their proofs, checking objective signs, value versus action-value notation, information units, finite depth and terminal actions, scale identities, threshold versus bracket notation, mixture randomization, and the controller's assumptions.

The following checks passed.

- `sec:methodology` defines the belief simplex, predictive and posterior distributions, preference parameters, and the entropy/horizon distinction. `subsec:formal_rho_equiv` defines expected immediate reward and the optimal belief-state value before using them in the formal recursion.
- `prop:equivalence` and `app:proof` consistently use depth `d`, successor depth `d+1`, commit-only actions at `d=H`, and no commit continuation. The proof cites the commit equation for the commit branch. Both recursions share the deterministic tie-breaking rule. The softmax discussion states concentration on minimizing policies and does not equate a deterministic tie choice with the limiting distribution over tied minimizers.
- Reward-based recursion, normalized preference scoring, the log-score exact case, and the empirical bit convention remain distinct. Weight units are reward per unit of information, while the informativeness ratio has reciprocal units. No sign or base conversion changed.
- `ex:destructive` states its value difference in reward units and no longer identifies its symmetric rewards with the strict-asymmetry hypotheses of `prop:nearopt`. Transition-aware and state-preserving posteriors remain distinct. The diagnostic is not asserted to be an additive correction or an equivalence test for state preservation.
- `def:pi3` distinguishes a level set, crossing threshold, finite-grid bracket, and endpoint mixture. Closed-enclosure containment retains its no-missed-crossing condition. The selected mixture is not equated with every attainable mixture or with a cap-constrained reward optimum.
- `prop:pi1` retains separate count and cost scaling identities. `prop:pi2` is restricted to exact maximizers over a fixed plan set. The receding-horizon distinction and nonmonotone usage caveat remain explicit.
- `cor:pi4` and its proof consistently use the strict `w > w_thresh` observation rule under commit-favoring ties. The indicator is explicitly defined and now uses a supported bold-one glyph in all three occurrences.
- `prop:pi5` and its appendix proof use the same sign of the budget error, interior crossing, projection interval, bounded martingale noise, and separation condition. The harmonic-schedule running-average claim is separate from pointwise expected-usage convergence. Neither the reset heuristic nor the constant-step library default is included in the guarantee.
- The appendix's reward-relevance information gain now averages the conditional KL divergence over prospective observations with the belief and action explicitly conditioned. The score and numerical-tolerance conventions introduced by the companion notation module are dimensionally consistent.

## Guarded corrections

`theory_notation_fixes.py` records the exact source replacements and rejects missing or nonunique anchors. It is applied by assembly to both masters, after the independent appendix corrections and before layout adjustments. The source fragments and frozen legacy files are not modified by this module. The raw-fragment preservation audit therefore continues to compare the original concision moves with the baseline, while this module records the separately approved notation amendments.

The amendments clarify definitions and indexing, add the common tie rule to the equivalence assumptions, correct the associated proof pointer and depth arguments, distinguish the softmax limit from deterministic tie resolution, replace unsupported indicator glyphs, and repair the destructive example's units and parenthetical reference. They introduce no new numerical result or experiment.

## Rendered verification

I visually inspected JAIR PDF pages 7, 15, and 40, and LNCS PDF pages 8, 9, 20, and 54 at 105 dpi. These cover the EFE/Bellman recursions, full equivalence statement, normalizer and units discussion, comparative statics and onset indicator, and the complete equivalence proof. The six pages checked before the last parenthetical deletion were rendered again from the final PDFs and are pixel-identical to the inspected images. The continued LNCS statement and units on page 9 were inspected from the final build directly.

The equations have visible subscripts, expectation operators, braces, signs, and supported indicator glyphs. No clipping or overlap was found. The final build logs `/tmp/rho_final_jair2.log` and `/tmp/rho_final_lncs.log` contain no overfull, undefined-reference, multiply-defined-label, or missing-character diagnostics. Existing class and underfull-box messages do not obscure the checked mathematics.

## Reviewed artifacts

SHA-256 values of the final rebuilt artifacts reviewed here:

- `paper/full_paper_jair.tex`: `7d68bf1679830172b0075be57bd7bbcc3f2c0c8b4b9082de4ff67aaf8f4a19f8`
- `paper/full_paper.tex`: `53262fbeaddab80f9d70d87df81595917c76e8cbfa363bedce5fd3c654293b9b`
- `paper/full_paper_jair.pdf`: `27b9dad5fe769a7ccfb6e66b009bb00847a1b98a58eebeb29be07f0aab68e54e`
- `paper/full_paper.pdf`: `7fcfb7ed52e96a8b5300182762203957599658fd0b73caff30b2a03922eaf6e5`
