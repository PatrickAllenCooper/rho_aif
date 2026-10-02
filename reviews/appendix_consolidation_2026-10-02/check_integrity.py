"""Record mechanical preservation checks for the appendix-only consolidation."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
LEGACY=ROOT/'paper/legacy/2026-10-02_pre_appendix_consolidation'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((LEGACY/'manifest.json').read_text())
for name,digest in manifest['files'].items():assert sha(LEGACY/name)==digest,name
report={'archived_files_unchanged':True,'manuscripts':{}}
for filename in ('full_paper_jair.tex','full_paper.tex'):
    old=(LEGACY/filename).read_text();new=(ROOT/'paper'/filename).read_text()
    assert old.split('\\appendix',1)[0]==new.split('\\appendix',1)[0],filename
    old_fig=set(re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}',old))
    new_fig=set(re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}',new))
    removed=sorted(old_fig-new_fig)
    assert all((ROOT/p).is_file() for p in removed)
    old_inputs=set(re.findall(r'\\input\{([^}]+)\}',old))
    new_inputs=set(re.findall(r'\\input\{([^}]+)\}',new))
    assert old_inputs==new_inputs,filename
    def sensor_block(s):
        start=s.index('\\subsection{Retrospective Sensor-Acquisition Protocol}')
        return s[start:s.index('\\section{Extended Budget Evidence}',start)]
    assert sensor_block(old)==sensor_block(new),filename
    old_proofs=re.findall(r'\\begin\{proof\}.*?\\end\{proof\}',old,re.S)
    new_proofs=re.findall(r'\\begin\{proof\}.*?\\end\{proof\}',new,re.S)
    assert len(old_proofs)==len(new_proofs)==6,filename
    changed=[i+1 for i,(a,b) in enumerate(zip(old_proofs,new_proofs)) if a!=b]
    # Scale and comparative statics are followed by equivalence, then thresholds.
    assert changed==[4],changed
    report['manuscripts'][filename]={'sha256':sha(ROOT/'paper'/filename),'main_text_unchanged':True,
        'sensor_protocol_unchanged':True,'external_table_inputs_unchanged':True,
        'proofs':6,'changed_proof_ordinal':changed,'figures_before':len(old_fig),'figures_after':len(new_fig),
        'removed_figures_still_archived':removed,'inline_tables_before':old.count('\\begin{table}'),
        'inline_tables_after':new.count('\\begin{table}')}
source=(ROOT/'paper/full_paper_jair.tex').read_text()
used=set()
for group in re.findall(r'\\cite\w*\s*(?:\[[^]]*\]\s*)*\{([^}]+)\}',source):used.update(k.strip() for k in group.split(','))
keys=set(re.findall(r'@\w+\{([^,]+),',(ROOT/'paper/full_paper_jair.bib').read_text()))
assert used==keys,(keys-used,used-keys)
report['jair_bibliography']={'entries':len(keys),'cited':len(used),'missing':[],'unused':[]}
changed=subprocess.check_output(['git','diff','--name-only','c5125ab','--','results','rho_aif','experiments','tests','paper/full_paper_jair.bib'],cwd=ROOT,text=True).splitlines()
assert not changed,changed
report['empirical_data_code_tests_and_bibliography_unchanged']=True
(HERE/'integrity_checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
