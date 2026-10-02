"""Guarded editorial proposals only. Does not write manuscript sources."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "paper/legacy/2026-10-02_pre_claim_focused_appendices"
OUT = Path(__file__).resolve().parent
jair = (BASE / "full_paper_jair.tex").read_text()
lncs = (BASE / "full_paper.tex").read_text()
START = r"\section{Additional Per-Environment Results}"
END = r"\section{Methodological and Budget-Theory Details}"

def sections(source):
    span = source[source.index(START):source.index(END)]
    return {part.splitlines()[0]: part for part in re.split(r"(?=\\section\{)", span) if part}

old_jair = sections(jair)
old_lncs = sections(lncs)
replacements = {}
reasons = {}

def replace(title, new, reason):
    key = r"\section{" + title + "}"
    assert key in old_jair, key
    replacements[key] = new.strip() + "\n\n" if new.strip() else ""
    reasons[key] = reason

replace("Additional Per-Environment Results", r"""
\section{Controls for the Information-Unit Weight}
\label{app:full_tables}

\subsection{Posterior-vote and reward-aware stopping}

The core results do not establish that an explicit information bonus is necessary for good performance. Posterior-vote is not significantly different from EFE on any Bandit metric: reward is $6.32/6.27$ ($p=0.58$), success $87.0\%/86.9\%$ ($p=0.97$), and usage $5.01/5.11$ ($p=0.30$). These are seed-level Welch comparisons under Table~\ref{tab:main}'s protocol. On Diagnosis and Tiger its rewards are lower, $-2.78$ and $3.79$, against EFE's $-1.37$ and $5.19$. Removing reward-aware stopping altogether gives a different failure. Epistemic-only commits immediately at chance on Tiger, Diagnosis, Bandit and Tileworld because no observation's information gain in bits clears its cost. The complete baseline rows and both seed-level and pooled uncertainties remain in the environment CSVs.

\subsection{Symmetric-reward counterexample}
\label{app:testbed}

Testbed uses two states, observation accuracy $0.75$, cost $0.1$, and symmetric commit rewards $+1/{-}1$. Under the $H=4$, $1{,}000$-episodes-per-seed, five-seed protocol, EFE takes $5.50$ observations and earns $+0.38$, compared with Planning's $3.15$ observations and $+0.48$ (seed-level Welch reward $p=1.1\times10^{-5}$). Posterior-vote matches Planning on observations, success and reward. EFE's higher success, $96.3\%$ versus $89.8\%$, therefore comes at a reward cost. Success-tuned myopic Info Gain ($w=20$) and Planning+IG ($w=10$), each tuned within its own class, go further: both take $9.79$ observations, attain $99.5\%$ success and earn only $+0.01$. This is an empirical $H=4$ comparison, not a consequence of the two-step ceiling in Proposition~\ref{prop:nearopt}. Results and selected weights are produced by \url{experiments/run_supplementary.py}.

\subsection{Information-unit sensitivity}
\label{app:nat_canonical}

Bit-unit $w=1$ equals $1/\ln2\approx1.44$ reward units per nat. The exactly nat-canonical policy instead uses bit-unit $w=\ln2\approx0.69$. A direct comparison under the Pareto protocol, $500$ episodes per seed over five seeds, gives bit-identical reward, success and usage on Tiger, Diagnosis, Bandit and Testbed (\texttt{results\_nat\_canonical\_check.csv}). Both conventions remain below Testbed's sampled maximum.

Tileworld changes policy. Nat-canonical EFE earns $-20.81$, succeeds on $74.7\%$, and uses $15.64$ scans, against $-21.53$, $72.0\%$, and $14.75$ at bit-unit $w=1$. Only usage differs significantly (seed-level Welch $p=9.5\times10^{-5}$, surviving Holm over three metrics), with reward $p=0.34$ and success $p=0.070$. Both are Pareto-dominated by sampled $w=20$. Thus the unit check preserves the positive and negative conclusions of Section~\ref{sec:pareto}, without establishing policy invariance to information units.

