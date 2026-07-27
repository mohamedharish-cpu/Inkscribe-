import os
import re
import unicodedata
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

def clean_text_for_pdf(text: str) -> str:
    """100% Failsafe ASCII Sanitizer to prevent any ReportLab encoding crash."""
    if not text:
        return ""
    
    # 1. Force replacement of all smart quotes, dashes, and ellipses
    text = re.sub(r'[\u201c\u201d\u201e\u201f\u275d\u275e]', '"', text)  # Smart Double Quotes
    text = re.sub(r'[\u2018\u2019\u201a\u201b\u275b\u275c]', "'", text)  # Smart Single Quotes
    text = re.sub(r'[\u2013\u2014\u2015]', '-', text)                  # Dashes
    text = re.sub(r'[\u2022\u2023\u2043\u204c\u204d]', '*', text)                 # Bullets
    text = text.replace('…', '...')
    
    # 2. Convert Markdown Bold (**text**) to HTML Bold (<b>text</b>)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    
    # 3. Forcibly strip ANY character outside standard ASCII range (0-127)
    normalized = unicodedata.normalize('NFKD', text)
    clean_ascii_bytes = normalized.encode('ascii', errors='ignore')
    return clean_ascii_bytes.decode('ascii')


def build_single_combined_pdf(notes_markdown: str, output_filename: str = "Inkscribe_Exam_Notes.pdf") -> str:
    """Generates a clean PDF guaranteed not to throw encoding errors."""
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
    
    # First, run total clean on entire text block
    safe_markdown = clean_text_for_pdf(notes_markdown)
    raw_lines = safe_markdown.split('\n')

    for line in raw_lines:
        line_clean = line.strip()
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
