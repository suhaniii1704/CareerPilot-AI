from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO


def generate_job_match_pdf(target_role, job_description, result):

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    elements = []

    # Title
    elements.append(
        Paragraph(
            "<b>CareerPilot AI - Job Match Report</b>",
            styles["Title"]
        )
    )

    elements.append(Spacer(1, 16))

    # Target role
    elements.append(
        Paragraph(
            f"<b>Target Role:</b> {target_role}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 14))

    # Job description heading
    elements.append(
        Paragraph(
            "<b>Job Description</b>",
            styles["Heading2"]
        )
    )

    elements.append(Spacer(1, 8))

    # Job description body
    elements.append(
        Paragraph(
            job_description.replace("\n", "<br/>"),
            styles["BodyText"]
        )
    )

    elements.append(Spacer(1, 18))

    # AI analysis heading
    elements.append(
        Paragraph(
            "<b>AI Job Match Analysis</b>",
            styles["Heading2"]
        )
    )

    elements.append(Spacer(1, 8))

    # AI analysis body
    for line in result.split("\n"):

        if line.strip():

            elements.append(
                Paragraph(
                    line,
                    styles["BodyText"]
                )
            )

            elements.append(Spacer(1, 6))

    doc.build(elements)

    pdf = buffer.getvalue()

    buffer.close()

    return pdf