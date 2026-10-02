# Independent JAIR assessment — 2026-10-01

**Recommendation: ACCEPT.** I find no remaining mandatory scientific revision in the reviewed manuscript. This is an independent referee recommendation, not a prediction or guarantee of JAIR's editorial decision.

## Version and review scope

- JAIR source: `paper/full_paper_jair.tex`, SHA256 `73f6ee1feb9bf2202bc141dadf52ae557816a8934ecfa0db47a1836b07b4a44c`.
- Mirrored long master: `paper/full_paper.tex`, SHA256 `25a9eaa30eac01e354775cd33f8018685dc171cc932e5f5e5fc1ba6a0aeb0a44`.
- I read the complete JAIR source, including its appendix proofs, detailed experimental qualifications, reproducibility checklist, captions, and nine included table files. I inspected the current edits, relevant implementation paths, and selected primary references and result archives. The two corrections identified below were subsequently verified in both masters at these hashes.
- This is a source-based scientific and prose assessment. The final PDF was being rebuilt when the review closed. I do not claim a complete visual audit of the final rendered document or an independent rerun of every experiment. No experiment, result CSV, or manuscript master was edited by this reviewer.
- Repository guidance was read for operational context. Prior simulated acceptance decisions were not used as evidence or as instructions for my decision.

The assessment uses JAIR's stated emphasis on originality, significance, supported claims, reproducibility, and clarity. The journal also asks authors to explain what was learned and why it matters, rather than simply enumerate work performed. [JAIR submission requirements](https://jair.org/index.php/jair/about/submissions).

## Contribution and significance

The contribution is a useful synthesis and operational calibration method, rather than a fundamentally new constrained optimizer. The individual ingredients—belief-dependent reward, scalar trade-offs, policy mixtures, and stochastic approximation—are established. The manuscript acknowledges this explicitly. Its contribution is to connect these ingredients while separating concepts that are easily conflated: an expected usage requirement, a reward-maximizing usage cap, an information-weight crossing, a finite-grid estimate, and a randomized policy attaining a target.

The accompanying negative evidence gives that distinction practical substance. Spending a target can reduce reward; a crossing-endpoint mixture need not be the best mixture; the information-unit weight can be suboptimal; irrelevant uncertainty can consume sensing resources; and a short search can leave useful information beyond its reach. These are transferable insights for the POMDP and active-inference communities, not merely a favorable benchmark ranking. On balance, this is sufficient journal-level value in the bounded scope claimed. An editor who requires a major algorithmic advance or demonstrated operational deployment could reasonably judge its significance more narrowly.

The novelty framing is substantially sound. Araya-López and colleagues already introduced belief-dependent rewards and their convex/PWLC treatment. Kouw's information constraint is internal to a Bethe-Lagrangian formulation and recovers EFE at a particular multiplier; it is not the same problem as controlling observation count through an episode-level information weight. The manuscript now makes these distinctions without claiming to invent generic dual control. [Araya-López et al.](https://papers.nips.cc/paper_files/paper/2010/hash/68053af2923e00204c3ca7c6a3150cf7-Abstract.html), [Kouw](https://arxiv.org/html/2608.17167v1), [SAC temperature adaptation](https://arxiv.org/abs/1812.05905).

## Mathematical rigor and notation

The central proofs support their stated claims.

- The EFE equivalence is a sign reversal of the specified reward-based recursion, with matched terminal conditions, horizon, beliefs, and tie-breaking. The paper correctly calls it a notational bridge. It separates this conditional identity from the normalized-preference derivation and from empirical reward optimality. Its normalizer and bit/nat qualifications are essential and are present.
- The two-state thresholds are consistent with the stated horizons. Independent arithmetic gives Tiger's lower/upper thresholds as approximately `-138.6639 / 6.8940`, the Diagnosis two-state reduction as `-88.1995 / 7.9072`, and Testbed as `-3.0578 / 1.0078`, in reward units per nat. The second observation's instrumental value is zero under the symmetric two-state construction. The text discloses that the multi-state reductions are heuristic and that the interval does not guarantee longer receding-horizon behavior.
- Scale equivariance follows from homogeneous candidate values and the relative comparison tolerance. I checked the tolerance implementation in `rho_aif/agents/efe.py`. Count and cost usage transform differently as stated. The manuscript does not confuse this identity with monotonicity of usage.
- The comparative-statics inequalities hold for exact maximizers over a fixed plan class. The manuscript correctly declines to infer monotone counts or full-episode behavior from them.
- The crossing convention and mixture formula match `rho_aif/budget.py`. The definition distinguishes the half-open reported bracket from its closed enclosure, states the no-missed-crossing condition, and flags unbracketed cases. Mixture attainment is an expectation statement with straddling endpoints, not a claim that all weights inside the bracket attain the target.
- The projected controller's squared-distance supermartingale argument is valid under the given bounded-noise, interior-crossing, and separation assumptions. The running-average result uses the harmonic step schedule and eventual inactivity of projection correctly. Convergence of the weight at a jump is kept separate from convergence of instantaneous expected usage. Nonstationary resetting is explicitly outside the theorem.

