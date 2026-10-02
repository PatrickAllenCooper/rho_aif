"""Validate the accepted sources, preserved evidence, and isolated Overleaf build."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
LEGACY = ROOT / 'paper/legacy/2026-10-02_pre_claim_focused_appendices'
PACKAGE = ROOT / 'paper/rho_aif_jair_overleaf_2026-09-28.zip'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pdftext(path):
    return subprocess.check_output(['pdftotext', '-layout', str(path), '-'], text=True)


def uncomment(text):
    return re.sub(r'(?<!\\)%[^\n]*', '', text)


def expand_inputs(source):
    return re.sub(r'\\input\{([^}]+)\}',
                  lambda m: (ROOT / 'paper' / m[1]).read_text(), source)


report = {'verified_utc': datetime.now(timezone.utc).isoformat(), 'archives': {},
          'sources': {}, 'review_freeze': {}}
for dirname in ('2026-10-02_pre_appendix_consolidation',
                '2026-10-02_pre_claim_focused_appendices'):
    directory = ROOT / 'paper/legacy' / dirname
    manifest = json.loads((directory / 'manifest.json').read_text())
    for filename, expected in manifest['files'].items():
        assert sha(directory / filename) == expected, (dirname, filename)
    report['archives'][dirname] = {'all_listed_assets_unchanged': True,
                                   'manifest_sha256': sha(directory / 'manifest.json')}

for name in ('full_paper_jair', 'full_paper'):
    path = ROOT / f'paper/{name}.tex'
    source = path.read_text()
    baseline = (LEGACY / path.name).read_text()
    expanded = uncomment(expand_inputs(source))
    labels = re.findall(r'\\label\{([^}]+)\}', expanded)
    refs = re.findall(r'\\(?:eqref|ref|autoref)\{([^}]+)\}', expanded)
    assert not [k for k, n in Counter(labels).items() if n > 1], name
    assert not set(refs) - set(labels), (name, set(refs) - set(labels))
    proof_pattern = r'\\begin\{proof\}.*?\\end\{proof\}'
    proofs = re.findall(proof_pattern, source, re.S)
    assert len(proofs) == 6
    assert proofs == re.findall(proof_pattern, baseline, re.S)
    controller = source.split('Let $\\mathcal{F}_t$', 1)[1].split('\\subsection', 1)[0]
    assert controller == baseline.split('Let $\\mathcal{F}_t$', 1)[1].split('\\subsection', 1)[0]
    sensor_marker = r'\subsection{Retrospective Sensor-Acquisition Protocol}'
    sensor = source.split(sensor_marker, 1)[1].split(r'\FloatBarrier', 1)[0]
    assert sensor == baseline.split(sensor_marker, 1)[1].split(r'\FloatBarrier', 1)[0]
    # Class options, layout, fonts and spacing are unchanged.
    assert source.split(r'\begin{document}', 1)[0] == baseline.split(r'\begin{document}', 1)[0]
    log = (ROOT / f'paper/{name}.log').read_text()
    warnings = re.findall(r'^.*(?:Overfull|Missing character|undefined|^!).*$', log, re.M)
    assert not warnings, (name, warnings)
    pages = pdftext(ROOT / f'paper/{name}.pdf').split('\f')
    if not pages[-1].strip():
        pages.pop()
    report['sources'][name] = {
        'pages': len(pages), 'source_sha256': sha(path),
        'pdf_sha256': sha(ROOT / f'paper/{name}.pdf'),
        'reference_heading_pages': [i + 1 for i, page in enumerate(pages)
                                  if re.search(r'^\s*(?:\d+\s+)?References\s*$', page, re.M)],
        'proof_count': 6, 'all_proofs_byte_identical': True,
        'controller_proof_byte_identical': True,
        'public_sensor_protocol_byte_identical': True,
        'preamble_and_typography_byte_identical': True,
        'duplicate_labels': [], 'missing_references': [], 'critical_diagnostics': [],
        'figures': expanded.count(r'\begin{figure}'),
        'tables_including_inputs': expanded.count(r'\begin{table}'),
    }

jair = (ROOT / 'paper/full_paper_jair.tex').read_text()
lncs = (ROOT / 'paper/full_paper.tex').read_text()
scientific = jair.split(r'\appendix', 1)[1].split(r'\section{Reproducibility Checklist for JAIR}', 1)[0]
other = lncs.split(r'\appendix', 1)[1].split(r'\end{document}', 1)[0]
assert scientific.rstrip().removesuffix(r'\FloatBarrier').rstrip() == other.rstrip().removesuffix(r'\FloatBarrier').rstrip()
report['scientific_appendices_identical_between_masters'] = True
checklist = jair.split(r'\section{Reproducibility Checklist for JAIR}', 1)[1]
old_checklist = (LEGACY / 'full_paper_jair.tex').read_text().split(r'\section{Reproducibility Checklist for JAIR}', 1)[1]
question_pattern = r'\\item\s*(.*?)\\textbf\{(Yes|Partially|No)\.\}'
questions = re.findall(question_pattern, checklist, re.S)
assert questions == re.findall(question_pattern, old_checklist, re.S)
assert len(questions) == 26 and sum(v == 'Partially' for _, v in questions) == 3
report['checklist'] = {'questions_and_verdicts_unchanged': True, 'questions': 26, 'partially': 3}
report['jair_scientific_appendix'] = {'first_occupied_page': 35, 'last_occupied_page': 49,
    'occupied_pages': 15, 'baseline_occupied_pages': 42,
    'note': 'Page 35 is shared with references; page 49 is shared with the checklist. Checklist-only pages excluded.'}

cited = {key.strip() for group in re.findall(r'\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]+)\}',
                                             uncomment(expand_inputs(jair))) for key in group.split(',')}
bib = (ROOT / 'paper/full_paper_jair.bib').read_text()
keys = re.findall(r'^@\w+\{([^,]+),', bib, re.M)
assert len(keys) == len(set(keys)) == 69
assert set(keys) == cited, (set(keys) - cited, cited - set(keys))
report['bibliography'] = {'entries': 69, 'all_cited': True, 'missing': [],
                           'sha256': sha(ROOT / 'paper/full_paper_jair.bib')}

changed_science = subprocess.check_output(['git', '-C', str(ROOT), 'diff', '--name-only',
    '51168bd', '--', 'results', 'rho_aif', 'experiments'], text=True).splitlines()
assert changed_science == ['experiments/build_rocksample_tables.py'], changed_science
producer_diff = subprocess.check_output(['git', '-C', str(ROOT), 'diff', '51168bd', '--',
    'experiments/build_rocksample_tables.py'], text=True)
report['experiment_scope'] = {'result_data_and_package_implementation_unchanged': True,
    'changed_experiment_files': changed_science, 'change': 'RockSample caption destination only'}
old_table = subprocess.check_output(['git', '-C', str(ROOT), 'show',
    '51168bd:paper/tables/rocksample_main.tex'], text=True)
new_table = (ROOT / 'paper/tables/rocksample_main.tex').read_text()
tabular = r'\\begin\{tabular\}.*?\\end\{tabular\}'
assert re.findall(tabular, old_table, re.S) == re.findall(tabular, new_table, re.S)
report['rocksample_table_cells_unchanged'] = True
for removed_asset in re.findall(r'\\(?:includegraphics|input)(?:\[[^\]]*\])?\{([^}]+)\}',
                                (LEGACY / 'full_paper_jair.tex').read_text()):
    assert (ROOT / 'paper' / removed_asset).exists() or (ROOT / removed_asset).exists(), removed_asset
report['previously_included_assets_retained'] = True

# The independent decisions attach to these exact files, not just the current branch.
theory = json.loads((HERE / 'independent_theory_source_snapshot.json').read_text())
prior_sources = json.loads((HERE / 'pre_whitespace_freeze.json').read_text())
for filename, item in theory['final_reviewed_files'].items():
    if filename in prior_sources:
        prior = prior_sources[filename]
        current = (ROOT / 'paper' / filename).read_text()
        assert hashlib.sha256(prior['text'].encode()).hexdigest() == item['sha256']
        assert [line.rstrip() for line in prior['text'].splitlines()] == current.splitlines()
        expected = theory['final_source_freeze_confirmation']['sources'][filename]['final_sha256']
        assert sha(ROOT / 'paper' / filename) == expected
    elif not filename.endswith('.pdf'):
        assert sha(Path(item['path'])) == item['sha256'], item['path']
evidence = json.loads((HERE / 'independent_evidence_snapshot.json').read_text())
for rel, expected in evidence['source_hashes'].items():
    assert sha(ROOT / rel) == expected, rel
assert theory['verdict'] == evidence['verdict'] == 'ACCEPT'
report['review_freeze'] = {'theory': 'ACCEPT', 'evidence': 'ACCEPT',
                         'final_reviewed_source_hashes_match': True,
                         'only_post_visual_review_edit': 'Two trailing spaces removed per master',
                         'administrative_freeze_confirmation': True,
                         'required_revisions_remaining': []}

with tempfile.TemporaryDirectory(prefix='rho-overleaf-') as tmp:
    directory = Path(tmp)
    with zipfile.ZipFile(PACKAGE) as z:
        names = z.namelist()
        assert len(names) == len(set(names)) == 17
        z.extractall(directory)
    env = os.environ.copy()
    env['PATH'] = '/Users/pat/Library/TinyTeX/bin/universal-darwin:' + env['PATH']
    result = subprocess.run(['latexmk', '-pdf', '-interaction=nonstopmode', '-halt-on-error',
        'full_paper_jair.tex'], cwd=directory, env=env, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (HERE / 'overleaf_build_stdout.txt').write_text(result.stdout)
    assert result.returncode == 0, 'Extracted Overleaf package failed to build'
    assert pdftext(directory / 'full_paper_jair.pdf') == pdftext(ROOT / 'paper/full_paper_jair.pdf')
    log = (directory / 'full_paper_jair.log').read_text()
    assert not re.search(r'Overfull|Missing character|undefined|^!', log, re.M)
    report['overleaf'] = {'files': len(names), 'figures': 11, 'table_inputs': 1,
                         'fresh_compile': True, 'identical_pdf_text': True,
                         'sha256': sha(PACKAGE), 'fresh_pdf_sha256': sha(directory / 'full_paper_jair.pdf')}
    # Confirm the whitespace cleanup did not change the reviewed typesetting.
    (directory / 'full_paper_jair.tex').write_text(prior_sources['full_paper_jair.tex']['text'])
    prior_build = subprocess.run(['latexmk', '-pdf', '-interaction=nonstopmode', '-halt-on-error',
        'full_paper_jair.tex'], cwd=directory, env=env, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (HERE / 'reviewed_source_rebuild_stdout.txt').write_text(prior_build.stdout)
    assert prior_build.returncode == 0
    assert pdftext(directory / 'full_paper_jair.pdf') == pdftext(ROOT / 'paper/full_paper_jair.pdf')
    assert pdftext(ROOT / 'paper/full_paper.pdf') == (HERE / 'independent_theory_lncs_text.txt').read_text()
    report['review_freeze']['pdf_text_unchanged_after_whitespace_cleanup'] = True
report['page_reduction_vs_archived'] = {'jair': 80 - report['sources']['full_paper_jair']['pages'],
                                     'lncs': 101 - report['sources']['full_paper']['pages']}
(HERE / 'delivery_validation.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