\FloatBarrier
""", "Replace duplicate core/Tileworld tables with three limiting controls needed to interpret the main results: posterior-vote, symmetric-reward over-sensing, and the directly measured information-unit change. Keep adverse outcomes and inferential scope, not every baseline row.")

replace("Two-State Testbed", "", "Move the indispensable negative Testbed comparison into the focused controls section. Remove its duplicate full-agent table and heuristic threshold-table pointer.")
replace("Supplementary Behavioral Checks", "", "Remove the showcase test-count sweep, reward-asymmetry tour and selected trajectories as peripheral empirical claims. They do not support usage calibration or add an indispensable limitation beyond the retained controls. Do not retain a compressed tour or its figure.")

replace("Environment Specifications", r"""
\section{Supplementary Environment Specifications}
\label{app:envs}

Section~\ref{sec:experiments} defines the main observation accuracies, costs and payoffs. Table~\ref{tab:environment_depths} records the planning depths and hidden-state counts, excluding observable position and action history. All main comparison agents use $\gamma=1$. The offline SARSOP/CPOMDP exports instead require $\gamma=0.999$, and separate discount and POMCP sensitivity batteries state their overrides locally.

\begin{table}[htbp]
\centering
\caption{Hidden-state size and planning horizon or tree depth for the reported comparison instances. RockSample depths were fixed before the reported runs, not selected on measured performance.}
\label{tab:environment_depths}
\begin{tablebody}
\begin{tabular}{lcc}
\toprule
Instance & Hidden states & $H$ \\
\midrule
Tiger / Testbed & $2$ & $6$ / $4$ \\
Diagnosis / Bandit & $4$ & $3$ / $2$ \\
Tileworld $6\times6$ / $8\times8$ & $36$ / $64$ & $2$ \\
RockSample [5,3] / [7,4] & $8$ / $16$ & $3$ / $4$ \\
RockSample [7,8] / [11,11] & $256$ / $2{,}048$ & $3$ / $2$ \\
Inspection $N=8$ / $N=16$ & $256$ / $65{,}536$ & $3$ / $2$ \\
\bottomrule
\end{tabular}
\end{tablebody}
\end{table}

Diagnosis uses $K=\lceil\log_2 N\rceil$ noisy binary tests of different partitions of the state space. Tileworld uses $K=2\lceil\log_2 n\rceil$ scans on an $n\times n$ grid, querying bit-level splits of row and column indices. These complementary partitions permit complete identification. The random and overlapping partition controls are described with their results in Appendix~\ref{app:tileworld_details}.

The additional Navigation task has no separate sensing action. Each move costs $0.5$ and yields a proximity-based warm/cold signal whose accuracy depends on Manhattan distance to the hidden goal. Reaching the goal pays $20$. The tested grids have $n^2$ hidden locations and an episode cap of $3n^2$ moves. NavEFE uses depth $2$.

RockSample's fixed maps are in \texttt{ROCKSAMPLE\_CONFIGS} (\url{experiments/run_rocksample.py}). On RS[11,11], the start cell $(5,0)$ contains a rock and every other rock is at least $3.16$ cells away, where sensor accuracy is roughly $0.55$. This geometry helps explain why useful distant checks fall beyond the tested exact-search horizons. Appendix~\ref{app:experimental_protocol} specifies the sensor kernel, step caps, variant-specific rules and Inspection parameters.

\FloatBarrier
""", "Remove two tables repeating main-text environment parameters. Retain the compact depth/hidden-state mapping and nonduplicated observation-structure and geometry definitions. Detailed RockSample/Inspection rules remain in the protocol appendix.")

replace("Navigation Results", r"""
\section{Limits across Task and Model Variations}

\subsection{Navigation without separate sensing}
\label{app:navigation}

