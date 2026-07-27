import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

def sanitize_to_pure_ascii(text: str) -> str:
    """
    Mathematically guarantees 100% pure ASCII output (ord < 128).
    Prevents any ReportLab UnicodeEncodeError / ASCII codec crashes.
    """
    if not text:
        return ""
    
    # 1. Map known Unicode characters to clean ASCII equivalents
    char_map = {
        '\u2026': '...', '…': '...',
        '\u201c': '"', '\u201d': '"', '“': '"', '”': '"',
        '\u2018': "'", '\u2019': "'", '‘': "'", '’': "'",
        '\u2013': '-', '\u2014': '-', '—': '-', '–': '-',
        '\u2022': '*', '•': '*',
    }
    for orig, repl in char_map.items():
        text = text.replace(orig, repl)
        
    # 2. Convert Markdown Bold (**text**) to HTML Bold (<b>text</b>)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    
    # 3. ABSOLUTE BULLETPROOF FILTER: Keep ONLY characters with ord < 128
    pure_ascii = "".join(c for c in text if ord(c) < 128)
    
    return pure_ascii


def build_single_combined_pdf(notes_markdown: str, output_filename: str = "Inkscribe_Exam_Notes.pdf") -> str:
    """Generates a styled PDF guaranteed free of encoding errors."""
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
    
    # Run absolute ASCII sanitizer on raw text
    safe_text = sanitize_to_pure_ascii(notes_markdown)
    raw_lines = safe_text.split('\n')

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
