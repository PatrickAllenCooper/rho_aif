# Evidence restructuring proposal, 2026-09-28

Scope: the original span from `\section{Experiments}` through the end of Results, before Discussion, in JAIR commit `2d3bac4`. Neither master was edited by this agent. Root integrates and builds both masters.

## Files and scale

- `evidence_original.tex` is an exact 22,518-word source extraction of the original evidence span.
- `evidence_main.tex` replaces that span with 5,932 source words, including tables, captions, and non-rendering figure descriptions. This is intentionally below the provisional 6,500–8,500-word budget because it retains the necessary qualifications at this length and leaves room for the root's theory/clarity requirements.
- `evidence_appendix.tex` retains 20,477 source words of detailed protocols, evidence, full comparisons, limitations, and figures. Repeated original navigation summaries and the closing repeated results summary are omitted. Every original evidence label, citation key, included figure/table path, and distinct decimal string remains in the union of main and appendix. This token inventory is a preservation check, not itself a scientific correctness proof.
- `evidence_main_template.tex` and `assemble_evidence.py` make the proposed fragments reproducible. The script uses the archived original span and unchanged existing `paper/tables/budget_frontier.tex`. Its integration-label smoke check reads the exact baseline full source with `git show 2d3bac4:paper/full_paper_jair.tex` and does not modify either master.

## Main narrative

The main text preserves a concise but complete environment progression, altered RockSample conventions, seed-level testing, battery differences, scale transfer (including Tiger's trivial flat curve), corrected restricted controller recovery, n=5 and n=20 TOST with retrospective/prospective scope, the literal usage-penalty/cap-envelope definition, and the held-out calibration study. It ends with an EFE comparison that retains the adverse results and scope limitations.

Primary safeguards retained adjacent to findings:

- Budgets are targets derived by a predeclared rule from the calibration curve, not application-specified targets.
- Expected-use equality, at-most usage, and hard per-episode caps remain different requirements.
- Endpoint mixtures are distinct from reward-maximizing equality mixtures and feasible mixtures over the sampled family, and from the sampled SARSOP envelope.
- Usage error at most 0.13 is an observed held-out result; selection below B is only a calibration fact and the separate held-out feasibility observation is stated as such.
- Twelve attainable rows contain eleven distinct budgets because Tiger's gap duplicates the middle target.
- The paired reference has support and weights fitted to the same held-out seed means. Its intervals are nominal pointwise plug-in intervals and omit selection, weight, cap-feasibility, and multiplicity uncertainty.
- Tiger has no wrong commits on that held-out stream. Its smallest/middle reward gaps are fragile to a sensitivity calculation using the canonical rare error rate.
- Bandit's endpoint mixture is not the best equality mixture on its own calibration grid.
- Endogenous CPOMDP caps are slack. Small negative measured gaps do not imply reward beyond a population constrained optimum.
- Controller recovery uses min(T,180) for all ten seeds, not a selected recovered-only mean. The unseeded-run correction and 9/10 versus 10/10 recoveries remain explicit. Nonstationary re-adaptation is outside the stationary theorem.
- TOST margins were retrospective on n=5, the added fifteen seeds prospective, and both the paired sensitivity and n=20 result remain in main.
- POMCP original comparisons use untuned constants. The separate sweep uses tuning-seed selection after the canonical sweep was already inspected. The Tiger claim remains retrospective; differences do not isolate information valuation.
- Tileworld's advantage is a fixed-horizon threshold and disappears on smaller grids. Observation-structure failures remain explicit.
- RS[11,11] is a negative finding with a much better heuristic, distant-sensing horizon limits, and phantom leaf exit costs.
- Inspection remains a synthetic known-model feasibility demonstration with a hand-coded leaf and no deployed validation.

## Main figures and tables

Retained main figures, with shorter captions but the original unmodified PDF assets and full accessibility descriptions:

- `fig:collapse`, `price_scale_invariance.pdf` — direct scale-transfer evidence, raw versus normalized coordinates. Caption says **separately** evaluated, not independently evaluated, because the streams are shared.
- `fig:dualmultiseed`, `price_dual_multiseed.pdf` — nonstationary recovery and scope limit.
- `fig:pareto`, `fig_pareto.pdf` — the three successes and two failures of canonical weight selection in one comparison. This is the least central retained plot and can move if layout requires, with its main summary unchanged.

Retained main tables:

- `tab:sarsop`: original cells, shortened caption.
- `tab:cpomdp`: original cells, shortened caption. Could move to appendix if needed. Long original-caption lineage concerning the actual usage-matched weights and sampled plateaus is retained in the appendix.
- `tab:main`: original cells, shortened caption. Details on pooled versus seed SE and omitted duplicate baseline rows are retained in appendix.
- New `tab:budget_frontier_main`: 12 rows copied by code from the existing generated table. Columns are environment, target type, B, endpoint-mixture U, endpoint-mixture R, and same-stream paired cap-reference gap. Every numeric cell is copied from the first or third panel of `paper/tables/budget_frontier.tex`; there is no new estimate, aggregation, rounding, or cherry-picked row. The complete original three-panel table remains in the appendix under its existing `tab:budget_frontier` label. This preserves comparisons to the feasible single member, target LP mixture, feasible LP mixture, original-stream reference, and same-stream reference. Both main and full tables use the existing uniform 9pt `\tablefontsize`.

## Moved evidence

`app:experimental_protocol` preserves all detailed environment definitions, six deviations from original RockSample, and evaluation mechanics.

`app:extended_budget_evidence` holds the former detailed budget section. Main-held subsection labels are replaced only at their definitions by `app:scale_details`, `app:dual_details`, `app:sarsop_details`, `app:cpomdp_details`, and `app:frontier_details`. Existing labels for onset, cost budgets, interleaved settings, staircases, distractor robustness, and atlas remain unchanged at their relocated subsections. Original numeric protocols and correction history are retained.

Moved budget floats: `tab:collapse-breadth`, `fig:prop2`, `fig:costbudget`, `fig:interleaved`, `fig:stairs`, `fig:distractor`, and the full input `tables/budget_frontier.tex`.

`app:extended_efe_results` holds detailed core, Pareto, Tileworld, RockSample, and Inspection results under `app:core_details`, `app:pareto_details`, `app:tileworld_details`, `app:rocksample_main_details`, and `app:inspection_details`. The pre-existing RockSample appendix remains a separate solver/extended-result source.

Moved EFE floats: `tab:tileworld`, `fig:tw_comparison`, `fig:tw_scaling`, input `tables/rocksample_main.tex`, and `tab:inspection`. Original row/metric explanations, statistical qualifications, negative findings, and mechanisms are preserved.

## Audit results and limits

- Temporary integration against the baseline has no duplicate direct labels and no missing references after reading table inputs.
- All original evidence labels, citation keys, figure paths, table input paths, and unique decimal strings survive in main plus appendix.
- Main introduces no decimal string absent from the baseline full manuscript or existing table inputs.
- No prose semicolon was introduced.
- Critic reviewed the main fragment and found no substantive strengthening; its one caption concern about statistical independence was corrected.
- The source has not been rendered by this agent. Root owns compilation, float placement, table readability, final claim-check triage, cross-master propagation, and full-paper review. No experiments, CSVs, or bibliography were modified.