Navigation supplies a negative case for the epistemic bonus. Over $150$ episodes per seed and five seeds on each of the $3\times3$, $5\times5$ and $7\times7$ grids, the myopic mover has the highest mean reward and success at every size. At $5\times5$, its reward is $-16.64\pm1.54$ against NavEFE's $-25.76\pm1.14$, and success is $80.7\pm1.4\%$ against $74.4\pm1.2\%$ (seed-level SE). Both differences survive Holm within metric (Welch $p=0.002$ and $0.010$). No pairwise comparison survives correction on the other two grids. No epistemic agent significantly beats the myopic rule in this battery. The result does not isolate task structure as its cause (\texttt{results\_navigation\_scaling.csv} and its seed-statistics companion).

\subsection{State count and discounting}
\label{app:scaling}
\label{app:discount}

Increasing state count alone does not produce an EFE advantage. A Diagnosis sweep at fixed $H=2$, with $500$ episodes per seed over five seeds, finds EFE and Planning bit-identical at $N=2,4$ and no consistent gap at $N=8,16$. The success advantage over Myopic is shared by reward-only Planning (\texttt{results\_scaling\_stats.csv}). Together with Section~\ref{sec:tileworld}'s fixed-depth threshold and the RockSample counterexample, this limits any interpretation of size as the governing variable.

Discounting also changes the comparison. The separate sweep uses $500$ episodes per seed over five seeds at $\gamma\in\{0.90,0.95,0.99,1\}$. Diagnosis and Bandit show no significant EFE/Planning success gap at $\gamma\le0.95$, but an advantage at $\gamma\ge0.99$ after Holm correction over the battery's $24$ tests. For example, EFE's Diagnosis usage falls from $9.68$ at $\gamma=1$ to $5.83$ at $0.95$. Tiger remains above $96\%$ success throughout. These are measured configuration effects, not a universal discount threshold (\texttt{results\_discount.csv}).

\subsection{Sensor-model misspecification}
\label{app:misspec}

The accuracy-sensitivity battery holds the true sensor fixed while varying the agent's model, using $500$ episodes per seed over five seeds (\texttt{results\_model\_misspec.csv}). On Tiger ($p_{\mathrm{true}}=0.85$, $H=4$), EFE and Planning are bit-identical at every tested accuracy. At $p_{\mathrm{agent}}\in\{0.70,0.75,0.80,0.85\}$ both take $4.23$ observations and earn $5.33\pm0.26$. At $0.90$ and $0.95$ both take $2.65$ and earn $3.91\pm0.38$ (seed-level SE). Overconfidence reduces sensing and reward without any EFE-specific buffering.

Diagnosis also changes in steps. With true accuracy $0.80$ and $H=3$, EFE takes $9.68$ tests and succeeds on $97.4\%$ at modeled accuracies $0.70$, $0.75$ and $0.80$. At $0.65$, $0.85$ and $0.90$ it takes $5.86$ tests and succeeds on $88.7\%$. Planning's pattern is similar but not identical. These discontinuities are not specific to the epistemic term, and the experiment does not establish their mechanism.

\FloatBarrier
""", "Replace three full robustness tables and a scaling table with the actual limiting comparisons needed by the discussion. Retain sample counts, fixed-depth scope, discount correction family and misspecification adverse outcomes, without listing every measured row.")

replace("Scaling Analysis", "", "Move its negative fixed-depth result to the task/model limits section and omit the peripheral full-agent scaling table.")
replace("PyMDP Consistency Check", "", "Remove the qualitative single-step library consistency exercise. The equivalence is proved for the stated recursion, and this check neither proves it nor tests usage calibration.")

replace("Supplementary Statistics", r"""
\section{Statistical Conventions}
\label{app:stats}

