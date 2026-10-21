# Independent post-edit attribution audit C

Date: 2026-10-21. Verdict: **PASS — no required changes**.

Read the actual live sources, their full Git diff, and `apply_attribution_edits.py`. The diff contains exactly three sentence replacements per master. All old strings occur zero times and all replacements occur exactly once in both files. The surrounding qualifications and citation keys are preserved.

## Attribution findings

1. **IDS, JAIR line 146 / LNCS line 99:** The revised sentence identifies an action distribution, squared expected one-period regret, and expected information gain about the optimal action. The official NIPS 2014 abstract explicitly states the squared-regret ratio and mutual information about the optimal action. The freshly fetched arXiv abstract agrees. The sentence no longer conflates the numerator with unsquared regret. No new overclaim found.

   Sources checked: https://papers.nips.cc/paper_files/paper/2014/hash/90720a2fcc41f9332e6a1558da327089-Abstract.html and https://arxiv.org/abs/1403.5556.

2. **Oudeyer and Kaplan, JAIR line 156 / LNCS line 109:** The replacement describes an earlier computational typology of intrinsic motivation. The publisher's 2007 full text and abstract directly support this description. It does not suggest that the 2007 paper reviewed the later VIME, count-based deep-RL, or random-network-distillation methods. No residual chronology ambiguity found.

   Source checked: https://www.frontiersin.org/journals/neurorobotics/articles/10.3389/neuro.12.006.2007/full.

3. **Resource-control precedent, JAIR line 454 / LNCS line 407:** The replacement concerns information prices and resource constraints, not a common adaptive update supplied by every cited source. Sims's primary university record confirms a finite Shannon-capacity constraint. The immediately surrounding text still distinguishes the present across-episode information weight from constrained-POMDP dual variables and information constraints internal to EFE. The earlier related-work paragraph already separates capacity constraints/prices, CMDP resource multipliers, and SAC target-entropy tuning. Read in this context, the revised grouped precedent statement is appropriately scoped and does not attribute online price adaptation to rational inattention.

   Source checked: https://collaborate.princeton.edu/en/publications/implications-of-rational-inattention/. The fresh publisher-deposited Crossref record for Sims is also saved in `sources_c/sims2003.crossref.json`.

No source or bibliography files were changed by this post-edit audit. This verdict is limited to the three attribution edits and their propagation; it does not claim a new full scientific review or acceptance decision.

## Verified SHA-256 hashes

- `paper/full_paper_jair.tex`: `5b86fb4963cb04b65926ef86d0da58c14a4c1a37db3b7f14810941b038eafd1f`
- `paper/full_paper.tex`: `326fe1a69322c416bea55658ba39ab30aef0ee6a58d7d61f32ca2a6611ab56ba`
- `reviews/citations_2026-10-21/apply_attribution_edits.py`: `a93ba11208d49e6d2e9befeb770e0ff229e668d1883092d142ae1adc98088dba`

Recorded at 2026-10-21T16:44:39.600399+00:00.
