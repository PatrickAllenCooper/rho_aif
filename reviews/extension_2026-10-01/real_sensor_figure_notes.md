# Real-sensor publication figure

PDF: `figures/real_sensor_transfer.pdf`
PNG: `figures/real_sensor_transfer.png`

The authored width is 6.7 inches. All text is at least 9.5pt, remaining above 9pt at a 6.5-inch printed width.
No table is generated because the paired-gap panel already carries the primary comparison.

## Suggested caption

Retrospective sensor acquisition on UCI Gas Sensor Drift with fixed researcher-defined expected-access targets $B\in\{2,4,8\}$. (a) Realized mean usage of the frozen crossing-endpoint mixture minus its target on unseen cases from batches 1--6 (Test) and separately on later batches 7--10. Zero denotes exact mean attainment, and the gray band is the predeclared $\pm0.5$ access tolerance. Collection-period positions are categorical. Test intervals are Bonferroni-adjusted 98.333\% conditional bootstrap intervals, with calibration selection repeated in each replicate. Later-batch intervals are nominal 95\% paired case-bootstrap intervals with the original calibration selections fixed. (b) Held-out accuracy differences in percentage points between the crossing mixture and the direct usage-penalty equality mixture or exact-count greedy conditional-information acquisition (CMI). Intervals are nominal 95\% paired bootstrap intervals including calibration reselection. Positive differences favor the crossing mixture. The fitted direct equality mixture need not attain exactly $B$ on held-out cases. All intervals condition on one trained observation model and exchangeability within batch/class strata. The fixed $B=2$ request has no calibration crossing and no plotted estimate; it fails the declared all-target criterion.

## Suggested Description

Two panels plot the available four- and eight-access crossing mixtures. The left panel shows usage minus target across within-period held-out cases and four later collection batches as separate points with intervals, a horizontal zero line, and a gray half-sensor tolerance band. Both series overshoot in every later batch. The right panel plots negative paired held-out accuracy differences from direct equality and exact-count information acquisition, with interval bars and a vertical zero line. The unavailable two-access request is stated in the caption and prose, not plotted as a measurement.

## Displayed held-out values

- B=2: crossing unavailable on calibration.
- B=4: mean usage 4.00563, accuracy 80.2266%. Usage-error interval {'lower': -0.2096900960742247, 'upper': 0.2553966271871885, 'valid_replicates': 2000, 'failed_replicates': 0}.
  - Accuracy gap against direct_target: {'lower': -0.02933498664641821, 'upper': -0.008275221608543009, 'valid_replicates': 2000, 'failed_replicates': 0} (probability units).
  - Accuracy gap against cmi: {'lower': -0.028674136060879887, 'upper': -0.0028191770592826664, 'valid_replicates': 2000, 'failed_replicates': 0} (probability units).
- B=8: mean usage 8.01889, accuracy 76.2786%. Usage-error interval {'lower': -0.36179539771959773, 'upper': 0.410857064577971, 'valid_replicates': 2000, 'failed_replicates': 0}.
  - Accuracy gap against direct_target: {'lower': -0.047870195045955584, 'upper': -0.02906543960694327, 'valid_replicates': 2000, 'failed_replicates': 0} (probability units).
  - Accuracy gap against cmi: {'lower': -0.04648122767868418, 'upper': -0.016550447239824243, 'valid_replicates': 2000, 'failed_replicates': 0} (probability units).

## Missing-selection audit

No displayed interval has a failed replicate.

## Input hashes

- `results/results_real_sensor_summary.csv`: `d060e6851e44428bca81aaf233d3b722a2b0d922905737a67a30808c0a09bcf2`
- `results/real_sensor_2026-10-01/analysis.json`: `4d20fa9bb79d0410e4d80fa7e5994c66442b5d97b022910e38cd9c44266b102b`
- `results/real_sensor_2026-10-01/selection.json`: `1ae12c9927968390c885b1d1b9cb1d2b5ddc4161572e9a4128acc08191ba259d`
- `experiments/protocols/gas_sensor_2026-10-01.json`: `737199e4807d7667644ec7c873e6e3f29e319fc02d209d3b571e1ebd253028a9`
