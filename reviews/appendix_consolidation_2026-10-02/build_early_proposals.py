"""Create guarded editorial proposals; never edits either manuscript."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / "paper/full_paper_jair.tex").read_text()
proposals = []


def section(title):
    start = SOURCE.index("\\section{" + title + "}")
    end = SOURCE.find("\\FloatBarrier\n\\section{", start + 1)
    return SOURCE[start:end]


def add(id, old, new, rationale, retained_evidence, **kwargs):
    assert SOURCE.count(old) == 1, id
    proposals.append(dict(id=id, old=old, new=new.rstrip()+"\n\n", rationale=rationale,
                          retained_evidence=retained_evidence, **kwargs))


# The main table already contains the four central rows. Keep their alternative
# uncertainty estimates explicitly, rather than repeating all twelve means.
old = section("Full Per-Environment Results")
tile = old[old.index("\\begin{table}[htbp]", old.index("\\caption{Tileworld")-30):]
# Use a precise boundary instead of coupling the proposal to caption offsets.
tile_start = old.rfind("\\begin{table}[htbp]", 0, old.index("\\caption{Tileworld"))
tile = old[tile_start:]
new = r"""\section{Additional Per-Environment Results}
\label{app:full_tables}

Table~\ref{tab:main} gives the four central agents on Tiger, Diagnosis, and Bandit. The table below adds the remaining baselines under the same $1{,}000$-episodes-per-seed, five-seed protocol. Untuned Info Gain is identical to Myopic, and Tiger's \texttt{pymdp}-AIF is identical to Posterior-vote. Complete rows remain in the environment CSVs.

\begin{table}[htbp]
\centering
\caption{Additional core baselines. Reward uncertainty is pooled episode-level SE, unlike the seed-level SE in Table~\ref{tab:main}. Tuned Info Gain maximizes success within its own class.}
\begin{tablebody}
\begin{tabular}{llccc}
\toprule
Environment & Agent & Obs. & Success & Reward \\
\midrule
Tiger & Info Gain ($w{=}20$) & $4.20$ & $99.4\%$ & $+5.19\pm0.12$ \\
& Epistemic-only & $0.00$ & $49.7\%$ & $-45.31\pm0.78$ \\
& Posterior-vote & $2.64$ & $96.8\%$ & $+3.79\pm0.28$ \\
\midrule
Diagnosis & Info Gain ($w{=}100$) & $13.19$ & $99.4\%$ & $-3.58\pm0.09$ \\
& Epistemic-only & $0.00$ & $24.7\%$ & $-35.16\pm0.37$ \\
& Posterior-vote & $5.83$ & $88.4\%$ & $-2.78\pm0.27$ \\
\midrule
Bandit & Info Gain ($w{=}20$) & $9.54$ & $98.8\%$ & $+5.12\pm0.04$ \\
& Epistemic-only & $0.00$ & $24.7\%$ & $+3.23\pm0.05$ \\
& Posterior-vote & $5.01$ & $87.0\%$ & $+6.32\pm0.05$ \\
\bottomrule
\end{tabular}
\end{tablebody}
\end{table}

For Table~\ref{tab:main}'s ordered rows (Myopic, Planning, Planning+IG, EFE), the corresponding pooled reward SEs are $(0.55,0.12,0.06,0.12)$ on Tiger, $(0.41,0.27,0.10,0.15)$ on Diagnosis, and $(0.06,0.06,0.04,0.05)$ on Bandit. These estimate episode-level precision rather than between-seed replicability. The two Tileworld tables retain their separate $500$-episodes-per-seed protocol.

""" + tile
add("early-01-core-table-consolidation", old, new,
    "Replace three repeated core tables by one table of additional baselines and a compact record of all omitted pooled SEs.",
    "Every original core mean remains either in main Table tab:main or the new table; all alternative pooled SEs are retained; both Tileworld tables remain unchanged.")

old = section("Supplementary Figures")
fstart = old.rfind("\\begin{figure}", 0, old.index("figures/fig_extended_efe.pdf"))
fend = old.index("\\end{figure}", fstart) + len("\\end{figure}")
extended = old[fstart:fend]
new = r"""\section{Supplementary Behavioral Checks}
\label{app:supp_figs}
\label{app:efe_trajectory}
\label{app:obs_scaling}
\label{app:tiger_sweep}
\label{app:tw_belief}
\label{app:foraging}

