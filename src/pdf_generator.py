import os
import re
import unicodedata
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

def sanitize_text_for_pdf(text: str) -> str:
    """
    100% Unicode & Smart-Quote proof sanitizer.
    Converts smart quotes (\u201c, \u201d, etc.) and strips unencodable emojis/symbols.
    """
    if not text:
        return ""
    
    # 1. Explicitly swap smart quotes, apostrophes, and dashes
    replacements = {
        '\u201c': '"',  # Left double quote (“)
        '\u201d': '"',  # Right double quote (”)
        '\u2018': "'",  # Left single quote (‘)
        '\u2019': "'",  # Right single quote (’)
        '\u2013': '-',  # En dash (–)
        '\u2014': '-',  # Em dash (—)
        '\u2026': '...',# Ellipsis (…)
        '\u2022': '*',  # Bullet point (•)
    }
    
    for unicode_char, ascii_char in replacements.items():
        text = text.replace(unicode_char, ascii_char)
    
    # 2. Normalize and strip any remaining non-ASCII characters safely
    normalized = unicodedata.normalize('NFKD', text)
    clean_ascii = normalized.encode('ascii', 'ignore').decode('ascii')
    
    # 3. Convert Markdown Bold (**text**) to ReportLab HTML Bold (<b>text</b>)
    formatted = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', clean_ascii)
    
    return formatted


def build_single_combined_pdf(notes_markdown: str, output_filename: str = "Inkscribe_Exam_Notes.pdf") -> str:
    """Generates a clean PDF from notes markdown text."""
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
    
    # Sanitize markdown content before parsing
    safe_markdown = sanitize_text_for_pdf(notes_markdown)
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
