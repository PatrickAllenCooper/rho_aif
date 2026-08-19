# Destructive Information: Theory Notes (DS-A)

**Date started**: August 19, 2026
**Status**: Working notes for stage DS-A of `docs/ideation/2026-08-19-destructive-sensing-design.md`. Statements here are drafted against the implemented operator in `rho_aif/agents/transition_aware.py` so theory and code cannot drift. No new citations are introduced; every reference is to results already in the verified table of `price_of_information.md` or to the JAIR manuscript's own propositions.

## 1. Setting and the transition-aware operator (T1)

An observe-then-commit POMDP with destructive sensing attaches to each observation action k a transition kernel T_k alongside the observation model O_k. The timing convention is the JAIR manuscript's (its Delta_T definition): the observation is emitted from the pre-transition state, then T_k acts. For belief b:

- Outcome probability: P(o | b, k) = sum_s O_k(o | s) b(s) (pre-transition emission).
- Joint posterior: b'_{o,T}(s') proportional to sum_s T_k(s' | s) O_k(o | s) b(s).
- Post-transition prior: bar b_k = T_k^T b.
- Transition-aware information gain, in bits: IG_T,k(b) = H(bar b_k) - E_o[H(b'_{o,T})].

The transition-aware EFE operator, exactly as implemented:

G(obs_k, b, d) = c_k - IG_T,k(b) + gamma * E_o[ min_a G(a, b'_{o,T}, d+1) ]
G(commit_i, b, d) = -E_b[r_i]

and the transition-aware Planning+IG value at weight w replaces -IG with +w*IG and min with max. At T_k = I both reduce to the manuscript's state-preserving operators.

**Proposition DI-1 (equivalence carries over).** For any horizon H, discount gamma, and kernels {T_k}, the transition-aware EFE minimizer and the transition-aware Planning+IG maximizer at w = 1 select identical actions at every belief, under the shared strict-improvement tie-break.

*Proof sketch.* Identical to the manuscript's Proposition 3.1 induction: at the leaf, commit terms are exact negations; at interior depth, both agents propagate the same posterior b'_{o,T} and the same outcome distribution P(o | b, k), so the induction hypothesis makes the continuation terms negations, and the observe terms are then negations term by term. The original proof never uses T = I; it only requires that the two agents share the belief-propagation map and tie-breaks. Numerically pinned by `tests/test_transition_aware.py` (w = 1 exact-equivalence test; delta = 0 reduction test). ∎

**Honesty note on the information measure (DI-Q1, open).** IG_T measures entropy reduction about the post-transition state, which is the state the agent must act on. Alternatives disagree when T_k is not the identity: the pre-transition mutual information I(s; o) prices what the test reveals about the state that existed when tested, and the two differ by the entropy injected by T_k itself. No axiomatic argument is claimed for IG_T beyond decision relevance; the manuscript's Example ex:destructive ranking flip is reproduced under IG_T (regression test), which is the operational requirement. An axiomatic comparison is future work and must not be claimed in any paper draft.

## 2. Over-testing region at H = 1 (T2, derivation shape)

Two live states {healthy, faulty} with belief q = P(faulty), one destructive test (accuracy p, destruction delta on faulty, delta/2 on healthy), commits paying R+ correct, -alpha R+ wrong, and -R+ on a destroyed unit (E1 amendment). The state-preserving H = 1 agent evaluates the test with the identity coupling, so its expected commit value after the test ignores the destroyed mass:

V_SP(test; q) = -c + w * IG_I(q) + E_o[ max_i E_{b'_o}[r_i] ]

The transition-aware value replaces both the epistemic and pragmatic continuations with the joint posterior. Writing m_o for the destroyed mass of b'_{o,T} given outcome o:

E_{b'_{o,T}}[r_i] = (1 - m_o) * E_surv[r_i] - m_o * R+

so the pragmatic continuation is damped by survival probability and charged the lost-unit value on the destroyed mass. Define the H = 1 over-testing region as the set of beliefs where the state-preserving agent tests but the transition-aware agent commits:

Omega(delta) = { q : V_SP(test; q) > max_i E_q[r_i] >= V_T(test; q) }.

**Claim DI-2 (to prove for the paper draft).** Omega(delta) is nonempty for every delta > 0 whenever the zero-destruction test is marginally worthwhile somewhere (the interval where V_SP(test) - max commit is positive but smaller than the destruction charge E_o[m_o (E_surv[max] + R+)] plus the epistemic correction), and Omega is monotone increasing in delta in the set-inclusion sense. The expected per-episode over-testing loss of the state-preserving agent is bounded by delta * (R+ + max(0, E_surv[max])) plus the wasted test costs.

*Status*: the decomposition above is exact; the monotonicity claim needs the (short) argument that m_o is affine increasing in delta at fixed q and that IG_T is decreasing in delta at fixed q (destruction shrinks the informative mass). Both are one-page algebra on the three-state simplex; write them out before any experiment claims them. A numeric check script over the (delta, p, alpha) grid of E1 belongs in `experiments/` when DS-D starts, mirroring `tests/test_budget.py::TestProp2OnsetExact`'s pattern of verifying a closed form against enumeration.

## 3. The irreversibility premium (T3)

Let U_D(w) be the usage curve of the transition-aware Planning+IG family on a destructive environment, and U(w) the state-preserving curve on its delta = 0 counterpart. Define the destructive shadow price w*_D(B) as the crossing bracket of U_D at budget B (Definition PI-3 verbatim, with U_D in place of U), and the irreversibility premium:

pi(B) = w*_D(B) - w*(B), on budgets achievable by both curves.

**Conjecture DI-3.** U_D(w) <= U(w) pointwise (at equal weight, destruction suppresses sensing), hence pi(B) >= 0 on the common range.

**Caveat recorded up front**: the E1 amendment gives destruction a bounded-downside property (destroyed pays -R+, a wrong call pays -alpha R+). For alpha >> 1 and very uncertain beliefs, the transition-aware agent can rationally test partly as disposal, which raises U_D locally and could produce pi(B) < 0 at low budgets on high-asymmetry instances. This is a genuine domain effect, not an artifact, and if observed it is reported as such (it bounds where the conjecture holds, exactly as Tileworld's flat curve bounded PI-2's scope). H3's falsifiability depends on this honesty.

## 4. Scale equivariance carries over (T4)

**Proposition DI-4 (expected, proof to write).** Scaling every reward and cost by alpha > 0 while holding w fixed multiplies every G(., b, d) of Section 1 by alpha except the IG term, exactly as in the manuscript's PI-1; therefore the implemented transition-aware receding-horizon agent satisfies U_{D,alpha}(alpha w) = U_D(w) as distributions over seeded episode streams. The PI-1 proof is a linearity induction over the lookahead tree and nowhere uses T = I, so it should transfer verbatim; confirm by walking the induction once with T_k in place and add a collapse test to the DS-D battery (H4).

## 5. What must NOT be claimed (standing list)

- No axiomatic superiority of IG_T over pre-transition mutual information (DI-Q1 open).
- No universal sign for pi(B) (Section 3 caveat).
- No closed-form w*_D; the contribution is the operational machinery carried over, mirroring the manuscript's positioning against Sims 2003 / Matejka-McKay 2015 / Altman 1999 (all already in the verified citation table).
- Nothing about E2/E3 until they exist (DS-B is PARTIAL: E1 only).
