"""Assemble the proposed evidence fragments from the archived pre-edit span.
This does not modify either manuscript master or any experimental artifact.
"""
from pathlib import Path
import re
D=Path(__file__).resolve().parent
s=(D/'evidence_original.tex').read_text()
p=D/'evidence_main.tex'
main=(D/'evidence_main_template.tex').read_text()
def block(kind,label):
    for m in re.finditer(r'\\begin\{'+kind+r'\}.*?\\end\{'+kind+r'\}',s,re.S):
        if '\\label{'+label+'}' in m[0]: return m[0]
    raise ValueError(label)
def caption(t,new):
    start=t.index('\\caption{')+len('\\caption{'); depth=1; end=start
    while depth:
        if t[end]=='{': depth+=1
        elif t[end]=='}': depth-=1
        end+=1
    return t[:start]+new+t[end-1:]
keep={
 'FIGURE_COLLAPSE':('figure','fig:collapse',r'Reward-scale transfer on Diagnosis. In (a), separately evaluated usage curves shift when rewards and sensing costs are multiplied by $\alpha\in\{0.1,1,10\}$. In (b), plotting against $w/\alpha$ collapses them exactly, including the $B{=}8$ grid bracket $(0.141,0.323]$. Points and error bars are means $\pm1$ seed-level SE over five seeds and $100$ episodes per seed, with shared per-episode streams. Lines guide the eye. Bands and open--closed endpoints mark grid brackets, not uncertainty intervals or policies attaining the target. The crossing between sampled points remains unresolved.'),
 'FIGURE_DUAL':('figure','fig:dualmultiseed',r'Online control on Diagnosis through a tenfold reward-and-cost rescale at episode $200$. Columns compare decay-only and reset-on-shift. Top panels show weight, as median and interquartile range over ten seeds. Bottom panels show rolling usage with window $20$ and target $B{=}8$. Recovery uses post-shift-only windows and a $20$-episode hold within $\pm1$ of the target. Restricted recovery time $\min(T,180)$ averages $157.3$ versus $51.2$ episodes, with paired difference $106.1$ and Student-$t$ $95\%$ interval $[96.8,115.4]$. This nonstationary experiment is outside Proposition~\ref{prop:pi5}.'),
 'FIGURE_PARETO':('figure','fig:pareto',r'Reward and success across eleven information weights from $0.01$ to $200$. The $w{=}1$ Planning+IG diamond and EFE star coincide under their equivalence assumptions and shared tie-breaking. They attain the largest sampled mean reward on Tiger, Diagnosis, and Bandit. On Testbed they trade reward for success, and on Tileworld $w{=}20$ dominates them on both axes. Labels identify sampled weights sharing a point. Error bars are seed-level SE, visible where larger than markers.'),
 'TABLE_SARSOP':('table','tab:sarsop',r'SARSOP and EFE ($w{=}1$) on the three core environments, five seeds and $500$ episodes per seed, $\gamma{=}0.999$. Values are means $\pm$ seed-level SE. Usage counts observations. Fixed-margin TOST and its retrospective/prospective scope are described in the text.'),
 'TABLE_CPOMDP':('table','tab:cpomdp',r'Estimated cap-constrained reference at EFE usage $B_{\mathrm{EFE}}$. $R_{\mathrm{ref}}$ maximizes reward over mixtures of sampled SARSOP-Lagrangian policies with usage at most that budget. Gap is $R_{\mathrm{ref}}-R_{\mathrm{EFE}}$, not a certified optimality gap. On each environment the best sampled reference is already feasible, so the cap does not bind. Values use five seeds and $300$ episodes per seed. The actually evaluated usage-matched Planning+IG grid weights produce the same rewards as EFE in this run.'),
 'TABLE_CORE':('table','tab:main',r'Core comparison, $1{,}000$ episodes per seed over five seeds. Reward is mean $\pm$ seed-level SE. Here $w^*=w^*_{\mathrm{succ}}$ is tuned for success, with reward tuning reported separately. Bold identifies EFE and its exact Tiger tie with Planning, not a per-column winner. Success-tuned Planning+IG buys greater accuracy at a reward cost. Full agents, pooled uncertainties, and statistical comparisons are in Appendices~\ref{app:full_tables} and~\ref{app:stats}.'),
}
for token,(kind,label,cap) in keep.items():
    marker='% '+token
    assert main.count(marker)==1,token
    main=main.replace(marker,caption(block(kind,label),cap))