Primary comparisons use independent two-sample Welch $t$-tests on per-seed means, ordinarily $n=5$, with Holm--Bonferroni correction. Uncorrected comparisons are marked locally. Unless stated otherwise, a family contains all pairwise agent comparisons and measured metrics within one environment or instance: $M\binom{A}{2}$ tests for $A$ agents and $M$ metrics. Families include agents and metrics omitted from the printed summaries. The nominal sizes are $108$ for Tiger, $84$ for Diagnosis and Bandit, and $18$ per Inspection instance. Undefined zero-variance comparisons are excluded, leaving $107$ defined tests for Tiger and $83$ for Diagnosis.

RockSample corrects within metric, with $21$ comparisons per instance over seven agents. Pooling metrics would loosen its non-rejection-based bolding rule. The discount sweep pools $24$ tests across environments, discounts and metrics. The MCTS ablation corrects within metric across its three environments, and the exploration sweep within metric within each of its three comparison families. The separate Tileworld scaling battery reports seed-level SEs without a Welch companion file.

Main tables report seed-level SE, which describes between-seed replicability. Pooled episode-level SEs and tests remain in the companion CSVs as supplementary descriptions, since episodes within a seed are not independent. The six core observe-then-commit and Tileworld statistics files use equal-variance pooled tests. Substituting Welch changes no non-degenerate decision at $\alpha=0.05$ among their $510$ comparisons. RockSample and Inspection use Welch at both levels. Bootstrap $95\%$ intervals use $10{,}000$ resamples and a fixed seed unless a study states otherwise.

Interpreted effect sizes use the pooled episode-level standard deviation. EFE's reward effects against Planning are $d=0.08$ on Diagnosis and $d=0.14$ on Bandit, small despite their detectable seed-level differences. We do not interpret Cohen's $d$ computed from five seed means. Equal episodes per seed make pooled and seed-level mean differences identical, so their sign agreement supplies no independent evidence. A failure to reject a difference is not equivalence. The fixed-margin TOST comparisons are reported separately.

\FloatBarrier
""", "Keep reproducibility-critical correction families, uncertainty definitions and inferential exceptions. Remove the broad effect-size matrix while retaining the two small effects used in the main claim.")

replace("Near-Optimality across Planning Horizons", "", "Remove the exploratory random-environment horizon study in full, including lenient descriptive pass criterion, figure and stratified map. This is peripheral to usage calibration and does not prove the horizon theorem. Remove its corresponding main/discussion claims and checklist exceptions, rather than retaining a dense summary.")
replace("Discount Factor Sensitivity", "", "Retain the configuration-dependent limitation with protocol in the task/model limits section, and remove the redundant full discount table.")
replace("Model Misspecification Sensitivity", "", "Retain the absence of EFE-specific robustness and the Diagnosis threshold counterexample in the task/model limits section. Remove the full row-by-row sensitivity table.")

replace("RockSample as an Interleaved Observe-Act Setting (Extended)", r"""
\section{Search Baseline Controls}

\subsection{RockSample: tuning and rollout limitations}
\label{app:rocksample}

The RockSample POMCP comparison depends on the search configuration, not just the objective. Its history tree uses UCB1, mean backup and Monte Carlo rollout with the exact factored posterior. The depth bound shrinks near the episode cap, masks remove invalid actions, and subtrees are not promoted because their accumulated values use shorter horizons. These departures depend on observable quantities. Three disjoint tuning seeds select rollout, exploration constant, horizon and root criterion through a two-stage coordinate grid. The configuration is frozen before evaluation. The $2{,}048$-simulation evaluation budget is twice the $1{,}024$ tuning budget and is not itself tuned.

On RS[5,3], frozen POMCP earns $12.74\pm0.11$ under the full table protocol, compared with EFE's $16.47\pm0.12$. Its standalone approach-then-check rollout earns $16.67\pm0.13$, significantly more than the search ($p=1.9\times10^{-14}$, surviving Holm). The search exits after $7.5$ steps, while the rollout follows a $13.5$-step collection tour. The position-independent $9.50$ net exit payoff makes early exit attractive under mean backup.

