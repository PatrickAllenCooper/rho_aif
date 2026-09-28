1. **Recommendation**: Accept

2. **Summary**: The paper establishes a formal equivalence between Expected Free Energy (EFE) minimization in active inference and $\rho$-POMDPs with an information-gain bonus. It shows that under a shared reward convention, the EFE objective corresponds to an information-unit weight of $w=1$. The authors extend this to factored observation POMDPs, where information-gathering actions preserve the hidden state, and introduce a transition-observation coupling diagnostic for when this fails (e.g., destructive sensing). The paper also proposes an operational shadow price framework for calibrating the information weight to meet a stated sensing budget, including exact scale equivariance, a crossing bracket for usage gaps, and an online dual controller. The claims are supported by rigorous empirical evaluation across multiple environments and baselines.

3. **Strengths**:
   - The theoretical mapping between EFE and $\rho$-POMDPs is precise, clarifying the exact conditions under which the equivalence holds (e.g., log-scoring, factored observation POMDPs).
   - The distinction between what EFE can price and what the factored reduction covers (Remark 1, destructive sensing) is insightful and rigorous.
   - The empirical evaluation is exceptionally thorough, with multi-seed statistics, proper baselines, and ablation studies.
   - The paper's characterization of the active inference literature is accurate, specifically identifying the sophisticated inference formulation rather than overclaiming.

4. **Required changes**: None.

5. **Optional suggestions**:
   1. In the discussion of the normalizer $\ln Z$ in Section 3.1 (line 225, "Deriving that recursion from a normalized preference distribution would add a term the recursion omits"), consider adding a brief footnote on how this constant might be handled in settings where episode lengths are fixed but unknown.

6. **Proof audit**:
   - **Proposition 1** (Statement line 206, Proof line 1091): The key step negates the EFE recursion $V = -\mathcal{G}$ to match the $\rho$-POMDP Bellman recursion with $R = -c_k$ and $\rho = I_k(b)$ for observations, and $R = \mathbb{E}_b[R_i]$ and $\rho=0$ for commits. This follows exactly. The $\ln Z$ normalizer argument (line 225) correctly notes that identifying pragmatic value with task reward omits the preference normalizer $\ln Z$. This is exact under log scoring rules because the reward is itself a log probability, making $Z=1$ and $\ln Z=0$.
   - **Proposition 2** (Statement line 233, Proof line 252): The key step sets the net gain from observing to zero at $H=1$ to find $w^*_{\mathrm{thresh}}$. This follows algebraically. For $p \in (1/2, 1)$ in Part (b), $p=1$ is properly excluded because $I(b)=0$ after the first observation, making the over-observation ratio undefined. For Part (a), $p=1$ is allowed with the standard $0 \ln 0 = 0$ convention, giving $I_{\max} = \ln 2$.
   - **Proposition 3 / Factored POMDPs** (Statement line 300, Proof line 305): The key step notes that for actions preserving $s_{\mathrm{hid}}$, the transition is the identity, so $b'_{o,T}$ coincides with $b'_o$, making $D_{\mathrm{KL}}[b'_{o,T} \| b'_o] = 0$. This follows.
   - **Proposition PI-1** (Statement line 429, Proof line 436): The key step shows that multiplying all rewards and costs by $\alpha$ and $w$ by $\alpha$ scales the objective by $\alpha$, leaving the argmax identical under a scale-independent tie-break. This follows.
   - **Proposition PI-2** (Statement line 449, Proof line 457): The key step uses a revealed-preference argument, adding the optimality inequalities for $w_1$ and $w_2$ to show $(w_2 - w_1)(I(\pi_{w_2}) - I(\pi_{w_1})) \ge 0$. This standard monotone comparative statics argument follows.
   - **Proposition PI-5** (Statement line 495, Proof line 500): The key step maps the projected decaying-step controller to the Robbins-Monro recursion and Kushner's constrained stochastic approximation. The mapping of conditions (martingale difference noise, sign and separation conditions) is correct and follows.
   - **Corollary PI-4** (Statement line 483, Proof line 487): The key step states that the first jump of the usage staircase occurs at the $H=1$ threshold $w^*_{\mathrm{thresh}}$ from Prop 2. This follows, as below this threshold the agent commits immediately (0 observations).
   - **Remark 1 on destructive sensing** (Statement line 338): The key step explains that recomputing the epistemic term from the transition-aware joint posterior removes the illusory information credit when an action changes the hidden state. This follows.
   - **Count/cost equivariance identities** (Statement lines 432, 434): $U_{\mathrm{count},\alpha}(\alpha w) = U_{\mathrm{count}}(w)$ and $U_{\mathrm{cost},\alpha}(\alpha w) = \alpha U_{\mathrm{cost}}(w)$. These follow directly from the actions being identical across scales.
   - **Lipschitz claim** (Line 127): Expected information gain is globally Lipschitz for full-support sensors. This follows because the entropy function has bounded derivative away from the boundary of the simplex.
   - **$\Delta_T$ coupling diagnostic** (Line 296): Defined as $\mathbb{E}_{o}\, D_{\mathrm{KL}}[b'_{o,T} \| b'_o]$. The claim that it is a diagnostic, not a bound, is explicitly stated and mathematically appropriate.

