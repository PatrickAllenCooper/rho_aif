"""Second guarded pass for long results/proposition passages."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def once(source: str, old: str, new: str) -> str:
    count = source.count(old)
    if count != 1:
        raise ValueError(f"Expected one match, found {count}: {old[:80]!r}")
    return source.replace(old, new, 1)


OLD_PROP = r"""Consider the projected decaying-step controller, the recursion~\eqref{eq:dual_update} with a finite $w_{\max}$ and step sizes satisfying $\sum_t a_t = \infty$ and $\sum_t a_t^2 < \infty$ (the schedule in~\eqref{eq:dual_update} with $\delta>0$). Suppose four conditions hold. (i) The environment, agent family, and budget $B$ are stationary, so that $\mathbb{E}[U_t \mid w_t] = U(w_t)$ for a fixed function $U$. (ii) Per-episode usage is bounded, which holds here because usage is bounded by the episode step cap, and each episode is run on an environment reset and freshly seeded independently of the past, so that the noise $U_t - U(w_t)$ is a martingale difference with bounded conditional second moment. (iii) There is a single crossing $w^* \in (0, w_{\max})$ with $U(w) < B$ for $w < w^*$ and $U(w) > B$ for $w > w^*$. (iv) The curve stays away from the budget outside every neighborhood of the crossing, that is, for every $0 < \epsilon_1 < \epsilon_2$, $\inf\{\,|U(w) - B| : \epsilon_1 \le |w - w^*| \le \epsilon_2,\ w \in [0, w_{\max}]\,\} > 0$. Then $w_t \to w^*$ with probability one, and hence in probability. Condition (iii) does not require $U(w^*) = B$, and condition (iv) does not require continuity, so the conclusion covers a gap budget in the sense of Definition~\ref{def:pi3}, where $U$ jumps over $B$ at $w^*$ without touching it. What converges in that case is the weight. The usage at the limit is $U(w^*)$, one side of the jump, so the expected usage at $w_t$ need not converge to $B$. The running average of observed usage under the schedule in~\eqref{eq:dual_update} does converge to $B$, $\frac{1}{n}\sum_{t<n} U_t \to B$ with probability one, gap budgets included, as Appendix~\ref{app:theory_controller} proves. Attaining $B$ in expectation with one stationary policy at a gap budget is the job of the endpoint mixture of Definition~\ref{def:pi3}, not of this recursion."""

NEW_PROP = r"""Consider the projected decaying-step recursion~\eqref{eq:dual_update} with finite $w_{\max}$ and step sizes satisfying $\sum_t a_t=\infty$ and $\sum_t a_t^2<\infty$. The schedule in~\eqref{eq:dual_update} satisfies these conditions when $\delta>0$. Assume:
\begin{enumerate}
\item[(i)] The environment, agent family, and target $B$ are stationary, with $\mathbb{E}[U_t\mid w_t]=U(w_t)$ for a fixed usage curve $U$.
\item[(ii)] Per-episode usage is bounded by the episode step cap. Each episode uses an independent environment reset and fresh seed, so $U_t-U(w_t)$ is a martingale difference with bounded conditional second moment.
\item[(iii)] There is a single crossing $w^*\in(0,w_{\max})$, with $U(w)<B$ for $w<w^*$ and $U(w)>B$ for $w>w^*$.
\item[(iv)] Usage stays away from $B$ outside every neighborhood of the crossing: for every $0<\epsilon_1<\epsilon_2$,
\[
\inf\{\,|U(w)-B|:\epsilon_1\le|w-w^*|\le\epsilon_2,\ w\in[0,w_{\max}]\,\}>0.
\]
\end{enumerate}
Then $w_t\to w^*$ almost surely, and hence in probability. Neither continuity nor $U(w^*)=B$ is required. At a gap budget, the weight converges even though $U(w_t)$ need not converge to $B$.

