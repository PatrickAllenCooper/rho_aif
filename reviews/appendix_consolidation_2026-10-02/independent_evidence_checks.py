"""Independent data-only checks for the appendix consolidation; no experiments."""
from pathlib import Path
import csv, hashlib, json, math, re
from decimal import Decimal, ROUND_HALF_UP
from collections import Counter
import numpy as np
from scipy.stats import t
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent

def rows(name):
    return list(csv.DictReader((ROOT/'results'/name).open()))
def first(rs, **kw):
    return next(r for r in rs if all(r[k]==str(v) for k,v in kw.items()))
def rounded(v,d):
    return str(Decimal(str(v)).quantize(Decimal(1).scaleb(-d),rounding=ROUND_HALF_UP))
def ci(vals):
    a=np.asarray(vals,dtype=float)
    return [float(a.mean()),float(a.mean()-1.96*a.std(ddof=1)/math.sqrt(len(a))),float(a.mean()+1.96*a.std(ddof=1)/math.sqrt(len(a)))]
E={}
rs=rows('results_showcase_asymmetry.csv')
p=first(rs,penalty=1,agent='Planning'); ig=first(rs,penalty=1,agent='InfoGain-Tuned'); efe=first(rs,penalty=1,agent='EFE')
E['asymmetry']={'source':'results/results_showcase_asymmetry.csv','penalty':1,'planning_reward':float(p['mean_reward']),'tuned_myopic_reward':float(ig['mean_reward']),'efe_reward':float(efe['mean_reward']),'planning_minus_tuned_ig':float(p['mean_reward'])-float(ig['mean_reward']),'planning_minus_efe':float(p['mean_reward'])-float(efe['mean_reward']),'episodes_per_seed':100,'seeds':5,'initial_claim_wrong_agent':True}
assert rounded(E['asymmetry']['planning_minus_tuned_ig'],1)=='1.6'
assert all(r['episodes_per_seed']=='100' and r['n_seeds']=='5' for r in rs)
rs=rows('results_showcase_obs_scaling.csv')
assert all(r['episodes_per_seed']=='100' and r['n_seeds']=='5' for r in rs)
E['obs_scaling']={'source':'results/results_showcase_obs_scaling.csv','episodes_per_seed':100,'n_seeds':5,'success_pairs':{k:[float(first(rs,num_tests_K=k,agent=a)['success_rate'])*100 for a in ['EFE','Planning']] for k in ['1','2','3']}}
rs=rows('results_pareto_sweep.csv')
b=first(rs,env='Bandit',w='0.5');tb=[r for r in rs if r['env']=='Testbed'];best=max(float(r['reward']) for r in tb)
E['pareto']={'source':'results/results_pareto_sweep.csv','bandit_w0_5_reward':float(b['reward']),'testbed_max_reward':best,'testbed_maximizing_grid_weights':[float(r['w']) for r in tb if float(r['reward'])==best],'grid':[float(r['w']) for r in tb]}
assert E['pareto']['testbed_maximizing_grid_weights']==[.01,.1,.5]
rs=rows('results_thresholds.csv')
E['thresholds']={'source':'results/results_thresholds.csv','testbed_upper_nats':float(first(rs,environment='Testbed')['w_thresh_upper_nats']),'tileworld_upper_nats':float(first(rs,environment='Tileworld')['w_thresh_upper_nats']),'tileworld_weight20_in_nats':20/math.log(2)}
rs=rows('results_mcts_efe_ablation_stats.csv');r=first(rs,env='Tiger',metric='observations',variant_b='no-tree-ig')
E['ablation']={'source':'results/results_mcts_efe_ablation_stats.csv','p':float(r['p_seed_level']),'holm_significant':r['significant_hb_seed_level']}
assert rounded(E['ablation']['p'],4)=='0.0014'
rs=rows('results_price_dual_multiseed_metrics.csv');dd={v:[r for r in rs if r['variant']==v] for v in ['decay','reset']}
E['dual']={'source':'results/results_price_dual_multiseed_metrics.csv'}
for v in dd:
    E['dual'][v]={key:ci([float(r[key]) for r in dd[v] if r[key]]) for key in ['readapt','readapt_restricted','pre_steady_err','post_steady_err']}
    E['dual'][v]['recovered']=sum(bool(r['readapt']) for r in dd[v])
delta=np.array([float(a['readapt_restricted'])-float(b['readapt_restricted']) for a,b in zip(dd['decay'],dd['reset'])])
E['dual']['paired_restricted']={'mean':float(delta.mean()),'min':float(delta.min()),'ci':[float(delta.mean()+k*t.ppf(.975,9)*delta.std(ddof=1)/math.sqrt(10)) for k in [-1,1]]}
E['dual']['post_error_reset_vs_decay']=dict(Counter('better' if float(b['post_steady_err'])<float(a['post_steady_err']) else 'worse' if float(b['post_steady_err'])>float(a['post_steady_err']) else 'tie' for a,b in zip(dd['decay'],dd['reset'])))
assert E['dual']['post_error_reset_vs_decay']=={'tie':4,'better':5,'worse':1}
rs=rows('results_cpomdp_baseline.csv')
E['cpomdp']={'source':'results/results_cpomdp_baseline.csv','weights':{r['env']:float(r['w_star_PIG']) for r in rs},'gaps':{r['env']:float(r['R_ref'])-float(r['R_EFE']) for r in rs}}
curves=rows('results_price_usage_curves.csv')
E['cpomdp']['plateaus_source']='results/results_price_usage_curves.csv'
E['cpomdp']['sampled_plateaus']={}
for env,lo,hi in [('Tiger',0,19.31),('Diagnosis',.316,19.31),('Bandit',.719,1.638)]:
    subset=[r for r in curves if r['env']==env and lo<=float(r['w'])<=hi]
    assert len({float(r['mean_usage']) for r in subset})==1
    E['cpomdp']['sampled_plateaus'][env]={'bounds':[float(subset[0]['w']),float(subset[-1]['w'])],'usage':float(subset[0]['mean_usage'])}
