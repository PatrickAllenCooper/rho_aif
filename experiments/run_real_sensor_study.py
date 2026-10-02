#!/usr/bin/env python3
"""Frozen UCI 224 retrospective sensor-access study. See experiments/protocols/."""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time
import urllib.request
import zipfile
from functools import lru_cache
from datetime import datetime, timezone

for _key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_key] = "1"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
from rho_aif.budget import UsageCurvePoint, crossing_bracket, lp_mixture

PROTOCOL = ROOT / "experiments/protocols/gas_sensor_2026-10-01.json"
OUT = ROOT / "results/real_sensor_2026-10-01"
RAW = ROOT / "data/raw/gas_sensor_224.zip"
PREPARED = ROOT / "data/processed/gas_sensor_224.npz"
URL = "https://archive.ics.uci.edu/static/public/224/gas+sensor+array+drift+dataset.zip"


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


@lru_cache(maxsize=1)
def config():
    frozen = subprocess.check_output(["git", "show", "fb3a9de:experiments/protocols/gas_sensor_2026-10-01.json"], cwd=ROOT)
    if PROTOCOL.read_bytes() != frozen:
        raise RuntimeError("Machine-readable protocol differs from predeclaration commit fb3a9de")
    cfg = json.loads(PROTOCOL.read_text())
    if sha(PROTOCOL.with_suffix(".md")) != cfg["protocol_sha256"]:
        raise RuntimeError("Frozen protocol hash mismatch")
    return cfg


