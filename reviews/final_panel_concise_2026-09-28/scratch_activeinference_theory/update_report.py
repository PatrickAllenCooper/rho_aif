import re

with open("reviews/final_panel_concise_2026-09-28/report_activeinference_theory.md", "r") as f:
    content = f.read()

# Withdraw the optional suggestion
content = re.sub(
    r"2\. \*\*Clarification on EFE variants:.*",
    "2. **Clarification on EFE variants:** (Withdrawn: The main body already addresses this at line 212 and points to Appendix B.1 for the taxonomy distinctions.)",
    content
)

# Append Section 8
addendum = """
## 8. Proof verification addendum

*   **Proposition 1 (Equivalence with $\\rho$-POMDPs)**: Line 198. Proof at Appendix A, line 875. The main-body pointer at line 212 correctly resolves here. Checked the induction boundary at $d=H$ (commit actions only) and the EFE-to-Bellman recurrence step (negation reverses minimization to maximization, recovering $\\rho_{\\mathrm{EFE}}(b,a) = I_a(b)$ for observation actions). Verdict: **correct**.
*   **Proposition 2 (Near-optimality thresholds)**: Line 227. Proof sketch at Appendix B.1, line 1664. The main-body pointer at line 249 correctly resolves here. Checked Part (a) single-observation threshold derivation (equating expected improvement with cost and information gain) and Part (b) second-observation cutoff $w > (c - \\mathrm{VoI}_2(b))/I(b)$. Both algebraic reductions hold. Verdict: **correct**.
*   **Definition 1 (Factored observation POMDP)**: Line 253. No proof attached or needed; definitions properly isolate observation, navigation, and exploitation sets. Verdict: **correct**.
*   **Proposition 3 (Factored extension)**: Line 271. Proof sketch at Appendix B.2, line 1700. The main-body pointer at line 311 correctly resolves here. Checked the state-preservation identity $T_{\\mathrm{hid}} = \\delta$, which trivializes the transition-observation discrepancy and yields $D_{\\mathrm{KL}}=0$. Verdict: **correct**.
*   **Example 1 (Destructive sensing)**: Line 280. Verified numerically by the authors (line 299). Checked the manual state-transition calculation: $b'_{o,T}$ becomes a point mass at 0 regardless of $o$, while $b'_o$ tracks the obsolete state $o$, yielding $D_{\\mathrm{KL}}=\\infty$ and establishing the $V_{\\mathrm{true}}$ vs. $V_{\\mathrm{naive}}$ sign flip for $c \\in (1,2)$. Verdict: **correct**.
*   **Definition 2 (Definition PI-3: Operational shadow price)**: Line 376. Evaluated the internal claim that "A budget is attainable by some per-episode mixture... iff $\\inf U(w) \\le B \\le \\sup U(w)$". This is a direct consequence of the linearity of expectation for randomized episodic policies across the achievable range. Verdict: **correct**.
*   **Proposition 4 (Proposition PI-1: Exact scale equivariance)**: Line 388. Proof is inline at line 397. Checked the scale transformation $\\alpha \\cdot (\\text{pragmatic}) + \\alpha w \\cdot (\\text{IG}) = \\alpha \\cdot (\\text{unscaled value})$. The strict positive scaling preserves the ordering and recovers the equivariance identities $U_{\\mathrm{count},\\alpha}(\\alpha w) = U_{\\mathrm{count}}(w)$ and $U_{\\mathrm{cost},\\alpha}(\\alpha w) = \\alpha U_{\\mathrm{cost}}(w)$. Verdict: **correct**.
*   **Proposition 5 (Proposition PI-2: Monotone comparative statics)**: Line 415. Proof is inline at line 422. Checked the paired inequalities from the argmax optimality definition. Algebraic combination properly isolates $(w_2 - w_1)(I(\\pi_{w_2}) - I(\\pi_{w_1})) \\ge 0$, establishing $I_2 \\ge I_1$ and $R_2 \\le R_1$. Verdict: **correct**.
*   **Corollary 1 (Corollary PI-4: Usage-onset corollary)**: Line 430. Proof at Appendix B.3, line 1754. The main-body pointer at line 437 correctly resolves here. Checked the equivalence of the step function $U(w) = \\mathbf{1}[w > w_{\\mathrm{thresh}}]$ mapped to Definition PI-3's crossing threshold. Verdict: **correct**.
*   **Proposition 6 (Proposition PI-5: Stationary convergence)**: Line 454. Proof at Appendix D.1, line 1761 (with the argument at line 1780). The main-body pointer at line 459 correctly resolves here. Checked the mapped Robbins-Monro recursion $w_{t+1} = \\text{Proj}(w_t - a_t(U_t - B))$ against the nonnegative supermartingale $Y_t = e_t^2 + C\\sum_{k\\ge t}a_k^2$. The bounds hold, yielding almost sure convergence $w_t \\to w^*$ and Kronecker's lemma properly supports the running-average claim. Verdict: **correct**.
"""

with open("reviews/final_panel_concise_2026-09-28/report_activeinference_theory.md", "w") as f:
    f.write(content + addendum)

