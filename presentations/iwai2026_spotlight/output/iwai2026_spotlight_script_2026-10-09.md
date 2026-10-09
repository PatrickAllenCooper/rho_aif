# IWAI 2026 spotlight script

Four slides. 331 spoken words. Rehearsal target 2:54, with six seconds of buffer.

The timing is a rehearsal guide, not a measured speaking duration. Read the spoken paragraphs only. Pause briefly when changing slides.

## Slide 1. The sensing decision (0:00-0:28)

Somewhere on this grid is a hidden target. The agent can buy a noisy scan, or choose one cell and end the search. A wrong choice is costly. Scanning forever is costly too.

Our accepted paper asks how expected free energy connects two questions: what should the agent learn, and when should it act?

## Slide 2. EFE as belief-dependent utility (0:28-1:17)

Start with equal probability across the grid. This scan asks whether the target is in the top half. It is eighty percent accurate, so a positive signal puts eighty percent of the probability in that half. The target itself stays fixed.

For the reward-based recursion we study, minimizing EFE is equivalent to planning with reward plus expected information gain. That is a rho-POMDP with belief-dependent utility.

The result requires exact Bayesian updates, matched horizons and units, and the stated reward convention. Weight one is not a universal exchange rate between arbitrary rewards and information.

## Slide 3. More certainty can cost more (1:17-2:08)

Now enlarge the grid to eight by eight, with planning limited to a two-step horizon.

The reward-only planner takes no scans and succeeds just one point four percent of the time. Weight-one EFE keeps scanning and reaches about sixty-nine percent.

A much larger information weight reaches almost ninety-eight percent, but its extra scans reduce net reward.

These are updated measurements from one thousand episodes across five seeds. They expose a shallow-planning limitation, not a failure of reward-only planning at every depth. At smaller grid sizes, the reward-only and EFE agents perform similarly.

## Slide 4. A target for expected sensing usage (2:08-2:54)

Our subsequent work asks how to calibrate that weight to an expected sensing target.

Measure usage across weights. When two policies straddle the target, a mixture can match it on calibration data.

Across twelve attainable target cases in three other simulated tasks, held-out mean error is at most zero point one three observations. These targets come from calibration curves.

This is expected usage, not a per-episode cap or a guarantee of maximum reward. On recorded sensor data, the policies overspend on later batches.

Please visit our poster to discuss these trade-offs.
