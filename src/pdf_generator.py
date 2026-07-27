import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

def clean_text_for_pdf(text: str) -> str:
    """Strictly sanitizes text to pure ASCII so ReportLab never encounters encoding errors."""
    if not text:
        return ""
    
    # 1. Swap common smart quotes, apostrophes, dashes, and bullet symbols
    replacements = {
        '“': '"', '”': '"', '‘': "'", '’': "'",
        '—': '-', '–': '-', '…': '...', '•': '*',
        '\u201c': '"', '\u201d': '"', '\u2018': "'", '\u2019': "'",
        '\u2013': '-', '\u2014': '-', '\u2026': '...', '\u2022': '*'
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)

    # 2. Convert Markdown Bold (**text**) to ReportLab HTML Bold (<b>text</b>)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)

    # 3. ABSOLUTE STRICT ASCII CLEANING (Strips any hidden non-ASCII characters safely)
    text = text.encode('ascii', errors='ignore').decode('ascii')

    return text


def build_single_combined_pdf(notes_markdown: str, output_filename: str = "Inkscribe_Exam_Notes.pdf") -> str:
    """Builds a clean PDF document from formatted text."""
    pdf_path = os.path.join(os.getcwd(), output_filename)
    
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1e1b4b"),
        spaceAfter=12
    )
    
    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#b45309"),
        spaceBefore=12,
        spaceAfter=8
    )
    
    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#15803d"),
        spaceBefore=10,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=6
    )

    story = []
    
    # Process text line by line with strict ASCII filter
    raw_lines = notes_markdown.split('\n')

    for line in raw_lines:
        line_clean = clean_text_for_pdf(line.strip())
        if not line_clean:
            story.append(Spacer(1, 4))
            continue
            
        if line_clean.startswith("# "):
            clean_title = line_clean.replace("# ", "")
            story.append(Paragraph(clean_title, title_style))
            story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#a855f7"), spaceAfter=10))
        elif line_clean.startswith("## "):
            clean_h1 = line_clean.replace("## ", "")
            story.append(Paragraph(clean_h1, h1_style))
        elif line_clean.startswith("### ") or line_clean.startswith("#### "):
            clean_h2 = re.sub(r'^#+\s*', '', line_clean)
            story.append(Paragraph(clean_h2, h2_style))
        elif line_clean.startswith("---"):
            story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#cbd5e1"), spaceBefore=8, spaceAfter=8))
        else:
            story.append(Paragraph(line_clean, body_style))

    doc.build(story)
    return pdf_path
