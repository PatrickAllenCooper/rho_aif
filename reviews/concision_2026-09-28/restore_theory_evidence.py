"""Prepare selective restoration of core evidence; never edit masters."""
from pathlib import Path
import re
p=Path(__file__).parent
main=(p/'theory_main.tex').read_text()
app=(p/'theory_appendix.tex').read_text()

def replace_once(s, old, new):
    assert s.count(old)==1, (old[:100],s.count(old))
    return s.replace(old,new,1)

start=app.index(r'\begin{example}[Destructive sensing')
end=app.index(r'\end{figure}',start)+len(r'\end{figure}')
example=app[start:end]
app=replace_once(app,example,'')
old=r'''State preservation is an exact hypothesis. Slow drift alone does not ensure a small diagnostic: a perfect sensor gives a point-mass posterior, and an arbitrarily small probability of a state change can place mass outside its support, making $\Delta_T$ infinite. Example~\ref{ex:destructive} in Appendix~\ref{app:theory_factored} shows a complete action-ranking reversal from using obsolete information. This limits the reduction, not transition-aware EFE. Recomputing predictive and posterior information about the post-transition state removes the example's illusory credit. We have not established $\Delta_T$ as an additive value correction or a decision-error bound, and extending the budget machinery to state-changing sensing remains open.'''
new=r'''State preservation is an exact hypothesis. Slow drift alone does not ensure a small diagnostic: a perfect sensor gives a point-mass posterior, and an arbitrarily small probability of a state change can place mass outside its support, making $\Delta_T$ infinite. Example~\ref{ex:destructive} shows a complete action-ranking reversal from using obsolete information.

'''+example+r'''

This example limits the state-preserving reduction, not transition-aware EFE. Recomputing predictive and posterior information about the post-transition state removes its illusory credit. We have not established $\Delta_T$ as an additive value correction or a decision-error bound, and extending the budget machinery to state-changing sensing remains open. Appendix~\ref{app:theory_factored} gives the proof of Proposition~\ref{prop:factored} and the fuller scope discussion.'''
main=replace_once(main,old,new)
app=replace_once(app,'The following example makes precise what fails and how badly.',r'Example~\ref{ex:destructive} makes precise what fails and how badly.')

for label in ('prop:pi1','prop:pi2'):
    header='\\paragraph{Proof of Proposition~\\ref{'+label+'}.}'
    i=app.index(header)
    a=app.index(r'\begin{proof}',i)
    b=app.index(r'\end{proof}',a)+len(r'\end{proof}')
    proof=app[a:b]
    app=app[:i]+app[b:]
    loc=main.index('\\label{'+label+'}')
    insert=main.index(r'\end{proposition}',loc)+len(r'\end{proposition}')
    main=main[:insert]+'\n'+proof+main[insert:]

main=replace_once(main,r'The proof follows by preserving each action ranking and inducting over decision points (Appendix~\ref{app:theory_budget_proofs}). ', '')
main=replace_once(main,r'Adding the two optimality inequalities proves the information-gain inequality. Substitution then proves the return inequality (Appendix~\ref{app:theory_budget_proofs}). Neither implies monotone observation count.',r'These inequalities do not imply monotone observation count.')
app=replace_once(app,r'\subsection{Scale equivariance and usage-threshold proofs}',r'\subsection{Proof and numerical check of the usage-onset corollary}')
app=replace_once(app,r'\paragraph{Proof and numerical check of Corollary~\ref{cor:pi4}.}',r'The scale-equivariance and comparative-statics proofs appear with Propositions~\ref{prop:pi1} and~\ref{prop:pi2}. We give the onset argument and its implementation check here.')
app=re.sub(r'\n{3,}', '\n\n',app)
(p/'theory_main_restored.tex').write_text(main)
(p/'theory_appendix_restored.tex').write_text(app)
print('restored main',len(main.split()),'restored appendix',len(app.split()))
