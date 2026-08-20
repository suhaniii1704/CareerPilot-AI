from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch

from io import BytesIO
import re


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def clean_text(text):
    """Clean markdown and unwanted formatting."""

    if not text:
        return ""

    text = str(text)

    # Remove markdown formatting
    text = text.replace("**", "")
    text = text.replace("###", "")
    text = text.replace("##", "")
    text = text.replace("#", "")

    return text.strip()


def format_text(text):
    """Make text safe for ReportLab Paragraph."""

    text = clean_text(text)

    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def clean_list_item(text):
    """Remove bullets and numbering from list items."""

    text = clean_text(text)

    text = re.sub(
        r"^[\-\*\u2022\u25cf\u25aa\s]+",
        "",
        text
    )

    text = re.sub(
        r"^\d+[\.\)\:\-]\s*",
        "",
        text
    )

    return text.strip()


# =========================================================
# PARSE AI RESULT
# =========================================================

def parse_job_match_result(result):
    """
    Parse the fixed AI response format:

    MATCH SCORE: 85%

    MISSING KEYWORDS:
    - ...

    STRENGTHS:
    - ...

    AI SUGGESTIONS:
    - ...
    """

    data = {
        "score": None,
        "missing_keywords": [],
        "strengths": [],
        "suggestions": [],
        "overview": []
    }

    if not result:
        return data

    current_section = "overview"

    for raw_line in result.splitlines():

        line = clean_text(raw_line)

        if not line:
            continue

        # Normalize heading for detection
        normalized = (
            line.upper()
            .replace(":", "")
            .strip()
        )

        # -------------------------------------------------
        # MATCH SCORE
        # -------------------------------------------------

        if "MATCH SCORE" in normalized:
            score_match = re.search(
            r"(\d{1,3})(?:\s*%|\s*/\s*100)?",
            line
            )

            if score_match:

               score = int(score_match.group(1))

               if 0 <= score <= 100:
                   data["score"] = score

            continue

        # -------------------------------------------------
        # MISSING KEYWORDS
        # -------------------------------------------------

        if (
            normalized == "MISSING KEYWORDS"
            or "MISSING KEYWORDS" in normalized
            or normalized == "SKILL GAPS"
            or normalized == "MISSING SKILLS"
        ):

            current_section = "missing_keywords"
            continue

        # -------------------------------------------------
        # STRENGTHS
        # -------------------------------------------------

        if (
            normalized == "STRENGTHS"
            or "MATCHING STRENGTHS" in normalized
            or "YOUR STRENGTHS" in normalized
        ):

            current_section = "strengths"
            continue

        # -------------------------------------------------
        # AI SUGGESTIONS
        # -------------------------------------------------

        if (
            normalized == "AI SUGGESTIONS"
            or "AI RECOMMENDATIONS" in normalized
            or normalized == "RECOMMENDATIONS"
            or normalized == "SUGGESTIONS"
        ):

            current_section = "suggestions"
            continue

        # -------------------------------------------------
        # REMOVE BULLET / NUMBER
        # -------------------------------------------------

        item = clean_list_item(line)

        if item:
            data[current_section].append(item)

    # -----------------------------------------------------
    # FALLBACK SCORE EXTRACTION
    # -----------------------------------------------------

    if data["score"] is None:

        score_match = re.search(
            r"(?:MATCH SCORE|OVERALL MATCH)[^\d]{0,30}(\d{1,3})(?:\s*%|\s*/\s*100)?",
            result,
            re.IGNORECASE
            )

        if score_match:

            score = int(score_match.group(1))

            if 0 <= score <= 100:
                data["score"] = score

    return data


# =========================================================
# CREATE LIST BOX
# =========================================================

def create_list_box(
    items,
    bullet_color,
    background_color,
    border_color,
    list_style,
    width
):
    """Create a professional bordered list box."""

    content = []

    for item in items:

        content.append(

            Paragraph(
                f'<font color="{bullet_color}">●</font> '
                f'{format_text(item)}',
                list_style
            )
        )

    table = Table(
        [[content]],
        colWidths=[width]
    )

    table.setStyle(

        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                background_color
            ),

            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.8,
                border_color
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                14
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                14
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                12
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7
            )
        ])
    )

    return table


# =========================================================
# PDF GENERATOR
# =========================================================