A post hoc budget--horizon sweep shows why the frozen result cannot characterize POMCP generally. At $16{,}384$ simulations, increasing the frozen horizon from $10$ to $15$, $25$ or $40$ raises mean reward from $12.52$ to about $15.6$, $15.2$ or $15.6$. Under this diagnostic's matched five-seed, $100$-episode protocol, EFE earns $16.90\pm0.45$ at about $1.7$ ms per decision, versus the best measured POMCP at roughly $15.6$ and $530$ ms. None of these reward gaps survives Holm over the nine diagnostic rows. Tuning horizon at one simulation budget missed an interaction with computation. The diagnostic does not re-select the frozen configuration.

The larger instance reverses this trend. On RS[11,11], the post hoc $2{,}048$-simulation sweep gives $12.94\pm0.24$ at horizon $10$ and $-54.78\pm0.86$ at $40$, with every tested horizon increase reducing reward after Holm ($p\le4.3\times10^{-5}$). The endpoints expand from $3.3$ steps and $1.6$ checks to $196$ steps and $144$ checks. Deeper search spends heavily on distant sensing. Its best measured alternative, $4{,}096$ simulations at horizon $10$, earns $13.14\pm0.15$, still $15.5$ below the standalone rollout's $28.66\pm0.83$ ($p=3.2\times10^{-5}$, surviving Holm at both levels). The $16{,}384$ tier was not run on this instance because of its per-step cost.

Two implementation sensitivities do not resolve the comparison. On RS[5,3], literal unweighted rejection sampling and the exact factored posterior give $12.93\pm0.25$ and $12.81\pm0.43$ ($p=0.81$). Replacing the exit-valued depth-cap leaf with a greedy-belief leaf gives $14.52\pm0.34$, but its differences from the frozen search and standalone rollout do not survive the sensitivity battery's per-metric Holm correction. These are non-rejections, not equivalence findings. The weighted agents' separate shared-leaf limitation is specified in Appendix~\ref{app:rocksample_main_details}.
""", "Delete the full extended table already represented by the main RockSample table. Retain the adverse standalone-rollout result, tuning/computation qualification, reversal under deeper search on RS[11,11], and implementation sensitivity limits that prevent a general solver-superiority claim.")

replace("IDS Baseline (Observe-then-Commit)", "", "Remove the full IDS benchmark and its positive EFE comparison. If the late distractor analysis retains IDS, its deterministic-action adaptation and fallback must be defined locally rather than referring here.")
replace("Proper-Scoring Calibration", "", "Remove the terminal-belief scoring study. Its quality-versus-calibration distinction is sound but peripheral to usage calibration and not used by a retained main claim.")
replace("Per-Test Value-of-Information Audit Trail", "", "Remove the software-audit demonstration and example table. The optional implementation remains in public code, and the manuscript's theorem/usage-calibration claims do not require this second interpretability deliverable.")
replace("Reward-Rescaling Invariance", "", "Remove the finite-grid reward-optimum sweep, which is weaker and redundant with the scale-equivariance theorem and retained usage-curve collapse experiment. Do not retain its three-seed descriptive exception in the checklist once the study is absent.")
replace("Information Base and the Nat-Canonical Agent", "", "Move the actual information-unit qualification into the focused controls section, dropping only repeated per-environment reward/success values.")

replace("POMCP Baseline Comparison", r"""
\subsection{Observe-then-commit POMCP and MCTS-EFE}
\label{app:pomcp}

The observe-then-commit POMCP adaptation \citep{silver2010} has two fidelity gaps absent from the separate RockSample implementation. The depth-cap leaf uses the best commit reward for the sampled state, an optimistic clairvoyant value. Rollout commits instead receive their belief-expected reward, replacing sampled payoff with conditional expectation. Their separate policy effects are not isolated. Rollouts start from the simulated path's updated belief, choose tests uniformly and commit to the belief-optimal action with probability $0.3$ per step.

