"""Aggregate independently inspected published PDFs; no manuscript changes."""
from pathlib import Path
import csv
import json
import statistics

HERE = Path(__file__).resolve().parent
a = json.loads((HERE / 'jair_appendix_sample_a.json').read_text())['articles']
b = json.loads((HERE / 'jair_appendix_sample_b.json').read_text())['records']
rows = []
for x in a + b:
    order = x.get('order', x.get('position'))
    pages = x.get('totalPagesOccupiedByAppendix', x.get('totalAppendixPages'))
    union = set()
    for lo, hi in x['appendixPhysicalPageIntervals']:
        assert 1 <= lo <= hi <= x['totalPhysicalPDFPages']
        union.update(range(lo, hi + 1))
    assert len(union) == pages, (order, pages, union)
    rows.append(dict(order=order, title=x['title'], article_url=x['articleURL'],
                     pdf_url=x['pdfURL'], total_pdf_pages=x['totalPhysicalPDFPages'],
                     substantive_appendix_pages=pages,
                     separate_substantive_online_appendix_pages=22 if order == 22 else 0,
                     survey_or_viewpoint=order in (19,27,28,29)))
rows.sort(key=lambda r: r['order'])
assert [r['order'] for r in rows] == list(range(1,31))

def stats(values):
    positive = [v for v in values if v > 0]
    return dict(papers=len(values), papers_with_appendices=len(positive),
                total_appendix_pages=sum(values),
                mean_all_papers=statistics.mean(values),
                median_all_papers=statistics.median(values),
                mean_papers_with_appendices=statistics.mean(positive),
                median_papers_with_appendices=statistics.median(positive),
                range_papers_with_appendices=[min(positive),max(positive)])

report = dict(measurement_date='2026-10-02',
    source='https://www.jair.org/index.php/jair/issue/view/1173',
    population='All 30 listed articles in JAIR Volume 84 (2025), excluding masthead',
    definition='Combined substantive appendix pages per paper, counting physical pages occupied at least in part. References-only, metadata-only and checklist-only pages excluded. Multiple appendix letters sharing a page counted once.',
    limitation='A census of one volume, not a journal-wide historical average or an acceptance threshold. Unlisted external supplementary files are outside the measurement; typography differs between some PDFs.',
    primary_in_article_pdf=stats([r['substantive_appendix_pages'] for r in rows]),
    excluding_three_surveys_and_one_viewpoint=stats([r['substantive_appendix_pages'] for r in rows if not r['survey_or_viewpoint']]),
    including_one_journal_linked_online_appendix_sensitivity=stats([r['substantive_appendix_pages']+r['separate_substantive_online_appendix_pages'] for r in rows]),
    online_sensitivity_note='The one separately linked Online Appendices PDF has 25 physical pages, of which 22 are substantive (3–24); cover, contents and references excluded. It uses different typography, so summed pages are an approximate sensitivity.',
    manuscript_comparison=dict(scientific_appendix_pages=42, scientific_appendix_page_span=[36,77],checklist_page_span=[78,80],total_pages=80),
    records=rows)
(HERE / 'jair_appendix_length_summary.json').write_text(json.dumps(report,indent=2)+'\n')
with (HERE / 'jair_appendix_lengths.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
print(json.dumps({k:v for k,v in report.items() if k != 'records'},indent=2))
