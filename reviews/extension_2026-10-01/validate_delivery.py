"""Build the delivered ZIP without repository inputs and verify final artifacts."""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
ARCHIVE=ROOT/'paper/rho_aif_jair_overleaf_2026-09-28.zip'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def pdftext(path):return subprocess.check_output(['pdftotext','-layout',str(path),'-'],text=True)
report={'artifact_sha256':{str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'paper/full_paper_jair.tex',ROOT/'paper/full_paper.tex',ROOT/'paper/full_paper_jair.pdf',ROOT/'paper/full_paper.pdf',ARCHIVE]}}
for name in ('full_paper_jair','full_paper'):
    source=(ROOT/f'paper/{name}.tex').read_text()
    text=pdftext(ROOT/f'paper/{name}.pdf')
    pages=text.split('\f')
    if not pages[-1].strip():pages.pop()
    log=(ROOT/f'paper/{name}.log').read_text()
    warnings=re.findall(r'^.*(?:Overfull|Missing character|undefined|^!).*$',log,re.M)
    if warnings:raise RuntimeError(f'{name}: unresolved diagnostics {warnings}')
    report[name]={'pages':len(pages),'reference_start_pages':[i+1 for i,p in enumerate(pages) if re.search(r'^\s*References\s*$',p,re.M)],
                  'figures':source.count('\\begin{figure}'),'tables':source.count('\\begin{table}'),'critical_diagnostics':warnings}
    labels=re.findall(r'\\label\{([^}]+)\}',source)
    if len(labels)!=len(set(labels)):raise RuntimeError(f'{name}: duplicate source labels')
    body=re.sub(r'\\Description\{[^\n]*\}','',source)
    if 'robust untuned default' in body:raise RuntimeError('Stale default claim')
manifest=json.loads((ROOT/'paper/legacy/2026-10-01_pre_external_study/manifest.json').read_text())
# Keep the original manifest itself and compare each listed legacy asset.
legacy=ROOT/'paper/legacy/2026-10-01_pre_external_study'
report['legacy_manifest_sha256']=sha(legacy/'manifest.json')
for filename, expected in manifest['files'].items():
    if sha(legacy/filename)!=expected:raise RuntimeError(f'Legacy asset changed: {filename}')
report['legacy_assets_unchanged']=True
with tempfile.TemporaryDirectory(prefix='rho-overleaf-') as tmp:
    directory=Path(tmp)
    with zipfile.ZipFile(ARCHIVE) as z:
        names=z.namelist()
        if len(names)!=39:raise RuntimeError(f'Unexpected dependency count {len(names)}')
        z.extractall(directory)
    mains=list(directory.rglob('full_paper_jair.tex'))
    if len(mains)!=1:raise RuntimeError('Archive main source ambiguous')
    working=mains[0].parent
    env=os.environ.copy();env['PATH']='/Users/pat/Library/TinyTeX/bin/universal-darwin:'+env['PATH']
    result=subprocess.run(['latexmk','-pdf','-interaction=nonstopmode','-halt-on-error','full_paper_jair.tex'],cwd=working,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (HERE/'overleaf_build_stdout.txt').write_text(result.stdout)
    if result.returncode:raise RuntimeError('Extracted Overleaf build failed')
    if pdftext(working/'full_paper_jair.pdf')!=pdftext(ROOT/'paper/full_paper_jair.pdf'):
        raise RuntimeError('Extracted package PDF text differs')
    log=(working/'full_paper_jair.log').read_text()
    if re.search(r'Overfull|Missing character|undefined|^!',log,re.M):raise RuntimeError('Extracted package has critical diagnostics')
    report['overleaf']={'files':len(names),'figures':sum(n.startswith('figures/') for n in names),'tables':sum(n.startswith('tables/') for n in names),'fresh_compile':True,'identical_pdf_text':True,'pdf_sha256':sha(working/'full_paper_jair.pdf')}
(HERE/'delivery_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
