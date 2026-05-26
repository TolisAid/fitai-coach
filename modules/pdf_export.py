from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.pagesizes import A4

from reportlab.lib.styles import getSampleStyleSheet

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from io import BytesIO

# =========================
# REGISTER FONT
# =========================

pdfmetrics.registerFont(
    TTFont(
        "Arial",
        "assets/fonts/arial.ttf"
    )
)

# =========================
# CREATE PDF
# =========================

def create_pdf(title, content):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Χρησιμοποιούμε unicode font
    title_style = styles["Title"]
    title_style.fontName = "Arial"

    body_style = styles["BodyText"]
    body_style.fontName = "Arial"

    story = []

    # Title
    story.append(
        Paragraph(title, title_style)
    )

    story.append(
        Spacer(1, 20)
    )

    # Content
    for line in content.split("\n"):

        if line.strip() == "":

            story.append(
                Spacer(1, 10)
            )

        else:

            story.append(
                Paragraph(line, body_style)
            )

    # Build PDF
    doc.build(story)

    buffer.seek(0)

    return buffer