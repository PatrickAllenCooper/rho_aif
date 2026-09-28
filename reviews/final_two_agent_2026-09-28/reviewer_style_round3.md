# Theory reviewer — style pass, round 3

Reviewed 2026-09-28. This is a bounded style review of both live manuscript masters, following my unqualified science ACCEPT in round 2. I read the contribution list, theory exposition, empirical interpretation, discussion, conclusion, appendices, and disclosure, and inventoried emphasis, headings, list environments, and punctuation in both masters. Source line numbers below identify the working state at this review and may shift after edits. Each proposed shared-text edit should be made in both masters. I did not edit either manuscript, change code, or delegate further. The other reviewer owns the full rendered-figure audit. I have not independently inspected every figure in this pass.

The source does not warrant a broad removal of emphasis or punctuation. Most italics introduce definitions or mark proof parts. Most bold text encodes table comparisons or the required JAIR checklist. The numbered contribution list is cross-referenced elsewhere and should remain. The structured abstract, theorem styles, mathematical semicolons, required checklist, authorship, and AI disclosure should remain. In particular, no remaining prose-semicolon problem was found. Style cannot establish whether text was AI-generated.

The following are concrete editorial recommendations, not newly discovered scientific defects. The largest change is item 3. My science ACCEPT remains in force. Final style acceptance should be recorded after the applied text and its rendering are checked.

## 1. Replace the cumbersome “two halves” framing in Contribution 4

Locations: `paper/full_paper_jair.tex:102` and `:108`; `paper/full_paper.tex:65` and `:71`.

Replace:

```tex
\item Practical guidance. A characterization in two halves of when EFE-as-$\rho$ helps, namely where the advantage appears and what governs it, and when it does not, namely where information gain fails by construction. On the first half, the advantage appears when the agent must choose among multiple observation actions.
```

with:

```tex
\item Practical guidance. We identify the tested conditions under which EFE-as-$\rho$ helps and the model structures in which information gain fails by construction. In the tested regimes, the advantage appears when the agent must choose among multiple observation actions.
```

Replace:

```tex
On the second half, we report where it does not help by construction.
```

with:

```tex
Two structural limits accompany these results.
```

Rationale: removes metadiscourse and an awkward sentence fragment while retaining the empirical scope and both negative results. The rest of the contribution, including the revised workshop claim, should remain.

## 2. Start the empirical summary with its result

Locations: JAIR `:993`; long master `:944`.

Delete just:

```tex
Taken together, the experiments tell a consistent story. The behavior predicted by Propositions~\ref{prop:equivalence} and~\ref{prop:factored} is what we observe.
```

The paragraph then starts with the existing `EFE matches Planning+IG at $w{=}1$ within their stated scope, ...`.

Rationale: the retained sentence states the actual agreement and its scope. The removed lead-in adds no distinct result.

## 3. Convert practical guidance to connected prose

Locations: JAIR `:1061–1072`; long master `:1012–1023`. Replace from the paragraph heading through the `\end{itemize}`, leaving the following paragraph beginning `EFE is not recommended in three situations` unchanged.

Exact proposed replacement:

```tex
\paragraph{Practical guidance.}
The experiments suggest the following guidance for choosing an information weight. The numeric thresholds for reward asymmetry $\alpha$, horizon $H$, and discount factor $\gamma$ are estimates from this benchmark suite, not established regime boundaries.

On our suite, reward asymmetry $\alpha \geq 5$ places $w{=}1$ well inside Proposition~\ref{prop:nearopt}'s $H{=}2$ near-optimality interval, because the penalty for a wrong commit far exceeds the observation cost. The random-environment study tempers this into a favorable-regime heuristic rather than a guarantee ($79\%$ of $\alpha \ge 10$ samples pass at $H{=}3$, Appendix~\ref{app:nearopt_horizon}).

With multiple observation actions, EFE's joint pragmatic--epistemic objective selects which information to gather and can improve on reward-only planning at matched horizon. The observed advantage depends on the gap between greedy and information-optimal behavior and on whether the search is deep enough to represent the latter. State-space size alone does not predict this gap. On the Tileworld sweep, the separation is within sampling error at $4{\times}4$ and $6{\times}6$ and opens at $8{\times}8$, where Planning collapses (Figure~\ref{fig:tw_scaling}). Diagnosis at $N{=}16$ under the $H{=}2$ scaling protocol shows no consistent EFE--Planning gap (Appendix~\ref{app:scaling}), the advantage vanishes on RockSample[11,11] (Section~\ref{sec:rocksample}), and on Structural Inspection the accuracy gap narrows from $N{=}8$ to $N{=}16$ (Section~\ref{sec:inspection}).

When observation and navigation preserve the hidden state, the information-unit-weight equivalence also holds for interleaved observe-act settings (factored observation POMDPs, Table~\ref{tab:taxonomy}). EFE then directs both where to go and what to check (Tables~\ref{tab:rocksample},~\ref{tab:inspection}).

When a weight cannot be tuned per task, transfer performance depends on the target environment. The information-unit weight $w{=}1$ ties the transferred success-tuned $w{=}10$ and $w{=}20$ on Tiger and Diagnosis, where only $w{=}50$, the top of the tested grid, degrades. On Bandit and Testbed, every transferred success-tuned weight costs reward relative to $w{=}1$ (Table~\ref{tab:transfer}).

Recursive EFE propagates epistemic value across steps at horizons $H \geq 2$. At $H{=}1$, it reduces to myopic information gain with $w{=}1$. On the tested multi-observation environments, its advantage appears at discount factors $\gamma \geq 0.99$. Heavier discounting truncates the effective horizon below the number of observations needed for confident disambiguation (Appendix~\ref{app:discount}). This discount threshold is read off two environments at one horizon each and should not be treated as a general boundary.
```

