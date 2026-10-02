"""Initial main-text withdrawals necessitated by removing peripheral appendices.

Historical proposal producer; later audit refinements belong in the final JSON.
"""
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE=ROOT/'paper/legacy/2026-10-02_pre_claim_focused_appendices'
texts={n:(BASE/n).read_text() for n in ('full_paper_jair.tex','full_paper.tex')}
rows=[]
def add(key,old,new,reason):
    for name,s in texts.items():
        assert s.count(old)==1,(key,name,s.count(old))
    rows.append(dict(id=key,old=old,new=new,reason=reason))
add('root-01',r'Appendices retain proofs, complete tables, robustness studies, and implementation details.',
    r'Appendices provide proofs, experiment specifications, and controls needed to interpret these claims.',
    'Describe the focused supporting material without promising complete tables for peripheral studies.')
add('root-02',r' We include an observe-then-commit IDS baseline in Appendix~\ref{app:ids}.','',
    'Remove the promise of a peripheral core-domain IDS comparison. The distinct distractor failure remains.')
add('root-03',r'The reward-maximizing weight scales with $k$ (Appendix~\ref{app:reward_scaling}). Proposition~\ref{prop:pi1} gives the corresponding usage identities.',
    r'Proposition~\ref{prop:pi1} establishes this equivariance and gives the corresponding usage identities.',
    'The theorem supplies the scale argument; omit the separate reward-optimal sampled-grid experiment.')
add('root-04',r'Only Tiger among the tabulated comparisons satisfies those assumptions. Diagnosis and Tileworld use unproved two-state reductions, and Testbed lies at the boundary $|R^-|=R^+$.',
    r'Tiger satisfies these assumptions, while Testbed lies at the boundary $|R^-|=R^+$. The proposition does not apply directly to Diagnosis or Tileworld.',
    'Remove the heuristic cross-domain threshold table while keeping the scope restriction explicit.')
add('root-05',r'Appendix~\ref{app:theory_factored} gives the complete example and Figure~\ref{fig:state_preservation}.',
    r'Appendix~\ref{app:theory_factored} gives the complete calculation.',
    'Keep the destructive-sensing counterexample without promising its redundant timing schematic.')
add('root-06',r' The \texttt{pymdp} check in Appendix~\ref{app:pymdp} tests qualitative consistency of the epistemic term, not certified numerical equivalence \citep{heins2022}.','',
    'Remove the peripheral software consistency check, which is not evidence for the stated recursion proof.')
add('root-07',r'Additional baselines are Greedy without sensing, information-directed sampling (Appendix~\ref{app:ids}), and a posterior-vote rule.',
    r'Additional baselines are Greedy without sensing and a posterior-vote rule.',
    'Remove the core-domain IDS comparison from the main roster; the distractor adaptation remains locally defined.')
add('root-08',r' Appendix~\ref{app:theory_positioning} gives the detailed comparisons, including sequential experimental design.','',
    'Related Work and the main positioning already state the theoretical comparison.')
add('root-09',r'\subsection{Additional Onset and Operating-Point Checks}'+'\n'+r'\label{sec:budget_breadth_summary}'+'\n\n'+r'Positive-threshold two-state instances place the observed onset within one refined grid step, $3\%$, above the closed-form threshold, while standard negative-threshold instances observe already at $w{=}0$ (Appendix~\ref{sec:prop2exp}). The atlas collects the implicit $w{=}1$ budgets and two grid brackets per instance from the measured curves (Appendix~\ref{app:w_atlas}). These are measured operating points, not a universal predictive formula for the price.'+'\n\n','',
    'Drop the peripheral atlas and standalone summary subsection; the corollary still points to its numerical onset check.')
add('root-10',r" In the sampled random two-state family, approximately $21\%$ fail the study's chosen reward-gap criterion even at $H=3$ (Appendix~\ref{app:nearopt_horizon}).", '',
    'Remove discussion of the discarded exploratory random-horizon study.')
add('root-11',r'Larger weights can buy greater success at a reward cost, and transfer at the top of the grid can be costly (Table~\ref{tab:transfer}).',
    r'Larger weights can buy greater success at a reward cost.',
    'The main Pareto comparison already supports the trade-off; discard the redundant weight-transfer experiment.')
(HERE/'root_proposals.json').write_text(json.dumps(rows,indent=2)+'\n')
print('Prepared',len(rows),'guarded main-text repairs')
