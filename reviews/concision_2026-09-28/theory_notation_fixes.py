"""Approved notation-only amendments, applied by assembly to each master.

Legacy files and draft fragments are never modified by this module. Every
replacement is guarded against an unexpected source version.
"""

def _once(source: str, old: str, new: str) -> str:
    count = source.count(old)
    if count != 1:
        raise ValueError(f"Expected one notation anchor, found {count}: {old[:100]}")
    return source.replace(old, new, 1)


def apply(source: str) -> str:
    changes = [
        (
            r"$-1$ otherwise (the Proposition~\ref{prop:nearopt} testbed).",
            r"$-1$ otherwise.",
        ),
        (
            r'A $\rho$-POMDP adds a belief-dependent utility $\rho:\Delta(S)\times\mathcal{A}\to\mathbb{R}$ to task reward, giving the objective',
            r'A $\rho$-POMDP adds a belief-dependent utility $\rho:\Delta(S)\times\mathcal{A}\to\mathbb{R}$ to task reward, where $\Delta(S)$ is the probability simplex over hidden states $S$. Its objective is',
        ),
        (
            r'The EFE formulation considered here combines expected negative log-preference with negative expected information gain,',
            r'At future time $\tau$, the EFE formulation considered here combines expected negative log-preference with negative expected information gain,',
        ),
        (
            r'$Q$ is the predictive distribution and $P(\cdot\mid C)$ the preference distribution, distinct from the observation model conditioned on state and action.',
            r'$Q(o_\tau\mid\pi)$ predicts observations under policy $\pi$, while $Q(s_\tau\mid\pi)$ and $Q(s_\tau\mid o_\tau,\pi)$ are the corresponding prior and posterior beliefs. The parameters $C$ specify the preference distribution $P(\cdot\mid C)$, which is distinct from the observation model conditioned on state and action.',
        ),
        (
            r'The agent selects a deterministic $\arg\min$, the infinite-policy-precision limit of $Q(\pi)\propto\exp(-\kappa\mathcal G(\pi))$. Policy precision $\kappa$ is distinct from the reward inverse temperature $\beta$ below.',
            r'The agent selects a minimizing action using a fixed tie-breaking rule. As policy precision $\kappa\to\infty$, the softmax $Q(\pi)\propto\exp(-\kappa\mathcal G(\pi))$ concentrates on policies minimizing $\mathcal G$. The implementation makes a deterministic selection among tied minimizers. Policy precision $\kappa$ is distinct from the reward inverse temperature $\beta$ below.',
        ),
        (
            r'At $d=H$, the value is the best commit value. This is a $\rho$-POMDP Bellman recursion with an action-dependent belief utility, as permitted by \citet{araya2010}.',
            r'At $d=H$, the value is the best commit value. Write $R(b,a):=\sum_s b(s)R(s,a)$ for expected immediate reward and $V^*(b,d):=\max_a V(a,b,d)$ for the optimal belief-state value. This is a $\rho$-POMDP Bellman recursion with an action-dependent belief utility, as permitted by \citet{araya2010}.',
        ),
        (
            r'and (iv) actions are selected by deterministic $\arg\min$ over $\mathcal{G}$, the $\kappa \to \infty$ limit of the standard softmax policy with precision $\kappa$.',
            r'and (iv) both recursions select actions deterministically with the same fixed tie-breaking rule.',
        ),
    ]
    changes.append((
        r"""Bellman equation $V^*(b) = \max_a \{R(b,a) + \rho_{\mathrm{EFE}}(b,a) + \mathbb{E}_o[V^*(b'_o)]\}$ over the same horizon, with terminal commit actions carrying no continuation term.""",
        r"""Bellman recursion
\begin{align*}
V^*(b,d)=\max_a\big\{&R(b,a)+\rho_{\mathrm{EFE}}(b,a)\\
&+\mathbb E_o[V^*(b'_o,d+1)]\big\}
\end{align*}
over the same horizon, with terminal commit actions carrying no continuation term and only commit actions available at $d=H$.""",
    ))
    changes.extend([
        (
            r'V_{\mathrm{true}}(a_D) = -c + \max_i r(\mathrm{Commit}_i,0) = 1-c,',
            r'V_{\mathrm{true}}(a_D) = -c + \max_i r(\mathrm{Commit}_i,0) = 1-c.',
        ),
        (
            r'For that implemented family, define the usage curve $U(w):=U(\pi^*_w)$.',
            r'For that implemented family, let $\pi^*_w$ denote the closed-loop policy using weight $w$ and define its usage curve by $U(w):=U(\pi^*_w)$. The star here denotes the policy produced by the finite-horizon planner, not an optimizer of total episodic return.',
        ),
        (
            'exactly one bit of illusory credit below the naive estimate, for both outcomes.',
            'For $w=1$ reward unit per bit, this is one reward unit below the naive estimate, for either outcome.',
        ),
        (
            r'Its proof is the single-step curve $U(w)=\mathbb 1[w>w_{\mathrm{thresh}}]$ under the commit-favoring tie rule.',
            r'Its proof is the single-step curve $U(w)=\mathbf{1}[w>w_{\mathrm{thresh}}]$ under the commit-favoring tie rule, where $\mathbf{1}[A]$ is $1$ when $A$ holds and $0$ otherwise.',
        ),
    ])
    for old,new in changes:
        source = _once(source,old,new)

    if source.count(r'\mathbb{1}') != 2:
        raise ValueError('Expected two appendix indicator glyphs.')
    source = source.replace(r'\mathbb{1}',r'\mathbf{1}')

    old_proof = r'''\begin{proof}
We show that $\arg\min_a \mathcal{G}(a, b, d) = \arg\max_a V_\rho(a, b, d)$ at every belief node, where $V_\rho$ is the $\rho$-POMDP value function with $\rho_{\mathrm{EFE}}(b, a)$ as defined in the proposition.

Define $V(a, b, d) \triangleq -\mathcal{G}(a, b, d)$. Since negation reverses ordering, $\arg\min_a \mathcal{G} = \arg\max_a V$.

Case 1, commit actions. For commit action $i$, Equation~\ref{eq:efe_recursive} gives $\mathcal{G}(\text{commit}_i) = -\mathbb{E}_b[R_i]$, so $V(\text{commit}_i, b) = \mathbb{E}_b[R_i]$. The $\rho$-POMDP value is $V_\rho(\text{commit}_i, b) = \mathbb{E}_b[R_i] + \rho_{\mathrm{EFE}}(b, \text{commit}_i) = \mathbb{E}_b[R_i] + 0$. These are identical.

Case 2, observation actions. For observation action $k$, Equation~\ref{eq:efe_recursive} gives
$\mathcal{G}(\text{obs}_k) = c_k - I_k(b) + \mathbb{E}_o[\min_{a'} \mathcal{G}(a', b'_o)].$
Negating both sides gives
$V(\text{obs}_k, b) = -c_k + I_k(b) + \mathbb{E}_o[\max_{a'} V(a', b'_o)].$
The $\rho$-POMDP Bellman backup with $R(b, \text{obs}_k) = -c_k$ and $\rho_{\mathrm{EFE}}(b, \text{obs}_k) = I_k(b)$ gives
$V_\rho(\text{obs}_k, b) = -c_k + I_k(b) + \gamma \mathbb{E}_o[\max_{a'} V_\rho(a', b'_o)].$
With $\gamma = 1$ (undiscounted finite horizon), the two recursions are structurally identical. Since the terminal values (commit actions) agree and the recursive updates agree, by induction on the remaining horizon $H - d$, $V(a, b, d) = V_\rho(a, b, d)$ for all $a$, $b$, $d$. Policies therefore coincide at every belief node.
\end{proof}'''
    new_proof = r'''\begin{proof}
Let $V_\rho(a,b,d)$ be the $\rho$-POMDP action value at belief $b$ and depth $d$, with $\rho_{\mathrm{EFE}}$ defined in the proposition. Define $V(a,b,d):=-\mathcal G(a,b,d)$. Negation reverses ordering, so the minimizing actions for $\mathcal G$ are the maximizing actions for $V$.

For any terminal commit action $i$ and $d\le H$, Equation~\ref{eq:bellman_commit} gives
\[
V(\mathrm{commit}_i,b,d)=\mathbb E_b[R_i]
=V_\rho(\mathrm{commit}_i,b,d),
\]
because $\rho_{\mathrm{EFE}}(b,\mathrm{commit}_i)=0$ and there is no continuation. At depth $H$, only these commit actions are available, establishing the induction boundary.

For observation action $k$ at $d<H$, negating Equation~\ref{eq:efe_recursive}, with its depth arguments explicit, gives
\[
V(\mathrm{observe}_k,b,d)=-c_k+I_k(b)
+\mathbb E_o\!\left[\max_{a'}V(a',b'_o,d+1)\right].
\]
The $\rho$-POMDP backup has the same immediate reward $-c_k$, belief utility $I_k(b)$, posterior distribution, and continuation depth. Under $\gamma=1$, it is therefore the same expression with $V_\rho$ replacing $V$. Induction on the remaining horizon $H-d$ gives $V(a,b,d)=V_\rho(a,b,d)$ for every available action and belief node. Their maximizing action sets coincide, and the shared tie-breaking rule selects the same action. Hence the policies agree throughout the finite-horizon tree and, when replanned from the same beliefs, at each real decision.
\end{proof}'''
    source = _once(source,old_proof,new_proof)
    return source
