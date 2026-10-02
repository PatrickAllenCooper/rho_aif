"""Guarded one-time assembly from the frozen pre-extension masters."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
NAMES = ('full_paper_jair.tex','full_paper.tex')
baseline = ROOT/'paper/legacy/2026-10-01_pre_external_study'
sources = {f'paper/{name}':(baseline/name).read_text() for name in NAMES}
for path, source in sources.items():
    if (ROOT/path).read_text() != source:
        raise SystemExit('Live masters have changed; do not overwrite subsequent work')
applied=[]


def replace(path,old,new,identity):
    count=sources[path].count(old)
    if count!=1:raise ValueError(f'{identity} {path}: expected one old span, got {count}')
    sources[path]=sources[path].replace(old,new,1)
    applied.append({'id':identity,'path':path,'old_sha256':hashlib.sha256(old.encode()).hexdigest(),'new_sha256':hashlib.sha256(new.encode()).hexdigest()})


for p in json.loads((HERE/'appendix_concision_proposals.json').read_text())['proposals']:
    edits=p.get('edits',[p])
    for edit in edits:
        for path in edit['paths']:replace(path,edit['old'],edit['new'],p['id'])
for g in json.loads((HERE/'main_concision_proposals.json').read_text())['groups']:
    if g['recommendation']!='recommended':continue
    for target in g['targets']:
        for edit in target['replacements']:replace(target['path'],edit['old'],edit['new'],g['id'])
for path,source in sources.items():
    source=source.replace('The first threshold is negative when observation is already instrumentally worthwhile.',
                          'The first threshold is negative when observation is already strictly instrumentally worthwhile.')
    (ROOT/path).write_text(source)
(HERE/'concision_application.json').write_text(json.dumps({'applied':applied,'output_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources}},indent=2)+'\n')
print(f'Applied {len(applied)} guarded replacements across both masters.')
