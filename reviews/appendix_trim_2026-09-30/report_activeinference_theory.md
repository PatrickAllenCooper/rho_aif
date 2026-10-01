1. **Recommendation.** Accept

2. **Summary**
The paper establishes a formal equivalence between minimizing a recursive, reward-based Expected Free Energy (EFE) objective and solving a $\rho$-POMDP with expected information gain as a belief-dependent reward at a specific weight ($w=1$). It rigorously scopes this equivalence, explicitly addressing the role of the preference normalizer ($\ln Z$) and the choice of information units. Building on this, it introduces a budgeted formulation to calibrate the information weight to a target expected sensing usage. It precisely defines the crossing threshold, its finite-grid bracket estimate, and the endpoint mixture required to attain gap budgets (Definition PI-3). The paper proves exact scale equivariance for this family (Proposition PI-1) and provides a supermartingale proof for the stationary convergence of a projected dual controller (Proposition PI-5). It also characterizes sensing onset thresholds for a two-state model.

3. **Strengths.**
- The theoretical claims are exceptionally well-scoped. The paper does not overclaim the EFE equivalence, explicitly noting its dependence on the log-scoring rule and the potential impact of the $\ln Z$ normalizer on variable-length episodes.
- The distinction between the theoretical nat units and the empirical bit units is handled transparently and verified empirically.
- Definition PI-3 is a model of clarity, carefully distinguishing the true crossing threshold from the finite-grid bracket and the endpoint mixture, which is crucial for discontinuous usage curves.
- The supermartingale proof for the dual controller (Proposition PI-5) is mathematically sound and correctly handles the bounded, discontinuous nature of the usage curve.
- The active-inference literature is represented fairly and comprehensively, acknowledging the diversity of EFE constructions and citing recent relevant work (e.g., Kouw 2026).

4. **Required changes.**
None. The theoretical claims within this lens are correct, properly scoped, and supported by the provided proofs and artifacts.

5. **Optional suggestions.**
None.

6. **What you verified.**
- **Proposition 1 and its proof:** Checked the induction proof in Appendix A. Result: Correct.
- **Units and $\ln Z$ normalizer:** Checked Section 3.2 for the discussion of the normalizer and the nat-canonical agent. Verified the empirical claims against `results/results_nat_canonical_check.csv`. Result: The CSV confirms that the nat-canonical agent ($w=\ln 2$ in bit units) is bit-identical to $w=1$ on Tiger, Testbed, Diagnosis, and Bandit, but differs on Tileworld, exactly as stated in the prose.
- **Definition PI-3:** Checked the definitions of the level set, crossing threshold, grid bracket, and endpoint mixture. Result: Mathematically precise and conceptually distinct.
- **Scale equivariance:** Checked the proof of Proposition PI-1 and verified the empirical collapse against `results/results_price_scale_collapse.csv`. Result: The CSV shows a `usage_spread` of exactly 0.0 across scales, confirming the bit-identical collapse claimed in the text.
- **Proposition PI-5 and supermartingale proof:** Checked the proof in Appendix C. Result: The application of the Robbins-Monro recursion with projection and the supermartingale convergence argument are correct.
- **Two-state threshold results:** Checked the claims in Proposition 2 against `results/results_thresholds.csv`. Result: The computed thresholds in the CSV match the theoretical properties described.
- **Active-inference literature:** Checked the Introduction and Related Work sections. Result: The literature is represented fairly, distinguishing the paper's specific recursive reward-based EFE from other variants (e.g., FEEF, generalized free energy) and properly positioning it against Bethe-Lagrangian formulations.