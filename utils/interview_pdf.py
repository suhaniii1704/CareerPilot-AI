from io import BytesIO
import html
import re

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether
)


# =========================================================
# COLORS
# =========================================================

NAVY = colors.HexColor("#111827")
BLUE = colors.HexColor("#2563EB")
PURPLE = colors.HexColor("#7C3AED")
GREEN = colors.HexColor("#16A34A")
ORANGE = colors.HexColor("#EA580C")
RED = colors.HexColor("#DC2626")
CYAN = colors.HexColor("#0891B2")

TEXT = colors.HexColor("#1F2937")
MUTED = colors.HexColor("#6B7280")
BORDER = colors.HexColor("#D1D5DB")

WHITE = colors.white


# =========================================================
# TEXT CLEANING
# =========================================================

def clean_text(value):

    if value is None:
        return ""

    text = str(value)

    text = text.replace("***", "")
    text = text.replace("**", "")
    text = text.replace("___", "")
    text = text.replace("---", "")

    text = re.sub(
        r"^\s*#{1,6}\s*",
        "",
        text,
        flags=re.MULTILINE
    )

    return text.strip()


def safe(value):

    return html.escape(
        clean_text(value)
    )


# =========================================================
# STYLES
# =========================================================

def create_styles():

    base = getSampleStyleSheet()

    return {

        "title": ParagraphStyle(
            "InterviewTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=23,
            leading=28,
            textColor=WHITE,
            alignment=1
        ),

        "subtitle": ParagraphStyle(
            "InterviewSubtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#D1D5DB"),
            alignment=1
        ),

        "card_title": ParagraphStyle(
            "InterviewCardTitle",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=BLUE,
            spaceAfter=8
        ),

        "body": ParagraphStyle(
            "InterviewBody",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=14,
            textColor=TEXT,
            spaceAfter=4
        ),

        "question": ParagraphStyle(
            "Question",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=15,
            textColor=TEXT,
            spaceAfter=7
        ),

        "small": ParagraphStyle(
            "Small",
            parent=base["Normal"],
            fontSize=8.5,
            leading=12,
            textColor=MUTED
        )
    }


# =========================================================
# CONTENT
# =========================================================

def make_content(text, styles):

    text = clean_text(text)

    if not text:

        return [
            Paragraph(
                "No information available.",
                styles["small"]
            )
        ]

    elements = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        if line.startswith("-") or line.startswith("•"):

            line = line[1:].strip()

            elements.append(
                Paragraph(
                    "• " + safe(line),
                    styles["body"]
                )
            )

        else:

            elements.append(
                Paragraph(
                    safe(line),
                    styles["body"]
                )
            )

    return elements


# =========================================================
# GENERAL CARD
# =========================================================

def create_card(
    title,
    content,
    accent,
    styles
):

    elements = [
        Paragraph(
            safe(title),
            ParagraphStyle(
                "CardHeading",
                parent=styles["card_title"],
                textColor=accent
            )
        )
    ]

    elements.extend(
        make_content(
            content,
            styles
        )
    )

    table = Table(
        [[elements]],
        colWidths=[165 * mm]
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                WHITE
            ),

            (
                "BOX",
                (0, 0),
                (-1, -1),
                1,
                accent
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                12
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                12
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                10
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                10
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            )
        ])
    )

    return table


# =========================================================
# PAGE HEADER / FOOTER
# =========================================================

def page_header_footer(
    canvas,
    doc
):

    canvas.saveState()

    width, height = A4

    canvas.setStrokeColor(BLUE)
    canvas.setLineWidth(1)

    canvas.line(
        20 * mm,
        height - 15 * mm,
        width - 20 * mm,
        height - 15 * mm
    )

    canvas.setFont(
        "Helvetica",
        8
    )

    canvas.setFillColor(
        MUTED
    )

    canvas.drawString(
        20 * mm,
        10 * mm,
        "CareerPilot AI"
    )

    canvas.drawRightString(
        width - 20 * mm,
        10 * mm,
        f"Page {doc.page}"
    )

    canvas.restoreState()


# =========================================================
# INTERVIEW PDF
# =========================================================

