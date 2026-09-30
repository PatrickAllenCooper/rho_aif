# JAIR Review Report: Active Inference Theory Lens

## 1. Recommendation
Accept

## 2. Summary
This manuscript establishes an operational equivalence between the recursive Expected Free Energy (EFE) objective of active inference and $\rho$-POMDPs using an information-gain reward bonus, specifically identifying $w=1$ as the implicit information weight under matched units. It introduces an expected sensing usage target as an alternative to tuned weights, operationalizing the threshold price, grid brackets, and endpoint mixtures. It evaluates the resulting EFE-equivalent planner across observe-then-commit and simple factored observation settings, demonstrating that $w=1$ is a strong, zero-shot default weight for expected reward when reward asymmetry is high, while clarifying that it does not maximize reward under a cap or automatically handle destructive sensing. The shortened manuscript successfully retains the core formal results and empirical comparisons while condensing the framing.

## 3. Strengths
*   **Precise mapping of EFE to established POMDP concepts:** The reduction of recursive EFE to a $\rho$-POMDP with $w=1$ (Proposition 1) grounds active inference's epistemic drive in standard decision-theoretic planning without claiming universal reward optimality.
*   **Clear boundaries on theoretical claims:** The paper is exceptionally disciplined in bounding its claims. It states exact hypotheses for its equivalence (observe-then-commit or hidden-state preservation) and explicitly constructs a counterexample (Example 1) where naive information gain fails under destructive sensing.
*   **Rigorous empirical evaluation:** The integration of fixed-margin TOST for equivalence claims, exact seed-level Welch testing, and the held-out target validation for the budget framework creates a highly credible empirical foundation.
*   **Careful handling of units and normalizers:** The manuscript correctly identifies that the $w=1$ equivalence is strictly conditional on the reward-to-preference log-score mapping, recognizing that this is a chosen convention rather than a scale-invariant derivation.

## 4. Required changes
None.

## 5. Optional suggestions
1. **Appendix placement:** Appendix F (PyMDP Consistency Check) is a very specific implementation note. It could be integrated into the main text as a single sentence if space permits, or left as is.
2. **Clarification on EFE variants:** (Withdrawn: The main body already addresses this at line 212 and points to Appendix B.1 for the taxonomy distinctions.)

## 6. Verification log
1. **Match:** Tiger $w=1$ (EFE) usage is $4.323 \pm 0.045$ and reward $5.061 \pm 0.158$, identically matching Planning ($w=0$) and SARSOP (Table 4 and `results_sarsop_baseline.csv`).
2. **Match:** Diagnosis $w=1$ (EFE) reward is $-1.217 \pm 0.184$, lower than SARSOP's $-1.452 \pm 0.336$ (Table 4 and `results_sarsop_baseline.csv`).
3. **Match:** Bandit EFE reward is $6.261 \pm 0.112$, closely matching SARSOP's $6.280 \pm 0.134$ (Table 4 and `results_sarsop_baseline.csv`).
4. **Match:** TOST equivalence holds for Tiger, Diagnosis, and Bandit at 5 seeds with stated margins ($p \le 0.0458$) (Section 6.6 and `results_tost_sarsop.csv`).
5. **Match:** TOST equivalence holds for $n=20$ robustness study ($p \le 6.8 \times 10^{-7}$) (`results_tost_sarsop_n20_robustness.csv`).
6. **Match:** POMCP (1000) on Tiger hits $1.80$ observations and 89.4% success compared to EFE's 4.20 and 99.4% (Table 9 and `results_pomcp.csv`).
7. **Match:** POMCP (1000) on Tileworld 6x6 collapses to 5.6% success (Table 9 and `results_pomcp.csv`).
8. **Match:** Distractor fraction for ordinary information gain saturates near 0.33 at high weights (Section 6.9 and `results_distractor_diagnosis.csv`).
9. **Match:** Reward-relevance variant of EFE has exactly 0.0 distractor fraction (`results_distractor_diagnosis.csv`).
10. **Match:** Model misspecification on Tiger for EFE overestimating sensor accuracy (0.90) drops observations to 2.65 and success to 96.9% (`results_model_misspec.csv`).

## 7. Would you recommend unqualified Accept if the required changes were made?
Yes.

