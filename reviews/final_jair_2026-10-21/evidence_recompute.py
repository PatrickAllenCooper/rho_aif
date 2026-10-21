"""Read-only checks from saved data; no episodes, fits, or resampling."""
from pathlib import Path
import hashlib, json, itertools
import numpy as np
import pandas as pd
from scipy import stats
ROOT=Path(__file__).resolve().parents[2]
R=ROOT/'results'
out={}
def load(name):return pd.read_csv(R/name)
def envelope(u,r,b,equality=False):
    # Enumerate all feasible one/two-policy mixtures, independent of project LP.
    choices=[]
    for i in range(len(u)):
        if (abs(u[i]-b)<1e-10 if equality else u[i]<=b+1e-10):choices.append((r[i],[(i,1.)]))
    for i,j in itertools.combinations(range(len(u)),2):
        if u[i]==u[j]:continue
        q=(b-u[i])/(u[j]-u[i])
        if -1e-10<=q<=1+1e-10:choices.append(((1-q)*r[i]+q*r[j],[(i,1-q),(j,q)]))
    return max(choices,key=lambda x:x[0]) if choices else None
# Restricted recovery from full traces, with independent rolling-window code.
dual=load('results_price_dual_multiseed.csv'); recover={}
for (variant,seed),g in dual.groupby(['variant','controller_seed']):
    u=g.sort_values('episode').usage.to_numpy()[200:]
    means=np.concatenate([np.full(19,np.nan),np.convolve(u,np.ones(20)/20,mode='valid')])
    hits=[t for t in range(181) if np.all(np.abs(means[t:t+20]-8)<=1+1e-12)]
    recover[(variant,int(seed))]=hits[0] if hits else 180
saved=load('results_price_dual_multiseed_metrics.csv')
for row in saved.itertuples():assert recover[(row.variant,int(row.controller_seed))]==row.readapt_restricted
seeds=sorted(dual.controller_seed.unique()); a=np.array([recover[('decay',s)] for s in seeds]);b=np.array([recover[('reset',s)] for s in seeds]);d=a-b
out['recovery']={'decay':a.tolist(),'reset':b.tolist(),'means':[a.mean(),b.mean()],'difference':d.mean(),'ci95':list(stats.t.interval(.95,9,loc=d.mean(),scale=stats.sem(d))),'all_favor_reset':bool((d>0).all()),'max_weight':dual.weight.max()}
out['recovery']['observed_recoveries']=saved.groupby('variant').readapt.count().to_dict()
# Endogenous cap references.
front=load('results_cpomdp_frontier.csv'); base=load('results_cpomdp_baseline.csv'); check=[]
for row in base.itertuples():
    g=front[front.env==row.env];best=envelope(g.usage.to_numpy(),g.reward.to_numpy(),row.budget_B_EFE)
    assert abs(best[0]-row.R_ref)<1e-10
    check.append({'env':row.env,'R_ref':best[0],'EFE_gap':row.R_EFE-best[0],'maximum_reward_policy_feasible':bool(g.loc[g.reward.idxmax(),'usage']<=row.budget_B_EFE)})
out['endogenous']=check
# Held-out mixtures and independently enumerated cap and equality envelopes.
fam=load('results_budget_frontier.csv');mix=fam[fam.policy=='mixture'];mix=mix[mix.heldout_usage.notna()]
assert len(mix)==12
out['usage']={'rows':len(mix),'max_absolute_error':(mix.heldout_usage-mix.budget).abs().max(),'overspend_rows':int((mix.heldout_usage>mix.budget).sum())}
cap=load('results_budget_frontier_heldout_reference.csv');cap=cap[cap.policy=='mixture'];cap=cap[cap.paired_gap.notna()]
cf=load('results_cpomdp_frontier_heldout.csv');target=load('results_budget_frontier_target_reference.csv');sub=load('results_cpomdp_frontier_subsidy.csv')
for row in cap.itertuples():
    g=cf[cf.env==row.env];best=envelope(g.usage.to_numpy(),g.reward.to_numpy(),row.budget)
    assert abs(best[0]-row.heldout_reference)<1e-10
    m=mix[(mix.env==row.env)&(mix.budget_kind==row.budget_kind)].iloc[0]
    family=np.fromstring(m.per_seed_reward,sep='|');ref=sum(q*np.fromstring(g.iloc[i].per_seed_reward,sep='|') for i,q in best[1]);delta=family-ref
    assert abs(delta.mean()-row.paired_gap)<1e-9 and abs(stats.sem(delta)-row.paired_gap_se)<1e-9
for row in target.itertuples():
    g=sub[sub.env==row.env];best=envelope(g.heldout_usage.to_numpy(),g.heldout_reward.to_numpy(),row.budget,True)
    assert abs(best[0]-row.target_reference)<1e-9
