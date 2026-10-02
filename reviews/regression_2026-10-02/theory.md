# Retrospective theory-preservation audit

Review date: 2026-10-02. Reviewed baseline: `7e665305` (the completed writing/figure pass). This is an independent check against the actual current sources, mathematical arguments, relevant code, dated legacy manuscript and correction ledger. Prior reviewer ACCEPT decisions were not treated as evidence.

Source fingerprints at inspection:

- JAIR `paper/full_paper_jair.tex`: `9cafe752f6640fc13236667ee57619a8e0628d7e4167ace3f9497e2947c34119`.
- LNCS `paper/full_paper.tex`: `bd6c34d232503a12919927b634fa942bcf1bba279aaf2353f8eb0d0e0a47cd21`.

Line references below are to this baseline. Subsequent repairs can change them.

## Finding

The principal theoretical corrections survive the shortening. I found one small wording regression in the latest clarity pass, rather than a missing proof or broken central result.

**Local repair, now verified: PI-5 unnecessarily made the selected endpoint mixture the only way to achieve stationary expected usage at a gap.** Baseline JAIR line 431 / LNCS line 397 said, “A single stationary policy with expected usage $B$ at a gap budget requires the endpoint mixture of Definition PI-3.” Randomization among other straddling family members can also attain the target. Definition PI-3 itself correctly states this at JAIR line 342, reflecting ledger 9.17.48's correction distinguishing general attainability from the selected crossing mixture. For example, a step usage curve with sampled usages `(0, 0.5, 1.5, 2)` and target `1` permits an equal mixture of the selected middle endpoints and also an equal mixture of the two outer endpoints. The crossing mixture is sufficient, not necessary.

`git blame` places the “requires” wording in `7e665305`. The previous `331ca34` text described attaining the target as “the job of the endpoint mixture,” a description of this paper's procedure rather than a necessity statement. The current wording should be replaced in both masters with: “To obtain expected usage $B$ at a gap budget with a fixed policy, one can use the per-episode endpoint mixture of Definition~\ref{def:pi3}.” This does not change the theorem, proof, implementation, or experimental result.

## Historical correction dispositions

1. **Four price objects — PRESERVED.** JAIR 319–342 separates the level set, population final crossing, finite-grid bracket and episode-level endpoint mixture. The threshold is the supremum of the explicit set $D_B$, and absence of a finite crossing is disclosed. No “set-valued price” assertion remains. The definition is byte-identical in LNCS (label at 286). The historical single-symbol ambiguity is also resolved: $w^*(B)$ is the threshold and the plotted nearest grid weight is $\hat w(B)$ (JAIR 403, 529).

2. **Closed enclosure rather than half-open containment — PRESERVED.** JAIR 331 explicitly distinguishes the reported $(w_{lo},w_{hi}]$ from its closed enclosure, permits the threshold to equal $w_{lo}$ and conditions containment on the grid missing no crossing between samples or beyond its end. The onset corollary at 395 and its proof at 1096 both retain the closed enclosure. The latest clarification still distinguishes the exact one-step decision from whole receding-horizon episodes (398, 1099).

3. **General mixture attainability versus the selected crossing pair — PRESERVED in the definition; MINOR REGRESSION in PI-5 prose.** JAIR 342 gives the closure of mixture usages, requires attained endpoint usage for boundary targets, retains the descending-curve counterexample and final-grid-below-target fallback. The caveat is not missing from the shortened definition. The isolated “requires” sentence at 431 is the finding above.

4. **Strict straddling and population versus estimated mixture targets — PRESERVED.** JAIR 333–340 gives the exact endpoint probability and attributes exact equality only to population endpoint usages. Held-out equality is explicitly not guaranteed when estimates determine the pair and probability. `rho_aif/budget.py:462` onward still uses strict `< B` / `>= B` thresholds, and flags fallbacks as unbracketed. The code's numerical tolerance affects its achievability flag, not the bracket. JAIR 344 retains the unbracketed Tiger and below-range cases.

5. **Calibration target versus cap optimization — PRESERVED.** JAIR 294–307 defines equality calibration before the separate $U\le B$ reference problem. It identifies the actual Lagrangian as $R-\lambda U$ and separately treats $R+wI$ as an information-floor relaxation for exact optimizers. The proof is still present (301–305). The implemented policy's star does not falsely mean an episodic-return optimizer. The target/cap figure caption at 312 explicitly allows better same-target mixtures and better cap-feasible policies that spend less. The distinction also survives Introduction 95, experimental framing 450, implications 610 and Conclusion 796.

6. **The $w=1$ anchor need not be recovered by inversion — PRESERVED.** Figure caption 102, Introduction 109 and Discussion 779 all say $w=1$ belongs to its implicit budget's level set and need not be its crossing threshold. The title's “canonical” terminology is not expanded into a scale-invariant or reward-optimality theorem. The three-of-five empirical qualification remains at 113 and 779.

