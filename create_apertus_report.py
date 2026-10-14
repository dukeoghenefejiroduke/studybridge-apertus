from pathlib import Path
from xml.sax.saxutils import escape
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from pypdf import PdfReader

src = Path("track_2b/technical_report.md")
out = Path("track_2b/StudyBridge_Report.pdf")

if not src.exists():
    raise SystemExit("Technical report not found.")

s = getSampleStyleSheet()
s.add(ParagraphStyle(name="T", parent=s["Title"], fontSize=16, leading=20, spaceAfter=8))
s.add(ParagraphStyle(name="H", parent=s["Heading1"], fontSize=11, leading=13, spaceBefore=6, spaceAfter=3))
s.add(ParagraphStyle(name="S", parent=s["Heading2"], fontSize=9, leading=11, spaceBefore=4, spaceAfter=2))
s.add(ParagraphStyle(name="B", parent=s["BodyText"], fontSize=7.5, leading=9, spaceAfter=3))

def clean(t):
    t = t.replace("—", "-").replace("–", "-").replace("’", "'")
    t = escape(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"`(.+?)`", r"<font name='Courier'>\1</font>", t)
    return t

items = []
for raw in src.read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line:
        items.append(Spacer(1, 2))
    elif line.startswith("# "):
        items.append(Paragraph(clean(line[2:]), s["T"]))
    elif line.startswith("## "):
        items.append(Paragraph(clean(line[3:]), s["H"]))
    elif line.startswith("### "):
        items.append(Paragraph(clean(line[4:]), s["S"]))
    elif line.startswith("- "):
        items.append(Paragraph("&#8226; " + clean(line[2:]), s["B"]))
    else:
        line = re.sub(r"^\d+\.\s*", "&#8226; ", line)
        items.append(Paragraph(clean(line), s["B"]))

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.drawCentredString(A4[0] / 2, 8*mm, "StudyBridge AI | Page %s" % doc.page)
    canvas.restoreState()

doc = SimpleDocTemplate(
    str(out), pagesize=A4, rightMargin=15*mm,
    leftMargin=15*mm, topMargin=12*mm, bottomMargin=14*mm
)
doc.build(items, onFirstPage=footer, onLaterPages=footer)

pages = len(PdfReader(str(out)).pages)
print("PDF:", out.resolve())
print("Pages:", pages)
print("Size: %.1f KB" % (out.stat().st_size / 1024))
print("Page limit:", "PASS" if pages <= 6 else "EXCEEDS SIX PAGES")
