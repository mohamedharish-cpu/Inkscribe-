import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def register_handwriting_font():
    """Registers Kalam handwriting font if present in fonts/ folder."""
    font_path = os.path.join("fonts", "Kalam-Regular.ttf")
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont("Kalam", font_path))
        return "Kalam"
    # Fallback to default Helvetica if TTF font not found
    return "Helvetica"

def parse_custom_color_tags(text: str) -> str:
    """
    Converts AI custom color tags to ReportLab HTML-style markup:
    - [COLOR:BLUE] -> Blue Heading text
    - [COLOR:ORANGE] -> Dark Orange Formula / Key Answer text
    - [COLOR:BOLD] -> Bold Black exam keyword text
    """
    text = re.sub(r'\[COLOR:BLUE\](.*?)\[/COLOR\]', r'<font color="#0F4C81"><b>\1</b></font>', text)
    text = re.sub(r'\[COLOR:ORANGE\](.*?)\[/COLOR\]', r'<font color="#D35400"><b>\1</b></font>', text)
    text = re.sub(r'\[COLOR:BOLD\](.*?)\[/COLOR\]', r'<b>\1</b>', text)
    return text

def build_single_combined_pdf(notes_text: str, output_filename: str = "outputs/Inkscribe_Handwritten_Notes.pdf") -> str:
    """
    Generates a single combined PDF document with custom colors, 
    formula callout styling, and hand-drawn diagram placeholders.
    """
    # Ensure outputs directory exists
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
    font_name = register_handwriting_font()
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Styles
    body_style = ParagraphStyle(
        'HandwrittenBody',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=11,
        leading=16,
        textColor=colors.HexColor('#2C3E50')
    )
    
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Title'],
        fontName=font_name,
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F4C81'),
        alignment=1 # Centered
    )

    story = []
    
    # Title Banner
    story.append(Paragraph("<b>✍️ INKSCRIBE AI — HANDWRITTEN EXAM NOTES</b>", title_style))
    story.append(Spacer(1, 15))

    # Split lines and process special blocks
    lines = notes_text.split('\n')
    
    for line in lines:
        line_str = line.strip()
        if not line_str:
            story.append(Spacer(1, 6))
            continue
            
        # Parse hand-drawn diagram placeholders into visual sketch boxes
        if line_str.startswith("[HAND-DRAWN DIAGRAM:"):
            diagram_info = line_str.replace("[HAND-DRAWN DIAGRAM:", "").replace("]", "").strip()
            
            diagram_content = [
                Paragraph(f"<b>🎨 HAND-DRAWN DIAGRAM PLACEHOLDER</b>", ParagraphStyle('DiagHeader', parent=body_style, textColor=colors.HexColor('#D35400'))),
                Paragraph(f"<i>{diagram_info}</i>", body_style)
            ]
            
            box_table = Table([[diagram_content]], colWidths=[500])
            box_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FEF9E7')),
                ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#F39C12')),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#F39C12')),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('LEFTPADDING', (0,0), (-1,-1), 12),
                ('RIGHTPADDING', (0,0), (-1,-1), 12),
            ]))
            story.append(Spacer(1, 6))
            story.append(box_table)
            story.append(Spacer(1, 6))
            continue

        # Formula callout boxes
        if "=== KEY FORMULAS TO REMEMBER ===" in line_str:
            p_text = f"<b><font color='#D35400'>🧮 {line_str}</font></b>"
            story.append(Spacer(1, 8))
            story.append(Paragraph(p_text, body_style))
            story.append(Spacer(1, 4))
            continue

        # Convert custom tags to HTML format for ReportLab
        formatted_line = parse_custom_color_tags(line_str)
        story.append(Paragraph(formatted_line, body_style))

    # Build the PDF
    doc.build(story)
    return output_filename