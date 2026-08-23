# What a multi-round automated verification campaign actually finds in a manuscript

**Status**: paper-ready summary of the verification campaign run against `paper/full_paper_jair.tex`, August 19–22, 2026.
**Purpose**: this material is not yet in any paper. It is written so it can be worked into either (a) a standalone methods/meta-science note, or (b) a verification-methodology section or appendix of the rho_aif manuscript itself.
**Source of record**: `full_paper_plan.md` §9.1–9.16. Every count below is traceable to a numbered ledger entry and a git commit.

---

## 1. What was done

A single ~66-page manuscript was put through eight distinct automated verification passes over four days, using multi-agent workflows in which independent subagents read the manuscript, the code, and the committed result CSVs, and reported findings that were then adversarially re-verified before being acted on. The passes differed in *instrument*, not merely in repetition:

| Pass | Instrument | Agents | Findings |
|---|---|---|---|
| §9.1–9.6 | Empirical-rigor pipeline audit + blind 13-agent re-verification | 13 | 5 pipeline defects; ~20 further stale claims |
| §9.7–9.8 | Referee simulation, round 1 (3 lenses) | 7 | 8 verified |
| §9.10 | Referee simulation, round 3 | 7 | 5 major + 10 minor |
| §9.11 | Referee simulation, round 4 | 7 | 2 major + 5 minor (first zero-blocking round) |
| §9.12 | Citation verification + literature sweep | 10 | 0 factual errors in 62 entries; 5 citations added |
| §9.13 | Self-identified weakness hardening | — | 9 addressed |
| §9.15 | Referee round 5 **+ statistics-specific claim audit** | 7 + 48 | 4 + **38** confirmed |
| §9.16 | **Venue-specific mock review panel** (5 role-differentiated reviewers + adjudicating editor) | 6 | **15** conditions, 1 blocking |

Roughly 100 agent-reviews in total, against one manuscript, with every finding verified against source before action.

---

## 2. The headline result: repetition converges, instrument change does not

The naive expectation is that review rounds exhibit diminishing returns until the manuscript is clean. Rounds of the *same* instrument did exactly that — the referee-simulation sequence decayed 20 → 8 → 15 → 7 and reached its first zero-blocking verdict at round 4, at which point the ledger recorded the manuscript as "at or near the practical ceiling of referee-simulation improvement."

That conclusion was wrong, and provably so. Holding the manuscript nearly fixed and changing only the *instrument* re-opened a rich seam twice:

- A **statistics-specific** audit (§9.15), which required agents to check every quantitative claim against this project's own written statistics protocol and against the source CSVs, found **38 confirmed gaps** — more than the four preceding referee rounds combined.
- A **venue-specific role-differentiated** panel (§9.16), which assigned reviewers concrete expertise identities rather than generic quality lenses, found **15 more**, including one blocking defect that five prior rounds had passed over.

**Claim for a paper**: convergence of a review instrument is evidence about the instrument, not about the artifact. Reported saturation of one review protocol should not be read as manuscript quality. This is directly measurable and, in our case, was measured twice.

---

## 3. The dominant failure mode: artifact-correct, prose-drifted

Across §9.15 and §9.16, in **every** confirmed instance, the committed data artifact was correct and the manuscript text had drifted away from it. Not one finding was a data-validity failure. The direction is consistent enough to name:

> **Propagation failure.** In a pipeline where results are regenerated frequently and prose is edited separately, the prose becomes stale relative to artifacts that are themselves correct.

Two concrete sub-patterns, both recurring independently across unrelated files:

**(a) Computed-then-discarded.** A shared helper computed seed-level standard errors and seed counts in memory from correctly seed-tagged episodes, and then individual experiment scripts hand-built their output rows from a subset of its fields, silently dropping the statistics before they reached disk. This recurred in **six** scripts written at different times. Each instance was individually trivial; the class was invisible until an instrument specifically looked for it. Downstream, this produced manuscript claims of the form "statistically indistinguishable" with no test statistic anywhere in the paper or the data.

**(b) Stale-label survival.** A tuned hyperparameter printed in a table caption (`w*=50`) matched no reachable output of the current code, which selected `20`/`10`. The number had been correct before a tuning fix landed and was never re-propagated. It survived five referee rounds because checking it required *running the tuner*, not reading the paper.

**Claim for a paper**: automated review that reads only the manuscript cannot detect propagation failure, because the manuscript is internally consistent. Detection requires an instrument that re-derives claims from source artifacts.

---

## 4. Reading source beats reading prose

The single most consequential finding of the entire campaign came from the one reviewer who read the implementation rather than the text. A baseline labelled `POMCP` and cited to Silver & Veness (2010) was found to build no search tree and use no UCB1 selection — a flat one-ply Monte Carlo evaluator under a canonical algorithm's name. Follow-up verification established it hit the episode step cap on **100% of episodes** on two of four instances, meaning its reported collapse was truncation rather than the information-seeking deficit the manuscript interpreted it as.

No prose-level review could have found this: the manuscript's description of the baseline was coherent, and the numbers in the table were the numbers the code produced. Only the name was wrong.

**Claim for a paper**: mislabeled or miscited baselines are a failure class invisible to text-level review and detectable only by code inspection. Given how much of empirical AI rests on named baselines, this is a general risk, not a local one.

---

## 5. Reviewers — including automated ones — are wrong at a measurable rate