def stamp():
    import scipy, sklearn
    return {"utc": now(), "git_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "python": sys.version, "numpy": np.__version__, "scipy": scipy.__version__, "sklearn": sklearn.__version__,
            "platform": platform.platform(), "machine": platform.machine(), "cpu_count": os.cpu_count(),
            "source_sha256": {p:sha(ROOT/p) for p in ("rho_aif/real_sensor.py", "rho_aif/budget.py", "experiments/run_real_sensor_study.py", "experiments/analyze_real_sensor_study.py")},
            "thread_limits": {k: os.environ[k] for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")}}


def parse_archive(path):
    """Read sparse-format source lines without changing their sensor ordering."""
    xs, ys, batches, ids, files = [], [], [], [], {}
    with zipfile.ZipFile(path) as archive:
        for batch in range(1, 11):
            names = [n for n in archive.namelist() if Path(n).name == f"batch{batch}.dat"]
            if len(names) != 1:
                raise ValueError(f"Expected one batch{batch}.dat, got {names}")
            raw = archive.read(names[0])
            files[names[0]] = hashlib.sha256(raw).hexdigest()
            for line_number, line in enumerate(raw.decode().splitlines(), 1):
                if not line.strip():
                    continue
                fields = line.split()
                x = np.zeros(128, dtype=float)
                seen = set()
                for token in fields[1:]:
                    index, value = token.split(":")
                    index = int(index) - 1
                    if index in seen or not 0 <= index < 128:
                        raise ValueError("Repeated or out-of-range feature index")
                    seen.add(index)
                    x[index] = float(value)
                if len(seen) != 128 or not np.isfinite(x).all():
                    raise ValueError("Source has missing/nonfinite descriptors")
                xs.append(x); ys.append(int(fields[0])); batches.append(batch)
                ids.append(f"batch{batch}:{line_number}")
        readmes = {n: archive.read(n).decode(errors="replace") for n in archive.namelist()
                   if not n.endswith("/") and ("readme" in n.lower() or n.lower().endswith(".txt"))}
    return np.asarray(xs), np.asarray(ys), np.asarray(batches), np.asarray(ids), files, readmes


def split_rows(X, y, batch, seed):
    """Group exact descriptors first, then stratify groups by first-row origin."""
    hashes = np.array([hashlib.sha256(np.asarray(row, dtype="<f8").tobytes()).hexdigest() for row in X])
    groups = {}
    for index in np.flatnonzero(batch <= 6):
        groups.setdefault(hashes[index], []).append(int(index))
    strata = {}
    for group in groups.values():
        first = group[0]
        strata.setdefault((int(batch[first]), int(y[first])), []).append(group)
    split = np.full(len(X), "shift", dtype="U16")
    rng = np.random.default_rng(seed)
    for key in sorted(strata):
        members = strata[key]
        order = rng.permutation(len(members))
        n_train, n_cal = int(.6 * len(members)), int(.2 * len(members))
        for j, group_index in enumerate(order):
            split[members[group_index]] = "train" if j < n_train else ("calibration" if j < n_train + n_cal else "test")
    overlap = (batch >= 7) & np.isin(hashes, list(groups))
    split[overlap] = "shift_overlap"
    integrity = {"early_duplicate_groups": sum(len(g) > 1 for g in groups.values()),
                 "early_duplicate_extra_rows": sum(len(g)-1 for g in groups.values()),
                 "conflicting_label_groups": sum(len(set(y[g])) > 1 for g in groups.values()),
                 "later_overlap_rows": int(overlap.sum()),
                 "counts": {key: int(np.sum(split == key)) for key in np.unique(split)}}
    return split, hashes, integrity


def prepare():
    from rho_aif.real_sensor import fit_sensor_model
    cfg = config()
    if (OUT / "model.json").exists() and not PREPARED.exists():
        reconstruct()
        return
    if (OUT / "model.json").exists() or PREPARED.exists():
        raise RuntimeError("Prepared study exists; use the archived inputs rather than silently refitting")
    started = now(); tick = time.perf_counter()
    RAW.parent.mkdir(parents=True, exist_ok=True)
    if not RAW.exists():
        with urllib.request.urlopen(URL, timeout=120) as response:
            RAW.write_bytes(response.read())
    downloaded = now()
    X, y, batch, ids, files, readmes = parse_archive(RAW)
    if X.shape != (13910, 128) or set(y) != set(range(1, 7)):
        raise ValueError("Dataset does not match the primary record")
    split, hashes, integrity = split_rows(X, y, batch, cfg["seed_split"])
    OUT.mkdir(parents=True, exist_ok=True)
    train = split == "train"
    fit_started = now(); fit_tick = time.perf_counter()
    model = fit_sensor_model(X[train], y[train], row_ids=ids[train], seed=cfg["seed_split"])
    fit_seconds = time.perf_counter() - fit_tick
    Z = model.encode(X)
    PREPARED.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(PREPARED, Z=Z, y=y, batch=batch, row_id=ids, split=split, descriptor_sha256=hashes)
    save_json(OUT / "model.json", model.to_dict())
    # Split identities and labels are transparent, but never inputs to policy selection at test time.
    import csv
    with (OUT / "split_manifest.csv").open("w") as fh:
        writer = csv.writer(fh); writer.writerow(["row_id", "batch", "class", "partition", "descriptor_sha256"])
        writer.writerows(zip(ids, batch, y, split, hashes))
    save_json(OUT / "dataset_manifest.json", {"source_url": URL, "retrieved_utc": downloaded, "zip_sha256": sha(RAW),
              "source_files": files, "readmes": readmes, "integrity": integrity, "protocol_sha256": cfg["protocol_sha256"],
              "prepared_sha256": sha(PREPARED), "split_dtype":split.dtype.str,
              "model_sha256": sha(OUT / "model.json"), "provenance": stamp(),
              "started_utc": started, "fit_started_utc": fit_started, "finished_utc": now(),
              "fit_seconds": fit_seconds, "total_seconds": time.perf_counter()-tick})
    print(json.dumps({"integrity": integrity, "fit_seconds": fit_seconds, "zip_sha256": sha(RAW)}), flush=True)


def reconstruct():
    """Restore encoded inputs from the archived split/model, without refitting."""
    import csv
    from rho_aif.real_sensor import SensorModel
    manifest=json.loads((OUT/'dataset_manifest.json').read_text())
    RAW.parent.mkdir(parents=True,exist_ok=True)
    if not RAW.exists():
        with urllib.request.urlopen(manifest['source_url'],timeout=120) as response:RAW.write_bytes(response.read())
    if sha(RAW)!=manifest['zip_sha256']:raise RuntimeError('Downloaded source differs from the archived dataset')
    X,y,batch,ids,files,_=parse_archive(RAW)
    if files!=manifest['source_files']:raise RuntimeError('Source file hashes differ')
    records=list(csv.DictReader((OUT/'split_manifest.csv').open()))
    if [r['row_id'] for r in records]!=ids.tolist():raise RuntimeError('Split row identities differ')
    if not np.array_equal(y,[int(r['class']) for r in records]):raise RuntimeError('Split class identities differ')
    if sha(OUT/'model.json')!=manifest['model_sha256']:raise RuntimeError('Archived model differs')
    model=SensorModel.from_dict(json.loads((OUT/'model.json').read_text()))
    split=np.asarray([r['partition'] for r in records],dtype=manifest['split_dtype'])
    hashes=np.asarray([r['descriptor_sha256'] for r in records])
    actual=np.array([hashlib.sha256(np.asarray(row,dtype='<f8').tobytes()).hexdigest() for row in X])
    if not np.array_equal(actual,hashes):raise RuntimeError('Descriptor identities differ')
    PREPARED.parent.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(PREPARED,Z=model.encode(X),y=y,batch=batch,row_id=ids,split=split,descriptor_sha256=hashes)
    if sha(PREPARED)!=manifest['prepared_sha256']:raise RuntimeError('Reconstructed encoding differs from the archived hash')
    print('Reconstructed frozen sensor records with the archived SHA256.',flush=True)


def policy_grid():
    from rho_aif.real_sensor import SensorPolicy
    cfg = config()
    policies = [SensorPolicy(name=f"w{i:02d}", kind="weight", weight=w) for i, w in enumerate(cfg["weights"])]
    policies += [SensorPolicy(name=f"d{i:02d}", kind="direct", penalty=p) for i, p in enumerate(cfg["penalties"])]
    for b in cfg["targets"]:
        policies += [SensorPolicy(name=f"cmi{b}", kind="fixed_cmi", count=b), SensorPolicy(name=f"order{b}", kind="fixed_order", count=b)]
    policies += [SensorPolicy(name="zero", kind="zero"), SensorPolicy(name="all", kind="all")]
    return policies


def load_prepared():
    from rho_aif.real_sensor import SensorModel
    manifest = json.loads((OUT / "dataset_manifest.json").read_text())
    if sha(PREPARED) != manifest["prepared_sha256"] or sha(OUT / "model.json") != manifest["model_sha256"]:
        raise RuntimeError("Prepared data or model changed after fitting")
    return SensorModel.from_dict(json.loads((OUT / "model.json").read_text())), np.load(PREPARED)


def crossing_weights(usages, weights, budget):
    """Return no policy when the selected crossing does not attain the target."""
    curve = [UsageCurvePoint(float(w), float(u), 0., 1, [float(u)]) for w, u in zip(weights, usages)]
    bracket = crossing_bracket(curve, budget)
    q = np.zeros(len(weights))
    # H1 predeclares a straddling crossing, including failure at an unbracketed minimum.
    # A directly attainable plateau remains represented by the separate equality LP.
    if not bracket.bracketed:
        return None, dataclasses.asdict(bracket)
    lo = list(weights).index(bracket.w_lo); hi = list(weights).index(bracket.w_hi)
    q[hi] = (budget - usages[lo]) / (usages[hi] - usages[lo]); q[lo] = 1. - q[hi]
    return q, dataclasses.asdict(bracket)


def select_policies(names, usage, reward):
    cfg = config(); selected = {}
    wi = [i for i,n in enumerate(names) if n.startswith("w")]
    di = [i for i,n in enumerate(names) if n.startswith("d")]
    for b in cfg["targets"]:
        q, bracket = crossing_weights(usage[wi], cfg["weights"], b)
        selected[f"crossing_B{b}"] = {"budget": b, "family": "crossing", "bracket": bracket,
          "weights": None if q is None else {names[i]: float(p) for i,p in zip(wi,q) if p > 0}}
        for family, indexes in (("weight",wi),("direct",di)):
            for equality in (True,False):
                solution = lp_mixture(usage[indexes], reward[indexes], b, equality=equality)
                key = f"{family}_{'target' if equality else 'cap'}_B{b}"
                selected[key] = {"budget": b, "family": key.split("_B")[0], "weights": None if solution is None else
                    {names[i]: float(p) for i,p in zip(indexes,solution["weights"]) if p > 0}}
        for prefix in ("cmi", "order"):
            selected[f"{prefix}_B{b}"] = {"budget": b, "family": prefix, "weights": {f"{prefix}{b}":1.}}
    for name in ("zero", "all", "w00", "w"+str(cfg["weights"].index(1)).zfill(2), "w"+str(cfg["weights"].index(float(np.log(2)))).zfill(2)):
        selected[f"anchor_{name}"] = {"budget": None, "family":"anchor", "weights":{name:1.}}
    return selected


def save_replay(path, result):
    # Explicit schema, aligned with row_id.npy and the candidate JSON registry.
    np.savez_compressed(path, correctness=result.correctness, usage=result.usage, reward=result.reward,
                        predictions=result.predictions, posteriors=result.posteriors,
                        order=result.acquisition_order, observations=result.observations,
                        candidate_evaluations=result.candidate_evaluations)


def run_partition(partition):
    from rho_aif.real_sensor import evaluate_policies
    model, data = load_prepared(); cfg=config()
    output = OUT / partition
    if (output / "complete.json").exists():
        raise RuntimeError(f"{partition} already completed; refusing duplicate evaluation")
    if partition == "calibration":
        mask = data["split"] == "calibration"
    else:
        if not (OUT / "selection.json").exists():
            raise RuntimeError("Calibration selections must be frozen first")
        selection=json.loads((OUT / "selection.json").read_text())
        if selection['protocol_sha256'] != cfg['protocol_sha256'] or selection['calibration_archive_sha256'] != sha(OUT / 'calibration/complete.json'):
            raise RuntimeError("Selection is not bound to the frozen protocol and calibration archive")
        mask = np.isin(data["split"], ["test", "shift", "shift_overlap"])
    output.mkdir(parents=True,exist_ok=True)
    policies = policy_grid()
    identity={'protocol_json_sha256':sha(PROTOCOL),'model_sha256':sha(OUT/'model.json'),'prepared_sha256':sha(PREPARED),
        'runner_sha256':sha(__file__),'module_sha256':sha(ROOT/'rho_aif/real_sensor.py'),'budget_module_sha256':sha(ROOT/'rho_aif/budget.py'),
        'policy_registry':[dataclasses.asdict(p) for p in policies], 'row_ids':data['row_id'][mask].tolist(),
        'selection_sha256':None if partition=='calibration' else sha(OUT/'selection.json')}
    identity_path=output/'run_identity.json'
    if identity_path.exists():
        if json.loads(identity_path.read_text()) != identity:raise RuntimeError('Checkpoint identity changed. Preserve the old run and document a restart.')
    elif any(output.glob('*.npz')):
        raise RuntimeError('Unidentified checkpoints exist; refusing to reuse them')
    else:save_json(identity_path,identity)
    np.savez_compressed(output / "rows.npz", **{key:data[key][mask] for key in ("row_id","batch","y","split")})
    summaries=[]; started=now(); tick=time.perf_counter()
    for p in policies:
        path=output / f"{p.name}.npz"
        if path.exists():
            # A trajectory is an immutable checkpoint; validate rather than recompute it.
            with np.load(path) as old:
                if len(old["usage"]) != int(mask.sum()): raise RuntimeError("Checkpoint row mismatch")
                metrics={"usage":float(old["usage"].mean()),"accuracy":float(old["correctness"].mean()),"reward":float(old["reward"].mean())}
            elapsed=None
        else:
            t=time.perf_counter()
            result=evaluate_policies(model,data["Z"][mask],data["y"][mask],[p],row_ids=data["row_id"][mask],batches=data["batch"][mask])[p.name]
            elapsed=time.perf_counter()-t
            save_replay(path,result)
            metrics={"usage":float(result.usage.mean()),"accuracy":float(result.correctness.mean()),"reward":float(result.reward.mean())}
        summaries.append({"name":p.name,"policy":dataclasses.asdict(p),"seconds":elapsed,"archive_sha256":sha(path),**metrics})
        save_json(output / "progress.json", {"started":started,"updated":now(),"rows":int(mask.sum()),"completed":summaries})
        # No locked outcome numbers appear in progress, and selection is already frozen.
        print(f"{now()} {partition} {p.name} complete ({elapsed}s)",flush=True)
    save_json(output / "complete.json", {"started":started,"finished":now(),"seconds":time.perf_counter()-tick,"rows":int(mask.sum()),
       "rows_sha256":sha(output/'rows.npz'), "run_identity_sha256":sha(identity_path),
       "provenance":stamp(),"policies":summaries,"peak_rss_platform_units":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
    if partition == "calibration":
        names=[r["name"] for r in summaries]
        selections=select_policies(names,np.array([r["usage"] for r in summaries]),np.array([r["reward"] for r in summaries]))
        save_json(OUT / "selection.json", {"created":now(),"protocol_sha256":cfg["protocol_sha256"],"calibration_archive_sha256":sha(output / "complete.json"),"selected":selections})


def smoke():
    from rho_aif.real_sensor import evaluate_policies
    model,data=load_prepared()
    mask=np.flatnonzero(data["split"]=="train")[:128]
    policies=policy_grid()
    keep={"w00","w"+str(len(config()["weights"])-1).zfill(2),"d00","d"+str(len(config()["penalties"])-1).zfill(2),"cmi8","all"}
    tick=time.perf_counter(); measurements=[]
    for p in policies:
        if p.name not in keep: continue
        t=time.perf_counter()
        result=evaluate_policies(model,data["Z"][mask],data["y"][mask],[p])[p.name]
        elapsed=time.perf_counter()-t
        measurements.append({"policy":p.name,"rows":len(mask),"seconds":elapsed,
            "episodes_per_second":len(mask)/elapsed,"candidate_evaluations":int(result.candidate_evaluations.sum()),
            "candidate_evaluations_per_second":float(result.candidate_evaluations.sum())/elapsed})
        if time.perf_counter()-tick>120: raise RuntimeError("Smoke exceeded the predeclared 120-second limit")
    remaining=int(np.sum(data["split"]!="train"))
    estimate=max(m["seconds"] for m in measurements)/len(mask)*remaining*len(policies)
    result={"measurements":measurements,"worst_case_estimated_seconds":estimate,"candidate_count":len(policies),"nontraining_rows":remaining,
            "peak_rss_platform_units":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,"provenance":stamp()}
    save_json(OUT / "smoke.json",result); print(json.dumps(result),flush=True)
    if estimate>4*3600: raise RuntimeError("Estimated compute exceeds protocol envelope; optimize before evaluation")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage",choices=["prepare","smoke","calibrate","evaluate"])
    args=parser.parse_args()
    if args.stage=="prepare":prepare()
    elif args.stage=="smoke":smoke()
    elif args.stage=="calibrate":run_partition("calibration")
    else:run_partition("evaluation")


if __name__=="__main__":
    main()
