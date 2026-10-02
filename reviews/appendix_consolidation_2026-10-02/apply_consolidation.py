"""Apply audited, non-overlapping appendix edits to the frozen twin masters.

One-time historical assembler. Refuses to overwrite later manuscript edits.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
LEGACY = ROOT / 'paper/legacy/2026-10-02_pre_appendix_consolidation'
GROUPS = ('early', 'late', 'theory', 'checklist')

def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()

def assemble(write=False):
    report = {}
    outputs = {}
    previous_path = HERE / 'application_manifest.json'
    previous = json.loads(previous_path.read_text()) if previous_path.exists() else {}
    for filename in ('full_paper_jair.tex', 'full_paper.tex'):
        baseline = (LEGACY / filename).read_text()
        current = (ROOT / 'paper' / filename).read_text()
        allowed = {sha(baseline), previous.get(filename, {}).get('assembled_sha256')}
        assert sha(current) in allowed, 'Refusing to overwrite later source edits: ' + filename
        appendix_start = baseline.index('\\appendix')
        spans = []
        changes = []
        for group in GROUPS:
            if group == 'checklist' and filename == 'full_paper.tex':
                continue
            for item in json.loads((HERE / (group + '_proposals.json')).read_text()):
                suffix = '_lncs' if filename == 'full_paper.tex' else ''
                old = item.get('old' + suffix, item['old'])
                new = item.get('new' + suffix, item['new'])
                assert old and baseline.count(old) == 1, (filename, item['id'], 'guard count', baseline.count(old))
                start = baseline.index(old)
                end = start + len(old)
                assert start > appendix_start, (filename, item['id'], 'outside appendix')
                assert not any(start < hi and lo < end for lo, hi, *_ in spans), (filename, item['id'], 'overlapping edit')
                spans.append((start, end, old, new, item['id']))
                changes.append({'id':item['id'], 'old_sha256':sha(old), 'new_sha256':sha(new),
                                'source_word_reduction':len(old.split())-len(new.split()),
                                'removed_labels':sorted(set(re.findall(r'\\label\{([^}]+)\}',old))-set(re.findall(r'\\label\{([^}]+)\}',new)))})
        source = baseline
        for start, end, old, new, item_id in sorted(spans, reverse=True):
            assert source[start:end] == old, item_id
            source = source[:start] + new + source[end:]
        assert source.split('\\appendix',1)[0] == baseline.split('\\appendix',1)[0]
        for env in set(re.findall(r'\\begin\{([^}]+)\}',source)):
            assert source.count('\\begin{'+env+'}') == source.count('\\end{'+env+'}'), (filename,env)
        report[filename] = {'baseline_sha256':sha(baseline), 'assembled_sha256':sha(source),
                            'edit_count':len(changes), 'source_word_reduction':len(baseline.split())-len(source.split()),
                            'changes':changes}
        outputs[filename] = source
    if write:
        if previous and not (HERE / 'initial_application_manifest.json').exists():
            (HERE / 'initial_application_manifest.json').write_text(json.dumps(previous,indent=2)+'\n')
        for filename, source in outputs.items():
            (ROOT / 'paper' / filename).write_text(source)
        (HERE / 'application_manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({name:{k:v for k,v in obj.items() if k!='changes'} for name,obj in report.items()},indent=2))

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    assemble(parser.parse_args().write)
