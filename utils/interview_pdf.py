from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet

from io import BytesIO


def generate_interview_pdf(target_role, history, final_report):

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    elements = []

    # Title
    elements.append(
        Paragraph(
            "<b>CareerPilot AI - Interview Report</b>",
            styles["Title"]
        )
    )

    elements.append(Spacer(1, 12))

    # Role
    elements.append(
        Paragraph(
            f"<b>Target Role:</b> {target_role}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 12))

    # Conversation
    elements.append(
        Paragraph(
            "<b>Interview Conversation</b>",
            styles["Heading2"]
        )
    )

    elements.append(Spacer(1, 6))

    for i, item in enumerate(history, 1):

        elements.append(
            Paragraph(
                f"<b>Q{i}:</b> {item['question']}",
                styles["Normal"]
            )
        )

        elements.append(Spacer(1, 4))

        elements.append(
            Paragraph(
                f"<b>Answer:</b> {item['answer']}",
                styles["Normal"]
            )
        )

        elements.append(Spacer(1, 10))

    # Final evaluation
    elements.append(Spacer(1, 12))

    elements.append(
        Paragraph(
            "<b>Final Evaluation</b>",
            styles["Heading2"]
        )
    )

    elements.append(Spacer(1, 6))

    for line in final_report.split("\n"):

        if line.strip():

            elements.append(
                Paragraph(
                    line,
                    styles["Normal"]
                )
            )

            elements.append(Spacer(1, 4))

    doc.build(elements)

    pdf = buffer.getvalue()

    buffer.close()

    return pdf