rs=rows('results_partition_sensitivity_6x6.csv')
E['partition']={'source':'results/results_partition_sensitivity_6x6.csv','modes':{}}
for mode in ['bitwise','random','overlapping']:
    a=first(rs,mode=mode,agent='EFE');b=first(rs,mode=mode,agent='Planning')
    v1=float(a['se_reward_seed_level'])**2;v2=float(b['se_reward_seed_level'])**2
    z=(float(a['reward'])-float(b['reward']))/math.sqrt(v1+v2)
    dof=(v1+v2)**2/(v1*v1/4+v2*v2/4)
    E['partition']['modes'][mode]={'welch_reward_p':float(2*t.sf(abs(z),dof)),'efe_scans':float(a['obs']),'planning_scans':float(b['obs']),'decimal_half_up_scans':[rounded(a['obs'],2),rounded(b['obs'],2)]}
assert rounded(E['partition']['modes']['random']['welch_reward_p'],2)=='0.24'
rs=rows('results_rocksample_11x11.csv');h=first(rs,agent='Rollout only (approach)')
d=rows('results_rocksample_efe_diagnostic.csv')[0]
E['rocksample']={'sources':['results/results_rocksample_11x11.csv','results/results_rocksample_efe_diagnostic.csv'],'heuristic_reward':float(h['mean_reward']),'heuristic_good':float(h['mean_good']),'diagnostic_efe_reward':float(d['mean_reward']),'diagnostic_efe_reward_decimal_half_up':rounded(d['mean_reward'],2)}
rs=rows('results_discount.csv')
E['discount']={'source':'results/results_discount.csv','rows':[]}
for env in ['Tiger','Diagnosis','Bandit']:
 for gamma in ['0.9','0.95','0.99','1.0']:
    a=first(rs,env=env,agent='EFE',gamma=gamma); b=first(rs,env=env,agent='Planning',gamma=gamma)
    E['discount']['rows'].append({'env':env,'gamma':gamma,'success_pct':[float(a['success'])*100,float(b['success'])*100],'gap_pp':100*(float(a['success'])-float(b['success'])),'obs':[float(a['obs']),float(b['obs'])],'reward':[float(a['reward']),float(b['reward'])]})
E['core_pooled_ses']={}
for env,n in [('Tiger','results_tiger.csv'),('Diagnosis','results_diagnosis_n4.csv'),('Bandit','results_bandit.csv')]:
 rs=rows(n); E['core_pooled_ses'][env]={a:rounded(first(rs,**{'':a})['se_reward_pooled'],2) for a in ['Myopic','Planning','Planning+IG','EFE']}
 E['core_pooled_ses'][env]['additional_rows']=[{k:r[k] for k in ['', 'mean_observations','success_rate','mean_reward','se_reward_pooled']} for r in rs if r[''] in ['InfoGain-Tuned','EpistemicOnly','Thompson']]
E['effect_sizes']={}
for env,n in [('Tiger','results_tiger_stats.csv'),('Testbed','results_summary_stats.csv'),('Diagnosis','results_diagnosis_n4_stats.csv'),('Bandit','results_bandit_stats.csv')]:
 rs=rows(n);vals=[]
 for a in ['Myopic','Planning','InfoGain-Tuned','Planning+IG','Thompson']:
    r=next(r for r in rs if r['metric']=='Reward' and {r['agent_a'],r['agent_b']}=={'EFE',a})
    vals.append(rounded(float(r['cohens_d'])*(1 if r['agent_a']=='EFE' else -1),2))
 r=next(r for r in rs if r['metric']=='Success' and {r['agent_a'],r['agent_b']}=={'EFE','Planning'})
 vals.append(rounded(float(r['cohens_d'])*(1 if r['agent_a']=='EFE' else -1),2))
 E['effect_sizes'][env]=vals
rs=rows('results_budget_frontier_target_reference.csv'); matched=rows('results_budget_frontier_target_reference_usage_matched.csv')
E['target_reference']={'source':'results/results_budget_frontier_target_reference.csv','negative_intervals':{stream:[{'env':r['env'],'kind':r['budget_kind'],'budget':float(r['budget'])} for r in rs if float(r[f'{stream}_ci_hi'])<0] for stream in ['heldout','fresh']},'usage_matched_source':'results/results_budget_frontier_target_reference_usage_matched.csv'}
E['source_hashes']={n:hashlib.sha256((ROOT/'paper'/n).read_bytes()).hexdigest() for n in ['full_paper_jair.tex','full_paper.tex']}
E['main_text_unchanged']={n:(ROOT/'paper'/n).read_text().split('\\appendix')[0]==(ROOT/'paper/legacy/2026-10-02_pre_appendix_consolidation'/n).read_text().split('\\appendix')[0] for n in ['full_paper_jair.tex','full_paper.tex']}
(OUT/'independent_evidence_checks.json').write_text(json.dumps(E,indent=2)+'\n')
print(json.dumps(E,indent=2))
