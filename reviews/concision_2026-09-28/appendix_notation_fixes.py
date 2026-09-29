"""Guarded notation corrections applied to each assembled manuscript.

No live master or legacy source is modified by importing this module.  All
replacements are source-level descriptions of existing mathematics or code.
"""


def apply(source: str) -> str:
    def replace(old: str, new: str, expected: int = 1) -> None:
        nonlocal source
        found = source.count(old)
        if found != expected:
            raise ValueError(
                f"appendix notation replacement expected {expected} matches, "
                f"found {found}: {old!r}"
            )
        source = source.replace(old, new)

    # w multiplies information to produce reward; eta=I_max/c has reciprocal units.
    replace(r"$1.44$ nats", r"$1.44$ reward units per nat", expected=4)
    replace(r"$28.9$ nats", r"$28.9$ reward units per nat")
    replace(
        r"$w^*_{\mathrm{hi}} \approx 1.01$ nats",
        r"$w^*_{\mathrm{hi}} \approx 1.01$ reward units per nat",
    )
    replace(r"($\eta$ in nats)", r"($\eta$ in nats per reward unit)")
    replace(
        r"Thresholds in nats.",
        r"The thresholds are in reward units per nat. $w^*_{\mathrm{ret}}$ is in the implementation's reward units per bit.",
    )
    replace(
        r"equivalently $4.97$ and $10.89$ nats",
        r"equivalently $4.97$ and $10.89$ reward units per nat",
    )

    # Expected information gain averages over prospective observations.
    replace(
        r"$\tilde{I}_a(b) = D_{\mathrm{KL}}\!\big[Q(s_{\mathrm{rel}} \mid o, a) \,\|\, Q(s_{\mathrm{rel}} \mid a)\big]$",
        r"$\tilde{I}_a(b) = \mathbb{E}_{o\sim Q(\cdot\mid b,a)} D_{\mathrm{KL}}\!\big[Q(s_{\mathrm{rel}} \mid b,o,a) \,\|\, Q(s_{\mathrm{rel}} \mid b,a)\big]$",
    )
    replace(
        "here written as the divergence between the posterior and prior over",
        "here written as the expected divergence between the posterior and prior over",
    )

    # Percentages use the magnitude of a possibly negative reward reference.
    replace(
        r"Gap is $R_{\mathrm{ref}}-R_{\mathrm{EFE}}$, not a certified optimality gap.",
        r"Gap is $R_{\mathrm{ref}}-R_{\mathrm{EFE}}$, and Gap \% is $100(R_{\mathrm{ref}}-R_{\mathrm{EFE}})/|R_{\mathrm{ref}}|$. Neither is a certified optimality gap.",
    )
    # Recovery runner returns the first start index, not the hold's completion.
    replace(
        r"where $180$ is the last post-rescale index at which that hold can be checked.",
        r"where $T$ is the zero-based post-rescale index at the start of the first qualifying hold and $180$ is the last admissible start index.",
    )
    # run_nearopt_horizon.py:94--98 compares reward quantities, not a
    # dimensionless percentage directly with an absolute reward tolerance.
    replace(
        r"we computed the reward-optimal weight $w^*$ by grid search and recorded whether $w{=}1$ falls within $\max(5\%, 0.5)$ of the best achievable reward.",
        r"we selected the weight $w^*_{\mathrm{ret}}$ with the largest estimated mean reward on the grid and recorded whether its estimated reward advantage over $w{=}1$ is at most $\max(0.05|\widehat R_{\mathrm{best}}|,0.5)$, where $\widehat R_{\mathrm{best}}$ is that largest estimated mean and $0.5$ is measured in reward units.",
    )
    replace(
        r"and $w^*$ is selected over the six-point grid",
        r"and $w^*_{\mathrm{ret}}$ is selected over the six-point grid",
    )
    replace(
        r"when that gap is within $\max(5\%, 0.5)$ of the best reward.",
        r"when that gap is at most $\max(0.05|\widehat R_{\mathrm{best}}|,0.5)$, where $\widehat R_{\mathrm{best}}$ is the largest estimated mean reward on the grid and $0.5$ is measured in reward units.",
    )

    # A reward dependency is not an observation channel in this model.
    replace(
        "Every observation model in the environment (condition tests, the distractor test, and the terminal commit reward) is constructed to depend on exactly one of the two factors.",
        "Each observation likelihood, for a condition test or the distractor test, depends on exactly one of the two factors. Terminal commit rewards depend only on the condition and are not observations.",
    )

    # The generic categorical scores are averaged over binary components for
    # Inspection: benchmark.py:330--331 and scoring.py:46--69.
    replace(r"the log score ($\log b(s^\star)$", r"the log score ($\ln b(s^\star)$")
    replace(
        r"the Brier score ($\sum_s (b(s) - \mathbb{1}[s=s^\star])^2$). These scores assess",
        r"the Brier score ($\sum_s (b(s) - \mathbb{1}[s=s^\star])^2$), where $s^\star$ is the true state. For Structural Inspection, each rule is applied to each component's binary belief and true fault status, then averaged over components. Its reported score is not a joint-state score. The implementation floors the probability used in the log score at $10^{-12}$ to keep numerical output finite. These scores assess",
    )

    # A zero posterior-divergence diagnostic does not imply state preservation.
    replace(
        r"For any action $a$ that violates Definition~\ref{def:factored}'s state-preserving hypothesis ($\Delta_T(b,a) \neq 0$),",
        r"For an action $a$ that violates Definition~\ref{def:factored}'s state-preserving hypothesis, $\Delta_T(b,a)$ may be nonzero. For such an action,",
    )
    replace(
        r"(those with $\Delta_T \equiv 0$ on information-gathering actions)",
        r"(those whose information-gathering and navigation actions preserve the hidden state)",
    )
    replace(
        r"The coupling term $\Delta_T$ itself is a diagnostic of when the factored hypothesis fails, and we have not shown it to be an additive correction to the EFE value or a bound on decision error.",
        r"A nonzero $\Delta_T$ witnesses failure of the state-preserving hypothesis, but a zero value alone does not establish state preservation. We have not shown this diagnostic to be an additive correction to the EFE value or a bound on decision error.",
    )
    replace(
        r"\textbf{Factored} ($\Delta_T{=}0$) & \textbf{Non-factored} ($\Delta_T{\neq}0$)",
        r"\textbf{Preserves hidden state} & \textbf{May change hidden state}",
    )
    replace(
        "The factored observation structure is common in practice whenever the quantity being measured is static or slow-changing relative to the decision horizon",
        "The factored observation structure models settings where the measured quantity is static over the decision horizon",
    )

    return source
