#!/usr/bin/env python3
"""Apply the final-panel edit batch identically to both live masters.

Every replacement must match exactly once in each target file, or the whole
batch aborts before anything is written.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JAIR = ROOT / "paper" / "full_paper_jair.tex"
LNCS = ROOT / "paper" / "full_paper.tex"
BOTH = (JAIR, LNCS)

EDITS = [
    # G1 notation: w*(B) is the crossing threshold; the bracket estimates it; hat-w is the nearest grid point.
    ("abstract-crosses", BOTH,
     "the weight at which the agent's expected sensing usage meets $B$",
     "the weight at which the agent's expected sensing usage crosses $B$"),
    ("intro-crosses", BOTH,
     "$w^*(B)$, the weight at which the agent's expected usage meets $B$. Where the usage curve jumps over $B$, so that no single weight meets it exactly, the price is still the one weight at which expected usage crosses $B$,",
     "$w^*(B)$, the weight at which the agent's expected usage crosses $B$. Where the usage curve jumps over $B$, so that no single weight meets it exactly, the price is still that one crossing weight,"),
    ("sec41-solving", BOTH,
     "Solving $U(w) = B$ for $w$ gives the operational shadow price $w^*(B)$, the weight that spends about $B$ units of sensing.",
     "Locating the weight at which $U(w)$ crosses $B$, in the sense Definition~\\ref{def:pi3} makes precise, gives the operational shadow price $w^*(B)$, the weight that spends about $B$ units of sensing."),
    ("def-price-is-threshold", BOTH,
     "At a jump of the curve the threshold is a single number, the location of the jump, even though the level set is empty there. Third, the \\emph{crossing bracket} $w^*(B) = (w_{\\mathrm{lo}}, w_{\\mathrm{hi}}]$ is the finite-grid estimate",
     "At a jump of the curve the threshold is a single number, the location of the jump, even though the level set is empty there. The operational shadow price of this article is this threshold, $w^*(B) := w^{\\dagger}(B)$, defined wherever the threshold is. Third, the \\emph{crossing bracket} $(w_{\\mathrm{lo}}, w_{\\mathrm{hi}}]$ is the finite-grid estimate"),
    ("def-fallback-threshold-exists", BOTH,
     "flagged as unbracketed, as it also does when the final grid point falls back below $B$.",
     "flagged as unbracketed, as it also does when the final grid point falls back below $B$, a case in which the threshold itself can still exist, since the solver's bracket needs a grid weight at or above $B$ after the last grid weight below it."),
    ("sec44-hat-w", BOTH,
     "we solve $w^*(B)$ by grid search minimizing $|U - B|$ and report the crossing bracket rather than a bisection root.",
     "we estimate $w^*(B)$ on the grid and report the crossing bracket rather than a bisection root, together with the grid weight minimizing $|U - B|$, written $\\hat{w}(B)$, which is the point the staircase figures mark and which can sit on the bracket's lower edge or, at a slack budget, below it."),
    ("sec45-bracket-for", BOTH,
     "A bracket $w^*(B)$ computed at one reward scale",
     "A bracket for $w^*(B)$ computed at one reward scale"),
    ("stairs-caption-markers", BOTH,
     "so the nearest-point solution returns a weight below the bracket while the dotted bar still marks the crossing. The usage curves behind Tiger,",
     "so the nearest-point solution returns a weight below the bracket while the dotted bar still marks the crossing. Every marker plots that nearest-point solution $\\hat{w}(B)$, which can also sit on a bracket's lower edge. The usage curves behind Tiger,"),
    ("interleaved-caption-markers", BOTH,
     "here $w{=}0$ on the lowest RockSample[5,3] budget). The underlying usage curves",
     "here $w{=}0$ on the lowest RockSample[5,3] budget). Every marker plots the nearest-point solution $\\hat{w}(B)$, which can sit on a bracket's lower edge. The underlying usage curves"),
    # F1 Proposition PI-5: the running average of usage does converge to B.
    ("pi5-statement-average", BOTH,
     "The usage at the limit is $U(w^*)$, one side of the jump, and neither the expected usage at $w_t$ nor its time average is guaranteed to converge to $B$. Attaining $B$ in expectation at a gap budget is the job of the endpoint mixture of Definition~\\ref{def:pi3}, not of this recursion.",
     "The usage at the limit is $U(w^*)$, one side of the jump, so the expected usage at $w_t$ need not converge to $B$. Its running average does converge to $B$, $\\frac{1}{n}\\sum_{t<n} U_t \\to B$ with probability one, gap budgets included, as the proof below shows. Attaining $B$ in expectation with one stationary policy at a gap budget is the job of the endpoint mixture of Definition~\\ref{def:pi3}, not of this recursion."),
    ("pi5-proof-kronecker", BOTH,
     "whose limit points are the stationary points of the projected dynamics, which under (iii) reduce to $w^*$ when $w^*$ is interior.",
     "whose limit points are the stationary points of the projected dynamics, which under (iii) reduce to $w^*$ when $w^*$ is interior. The running-average claim follows from that convergence. Because $w^*$ is interior and the increments $a_t (B - U_t)$ vanish, usage being bounded by (ii), the projection is inactive from some episode on, so $\\sum_t a_t (B - U_t)$ converges, its partial sums being differences of the convergent iterates. Since $1/a_t = (1 + \\delta t)/\\eta_0$ increases to infinity, Kronecker's lemma gives $a_n \\sum_{t<n} (B - U_t) \\to 0$, and because $n\\,a_n \\to \\eta_0/\\delta > 0$ this is $\\frac{1}{n}\\sum_{t<n} (B - U_t) \\to 0$ almost surely."),
    # G2 Figure 4 caption direction.
    ("fig4-caption-direction", BOTH,
     "median trajectory with interquartile band, dropping after the rescale invalidates the pre-rescale weight and climbing back as the controller re-adapts.",
     "median trajectory with interquartile band, falling from its initial value to about $0.3$ within the first few dozen episodes, holding there until the rescale invalidates it, and then climbing about tenfold, to about $2.7$, as the controller re-adapts."),
    ("fig4-caption-targets", BOTH,
     "against the dashed budget line $B{=}8$ the controller tracks.",
     "against the dashed budget line $B{=}8$ the controller targets."),
    # G3 hero Description sign (JAIR carries the Description).
    ("hero-description-sign", (JAIR,),
     "written as G of pi equals a pragmatic term plus an epistemic term,",
     "written as G of pi equals a pragmatic term minus an epistemic term,"),
    # S1 TOST chronology.
    ("tost-fixed-margin-intro", BOTH,
     "We therefore formalize the comparison with a predeclared-margin two one-sided tests (TOST) procedure",
     "We therefore formalize the comparison with a fixed-margin two one-sided tests (TOST) procedure"),
    ("tost-chronology", BOTH,
     "which is $\\pm 1.0$ reward for Tiger and Diagnosis and $\\pm 0.5$ for Bandit. It was fixed before these samples were inspected. It is an operational margin",
     "which is $\\pm 1.0$ reward for Tiger and Diagnosis and $\\pm 0.5$ for Bandit, a value fixed by each environment's own cost parameter. The test itself was added after an earlier comparison of the same two policies on the same canonical seeds, one without any equivalence test, had already been reported, so the margin was chosen with that comparison known and the five-seed test is retrospective rather than prospectively predeclared. The fifteen seeds that the $n{=}20$ robustness study below adds to the canonical five were fixed before that study was run, after the margin, and are the prospective part of this evidence. It is an operational margin"),
    ("tost-within-margin-sarsop", BOTH,
     "is therefore statistically equivalent to the SARSOP reference within the predeclared margin on this suite",
     "is therefore statistically equivalent to the SARSOP reference within the fixed margin on this suite"),
    ("tost-within-margin-cpomdp", BOTH,
     "is statistically equivalent, within the predeclared margin, to a near-optimal policy's reward",
     "is statistically equivalent, within the fixed margin, to a near-optimal policy's reward"),
    ("tost-abstract", (JAIR,),
     "is statistically equivalent to SARSOP by a predeclared-margin equivalence test on the three core environments.",
     "is statistically equivalent to SARSOP by a fixed-margin equivalence test on the three core environments."),
    ("tost-contrib", BOTH,
     "by the two one-sided tests (TOST) procedure at the predeclared sensing-cost margin,",
     "by the two one-sided tests (TOST) procedure at a fixed sensing-cost margin,"),
    ("tost-conclusion", BOTH,
     "It is statistically equivalent to SARSOP by a predeclared-margin TOST on the three core environments,",
     "It is statistically equivalent to SARSOP by a fixed-margin TOST on the three core environments,"),
    ("tost-checklist", (JAIR,),
     "is additionally backed by a predeclared-margin TOST equivalence test",
     "is additionally backed by a fixed-margin TOST equivalence test"),
    # S3 single tuning stream.
    ("tuning-seed", BOTH,
     "because its computational cost per episode is an order of magnitude higher than that of the other observe-then-commit environments. This tuned baseline weight",
     "because its computational cost per episode is an order of magnitude higher than that of the other observe-then-commit environments. Every grid point is evaluated on one common tuning stream, seed $7$, disjoint from the five evaluation seeds and reset for each candidate so that candidates face the same episodes, and ties go to the smallest weight reaching the maximum (\\texttt{tune\\_info\\_gain\\_weight} in \\texttt{experiments/run\\_experiment.py}). Each tuned weight is therefore a selection on one stream of $200$ or $100$ episodes and carries that stream's sampling noise. Seed $7$ is also the first held-out seed of Section~\\ref{sec:budget_frontier}, which evaluates only the calibrated family and never a tuned baseline. This tuned baseline weight"),
    ("tuning-seed-checklist", (JAIR,),
     "Deviations are stated where they occur. The principal ones are three seeds for the reward-rescaling sweep,",
     "Deviations are stated where they occur. The principal ones are the single tuning stream, seed $7$, on which the tuned baseline weights of Table~\\ref{tab:agents} are selected, three seeds for the reward-rescaling sweep,"),
    # F3 selection bias.
    ("from-below-selection", BOTH,
     "it can only estimate the constrained optimum from below, up to its own sampling error, so any measured gap to it understates the gap to the optimum.",
     "it can only estimate the constrained optimum from below, up to its own sampling error and the upward selection bias of taking a maximum over noisy sampled points, so any measured gap to it understates the gap to the optimum up to those two effects."),
    # F4 Table 6 weights.
    ("table6-weights", BOTH,
     "Planning+IG at the usage-matched weight $w^*$ (not $w{=}1$, but $w^*{=}0.00$, $0.45$, and $1.07$ for Tiger, Diagnosis, and Bandit respectively) attained reward bit-identical to EFE's",
     "Planning+IG at the usage-matched grid weight actually run (not $w{=}1$, but $0.00$, $0.45$, and $1.07$ for Tiger, Diagnosis, and Bandit respectively, each the nearest grid point on a lighter usage curve rather than a bracket, and each lying inside a range of sampled weights over which the shadow-price usage curve of \\texttt{results\\_price\\_usage\\_curves.csv} takes the same value as at $w{=}1$) attained reward bit-identical to EFE's"),
]

FRONTIER_OLD = (
    "On Tiger the mixture's reward is $0.34$ above the envelope at the smallest budget and $0.05$ and $0.36$ below it at the two larger ones. "
    "These ratios are descriptive rather than tests. They take the reference at its sample mean, ignore its own uncertainty and the selection of the estimated envelope, "
    "and compare estimates from different evaluation streams, so a held-out reward above the reference's sample mean is not evidence that the family beats the optimal constrained policy, "
    "and the reference remains near-optimal and estimated rather than exact."
)
FRONTIER_NEW = (
    "On Tiger the mixture's reward is $0.34$ above the envelope at the smallest budget and $0.05$ and $0.36$ below it at the two larger ones. "
    "These comparisons are descriptive rather than tests, and they compare estimates from different evaluation streams, since the reference was evaluated on the canonical seeds with once-per-seed seeding and the family on the held-out seeds with per-episode seeding. "
    "The stream effect is not small. Re-evaluated on the held-out stream, Tiger's unpenalized reference policy scores $5.68$ rather than $5.02$, the same reward as the best feasible member, which runs the reward-only policy. "
    "A same-stream comparison, added after the results above had been inspected and in response to a referee, therefore re-evaluated every sampled reference policy on the held-out seeds under the family's per-episode seeding, after checking that each saved policy reproduces the committed reference to $10^{-9}$ on the canonical stream, "
    "and recomputed the envelope there, which pairs each seed's family reward with a reference reward on the same episode seeds (the last two columns of Table~\\ref{tab:budget_frontier}, \\texttt{experiments/run\\_frontier\\_reference\\_heldout.py}, \\texttt{results\\_budget\\_frontier\\_heldout\\_reference.csv}). "
    "On that comparison the mixture falls short of the envelope on nine of the twelve attainable budgets with a paired $95\\%$ $t$ interval that excludes zero, by $0.33$, $0.72$, and $1.03$ at Tiger's $0.25$, $0.5$, and $0.75$ budgets, its gap budget coinciding with its $0.5$ budget, $0.76$ and $1.10$ at Diagnosis's $0.5$ and $0.75$ budgets, and $0.57$, $1.32$, and $0.59$ at Bandit's $0.5$, $0.75$, and gap budgets, the largest being about a fifth of Bandit's reference reward. "
    "The other three, Diagnosis's $0.25$ and gap budgets and Bandit's $0.25$ budget, are within sampling error ($-0.03 \\pm 0.28$, $+0.00 \\pm 0.22$, and $-0.21 \\pm 0.12$). "
    "Tiger's nominal excess at its smallest budget was therefore the stream effect, not a family reward above the reference. "
    "The same-stream envelope is still a maximum over noisy sampled points, so it removes the stream mismatch but not the envelope's selection bias, and the reference remains near-optimal and estimated rather than exact."
)
EDITS.append(("frontier-same-stream", BOTH, FRONTIER_OLD, FRONTIER_NEW))

EDITS += [
    ("abstract-frontier", (JAIR,),
     "and on eleven of the twelve attainable budgets its reward falls short of the estimated feasible envelope of a near-optimal constrained reference, by amounts that are largest at each environment's largest budget, from within sampling error at the smallest Diagnosis budgets to about a fifth of the reference reward at Bandit's largest,",
     "and on nine of the twelve attainable budgets its reward falls short of the estimated feasible envelope of a near-optimal constrained reference, evaluated on the same held-out seeds, with a paired $95$ percent interval excluding zero, by amounts that are largest at each environment's largest budget and reach about a fifth of the reference reward at Bandit's largest budget, the other three being within sampling error,"),
    ("conclusion-frontier", BOTH,
     "while on eleven of the twelve attainable budgets its reward falls short of the estimated feasible envelope of the near-optimal constrained reference, by amounts that are largest at each environment's largest budget, from within sampling error at the smallest Diagnosis budgets to about a fifth of the reference reward at Bandit's largest,",
     "while on nine of the twelve attainable budgets its reward falls short of the estimated feasible envelope of the near-optimal constrained reference, evaluated on the same held-out seeds, with a paired $95$ percent interval excluding zero, by amounts that are largest at each environment's largest budget and reach about a fifth of the reference reward at Bandit's largest budget, the other three being within sampling error,"),
]


def main(dry: bool) -> None:
    texts = {p: p.read_text() for p in BOTH}
    errors = []
    for name, targets, old, new in EDITS:
        for p in targets:
            n = texts[p].count(old)
            if n != 1:
                errors.append(f"{name}: {p.name} has {n} matches")
                continue
            texts[p] = texts[p].replace(old, new)
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    if dry:
        print(f"dry run ok, {len(EDITS)} edits")
        return
    for p, t in texts.items():
        p.write_text(t)
    print(f"applied {len(EDITS)} edits")


if __name__ == "__main__":
    main(dry="--apply" not in sys.argv)
