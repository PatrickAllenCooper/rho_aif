"""Restore selected direct evidence after assemble_evidence.py.
Exact moves avoid duplicated floats; the shorter distractor main replaces its summary.
"""
from pathlib import Path
import re
D=Path(__file__).resolve().parent
original=(D/'evidence_original.tex').read_text()
main=(D/'evidence_main.tex').read_text()
app=(D/'evidence_appendix.tex').read_text()
def subsection(s,label):
    p=s.index('\\label{'+label+'}')
    start=s.rfind('\\subsection{',0,p)
    m=re.search(r'\\(?:subsection|section)\{',s[p:])
    end=p+m.start() if m else len(s)
    return s[start:end]
def block(s,kind,label):
    for m in re.finditer(r'\\begin\{'+kind+r'\}.*?\\end\{'+kind+r'\}',s,re.S):
        if '\\label{'+label+'}' in m[0]: return m[0]
    raise ValueError(label)
restored=''
for label in ['sec:cost_budget','sec:interleaved_budget','sec:stairs']:
    chunk=subsection(app,label)
    assert chunk==subsection(original,label)
    app=app.replace(chunk,'',1);restored+=chunk
anchor='\\subsection{Unconstrained Reward Reference}'
assert main.count(anchor)==1
main=main.replace(anchor,restored+anchor)
# Move direct full tables to their concise main-text analyses.
rock='\\input{tables/rocksample_main.tex}'
assert app.count(rock)==1 and rock not in main
app=app.replace(rock,'',1)
anchor='The important counterexample is RS[11,11].'
main=main.replace(anchor,rock+'\n\n'+anchor,1)
main=main.replace('Appendix~\\ref{app:rocksample_main_details} retains the main table, leaf-rule disclosure, depth check, and heuristic comparison,', 'Table~\\ref{tab:rocksample} gives the full comparison. Appendix~\\ref{app:rocksample_main_details} retains the leaf-rule disclosure, depth check, and heuristic comparison,')
inspection=block(app,'table','tab:inspection');app=app.replace(inspection,'',1)
anchor='Across the battery, the canonical weight'
main=main.replace(anchor,inspection+'\n\n'+anchor,1)
main=main.replace('Table~\\ref{tab:inspection} and the qualified two-state interpretation appear in Appendix~\\ref{app:inspection_details}.', 'Table~\\ref{tab:inspection} reports both instances, with the qualified two-state interpretation in Appendix~\\ref{app:inspection_details}.')
scaling=block(app,'figure','fig:tw_scaling');app=app.replace(scaling,'',1)
anchor='\\subsection{RockSample}\n'
main=main.replace(anchor,scaling+'\n\n'+anchor,1)
main=main.replace('In a separate fixed-$H{=}2$ sweep,', 'In a separate fixed-$H{=}2$ sweep (Figure~\\ref{fig:tw_scaling}),')
# A concise primary distractor narrative keeps the original full detail in appendix.
distractor=block(app,'figure','fig:distractor');app=app.replace(distractor,'',1)
app=app.replace('\\label{sec:distractor}', '\\label{app:distractor_details}',1)
start=main.index('\\subsection{Breadth and Limits of the Budget Instrument}')
end=main.index('\\section{Results}',start)
new=r'''\subsection{Reward-Irrelevant Sensing}
\label{sec:distractor}

An expected sensing target controls the amount of sensing, but does not ensure that it concerns the task. We test this limit with Distractor Diagnosis, whose hidden state combines the usual four-way condition with an independent binary nuisance bit. Commit rewards depend only on the condition. An added test observes only the nuisance bit, while the original tests observe only the condition. Under the independent generative process the belief stays factored, so the distractor carries exactly zero information about the condition. Appendix~\ref{app:distractor} states and tests that property, whose scope excludes correlated priors introduced through misspecification.

We sweep ordinary Planning+IG over sixteen weights with five seeds and $100$ episodes per weight and seed, refining the grid where distractor use begins. The distractor fraction is zero through $w{=}3.5$, $0.103\pm0.001$ at $w{=}4$, $0.233\pm0.003$ at $w{=}5$, and approximately one third at the largest weights (Figure~\ref{fig:distractor}). Thus the observed onset bracket is $(3.5,4.0]$. The canonical $w{=}1$ agent avoids the distractor on this instance because it is below onset, not because its objective is structurally immune. At sufficiently high weights, genuine information about the nuisance bit earns more epistemic value than the test costs.

A reward-relevance variant scores information gain on the marginal belief over reward-equivalence classes. Two states belong to the same class when every commit action pays the same in them, so the partition is determined by the commit reward matrix already supplied to the agent. On this benchmark, the two states differing only in the nuisance bit share a class and the four classes are the four conditions. The planner still propagates the full joint posterior and changes only the belief on which information gain is scored. If no states are reward-equivalent, the variant reduces to ordinary information gain. This construction uses the known reward model and the benchmark's factorization, rather than learning task relevance from data.

The variant buys zero distractor tests at every swept weight. At $w{=}100$, ordinary information gain buys $6.46$ distractor tests, $33.2\%$ of its usage, and earns $-10.48\pm0.11$ reward against the variant's $-3.64\pm0.36$. Seed-level Welch tests with Holm correction over the weight-by-metric family detect usage and distractor-count differences at every tested weight past onset. Reward differences survive that correction at $w{=}31.6$ and $100$, with $p=1.2{\times}10^{-5}$ and $1.5{\times}10^{-5}$, but not at the smaller post-onset weights. Success rates are identical through $31.6$, and the variant's nominal advantage at $100$ is not significant.

Relevance weighting does not solve over-observation. At the two largest weights the variant still buys $13.16$ task-relevant tests against $9.77$ at $w{=}10$. Nor is the IDS adaptation used here immune to nuisance sensing. Its information about the optimal commit is correctly zero for the distractor, but its zero-denominator fallback uses raw state-entropy reduction and yields a distractor fraction of $0.305\pm0.005$. This is a failure of that implementation choice, not evidence against reward-aware information measures in general. A sensing target and relevance weighting therefore address different design requirements. Appendix~\ref{app:distractor_details} preserves the full curves, implementation analysis, corrected comparison family, and remaining numerical results.

% DISTRACTOR_FIGURE

\subsection{Additional Onset and Operating-Point Checks}
\label{sec:budget_breadth_summary}

Positive-threshold two-state instances place the observed onset within one refined grid step, $3\%$, above the closed-form threshold, while standard negative-threshold instances observe already at $w{=}0$ (Appendix~\ref{sec:prop2exp}). The atlas collects the implicit $w{=}1$ budgets and two grid brackets per instance from the measured curves (Appendix~\ref{app:w_atlas}). These are measured operating points, not a universal predictive formula for the price.

'''
new=new.replace('% DISTRACTOR_FIGURE',distractor)
main=main[:start]+new+main[end:]
# These restored labels now refer to main sections rather than appendix subsections.
for label in ['sec:cost_budget','sec:interleaved_budget','sec:stairs']:
    main=main.replace('Appendix~\\ref{'+label+'}', 'Section~\\ref{'+label+'}')
