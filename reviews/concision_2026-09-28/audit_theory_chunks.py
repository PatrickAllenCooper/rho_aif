"""Mechanical relocation audit for the proposed theory chunks (no writes)."""
from pathlib import Path
import collections
import re
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
base = subprocess.check_output(['git', 'show', '2d3bac4:paper/full_paper_jair.tex'], cwd=root, text=True)
old = base[base.index(r'\section{Methodology}'):base.index(r'\section{Experiments}')]
suffix = '_restored' if '--restored' in sys.argv else ''
main = (Path(__file__).parent/f'theory_main{suffix}.tex').read_text()
appendix = (Path(__file__).parent/f'theory_appendix{suffix}.tex').read_text()
new = main + appendix
labels = lambda s: re.findall(r'\\label\{([^}]+)\}', s)
cites = lambda s: {key.strip() for group in re.findall(r'\\cite\w*\{([^}]+)\}', s) for key in group.split(',')}
missing = set(labels(old)) - set(labels(new))
duplicates = [k for k,v in collections.Counter(labels(new)).items() if v>1]
missing_cites = cites(old)-cites(new)
unknown_refs = set(re.findall(r'\\(?:eqref|ref)\{([^}]+)\}',new))-set(labels(base+new))
assert not (missing or duplicates or missing_cites or unknown_refs), (missing, duplicates, missing_cites, unknown_refs)

def environment(s, kind, label):
    point = s.index('\\label{'+label+'}')
    start = s.rfind('\\begin{'+kind+'}',0,point)
    end = s.index('\\end{'+kind+'}',point)+len('\\end{'+kind+'}')
    return s[start:end]

statements = [('proposition','prop:equivalence'),('proposition','prop:nearopt'),
              ('definition','def:factored'),('proposition','prop:factored'),
              ('definition','def:pi3'),('proposition','prop:pi1'),
              ('proposition','prop:pi2'),('corollary','cor:pi4'),
              ('proposition','prop:pi5')]
for kind,label in statements:
    previous=environment(old,kind,label)
    revised=environment(main,kind,label)
    revised=revised.replace('proved separately in Appendix~\\ref{app:theory_thresholds}.','proved separately below.')
    revised=revised.replace('as Appendix~\\ref{app:theory_controller} proves','as the proof below shows')
    assert previous==revised,label
print(f'PASS: {len(labels(old))} original labels preserved exactly once, {len(cites(old))} citation keys retained, no unresolved introduced references.')
print(f'PASS: all {len(statements)} formal statements byte-identical apart from two proof-location pointers.')
print(f'Source words: original {len(old.split())}, main {len(main.split())}, appendix {len(appendix.split())}.')