The adjudicating editor in §9.16 overruled or reduced **8 of the panel's concerns**, and **four of those involved the reviewer misreading the code or the manuscript**, including two claims about the flawed baseline's mechanism that were contradicted by the committed data (the reviewer asserted the agent sampled ground-truth state and never checked; it sampled its own belief and checked almost continuously — it was the *rollout policy* that never checked).

Notably, the reviewer whose supporting mechanism was most wrong was also the reviewer whose core finding was most important. Discarding the review on the strength of its errors would have discarded the campaign's best result.

**Claim for a paper**: adversarial verification of reviewer claims is not optional overhead in automated review — it is what makes the output usable. Report both the confirmed-finding rate and the reviewer-error rate; a pipeline that reports only the former is not characterizing its instrument.

---

## 6. The fixing agent introduces defects at a measurable rate

In §9.15 the agent performing repairs introduced a new false claim while correcting a true one: having found the stale `w*=50` label, it wrote a replacement caption asserting that the two tuned agents were "tuned independently per agent class" at weights `20` and `10`. That was false — the script passed a single myopic-class weight to both — and the accompanying causal story ("planning depth pushes its tuned weight into net-negative reward") was fabricated from the incorrect premise.

This was caught one pass later by §9.16. Investigating it revealed the underlying bug was **broader than either the original reviewers or the repair had identified**: the weight-transfer error affected all four environments, violating the tuning function's own documented contract.

**Claim for a paper**: the repair step is itself a defect source and requires the same verification as the drafting step. An automated review-and-repair loop with no post-repair verification pass will inject errors at some nonzero rate. We observed at least one substantive injected error per major editing pass.

---

## 7. What the campaign changed about the manuscript's actual claims

Not cosmetic. A partial list of substantive corrections:

- A "Pareto knee on every environment" claim, in six locations, was false: on one environment the paper's own regenerated sweep shows the recommended setting is **Pareto-dominated on both axes**.
- A simple posterior-sampling baseline with **no information-gain term** was found statistically indistinguishable from the paper's proposed method on one environment on all three metrics (p = 0.58, 0.97, 0.30), and nominally ahead on reward — while being absent from tables captioned "full agent set."
- A headline scaling contrast (69.4% vs 1.4%) was found to be a comparison against an agent that takes **zero** sensing actions at that scale, making it a joint horizon-and-scale artifact rather than the scale effect claimed.
- A mechanism claim ("policy saturation, not a compute ceiling") was withdrawn as not separable from a previously undisclosed shared leaf heuristic.
- Three benchmark deviations from a canonical published environment were undisclosed, and a reproducibility checklist asserted conformance to the standard generator.

**Claim for a paper**: the corrections were not stylistic. In a manuscript that had already passed multiple review rounds, instrument-diverse verification changed what the paper asserts.

---

## 8. Honest limits (state these prominently in any write-up)

These are real and should not be buried:

1. **n = 1.** One manuscript, one research group, one domain. Nothing here establishes base rates for the field.
2. **The reviewers are simulated.** They agreed with each other more readily than a real panel likely would, and their verdict distribution (4–1) should not be read as predictive of a real editorial outcome.
3. **No control condition.** We cannot separate "instrument change finds more" from "later passes find more because the manuscript changed underneath them," though the manuscript changed only modestly between §9.11 and §9.15 relative to the 38-finding jump.
4. **The auditor and the audited share an architecture.** The same class of system wrote much of the prose, performed the audits, and executed the repairs. Correlated blind spots are plausible and undetectable from inside this setup.
5. **Finding counts are not severity-weighted.** A count of 38 mixes one blocking defect with many minor traceability gaps.
6. **Selection effect on the "artifact-correct" claim.** The instruments were designed to compare prose against artifacts, so they were best positioned to find prose-vs-artifact mismatch. A data-validity failure might have been missed rather than absent.

---

## 9. Suggested framing

The most defensible paper here is **not** "AI agents can review papers." It is narrower and better supported:

> **Working title.** *Instrument diversity, not iteration depth, determines what automated manuscript verification finds.*
>
> **Core claim.** Repeated application of a single automated review protocol converges to zero findings while substantial defects remain. Changing the instrument — from generic quality review to protocol-specific claim auditing, to venue-specific role-differentiated review, to source-code inspection — re-opens findings at rates exceeding the converged protocol. Convergence therefore measures the instrument, not the artifact.
>
> **Supporting claims.** (i) The dominant residual failure mode in a regeneration-heavy pipeline is prose drifting from correct artifacts, which text-level review is structurally unable to detect. (ii) Mislabeled baselines are detectable only by code inspection. (iii) Both the reviewing and the repairing agent produce errors at measurable rates, so adversarial verification and post-repair verification are load-bearing, not optional.
>
> **Evidence.** A single longitudinal case study with a complete public audit trail: ~100 agent-reviews, eight instruments, every finding traceable to a ledger entry, a source artifact, and a commit.

The strongest asset is the audit trail. Most claims about AI-assisted review are made without one; this campaign can show its work at every step, including its own mistakes.

---

## 10. The one-sentence finding

> Five rounds of automated referee simulation converged to zero blocking findings on a manuscript that a statistics-specific audit then found 38 gaps in, and a code-reading reviewer then found a canonical baseline had been misimplemented and miscited in — because each instrument can only see the failure modes it was built to look for.