# State uncertainty convention for every compact-frontier metric, as requested.
main=main.replace('$U$ and $R$ are held-out mixture usage and reward. The paired gap', '$U$ and $R$ are held-out mixture usage and reward. All $\\pm$ values are seed-level SE. The paired gap')
main=main.replace('paired cap-reference gap, with seed-level SE.', 'paired cap-reference gap.')
main=main.replace('The count-usage curves of this section so far treat every observation as one unit regardless of price.', r'The count-usage curves of Section~\ref{sec:collapse} treat every observation as one unit regardless of price.')
app=app.replace('The staircases of the previous subsection price sensing', r'The staircases of Section~\ref{sec:stairs} price sensing')
app=app.replace('The next subsection moves to budgets set by a predeclared rule from the calibration curve, independently of weight-one usage.', r'Section~\ref{sec:budget_frontier} considers budgets set by a predeclared rule from the calibration curve, independently of weight-one usage.')
app=app.replace('The subsection after it turns from how much reward the family attains to what the information term\'s sensing is about.', r'Section~\ref{sec:distractor} examines whether that sensing concerns reward-relevant information.')
app=app.replace('The previous subsection already read this figure panel by panel to make the tied brackets and the two exceptions precise, so here we draw only the general conclusion from it.', r'Appendix~\ref{app:core_details} identifies the tied brackets and the two exceptions, and this subsection gives the full weight-sweep interpretation.')
(D/'evidence_main.tex').write_text(main)
(D/'evidence_appendix.tex').write_text(app)
print('Main words',len(main.split()),'Appendix words',len(app.split()))
from collections import Counter
labels=re.findall(r'\\label\{([^}]+)\}',main+'\n'+app)
print('Duplicate fragment labels',[k for k,v in Counter(labels).items() if v>1])
print('Lost original labels',set(re.findall(r'\\label\{([^}]+)\}',original))-set(labels))
