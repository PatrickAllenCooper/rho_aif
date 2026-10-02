#!/usr/bin/env python3
"""Analyze the frozen real-record study, including calibration reselection."""
from __future__ import annotations
import csv
import json
import time
from pathlib import Path
import sys
import numpy as np

from run_real_sensor_study import OUT, ROOT, config, now, save_json, select_policies, sha, stamp


def load_partition(partition):
    directory=OUT/partition
    metadata=json.loads((directory/'complete.json').read_text())
    if sha(directory/'rows.npz')!=metadata['rows_sha256'] or sha(directory/'run_identity.json')!=metadata['run_identity_sha256']:
        raise RuntimeError('Row identities or run manifest changed')
    identity=json.loads((directory/'run_identity.json').read_text())
    if sha(OUT/'model.json')!=identity['model_sha256']:
        raise RuntimeError('Model identity changed')
    rows=np.load(directory/'rows.npz')
    names=[entry['name'] for entry in metadata['policies']]
    keys=('correctness','usage','reward')
    matrices={key:[] for key in keys}
    logloss=[]; brier=[]
    classes=np.array(json.loads((OUT/'model.json').read_text())['classes'])
    target=np.array([int(np.flatnonzero(classes==y)[0]) for y in rows['y']])
    onehot=np.eye(len(classes))[target]
    for entry in metadata['policies']:
        path=directory/f"{entry['name']}.npz"
        if sha(path)!=entry['archive_sha256']:raise RuntimeError('Trajectory hash mismatch')
        with np.load(path) as result:
            for key in keys:matrices[key].append(result[key])
            posterior=result['posteriors']
            logloss.append(-np.log(np.clip(posterior[np.arange(len(target)),target],np.finfo(float).tiny,1)))
            brier.append(np.square(posterior-onehot).sum(axis=1))
    matrices={key:np.asarray(values,dtype=float) for key,values in matrices.items()}
    matrices['log_loss']=np.asarray(logloss);matrices['brier']=np.asarray(brier)
    return names,rows,matrices


def mixture_vector(selection,names):
    if selection['weights'] is None:return None
    weights=selection['weights']
    if set(weights)-set(names):raise ValueError('Mixture refers to unknown candidates')
    q=np.array([weights.get(name,0.) for name in names],dtype=float)
    if not np.isfinite(q).all() or np.any(q<0) or not np.isclose(q.sum(),1,rtol=0,atol=1e-10):
        raise ValueError('Mixture must be a finite probability vector')
    return q


def strata_indices(batch,y):
    return [np.flatnonzero((batch==b)&(y==c)) for b,c in sorted(set(zip(batch.tolist(),y.tolist())))]


def resample_weights(rng, strata, n):
    counts=np.zeros(n,dtype=float)
    for ids in strata:
        counts[ids]=rng.multinomial(len(ids),np.full(len(ids),1/len(ids)))
    return counts/n


def interval(values, level=.95):
    values=np.asarray(values)
    finite=values[np.isfinite(values)]
    if not len(finite):return {'lower':None,'upper':None,'valid_replicates':0,'failed_replicates':len(values)}
    limits=np.quantile(finite,[(1-level)/2,1-(1-level)/2])
    return {'lower':float(limits[0]),'upper':float(limits[1]),'valid_replicates':len(finite),'failed_replicates':int(len(values)-len(finite))}


