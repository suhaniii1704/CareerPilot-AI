from io import BytesIO
import html
import re

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
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
# TEXT HELPERS
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
    return html.escape(clean_text(value))


# =========================================================
# STYLES
# =========================================================

def create_styles():

    base = getSampleStyleSheet()

    return {

        "title": ParagraphStyle(
            "ReportTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=23,
            leading=28,
            textColor=WHITE,
            alignment=1
        ),

        "subtitle": ParagraphStyle(
            "ReportSubtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#D1D5DB"),
            alignment=1
        ),

        "card_title": ParagraphStyle(
            "CardTitle",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=BLUE,
            spaceAfter=8
        ),

        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=14,
            textColor=TEXT,
            spaceAfter=4
        ),

        "small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=12,
            textColor=MUTED
        ),

        "score": ParagraphStyle(
            "Score",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=28,
            leading=32,
            alignment=1
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

    result = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        line = re.sub(
            r"^[-•]\s*",
            "",
            line
        )

        result.append(
            Paragraph(
                "• " + safe(line),
                styles["body"]
            )
        )

    return result


# =========================================================
# CARD
# =========================================================

def create_card(
    title,
    content,
    accent,
    styles
):

    elements = []

    elements.append(
        Paragraph(
            safe(title),
            ParagraphStyle(
                "CardHeading",
                parent=styles["card_title"],
                textColor=accent
            )
        )
    )

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
# HEADER / FOOTER
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
# MAIN FUNCTION
# =========================================================

def generate_report(
    resume_data,
    target_role,
    output_path
):

    styles = create_styles()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=22 * mm,
        leftMargin=22 * mm,
        topMargin=22 * mm,
        bottomMargin=18 * mm,
        title="CareerPilot AI - Resume Analysis Report"
    )

    elements = []

    info = resume_data.get(
        "personal_information",
        {}
    ) or {}

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
                    "Professional Resume Analysis Report",
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
    # CANDIDATE PROFILE
    # =====================================================

    candidate = (
        f"Candidate: {info.get('name', 'Not available')}\n"
        f"Target Role: {target_role}"
    )

    elements.append(
        create_card(
            "👤 CANDIDATE PROFILE",
            candidate,
            BLUE,
            styles
        )
    )

    elements.append(
        Spacer(1, 10)
    )

    # =====================================================
    # ATS SCORE
    # =====================================================

    try:
        ats = float(
            resume_data.get(
                "ats_score",
                0
            )
        )
    except (TypeError, ValueError):

        ats = 0

    if ats >= 80:

        score_color = GREEN
        status = "Excellent ATS Compatibility"

    elif ats >= 60:

        score_color = ORANGE
        status = "Good ATS Compatibility"

    else:

        score_color = RED
        status = "Needs Improvement"

    score_table = Table(
        [[
            Paragraph(
                "⭐ ATS SCORE",
                ParagraphStyle(
                    "ScoreLabel",
                    parent=styles["card_title"],
                    textColor=score_color
                )
            ),

            Paragraph(
                f"{ats:.0f}/100",
                ParagraphStyle(
                    "ScoreValue",
                    parent=styles["score"],
                    textColor=score_color
                )
            ),

            Paragraph(
                status,
                styles["small"]
            )
        ]],
        colWidths=[
            55 * mm,
            45 * mm,
            65 * mm
        ]
    )

    score_table.setStyle(
        TableStyle([
            (
                "BOX",
                (0, 0),
                (-1, -1),
                1,
                score_color
            ),

            (
                "INNERGRID",
                (0, 0),
                (-1, -1),
                0.5,
                BORDER
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "ALIGN",
                (1, 0),
                (1, 0),
                "CENTER"
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                10
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                10
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
            )
        ])
    )

    elements.append(score_table)

    elements.append(
        Spacer(1, 12)
    )

    # =====================================================
    # PERSONAL INFORMATION
    # =====================================================

    personal = (
        f"Name: {info.get('name', '')}\n"
        f"Email: {info.get('email', '')}\n"
        f"Phone: {info.get('phone', '')}\n"
        f"LinkedIn: {info.get('linkedin', '')}\n"
        f"GitHub: {info.get('github', '')}"
    )

    elements.append(
        create_card(
            "👤 PERSONAL INFORMATION",
            personal,
            BLUE,
            styles
        )
    )

    elements.append(
        Spacer(1, 10)
    )

    # =====================================================
    # SKILLS
    # =====================================================

    skills = resume_data.get(
        "skills",
        []
    ) or []

    skills_text = (
        "\n".join(
            str(skill)
            for skill in skills
        )
        if skills
        else "No skills found."
    )

    elements.append(
        create_card(
            "🛠 TECHNICAL SKILLS",
            skills_text,
            PURPLE,
            styles
        )
    )

    elements.append(
        Spacer(1, 10)
    )

    # =====================================================
    # EDUCATION
    # =====================================================

    education = resume_data.get(
        "education",
        []
    ) or []

    if education:

        for edu in education:

            content = (
                f"Degree: {edu.get('degree', '')}\n"
                f"Institution: {edu.get('institution', '')}\n"
                f"Year: {edu.get('year', '')}\n"
                f"CGPA: {edu.get('cgpa', '')}"
            )

            elements.append(
                create_card(
                    "🎓 EDUCATION",
                    content,
                    BLUE,
                    styles
                )
            )

            elements.append(
                Spacer(1, 10)
            )

    else:

        elements.append(
            create_card(
                "🎓 EDUCATION",
                "No education information found.",
                BLUE,
                styles
            )
        )

        elements.append(
            Spacer(1, 10)
        )

    # =====================================================
    # EXPERIENCE
    # =====================================================

    experience = resume_data.get(
        "experience",
        []
    ) or []

    if experience:

        for exp in experience:

            content = (
                f"Role: {exp.get('role', '')}\n"
                f"Company: {exp.get('company', '')}\n"
                f"Duration: {exp.get('duration', '')}\n"
                f"Description: {exp.get('description', '')}"
            )

            elements.append(
                create_card(
                    "💼 EXPERIENCE",
                    content,
                    CYAN,
                    styles
                )
            )

            elements.append(
                Spacer(1, 10)
            )

    else:

        elements.append(
            create_card(
                "💼 EXPERIENCE",
                "No experience information found.",
                CYAN,
                styles
            )
        )

        elements.append(
            Spacer(1, 10)
        )

    # =====================================================
    # PROJECTS
    # =====================================================

    projects = resume_data.get(
        "projects",
        []
    ) or []

    if projects:

        for project in projects:

            content = (
                f"Project: {project.get('name', '')}\n"
                f"Tech Stack: {project.get('technologies', '')}\n"
                f"Description: {project.get('description', '')}"
            )

            elements.append(
                create_card(
                    "📂 PROJECT",
                    content,
                    PURPLE,
                    styles
                )
            )

            elements.append(
                Spacer(1, 10)
            )

    else:

        elements.append(
            create_card(
                "📂 PROJECTS",
                "No projects found.",
                PURPLE,
                styles
            )
        )

        elements.append(
            Spacer(1, 10)
        )

    # =====================================================
    # CERTIFICATIONS
    # =====================================================

    certifications = resume_data.get(
        "certifications",
        []
    ) or []

    certifications_text = (
        "\n".join(
            str(cert)
            for cert in certifications
        )
        if certifications
        else "No certifications found."
    )

    elements.append(
        create_card(
            "🏆 CERTIFICATIONS",
            certifications_text,
            GREEN,
            styles
        )
    )

    elements.append(
        Spacer(1, 10)
    )

    # =====================================================
    # MISSING SKILLS
    # =====================================================

    missing_skills = resume_data.get(
        "missing_skills",
        []
    ) or []

    missing_text = (
        "\n".join(
            str(skill)
            for skill in missing_skills
        )
        if missing_skills
        else "No major missing skills found."
    )

    elements.append(
        create_card(
            f"🎯 MISSING SKILLS FOR {str(target_role).upper()}",
            missing_text,
            ORANGE,
            styles
        )
    )

    elements.append(
        Spacer(1, 10)
    )

    # =====================================================
    # AI SUGGESTIONS
    # =====================================================

    suggestions = resume_data.get(
        "suggestions",
        []
    ) or []

    suggestions_text = (
        "\n".join(
            str(suggestion)
            for suggestion in suggestions
        )
        if suggestions
        else "No suggestions available."
    )

    elements.append(
        create_card(
            "💡 AI IMPROVEMENT SUGGESTIONS",
            suggestions_text,
            BLUE,
            styles
        )
    )

    # =====================================================
    # BUILD PDF
    # =====================================================

    doc.build(
        elements,
        onFirstPage=page_header_footer,
        onLaterPages=page_header_footer
    )