\paragraph{Test selection.} At fixed Diagnosis size $N{=}8$ and horizon $H{=}3$ (500 episodes), EFE and Planning are bit-identical with one test, within seed-level sampling error with two ($43.2\%$ vs.\ $43.8\%$ success), and separated with three ($96.0\%$ vs.\ $82.8\%$). This is a threshold pattern, not steady growth with test count. The main Diagnosis battery separately shows a gap with two tests. Figure~\ref{fig:extended_efe} shows how informative tests change within an episode. The chosen test maximizes the recursive score, not necessarily the one-step information gain in panel (b). The full scaling curves are archived in \texttt{results\_showcase\_obs\_scaling.csv}.

""" + extended + r"""

\paragraph{Reward asymmetry.} A Tiger sweep at $H{=}6$ uses 500 episodes per penalty and the five canonical seeds (\texttt{results\_showcase\_asymmetry.csv}). Across $|R^-|\in[1,500]$, EFE increases listening from $2.7$ to $5.8$ without reconfiguration. Success-tuning myopic Info Gain separately at each penalty selects $w{=}20$ throughout, with $4.37$ observations. Planning+IG reaches $5.77$ at penalties $200$ and $500$. At low stakes, EFE's extra listening costs about $1.6$ reward relative to Planning. At the largest penalty, myopic Info Gain nominally beats EFE ($4.61$ vs.\ $4.23$). The sweep demonstrates adaptation, not uniform dominance.

\paragraph{Trajectory diagnostics.} Illustrative Tiger traces commit when commit value exceeds recursive observe value, without a separate stopping rule. Selected Diagnosis traces all commit correctly, after $14$ observations for Planning, $29$ for EFE, and $32$ for tuned Info Gain. They were not selected to represent typical lengths. A separate 300-episode Diagnosis visualization ($N{=}8$, $K{=}3$) places EFE's observation-survival curve between Planning's and Planning+IG's. Entropy and cumulative-reward curves condition on episodes still running and display episode-level SE. That visualization transfers the myopic Info Gain weight selected on 100 tuning episodes to Planning+IG, unlike the main tables' own-class tuning. These diagnostic plots remain in \texttt{figures/fig\_efe\_trajectory.pdf}, \texttt{fig\_belief\_heatmap.pdf}, and \texttt{fig\_efficiency\_curves.pdf}. Tileworld's three-agent trace is Figure~\ref{fig:tw_comparison}.
"""
add("early-02-supplementary-illustrations", old, new,
    "Retain the mechanistically useful four-panel adaptive-test figure; replace five illustrative plots with their distinctive findings and archived paths.",
    "All unfavorable reward/asymmetry findings, finite test-count pattern, nonrepresentative trace caveat, conditional-mean plotting convention, and alternate tuning protocol remain. No removed figure is referenced outside this section.",
    removed_labels=["fig:traj","fig:obs_scaling","fig:sweep","fig:belief_heatmap","fig:efficiency"])

old = section("Navigation Results")
start = old.index("\\begin{table}")
end = old.index("\\end{table}",start)+len("\\end{table}")
new = r"""\section{Navigation Results}
\label{app:navigation}

Navigation has no separate sensing actions. Moving produces proximity-based warm/cold evidence about the hidden goal (Appendix~\ref{app:envs}).

""" + old[start:end] + r"""

NavMyopic moves toward the highest-probability cell and has the highest mean reward and success at every size. Its advantage over NavEFE at $5{\times}5$ survives seed-level Welch tests with Holm correction within metric (reward $p{=}0.002$, success $p{=}0.010$, observations $p{=}0.001$). No pairwise comparison survives correction at $3{\times}3$ or $7{\times}7$. NavEFE's nominal reward advantage over one-step NavInfoGain at $7{\times}7$ ($p{=}0.040$ uncorrected) also fails correction. Thus no epistemic agent significantly beats the myopic rule on these grids. This contrasts with tasks that offer several distinct sensing actions, while leaving causality between task structure and performance unresolved.
"""
add("early-03-navigation",old,new,"Remove repeated table values and speculative mechanism while retaining the negative navigation evidence.","Entire table, all significant comparisons, correction family, and lack of epistemic superiority remain.")

old = section("PyMDP Consistency Check")
new = r"""\section{PyMDP Consistency Check}
\label{app:pymdp}