# Compact table consists exclusively of cells copied from the existing generated table.
table=(Path('paper/tables/budget_frontier.tex')).read_text()
parts=table.split('\\begin{table}[t]')[1:]
def rows(t):
    return [line.split(' & ') for line in t.splitlines() if re.match(r'(Tiger|Diagnosis|Bandit) & ',line) and 'unattainable' not in line]
r1,r3=rows(parts[0]),rows(parts[2]); assert len(r1)==len(r3)==12
compact=r'''\begin{table}[t]
\centering
\caption{Endpoint-mixture calibration on held-out seeds, $100$ episodes per seed over five seeds. $B$ is the calibration-derived expected-use target. $U$ and $R$ are held-out mixture usage and reward. The paired gap is mixture reward minus the same-stream cap-reference envelope, with seed-level SE. Its support and weights are fitted on those same seed means and held fixed for the SE, so intervals derived from this column are nominal pointwise plug-in summaries, as qualified in the text. Tiger's gap row duplicates its middle target. All three below-range targets are declared unattainable. Complete within-family and reference comparisons appear in Table~\ref{tab:budget_frontier}.}
\label{tab:budget_frontier_main}
%% All numerical cells copied from tables/budget_frontier.tex, produced by
%% experiments/run_budget_frontier.py and run_frontier_reference_heldout.py.
\tablefontsize
\setlength{\tabcolsep}{4pt}
\begin{tabular}{@{}llcccc@{}}
\toprule
Environment & Target & $B$ & $U$ & $R$ & Paired gap \\
\midrule
'''
last=None
for a,b in zip(r1,r3):
    assert a[:2]==b[:2]
    if last is not None and a[0]!=last: compact+='\\midrule\n'
    last=a[0]
    compact+=' & '.join([a[0],a[1].replace(' of range',''),a[2],a[4],a[5].removesuffix(r' \\'),b[4]])+'\n'
compact+=r'''\bottomrule
\end{tabular}
\end{table}'''
assert main.count('% TABLE_FRONTIER_COMPACT')==1
main=main.replace('% TABLE_FRONTIER_COMPACT',compact)
main=main.replace('\\subsection{Spatial and Interleaved Environments}', '\\subsection{Tileworld}')
main=main.replace('\\label{sec:rocksample}\nRockSample', '\\subsection{RockSample}\n\\label{sec:rocksample}\n\nRockSample')
main=main.replace('\\label{sec:inspection}\nInspection', '\\subsection{Structural Inspection}\n\\label{sec:inspection}\n\nInspection')
p.write_text(main)
# Preserve the original detailed evidence in the appendix, removing only floats
# already retained in main and old navigational overviews/closing repetitions.
exp,budget=s.split('\\section{Experiments on Shadow Prices and Sensing Budgets}',1)
budget,results=budget.split('\\section{Results}',1)
exp=exp.split('\\label{sec:experiments}\n',1)[1]
paras=exp.strip().split('\n\n')
exp='\n\n'.join(paras[1:-1])+'\n\n'
app=r'''\section{Extended Experimental Specifications and Protocols}
\label{app:experimental_protocol}

This appendix preserves the detailed environment definitions and evaluation protocols summarized in Section~\ref{sec:experiments}.

'''+exp
app+=r'''\section{Extended Budget Evidence}
\label{app:extended_budget_evidence}

The following studies retain the detailed protocols, auxiliary comparisons, and robustness analyses behind Section~\ref{sec:budget_experiments}. The main text carries the primary calibration results and their principal limitations.

'''
budget=budget[budget.index('\\subsection{Curve Collapse'):]
rename={'sec:collapse':'app:scale_details','sec:dual_multiseed':'app:dual_details','sec:sarsop':'app:sarsop_details','sec:cpomdp':'app:cpomdp_details','sec:budget_frontier':'app:frontier_details'}
for old,new in rename.items(): budget=budget.replace('\\label{'+old+'}', '\\label{'+new+'}')
for token in ['FIGURE_COLLAPSE','FIGURE_DUAL','TABLE_SARSOP','TABLE_CPOMDP']:
    kind,label,_=keep[token]; assert block(kind,label) in budget
    replacement=''
    if label=='tab:cpomdp':
        replacement=r'''The usage-matched Planning+IG grid weights evaluated in Table~\ref{tab:cpomdp} are $0.00$, $0.45$, and $1.07$ for Tiger, Diagnosis, and Bandit. They are nearest grid points selected on a lighter usage curve rather than crossing brackets. Each lies on a run of consecutive sampled weights with constant usage that also straddles $w{=}1$, namely $[0,19.3]$, $[0.316,19.3]$, and $[0.72,1.64]$ respectively in \texttt{results\_price\_usage\_curves.csv}. The corresponding rewards in \texttt{results\_cpomdp\_baseline.csv}, columns \texttt{R\_PIG} and \texttt{R\_EFE}, agree to the precision stored. This observed agreement is not a consequence of Proposition~\ref{prop:equivalence} at weights other than $1$.'''
    budget=budget.replace(block(kind,label),replacement)
