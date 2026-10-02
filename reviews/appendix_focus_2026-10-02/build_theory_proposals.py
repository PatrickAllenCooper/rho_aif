from pathlib import Path
import json,re,hashlib
root=Path(__file__).resolve().parents[2]
base=root/'paper/legacy/2026-10-02_pre_claim_focused_appendices'
j=(base/'full_paper_jair.tex').read_text()
l=(base/'full_paper.tex').read_text()
changes=[]
def add(id, old,new,reason):
    assert old and j.count(old)==1,(id,'JAIR',j.count(old))
    assert l.count(old)==1,(id,'LNCS',l.count(old))
    changes.append(dict(id=id,old=old,new=new,reason=reason))
def span(a,b):
    start=j.index(a)
    end=j.index(b,start)
    return j[start:end]
add('theory-focus-01',span('Equation~\\ref{eq:efe_recursive} uses recursive closed-loop EFE','\\subsection{Two-State Thresholds'),
    'The equivalence proof concerns the reward-based recursion and information units specified in Section~\\ref{subsec:formal_rho_equiv}. Related Work distinguishes this objective from other EFE formulations.\n\n',
    'The main formal-equivalence section already gives the normalizer derivation, conditional pragmatic identification, nat/bit distinction and scale dependence, while Related Work names the alternative EFE constructions. Keep the OTC schematic and a short scope pointer rather than restating these limitations here.')
add('theory-focus-02',span('Only Tiger in Table~\\ref{tab:alpha_eta}', '\\paragraph{Discounting.}'),'',
    'Remove the auxiliary cross-domain threshold table and its interpretation. Only one row satisfies the stated theorem assumptions; the other rows are heuristic reductions or a boundary case, and the longer-horizon measured outcomes already have direct empirical support. The full proposition and confirming/disconfirming proof remain verbatim. Requires removal of the main-text promise of tabulated heuristic comparisons and the Testbed table pointer.')
old=span('Current information gain is immediate while the eventual commit reward is discounted.', '\\subsection{State-Preservation Proof')
add('theory-focus-03',old,
    "Current information gain is immediate while the eventual commit reward is discounted. This increases the epistemic share along a branch but need not increase sensing, because the entire continuation is discounted relative to committing now. Appendix~\\ref{app:discount} reports the behavioral sensitivity.\n\n",
    'Retain the discounted recursion and its nontrivial behavioral qualification, but leave the numerical discount comparison with its own results.')
add('theory-focus-04',span('Figure~\\ref{fig:state_preservation} isolates the timing distinction', '\\begin{proof}[Proof sketch]'),'',
    'Remove a second schematic that repeats the complete destructive-sensing example directly above it. The example retains its original narrative and every displayed calculation. Main-text Figure pointer must be removed. The basic OTC loop diagram remains.')
add('theory-focus-05',span('The hypothesis can model non-destructive testing', '\\begin{remark}[Transition-aware information gain]'),'',
    'Delete a generic application paragraph that repeats the exact-state-preservation warning in the main text and introduces no protocol or proof step.')
add('theory-focus-06',span('Example~\\ref{ex:destructive} limits the state-preserving reduction, not EFE with correct transition dynamics.', '\\end{remark}'),
    "For general transitions, compute information gain by comparing the transition-aware posterior $b'_{o,T}$ with the corresponding predictive distribution over the post-transition state. Genuine information about that state can remain. A nonzero $\\Delta_T$ witnesses failure of state preservation, but zero does not establish it. The diagnostic is neither an established additive value correction nor a decision-error bound. Extending the budget procedure to these dynamics, or proving a perturbation bound, remains open.\n",
    'The posterior formula and the destructive example\'s zero information gain and value 1-c are already derived immediately above. Remove that repeated derivation while retaining the general transition-aware prescription and every diagnostic limitation.')
add('theory-focus-07',span('\\subsection{Agent Specifications and Weight Selection}', '\\subsection{Proof and Numerical Check of the Usage-Onset Corollary}'),
    "\\subsection{Agent Implementation Details}\n\\label{app:theory_agents}\n\nSection~\\ref{sec:agents} specifies the objectives, tuning grid, episode counts and tie rules. The success-weight tuner is \\texttt{tune\\_\\allowbreak info\\_\\allowbreak gain\\_\\allowbreak weight} in \\texttt{experiments/\\allowbreak run\\_\\allowbreak experiment.py}. Greedy samples unchecked rocks in RockSample and diagnoses from the prior without tests in Inspection. Epistemic-only compares information gain with sensing cost, with no reward-aware stopping, and selects the belief-argmax state on commitment.\n\n",
    'Remove repeated definitions, the duplicate full tuning protocol, and auxiliary ablation/consistency interpretation. The main Agents section already contains the entire tuning protocol, distinctions between reward and success tuning, and posterior-vote caveat. Retain the implementation pointer and domain-specific Greedy behavior here. Main appendix pointer should say implementation details.')