7. **Count/cost scale identities and grid rescaling — PRESERVED.** Proposition PI-1 at 351–362 separately states count invariance and multiplication of cost usage by $\alpha$. JAIR 366–371 gives the correct threshold transformations, including the $B/\alpha$ argument for cost, and conditions bracket rescaling on rescaling the grid. Its proof remains complete. The same labeled proposition is byte-identical in LNCS.

8. **Relative tie-breaking and measured bit identity — PRESERVED.** JAIR 364 says the $10^{-12}$ tolerance scales with candidate magnitude and explicitly distinguishes floating-point measurement from mathematical homogeneity. Both agents' `_strictly_better` helpers (`rho_aif/agents/efe.py:22`, `planning_infogain.py:23`) use the larger absolute magnitude and explicitly handle infinite sentinels. JAIR 471 and 479 scope exact collapse to matched measured points and seed SEs. No abstract guarantee of bit-identical floating-point behavior is introduced.

9. **Directly tuned weights also transfer under equivariance — PRESERVED.** JAIR 371 and 445 explicitly retain this withdrawn contrast. Calibration's stated benefit is specification in sensing units; it does not claim exclusive rescaling capability or reduced sampling cost.

10. **Monotonicity is about exact fixed-plan maximizers, not observation count — PRESERVED.** PI-2 (378–389) retains its two optimality inequalities and the correct consequences for information and reward. The text immediately excludes a monotone-count conclusion and whole receding-horizon trajectories. The staircase discussion and nonmonotone examples remain. No shortened monotonicity claim smuggles in the stronger assertion.

11. **PI-5 full conditions, controller variants and gap distinction — PRESERVED except for the isolated mixture-necessity wording.** JAIR 419–428 keeps stationarity, fresh independent resets, bounded usage and martingale differences, an interior sign-consistent crossing, separation away from it, and the diminishing-step assumptions. JAIR 429 separates weight convergence from expected usage at the current weight. JAIR 431 restricts the running-average result to the harmonic schedule. JAIR 415 and 436 exclude the constant-step unprojected library default and reset-on-shift heuristic. Code (`rho_aif/budget.py:864`; `rho_aif/agents/dual_descent.py`) retains the upper-projection option and separately optional reset mechanism.

12. **Direct supermartingale proof instead of an unsupported exact theorem mapping — PRESERVED.** JAIR 434 uses Robbins–Monro, Blum and Kushner as background. The actual proof at 1108–1115 derives the projected squared-distance drift, constructs the nonnegative supermartingale, rules out nonzero limiting error with separation and divergent step sum, then invokes eventual inactive projection and Kronecker's lemma for average usage. The mathematical body of this proof is byte-identical to the dated 80-page pre-trim source. The latest edit only adds a roadmap sentence. The stationary theorem is not applied to empirical mid-run changes (491, 496, 794).

13. **Normalizer, reward convention and bits/nats — PRESERVED.** JAIR 181 gives the variable-length normalizer warning before the theorem. JAIR 191–216 states the exchange-rate assumption, derives $\ln P=\beta R-\ln Z$, describes policy dependence of the accumulated normalizer, separates the exact log-score case from the conditional reward recursion, and separately labels the empirical bit convention. The nat-canonical conversion and its measured exception on Tileworld remain. Nothing in the short abstract removes the conditional reward identification (80).

14. **Rewards are not observations — PRESERVED.** The observe-then-commit setup (161), factored definition (228), commit theorem (199), factored scope discussion (249), loop caption (993), and appendix (1076) keep this restriction. Nonterminal exploitation is not accidentally assigned zero information merely because its reward is unknown: the text expressly says payoffs are not conditioned upon, and an agent conditioning on them must include their information.

15. **Hidden-state preservation and coupling diagnostic — PRESERVED.** JAIR 233–253 defines observation-before-transition posteriors and the diagnostic, limits the proposition to observation/navigation actions, says slow drift can make the divergence infinite, and denies an additive value correction or error bound. The full destructive-sensing example and action-ranking reversal remain at 1049–1069. Appendix 1080 retains the logically important one-way statement: nonzero diagnostic witnesses failure of preservation, whereas zero does not establish preservation. No removed appendix is needed for this claim.

16. **Fehr's Lipschitz hypothesis — PRESERVED.** Related Work 124 states the hypothesis, distinguishes full-support likelihoods from zero-likelihood/noiseless models and says the present exact recursion does not rely on the approximation guarantee. It does not revive the previously incorrect claim that every information-gain reward fails Lipschitz continuity at simplex vertices.

