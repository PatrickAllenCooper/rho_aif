"""Apply the matched, meaning-preserving naturalness pass to both masters.

Each source phrase must occur exactly once in each master. This file records the
edits for audit; it is not part of manuscript production or the experiment suite.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MASTERS = [ROOT / "paper/full_paper_jair.tex", ROOT / "paper/full_paper.tex"]

REPLACEMENTS = [
    (
        "the amount of observation the agent is expected to use before committing",
        "the amount of sensing the agent is expected to use before committing",
    ),
    (
        "Four properties make this price usable in practice. It can be computed offline and tracked online. It rescales in step with the rewards, and where the usage curve jumps over the budget it is reported as a crossing bracket together with a mixture that attains the budget in expectation.",
        "Four properties make this price useful in practice. It can be estimated offline, tracked online, and rescaled with rewards. When the usage curve jumps over a budget, a crossing bracket estimates the price and an endpoint mixture can attain the budget in expectation.",
    ),
    (
        "A budget that falls inside one of the staircase's jumps is met exactly by no single weight.",
        "No single weight exactly meets a budget inside a staircase jump.",
    ),
    (
        "What the log-scoring derivation supplies is a principled anchor within that unavoidable choice rather than an escape from it.",
        "The log-scoring derivation supplies a principled anchor for that choice.",
    ),
    (
        "Both belong to the agent's one generative model in the active-inference convention",
        "Both belong to the same generative model in the active-inference convention",
    ),
    (
        "Their pragmatic term is still well defined, but the outcome it scores is not a fresh observation.",
        "The pragmatic term for a commit is still well defined, but it does not score a fresh observation.",
    ),
    (
        "The two routes express the same identification up to the preference normalizer, within the reward-based recursion the implementation uses, and what otherwise separates them is whether its scale is declared.",
        "Within the implementation's reward-based recursion, the two routes express the same identification up to the preference normalizer. They differ in whether the reward scale is stated explicitly.",
    ),
    (
        "The summary is that none of them supplies an operational sensing budget",
        "None of them supplies an operational sensing budget",
    ),
    (
        "On all three environments the envelope is a single sampled policy rather than a mixture, the $\\lambda{=}0$ policy on Tiger and Bandit and the $\\lambda{=}0.05$ policy on Diagnosis, because on each the sampled policy with the largest reward anywhere on its frontier is itself feasible at $B_{\\mathrm{EFE}}$",
        "On all three environments the envelope selects a single sampled policy rather than a mixture: the $\\lambda{=}0$ policy on Tiger and Bandit, and the $\\lambda{=}0.05$ policy on Diagnosis. In each case the highest-reward sampled policy on the frontier is itself feasible at $B_{\\mathrm{EFE}}$",
    ),
    (
        "Read together with Table~\\ref{tab:sarsop}'s TOST result, the two comparisons say complementary things.",
        "The TOST result in Table~\\ref{tab:sarsop} and the constrained reference answer different questions.",
    ),
    (
        "The constrained reference adds a second statement, made at the sensing level this agent actually spends, the usage-matched budget $B_{\\mathrm{EFE}}$.",
        "The constrained reference compares rewards at the sensing level EFE actually uses, $B_{\\mathrm{EFE}}$.",
    ),
    (
        "A designer would state a budget from outside.",
        "In an application, the designer would set the budget independently of the weight-one policy.",
    ),
    (
        "It bites at the $0.25$ budget of $5.51$",
        "It changes the reported bracket at the $0.25$ budget of $5.51$",
    ),
    (
        "The first question has a clean answer. ",
        "",
    ),
    (
        "The mixture's held-out mean usage exceeds $B$ on three of the twelve budgets, by at most $0.13$ observations, which is what targeting an expectation on a finite sample looks like, and a designer who needs a hard per-episode cap needs a different mechanism.",
        "The mixture's held-out mean usage exceeds $B$ on three of the twelve budgets, by at most $0.13$ observations. Such deviations are possible when targeting a population expectation with a finite sample. A designer who needs a hard per-episode cap needs a different mechanism.",
    ),
    (
        "The procedure calibrates expected usage within a family. It does not maximize reward under a cap, and the study puts a number on the difference.",
        "The procedure calibrates expected usage within a family. It does not maximize reward under a cap, and the study quantifies the difference.",
    ),
    (
        "The practical message is that under a shared reward convention, active inference supplies an untuned information-unit weight that is a strong default, without any claim of scale-free calibration or uniform optimality, that a success-tuned higher weight still buys accuracy where near-certain commits are required, and that, when an expected sensing usage is the intended design requirement, a stated sensing budget is the way to move off that default.",
        "Under a shared reward convention, active inference supplies an untuned information-unit weight that is a strong default, though neither scale-free nor uniformly optimal. A higher, success-tuned weight can buy accuracy where near-certain commits are required. When the design requirement is expected sensing usage, a stated budget provides a way to move off the default.",
    ),
    (
        "A high-testing level (9.68 observations, 97.4\\% success) at mismatch $\\in \\{-0.10, -0.05, 0.00\\}$, and a low-testing level (5.86 observations, 88.7\\% success) at mismatch $\\in \\{-0.15, +0.05, +0.10\\}$.",
        "The high-testing level (9.68 observations, 97.4\\% success) occurs at mismatch $\\in \\{-0.10, -0.05, 0.00\\}$. The low-testing level (5.86 observations, 88.7\\% success) occurs at mismatch $\\in \\{-0.15, +0.05, +0.10\\}$.",
    ),
    (
        "We do not have a mechanistic account of why the transition sits precisely where it does and report the pattern descriptively rather than explain it.",
        "We report the pattern without assigning a mechanism to the precise transition point.",
    ),
    (
        "The resulting binary is not committed. The patch script is.",
        "The resulting binary is not committed, but the patch script is.",
    ),
    (
        "This is a consistency check, not a certified numerical equivalence, and we state its strength precisely rather than leaving ``validated'' to do unearned work.",
        "This is a consistency check, not a certified numerical equivalence.",
    ),
    (
        "The same measurement on RockSample[7,8] fails informatively.",
        "The RockSample[7,8] reference calculation instead exposes a limitation.",
    ),
    (
        "One caveat about what a penalty sweep can certify belongs before the protocol, and it needs two terms.",
        "Two definitions clarify what a penalty sweep can certify.",
    ),
    (
        "The same undershoot cuts the other way for the optimality comparison. ",
        "",
    ),
    (
        "The boundary of what this fixes matters as much as the fix. ",
        "",
    ),
    (
        "Tying Planning costs EFE nothing against the tuned Planning+IG alternative. ",
        "",
    ),
    (
        "With the family's distance from near-optimal reward now measured at the endogenous budget, the next subsection moves to target budgets set by a predeclared rule from the calibration curve rather than by the weight-one usage, and there the question changes. It is no longer how close the family comes to near-optimal reward but whether calibration meets a stated expected usage on held-out seeds, and at what reward.",
        "The next subsection evaluates target budgets set by a predeclared rule from the calibration curve rather than by weight-one usage. It asks whether calibration meets those expected-usage targets on held-out seeds and what reward it earns.",
    ),
    (
        "The Tileworld adds a third condition,",
        "Tileworld adds a third condition,",
    ),
    (
        "The Tileworld projects the Diagnosis partition structure onto a 2D grid.",
        "Tileworld projects the Diagnosis partition structure onto a 2D grid.",
    ),
    (
        "On every one of the twelve attainable budgets the endpoint mixture meets its expected-usage target",
        "At all twelve attainable budgets, the endpoint mixture meets its expected-usage target",
    ),
]

# These second-pass edits retain the useful connective prose while repairing
# awkward phrasing. They follow the first list when replayed from the baseline.
REFINEMENTS = [
    (
        "The log-scoring derivation supplies a principled anchor for that choice.",
        "The log-scoring derivation gives a principled anchor within this unavoidable choice of units, while leaving the reward convention itself to the designer.",
    ),
    (
        "None of them supplies an operational sensing budget",
        "None of these approaches gives a designer an operational sensing budget",
    ),
    (
        "The TOST result in Table~\\ref{tab:sarsop} and the constrained reference answer different questions.",
        "Read together, the TOST result in Table~\\ref{tab:sarsop} and the constrained reference illuminate two distinct aspects of the comparison.",
    ),
    (
        "At all twelve attainable budgets, the endpoint mixture meets",
        "The held-out usage results answer the first question directly. At all twelve attainable budgets, the endpoint mixture meets",
    ),
    (
        "and the study quantifies the difference.",
        "and the study measures how large that difference is.",
    ),
    (
        "Under a shared reward convention, active inference supplies an untuned information-unit weight that is a strong default, though neither scale-free nor uniformly optimal. A higher, success-tuned weight can buy accuracy where near-certain commits are required. When the design requirement is expected sensing usage, a stated budget provides a way to move off the default.",
        "Under a shared reward convention, active inference supplies an untuned information-unit weight that serves as a strong default in the tested settings; it promises neither scale-free calibration nor uniform optimality. A higher weight tuned for success can buy accuracy where near-certain commits are required, at the reward cost shown by the sweep. When expected sensing usage is the design requirement, stating a budget and calibrating the corresponding weight gives the engineer an operating point away from that default.",
    ),
    (
        "This is a consistency check, not a certified numerical equivalence.",
        "This comparison checks consistency between implementations; it does not certify numerical equivalence, so the evidence below is stated in terms of the behaviors actually compared.",
    ),
    (
        "Two definitions clarify what a penalty sweep can certify.",
        "Before presenting the protocol, two definitions clarify what a penalty sweep can and cannot certify.",
    ),
    (
        "Conservative here refers to frontier achievability alone. A reference that undershoots",
        "Conservative here refers to frontier achievability alone. For an optimality comparison, however, an underestimated reference has the opposite effect. A reference that undershoots",
    ),
    (
        "At the two largest weights the relevance-weighted agent still runs",
        "Relevance weighting also has a limit that matters here. At the two largest weights the relevance-weighted agent still runs",
    ),
    (
        "With no weight selection at all, EFE reaches within a fraction",
        "The exact tie with Planning does not itself describe EFE's relation to the tuned Planning+IG alternative. With no weight selection at all, EFE reaches within a fraction",
    ),
    (
        "The next subsection evaluates target budgets set by a predeclared rule from the calibration curve rather than by weight-one usage. It asks whether calibration meets those expected-usage targets on held-out seeds and what reward it earns.",
        "The comparison at $B_{\\mathrm{EFE}}$ measures the family's distance from near-optimal reward at the endogenous weight-one usage. The next subsection moves to budgets set by a predeclared rule from the calibration curve, independently of weight-one usage. It asks whether calibration meets those expected-usage targets on held-out seeds and what reward it earns.",
    ),
]


def main() -> None:
    updates = {}
    for path in MASTERS:
        text = path.read_text()
        for old, new in [*REPLACEMENTS, *REFINEMENTS]:
            count = text.count(old)
            if count != 1:
                raise ValueError(f"{path}: expected one instance, found {count}: {old[:70]}")
            text = text.replace(old, new)
        updates[path] = text
    for path, text in updates.items():
        path.write_text(text)
        print(f"{path}: applied {len(REPLACEMENTS)} edits and {len(REFINEMENTS)} refinements")


if __name__ == "__main__":
    main()