def generate_interview_pdf(
    target_role,
    history,
    final_report
):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=22 * mm,
        leftMargin=22 * mm,
        topMargin=22 * mm,
        bottomMargin=18 * mm,
        title="CareerPilot AI - Interview Report"
    )

    styles = create_styles()

    elements = []

    # =====================================================
    # HEADER
    # =====================================================

    header = Table(
        [
            [
                Paragraph(
                    "CareerPilot AI",
                    styles["title"]
                )
            ],
            [
                Paragraph(
                    "AI Interview Performance Report",
                    styles["subtitle"]
                )
            ]
        ],
        colWidths=[165 * mm]
    )

    header.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                NAVY
            ),

            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.8,
                NAVY
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, 0),
                16
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, 0),
                2
            ),

            (
                "TOPPADDING",
                (0, 1),
                (-1, 1),
                2
            ),

            (
                "BOTTOMPADDING",
                (0, 1),
                (-1, 1),
                16
            )
        ])
    )

    elements.append(header)

    elements.append(
        Spacer(1, 12)
    )

    # =====================================================
    # TARGET ROLE
    # =====================================================

    elements.append(
        create_card(
            "🎯 TARGET ROLE",
            str(target_role),
            BLUE,
            styles
        )
    )

    elements.append(
        Spacer(1, 10)
    )

    # =====================================================
    # INTERVIEW OVERVIEW
    # =====================================================

    question_count = (
        len(history)
        if history
        else 0
    )

    overview = (
        f"Questions Answered: {question_count}\n"
        f"Interview Type: AI-Powered Mock Interview\n"
        f"Target Role: {target_role}"
    )

    elements.append(
        create_card(
            "📊 INTERVIEW OVERVIEW",
            overview,
            PURPLE,
            styles
        )
    )

    elements.append(
        Spacer(1, 14)
    )

    # =====================================================
    # INTERVIEW CONVERSATION
    # =====================================================

    if history:

        heading = Paragraph(
            "💬 INTERVIEW CONVERSATION",
            ParagraphStyle(
                "ConversationHeading",
                parent=styles["card_title"],
                textColor=BLUE,
                fontSize=15
            )
        )

        elements.append(
            heading
        )

        elements.append(
            Spacer(1, 7)
        )

        for index, item in enumerate(
            history,
            start=1
        ):

            question = item.get(
                "question",
                ""
            )

            answer = item.get(
                "answer",
                ""
            )

            card_content = []

            # Question number
            card_content.append(
                Paragraph(
                    f"QUESTION {index}",
                    ParagraphStyle(
                        "QuestionNumber",
                        parent=styles["card_title"],
                        textColor=PURPLE,
                        fontSize=12
                    )
                )
            )

            # Interviewer question
            card_content.append(
                Paragraph(
                    f"<b>Interviewer:</b> {safe(question)}",
                    styles["question"]
                )
            )

            card_content.append(
                Spacer(1, 5)
            )

            # Candidate answer
            card_content.append(
                Paragraph(
                    "<b>Your Answer:</b>",
                    ParagraphStyle(
                        "AnswerLabel",
                        parent=styles["body"],
                        fontName="Helvetica-Bold",
                        textColor=CYAN
                    )
                )
            )

            card_content.extend(
                make_content(
                    answer,
                    styles
                )
            )

            question_table = Table(
                [[card_content]],
                colWidths=[165 * mm]
            )

            question_table.setStyle(
                TableStyle([
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        WHITE
                    ),

                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        1,
                        PURPLE
                    ),

                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        12
                    ),

                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        12
                    ),

                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        10
                    ),

                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        10
                    ),

                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP"
                    )
                ])
            )

            elements.append(
                KeepTogether([
                    question_table,
                    Spacer(1, 10)
                ])
            )

    # =====================================================
    # FINAL EVALUATION
    # =====================================================

    if final_report:

        elements.append(
            Spacer(1, 5)
        )

        elements.append(
            create_card(
                "📋 FINAL AI EVALUATION",
                final_report,
                CYAN,
                styles
            )
        )

    # =====================================================
    # BUILD
    # =====================================================

    doc.build(
        elements,
        onFirstPage=page_header_footer,
        onLaterPages=page_header_footer
    )

    buffer.seek(0)

    pdf = buffer.getvalue()

    buffer.close()

    return pdf