def bootstrap_calibration(names,cal_rows,cal,test_rows,test):
    cfg=config(); rng=np.random.default_rng(cfg['seed_bootstrap']); nrep=cfg['bootstrap_replicates']
    cs=strata_indices(cal_rows['batch'],cal_rows['y']); ts=strata_indices(test_rows['batch'],test_rows['y'])
    targets=cfg['targets']; families=['crossing','weight_target','weight_cap','direct_target','direct_cap','cmi','order']
    values={f'{f}_B{b}':{metric:np.full(nrep,np.nan) for metric in ('correctness','usage','reward')} for b in targets for f in families}
    original=select_policies(names,cal['usage'].mean(axis=1),cal['reward'].mean(axis=1))
    for rep in range(nrep):
        cweights=resample_weights(rng,cs,len(cal_rows['y']));tweights=resample_weights(rng,ts,len(test_rows['y']))
        usage=cal['usage']@cweights;reward=cal['reward']@cweights
        chosen=select_policies(names,usage,reward)
        means={key:test[key]@tweights for key in ('correctness','usage','reward')}
        for key in values:
            q=mixture_vector(chosen[key],names)
            if q is None:continue
            for metric in means:values[key][metric][rep]=q@means[metric]
        if (rep+1)%200==0:print(f'{now()} bootstrap {rep+1}/{nrep}',flush=True)
    np.savez_compressed(OUT/'bootstrap.npz',**{f'{key}__{metric}':v for key,d in values.items() for metric,v in d.items()})
    report={}
    for b in targets:
        key=f'crossing_B{b}'; error=values[key]['usage']-b
        entry={'usage_error_interval':interval(error,1-.05/len(targets)),'comparisons':{}}
        ci=entry['usage_error_interval']
        entry['usage_within_margin']=bool(original[key]['weights'] is not None and ci['failed_replicates']==0 and ci['lower'] is not None and ci['lower']>=-cfg['usage_margin'] and ci['upper']<=cfg['usage_margin'])
        for other in ('direct_target','cmi','weight_target','direct_cap','weight_cap','order'):
            reference=f'{other}_B{b}'
            entry['comparisons'][other]={metric:interval(values[key][metric]-values[reference][metric]) for metric in ('correctness','usage','reward')}
        report[str(b)]=entry
    return report