17. **Two-state hypotheses, perfect sensing and the former “near-optimality interval” — PRESERVED AND CLARIFIED.** JAIR 1007 states positive correct reward, asymmetric payoffs, a uniform prior and sensor accuracy range. Parts (a)/(b) separate $p=1$ from $p<1$ and explain the zero-information denominator under perfect sensing (1027). The exact posterior calculation for the second observation remains at 1037. Main text 220 and theorem 1027 now accurately call the interval “single-observation,” and distinguish the case where immediate commitment is reward-optimal and an observation incurs the stated loss. The result is not extended to longer receding-horizon episodes.

18. **Mathematical consistency corrections from the main-text shortening — PRESERVED, OR REMOVED WITH THE UNUSED DISPLAY.** Bellman depth and terminal conditions are explicit (186–204 and 817–832), the softmax limiting distribution is distinguished from deterministic tie selection (181), and $H(b)$ versus horizon $H$ is defined (176). The unsupported indicator glyph is replaced by defined $\mathbf1$ (398). The displayed reward-relevant IG formula that formerly needed an observation expectation is no longer printed, but the remaining variant is clearly ordinary expected information gain on the marginal reward-equivalence belief (640), and the factorization derivation remains (974–978). There is no surviving incorrect formula. The proper-scoring software demonstration has been removed together with its empirical demonstration claims; the theoretical log-score identification still has its own assumptions and derivation.

19. **Synthetic Inspection and conditional practical recommendation — PRESERVED.** Discussion 790 retains a synthetic task, known simulators and a hand-coded leaf rule. Conclusion 796 says calibration adapts an already-selected family, subject to a transfer check, and is not itself a reason to prefer that family over directly counting/penalizing accesses. The extension's independent targets are distinguished from an actual operational requirement (777). No broad deployment or realism claim is restored.

## Proof and mirror integrity

I extracted every `proof` environment from the live JAIR source and from `paper/legacy/2026-10-02_pre_claim_focused_appendices/full_paper_jair.tex`. There are six in each; all six match byte-for-byte. The controller proof is outside a `proof` environment, so I checked its mathematical body separately; it also matches byte-for-byte. Thus the latest appendix trimming did not shorten away a step of any of these arguments.

I separately compared the complete labeled environments for `prop:equivalence`, `def:factored`, `prop:factored`, `def:pi3`, `prop:pi1`, `prop:pi2`, `cor:pi4`, `prop:pi5`, `prop:nearopt`, `ex:destructive` and `rem:transition-aware` between the two current masters. All eleven match byte-for-byte. The minor finding therefore occurs in both versions, rather than being an overlooked mirror mismatch.

No new experiment was run for this audit. No empirical file, manuscript or mathematical implementation was edited by this reviewer. The finding can be repaired by one mirrored sentence replacement, followed by the ordinary publication build and package refresh. Subject to that repair, I find no material regression of the audited theoretical corrections and no indispensable proof removed by the shortening.

## Verified repair and final theory verdict

The root agent applied the repair to both masters. I re-read the actual working sources, rather than relying on its summary. JAIR 431 / LNCS 397 now say: “The per-episode endpoint mixture of Definition~\ref{def:pi3} gives a fixed randomized policy with expected usage $B$ when its endpoints straddle the target.” This is correctly a sufficient construction, includes its required straddling condition and no longer excludes alternative mixtures. The theorem statement, proof and data are otherwise unchanged. The accompanying tolerance sentence is now a direct comparison of absolute and relative tolerances, without narrating revision history, and does not broaden the measured bit-identity claim. The caption sentence splits do not change the relevant mathematical scope.

Verified repaired source fingerprints:

- JAIR: `853e03987bce7e92606f7ef736142e24d5166bbbdab60bfea170f10f491cd6d4`.
- LNCS: `74a541bf762fce3dd8ac210aa528502cfd8ffd9d5e9825a975015e60f0493f08`.

**Final verdict: no remaining required theoretical regression repair in the audited scope.** The shortened manuscript preserves the substantive corrections, qualifications and proofs reviewed here. This is a preservation audit, not an exhaustive new theorem-verification campaign or a prediction of a journal decision.

### Final source freeze after platform clarification

I inspected the complete final source diff against `7e66530` in both masters after the last platform clarification. Beyond the already verified mixture-sufficiency repair, measured-tolerance wording and punctuation splits, the shared sensor reproducibility paragraph now identifies its recorded macOS 27.0 / arm64 / Python 3.9.6 platform and one-thread configuration. The JAIR checklist distinguishes that platform from the simulation environment of record. These additions introduce no mathematical, inferential or theoretical scope change. No new theoretical issue is present in the final diff.

Final inspected source hashes:

- JAIR: `db283e6949d6a018a1bbed7fb93c4291b0b5b25dbf0fab63d2b43978da4fb9a9`.
- LNCS: `4aed0485371b1186953c13956d87232b3da8b14dac6e19bfd45867333e87953f`.

Final theory-preservation verdict remains **PASS, with no required repair outstanding**.
