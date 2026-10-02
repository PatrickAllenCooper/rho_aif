from pathlib import Path
import json,re,subprocess
ROOT=Path('/Users/pat/code/rho_aif')
src=subprocess.check_output(['git','show','c5125ab:paper/full_paper_jair.tex'],cwd=ROOT,text=True)
proposals=[]
def block(start,end):
 a=src.index(start); b=src.index(end,a+len(start)); return src[a:b]
def propose(id,start,end,new,rationale,retained):
 old=block(start,end)
 proposals.append(dict(id=id,old=old,new=new.rstrip()+'\n\n',rationale=rationale,retained_evidence=retained))
def floats(start,end,kind):
 old=block(start,end)
 return '\n\n'.join(re.findall(r'\\begin\{'+kind+r'\}.*?\\end\{'+kind+r'\}',old,re.S))
A=r'\section{Extended Experimental Specifications and Protocols}'
B=r'\subsection{Retrospective Sensor-Acquisition Protocol}'
propose('late_protocol_dedup',A,B,r'''\section{Extended Experimental Specifications and Protocols}
\label{app:experimental_protocol}

Sections~\ref{sec:experiments} and Appendix~\ref{app:envs} specify the environments, episode counts and statistical protocol. Battery-specific counts and seeding differ, so estimates are not interchangeable. For example, Tiger EFE uses $4.20$ observations in Table~\ref{tab:main} and $4.32$ in Table~\ref{tab:sarsop}. All simulators use the Gymnasium Python interface \citep{towers2024}.

Our RockSample variant differs from \citet{smith2004} in six ways. Every action costs $0.5$, maps are fixed but our own, returns are undiscounted with cap $N^2+10K$, exit pays $+10$ from any cell, sampled rock qualities remain fixed, and sensor accuracy is $\max(0.5,0.95\,2^{-d/4})$ at Euclidean distance $d$. The original has free moves and checks, east-edge exit, a good rock becomes bad after sampling, and its sensor starts perfect and approaches chance asymptotically. Here the sensor reaches chance at about $3.7$ cells. Observable sample history prevents repeated sampling rewards. Good/bad sampling pays $+10/-10$, before action cost. These choices preserve hidden state but prevent comparison of absolute returns with published RockSample results. State counts include only the $2^K$ hidden quality vectors, not observable position.

Inspection has prior fault probability $0.3$, a $0.5$ move cost, and visual/detailed tests with accuracies $0.70/0.90$ and costs $0.5/2$. Correct nominal/fault declarations pay $2/5$, missed faults cost $50$ and false alarms cost $5$. Each component is declared once while the agent stands on it. An episode ends after all declarations or at the step cap. Tests and moves preserve component states. This remains a synthetic known-model benchmark.

\FloatBarrier
''','Remove descriptions and statistical boilerplate repeated verbatim in the main experiment setup. Retain RockSample departures and residual Inspection details.','Main Section 5 retains Tiger/Diagnosis/Bandit/Tileworld definitions, instance list and protocols. Here retains all six material RockSample departures, exact sensor rule, hidden-state count convention, and Inspection prior/payoffs/termination.')
# The real-sensor protocol stays untouched: its model and inferential details are load-bearing.
A=r'\subsection{Cost-Denominated Budgets}'; # occurs twice: use appendix-anchored extraction via full unique header+label
A='\\subsection{Cost-Denominated Budgets}\n\\label{app:cost_details}'
B=r'\subsection{Curve Collapse across Reward Scales}'; # first after A
old=block(A,B); fig=floats(A,B,'figure')
propose('late_cost',A,B,r'''\subsection{Cost-Denominated Budgets}
\label{app:cost_details}

Figure~\ref{fig:costbudget} gives the curves behind Section~\ref{sec:cost_budget}. Diagnosis tests cost $0.5$ and $2.5$ but retain equal accuracy. Targets are paired at the same fractional position in each curve's sampled range, with end margins ensuring a crossing. The changing test mix prevents a fixed count-to-cost conversion. Nevertheless, both tested pairs share brackets: the $12.0\%$ spread in mean cost per test does not move either crossing across a grid boundary. Adjacent positive weights differ by $\sqrt{10}$, so this coincidence does not imply interchangeable denominations.

'''+fig,'Replace four explanatory paragraphs repeating the main cost-budget result with one paragraph plus the full diagnostic figure.','Test costs, pairing rule, ratio spread, grid spacing, coincident brackets, uncertainty and no-fixed-conversion limitation remain in text/figure or main Section 6.3.')
A='\\subsection{Curve Collapse across Reward Scales}\n\\label{app:scale_details}';B=r'\subsection{Proposition~\ref{prop:nearopt} Onset on Positive-Threshold Two-State Instances}'
table=floats(A,B,'table')
propose('late_scale',A,B,r'''\subsection{Curve Collapse across Reward Scales}
\label{app:scale_details}

Table~\ref{tab:collapse-breadth} completes Section~\ref{sec:collapse}'s check on grids scaled by $\alpha\in\{0.1,1,10\}$, with per-episode shared streams. All matched usage values are bit-identical and normalized brackets coincide to floating-point precision ($\le10^{-15}$). Tiger is a trivial collapse with no crossing at $B=4$, showing that equivariance need not provide an adjustable usage range.

'''+table,'Remove repeated exposition while retaining breadth table cited by the main text.','Every environment, zero spread, brackets and Tiger negative control retained.')
A=B;B=r'\subsection{Interleaved Usage Curves}';fig=floats(A,B,'figure')
propose('late_onset',A,B,r'''\subsection{Proposition~\ref{prop:nearopt} Onset on Positive-Threshold Two-State Instances}
\label{sec:prop2exp}

The onset check uses two variants of Appendix~\ref{app:testbed}'s \texttt{InfoSeekingEnv}, with accuracy $p\in\{0.60,0.58\}$, cost $0.3$ and commit payoffs $\pm1$. The threshold formula remains applicable at reward asymmetry $\alpha=1$, although the proposition's strict-asymmetry condition does not. Thresholds are $3.44$ and $7.55$ reward units per bit, or $4.97$ and $10.89$ per nat. Usage is zero at and below each threshold and begins in $(w_{\mathrm{thresh}},1.03w_{\mathrm{thresh}}]$ on the refined grid (Figure~\ref{fig:prop2}). Standard Tiger and Testbed have negative thresholds and $U(0)>0$, providing the complementary sanity checks.

'''+fig,'Condense the numerical check to its parameters, unit conversion and actual findings.','Boundary asymmetry condition, both threshold values/unit systems, 3% bracket and negative-threshold controls retained.')
A=B;B=r'\subsection{Multi-Seed Online Dual Control under Reward Rescale}';fig=floats(A,B,'figure')
propose('late_interleaved',A,B,r'''\subsection{Interleaved Usage Curves}
\label{app:interleaved_details}

Figure~\ref{fig:interleaved} uses five common seeds. At each grid weight, RockSample[5,3] has $50$ episodes on a ten-point grid, RockSample[7,4] has $30$ on eight points, and Inspection-$N=16$ has $50$ on ten points. Four budgets per instance are placed evenly inside the sampled range, with narrower end margins than the count/cost study. Usage SEs are evaluated at the plotted grid weights, not interpreted as price uncertainty.

Section~\ref{sec:interleaved_budget} reports the ranges and RockSample[5,3]'s nonmonotone dip below $U(0)$. Only the other two sampled curves attain their minimum at $w=0$. The lowest RockSample[5,3] target is attainable but marked slack because its nearest sampled usage occurs at $w=0$, below the crossing bracket. None of these observations bounds untested weights. This study uses Inspection-$N=16$, complementing the $N=8$ staircase in Section~\ref{sec:stairs}.

'''+fig,'Remove repeated usage-range and monotonicity explanations already in main Section 6.4.','Grid and episode counts, shared seeds, target-placement distinction, SE interpretation, nonmonotone exception, slack-marker meaning and two Inspection sizes retained.')
A=B;B=r'\subsection{SARSOP as a Near-Optimal Offline Reference}'
propose('late_dual',A,B,r'''\subsection{Multi-Seed Online Dual Control under Reward Rescale}
\label{app:dual_details}

Section~\ref{sec:dual_multiseed} gives the complete detector, recovery definition and paired restricted-time comparison. All ten pairs favor reset, by at least $89$ episodes. Decay-only recovers on nine seeds, two only at index $180$. Its remaining seed ends within tolerance without completing the required hold. Thus its restricted mean of $157.3$ is a lower bound on these ten runs' unrestricted recovery time, not a population bound. Among the nine recovered seeds, the descriptive mean is $154.8$ with normal-approximation $95\%$ CI $[142.7,166.9]$. Every reset run triggers once and recovers, giving $51.2$ and $[46.1,56.3]$. These separate intervals do not quantify the ratio.

Over the fixed final steady-state block, $|U-B|$ is $0.06$ with CI $[0.024,0.096]$ under reset and $0.39$ with $[0.118,0.666]$ under decay. Before the shift it is $0.10$ with $[0.051,0.149]$ for both. These are normal-approximation intervals across controller seeds. Reset has lower final error on five seeds, ties on four and is worse on one. The restricted-time paired interval in the main text instead uses Student's $t$ distribution. Metrics and the per-episode-seeded traces are archived in \texttt{results\_\allowbreak price\_\allowbreak dual\_\allowbreak multiseed\_\allowbreak metrics.csv} and its companion outputs. Neither shifted run falls under the stationary guarantee of Proposition~\ref{prop:pi5}.
''','Retain residual censoring and steady-state evidence while citing the main text for protocol and primary estimand.','Every adverse seed/censoring qualification, all CI types and steady-state seed counts retained. No duplicate recovery formula or causal narrative.')
A=B;B=r'\subsection{A Near-Optimal Constrained-POMDP Reference}';table=floats(A,B,'table')
propose('late_sarsop',A,B,r'''\subsection{SARSOP as a Near-Optimal Offline Reference}
\label{app:sarsop_details}

Table~\ref{tab:sarsop} gives the five-seed comparison. The common export, $\gamma=0.999$ solve and alpha-vector evaluation are specified in Appendix~\ref{app:sarsop_build}. The initial-belief value-bound gap reaches $10^{-3}$ in under one second per environment.

'''+table+r'''

The unpaired Welch TOST uses the margins of Section~\ref{sec:sarsop}. The larger one-sided $p$-values on Tiger, Diagnosis and Bandit are $0.0010$, $0.0458$ and $0.0130$, all surviving Holm correction. Their $90\%$ difference intervals are $[-0.41,0.41]$, $[-0.51,0.98]$ and $[-0.35,0.31]$, strictly inside the respective margins. The five-seed margins were chosen retrospectively. Fifteen additional seeds were fixed after the margin and before the $n=20$ study, which gives $p=4.5\times10^{-10}$, $6.8\times10^{-7}$ and $6.0\times10^{-11}$ (\texttt{results\_\allowbreak tost\_\allowbreak sarsop.csv} and \texttt{results\_\allowbreak tost\_\allowbreak sarsop\_\allowbreak n20\_\allowbreak robustness.csv}, each with per-seed archives).

Shared seed labels do not match episodes when policies consume random draws differently. A five-seed paired sensitivity check gives identically zero Tiger differences, and $p=0.016$ on Diagnosis and $3.6\times10^{-5}$ on Bandit. Its SEs of $0.24/0.03$ are below the unpaired $0.38/0.18$, so the unpaired analysis is conservative on these samples, not by design.

The predeclared episode-matched check resets episode $e$ of seed $s$ at $10^4s+e$, matching hidden states and observation draws while actions agree. It uses the same twenty seeds, $500$ episodes each and fixed margins. Tiger again acts identically. Diagnosis's paired difference is $+0.11\pm0.09$ with $p_{\mathrm{TOST}}=3.2\times10^{-9}$, and Bandit's is $+0.04\pm0.03$ with $p=4.6\times10^{-12}$ (SE). Unpaired tests on those runs also support equivalence ($3.8\times10^{-5}$ and $1.8\times10^{-8}$). Results and per-seed inputs are in \texttt{results\_\allowbreak tost\_\allowbreak sarsop\_\allowbreak episode\_\allowbreak paired.csv} and its companion file.

Tiger has no usage-matched crossing on the offline grid: SARSOP's $4.32$ is below the sampled floor $4.37$, within one usage SE. The ``usage-matched'' $w=0$ row in \texttt{results\_\allowbreak sarsop\_\allowbreak baseline.json} is therefore a low-end fallback, not an attained target.
''','Consolidate repeated methodological explanation into one compact evidence record, retaining all test designs and diagnostic results.','Original table, TOST margins via main pointer, retrospective/prospective distinctions, unpaired/paired/episode-matched designs, numeric p-values and CIs, archives, fallback warning retained.')
A=B;B=r'\subsection{Calibration-Derived Target Budgets and What Calibration Buys}';table=floats(A,B,'table')
propose('late_cpomdp',A,B,r'''\subsection{A Near-Optimal Constrained-POMDP Reference}
\label{app:cpomdp_details}

Section~\ref{sec:cpomdp} defines the penalty sweep and feasible-envelope LP. An exact maximizer of $R-\lambda U$ is reward-optimal under a cap at its own usage. Our approximately solved, noisily evaluated points do not inherit a certified bound, and a finite penalty grid need not recover the full frontier. No zero duality gap is assumed for the continuous belief MDP. Maximizing over noisy points also introduces selection bias.

'''+table+r'''

At $B_{\mathrm{EFE}}$, the envelope chooses the single $\lambda=0$ policy on Tiger and Bandit and $\lambda=0.05$ on Diagnosis. The cap does not bind: usage equals EFE's on Tiger and is lower on the other two. In Diagnosis, reference and EFE usages are $9.785/9.824$. Reward SEs of $0.12$--$0.39$ exceed the displayed gaps. Negative estimated gaps can reflect sampling or reference approximation rather than reward beyond the population constrained optimum.

The actually evaluated usage-matched Planning+IG weights are $0.00$, $0.45$ and $1.07$. They lie on sampled usage plateaus $[0,19.3]$, $[0.316,19.3]$ and $[0.72,1.64]$ containing $w=1$, and their archived rewards equal EFE's. This is a measurement, not an equivalence theorem for other weights. The shared \texttt{feasible\_\allowbreak envelope} routine in \texttt{rho\_\allowbreak aif/budget.py} produces the reference from \texttt{results\_\allowbreak cpomdp\_\allowbreak frontier.csv}, with comparisons in \texttt{results\_\allowbreak cpomdp\_\allowbreak baseline.csv}. No comparable constrained reference is available for the larger RockSample or Inspection instances.
''','Delete extended definitions of a constrained POMDP, duality, envelopes and penalty sweep already stated in Sections 4 and 6.7.','At-most-two-support envelope and grid protocol remain in main. Table, nonbinding-cap evidence, negative-gap caveat, measured plateau caveat and solver scope retained.')
A=B;B=r'\subsection{Distractor Robustness under Reward-Irrelevant Sensing}'
propose('late_frontier',A,B,r'''\subsection{Calibration-Derived Target Budgets and What Calibration Buys}
\label{app:frontier_details}

Table~\ref{tab:budget_frontier} completes the comparisons in Section~\ref{sec:budget_frontier}. That section specifies calibration-derived targets, held-out seeds, the original endpoint and feasible-member policies, and the two LP mixtures added after inspection. All selections remain confined to the calibration grid. The best equality mixture coincides with the selected endpoint mixture at eleven of twelve targets, allowing equivalent plateau endpoints. Bandit's gap target is the exception. The best feasible mixture equals the best feasible member at every slack target, the endpoint mixture at the three binding Diagnosis targets, and the best equality mixture at Bandit's gap target.

Bandit's last-crossing rule matters at $B=5.51$. Usage first crosses between $w=0.06$ and $0.14$, falls to $5.11$ on the $[0.72,1.64]$ plateau, then crosses again in the reported $(1.64,3.73]$ bracket. At $B=4.71$, the only crossing is $(0.06,0.14]$. Tiger's gap target duplicates its middle target, leaving eleven distinct attainable budgets.

The committed-reference column uses canonical once-per-seed streams, whereas the family uses held-out per-episode streams. It is descriptive. The same-stream reference was added after inspection, after every saved policy reproduced its committed reward to $10^{-9}$. Its paired intervals hold fitted supports and probabilities fixed, omitting their selection uncertainty, cap-feasibility uncertainty and multiplicity. As detailed in the main text, the Tiger reference changes from $5.02$ to $5.68$ across streams. The canonical wrong-commit rate of $0.6\%$ accounts for about $0.66$ expected reward, almost the full difference. No held-out Tiger support policy errs, so its nominal intervals omit important rare-event uncertainty.

A predeclared fresh-seed replication first reproduces all twelve held-out paired gaps to $10^{-9}$, then freezes the mixture/reference supports and evaluates seeds $12$--$21$, $100$ episodes each, using $9$ degrees of freedom. Eight of eleven distinct cap gaps again exclude zero, but the Diagnosis rows change. Its $0.75$ gap remains negative at $-0.82\pm0.28$, the $0.5$ gap moves from $-0.76$ to $+0.02\pm0.29$, the smallest target becomes negative at $-0.56\pm0.24$, and the gap target narrowly includes zero at $-0.46\pm0.20$ (SE). Tiger's and Bandit's three negative intervals recur, while Bandit's smallest target again includes zero. One Diagnosis policy pair had already been evaluated on these fresh seeds before the replication was specified, so that pair is not blind. A wrong diagnosis changes reward by $60$, making these small samples sensitive to few errors. The replication supports the count, not the identity of deficient Diagnosis targets (\texttt{results\_\allowbreak budget\_\allowbreak frontier\_\allowbreak fresh\_\allowbreak seed\_\allowbreak replication.csv}).

The predeclared target-matched reference adds eleven subsidies $\lambda=-cs$, with $s$ from $0.1$ to $0.98$ and observation cost $c$, keeping net observation reward negative. Maximum held-out usages become $7.17$, $16.58$ and $11.59$ on Tiger, Diagnosis and Bandit. Equality-mixture supports are fitted on held-out usage and frozen for the fresh stream. They coincide with the cap reference at four binding budgets and include a subsidized policy at the seven slack budgets. No slack-budget target-gap interval excludes zero on either stream. The two held-out shortfalls are Diagnosis at $B=9.53$ and Bandit's gap target. The two fresh shortfalls are Diagnosis at $B=7.72$ ($-0.56\pm0.24$) and Bandit's gap target ($-0.50\pm0.11$). Only Bandit's recurs.

A post hoc analysis refits the equality reference at each mixture's realized held-out usage rather than at $B$, using no new episodes. Every held-out Tiger mean gap then becomes zero, because rewards there equal $10$ minus usage. Diagnosis still falls short at $B=9.53$ held out and $B=7.72$ fresh. Bandit's gap-target interval reaches $+0.001$ held out but remains negative fresh. Target gaps thus include usage mismatch, and neither fitted reference certifies the population constrained frontier. These comparisons are archived in \texttt{results\_\allowbreak budget\_\allowbreak frontier\_\allowbreak target\_\allowbreak reference.csv} and its \texttt{usage\_\allowbreak matched} companion, with subsidized points in \texttt{results\_\allowbreak cpomdp\_\allowbreak frontier\_\allowbreak subsidy.csv}.

\input{tables/budget_frontier.tex}
''','Replace repeated row-by-row main/table narration by residual selection and replication evidence. Keep all three-panel table inputs intact.','All methodological amendments, selection-vs-evaluation distinctions, last crossing, same-stream bias, rare-event caveat, changing Diagnosis replication, nonblind pair, target-vs-cap construction, and usage-matched adverse result retained. Main and full table retain all original means.')
A=B;B='\\FloatBarrier\n\\section{Extended EFE Comparisons}'
propose('late_distractor',A,B,r'''\subsection{Distractor Robustness under Reward-Irrelevant Sensing}
\label{app:distractor_details}

Section~\ref{sec:distractor} gives the refined-grid protocol, curves, relevance partition and corrected comparison family. Appendix~\ref{app:distractor} establishes the factorization guarantee. The relevance variant changes only the belief on which information gain is scored,
\[
\tilde I_a(b)=\mathbb E_{o\sim Q(\cdot\mid b,a)}D_{\mathrm{KL}}\!\left[Q(s_{\mathrm{rel}}\mid b,o,a)\,\|\,Q(s_{\mathrm{rel}}\mid b,a)\right],
\]
where $s_{\mathrm{rel}}$ is the reward-equivalence class determined by commit payoffs. The lookahead still propagates the full joint posterior.

The remaining reward pairs, ordinary versus relevance-weighted information gain, are $-2.45/-1.45$ at $w=4$ and $-4.31/-1.45$ at both $w=5$ and $10$. These nominal improvements do not survive Holm correction over all weights and reported metrics. At $w=100$, success is $98.4\%/99.2\%$, also not significantly different. Reward differences survive only at $31.6$ and $100$, as reported in the main text.

The IDS adaptation's \texttt{info\_\allowbreak astar} correctly vanishes for the distractor, but its near-zero-denominator fallback to \texttt{info\_\allowbreak state} rewards nuisance information. Its distractor fraction is $0.305\pm0.005$, versus ordinary information gain's saturated $0.330$--$0.332$ (SE $0.004$--$0.005$). The relevance variant has no fallback and buys zero distractor tests. This isolates a flaw in that IDS implementation pattern, not in reward-aware information measures generally. Appendix~\ref{app:ids} reports its broader results.
''','Eliminate duplicated main study exposition; retain exact marginal score and remaining nonsignificant findings.','Factorization scope, known reward-class requirement, formula, non-significant low-weight reward gains, nonsignificant success gap, and IDS fallback limitation retained.')
A=r'\subsection{Core Environments}'; # unique appendix anchor
A='\\subsection{Core Environments}\n\\label{app:core_details}';B=r'\subsection{Pareto Analysis and the Information-Unit Weight $w{=}1$}'
propose('late_core',A,B,r'''\subsection{Core Environments}
\label{app:core_details}

Appendix~\ref{app:full_tables} adds the baselines omitted from Table~\ref{tab:main} and prints pooled episode-level SE rather than seed-level SE. It omits untuned Info Gain rows identical to Myopic and Tiger's \texttt{pymdp}-AIF row identical to Posterior-vote. Both uncertainty summaries remain in the CSVs.

Posterior-vote is a relevant negative control. On Bandit it is not significantly different from EFE on reward ($6.32/6.27$, $p=0.58$), success ($87.0\%/86.9\%$, $p=0.97$) or usage ($5.01/5.11$, $p=0.30$). On Testbed it ties Planning exactly and beats EFE. On Diagnosis and Tiger its rewards are instead $-2.78$ and $3.79$, against EFE's $-1.37$ and $5.19$. Epistemic-only commits immediately at chance on Tiger, Diagnosis, Bandit and Tileworld, so removing reward-aware stopping causes non-exploration in this implementation.

Table~\ref{tab:effect_sizes} reports pooled effect sizes. EFE/Planning reward effects are zero on Tiger and below $0.15$ in magnitude on Diagnosis and Bandit, despite corrected seed-level reward and success differences on the latter two. The large Tileworld-$8\times8$ reward effect ($|d|=1.13$) compares EFE with a non-scanning planner. Equal episodes per seed make pooled and seed-level mean differences identical, so sign agreement is no independent check. Inference uses seed-level tests and intervals, not Cohen's $d$ computed from only five seed means.
''','Remove repeat explanations of main comparisons and statistics appendix while retaining competitor ties and effect-size cautions.','Posterior-vote ties/superiority and failed transfer, Epistemic-only chance stopping, pooled-vs-seed distinction, duplicate-row policy, small effects and 8x8 horizon limitation retained.')
A=B;B=r'\subsection{Spatial Epistemic Foraging on Tileworld}'
propose('late_pareto',A,B,r'''\subsection{Pareto Analysis and the Information-Unit Weight $w{=}1$}
\label{app:pareto_details}

Section~\ref{sec:pareto} and Figure~\ref{fig:pareto} give the eleven-weight sweep on five environments, excluding RockSample and Inspection. Success peaks at the grid's upper endpoint $w=200$ throughout. Moving to $w=50$ on Tiger and Diagnosis gains at most $1.8$ percentage points of accuracy while costing $1.07$ and $2.41$ reward. Bandit's $w=5$ gains $9.8$ points for $0.41$ reward. Tileworld instead maximizes sampled reward at $20$, while Testbed's maximizing run includes $0$. These are sampled-grid trade-offs, leaving intermediate weights unresolved. The three reward-maximizing runs containing $w=1$ do not establish success optimality or a scale-free default.
''','Replace duplicate sweep interpretation with residual reward-success tradeoff numbers.','All five environments, endpoint success maximum, two adverse reward exceptions and no-unsampled-optimality scope retained.')
A=B;B=r'\subsection{RockSample as an Interleaved Observe-Act Setting}';table=floats(A,B,'table');fig=floats(A,B,'figure')
propose('late_tileworld',A,B,r'''\subsection{Spatial Epistemic Foraging on Tileworld}
\label{app:tileworld_details}

Table~\ref{tab:tileworld} and Figure~\ref{fig:tw_comparison} complement Section~\ref{sec:tileworld}. EFE and Planning do not separate on reward ($p=0.82$) or success ($p=0.17$) at $6\times6$, while EFE uses fewer scans ($14.75/15.64$, seed-level $p=8.8\times10^{-5}$). These are failures to reject differences, not demonstrated equivalence. The figure's InfoGain-Tuned row is the myopic agent at its own tuned weight, distinct from the tree-search Planning+IG table row.

'''+table+'\n\n'+fig+r'''

The separate scaling sweep fixes $H=2$ and $w=100$ for both weighted agents, even though one series retains the name InfoGain-Tuned. It uses the smaller episode count in Figure~\ref{fig:tw_scaling}, not the full-table protocol. At $4\times4$ and $6\times6$, EFE and Planning reward and success are within one SE without formal tests for this sweep. At $8\times8$, Planning takes no scans and matches Myopic exactly ($1.4\%$ success, $-49.16$ reward), while EFE reaches $69.4\%\pm1.0$ points. A two-scan lookahead cannot sufficiently concentrate the initially uniform belief over $64$ cells, so this is a horizon-and-scale result rather than evidence against deeper reward planning. The fixed-$100$ Planning+IG series reaches $97.8\%$ success at a substantial reward cost.

A separate $6\times6$ partition study uses $H=2$, five seeds and $200$ episodes per seed. Random partitions assign cells to equal halves, losing guaranteed joint identification. Overlapping partitions threshold random weighted row/column coordinates, creating correlated tilted cuts. These replace the complementary bit partitions while keeping the rest of the benchmark fixed (\texttt{experiments/\allowbreak run\_\allowbreak tileworld.py partition}). EFE/Planning rewards, with seed-level SE, are $-21.62\pm0.87/-21.41\pm0.64$ for bitwise, $-29.31\pm0.43/-30.32\pm0.66$ for random and $-47.53\pm0.73/-47.66\pm0.68$ for overlapping partitions. Success is $71.9/73.6\%$, $56.1/55.1\%$ and $8.5/8.4\%$, respectively. No mode separates them on reward or success. The largest reward gap, under random partitions, has Welch $p=0.24$. EFE's scan counts are lower in all three ($14.76/15.57$, $12.97/13.38$, $2.63/2.70$). Absolute performance falls sharply with less complementary observations, so this study does not establish model-independent advantage (\texttt{results\_\allowbreak partition\_\allowbreak sensitivity\_\allowbreak 6x6.csv}).
''','Consolidate scaling interpretation and partition definitions while retaining all adverse partition outcomes and table/figure.','Full current table and belief figure preserved. Separate protocols, fixed-weight naming caveat, no-scan 8x8 competitor, all partition reward/success/usage values and nonsignificance retained.')
A=B;B=r'\subsection{Structural Inspection}'
propose('late_rocksample',A,B,r'''\subsection{RockSample as an Interleaved Observe-Act Setting}
\label{app:rocksample_main_details}

The weighted agents use independent per-rock beliefs and the tabled search depths. They share a leaf rule that repeatedly chooses an unsampled rock with positive belief-weighted sample value, subtracts travel cost, visits the best remaining rock and samples it, then exits when none remains. The leaf also charges travel to the east edge before exit, although the environment allows exit anywhere. This deflates depth-capped continuations relative to immediate exit and biases the entire family toward early exit. All weighted agents use this same leaf rule.

The standalone heuristic in Table~\ref{tab:rocksample} is POMCP's approach-then-check rollout without a tree. It approaches the unresolved rock with highest belief per unit distance, checks nearby at accuracy $0.95$, samples above its belief threshold, abandons rocks below $0.15$ and exits when none remains. It is a hand-coded policy without a search horizon. Greedy instead samples without checking. Appendix~\ref{app:rocksample} gives the POMCP protocol and sensitivity studies.

On RS[5,3], EFE and $w=5$ are not significantly different ($16.47/16.41$, Welch $p=0.74$). On RS[7,4], EFE leads $w=5$ ($15.96/14.56$, $p<10^{-5}$) and is not significantly different from the heuristic ($15.85$, $p=0.65$). On RS[7,8], EFE and $w=5$ ($21.85/23.76$, uncorrected $p=0.09$) both fall below the heuristic's $28.33\pm0.82$, with Holm-significant $p=4.6\times10^{-4}$ and $2.4\times10^{-3}$. These non-rejections are not equivalence tests. Raising $w$ from $5$ to $10$ hurts on RS[7,8] ($20.55$, $p=0.003$) and RS[5,3] ($14.60$, $p=3.5\times10^{-9}$), surviving the per-metric Holm family, while RS[7,4] does not separate ($p=0.18$). The three tested weights establish no dense-grid optimum.

On RS[11,11], Planning and EFE both earn $13.23$ while the heuristic earns $28.66\pm0.83$. A depth-three rerun leaves Planning/EFE at $13.23$ and Planning+IG at $13.17$, within one SE of the shallower results (\texttt{results\_\allowbreak rocksample\_\allowbreak 11x11\_\allowbreak depth3\_\allowbreak check.csv}). The heuristic collects $5.22$ good rocks against about half a rock for each tree-search agent. Useful distant checks require travel beyond the tested exact-search horizons. At the uniform prior, each untouched rock has zero expected sampling reward and fails the leaf's positive-value filter, compounded by the phantom exit cost. These observations support a horizon-and-leaf limitation, not absence of exploitable reward. The adverse deeper-POMCP results in Appendix~\ref{app:rocksample} show that additional reach alone does not resolve it. Across the four RockSample instances and three Tileworld sizes, this is a mechanistic interpretation of representable sensing opportunities, not an independently tested scaling law.
''','Remove repeated main/early-appendix result interpretation, keep the shared-leaf disclosure and precise weight/heuristic comparisons.','Phantom exit cost, hand-coded standalone heuristic, significantly suboptimal weighted family, dense-tuning caveat, depth3 null check, good-rock disparity and noncausal/generalization scope retained.')
A='\\subsection{Structural Inspection}\n\\label{app:inspection_details}';B='\\FloatBarrier\n\\section{Additional Interpretation and Tree-Search Controls}'
propose('late_inspection',A,B,r'''\subsection{Structural Inspection}
\label{app:inspection_details}

The tree-search agents share a hand-coded greedy completion rule and differ only in information weight. Table~\ref{tab:inspection}'s Missed column counts faulty components declared nominal, and Tests counts all tests per episode. EFE's accuracy gain over Planning has seed-level Welch $p<10^{-10}$ at $N=8$ and $p<10^{-7}$ at $N=16$. At $N=16$, $w=5$ uses $38.3\pm0.05$ tests against EFE's $28.1\pm0.09$ ($p=1.7\times10^{-11}$, SE), while EFE and Planning do not separate on reward ($p=0.57$).

Applying Proposition~\ref{prop:nearopt} here is only a heuristic two-state reduction. The nominal declaration has reward asymmetry $|R^-|/R^+=25$, but fault declaration is symmetric, with ratio $1$. The missed-fault penalty can therefore remove Part (a)'s lower-threshold restriction. Part (b)'s over-observation threshold is not evaluated, so this does not place $w=1$ inside the full near-optimality interval or establish deployment relevance.
''','Keep residual statistics and qualified threshold reading while removing task description and main-result repetition.','Shared known-model/leaf comparison, accuracy p-values, costly higher-weight tests, non-significant reward difference and unevaluated upper threshold retained.')
A=r'\subsection{The Information-Unit Weight and Tuning}';B=r'\subsection{Zero-Shot Weight Transfer}'
propose('late_tuning',A,B,r'''\subsection{The Information-Unit Weight and Tuning}

Weight transfer requires matching reward/information units and the planning configuration. At $w=100$ on Bandit, depth-two Planning+IG uses $12.36$ inspections against myopic Info Gain's $11.50$ (canonical five-seed Welch $p=0.003$, \texttt{experiments/\allowbreak run\_\allowbreak bandit\_\allowbreak w100\_\allowbreak depth\_\allowbreak comparison.py}). This is evidence that a weight tuned at one depth need not retain its usage at another. Appendix~\ref{app:discount} gives the separate discount sweep. Diagnosis and Bandit success gains appear at $\gamma\in\{0.99,1\}$ but not $\{0.90,0.95\}$, a result for those tested configurations rather than a general discount threshold.
''','Remove repeated canonical-weight positioning and generic tuning discussion while retaining the unique depth measurement.','Unique 12.36/11.50/p=.003 result, depth transfer limitation and localized discount claim retained.')
A=B;B=r'\subsection{Approximate Planning with MCTS-EFE}';table=floats(A,B,'table')
propose('late_transfer',A,B,r'''\subsection{Zero-Shot Weight Transfer}

Table~\ref{tab:transfer} transfers weights tuned within the evaluated Planning+IG class. Under this shared reward convention, moderate weights lie on flat reward regions, whereas the success-tuned $w=50$ harms reward, including on its tuning environments. This is neither scale-free calibration nor evidence that the canonical weight is optimal everywhere.

'''+table+r'''

Proposition~\ref{prop:nearopt}'s lower threshold concerns $H=1$ and its interval concerns $H=2$. Their two-state scope and heuristic reductions are detailed in Appendix~\ref{app:theory_thresholds}. The random-environment study of Appendix~\ref{app:nearopt_horizon} instead uses an empirical reward-gap criterion: $w=1$ passes on $30\%$, $58\%$ and $79\%$ of the $100$ sampled environments at depths $1$, $2$ and $3$. Thus greater depth still leaves about one fifth failing. Expected-usage calibration addresses a different requirement and remains conditional on target attainability within the selected family.
''','Keep the complete transfer table, replace two repetitive interpretations and speculative real-world extrapolation with the finite-horizon limitation.','Every transferred weight/reward/SE remains in table. Class-consistent tuning, reward convention, two horizon scopes and 21% depth3 failure remain.')
A=B;B='\\FloatBarrier\n\\section{Reproducibility Checklist for JAIR}'
propose('late_mcts',A,B,r'''\subsection{Approximate Planning with MCTS-EFE}

Exact enumeration costs $\mathcal O((K|\mathcal O|)^H)$ for $K$ sensing actions with $|\mathcal O|$ outcomes each. MCTS-EFE uses UCB1 over observe/commit actions, enumerates each observation action's outcomes, adds exact per-node information gain, and backs up maxima. EFE-greedy leaf rollouts compare immediate commitment with the best one-step EFE observation. Commit-child values are exact belief-expected rewards. The default exploration constant is the fixed commit-reward range, $110$ on Tiger, rather than the preliminary-return range used by \citet{silver2010}. Appendix~\ref{app:pomcp} reports exploration tuning, informed rollouts, the ablation and a separate compute-matched Tiger control.

The simulation-matched comparison uses $500$ simulations on Tiger at $H=10$. MCTS-EFE reaches $97.7\%\pm0.5$ percentage points against POMCP's $88.1\%\pm0.2$ ($p=4.4\times10^{-6}$). Its cost is $14$--$16$ ms per episode across tested horizons, versus $11$--$12$ ms for POMCP, so matching simulations does not match computation. At $H=5$ and $200$ simulations on Diagnosis, the corresponding success rates are $94.2\%\pm0.5$ and $65.5\%\pm2.1$ ($p=1.1\times10^{-4}$). These are seed-level SEs and Welch tests from \texttt{results\_\allowbreak mcts\_\allowbreak efe.csv}.

On Tileworld-$6\times6$, MCTS-EFE reaches $95.4\%\pm0.6$ at both $200$ and $500$ simulations, compared with Exact-EFE's $71.9\%\pm1.5$ under this battery's protocol. The gain costs reward ($-25.02/-21.62$) and observations ($32.3/14.8$). POMCP reaches only $2.6\%\pm0.4$ and $3.9\%\pm0.5$, with about $0.09$ scans per episode. The success gaps have $p<10^{-9}$ at both budgets. On Tiger and Diagnosis, MCTS-EFE instead falls below Exact-EFE on both success ($97.7/99.9\%$, $94.2/97.1\%$) and reward ($3.73/5.65$, $-3.26/-1.44$). Thus approximate search does not uniformly improve either metric.

The controls detect no success or reward effect of either switchable component, in-tree information gain and max-backup, after Holm correction at five seeds. EFE leaf evaluation, exact beliefs and exact commit-child values remain coupled. The exploration selection uses disjoint tuning seeds but its rule was written after inspecting the canonical-seed sweep, so Tiger's tuned comparison is retrospective. These results concern the joint implementation, not isolated directed sensing or general superiority over POMDP solvers. Progressive widening methods \citep{sunberg2018,benchetrit2025} are possible extensions for larger observation spaces, not evaluated improvements here.
''','Keep method and nonduplicated per-environment results, cite the early POMCP appendix for its complete controls rather than repeat every tuning result.','Algorithm ingredients, exact-vs-sampled and max-backup scope, default constant distinction, simulation-vs-compute, adverse Exact-EFE tradeoffs, five-seed ablation null, retrospective selection, and attribution limits retained.')
# Resolve each guard against the LNCS baseline, preserving its own untouched floats.
lncs=subprocess.check_output(['git','show','c5125ab:paper/full_paper.tex'],cwd=ROOT,text=True)
for p in proposals:
 old=p['old']; new=p['new']
 if lncs.count(old)==1:
  continue
 # Locate by unique first heading/label, then following heading (or end-document for JAIR-only checklist).
 start=old.split('\n\n',1)[0]
 if start not in lncs:
  raise ValueError((p['id'],'start guard absent',start))
 a=lncs.index(start)
 # Last replacement terminates at appendix bibliography in LNCS.
 if p['id']=='late_mcts':
  candidates=[x for x in [lncs.find('\\begin{thebibliography}',a),lncs.find('\\bibliography',a),lncs.find('\\end{document}',a)] if x>=0]
  b=min(candidates)
  # capture bibliography section/comment boundary carefully based on exact final prose
  ending=old.rstrip().split('\n')[-1]
  end_sentence=ending[-100:]
  if end_sentence in lncs[a:b]:
   b=lncs.index(end_sentence,a)+len(end_sentence)
   while b<len(lncs) and lncs[b]=='\n': b+=1
  else: raise ValueError('LNCS final prose differs at end')
 else:
  # first nonempty source after old block identifies next boundary
  following=src[src.index(old)+len(old):].split('\n\n',1)[0]
  b=lncs.find(following,a+len(start))
  if b<0: raise ValueError((p['id'],'end boundary absent',following))
 old_l=lncs[a:b]
 # Whole text is equal after removing Description and generic widths? Preserve full LNCS floats individually.
 new_l=new
 j_floats=re.findall(r'\\begin\{(?:table|figure)\}.*?\\end\{(?:table|figure)\}',old,re.S)
 l_floats=re.findall(r'\\begin\{(?:table|figure)\}.*?\\end\{(?:table|figure)\}',old_l,re.S)
 if len(j_floats)!=len(l_floats): raise ValueError((p['id'],'float mismatch'))
 for j,l in zip(j_floats,l_floats):
  if j in new_l:new_l=new_l.replace(j,l)
 p['old_lncs']=old_l;p['new_lncs']=new_l
 if lncs.count(old_l)!=1: raise ValueError((p['id'],'lncs old nonunique'))
# source proof/label safety checks are advisory; no master changes.
for p in proposals:
 assert src.count(p['old'])==1,p['id']
 assert src.index(p['old']) >= src.index(r'\section{Extended Experimental Specifications and Protocols}'),p['id']
 assert ';' not in p['new'],p['id']
 p['old_words']=len(p['old'].split());p['new_words']=len(p['new'].split())
 p['removed_labels']=sorted(set(re.findall(r'\\label\{([^}]+)\}',p['old']))-set(re.findall(r'\\label\{([^}]+)\}',p['new'])))
path=ROOT/'reviews/appendix_consolidation_2026-10-02/late_proposals.json'
path.write_text(json.dumps(proposals,indent=2)+'\n')
print(json.dumps(dict(proposals=len(proposals),old_words=sum(p['old_words'] for p in proposals),new_words=sum(p['new_words'] for p in proposals),removed_labels=[(p['id'],p['removed_labels']) for p in proposals if p['removed_labels']],lncs_variants=[p['id'] for p in proposals if 'old_lncs' in p]),indent=2))