out['references']={'cap_negative_ci':cap[cap.paired_gap_ci_hi<0][['env','budget']].drop_duplicates().to_dict('records'),'target_heldout_negative_ci':target[target.heldout_ci_hi<0][['env','budget','heldout_gap']].drop_duplicates().to_dict('records'),'target_fresh_negative_ci':target[target.fresh_ci_hi<0][['env','budget','fresh_gap']].drop_duplicates().to_dict('records')}
# Paired TOST recomputation from 60 seed rows.
tost=load('results_tost_sarsop_episode_paired_per_seed.csv');checks=[]
for env,g in tost.groupby('env'):
    x=(g.mean_EFE-g.mean_SARSOP).to_numpy();se=stats.sem(x);margin=.5 if env=='Bandit' else 1
    p=max(stats.t.sf((x.mean()+margin)/se,len(x)-1),stats.t.cdf((x.mean()-margin)/se,len(x)-1)) if se else 0.
    checks.append({'env':env,'n':len(x),'diff':x.mean(),'se':se,'p_tost_paired':p})
out['tost']=checks
# Re-select POMCP constants independently; no planner runs.
tuning=load('results_pomcp_exploration_tuning.csv');canonical=load('results_pomcp_exploration_sweep.csv');sel=load('results_pomcp_exploration_selected.csv');chosen=[]
for (env,agent),g in tuning.groupby(['env','agent']):
    s=g.sort_values(['success','reward'],ascending=False).iloc[0];chosen.append({'env':env,'agent':agent,'label':s.label})
    expected=sel[sel.env==env]['label_efe' if agent=='MCTS-EFE' else 'label_pomcp'].unique();assert len(expected)==1 and expected[0]==s.label
out['pomcp_selections']=chosen
ps=[]
for row in sel.itertuples():
    v1=row.se_efe**2;v2=row.se_pomcp**2;df=(v1+v2)**2/(v1*v1/4+v2*v2/4);p=2*stats.t.sf(abs(row.mean_efe-row.mean_pomcp)/(v1+v2)**.5,df)
    assert abs(p-row.p_seed_level)<1e-12;ps.append(p)
assert all(p<=.05/(6-i) for i,p in enumerate(sorted(ps)))
out['selected_pomcp_welch_pvalues']=ps
# Reconstruct sensor summary from saved per-case candidates/selection, and intervals from saved bootstrap arrays.
sensor=R/'real_sensor_2026-10-01';selected=json.loads((sensor/'selection.json').read_text())['selected'];rows=np.load(sensor/'evaluation/rows.npz');summary=load('results_real_sensor_summary.csv');summary=summary[summary.partition!='calibration'];errors=[]
for row in summary.itertuples():
    if row.partition!='test' and not (row.partition.startswith('batch') and row.partition[5:].isdigit()):continue
    q=selected[row.method]['weights'];mask=(rows['split']=='test') if row.partition=='test' else ((rows['batch']==int(row.partition[5:]))&(rows['split']=='shift'))
    if q is None:continue
    for metric in ['correctness','usage','reward']:
        val=sum(weight*np.load(sensor/'evaluation'/f'{name}.npz')[metric][mask].mean() for name,weight in q.items())
        errors.append(abs(val-getattr(row,metric)))
assert max(errors)<1e-12
boot=np.load(sensor/'bootstrap.npz');analysis=json.loads((sensor/'analysis.json').read_text());ci=[]
for b in [2,4,8]:
    vals=boot[f'crossing_B{b}__usage']-b;valid=np.isfinite(vals);levels=[.05/6,1-.05/6]
    interval=np.quantile(vals[valid],levels).tolist() if valid.any() else None
    if interval is not None:assert np.allclose(interval,[analysis['bootstrap'][str(b)]['usage_error_interval'][k] for k in ['lower','upper']],rtol=0,atol=1e-12)
    ci.append({'B':b,'valid':int(valid.sum()),'failed':int((~valid).sum()),'usage_error_ci':interval})
out['sensor']={'max_per_case_summary_error':max(errors),'recomputed_cells':len(errors),'usage_intervals':ci,'test_values':summary[(summary.partition=='test')&summary.method.str.contains('crossing|direct_target|cmi|weight_target')][['method','usage','correctness']].fillna('unavailable').to_dict('records')}
# Sensor candidate hash manifests, source model, and fixed protocol chronology.
hashchecks=0
for part in ['calibration','evaluation']:
    metadata=json.loads((sensor/part/'complete.json').read_text())
    for entry in metadata['policies']:
        assert hashlib.sha256((sensor/part/f"{entry['name']}.npz").read_bytes()).hexdigest()==entry['archive_sha256'];hashchecks+=1
out['sensor']['candidate_hash_checks']=hashchecks
sc=load('results_price_scale_collapse.csv');assert (sc.usage_spread==0).all();out['scale_collapse']={'cells':len(sc),'max_spread':float(sc.usage_spread.max()),'environments':list(sc.env.unique())}
stability=load('results_price_bracket_stability.csv')
out['bracket_stability']={'rows':len(stability),'all_samples_agree':int((stability.frac_reported==1).sum()),'at_least_99pct_agree':int((stability.frac_reported>=.99).sum()),'min_agreement':stability.frac_reported.min()}
pareto=load('results_pareto_sweep.csv');out['pareto_reward_maximum_weights']={env:g.loc[np.isclose(g.reward,g.reward.max(),rtol=0,atol=1e-10),'w'].tolist() for env,g in pareto.groupby('env')}
out['source_sha256']=hashlib.sha256((ROOT/'paper/full_paper_jair.tex').read_bytes()).hexdigest()
path=Path(__file__).with_name('evidence_recompute.json');path.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