old=span('\\texttt{TestProp2OnsetExact} in \\url{tests/test_budget.py}', '\\subsection{Proof and Implementation Scope of the Online Controller}')
new="\\texttt{TestProp2OnsetExact} in \\url{tests/test_budget.py} checks the onset with the implemented $H=1$ planner over complete receding-horizon episodes. It therefore asserts zero usage below the threshold and at least one observation above it, rather than the one-shot proof's exact usage of one.\n\n"
add('theory-focus-08',old,new,
    'Keep the implementation check and the essential distinction between a one-shot theorem and full receding-horizon episodes. Remove the numerical unit-test walkthrough and optional refined-grid experimental pointer. The full onset proof remains verbatim.')
old=span('The implementation and its three variants are specified in Section~\\ref{sec:pi5}.', 'Let $\\mathcal{F}_t$ be the history before episode $t$')
new="Only the projected decaying-step variant specified in Section~\\ref{sec:pi5} is covered below. It is implemented by \\texttt{DualWeightAgent} in \\texttt{rho\\_\\allowbreak aif/\\allowbreak agents/\\allowbreak dual\\_\\allowbreak descent.py} and \\texttt{dual\\_\\allowbreak update} in \\texttt{rho\\_\\allowbreak aif/\\allowbreak budget.py}.\n\n"
add('theory-focus-09',old,new,
    'The historical stochastic-approximation attribution is already given beside the main proposition. Remove its second telling and retain the implementation pointer and full direct supermartingale/running-average proof unchanged.')
old=span('\\subsection{Relationship to Constrained Planning and Experimental Design}', '\\FloatBarrier\n\\section{Extended Experimental Specifications and Protocols}')
rs=span('The same reference construction does not reach EFE\'s operating region on RockSample[7,8].','Sequential Bayesian experimental design selects experiments')
new="\\subsection{Limit of the RockSample Constrained Reference}\n\\label{app:theory_positioning}\n\n"+rs
add('theory-focus-10',old,new,
    'The main Related Work and budget-positioning sections already explain CMDPs, rational inattention, SAC, CPOMDP randomization, experimental design, EFE-internal constraints, recursive dual ascent, calibration cost and scale transfer. Retain only the specific failed RockSample reference diagnostic and its producer. Main promise of detailed prior-art comparisons must instead point to this diagnostic.')
old=span('Sections~\\ref{sec:experiments} and Appendix~\\ref{app:envs} specify the environments, episode counts and statistical protocol.', 'Our RockSample variant differs from')
new='Sections~\\ref{sec:experiments} and Appendix~\\ref{app:envs} specify the environments, episode counts and statistical protocol. Battery-specific counts and seeding differ, so estimates are not interchangeable. All simulators use the Gymnasium Python interface \\citep{towers2024}.\n\n'
add('theory-focus-11',old,new,
    'Remove the repeated illustrative Tiger observation counts. Preserve the warning against cross-battery numerical interchange and the simulator interface citation. The RockSample, Inspection and public-sensor protocol paragraphs remain unchanged.')
for source,label in [(j,'jair'),(l,'lncs')]:
    revised=source
    for p in changes:
        assert revised.count(p['old'])==1,(label,p['id'])
        revised=revised.replace(p['old'],p['new'])
    # Independently check that proofs and complete retrospective-sensor protocol survive byte for byte.
    proofs=lambda s:re.findall(r'\\begin\{proof\}(?:\[[^\]]*\])?.*?\\end\{proof\}',s,re.S)
    assert proofs(source)==proofs(revised),label
    s=source[source.index('\\subsection{Retrospective Sensor-Acquisition Protocol}'):source.index('\\section{Extended Budget Evidence}')]
    assert s in revised,label
    owned=lambda s:s[s.index('\\section{Methodological and Budget-Theory Details}'):s.index('\\section{Extended Budget Evidence}')]
    print(label,'owned words',len(owned(source).split()),'->',len(owned(revised).split()),'removed labels', sorted(set(re.findall(r'\\label\{([^}]+)\}',source))-set(re.findall(r'\\label\{([^}]+)\}',revised))))
(root/'reviews/appendix_focus_2026-10-02/theory_proposals.json').write_text(json.dumps(changes,indent=2)+'\n')
print('Wrote',len(changes),'guarded changes; full proofs and public sensor protocol unchanged')
