"""Guarded, mirrored prose clarifications for the 2026-10-02 clarity review."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MASTERS = [ROOT / "paper/full_paper_jair.tex", ROOT / "paper/full_paper.tex"]


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise ValueError(f"Expected one occurrence, got {count}: {old[:100]!r}")
    return text.replace(old, new, 1)


REPLACEMENTS = [
    (
        r"For a family of policies indexed by information weight $w$, let $U(w)$ be the expected sensing usage. We call the weight at which this curve crosses $B$ its \emph{operational shadow price}, $w^*(B)$. The adjective operational matters: this price is read from a usage curve, rather than obtained as the Lagrange multiplier of a usage-cap constraint. The curve can have plateaus, jumps, and non-monotone portions. A finite grid therefore estimates a crossing by a bracket. When the selected endpoint policies straddle a usage gap, a per-episode mixture can attain the target in expectation under the conditions of Definition~\ref{def:pi3}. The crossing threshold, its grid bracket, and this randomized policy are distinct objects.",
        r"For each information weight $w$, let $U(w)$ be the expected number or cost of sensing actions under the resulting policy. We seek a policy with usage $B$, but $U(w)$ can jump over that target, stay flat, or cross it more than once. We call its final crossing threshold the \emph{operational shadow price}, $w^*(B)$. This price is read from the usage curve. It is not the Lagrange multiplier of a problem that maximizes reward under a usage cap. A finite weight grid brackets the crossing. If the selected endpoint policies straddle $B$, a per-episode mixture can meet it in expectation under Definition~\ref{def:pi3}. The threshold, bracket, and randomized policy are distinct objects.",
    ),
    (
        "\\end{figure}\n\n\n\nThe price has a useful response",
        "\\end{figure}\n\nThe price has a useful response",
    ),
    (
        "This is a $\\rho$-POMDP Bellman recursion with an action-dependent belief utility, as permitted by \\citet{araya2010}.\n\n\\begin{proposition}",
        "This is a $\\rho$-POMDP Bellman recursion with an action-dependent belief utility, as permitted by \\citet{araya2010}. The proposition identifies the two recursions when $\\beta=1$ fixes the exchange rate at one reward unit per nat of log preference. A separately normalized preference distribution needs the qualification following the proof.\n\n\\begin{proposition}",
    ),
    (
        "The second bounds a near-optimality interval under the proposition's symmetric two-state assumptions.",
        "The second bounds a single-observation interval under the proposition's symmetric two-state assumptions. When the first threshold is positive, immediate commitment is reward-optimal and buying that observation has the reward cost stated in the proposition.",
    ),
    (
        r"The single observe-or-commit decision does admit an exact usage threshold. In this corollary and its onset checks, we write $w_{\mathrm{thresh}}$ for the $w^*_{\mathrm{thresh}}$ of Proposition~\ref{prop:nearopt}, dropping the star to distinguish it from $w^*(B)$.",
        r"For a single observe-or-commit decision, the usage curve has an exact onset. Consider the symmetric two-state setting of Proposition~\ref{prop:nearopt}: the prior is uniform, the observation is correct with probability $p$, it costs $c$, and correct and incorrect commits pay $R^+$ and $R^-$. With information measured in nats, $I_{\max}=\ln 2+p\ln p+(1-p)\ln(1-p)$, using $0\ln0=0$. The observation starts to be selected above $w_{\mathrm{thresh}}=[c-(p-\tfrac12)(R^+-R^-)]/I_{\max}$. Here $w_{\mathrm{thresh}}$ abbreviates that proposition's $w^*_{\mathrm{thresh}}$. It is distinct from the budget-dependent crossing threshold $w^*(B)$.",
    ),
    (
        r"\begin{corollary}[Proposition~\ref{prop:nearopt}'s onset thresholds are usage-staircase knots]",
        r"\begin{corollary}[Single-observation threshold and usage onset]",
    ),
    (
        r"In the two-state $H{=}1$ setting of Proposition~\ref{prop:nearopt} with $w_{\mathrm{thresh}} \geq 0$, equivalently $c \geq (p - \tfrac{1}{2})(R^+ - R^-)$, for any budget $B \in (0,1)$ the crossing threshold of Definition~\ref{def:pi3} is exactly $w_{\mathrm{thresh}}$, the weight at which the staircase leaves zero, and the closed enclosure $[w_{\mathrm{lo}}, w_{\mathrm{hi}}]$ of a finite-grid crossing bracket contains that threshold whenever the sampled usages straddle $B$, locating it to grid resolution rather than equalling it. When $w_{\mathrm{thresh}} < 0$ every nonnegative weight already observes, so $U \equiv 1$ on $[0,\infty)$ and no onset knot lies in the nonnegative range. The onset boundary of the budgeted problem recovers Proposition~\ref{prop:nearopt}'s closed form as the first knot of the usage staircase.",
        r"In the two-state $H{=}1$ setting of Proposition~\ref{prop:nearopt}, suppose $w_{\mathrm{thresh}}\geq0$, equivalently $c\geq(p-\tfrac12)(R^+-R^-)$. For every $B\in(0,1)$, the crossing threshold of Definition~\ref{def:pi3} is $w_{\mathrm{thresh}}$: the point where usage leaves zero. If sampled usages straddle $B$, the closed enclosure $[w_{\mathrm{lo}},w_{\mathrm{hi}}]$ of their finite-grid bracket contains that threshold. The bracket locates the threshold only to grid resolution. If $w_{\mathrm{thresh}}<0$, every nonnegative weight already observes, so $U\equiv1$ on $[0,\infty)$ and there is no onset knot in that range.",
    ),
    (
        "Figure~\\ref{fig:collapse} shows the result in raw and normalized coordinates. Every matched $w/\\alpha$ point agrees bit-exactly on Diagnosis, Bandit, Tiger, and Tileworld. Shared per-episode random streams make exact empirical agreement possible when actions coincide. These CSVs are byte-identical under an absolute comparison tolerance in place of the relative one of Section~\\ref{sec:pi1}, which does not bind at these points.",
        "Figure~\\ref{fig:collapse} shows how the raw crossing brackets move with scale and how the three Diagnosis curves coincide when weight is divided by $\\alpha$. Every matched $w/\\alpha$ point agrees bit-exactly on Diagnosis, Bandit, Tiger, and Tileworld. Shared per-episode random streams make exact empirical agreement possible when actions coincide. A separate rerun with the former absolute tie tolerance produced byte-identical CSVs, so the tolerance change did not affect these measured points.",
    ),
    (
        "The observe-then-commit domains and the smaller Inspection instance now receive the same treatment as the interleaved instances.",
        "We estimate usage staircases for the observe-then-commit domains and the smaller Inspection instance using the same crossing procedure.",
    ),
    (
        "where $U_{\\min}$ and $U_{\\max}$ are the endpoints of each curve's usage range",
        "where $U_{\\min}$ and $U_{\\max}$ are the smallest and largest usages sampled on each weight grid",
    ),
    (
        "showing local non-monotonicity from discrete policy switches, the first of the two obstacles noted after Proposition~\\ref{prop:pi2}.",
        "showing local non-monotonicity from discrete policy switches. A final crossing bracket can therefore hide earlier crossings.",
    ),
    (
        "\\section{Results}\n\\label{sec:results}",
        "\\section{Results for the Information-Unit Weight}\n\\label{sec:results}",
    ),
    (
        "RockSample corrects within metric, with $21$ comparisons per instance over seven agents. Pooling metrics would loosen its non-rejection-based bolding rule.",
        "RockSample corrects within metric, with $21$ comparisons per instance over seven agents. A single correction across metrics would use a larger family, reject fewer differences, and could bold more rows under the table's non-rejection rule. Bolding does not assert equality.",
    ),
    (
        "\\textbf{Part (b) ($H{=}2$ near-optimality interval).}",
        "\\textbf{Part (b) ($H{=}2$ single-observation interval).}",
    ),
    (
        "We call this the near-optimality interval.",
        "We call this the single-observation interval.",
    ),
    (
        "Only the projected decaying-step variant specified in Section~\\ref{sec:pi5} is covered below. It is implemented",
        "The proof has two steps: a squared-distance argument establishes convergence of the weight, and the eventual absence of projection gives convergence of average observed usage. Only the projected decaying-step variant specified in Section~\\ref{sec:pi5} is covered below. It is implemented",
    ),
    (
        "The observed-sensor mask augments the planning state. At belief $b$, the one-observation acquisition value for an unobserved sensor $j$ is\n\\[",
        "The observed-sensor mask augments the planning state. Let $Y$ denote gas identity and $Z_j$ the encoded category of sensor $j$. At belief $b$, $P(z\\mid b,j)$ predicts that sensor's next category, and $b(y\\mid z,j)$ is the posterior class probability after observing it. Stopping has value $\\max_y b(y)$. The value of acquiring an unobserved sensor $j$ and then stopping is\n\\[",
    ),
    (
        "Here $Y$ is gas identity and $Z_j$ is the sensor category. Information is measured in bits, and the stopping value is $\\max_y b(y)$. This is the $H=1$",
        "Information is measured in bits. This is the $H=1$",
    ),
]


for path in MASTERS:
    source = path.read_text()
    edited = source
    for old, new in REPLACEMENTS:
        edited = replace_once(edited, old, new)
    path.write_text(edited)
    print(f"{path.name}: {len(REPLACEMENTS)} guarded prose edits")
