# Grid-world spotlight script proposal — 2026-10-09

Four slides, three minutes. Spoken word count 331, split 54, 94, 92, 91. Timing target2:54, leaving6seconds of buffer. The 4×4 prior/posterior illustration is a mathematical schematic of the benchmark's observation model. The measured experiment on slide 3 uses 8×8 grids. Native geometric shapes and a native data chart support the requested minimal black-and-white design. No AI-generated imagery is needed.

## Slide 1 — Official accepted title and motivating grid — 0:00–0:28

Somewhere on this grid is a hidden target. The agent can buy a noisy scan, or choose one cell and end the search. A wrong choice is costly. Scanning forever is costly too.

Our accepted paper asks how expected free energy connects two questions: what should the agent learn, and when should it act?

## Slide 2 — Seeing changes belief, not the target — 0:28–1:17

Start with equal probability across the grid. This scan asks whether the target is in the top half. It is eighty percent accurate, so a positive signal puts eighty percent of the probability in that half. The target itself stays fixed.

For the reward-based recursion we study, minimizing EFE is equivalent to planning with reward plus expected information gain. That is a rho-POMDP with belief-dependent utility.

The result requires exact Bayesian updates, matched horizons and units, and the stated reward convention. Weight one is not a universal exchange rate between arbitrary rewards and information.

## Slide 3 — Information can help a shallow planner — 1:17–2:08

Now enlarge the grid to eight by eight, with planning limited to a two-step horizon.

The reward-only planner takes no scans and succeeds just one point four percent of the time. Weight-one EFE keeps scanning and reaches about sixty-nine percent.

A much larger information weight reaches almost ninety-eight percent, but its extra scans reduce net reward.

These are updated measurements from one thousand episodes across five seeds. They expose a shallow-planning limitation, not a failure of reward-only planning at every depth. At smaller grid sizes, the reward-only and EFE agents perform similarly.

## Slide 4 — Calibrate expected sensing usage — 2:08–2:54

Our subsequent work asks how to calibrate that weight to an expected sensing target.

Measure usage across weights. When two policies straddle the target, a mixture can match it on calibration data.

Across twelve attainable target cases in three other simulated tasks, held-out mean error is at most zero point one three observations. These targets come from calibration curves.

This is expected usage, not a per-episode cap or a guarantee of maximum reward. On recorded sensor data, the policies overspend on later batches.

Please visit our poster to discuss these trade-offs.

## Source and delivery notes — not spoken

- The 4×4 illustration represents a uniform prior over a fixed hidden target. Use cells, probability shading or dot areas, and a dashed scan boundary. Do not draw a robot, obstacles, movement arrows or a navigation path. Tileworld has no moving-agent action.
- The scan is an actual available 4×4 row-bit partition: top two rows versus bottom two. With the benchmark's 80% sensor accuracy and uniform prior, a positive top-half signal gives 80% posterior mass in the top eight cells and 20% in the bottom eight. Each upper cell has probability0.1 and each lower cell0.025. Label this an illustrative Bayesian update, not a measured episode.
- Grid mechanics: `rho_aif/environments/tileworld.py`, especially `_build_partitions`, `_build_observation_models`, and `step`; accepted `paper/paper_iwai2026_abridged.tex` methodology and Tileworld description; current `paper/full_paper_jair.tex` lines454 and715–727.
- Slide 2 should visibly scope the identity to the specified reward-based recursion. Per-step reward plus expected information gain sits within the same future-value recursion, including terminal values and shared tie breaking. Current formal conditions supersede broad readings of the frozen accepted version. General normalized preferences may contribute a policy-dependent normalizer. Log-score reward is the exact identification case. Empirical weight one on slide 3 means one reward unit per bit, not per nat.
- Slide 3 source: `results/results_tileworld_scaling.csv`, grid_size8, rows Planning, EFE and Planning+IG. Success percentages are1.4,69.4,97.8. Seed-level SE in percentage points are0.2915476,1.0416333,0.5830952, displayed as±0.3,±1.0,±0.6pp. Mean scan counts are0,17.496,39.52. Mean net rewards are−49.16,−25.856,−30.84. All rewards already include scan costs.
- The high-weight comparator is fixedw100. It is **not tuned for success** in this scaling experiment. A producer variable's name does not establish tuning. Current manuscript line722 explicitly states fixedw100. Suggested label: “High information weight, w=100”.
- Scaling protocol: five seeds42/123/456/789/1024,200episodes each,1,000total, matchedH2 but not matched computation. The sweep has seed-level SEs and no formal scaling-test companion. Describe measured means and the observed horizon limitation, not a formal superiority test.
- At4×4 and6×6, Planning and EFE success means are within one SE in this scaling battery. “Perform similarly” is descriptive, not a statistical equivalence claim. Neither the result nor the script asserts that larger state spaces universally favor EFE.
- The final result is from **other tasks**, Tiger, Diagnosis and Bandit, in `results/results_budget_frontier.csv`. Twelve attained target cases include one duplicated Tiger budget, hence11distinct environment-budget pairs. Max absolute held-out mean usage error is0.123, so≤0.13 is conservative rounding. Three below-range targets fail. Targets were fixed by a predeclared rule from calibration curves, not supplied by an operator. The graphical calibration curve must be either sourced directly from this archive or clearly marked schematic.
- Public sensor transfer caveat: current manuscript `sec:real_sensor` and `results/results_real_sensor_summary.csv`. This is retrospective replay of recorded measurements, not field deployment. Later batches overspend for both originally straddled targets. The script does not claim this procedure always transfers or improves classification.
- Suggested restrained visual grammar: white background, black text and grid lines, two gray probability levels plus white. Native labels, thin connectors and honest data marks only. Sparse visible text should let the speaker carry the detail.