def generate_job_match_pdf(
    target_role,
    job_description,
    result
):

    buffer = BytesIO()

    # -----------------------------------------------------
    # DOCUMENT
    # -----------------------------------------------------

    doc = SimpleDocTemplate(

        buffer,

        pagesize=A4,

        rightMargin=45,
        leftMargin=45,

        topMargin=45,
        bottomMargin=55
    )

    page_width = 7.05 * inch

    # -----------------------------------------------------
    # COLORS
    # -----------------------------------------------------

    dark = colors.HexColor("#111827")

    accent = colors.HexColor("#F97316")

    border = colors.HexColor("#CBD5E1")

    text_dark = colors.HexColor("#1E293B")

    text_light = colors.HexColor("#64748B")

    green = colors.HexColor("#15803D")

    green_bg = colors.HexColor("#F0FDF4")

    red = colors.HexColor("#DC2626")

    red_bg = colors.HexColor("#FEF2F2")

    blue = colors.HexColor("#2563EB")

    blue_bg = colors.HexColor("#EFF6FF")

    orange_bg = colors.HexColor("#FFF7ED")

    gray_bg = colors.HexColor("#F8FAFC")

    # -----------------------------------------------------
    # STYLES
    # -----------------------------------------------------

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(

        "CareerPilotTitle",

        parent=styles["Title"],

        fontName="Helvetica-Bold",

        fontSize=25,

        leading=30,

        textColor=colors.white,

        alignment=TA_CENTER
    )

    subtitle_style = ParagraphStyle(

        "CareerPilotSubtitle",

        parent=styles["Normal"],

        fontName="Helvetica",

        fontSize=10,

        leading=14,

        textColor=colors.HexColor("#D1D5DB"),

        alignment=TA_CENTER
    )

    section_title_style = ParagraphStyle(

        "SectionTitle",

        parent=styles["Heading2"],

        fontName="Helvetica-Bold",

        fontSize=13,

        leading=17,

        textColor=dark,

        spaceAfter=9
    )

    body_style = ParagraphStyle(

        "Body",

        parent=styles["BodyText"],

        fontName="Helvetica",

        fontSize=10,

        leading=15,

        textColor=text_dark
    )

    role_style = ParagraphStyle(

        "Role",

        parent=styles["Normal"],

        fontName="Helvetica-Bold",

        fontSize=17,

        leading=23,

        textColor=dark
    )

    score_label_style = ParagraphStyle(

        "ScoreLabel",

        parent=styles["Normal"],

        fontName="Helvetica-Bold",

        fontSize=10,

        textColor=text_light,

        alignment=TA_CENTER
    )

    score_style = ParagraphStyle(

        "Score",

        parent=styles["Normal"],

        fontName="Helvetica-Bold",

        fontSize=34,

        leading=42,

        textColor=accent,

        alignment=TA_CENTER
    )

    list_style = ParagraphStyle(

        "List",

        parent=body_style,

        leftIndent=14,

        firstLineIndent=-10,

        spaceAfter=7
    )

    # -----------------------------------------------------
    # PARSE AI RESULT
    # -----------------------------------------------------

    result = result or ""

    analysis = parse_job_match_result(result)

    # -----------------------------------------------------
    # ELEMENTS
    # -----------------------------------------------------

    elements = []

    # =====================================================
    # HEADER
    # =====================================================

    header = Table(

        [[

            Paragraph(
                "CareerPilot AI",
                title_style
            )

        ], [

            Paragraph(
                "AI-POWERED JOB MATCH REPORT",
                subtitle_style
            )

        ]],

        colWidths=[page_width]
    )

    header.setStyle(

        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                dark
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                18
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                18
            )
        ])
    )

    elements.append(header)

    elements.append(
        Spacer(1, 22)
    )

    # =====================================================
    # TARGET ROLE
    # =====================================================

    elements.append(

        Paragraph(
            "■ TARGET ROLE",
            section_title_style
        )
    )

    elements.append(

        Paragraph(
            format_text(
                target_role
                if target_role
                else "Role not specified"
            ),
            role_style
        )
    )

    elements.append(
        Spacer(1, 22)
    )

    # =====================================================
    # MATCH SCORE
    # =====================================================

    elements.append(

        Paragraph(
            "■ JOB MATCH SCORE",
            section_title_style
        )
    )

    if analysis["score"] is not None:

        score_text = f"{analysis['score']}/100"

    else:

        score_text = "Not Available"

    score_card = Table(

        [[

            Paragraph(
                "MATCH SCORE",
                score_label_style
            )

        ], [

            Paragraph(
                score_text,
                score_style
            )

        ]],

        colWidths=[page_width]
    )

    score_card.setStyle(

        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                orange_bg
            ),

            (
                "BOX",
                (0, 0),
                (-1, -1),
                1,
                accent
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                13
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                13
            )
        ])
    )

    elements.append(score_card)

    elements.append(
        Spacer(1, 22)
    )

    # =====================================================
    # MATCH OVERVIEW
    # =====================================================

    if analysis["overview"]:

        elements.append(

            Paragraph(
                "■ MATCH OVERVIEW",
                section_title_style
            )
        )

        overview_text = " ".join(
            analysis["overview"]
        )

        elements.append(

            Paragraph(
                format_text(overview_text),
                body_style
            )
        )

        elements.append(
            Spacer(1, 20)
        )

    # =====================================================
    # MATCHING STRENGTHS
    # =====================================================

    if analysis["strengths"]:

        elements.append(

            Paragraph(
                "■ MATCHING STRENGTHS",
                section_title_style
            )
        )

        elements.append(

            create_list_box(

                analysis["strengths"],

                "#15803D",

                green_bg,

                green,

                list_style,

                page_width
            )
        )

        elements.append(
            Spacer(1, 20)
        )

    # =====================================================
    # MISSING KEYWORDS
    # =====================================================

    if analysis["missing_keywords"]:

        elements.append(

            Paragraph(
                "■ MISSING KEYWORDS",
                section_title_style
            )
        )

        elements.append(

            create_list_box(

                analysis["missing_keywords"],

                "#DC2626",

                red_bg,

                red,

                list_style,

                page_width
            )
        )

        elements.append(
            Spacer(1, 20)
        )

    # =====================================================
    # AI SUGGESTIONS
    # =====================================================

    if analysis["suggestions"]:

        elements.append(

            Paragraph(
                "■ AI SUGGESTIONS",
                section_title_style
            )
        )

        suggestion_content = []

        for number, item in enumerate(
            analysis["suggestions"],
            start=1
        ):

            suggestion_content.append(

                Paragraph(
                    f'<font color="#2563EB">'
                    f'<b>{number}.</b>'
                    f'</font> '
                    f'{format_text(item)}',

                    list_style
                )
            )

        suggestion_box = Table(

            [[suggestion_content]],

            colWidths=[page_width]
        )

        suggestion_box.setStyle(

            TableStyle([

                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    blue_bg
                ),

                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.8,
                    blue
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    14
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    14
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    12
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                )
            ])
        )

        elements.append(suggestion_box)

        elements.append(
            Spacer(1, 22)
        )

    # =====================================================
    # JOB DESCRIPTION
    # IMPORTANT: MOVED TO THE END
    # =====================================================

    elements.append(

        Paragraph(
            "■ JOB DESCRIPTION",
            section_title_style
        )
    )

    job_text = format_text(
        job_description
        if job_description
        else "Job description not provided."
    )

    job_box = Table(

        [[

            Paragraph(
                job_text.replace(
                    "\n",
                    "<br/>"
                ),
                body_style
            )

        ]],

        colWidths=[page_width]
    )

    job_box.setStyle(

        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                gray_bg
            ),

            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.8,
                border
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                14
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                14
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                14
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                14
            )
        ])
    )

    elements.append(job_box)

    # =====================================================
    # FOOTER
    # =====================================================

    def add_footer(canvas, document):

        canvas.saveState()

        width, height = A4

        canvas.setStrokeColor(border)

        canvas.line(
            45,
            35,
            width - 45,
            35
        )

        canvas.setFont(
            "Helvetica",
            8
        )

        canvas.setFillColor(text_light)

        canvas.drawString(
            45,
            22,
            "CareerPilot AI • AI-Powered Career Intelligence"
        )

        canvas.drawRightString(
            width - 45,
            22,
            f"Page {document.page}"
        )

        canvas.restoreState()

    # =====================================================
    # BUILD PDF
    # =====================================================

    doc.build(

        elements,

        onFirstPage=add_footer,

        onLaterPages=add_footer
    )

    pdf = buffer.getvalue()

    buffer.close()

    return pdf