app+=budget
app+=r'''\section{Extended EFE Comparisons}
\label{app:extended_efe_results}

These analyses retain the full per-environment comparisons and behavioral qualifications summarized in Section~\ref{sec:results}.

'''
results=results[results.index('\\subsection{Core Environments}'):]
results=results[:results.index('\\subsection{Summary}')]
results=results.replace('\\subsection{Core Environments}', '\\subsection{Core Environments}\n\\label{app:core_details}',1)
for old,new in {'sec:pareto':'app:pareto_details','sec:tileworld':'app:tileworld_details','sec:rocksample':'app:rocksample_main_details','sec:inspection':'app:inspection_details'}.items(): results=results.replace('\\label{'+old+'}', '\\label{'+new+'}')
for token in ['TABLE_CORE','FIGURE_PARETO']:
    kind,label,_=keep[token]; assert block(kind,label) in results
    replacement=''
    if label=='tab:main':
        replacement=r'''Table~\ref{tab:main} uses seed-level reward SE, whereas Appendix~\ref{app:full_tables} reports pooled episode-level SE. The committed CSVs carry both. Pooled SE is smaller for some cells and larger for others, depending on within-seed and between-seed variation. The full tables omit untuned Info Gain rows that are bit-identical to Myopic and Tiger's pymdp-AIF row, which is bit-identical to Posterior-vote on all reported metrics (\texttt{results\_tiger.csv}).'''
    results=results.replace(block(kind,label),replacement)
app+=results
app=re.sub(r'\n{4,}', '\n\n',app)
(D/'evidence_appendix.tex').write_text(app)
print('Main words',len(main.split()),'Appendix words',len(app.split()))
# Test integration against the archived original full document without modifying it.
import subprocess
full=subprocess.check_output(['git','show','2d3bac4:paper/full_paper_jair.tex'],text=True); assert s in full
combined=full.replace(s,main).replace('\\appendix','\\appendix\n\n'+app,1)
labels=re.findall(r'\\label\{([^}]+)\}',combined)
from collections import Counter
print('Duplicate direct labels',[k for k,v in Counter(labels).items() if v>1])
alllabels=set(labels)
for f in re.findall(r'\\input\{([^}]+)\}',combined):
    q=Path('paper')/f
    if not q.suffix:q=q.with_suffix('.tex')
    if q.exists(): alllabels.update(re.findall(r'\\label\{([^}]+)\}',q.read_text()))
refs=set(re.findall(r'\\(?:ref|eqref)\{([^}]+)\}',combined))
print('Unresolved references',sorted(refs-alllabels))
