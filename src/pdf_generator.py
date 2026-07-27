import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

def clean_text_for_pdf(text: str) -> str:
    """
    100% Strict ASCII Sanitizer.
    Replaces smart quotes/dashes and strips ALL non-ASCII characters to prevent PDF encoding errors.
    """
    if not text:
        return ""
    
    # 1. Swap common Unicode quotes and dashes to standard ASCII equivalents
    replacements = {
        '“': '"', '”': '"', '‘': "'", '’': "'",
        '—': '-', '–': '-', '…': '...', '•': '*',
        '™': '', '®': '', '©': ''
    }
    for key, val in replacements.items():
        text = text.replace(key, val)
        
    # 2. Convert Markdown Bold (**text**) to ReportLab HTML Bold (<b>text</b>)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    
    # 3. STRICT ASCII FILTER: Remove any remaining non-ASCII character (ordinal > 127)
    clean_ascii = re.sub(r'[^\x00-\x7F]+', '', text)
    
    return clean_ascii


def build_single_combined_pdf(notes_markdown: str, output_filename: str = "Inkscribe_Exam_Notes.pdf") -> str:
    """Generates a clean, styled PDF from markdown text."""
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
    
    # Clean text to 100% strict ASCII
    safe_markdown = clean_text_for_pdf(notes_markdown)
    lines = safe_markdown.split('\n')

    for line in lines:
        line_str = line.strip()
        if not line_str:
            story.append(Spacer(1, 4))
            continue
            
        if line_str.startswith("# "):
            clean_line = line_str.replace("# ", "")
            story.append(Paragraph(clean_line, title_style))
            story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#a855f7"), spaceAfter=10))
        elif line_str.startswith("## "):
            clean_line = line_str.replace("## ", "")
            story.append(Paragraph(clean_line, h1_style))
        elif line_str.startswith("### ") or line_str.startswith("#### "):
            clean_line = re.sub(r'^#+\s*', '', line_str)
            story.append(Paragraph(clean_line, h2_style))
        elif line_str.startswith("---"):
            story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#cbd5e1"), spaceBefore=8, spaceAfter=8))
        else:
            story.append(Paragraph(line_str, body_style))

    doc.build(story)
    return pdf_path
