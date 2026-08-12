from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
)


def generate_roadmap_pdf(
    target_role,
    current_level,
    time_available,
    roadmap
):
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

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=22,
        spaceAfter=15
    )

    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        fontSize=14,
        spaceBefore=12,
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["BodyText"],
        fontSize=10,
        leading=15,
        spaceAfter=6
    )

    story = []

    story.append(
        Paragraph(
            "🚀 CareerPilot AI – Career Roadmap",
            title_style
        )
    )

    story.append(
        Paragraph(
            f"<b>Target Role:</b> {target_role}",
            body_style
        )
    )

    story.append(
        Paragraph(
            f"<b>Current Level:</b> {current_level}",
            body_style
        )
    )

    story.append(
        Paragraph(
            f"<b>Time Available:</b> {time_available}",
            body_style
        )
    )

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            "Personalized Career Roadmap",
            heading_style
        )
    )

    # Convert roadmap to plain text if Gemini returns content parts
    if isinstance(roadmap, list):
        roadmap = "".join(
            part.get("text", "")
            for part in roadmap
            if isinstance(part, dict)
        )

    for line in roadmap.split("\n"):

        line = line.strip()

        if not line:
            story.append(Spacer(1, 5))
            continue

        if line.startswith("#"):
            clean_line = line.lstrip("#").strip()

            story.append(
                Paragraph(
                    clean_line,
                    heading_style
                )
            )

        else:
            clean_line = line.replace("&", "&amp;")

            story.append(
                Paragraph(
                    clean_line,
                    body_style
                )
            )

    doc.build(story)

    buffer.seek(0)

    return buffer.getvalue()