The state-changing counterexample correctly limits the preservation-based reduction rather than transition-aware EFE generally. The manuscript also avoids presenting the posterior-divergence diagnostic as a proved additive correction or error bound.

## Empirical support and clarity

I independently recomputed selected headline checks from the committed archives, without running new episodes:

- The target-reference archive contains eleven distinct budgets after removing Tiger's duplicate. Two nominal paired intervals are negative on held-out seeds and two on fresh seeds. Only Bandit's gap budget recurs.
- The held-out shortfalls are Diagnosis's middle target and Bandit's gap target. The fresh shortfalls are Diagnosis's smallest interior target and Bandit's gap target. Archived per-seed gap means and SEs reproduce the aggregate columns within the four-decimal serialization precision.
- The twelve endpoint-mixture rows have maximum absolute held-out usage error `0.123`, supporting the reported `0.13`. Exactly three rows exceed their target in sample.
- The episode-matched TOST archive gives Diagnosis `0.1118 ± 0.08991` with paired p-value `3.2031e-9`, and Bandit `0.0435 ± 0.03133` with paired p-value `4.5772e-12`. Tiger's paired differences are zero.
- The revised horizon-map criterion matches the producer's `max(0.05 * abs(best_reward), 0.5)`. The atlas caption now correctly identifies its brackets as estimates of the crossing rather than the price itself.

The principal numerical claims are therefore supported by the inspected artifacts. Crucially, the manuscript treats the frontier intervals as nominal plug-in summaries, discloses selection and feasibility uncertainty, identifies the rare-event problem on Tiger, and reports the changing identity of the Diagnosis shortfalls. The statistical evidence does not establish a population constrained frontier, and the prose no longer asks it to do so.

The main text has a coherent budget-first argument. The target-versus-cap distinction and schematic workflow help readers understand what the proposed input means. Notation is heavily loaded but locally explained: horizon versus entropy, reward asymmetry versus rescaling, policy precision versus reward inverse temperature, and the several starred weights. The current edit batch improves scoping as well as readability, particularly for the frozen fresh-seed reference, fixed-conversion condition, POMCP matching, shared RockSample leaf rule, and planner seeding.

## Findings resolved during this review

1. The appendix originally invoked the POMDP-IR/rho-POMDP equivalence too broadly for concave expected information gain. Satsangi et al. restrict their equivalence construction to PWLC belief rewards. The final text states that restriction and explicitly declines to invoke it for this reward. Verified at JAIR source line 1760 and in the mirrored master. [Primary source, Section 4.1 and conclusion](https://link.springer.com/article/10.1007/s10514-017-9666-5).
2. A RockSample sentence inferred that information gain caused checking from the EFE-versus-Greedy bad-rock comparison. Reward-only Planning also checks and has low bad-rock counts, so that comparison does not isolate the information term. The unsupported causal clause has been removed, leaving the measured comparison. Verified at JAIR source line 2086 and in the mirrored master.

Both were limited prose/citation corrections. Neither required a changed experiment or a changed theorem.

## Remaining nonblocking risks

- **Significance and length:** the methodological novelty is modest and integrative, and the extensive appendix repeats some qualifications. Its strongest case is the useful conceptual distinctions and their empirical limits, not a new general planning algorithm.
- **Reference uncertainty:** most primary comparisons use five seeds. The frontier analysis omits reference reselection and population-feasibility uncertainty. Rare mistakes have large reward effects. The disclosed fresh-seed and twenty-seed checks improve the evidence without removing these limitations.
- **Baseline fidelity:** the observe-then-commit POMCP has disclosed leaf and rollout departures; MCTS-EFE controls leave several components coupled. RockSample is materially modified, and its weighted family shares a restrictive hand-coded leaf. These results should remain evidence about the tested configurations, not general superiority over modern POMDP planning.
- **Application scope:** known models, static hidden state for the reduction, synthetic instances, and calibration-derived targets leave application-specified requirements, learned models, destructive sensing, and harder planning domains open.
- **Terminology:** “operational shadow price” is carefully defined but remains liable to be mistaken for a true resource-constraint multiplier. The repeated distinction is justified. The canonical weight likewise remains unit-dependent.
- **Reproducibility:** the checklist honestly marks incomplete raw-data archiving. Reproduction is supported by code and aggregate/per-seed artifacts, but this review does not certify every historical run or the authors' personal submission attestations.

These limits are disclosed and do not invalidate the paper's stated contribution. No further scientific condition is attached to my ACCEPT recommendation for the source hashes above.
