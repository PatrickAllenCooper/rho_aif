#!/usr/bin/env python3
"""Independent audit: no experiment-module imports; never refits or selects on test."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[k]='1'
import csv, hashlib, io, json, subprocess, time, zipfile
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[2]; D=R/'results/real_sensor_2026-10-01'; A=Path(__file__).parent
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
J=lambda p:json.loads(Path(p).read_text())
report={'started':time.time(),'checks':{},'hashes':{}}
def ck(name,value):
    assert value,name
    report['checks'][name]=True

def entropy(x):return -np.sum(np.where(x>0,x*np.log2(np.where(x>0,x,1)),0),axis=-1)

cfg=J(R/'experiments/protocols/gas_sensor_2026-10-01.json'); model=J(D/'model.json'); manifest=J(D/'dataset_manifest.json'); selection=J(D/'selection.json');analysis=J(D/'analysis.json')
ck('protocol_frozen',subprocess.check_output(['git','show','fb3a9de:experiments/protocols/gas_sensor_2026-10-01.json'],cwd=R)==(R/'experiments/protocols/gas_sensor_2026-10-01.json').read_bytes())
ck('protocol_markdown_hash',H(R/'experiments/protocols/gas_sensor_2026-10-01.md')==cfg['protocol_sha256'])
ck('selection_frozen',subprocess.check_output(['git','show','5a3a79d:results/real_sensor_2026-10-01/selection.json'],cwd=R)==(D/'selection.json').read_bytes())
ck('raw_hash',H(R/'data/raw/gas_sensor_224.zip')==manifest['zip_sha256'])
ck('model_hash',H(D/'model.json')==manifest['model_sha256'])
ck('prepared_hash',H(R/'data/processed/gas_sensor_224.npz')==manifest['prepared_sha256'])
X=[]; labels=[]; batches=[]; identities=[]
with zipfile.ZipFile(R/'data/raw/gas_sensor_224.zip') as z:
    for b in range(1,11):
        name=next(n for n in z.namelist() if n.endswith(f'/batch{b}.dat'))
        raw=z.read(name);ck(f'source_batch{b}_hash',hashlib.sha256(raw).hexdigest()==manifest['source_files'][name])
        for line_num,line in enumerate(raw.decode().splitlines(),1):
            if not line.strip():continue
            fields=line.split(); a={int(t.split(':')[0]):float(t.split(':')[1]) for t in fields[1:]}
            ck0=len(a)==128 and sorted(a)==list(range(1,129));assert ck0
            X.append([a[j] for j in range(1,129)]);labels.append(int(fields[0]));batches.append(b);identities.append(f'batch{b}:{line_num}')
X=np.asarray(X); labels=np.asarray(labels); batches=np.asarray(batches); identities=np.asarray(identities)
prepared=np.load(R/'data/processed/gas_sensor_224.npz'); split=prepared['split']; Z=prepared['Z']
ck('all_row_identities',np.array_equal(identities,prepared['row_id']) and np.array_equal(labels,prepared['y']) and np.array_equal(batches,prepared['batch']))
rowhash=np.asarray([hashlib.sha256(a.astype('<f8').tobytes()).hexdigest() for a in X]);ck('all_descriptors',np.array_equal(rowhash,prepared['descriptor_sha256']))
ck('no_early_duplicates_or_later_overlap',len(set(rowhash[batches<=6]))==sum(batches<=6) and not set(rowhash[batches<=6])&set(rowhash[batches>=7]))
rng=np.random.default_rng(cfg['seed_split']); recreated=np.full(len(X),'shift',dtype='U16')
for b,c in sorted(set(zip(batches[batches<=6],labels[batches<=6]))):
    ids=np.flatnonzero((batches==b)&(labels==c)); p=rng.permutation(len(ids));nt=int(.6*len(ids));nc=int(.2*len(ids))
    recreated[ids[p[:nt]]]='train';recreated[ids[p[nt:nt+nc]]]='calibration';recreated[ids[p[nt+nc:]]]='test'
ck('split_independently_reproduced',np.array_equal(recreated,split))
train=split=='train';classes=np.asarray(model['classes']);prior=np.asarray(model['prior']);L=np.asarray(model['likelihood']); centers=np.asarray(model['centers']);means=np.asarray(model['scaler_mean']);scales=np.asarray(model['scaler_scale'])
ck('training_provenance',model['provenance']['training_row_ids']==identities[train].tolist())
ck('training_scaler_means',np.allclose(X[train].mean(axis=0).reshape(16,8),means,rtol=1e-12,atol=1e-10))
ck('training_scaler_scales',np.allclose(X[train].std(axis=0).reshape(16,8),scales,rtol=1e-12,atol=1e-10))
for s in range(16):
    scaled=(X[:,s*8:(s+1)*8]-means[s])/scales[s]
    independent=((scaled[:,None]-centers[s])**2).sum(axis=2).argmin(axis=1)
    assert np.array_equal(independent,Z[:,s])
    for c,y in enumerate(classes):
        counts=np.bincount(Z[train&(labels==y),s],minlength=8)+1
        assert np.array_equal(counts/counts.sum(),L[s,c])
ck('every_encoding_and_likelihood_count',True)
counts=np.asarray([(labels[train]==y).sum() for y in classes])+1
ck('training_prior',np.array_equal(counts/counts.sum(),prior))

def qvector(sel,names):return None if sel['weights'] is None else np.asarray([sel['weights'].get(n,0.) for n in names])

part={}; all_candidates=0;paths=0
for partition in ('calibration','evaluation'):
    d=D/partition; meta=J(d/'complete.json');identity=J(d/'run_identity.json');rows=np.load(d/'rows.npz')
    ck(partition+'_manifest_hashes',H(d/'rows.npz')==meta['rows_sha256'] and H(d/'run_identity.json')==meta['run_identity_sha256'])
    ck(partition+'_model_identity',identity['model_sha256']==H(D/'model.json') and identity['prepared_sha256']==H(R/'data/processed/gas_sensor_224.npz'))
    source_map={'runner_sha256':'experiments/run_real_sensor_study.py','module_sha256':'rho_aif/real_sensor.py','budget_module_sha256':'rho_aif/budget.py'}
    ck(partition+'_code_hashes',all(H(R/source)==identity[key] for key,source in source_map.items()))
    if partition=='evaluation':ck('heldout_bound_to_frozen_selection',identity['selection_sha256']==H(D/'selection.json') and meta['started']>selection['created'])
    mask=split=='calibration' if partition=='calibration' else np.isin(split,['test','shift','shift_overlap']);assert np.array_equal(identities[mask],rows['row_id']); z=Z[mask]
    names=[p['name'] for p in meta['policies']]; results={};mat={k:[] for k in ('correctness','usage','reward','log_loss','brier')}
    for p in meta['policies']:
        name=p['name'];file=d/f'{name}.npz';assert H(file)==p['archive_sha256'];r=np.load(file);results[name]=r; all_candidates+=1
        u=r['usage'];o=r['order'];obs=r['observations'];assert np.array_equal((o>=0).sum(axis=1),u)
        posterior=np.tile(prior,(len(u),1))
        for t in range(16):
            active=np.flatnonzero(u>t); a=o[active,t];v=obs[active,t]
            assert np.array_equal(z[active,a],v)
            posterior[active]*=L[a,:,v];posterior[active]/=posterior[active].sum(axis=1)[:,None]
            assert np.all(o[u<=t,t]==-1) and np.all(obs[u<=t,t]==-1)
        assert all(len(set(row[:count]))==count for row,count in zip(o,u));assert np.allclose(posterior,r['posteriors'],rtol=1e-12,atol=1e-12)
        pred=classes[posterior.argmax(axis=1)];assert np.array_equal(pred,r['predictions'])
        assert np.array_equal((pred==rows['y']).astype(int),r['correctness']);assert np.array_equal(r['correctness']-.02*u,r['reward'])
        for k in ('correctness','usage','reward'):mat[k].append(r[k])
        targets=np.searchsorted(classes,rows['y']);mat['log_loss'].append(-np.log(posterior[np.arange(len(u)),targets]));mat['brier'].append(((posterior-np.eye(6)[targets])**2).sum(axis=1));paths+=len(u)
    part[partition]={'meta':meta,'identity':identity,'rows':rows,'names':names,'results':results,'mat':{k:np.asarray(v) for k,v in mat.items()},'Z':z}
ck('all_trajectory_hashes_paths_observations_posteriors_and_scores',True)
report['trajectory_counts']={'archives':all_candidates,'case_policy_paths':paths}
names=part['calibration']['names']; ck('candidate_alignment',names==part['evaluation']['names'])
# Exhaustive vertex enumeration is independent of production scipy.linprog.
def vertex(U,V,B,cap=False,all_optima=False):
    sols=[]
    for i,u in enumerate(U):
        if (cap and u<=B) or abs(u-B)<1e-12:sols.append((V[i],i,i,1.))
    ii,jj=np.triu_indices(len(U),1); good=((U[ii]-B)*(U[jj]-B)<0);ii=ii[good];jj=jj[good]
    q=(B-U[jj])/(U[ii]-U[jj]);vv=q*V[ii]+(1-q)*V[jj]
    sols.extend(zip(vv,ii,jj,q))
    if not sols:return None
    best=max(s[0] for s in sols)
    if all_optima:
        outputs=[]
        for v,i,j,p in sols:
            if best-v>1e-10:continue
            out=np.zeros(len(U));out[i]+=p;out[j]+=1-p;outputs.append(out)
        return outputs
    v,i,j,p=max(sols,key=lambda x:x[0]);out=np.zeros(len(U));out[i]+=p;out[j]+=1-p
    return out

def crossing(U,B):
    below=np.flatnonzero(U<B)
    if not len(below):return None
    i=below[-1];j=i+1
    if j>=len(U) or U[j]<B:return None
    q=np.zeros(len(U));q[j]=(B-U[i])/(U[j]-U[i]);q[i]=1-q[j];return q

cal=part['calibration']['mat'];wi=np.asarray([i for i,n in enumerate(names) if n.startswith('w')]);di=np.asarray([i for i,n in enumerate(names) if n.startswith('d')]);sel=selection['selected']
for name,s in sel.items():
    if s['family']=='anchor' or s['family'] in ('cmi','order'):continue
    idx=di if s['family'].startswith('direct') else wi;U=cal['usage'][idx].mean(axis=1);V=cal['reward'][idx].mean(axis=1);B=s['budget']
    q=crossing(U,B) if s['family']=='crossing' else vertex(U,V,B,cap='cap' in s['family']);q0=qvector(s,names)
    assert (q is None)==(q0 is None)
    if q is not None:
        assert abs(np.sum(q*V)-np.sum(q0*cal['reward'].mean(axis=1)))<1e-10
        assert abs(np.sum(q*U)-np.sum(q0*cal['usage'].mean(axis=1)))<1e-10
ck('all_frozen_crossings_and_lp_optima',True)
# Every summary, including log scores and balanced accuracy, from trajectory arrays.
summary=list(csv.DictReader((R/'results/results_real_sensor_summary.csv').open()))
for row in summary:
    if row['partition']=='shift_equal_batch':continue
    p='calibration' if row['partition']=='calibration' else 'evaluation';d=part[p];q=qvector(sel[row['method']],names)
    if q is None:assert row['feasible_on_calibration']=='False' and row['correctness']=='';continue
    mask=np.ones(len(d['rows']['y']),dtype=bool) if p=='calibration' else (d['rows']['split']=='test' if row['partition']=='test' else d['rows']['batch']==int(row['partition'][5:]))
    for k in d['mat']:
        val=np.sum(q[:,None]*d['mat'][k][:,mask],axis=0)
        assert np.isclose(val.mean(),float(row[k]),rtol=1e-11,atol=1e-11),(row['partition'],row['method'],k)
    correct=np.sum(q[:,None]*d['mat']['correctness'][:,mask],axis=0);y=d['rows']['y'][mask]
    assert np.isclose(np.mean([correct[y==c].mean() for c in np.unique(y)]),float(row['balanced_accuracy']),atol=1e-12)
for row in summary:
    if row['partition']!='shift_equal_batch':continue
    parts=[r for r in summary if r['method']==row['method'] and r['partition'] in ['batch7','batch8','batch9','batch10']]
    for k in part['calibration']['mat']:assert np.isclose(np.mean([float(r[k]) for r in parts]),float(row[k]))
ck('all_summary_cells_independently_recomputed',True)
# Reproduce every calibration/test bootstrap draw from saved outcomes, independently select.
tmask=part['evaluation']['rows']['split']=='test';te={k:v[:,tmask] for k,v in part['evaluation']['mat'].items()};cr=part['calibration']['rows'];tr={k:part['evaluation']['rows'][k][tmask] for k in ('batch','y')}
def strata(rows):return [np.flatnonzero((rows['batch']==b)&(rows['y']==c)) for b,c in sorted(set(zip(rows['batch'].tolist(),rows['y'].tolist())))]
cs,ts=strata(cr),strata(tr); rng=np.random.default_rng(cfg['seed_bootstrap']); boot=np.load(D/'bootstrap.npz');maxdelta=0.; LPties=0
for rep in range(cfg['bootstrap_replicates']):
    cw=np.zeros(len(cr['y']));tw=np.zeros(len(tr['y']))
    for ids in cs:cw[ids]=rng.multinomial(len(ids),np.full(len(ids),1/len(ids)))
    for ids in ts:tw[ids]=rng.multinomial(len(ids),np.full(len(ids),1/len(ids)))
    cw/=len(cw);tw/=len(tw)
    U=np.sum(cal['usage']*cw,axis=1);V=np.sum(cal['reward']*cw,axis=1);testmeans={k:np.sum(te[k]*tw,axis=1) for k in ('correctness','usage','reward')}
    for B in cfg['targets']:
        for family in ('crossing','weight_target','weight_cap','direct_target','direct_cap','cmi','order'):
            idx=di if family.startswith('direct') else wi
            if family in ('cmi','order'):
                q=np.zeros(len(names));q[names.index(f'{family}{B}')]=1
            else:
                small=crossing(U[idx],B) if family=='crossing' else vertex(U[idx],V[idx],B,cap='cap' in family)
                q=None if small is None else np.zeros(len(names))
                if q is not None:q[idx]=small
            if q is not None and family not in ('crossing','cmi','order') and any(abs(np.sum(q*testmeans[m])-boot[f'{family}_B{B}__{m}'][rep])>1e-8 for m in testmeans):
                options=vertex(U[idx],V[idx],B,cap='cap' in family,all_optima=True);found=False
                for small in options:
                    candidate=np.zeros(len(names));candidate[idx]=small
                    if all(abs(np.sum(candidate*testmeans[m])-boot[f'{family}_B{B}__{m}'][rep])<1e-8 for m in testmeans):q=candidate;found=True;break
                assert found,('No optimal vertex matches saved bootstrap',rep,B,family)
                LPties+=1
            for metric in testmeans:
                val=np.nan if q is None else np.sum(q*testmeans[metric]);saved=boot[f'{family}_B{B}__{metric}'][rep]
                if np.isnan(val):assert np.isnan(saved)
                else:
                    delta=abs(val-saved);maxdelta=max(maxdelta,delta)
                    # LP duplicate trajectories and objective ties may choose distinct indices but same outcomes.
                    assert delta<1e-8,(rep,B,family,metric,val,saved)
    if rep%500==0:print('bootstrap checked',rep,flush=True)
report['bootstrap_max_abs_difference']=maxdelta;report['bootstrap_lp_tie_alternative_matches']=LPties;ck('all_2000_bootstrap_reselections_independently_verified_including_optimal_ties',True)
for B in cfg['targets']:
    vals=boot[f'crossing_B{B}__usage']-B;finite=vals[np.isfinite(vals)];entry=analysis['bootstrap'][str(B)]
    assert entry['usage_error_interval']['failed_replicates']==len(vals)-len(finite)
    if len(finite):assert np.allclose(np.quantile(finite,[.05/6,1-.05/6]),[entry['usage_error_interval']['lower'],entry['usage_error_interval']['upper']])
    for other,metrics in entry['comparisons'].items():
        for m,iv in metrics.items():
            vals=boot[f'crossing_B{B}__{m}']-boot[f'{other}_B{B}__{m}'];finite=vals[np.isfinite(vals)]
            assert iv['failed_replicates']==len(vals)-len(finite)
            if len(finite):assert np.allclose(np.quantile(finite,[.025,.975]),[iv['lower'],iv['upper']])
ck('all_within_period_intervals_and_failure_counts',True)
# Seeded episode-level choices: independent RNG stream and full-policy selection.
real=np.load(D/'seeded_mixture_realizations.npz');mixrng=np.random.default_rng(cfg['seed_mixture'])
for group in ['calibration','test','batch7','batch8','batch9','batch10']:
    d=part['calibration' if group=='calibration' else 'evaluation']
    mask=np.ones(len(d['rows']['y']),dtype=bool) if group=='calibration' else (d['rows']['split']=='test' if group=='test' else d['rows']['batch']==int(group[5:]))
    for name,chosen in sel.items():
        q=qvector(chosen,names)
        if q is None:continue
        components=mixrng.choice(len(names),size=int(mask.sum()),p=q);ids=np.flatnonzero(mask)
        assert np.array_equal(components,real[f'{group}__{name}__component'])
        for metric in ('correctness','usage','reward'):assert np.array_equal(d['mat'][metric][components,ids],real[f'{group}__{name}__{metric}'])
ck('every_seeded_episode_mixture_realization',True)
# Every later-batch reported interval and selected resamples independently reconstructed.
shiftrng=np.random.default_rng(cfg['seed_bootstrap']+1);d=part['evaluation'];shift_draws=0
for b in cfg['shift_batches']:
    sb=np.load(D/f'bootstrap_batch{b}.npz');mask=d['rows']['batch']==b;n=int(mask.sum());ss=strata({k:d['rows'][k][mask] for k in ('batch','y')})
    for rep in range(cfg['bootstrap_replicates']):
        counts=np.zeros(n)
        for ids in ss:counts[ids]=shiftrng.multinomial(len(ids),np.full(len(ids),1/len(ids)))
        if rep not in (0,1,2,55,500,1000,1999):continue
        weights=counts/n
        for metric in ('correctness','usage','reward'):
            means=np.sum(d['mat'][metric][:,mask]*weights,axis=1)
            for name,chosen in sel.items():
                q=qvector(chosen,names);saved=sb[f'{name}__{metric}'][rep]
                if q is None:assert np.isnan(saved)
                else:assert abs(np.sum(q*means)-saved)<1e-10
        shift_draws+=1
    for B in cfg['targets']:
        expected=analysis['shift_intervals'][str(b)][str(B)]
        values={'usage_error':sb[f'crossing_B{B}__usage']-B,'accuracy_gap_direct':sb[f'crossing_B{B}__correctness']-sb[f'direct_target_B{B}__correctness'],'accuracy_gap_cmi':sb[f'crossing_B{B}__correctness']-sb[f'cmi_B{B}__correctness']}
        for metric,vals in values.items():
            finite=vals[np.isfinite(vals)];iv=expected[metric];assert iv['failed_replicates']==len(vals)-len(finite)
            if len(finite):assert np.allclose(np.quantile(finite,[.025,.975]),[iv['lower'],iv['upper']])
ck('later_batch_intervals_and_frozen_selection_bootstrap',True);report['shift_bootstrap_draws_recomputed']=shift_draws
report['headline_recomputed']={r['partition']+'__'+r['method']:{k:(float(r[k]) if r[k] else None) for k in ('correctness','usage','usage_error','reward','log_loss','brier')} for r in summary if r['method'] in ('crossing_B2','crossing_B4','crossing_B8','anchor_zero','anchor_all') and r['partition']!='calibration'}

# Direct scalar recomputation of action scores for 32 preselected records per partition and all candidates.
def action(belief,available,policy,order,step):
    if policy['kind']=='zero':return -1
    if policy['kind'] in ('fixed_order','all'):
        if policy['kind']=='fixed_order' and step>=policy['count']:return -1
        return order[step] if step<16 else -1
    if policy['kind']=='fixed_cmi' and step>=policy['count']:return -1
    if not available:return -1
    vals=[]
    for s in available:
        joint=belief[:,None]*L[s];prob=joint.sum(axis=0)
        info=entropy(prob)-np.sum(belief*entropy(L[s]));a=joint.max(axis=0).sum()
        vals.append(info if policy['kind']=='fixed_cmi' else a-.02+policy['weight']*max(info,0)-policy['penalty'])
    vals=np.asarray(vals);stop=belief.max();scale=max(abs(vals).max(),stop) if policy['kind']!='fixed_cmi' else abs(vals).max();tol=1e-12*scale
    if policy['kind']!='fixed_cmi' and vals.max()<=stop+tol:return -1
    return available[np.flatnonzero(vals>=vals.max()-tol)[0]]
info=np.asarray([entropy((prior[:,None]*L[s]).sum(axis=0))-np.sum(prior*entropy(L[s])) for s in range(16)]);order=[]
while len(order)<16:
    remain=[s for s in range(16) if s not in order];v=info[remain];order.append(remain[np.flatnonzero(v>=v.max()-1e-12*np.abs(v).max())[0]])
checked=0
for p,d in part.items():
    for ix in np.linspace(0,len(d['Z'])-1,32,dtype=int):
        for reg in d['meta']['policies']:
            pol=reg['policy'];r=d['results'][reg['name']];belief=prior.copy();available=list(range(16));path=[]
            for step in range(17):
                s=action(belief,available,pol,order,step)
                if s<0:break
                path.append(s);available.remove(s);belief*=L[s,:,d['Z'][ix,s]];belief/=belief.sum()
            assert path==r['order'][ix,:r['usage'][ix]].tolist(),(p,ix,pol['name'],path)
            checked+=1
ck('scalar_policy_paths_independently_recomputed',True);report['scalar_paths_checked']=checked
for p in ('experiments/protocols/gas_sensor_2026-10-01.md','experiments/protocols/gas_sensor_2026-10-01.json','rho_aif/real_sensor.py','experiments/run_real_sensor_study.py','experiments/analyze_real_sensor_study.py','results/real_sensor_2026-10-01/model.json','results/real_sensor_2026-10-01/selection.json','results/real_sensor_2026-10-01/analysis.json','results/results_real_sensor_summary.csv'):
    report['hashes'][p]=H(R/p)
report['elapsed_seconds']=time.time()-report['started'];report['snapshot_head']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
(A/'independent_evidence_audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