7. **Literature characterization**:
   - **Friston et al.** (Lines 138-139, 146): Claims Friston (2010) casts perception/action as variational inference, and Friston (2021) introduced sophisticated inference (recursive tree search over belief trajectories). Accurate.
   - **Da Costa** (Lines 139, 146): Claims Da Costa (2020) synthesized discrete-state AIF, and Da Costa (2020b) proved an optimality result for sophisticated inference in the $\beta \to \infty$ limit. Accurate.
   - **Parr** (Line 139): Claims Parr (2019) showed EFE decomposes into pragmatic and epistemic value, and compared EFE against generalised free energy. Accurate.
   - **Champion** (Line 141): Claims Champion (2024) addressed the unification problem of four EFE formulations. Accurate.
   - **Kouw 2026** (Line 519): Claims Kouw (2026) derives EFE as the stationary point of a constrained Bethe-Lagrangian optimization. Accurate.
   - **Sweeney 2026** (Line 143): Claims Sweeney (2026) surveys formal correspondences between EFE and six decision-theoretic frameworks. Accurate.
   - **Sophisticated inference** (Lines 146, 185): Claims it evaluates policies closed-loop via recursive tree search over belief states. Accurate.

8. **Verification log**:
   I checked 20 quantitative claims in the text against the backing CSVs:
   - Tiger Myopic Success: 85.3% (CSV: 0.8532) - Match
   - Tiger Myopic Reward: -7.15 (CSV: -7.148) - Match
   - Tiger EFE Success: 99.4% (CSV: 0.9944) - Match
   - Tiger EFE Reward: +5.19 (CSV: 5.186) - Match
   - Diagnosis Myopic Success: 64.7% (CSV: 0.6472) - Match
   - Diagnosis Myopic Reward: -13.17 (CSV: -13.168) - Match
   - Diagnosis EFE Success: 97.2% (CSV: 0.9716) - Match
   - Diagnosis EFE Reward: -1.37 (CSV: -1.3688) - Match
   - Bandit Myopic Success: 62.2% (CSV: 0.6218) - Match
   - Bandit Myopic Reward: +5.56 (CSV: 5.5645) - Match
   - Bandit EFE Success: 86.9% (CSV: 0.8694) - Match
   - Bandit EFE Reward: +6.27 (CSV: 6.2718) - Match
   - Nat-canonical check on Tiger: $w=\ln 2$ reward is 5.3264, bit-identical to $w=1$ (CSV `results_nat_canonical_check.csv`: `reward_nat` 5.3264, `bit_identical_to_w1` True). Match.
   - Nat-canonical check on Tileworld: $w=\ln 2$ reward is -20.8072, not bit-identical to $w=1$ (CSV `results_nat_canonical_check.csv`: `reward_nat` -20.8072, `bit_identical_to_w1` False). Match.
   - SARSOP TOST on Tiger: diff 0.0, p_tost 0.001025, equivalent True (CSV `results_tost_sarsop.csv`). Match.
   - SARSOP TOST on Diagnosis: diff 0.2352, p_tost 0.0458, equivalent True (CSV `results_tost_sarsop.csv`). Match.
   - SARSOP TOST on Bandit: diff -0.0186, p_tost 0.01297, equivalent True (CSV `results_tost_sarsop.csv`). Match.
   - W_atlas Bandit budget1: 4.5988, bracketed True (CSV `results_w_atlas.csv`). Match.
   - W_atlas Diagnosis budget1: 6.993, bracketed True (CSV `results_w_atlas.csv`). Match.
   - Dual-control recovery-time: Decay mean 157.3, Reset mean 51.2, difference 106.1 (CSV `results_price_dual_multiseed_metrics.csv`). Match.

9. **Would you recommend unqualified Accept if the required changes were made?** Yes.