Under the harmonic schedule in~\eqref{eq:dual_update}, the running average of observed usage also converges: $\frac1n\sum_{t<n}U_t\to B$ almost surely, including at gap budgets, as Appendix~\ref{app:theory_controller} proves. This is a time-average result. A single stationary policy with expected usage $B$ at a gap budget requires the endpoint mixture of Definition~\ref{def:pi3}."""

OLD_FRONTIER = r"""Under that fitted comparison, negative $95\%$ intervals exclude zero at eight of eleven distinct budgets, counting Tiger's duplicate once. The cap is slack at seven budgets: every Tiger target, Bandit's three interior targets, and Diagnosis's largest. At these budgets, the reference is the unpenalized SARSOP policy, the estimated unconstrained reward optimum. A gap there combines the cost of spending $B$ with any inefficiency of the family. A predeclared target-matched reference separates the two. Subsidized SARSOP policies, with negative usage penalties, extend the sampled points above the unpenalized usage, and the reference becomes the best sampled mixture whose usage equals $B$ (\texttt{run\_\allowbreak frontier\_\allowbreak target\_\allowbreak reference.py}). Against it, intervals exclude zero at two of eleven distinct budgets on the held-out seeds. Replaying the held-out-fitted mixtures on ten fresh seeds again gives two shortfalls, all at budgets whose held-out cap reference binds. Fresh realized usage need not equal $B$. Only Bandit's gap-budget shortfall, $-0.59$ held out and $-0.50$ fresh, appears on both streams, and its held-out interval just reaches zero when the reference is matched to the mixture's realized usage rather than to $B$ (Appendix~\ref{app:frontier_details}). Diagnosis's held-out shortfall at $B{=}9.53$ mostly pairs a policy on the usage plateau containing $w{=}1$ with the unpenalized SARSOP policy at nearly equal usage. The twenty-seed episode-matched check of Section~\ref{sec:sarsop} finds that pair equivalent within the margin, although on these five held-out seeds it differs by $1.01\pm0.18$. Both references are maxima over noisy sampled points, so selection bias remains."""

NEW_FRONTIER = r"""Against the cap-feasible reference fitted on the held-out stream, negative $95\%$ intervals exclude zero at eight of eleven distinct budgets, counting Tiger's duplicate once. The cap is slack at seven budgets: every Tiger target, Bandit's three interior targets, and Diagnosis's largest. There the reference is the unpenalized SARSOP policy, the estimated unconstrained reward optimum. A reward gap can therefore combine the cost of spending $B$ with inefficiency within the information-weight family.

The predeclared target-matched reference separates these effects by requiring usage equal to $B$. Subsidized SARSOP policies, with negative usage penalties, extend the sampled points above unpenalized usage, and the reference selects the best sampled mixture at $B$ (\texttt{run\_\allowbreak frontier\_\allowbreak target\_\allowbreak reference.py}). Against it, intervals exclude zero at two of eleven distinct budgets on the held-out seeds. Replaying the held-out-fitted mixtures on ten fresh seeds again gives two shortfalls, both where the held-out cap reference binds. Fresh realized usage need not equal $B$.

Only Bandit's gap-budget shortfall appears on both streams: $-0.59$ held out and $-0.50$ fresh. Its held-out interval just reaches zero if the reference is matched to the mixture's realized usage instead of $B$ (Appendix~\ref{app:frontier_details}). Diagnosis's held-out shortfall at $B{=}9.53$ compares a policy on the usage plateau containing $w{=}1$ with unpenalized SARSOP at nearly equal usage. The twenty-seed episode-matched check of Section~\ref{sec:sarsop} finds that pair equivalent within its margin, although on these five held-out seeds it differs by $1.01\pm0.18$. Both references maximize over noisy sampled points, so selection bias remains."""

OLD_TILE = r"""In a separate fixed-$H{=}2$ sweep (Figure~\ref{fig:tw_scaling}), Planning takes no scans at $8{\times}8$ and achieves $1.4\% \pm 0.3$pp success, while EFE achieves $69.4\% \pm 1.0$pp. The short horizon cannot value enough scans to repay their costs before committing on a large grid. The contrast is therefore with a non-scanning finite-horizon agent, not with reward-only planning at arbitrary depth. At $4{\times}4$ and $6{\times}6$ the two are within one SE, with no formal test for that sweep. The advantage appears at a horizon-and-scale threshold rather than widening uniformly with size. Its weighted comparators use fixed $w{=}100$, not class-specific tuning. Random and overlapping scan partitions sharply reduce all agents' absolute performance and do not separate EFE from Planning on reward or success, although EFE uses fewer scans in all three modes. Appendix~\ref{app:tileworld_details} preserves these robustness results and their scope."""

NEW_TILE = r"""A separate sweep at fixed $H{=}2$ exposes a limitation of shallow planning (Figure~\ref{fig:tw_scaling}). Planning uses $15.57$ scans at $6{\times}6$ but none at $8{\times}8$, where its success drops to $1.4\%\pm0.3$pp. EFE still uses $17.50$ scans and reaches $69.4\%\pm1.0$pp. At this depth, Planning cannot value enough scans before commitment on the larger grid. This is a contrast with a non-scanning finite-horizon agent, not reward-only planning at arbitrary depth. At $4{\times}4$ and $6{\times}6$, Planning and EFE are within one SE, with no formal test for this sweep. The advantage thus appears at a horizon-and-scale threshold rather than widening uniformly with size.

The plotted Planning+IG comparator uses fixed $w{=}100$, not class-specific tuning. It reaches $97.8\%$ success at $8{\times}8$ but takes $39.52$ scans and earns $-30.84$, against EFE's $-25.86$ reward. Random and overlapping scan partitions sharply reduce all agents' absolute performance and do not separate EFE from Planning on reward or success, although EFE uses fewer scans in all three modes. Appendix~\ref{app:tileworld_details} preserves these robustness results and their scope."""


for path in (ROOT / "paper/full_paper_jair.tex", ROOT / "paper/full_paper.tex"):
    text = path.read_text()
    text = once(text, OLD_PROP, NEW_PROP)
    text = once(text, OLD_FRONTIER, NEW_FRONTIER)
    text = once(text, OLD_TILE, NEW_TILE)
    path.write_text(text)
    print(f"{path.name}: proposition, frontier, Tileworld clarified")