Rationale: replaces one long bullet and six fragment-led bullets with topic sentences. It preserves all three numeric threshold qualifications, every supporting environment and citation, the reward-asymmetry success percentage, transfer weights, interleaving condition, and the absence of a general size law. It also avoids introducing the list as favoring EFE “over tuned alternatives,” since several of its actual comparisons are with reward-only planning. The opening still explicitly marks these statements as suite-based guidance.

## 4. Use concise, descriptive paragraph headings

Apply these exact heading-only replacements in both masters:

1. JAIR `:1006`, long `:957`:

   ```tex
   \paragraph{What the information-unit weight optimizes, and what its measured reward and success imply for tuning.}
   ```

   becomes:

   ```tex
   \paragraph{The information-unit weight and tuning.}
   ```

2. JAIR `:1505`, long `:1792`:

   ```tex
   \paragraph{Horizon map of where myopic and deeper planning agree, and where they do not.}
   ```

   becomes:

   ```tex
   \paragraph{Agreement across planning horizons.}
   ```

3. JAIR `:1560`, long `:1847`:

   ```tex
   \paragraph{Discounting erases EFE's advantage on multi-observation environments.}
   ```

   becomes:

   ```tex
   \paragraph{Sensitivity to discounting.}
   ```

4. JAIR `:1793`, long `:2079`:

   ```tex
   \paragraph{Which component does the work.}
   ```

   becomes:

   ```tex
   \paragraph{Component ablation.}
   ```

Rationale: makes headings easy to scan. The discount heading no longer reads like an unrestricted claim when its supporting paragraph is specifically about the measured discount sweep. No paragraph content changes are implied by these heading edits.

## 5. Let the measured misspecification results carry the interpretation

Locations: JAIR `:1619`; long `:1906`.

Replace:

```tex
\paragraph{Key findings.} On Tiger, both EFE and Planning agents are remarkably robust. Success falls at most $2.7$pp below the calibrated $99.6\%$ across the tested range of $-0.15$ to $+0.10$.
```

with:

```tex
\paragraph{Asymmetric sensitivity to sensor error.} On Tiger, success falls at most $2.7$pp below the calibrated $99.6\%$ for both EFE and Planning across the tested range of $-0.15$ to $+0.10$.
```

In the same paragraph replace:

```tex
This is a genuine, environment-specific finding, not a case we can attribute to the epistemic term.
```

with:

```tex
This finding is specific to the tested environment and cannot be attributed to the epistemic term.
```

Rationale: replaces an intensifier and generic heading with the concrete measured scope. The unchanged following sentences retain the asymmetry, identical EFE/Planning rows, and absence of an EFE-specific buffering effect.

## 6. Remove a few promotional intensifiers from the POMCP comparison

Locations: JAIR `:1787–1789`; long `:2073–2075`.

Exact replacements within those paragraphs:

```tex
\paragraph{Key findings.} Table~\ref{tab:pomcp}
```

becomes:

```tex
\paragraph{POMCP comparison.} Table~\ref{tab:pomcp}
```

```tex
On Diagnosis, the gap is dramatic. POMCP achieves only
```

becomes:

```tex
On Diagnosis, POMCP achieves
```

```tex
but at real reward cost
```

becomes:

```tex
but with lower reward
```

```tex
Its wall-clock cost balloons to roughly
```

becomes:

```tex
Its wall-clock cost rises to roughly
```

Rationale: the reported magnitudes already convey the size and direction of each difference. All numerical results, uncertainty, tuning limitations, and the later stronger-baseline qualifications remain unchanged.

## 7. Simplify the budget-frontier interpretation without losing its uncertainty limits

Locations: JAIR `:761`; long `:716`.

Replace:

```tex
The second question has a less flattering answer, and it delimits what calibration is for.
```

with:

```tex
The reward comparison shows the limits of usage calibration.
```

Replace:

```tex
The resulting intervals are nominal, pointwise plug-in summaries: they do not propagate support reselection, uncertainty in mixture weights or cap feasibility, or multiplicity across budgets.
```

with:

```tex
The resulting intervals are nominal, pointwise plug-in summaries. They do not propagate support reselection, uncertainty in mixture weights or cap feasibility, or multiplicity across budgets.
```

Rationale: removes evaluative framing and splits a dense sentence at its natural boundary. All inferential qualifications remain explicit. No need to remove legitimate colons elsewhere, including the structured abstract labels.

## 8. Remove the italics from the long environment-table note

Locations: JAIR `:1350`; long `:1638`.

Replace:

```tex
\multicolumn{9}{l}{\emph{Interleaved observe-act (Proposition~\ref{prop:factored}). Undiscounted. Every RockSample action costs $-0.5$, and Inspection's per-action costs are given in its own rows}} \\
```

with:

```tex
\multicolumn{9}{l}{Interleaved observe-act (Proposition~\ref{prop:factored}). Undiscounted. Every RockSample action costs $-0.5$, and Inspection's per-action costs are given in its own rows} \\
```

Rationale: an entire long note does not need emphasis. Retain italics that introduce mathematical terms and the short `Success rate` table group label, whose typography serves a structural purpose. Retain bold table values and labels according to their stated conventions.

## Verification needed after application

Check mirrored shared text, contribution references, list-environment balance, and that neither disclosure nor the JAIR checklist changed. Build both masters and inspect the practical-guidance pages and the environment-table note for paragraph/page-break quality. Preserve all science fixes accepted in round 2. The other reviewer should record the separate full-figure visual result. I found no reason to expand this style pass into a broad rewrite, citation change, or new experiment.