## 8. Proof verification addendum

*   **Proposition 1 (Equivalence with $\rho$-POMDPs)**: Line 198. Proof at Appendix A, line 875. The main-body pointer at line 212 correctly resolves here. Checked the induction boundary at $d=H$ (commit actions only) and the EFE-to-Bellman recurrence step (negation reverses minimization to maximization, recovering $\rho_{\mathrm{EFE}}(b,a) = I_a(b)$ for observation actions). Verdict: **correct**.
*   **Proposition 2 (Near-optimality thresholds)**: Line 227. Proof sketch at Appendix B.1, line 1664. The main-body pointer at line 249 correctly resolves here. Checked Part (a) single-observation threshold derivation (equating expected improvement with cost and information gain) and Part (b) second-observation cutoff $w > (c - \mathrm{VoI}_2(b))/I(b)$. Both algebraic reductions hold. Verdict: **correct**.
*   **Definition 1 (Factored observation POMDP)**: Line 253. No proof attached or needed; definitions properly isolate observation, navigation, and exploitation sets. Verdict: **correct**.
*   **Proposition 3 (Factored extension)**: Line 271. Proof sketch at Appendix B.2, line 1700. The main-body pointer at line 311 correctly resolves here. Checked the state-preservation identity $T_{\mathrm{hid}} = \delta$, which trivializes the transition-observation discrepancy and yields $D_{\mathrm{KL}}=0$. Verdict: **correct**.
*   **Example 1 (Destructive sensing)**: Line 280. Verified numerically by the authors (line 299). Checked the manual state-transition calculation: $b'_{o,T}$ becomes a point mass at 0 regardless of $o$, while $b'_o$ tracks the obsolete state $o$, yielding $D_{\mathrm{KL}}=\infty$ and establishing the $V_{\mathrm{true}}$ vs. $V_{\mathrm{naive}}$ sign flip for $c \in (1,2)$. Verdict: **correct**.
*   **Definition 2 (Definition PI-3: Operational shadow price)**: Line 376. Evaluated the internal claim that "A budget is attainable by some per-episode mixture... iff $\inf U(w) \le B \le \sup U(w)$". This is a direct consequence of the linearity of expectation for randomized episodic policies across the achievable range. Verdict: **correct**.
*   **Proposition 4 (Proposition PI-1: Exact scale equivariance)**: Line 388. Proof is inline at line 397. Checked the scale transformation $\alpha \cdot (\text{pragmatic}) + \alpha w \cdot (\text{IG}) = \alpha \cdot (\text{unscaled value})$. The strict positive scaling preserves the ordering and recovers the equivariance identities $U_{\mathrm{count},\alpha}(\alpha w) = U_{\mathrm{count}}(w)$ and $U_{\mathrm{cost},\alpha}(\alpha w) = \alpha U_{\mathrm{cost}}(w)$. Verdict: **correct**.
*   **Proposition 5 (Proposition PI-2: Monotone comparative statics)**: Line 415. Proof is inline at line 422. Checked the paired inequalities from the argmax optimality definition. Algebraic combination properly isolates $(w_2 - w_1)(I(\pi_{w_2}) - I(\pi_{w_1})) \ge 0$, establishing $I_2 \ge I_1$ and $R_2 \le R_1$. Verdict: **correct**.
*   **Corollary 1 (Corollary PI-4: Usage-onset corollary)**: Line 430. Proof at Appendix B.3, line 1754. The main-body pointer at line 437 correctly resolves here. Checked the equivalence of the step function $U(w) = \mathbf{1}[w > w_{\mathrm{thresh}}]$ mapped to Definition PI-3's crossing threshold. Verdict: **correct**.
*   **Proposition 6 (Proposition PI-5: Stationary convergence)**: Line 454. Proof at Appendix D.1, line 1761 (with the argument at line 1780). The main-body pointer at line 459 correctly resolves here. Checked the mapped Robbins-Monro recursion $w_{t+1} = \text{Proj}(w_t - a_t(U_t - B))$ against the nonnegative supermartingale $Y_t = e_t^2 + C\sum_{k\ge t}a_k^2$. The bounds hold, yielding almost sure convergence $w_t \to w^*$ and Kronecker's lemma properly supports the running-average claim. Verdict: **correct**.