The standard \texttt{pymdp} Agent \citep{heins2022}, wrapped for observe-then-commit tasks, matches myopic Info Gain at $w{=}1$ on Testbed under the canonical protocol ($3.15$ observations, $89.8\%$ success, $+0.480$ reward). Both also match reward-only Planning, whereas recursive $H{=}4$ EFE takes $5.50$ observations. Choices agree at the tested uniform, intermediate, and confident two-state beliefs, and information-gain evaluations agree qualitatively. This is a limited single-step consistency check, not certified numerical equivalence or validation of recursive EFE (\texttt{results\_summary.csv}).
"""
add("early-04-pymdp",old,new,"Collapse a small consistency check to its outcomes and exact inferential scope.","All numeric outcomes, weak-evidence caveat, agent/horizon distinction and citation preserved.")

old = section("Supplementary Statistics")
table_start=old.index("\\begin{table}")
new = old[:table_start]
paragraph_start=new.index("Table~\\ref{tab:main} reports seed-level SE.")
new=new[:paragraph_start]+r"""Table~\ref{tab:main} reports seed-level SE, while Appendix~\ref{app:full_tables} supplies pooled SE and additional baselines. The former describes between-seed replicability, the latter episode-level precision. Companion \texttt{*\_stats.csv} files contain tests and effect sizes. The separate Tileworld scaling battery has seed-level reward and success SEs but no Welch companion file.

