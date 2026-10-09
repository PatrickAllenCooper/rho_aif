"""Export the exact spoken content as a readable two-page rehearsal script."""
import json
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak

HERE = Path(__file__).resolve().parent
data = json.loads((HERE / 'content.json').read_text())
out = HERE / 'output'
out.mkdir(exist_ok=True)
font_dir = Path('/System/Library/Fonts/Supplemental')
pdfmetrics.registerFont(TTFont('Arial', str(font_dir / 'Arial.ttf')))
pdfmetrics.registerFont(TTFont('Arial-Bold', str(font_dir / 'Arial Bold.ttf')))
pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Arial-Bold')
navy = colors.HexColor('#111111')
teal = colors.HexColor('#111111')
styles = {
    'title': ParagraphStyle('title', fontName='Arial-Bold', fontSize=19,
                            leading=24, textColor=navy, spaceAfter=10),
    'meta': ParagraphStyle('meta', fontName='Arial', fontSize=10.5,
                           leading=15, textColor=colors.HexColor('#575757'), spaceAfter=20),
    'heading': ParagraphStyle('heading', fontName='Arial-Bold', fontSize=14,
                              leading=20, textColor=teal, spaceAfter=12),
    'body': ParagraphStyle('body', fontName='Arial', fontSize=13.5,
                           leading=20, textColor=navy, spaceAfter=11, alignment=TA_LEFT),
}
titles = data['titles']
assert len(data['scripts']) == 4
assert sum(len(s.split()) for s in data['scripts']) == 331
story = []
markdown = ['# IWAI 2026 spotlight script', '',
            'Four slides. 331 spoken words. Rehearsal target 2:54, with six seconds of buffer.', '',
            'The timing is a rehearsal guide, not a measured speaking duration. Read the spoken paragraphs only. Pause briefly when changing slides.', '']
for i, (title, script, timing) in enumerate(zip(titles, data['scripts'], data['times'])):
    if i in (0, 2):
        if i == 2:
            story.append(PageBreak())
        story.append(Paragraph('IWAI 2026 - three-minute script', styles['title']))
        story.append(Paragraph('Patrick Cooper | Four slides | 331 spoken words | Target finish 2:54'.replace(' | ', ' / '), styles['meta']))
    heading = f'Slide {i+1}. {title}'
    time = timing.replace('–', '-')
    story.append(Paragraph(escape(heading) + '<br/>' + time, styles['heading']))
    for para in script.split('\n\n'):
        story.append(Paragraph(escape(para), styles['body']))
    if i < 3:
        story.append(Spacer(1, 14))
    markdown += [f'## {heading} ({time})', '', script, '']

def footer(canvas, doc):
    canvas.setFont('Arial', 9)
    canvas.setFillColor(colors.HexColor('#575757'))
    canvas.drawString(54, 31, 'Rehearse aloud once and adjust to your own speaking pace.')
    canvas.drawRightString(letter[0]-54, 31, str(doc.page))

doc = SimpleDocTemplate(str(out / 'iwai2026_spotlight_script_2026-10-09.pdf'),
                        pagesize=letter, rightMargin=54, leftMargin=54,
                        topMargin=43, bottomMargin=50,
                        title='IWAI 2026 - three-minute spotlight script',
                        author='Patrick Cooper and Alvaro Velasquez')
doc.build(story, onFirstPage=footer, onLaterPages=footer)
(out / 'iwai2026_spotlight_script_2026-10-09.md').write_text('\n'.join(markdown))
print(out / 'iwai2026_spotlight_script_2026-10-09.pdf')