def main():
    if (OUT/'analysis.json').exists():raise RuntimeError('Analysis already exists. Preserve its artifacts before a documented rerun.')
    started=now();tick=time.perf_counter();cfg=config()
    names,cr,cal=load_partition('calibration');en,er,evaluation=load_partition('evaluation')
    if en!=names:raise RuntimeError('Candidate order mismatch')
    selection=json.loads((OUT/'selection.json').read_text())
    if selection['calibration_archive_sha256']!=sha(OUT/'calibration/complete.json'):raise RuntimeError('Selection archive mismatch')
    selected=selection['selected'];summaries=[];perclass=[]
    masks={'calibration':np.ones(len(cr['y']),dtype=bool),'test':er['split']=='test'}
    for b in cfg['shift_batches']:
        masks[f'batch{b}']=(er['batch']==b)&(er['split']=='shift')
        if np.any((er['batch']==b)&(er['split']=='shift_overlap')):masks[f'batch{b}_inclusive']=(er['batch']==b)
    realization={};mix_rng=np.random.default_rng(cfg['seed_mixture'])
    for group,mask in masks.items():
        data=cal if group=='calibration' else evaluation;rows=cr if group=='calibration' else er
        for name,chosen in selected.items():
            q=mixture_vector(chosen,names)
            record={'partition':group,'method':name,'budget':chosen['budget'],'n_cases':int(mask.sum()),'feasible_on_calibration':q is not None,
                    'data_available':bool(np.any(mask))}
            if q is None or not np.any(mask):
                summaries.append(record);continue
            vectors={key:q@data[key][:,mask] for key in data}
            for key,v in vectors.items():record[key]=float(np.mean(v))
            record['usage_error']=None if chosen['budget'] is None else record['usage']-chosen['budget']
            label=rows['y'][mask]
            record['balanced_accuracy']=float(np.mean([vectors['correctness'][label==c].mean() for c in np.unique(label)]))
            for c in np.unique(label):
                cm=label==c
                perclass.append({'partition':group,'method':name,'class':int(c),'n_cases':int(cm.sum()),
                    'accuracy':float(vectors['correctness'][cm].mean()),'usage':float(vectors['usage'][cm].mean())})
            summaries.append(record)
            components=mix_rng.choice(len(names),size=int(mask.sum()),p=q)
            ids=np.flatnonzero(mask)
            for key in ('correctness','usage','reward'):
                realization[f'{group}__{name}__{key}']=data[key][components,ids]
            realization[f'{group}__{name}__component']=components
    np.savez_compressed(OUT/'seeded_mixture_realizations.npz',**realization)
    tm=er['split']=='test'
    test_rows={key:er[key][tm] for key in ('batch','y')}
    test={key:value[:,tm] for key,value in evaluation.items()}
    bootstrap=bootstrap_calibration(names,cr,cal,test_rows,test)
    # Later-period intervals retain the original selection; no per-batch refitting.
    shift_intervals={}; rng=np.random.default_rng(cfg['seed_bootstrap']+1)
    for b in cfg['shift_batches']:
        mask=masks[f'batch{b}']; strata=strata_indices(er['batch'][mask],er['y'][mask]);n=int(mask.sum())
        if n==0:
            shift_intervals[str(b)]={'available':False,'reason':'No later cases remain after exact-overlap exclusion'}
            continue
        candidate={key:evaluation[key][:,mask] for key in ('correctness','usage','reward')}
        chosen={name:mixture_vector(sel,names) for name,sel in selected.items()}
        sample={name:{key:np.full(cfg['bootstrap_replicates'],np.nan) for key in candidate} for name in selected}
        for rep in range(cfg['bootstrap_replicates']):
            res=resample_weights(rng,strata,n)
            means={key:value@res for key,value in candidate.items()}
            for name,q in chosen.items():
                if q is None:continue
                for key in means:sample[name][key][rep]=q@means[key]
        shift_intervals[str(b)]={}
        for target in cfg['targets']:
            key=f'crossing_B{target}'
            shift_intervals[str(b)][str(target)]={'usage_error':interval(sample[key]['usage']-target),
                'accuracy_gap_direct':interval(sample[key]['correctness']-sample[f'direct_target_B{target}']['correctness']),
                'accuracy_gap_cmi':interval(sample[key]['correctness']-sample[f'cmi_B{target}']['correctness'])}
        np.savez_compressed(OUT/f'bootstrap_batch{b}.npz',**{f'{name}__{key}':v for name,d in sample.items() for key,v in d.items()})
    # Equal-batch means are descriptive, not additional independent test cases.
    for name,sel in selected.items():
        records=[r for r in summaries if r['method']==name and r['partition'] in [f'batch{b}' for b in cfg['shift_batches']]]
        if len(records)!=len(cfg['shift_batches']) or any('correctness' not in r for r in records):continue
        mean={'partition':'shift_equal_batch','method':name,'budget':sel['budget'],'n_cases':sum(r['n_cases'] for r in records),'feasible_on_calibration':True,'data_available':True}
        for key in ('correctness','usage','reward','log_loss','brier','balanced_accuracy'):
            mean[key]=float(np.mean([r[key] for r in records]))
        mean['usage_error']=None if sel['budget'] is None else mean['usage']-sel['budget'];summaries.append(mean)
    fields=['partition','method','budget','n_cases','feasible_on_calibration','data_available','correctness','usage','usage_error','reward','balanced_accuracy','log_loss','brier']
    with (ROOT/'results/results_real_sensor_summary.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(summaries)
    with (OUT/'per_class.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(perclass[0]));writer.writeheader();writer.writerows(perclass)
    wi=[i for i,name in enumerate(names) if name.startswith('w')]
    usages=cal['usage'][wi].mean(axis=1)
    save_json(OUT/'analysis.json',{'started':started,'finished':now(),'seconds':time.perf_counter()-tick,'protocol_sha256':cfg['protocol_sha256'],
        'selection_sha256':sha(OUT/'selection.json'),'provenance':stamp(),'bootstrap':bootstrap,'shift_intervals':shift_intervals,
        'calibration_weight_usage':usages.tolist(),'calibration_descending_grid_steps':int(np.sum(np.diff(usages)<0)),
        'inference_scope':'Case bootstrap conditional on one fitted model and exchangeability within batch/class strata. No retraining, trial-dependence or between-batch uncertainty.'})
    print(json.dumps(bootstrap,indent=2),flush=True)


if __name__=='__main__':main()
