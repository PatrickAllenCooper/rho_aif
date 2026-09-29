# Independent review of editorial concision drafts

Date: 2026-09-28. Reviewed `intro_main.tex`, `related_main.tex`, `discussion_main.tex`, and `editorial_appendix.tex` against the saved original sections. Also read `theory_main.tex` at the theory editor's request. Masters were not edited by this reviewer.

## Assessment

The shorter Introduction and Discussion preserve the principal argument and the important negative findings. The expected-usage target is distinguished from a cap, mixture selection is distinguished from optimality, reward convention and normalizer scope remain visible, the random two-state failure rate remains qualified, and the POMCP comparison no longer reads as an isolated-component or general-solver superiority claim. The main text retains Navigation, RockSample, discounting, model mismatch, and synthetic Inspection limitations. I found no newly strengthened scientific claim requiring a substantive rewrite.

All 58 distinct citation keys in the original Introduction, Related Work, and Discussion remain in the revised editorial main text plus appendix. The additional editorial key is the already existing Kouw reference. This verifies retention, not a new external bibliography audit.

The theory draft preserves the formal statements and their restrictions. The normalizer qualification is especially improved by being stated before and after the recursion. The exact-optimizer information-floor statement is immediately distinguished from the replanning implementation. Count/cost rescaling, bracket containment, and controller gap-budget distinctions survive.

## Local corrections sent to editors

1. The relocated interpretation appendix still refers to the “reward-to-nats calibration paragraph of Section Methodology.” The full derivation is now in `app:theory_setup`. The shortened main paragraph is titled “Reward and information units.” Point to the actual location, or name the shorter main paragraph accurately.
2. The same appendix says the formal-equivalence subsection “read Table alpha_eta against that prediction.” The detailed reading has moved to `app:theory_thresholds`. Update that locative.
3. In the main Discussion, “reduces to myopic information gain” can sound as though the reward term vanishes. “Reduces to myopic reward plus information gain at w=1” preserves the intended statement clearly.
4. The Introduction's contribution summary can state “an interval of weights that avoids an unnecessary second observation.” Its current reference to an interval “in which w=1 avoids” is less precise because whether one lies in that interval depends on the parameters.
5. The theory positioning paragraph calls sampled reference mixtures feasible. Prefer “selected as feasible from estimated usage” to make their statistical feasibility status immediately explicit, consistent with the later qualification.

These are local wording and navigation fixes. Final review of the assembled source and compiled references is still pending.
