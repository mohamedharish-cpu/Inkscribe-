import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def clean_markdown_to_html(text: str) -> str:
    """Converts bold markdown to HTML <b> tags and cleans remaining raw symbols."""
    # Convert **bold** to <b>bold</b>
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Remove single asterisks or lingering markdown symbols
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    text = text.replace('###', '').replace('##', '').replace('#', '')
    return text.strip()

def build_single_combined_pdf(markdown_text: str, output_filename: str = "Inkscribe_Exam_Handwritten_Notes.pdf") -> str:
    """Generates a beautifully styled, color-highlighted PDF from generated notes."""
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom Highlight & Color Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=colors.HexColor("#1e1b4b"),
        alignment=1, # Center
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=15,
        textColor=colors.HexColor("#065f46"), # Deep Green Highlight
        spaceBefore=14,
        spaceAfter=6
    )

    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor("#9333ea"), # Royal Purple Highlight
        spaceBefore=10,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=6
    )

    question_box_style = ParagraphStyle(
        'QuestionBoxText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#b45309"), # Gold / Amber Dark
        spaceAfter=0
    )

    story = []

    # Main Document Header
    story.append(Paragraph("✍️ INKSCRIBE AI — HIGH-YIELD EXAM NOTES", title_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#a855f7"), spaceAfter=15))

    lines = markdown_text.split('\n')
    
    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue

        # Header 1 parsing (e.g., Unit Titles / Major Topics)
        if line_str.startswith('# ') or line_str.startswith('## '):
            cleaned = clean_markdown_to_html(line_str)
            story.append(Paragraph(f"📌 {cleaned}", h1_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceAfter=6))

        # Header 2 parsing (e.g., Sub-topics)
        elif line_str.startswith('### '):
            cleaned = clean_markdown_to_html(line_str)
            story.append(Paragraph(f"▶ {cleaned}", h2_style))

        # Highlighting Questions / 16-Mark Questions in a Gold Highlight Box
        elif "Question" in line_str or "16-Mark" in line_str:
            cleaned = clean_markdown_to_html(line_str)
            p = Paragraph(f"<b>{cleaned}</b>", question_box_style)
            # Create a highlighted box
            t = Table([[p]], colWidths=[520])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#fef3c7")), # Amber Highlight BG
                ('BORDER', (0, 0), (-1, -1), 1, colors.HexColor("#f59e0b")), # Gold Border
                ('PADDING', (0, 0), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(Spacer(1, 6))
            story.append(t)
            story.append(Spacer(1, 6))

        # Bullet Points
        elif line_str.startswith('* ') or line_str.startswith('+ ') or line_str.startswith('- '):
            cleaned = clean_markdown_to_html(line_str[2:])
            bullet_p = Paragraph(f"• {cleaned}", body_style)
            story.append(bullet_p)

        # Standard Paragraphs
        else:
            cleaned = clean_markdown_to_html(line_str)
            story.append(Paragraph(cleaned, body_style))

    doc.build(story)
    return output_filename