The core battery fixes UCB1 constant $10$, depth cap $H+3$, and simulation counts $\{500,1000,2000,5000\}$. Each outer seed initializes both environment and planner randomness. A fixed constant has different effective strength across reward scales, and simulation budgets do not match computation to exact EFE or Planning. Nor does the comparison isolate directed observation choice, since exact EFE also changes tree enumeration, leaf values and commit values. The full core results are in \texttt{results\_pomcp.csv}. The simulation-matched MCTS-EFE comparison and its algorithm are described in Appendix~\ref{app:interpretation}.

\paragraph{Computation and component controls.}
A same-machine Tiger control, timed without contention over five seeds and $200$ episodes per seed, compares MCTS-EFE($500$) at $13.87$s with POMCP($661$) at $13.88$s. MCTS-EFE uses horizon $10$, while POMCP uses constant $5$ and depth cap $13$. The latter simulation count was selected by timing calibration at $200$, $500$ and $1{,}000$ simulations. Success is $97.7\pm0.5\%$ versus $88.0\pm0.6\%$. Both the compute-matched POMCP and its $500$-simulation version trail MCTS-EFE on success and reward ($p<0.0001$). This result concerns the tested constant and protocol, not all POMCP configurations.

Switching MCTS-EFE's in-tree information gain and max-backup independently detects no success or reward effect after Holm correction within metric across the three environments. Only Tiger usage changes significantly, from $3.73$ to $3.48$ without in-tree information gain ($p=0.0014$). Five seeds give limited sensitivity. The fixed EFE-greedy leaf, exact beliefs and exact commit values remain candidate explanations, so this ablation cannot attribute the advantage to information gain throughout the tree. These ablation and compute-matched batteries retain fixed internal planner seeds, unlike the core POMCP and exploration-sweep batteries.

\paragraph{Exploration selection and its limits.}
The exploration sweep tests $c\in\{1,2,5,10,20,50,R\}$ on Tiger, Diagnosis and Tileworld, where $R$ is the commit-reward range and MCTS-EFE's default. Bandit is not swept. POMCP also receives an informed rollout selecting the largest exact one-step information gain. Selection maximizes success and then reward on seeds $\{11,22,33\}$ with $100$ episodes each. This rule was recorded before selection, but the rule and grid followed inspection of the canonical-seed exploratory sweep. Evaluation uses the canonical five seeds.

Selected MCTS-EFE uses $c=5$ on Tiger and Diagnosis, and its default on Tileworld. Selected POMCP uses $c=50$ with uniform rollouts on Tiger, $c=5$ with uniform rollouts on Diagnosis, and $c=5$ with informed rollouts on Tileworld. On Tiger, selected MCTS-EFE retains higher success ($98.2\pm0.3\%$ versus $93.2\pm0.5\%$, $p=0.0001$) and reward ($4.33\pm0.28$ versus $0.39\pm0.52$, $p=0.0005$). Both survive Holm over the six selected success/reward comparisons, as do the selected Diagnosis and Tileworld comparisons.

This sweep does not exhaust plausible configurations. Diagnosis's evaluation-seed-best POMCP setting differs from its tuning selection. Tileworld's best uniform-rollout constant is the grid's lower edge, and lower values were not tested. MCTS-EFE's default is not reward-optimal either. Informed rollouts leave one-test Tiger unchanged, give no significant Diagnosis success gain, and improve Tileworld success but not reward after Holm. None of these controls isolates all architectural differences.

\FloatBarrier
""", "Remove repetitive core/search and exploration/ablation tables while keeping the protocol, prospective-versus-post-inspection selection disclosure, matched-computation outcome, null component effects and search-boundary limitations required by the main discussion.")

replace(r"Budgeted $\rho$-POMDP Supplementary Details", r"""
\section{Budget Benchmark Implementation}
\label{app:budget_supp}

\subsection{SARSOP export and evaluation}
\label{app:sarsop_build}

