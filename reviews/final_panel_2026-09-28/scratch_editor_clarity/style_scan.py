import re
src=open('/Users/pat/code/rho_aif/paper/full_paper_jair.tex').read().split('\n')
start=next(i for i,l in enumerate(src) if '\\begin{document}' in l)
def strip(l):
    l=re.sub(r'(?<!\\)%.*','',l)
    l=re.sub(r'\$[^$]*\$','',l)
    l=re.sub(r'\\\(.*?\\\)','',l)
    return l
inmath=False
for i,l in enumerate(src[start:],start=start+1):
    if re.search(r'\\begin\{(equation|align|gather|multline)\*?\}',l): inmath=True
    s=strip(l)
    if not inmath:
        if ';' in s: print('SEMI',i, s[max(0,s.find(';')-80):s.find(';')+40])
        for m in re.finditer(r'\\(emph|textit|textbf)\{([^}]*)\}',s):
            print('EMPH',i,m.group(1),m.group(2)[:60])
        for m in re.finditer(r'\bexact(ly)?\b[^.]{0,60}(SARSOP|CPOMDP|constrained)',s):
            print('EXACT',i,m.group(0)[:120])
        for m in re.finditer(r'(track(s|ing)? (guarantee|the budget)|dissolv|validat)',s):
            print('VOCAB',i,s[max(0,m.start()-60):m.end()+40])
        for m in re.finditer(r'Lagrange multiplier',s):
            print('LAGR',i,s[max(0,m.start()-120):m.end()+60])
    if re.search(r'\\end\{(equation|align|gather|multline)\*?\}',l): inmath=False