\begin{table}[htbp]
\centering
\caption{Pooled episode-level Cohen's $d$, positive when EFE scores higher. Five reward columns compare EFE with the named agent. The final column compares success with Planning, treating outcomes as Bernoulli. Magnitudes below $0.2$, $0.5$, and $0.8$ are conventionally negligible, small, and medium, respectively.}
\label{tab:effect_sizes}
\begin{tablebody}
\begin{tabular}{lrrrrrr}
\toprule
& \multicolumn{5}{c}{Reward} & Success \\
Environment & Myopic & Planning & Tuned IG & Plan.+IG & Vote & Planning \\
\midrule
Tiger & $0.44$ & $0.00$ & $0.00$ & $0.14$ & $0.09$ & $0.00$ \\
Testbed & $-0.07$ & $-0.18$ & $0.69$ & $0.69$ & $-0.18$ & $0.26$ \\
Diagnosis & $0.55$ & $0.08$ & $0.25$ & $0.25$ & $0.09$ & $0.33$ \\
Bandit & $0.18$ & $0.14$ & $0.36$ & $0.37$ & $-0.01$ & $0.40$ \\
\bottomrule
\end{tabular}
\end{tablebody}
\end{table}
"""
add("early-05-effect-size-matrix",old,new,"Transpose the 24-row effect-size table into a four-row matrix and align table cross-references with consolidated core tables.","All 24 effect sizes and their sign conventions remain. Statistical protocol and all correction-family definitions remain verbatim.")

old=section("Reward-Rescaling Invariance")
table_start=old.index("\\begin{table}")
table=old[table_start:]
new=r"""\section{Reward-Rescaling Invariance}
\label{app:reward_scaling}

Multiplying all rewards and costs by $k$ preserves a policy when its information weight is also multiplied by $k$ (Proposition~\ref{prop:pi1}). A finite-grid reward sweep on Diagnosis and Bandit uses $k\in\{0.1,1,10\}$ and 200 episodes over each of three seeds per $(k,w)$ pair. Table~\ref{tab:reward_scaling} records the selected weights, with ties resolved toward the smallest maximizer. The normalized ratio is constant on Bandit and varies twofold on Diagnosis's flat plateaus. This is evidence about a finite grid, not a precise stability estimate. The full curves remain in \texttt{results\_reward\_scaling.csv} and \texttt{figures/fig\_reward\_scaling.pdf}. Section~\ref{sec:collapse} supplies the stronger usage-curve collapse check. Fixed $w{=}1$ is not scale invariant.

"""+table
# Repetition between the revised text and old caption has no evidential purpose.
cap_start=new.index("\\caption{")
cap_end=new.index("\n\\label{",cap_start)
new=new[:cap_start]+r"""\caption{Sampled reward-maximizing Planning+IG weights under global reward scale $k$. Flat plateaus can contain several grid maximizers.}"""+new[cap_end:]
add("early-06-rescaling-plot",old,new,"Remove the second scale-equivariance plot, whose qualitative conclusion repeats the stronger main usage-collapse experiment, while retaining its finite-grid table.","All six selected weights/ratios, sample sizes, plateau/tie caveat and lack of fixed-weight scale invariance remain.",removed_labels=["fig:reward_scaling"])

old=section("Information Base and the Nat-Canonical Agent")
new=r"""\section{Information Base and the Nat-Canonical Agent}
\label{app:nat_canonical}

Bit-unit $w{=}1$ equals $1/\ln2\approx1.44$ reward units per nat. The exactly nat-canonical policy instead uses bit-unit $w{=}\ln2\approx0.69$ (Section~\ref{subsec:formal_rho_equiv}). A direct comparison under the Pareto sweep protocol (500 episodes per seed over five seeds, \texttt{results\_nat\_canonical\_check.csv}) gives bit-identical reward, success, and usage on Tiger, Diagnosis, Bandit, and Testbed. Their respective reward/success pairs are $5.33/99.6\%$, $-1.26/97.4\%$, $6.24/86.9\%$, and $0.37/96.4\%$. This direct check matters on Bandit, where the nearest lower swept weight, $0.5$, scores $6.05$ rather than $6.24$. Both conventions remain below Testbed's sampled maximum $0.48$.

Tileworld changes policy. Nat-canonical EFE gives $-20.81$ reward, $74.7\%$ success, and $15.64$ scans, versus $-21.53$, $72.0\%$, and $14.75$ at bit-unit $w{=}1$. Only usage differs significantly (seed-level Welch $p{=}9.5{\times}10^{-5}$, surviving Holm over three metrics), with reward $p{=}0.34$ and success $p{=}0.070$. Both policies remain Pareto-dominated by sampled $w{=}20$, whose reward is $-18.95$ and success $91.8\%$. The unit check therefore preserves the paper's main positive and negative conclusions without implying policy invariance to information units.
"""
add("early-07-information-units",old,new,"Shorten the unit check by removing repeated interpretation of tied grid runs and derivational reminders.","Both conventions, direct off-grid check, all four exact ties, adverse Testbed result, Tileworld change and corrected significance scope remain.")

old=section("Discount Factor Sensitivity")
new=r"""\section{Discount Factor Sensitivity}
\label{app:discount}

We compare EFE with same-horizon Planning over four discounts using 500 episodes per seed and five canonical seeds (\texttt{experiments/run\_discount.py}). This is lighter than Table~\ref{tab:main}'s battery. Table~\ref{tab:discount} combines numerically identical settings but retains every measured outcome.

\begin{table}[htbp]
\centering
\caption{Discount sensitivity. Paired cells list EFE / Planning. Success gaps are percentage points, followed by seed-level Welch $p$. Stars denote significance after Holm correction over the battery's 24 tests.}
\label{tab:discount}
\begin{tablebody}
\begin{tabular}{llcccc}
\toprule
Environment & $\gamma$ & Obs. & Success (\%) & Reward & Gap ($p$) \\
\midrule
Tiger & $0.90$ & $4.23/2.65$ & $99.6/96.9$ & $5.33/3.91$ & $2.7$ ($<10^{-3}$)$^*$ \\
& $0.95,0.99,1$ & $4.23/4.23$ & $99.6/99.6$ & $5.33/5.33$ & $0.0$ ($1.0$) \\
\midrule
Diagnosis & $0.90,0.95$ & $5.83/5.86$ & $88.8/88.7$ & $-2.58/-2.62$ & $0.0$ ($0.96$) \\
& $0.99$ & $9.67/5.89$ & $97.5/89.6$ & $-1.19/-2.15$ & $7.9$ ($<10^{-4}$)$^*$ \\
& $1.00$ & $9.68/5.85$ & $97.4/88.8$ & $-1.26/-2.59$ & $8.6$ ($<10^{-4}$)$^*$ \\
\midrule
Bandit & $0.90,0.95$ & $2.04/2.04$ & $61.9/62.0$ & $5.55/5.56$ & $-0.2$ ($0.95$) \\
& $0.99$ & $5.16/2.38$ & $86.9/64.5$ & $6.24/5.61$ & $22.4$ ($<10^{-4}$)$^*$ \\
& $1.00$ & $5.16/3.24$ & $86.9/69.9$ & $6.24/5.67$ & $17.0$ ($<10^{-4}$)$^*$ \\
\bottomrule
\end{tabular}
\end{tablebody}
\end{table}

Tiger remains above $96\%$ success throughout. Diagnosis and Bandit show no significant gap at $\gamma\le0.95$, while their EFE advantage emerges at $\gamma\ge0.99$. On this grid, the effective horizon matters. Gaps use unrounded estimates and can differ from subtraction of the displayed percentages.
"""
add("early-08-discount-table",old,new,"Collapse 24 agent rows into eight paired rows, combining settings only when every printed outcome and p-value agrees.","Every original observation mean, success, reward, gap, p-value, significance marker, sample count, and discount remains. Added explicit rounding note prevents readers treating 0.0/0.1 discrepancies as errors.")

old=section("Model Misspecification Sensitivity")
diag_start=old.rfind("\\begin{table}",0,old.index("\\caption{Model misspecification on Diagnosis"))
diag_end=old.index("\\end{table}",diag_start)+len("\\end{table}")
diag=old[diag_start:diag_end]
new=r"""\section{Model Misspecification Sensitivity}
\label{app:misspec}
\label{tab:misspec-tiger}

We vary the agent's observation accuracy around the true value, holding the environment fixed. Both batteries use 500 episodes per seed over five seeds (\texttt{results\_model\_misspec.csv}). Reward uncertainties below are seed-level SE.

On Tiger ($p_{\mathrm{true}}{=}0.85$, $H{=}4$), EFE and Planning are bit-identical at every tested accuracy. For $p_{\mathrm{agent}}\in\{0.70,0.75,0.80,0.85\}$, both take $4.23$ observations, succeed on $99.6\%$, and earn $5.33\pm0.26$. At $0.90$ and $0.95$, both take $2.65$ observations, succeed on $96.9\%$, and earn $3.91\pm0.38$. The tested overestimates reduce sensing and performance, with no EFE-specific buffering.

"""+diag+r"""

Diagnosis ($p_{\mathrm{true}}{=}0.80$, $H{=}3$) also changes in steps. Mild underestimation and calibration give EFE the same $9.68$ tests and $97.4\%$ success. Its largest underestimate and both overestimates give $5.86$ tests and $88.7\%$ success. Planning's pattern is similar but not identical. These thresholds are therefore not specific to the epistemic term, and the experiment does not establish their mechanism.
"""
# The Tiger table's label is not referenced outside its replaced section.
new=new.replace("\\label{tab:misspec-tiger}\n", "")
add("early-09-misspecification",old,new,"Replace the fully redundant Tiger table with its two distinct outcome groups; keep the complete nontrivial Diagnosis table.","All six Tiger accuracy settings and their exact EFE/Planning ties, all outcomes and SEs, both protocols, and every Diagnosis row remain.",removed_labels=["tab:misspec-tiger"])

old=section("RockSample as an Interleaved Observe-Act Setting (Extended)")
new=r"""\section{RockSample as an Interleaved Observe-Act Setting (Extended)}
\label{app:rocksample}

Table~\ref{tab:rocksample_extended} extends Table~\ref{tab:rocksample} with counts, two higher weights, tuned POMCP, and its standalone rollout. Both tables use the same instance CSVs and \texttt{build\_rocksample\_tables.py}. Separate POMCP tuning, budget, horizon, and sensitivity CSVs support the diagnostics below.

\input{tables/rocksample_extended.tex}

Greedy samples without checking quality, taking $1.51$--$5.52$ bad rocks per episode across instances, versus EFE's $0.01$--$0.06$ (seed-level Welch $p<5{\times}10^{-8}$ at each instance). On RS[11,11], all tree-search agents instead use the low-activity policies described in Section~\ref{sec:rocksample}. Appendix~\ref{app:rocksample_main_details} gives the higher-weight and heuristic comparisons. At RS[7,8], increasing $w$ from $5$ to $10$ buys $0.54$ more good rocks but adds $17.2$ steps, each costing $0.5$. More sensing need not improve return.

\paragraph{POMCP implementation and selection.} The history tree uses UCB1, mean backup, and Monte Carlo rollout. Its depth bound shrinks near the episode cap, action masks remove wall bumps and invalid checks/samples, and subtrees are not promoted because their accumulated values use shorter horizons. These three departures depend on observable quantities. The default belief is the exact factored posterior. A literal unweighted rejection-sampling particle filter gives $12.93\pm0.25$ versus $12.81\pm0.43$ ($p{=}0.81$), so this comparison detects no belief-mode effect. Replacing the exit-valued depth-cap leaf by a greedy-belief leaf gives $14.52\pm0.34$, versus the frozen $12.81\pm0.43$ and standalone rollout's $17.16\pm0.44$. Neither comparison survives this sensitivity battery's per-metric Holm correction (uncorrected $p{=}0.015$ and $0.002$).

Three disjoint tuning seeds select rollout, exploration constant, horizon, and root criterion through a two-stage coordinate grid. The configuration is frozen before evaluation. The evaluation budget of 2{,}048 simulations is twice the tuning budget of 1{,}024 and is not itself tuned. At the full protocol on RS[5,3], frozen POMCP earns $12.74\pm0.11$ against EFE's $16.47\pm0.12$, at $46.6$ versus $1.76$ ms per decision. Its standalone approach-then-check rollout earns $16.67\pm0.13$ at $0.005$ ms, significantly above the search ($p{=}1.9{\times}10^{-14}$, surviving Holm). The position-independent $9.50$ exit option makes early exit attractive under mean backup. The search exits after $7.5$ steps, while its rollout follows a $13.5$-step collection tour.

\paragraph{Budget--horizon interaction.} A post-hoc RS[5,3] sweep on the canonical evaluation seeds finds frozen $H{=}10$ worst at both tested simulation tiers. At 16{,}384 simulations its reward is $12.52\pm0.26$, versus $15.60\pm0.37$, $15.24\pm0.39$, and $15.62\pm0.36$ for $H{=}15,25,40$. Increasing simulations beyond 1{,}024 reduces reward at $H{=}10$ (from $13.19$ to $12.52$) but helps at $H{=}15$ (from $14.00$ to $15.60$). Tuning horizon at a single budget missed this interaction. The diagnostic does not re-select the frozen configuration.

On RS[11,11], the corresponding post-hoc 2{,}048-simulation sweep gives the opposite result. Rewards at $H{=}10,15,25,40$ are $12.94\pm0.24$, $-7.54\pm1.20$, $-34.65\pm1.12$, and $-54.78\pm0.86$. Every decline survives Holm (seed-level Welch $p\le4.3{\times}10^{-5}$). The endpoints expand from $3.3$ steps and $1.6$ checks to $196$ steps and $144$ checks. The deepest tree collects only $3.4$ good rocks against the rollout's $5.2$, whose checks number $11$. Action costs overwhelm the collection return. The 16{,}384-simulation tier was not run on this instance because of its per-step cost.

\paragraph{Scope of the comparison.} Under the RS[5,3] diagnostic's matched five-seed, 100-episode protocol, EFE earns $16.90\pm0.45$ at $1.7$ ms per decision, against the best measured POMCP's roughly $15.6$ at $530$ ms. None of the reward differences survives Holm over nine diagnostic rows ($p{=}0.058$ against $H{=}15,40$ and $0.024$ against $H{=}25$ uncorrected). POMCP is also only $1.5$--$1.9$ reward below its standalone rollout at 16{,}384 simulations and $H\ge15$ (uncorrected $p{=}0.012$--$0.028$, none surviving the seed-level 36-comparison reward family). Its $H{=}25$ deficit survives only the pooled-level correction. Thus the apparent search gap on this instance depends substantially on computation and tuning.

On RS[11,11], the best measured alternative, 4{,}096 simulations at $H{=}10$, earns $13.14\pm0.15$, within sampling error of the frozen setting but $15.5$ below its rollout's $28.66\pm0.83$ ($p{=}3.2{\times}10^{-5}$, surviving Holm at both levels). These diagnostics limit conclusions about POMCP generally. They do not alter the predeclared table or show information weighting superior to the standalone heuristic.
"""
add("early-10-rocksample-diagnostics",old,new,"Consolidate the long RockSample narrative into implementation, tuning-interaction, and scope paragraphs. Leave the full extended table and all genuinely adverse diagnostics.","Preserves posterior/leaf fidelity checks, independent tuning and post-hoc qualification, rollout beating search, frozen-horizon handicap, its reversal on RS11, matched-protocol failure to reject reward difference, and exact correction families. Repeated per-instance timings and family comparisons remain in instance CSVs and the extended table/later RockSample section.")

old=section("IDS Baseline (Observe-then-Commit)")
tstart=old.index("\\begin{table}")
tend=old.index("\\end{table}",tstart)+len("\\end{table}")
table=old[tstart:tend]
cstart=table.index("\\caption{")
cend=table.index("\n\\label",cstart)
table=table[:cstart]+r"""\caption{Observe-then-commit IDS and matched controls, 500 episodes per canonical seed over five seeds. Reward is mean $\pm$ seed-level SE. Planning+IG uses the own-class success-tuned weights in \texttt{results\_supplementary\_tuned\_weights.csv}.}"""+table[cend:]
new=r"""\section{IDS Baseline (Observe-then-Commit)}
\label{app:ids}

Our adaptation of information-directed sampling \citep{russo2014} minimizes $\Delta^2/I$ over individual observation actions. Here $\Delta$ is the opportunity cost of observing rather than committing and $I$ measures information about the optimal commit. Unlike IDS over randomized action distributions, this deterministic argmin lacks the general role for randomization established by \citet{russo2018ids}. It also substitutes state-entropy gain when information about the optimal commit vanishes. The comparison therefore concerns this adaptation, not IDS in full generality.

"""+table+r"""

IDS exactly ties EFE and Planning on Tiger. On Diagnosis and Bandit it attains near-ceiling success with more observations and lower reward than EFE (seed-level Welch reward $p{=}0.0009$ and $1.5{\times}10^{-6}$). It resembles success-tuned Planning+IG on Diagnosis and has lower mean reward on Bandit. These results favor $w{=}1$ for reward on the two tested multi-observation instances under the stated units, without establishing a general advantage over information-ratio methods.
"""
add("early-11-ids",old,new,"Remove repeated table readings and scope the concluding default claim to the actual adapted baseline and tested instances.","Complete matched table, both departures from canonical randomized IDS, citations, p-values and negative generalization boundaries remain.")

old=section("POMCP Baseline Comparison")
tstart=old.index("\\begin{table}")
tend=old.index("\\end{table}",tstart)+len("\\end{table}")
table=old[tstart:tend]
cstart=table.index("\\caption{")
cend=table.index("\n\\label",cstart)
table=table[:cstart]+r"""\caption{POMCP at 1{,}000 simulations per decision. Five canonical seeds yield 5{,}000 episodes on each core environment and 1{,}000 on Tileworld. EFE/Planning are rerun inside this harness and reproduce Table~\ref{tab:main} on the core tasks. Reward uncertainty is seed-level SE. Bold identifies EFE and its exact Tiger tie with Planning, not column winners.}"""+table[cend:]
new=r"""\section{POMCP Baseline Comparison}
\label{app:pomcp}

Our observe-then-commit POMCP adaptation \citep{silver2010} has two fidelity gaps. The depth-cap leaf uses the best commit reward for the sampled state, an optimistic clairvoyant value. Rollout commits instead receive their belief-expected reward, replacing a sampled payoff by its conditional expectation. Their separate policy effects are not isolated. Rollouts start from the simulated path's updated belief, choose tests uniformly, and commit to the belief-optimal action with probability $0.3$ per step. Regression tests cover observation costs and path-belief initialization. The separate RockSample implementation has neither fidelity gap (Appendix~\ref{app:rocksample}).

The core battery uses UCB1 constant $10$, fixed without environment-specific tuning, depth cap $H{+}3$, and simulation counts $\{500,1000,2000,5000\}$. Each outer seed initializes both environment and planner randomness. Because reward scales vary, a fixed exploration constant has different effective strength across tasks. Simulation budgets do not match computation to exact EFE or Planning. Nor does this comparison isolate directed observation choice, since exact EFE also changes tree enumeration, beliefs, leaf values, and commit values.

"""+table+r"""

At 5{,}000 simulations, POMCP still reaches only $89.5\pm0.3\%$ success on Tiger, $71.6\pm0.9\%$ on Diagnosis, and $62.1\pm1.2\%$ on Bandit. No Tileworld budget exceeds $3.8\%$. Bandit's scaling is non-monotone, with success $50.9\pm1.1\%$, $47.2\pm1.0\%$, and $51.6\pm1.1\%$ at 500, 1{,}000, and 2{,}000 simulations. More computation at this fixed constant therefore does not close the gaps, but this does not bound a better-tuned POMCP.

\paragraph{Matched computation and ablation.} Appendix~\ref{app:interpretation} defines MCTS-EFE and reports its simulation-matched comparison. An uncontended same-machine control times MCTS-EFE(500) over five seeds and 200 episodes per seed at $13.87$s, with $97.7\pm0.5\%$ success. Calibration at 200/500/1{,}000 simulations selects POMCP(661), taking $13.88$s and attaining $88.0\pm0.6\%$ success and $-4.80\pm0.69$ reward. POMCP(500) takes $10.42$s and gives $88.1\pm0.2\%$ and $-4.67\pm0.19$. Seed-level Welch differences between those POMCP configurations are not significant (success $p{=}0.89$, reward $p{=}0.85$), while both trail MCTS-EFE on both metrics ($p<0.0001$). This is evidence at the tested constant and protocol. Exact EFE's own matched-battery reference is $99.9\%$ at $H{=}6$ and $64$ ms per episode. MCTS-EFE's measured Tiger success and usage remain $97.7\%$ and $3.735$ across horizons $6,8,10$ and simulation counts $200,500,1000$.

Table~\ref{tab:mcts-ablation} switches MCTS-EFE's in-tree information gain and max-backup independently. Neither changes success or reward detectably after Holm correction within metric across the three environments. Only Tiger usage changes significantly, from $3.73$ to $3.48$ without in-tree information gain ($p{=}0.0014$). Five seeds give limited sensitivity. The fixed EFE-greedy leaf, exact beliefs, and exact commit values remain candidate explanations, so the ablation cannot attribute the advantage to information gain throughout the tree.

\input{tables/mcts_ablation.tex}

\paragraph{Exploration and rollout sweep.} Table~\ref{tab:pomcp-sweep} sweeps constants $c\in\{1,2,5,10,20,50,R\}$ on Tiger, Diagnosis, and Tileworld, where $R$ is the commit reward range and MCTS-EFE's default. This $c$ is unrelated to sensing cost. Bandit is not swept. The informed rollout selects the largest exact one-step information gain. Outside the sweep, POMCP uses $c{=}10$ in Table~\ref{tab:pomcp} and $c{=}5$ in the MCTS battery. Planner randomness here follows the outer seed, whereas the earlier MCTS battery fixes the planner seed, so their POMCP rows need not coincide.

The selection rule maximizes success and then reward on seeds $\{11,22,33\}$ with 100 episodes each. It was recorded before selection, but both rule and grid followed inspection of the canonical-seed exploratory sweep. It selects MCTS-EFE $c{=}5$ on Tiger/Diagnosis and its default on Tileworld. POMCP selects $c{=}50$ with uniform rollouts on Tiger, $c{=}5$ with uniform rollouts on Diagnosis, and $c{=}5$ with informed rollouts on Tileworld (\texttt{select\_pomcp\_constants.py}). On the canonical evaluation seeds, selected MCTS-EFE retains higher Tiger success ($98.2\pm0.3\%$ vs.\ $93.2\pm0.5\%$, $p{=}0.0001$) and reward ($4.33\pm0.28$ vs.\ $0.39\pm0.52$, $p{=}0.0005$). Both survive Holm over the six selected success/reward comparisons. The selected Diagnosis and Tileworld comparisons also survive that correction. Their POMCP success rates are $65.6\pm1.4\%$ and $8.2\pm0.6\%$, against MCTS-EFE's $94.7\pm0.4\%$ and $95.4\pm0.6\%$.

Several qualifications matter. Diagnosis's evaluation-seed-best POMCP row ($c{=}2$, $69.1\pm1.7\%$) is not the tuning selection. Tileworld's best uniform constant is the grid's lower edge $c{=}1$, and lower constants were not tested. MCTS-EFE's default is not reward-optimal either, with Tileworld reward improving from $-25.02\pm0.25$ to $-22.26\pm0.46$ at $c{=}5$ ($p{=}0.0017$). Informed POMCP rollouts leave Tiger unchanged because it has one test. At $c{=}5$ they give no significant Diagnosis success gain ($p{=}0.57$), and improve Tileworld success but not reward after Holm (uncorrected $p{=}0.0002$ and $0.012$). None of these controls isolates all architectural differences.

\input{tables/pomcp_exploration_sweep.tex}
"""
add("early-12-pomcp",old,new,"Consolidate implementation caveats, computation controls and selection results, removing prose that repeats the retained full tables.","All three full tables remain. Keeps both fidelity gaps, seeding/protocol differences, fixed-constant limits, compute matching, null ablations, non-blind rule construction, disjoint tuning seeds, selected vs descriptive configurations, lower-edge caveat, and informed-rollout correction scope.")

# Generate explicit venue-specific guarded inputs and outputs. The sole surviving
# figure keeps LNCS's original full-width setting and omits JAIR accessibility.
import re
LNCS=(ROOT / "paper/full_paper.tex").read_text()
for item in proposals:
    if LNCS.count(item["old"]) == 1:
        continue
    title=re.search(r"\\section\{([^\n]*)\}",item["old"]).group(1)
    start=LNCS.index("\\section{"+title+"}")
    end=LNCS.find("\\FloatBarrier\n\\section{",start+1)
    item["old_lncs"]=LNCS[start:end]
    new_lncs=re.sub(r"^\\Description\{.*\}\n", "",item["new"],flags=re.M)
    new_lncs=new_lncs.replace(r"\includegraphics[width=0.78\linewidth]{figures/fig_extended_efe.pdf}",
                             r"\includegraphics[width=\linewidth]{figures/fig_extended_efe.pdf}")
    item["new_lncs"]=new_lncs
    assert LNCS.count(item["old_lncs"])==1

out=Path(__file__).with_name("early_proposals.json")
out.write_text(json.dumps(proposals,indent=2)+"\n")
print(f"Wrote {len(proposals)} guarded proposals to {out}")