The reference uses the original APPL C++ solver \texttt{pomdpsol}, built by \url{tools/build_sarsop.sh} with four documented Apple-Silicon/clang compatibility patches. The binary is not committed. \url{experiments/run_sarsop_baseline.py} exports each discrete observe-then-commit benchmark from the agents' own state, action and observation definitions, adding an absorbing done state and discount $\gamma=0.999$. It solves to precision $10^{-3}$, parses the XML alpha vectors and evaluates their policy through the shared episode runner. \url{tests/test_sarsop_export.py} checks the exporter, parser and argmax agent without the solver binary.

\subsection{Distractor factorization}
\label{app:distractor}

\texttt{DistractorDiagnosisEnv} has a four-way condition $x$ and binary nuisance $z$. Each test observes one factor, terminal rewards depend only on $x$, and rewards are not observations. For a factored belief $b(x,z)=b_X(x)b_Z(z)$ and nuisance likelihood $L(o\mid z)$, Bayes' rule gives
\[
b'(x,z\mid o)=b_X(x)\frac{L(o\mid z)b_Z(z)}{\sum_{\tilde z}L(o\mid\tilde z)b_Z(\tilde z)}.
\]
The condition marginal is therefore unchanged. Condition tests preserve the nuisance marginal by the same argument. The independent generative process preserves this factorization, but correlated beliefs, including those caused by misspecification, are outside the guarantee. \url{tests/test_distractor_diagnosis.py} checks both marginal identities numerically.

\FloatBarrier
""", "Keep the actual reference-construction method and proof supporting reward-irrelevant sensing. Drop the atlas, whose descriptive operating points duplicate the usage curves and main target-calibration experiments.")

assert set(replacements) == set(old_jair)
records = []
for i, key in enumerate(old_jair, 1):
    old, new = old_jair[key], replacements[key]
    assert jair.count(old) == 1
    record = {"id": f"early-{i:02d}", "old": old, "new": new, "reason": reasons[key]}
    if old_lncs[key] != old:
        record.update(old_lncs=old_lncs[key], new_lncs=new)
    assert lncs.count(record.get("old_lncs", old)) == 1
    records.append(record)

(OUT / "early_proposals.json").write_text(json.dumps(records, indent=2) + "\n")
(OUT / "early_proposed_span.tex").write_text("".join(replacements.values()))

old_span = "".join(old_jair.values())
new_span = "".join(replacements.values())
old_labels = set(re.findall(r"\\label\{([^}]+)\}", old_span))
new_labels = set(re.findall(r"\\label\{([^}]+)\}", new_span))
removed_labels = sorted(old_labels - new_labels)
removed_inputs = re.findall(r"\\input\{([^}]+)\}", old_span)
for inp in removed_inputs:
    old_labels.update(re.findall(r"\\label\{([^}]+)\}", (ROOT / "paper" / inp).read_text()))
removed_labels = sorted(old_labels - new_labels)
lines = jair.splitlines()
start_line = jair[:jair.index(START)].count("\n") + 1
end_line = jair[:jair.index(END)].count("\n") + 1
outside_refs = []
for n, line in enumerate(lines, 1):
    if start_line <= n < end_line:
        continue
    hits = [label for label in removed_labels if re.search(r"\\(?:ref|pageref|autoref)\{"+re.escape(label)+r"\}", line)]
    if hits:
        outside_refs.append({"line": n, "labels": hits, "text": line})
(OUT / "early_reference_impact.json").write_text(json.dumps({
    "removed_labels": removed_labels, "added_labels": sorted(new_labels-old_labels),
    "removed_table_inputs": removed_inputs, "outside_references": outside_refs,
    "old_words": len(old_span.split()), "new_words": len(new_span.split()),
}, indent=2) + "\n")
print(f"Wrote {len(records)} exact, unique proposals; words {len(old_span.split())} -> {len(new_span.split())}")
print("Removed labels:", ", ".join(removed_labels))
print("Outside reference passages:", len(outside_refs))
