import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

def clean_text_for_pdf(text: str) -> str:
    """Replaces unicode smart quotes, dashes, and strips unencodable emojis for clean PDF generation."""
    if not text:
        return ""
    
    # Common Unicode character replacements
    replacements = {
        '“': '"', '”': '"', '‘': "'", '’': "'",
        '—': '-', '–': '-', '…': '...',
        '•': '*', '🎯': '', '✍️': '', '⚡': '',
        '🚀': '', '📄': '', '📦': '', '💡': '',
        '🚨': '', '📥': '', '✅': '', '📌': '',
        '™': '', '®': '', '©': ''
    }
    
    for key, val in replacements.items():
        text = text.replace(key, val)
    
    # Convert markdown bold **text** to HTML bold <b>text</b> for ReportLab Paragraphs
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    
    # Strip any remaining non-ASCII characters to guarantee no ASCII codec encoding errors
    return text.encode('ascii', 'ignore').decode('ascii')


def build_single_combined_pdf(notes_markdown: str, output_filename: str = "Inkscribe_Exam_Notes.pdf") -> str:
    """Converts sanitized markdown text into a styled PDF document."""
    pdf_path = os.path.join(os.getcwd(), output_filename)
    
    # Page setup
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1e1b4b"),
        spaceAfter=12
    )
    
    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#b45309"),
        spaceBefore=14,
        spaceAfter=8
    )
    
    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
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
    
    # Clean text first
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
