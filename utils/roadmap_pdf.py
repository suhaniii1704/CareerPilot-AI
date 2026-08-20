from io import BytesIO
import re
import html

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    PageBreak,
)


# =========================================================
# COLORS
# =========================================================

NAVY = colors.HexColor("#111827")
LIGHT_NAVY = colors.HexColor("#F4F7FB")
BLUE = colors.HexColor("#2563EB")
PURPLE = colors.HexColor("#7C3AED")
RED = colors.HexColor("#DC2626")
CYAN = colors.HexColor("#0891B2")
GRAY = colors.HexColor("#6B7280")
DARK = colors.HexColor("#111827")
WHITE = colors.white
BORDER = colors.HexColor("#D1D5DB")


# =========================================================
# CLEAN TEXT
# =========================================================

def clean_text(text):

    if not text:
        return ""

    text = str(text)

    # Remove markdown formatting
    text = text.replace("***", "")
    text = text.replace("**", "")
    text = text.replace("___", "")
    text = text.replace("---", "")

    # Remove markdown heading symbols
    text = re.sub(
        r"^\s*#{1,6}\s*",
        "",
        text,
        flags=re.MULTILINE
    )

    return text.strip()


# =========================================================
# CONVERT GEMINI RESPONSE
# =========================================================

def normalize_roadmap(roadmap):

    if isinstance(roadmap, list):

        roadmap = "".join(
            part.get("text", "")
            for part in roadmap
            if isinstance(part, dict)
        )

    return str(roadmap).replace(
        "\r\n",
        "\n"
    ).strip()


# =========================================================
# PARSE ROADMAP
# =========================================================

def parse_roadmap(roadmap):

    roadmap = normalize_roadmap(roadmap)

    sections = {
        "summary": "",
        "weeks": [],
        "gaps": "",
        "project": ""
    }

    # -----------------------------------------------------
    # WEEK HEADINGS
    # -----------------------------------------------------

    week_pattern = re.compile(
        r"(?im)^\s*#{0,6}\s*WEEK\s+(\d+)\s*:?\s*$"
    )

    week_matches = list(
        week_pattern.finditer(roadmap)
    )

    # -----------------------------------------------------
    # KEY GAPS
    # -----------------------------------------------------

    gaps_pattern = re.compile(
        r"(?im)^\s*#{0,6}\s*KEY\s+GAPS\s*:?\s*$"
    )

    gaps_match = gaps_pattern.search(
        roadmap
    )

    # -----------------------------------------------------
    # FINAL PROJECT
    # -----------------------------------------------------

    project_pattern = re.compile(
        r"(?im)^\s*#{0,6}\s*FINAL\s+PROJECT\s*:?\s*$"
    )

    project_match = project_pattern.search(
        roadmap
    )

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    positions = []

    if week_matches:
        positions.append(
            week_matches[0].start()
        )

    if gaps_match:
        positions.append(
            gaps_match.start()
        )

    if project_match:
        positions.append(
            project_match.start()
        )

    if positions:

        summary_end = min(positions)

        sections["summary"] = clean_text(
            roadmap[:summary_end]
        )

    else:

        sections["summary"] = clean_text(
            roadmap
        )

    # -----------------------------------------------------
    # WEEKLY SECTIONS
    # -----------------------------------------------------

    for index, match in enumerate(
        week_matches
    ):

        week_number = int(
            match.group(1)
        )

        start = match.end()

        possible_ends = []

        # Next week
        if index + 1 < len(
            week_matches
        ):

            possible_ends.append(
                week_matches[index + 1].start()
            )

        # Key gaps
        if (
            gaps_match
            and gaps_match.start() > start
        ):

            possible_ends.append(
                gaps_match.start()
            )

        # Final project
        if (
            project_match
            and project_match.start() > start
        ):

            possible_ends.append(
                project_match.start()
            )

        if possible_ends:

            end = min(
                possible_ends
            )

        else:

            end = len(roadmap)

        content = clean_text(
            roadmap[start:end]
        )

        if content:

            sections["weeks"].append(
                {
                    "number": week_number,
                    "content": content
                }
            )

    # -----------------------------------------------------
    # KEY GAPS
    # -----------------------------------------------------

    if gaps_match:

        start = gaps_match.end()

        if (
            project_match
            and project_match.start() > start
        ):

            end = project_match.start()

        else:

            end = len(roadmap)

        sections["gaps"] = clean_text(
            roadmap[start:end]
        )

    # -----------------------------------------------------
    # FINAL PROJECT
    # -----------------------------------------------------

    if project_match:

        sections["project"] = clean_text(
            roadmap[
                project_match.end():
            ]
        )

    return sections


# =========================================================
# STYLES
# =========================================================

def create_styles():

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "RoadmapTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=27,
        textColor=WHITE,
        alignment=TA_CENTER,
        spaceAfter=5
    )

    subtitle_style = ParagraphStyle(
        "RoadmapSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#D1D5DB"),
        alignment=TA_CENTER
    )

    section_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=DARK,
        spaceAfter=7
    )

    body_style = ParagraphStyle(
        "RoadmapBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=DARK,
        spaceAfter=3
    )

    bullet_style = ParagraphStyle(
        "RoadmapBullet",
        parent=body_style,
        leftIndent=10,
        firstLineIndent=-7,
        spaceAfter=4
    )

    small_style = ParagraphStyle(
        "SmallText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=GRAY
    )

    return {
        "title": title_style,
        "subtitle": subtitle_style,
        "section": section_style,
        "body": body_style,
        "bullet": bullet_style,
        "small": small_style
    }


# =========================================================
# SAFE PARAGRAPH TEXT
# =========================================================

def safe(text):

    return html.escape(
        clean_text(text)
    )


# =========================================================
# CONTENT TO PARAGRAPHS
# =========================================================

def make_content_paragraphs(
    text,
    styles
):

    elements = []

    text = clean_text(text)

    if not text:
        return elements

    lines = text.split("\n")

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # Remove markdown heading markers
        line = re.sub(
            r"^#{1,6}\s*",
            "",
            line
        ).strip()

        # Bullet
        if line.startswith("-"):

            content = line[1:].strip()

            elements.append(
                Paragraph(
                    "• " + safe(content),
                    styles["bullet"]
                )
            )

        elif line.startswith("•"):

            content = line[1:].strip()

            elements.append(
                Paragraph(
                    "• " + safe(content),
                    styles["bullet"]
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
# CREATE CARD
# =========================================================

def create_card(
    title,
    content,
    border_color,
    styles
):

    content_elements = make_content_paragraphs(
        content,
        styles
    )

    if not content_elements:
        content_elements = [
            Paragraph(
                "No information available.",
                styles["small"]
            )
        ]

    # Card title
    title_paragraph = Paragraph(
        f"<b>{safe(title)}</b>",
        ParagraphStyle(
            "CardTitle",
            parent=styles["section"],
            textColor=border_color,
            fontSize=13,
            leading=16,
            spaceAfter=7
        )
    )

    card_content = [
        title_paragraph
    ]

    card_content.extend(
        content_elements
    )

    # Put content in a one-cell table
    card = Table(
        [[card_content]],
        colWidths=[165 * mm]
    )

    card.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.white
                ),

                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1.2,
                    border_color
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
            ]
        )
    )

    return card


# =========================================================
# HEADER / FOOTER
# =========================================================

def add_page_header_footer(
    canvas,
    doc
):

    canvas.saveState()

    width, height = A4

    # Top line
    canvas.setStrokeColor(
        colors.HexColor("#2563EB")
    )

    canvas.setLineWidth(1)

    canvas.line(
        20 * mm,
        height - 15 * mm,
        width - 20 * mm,
        height - 15 * mm
    )

    # Footer
    canvas.setFont(
        "Helvetica",
        8
    )

    canvas.setFillColor(
        colors.HexColor("#6B7280")
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
# MAIN PDF FUNCTION
# =========================================================

def generate_roadmap_pdf(
    target_role,
    current_level,
    time_available,
    roadmap
):

    buffer = BytesIO()

    # -----------------------------------------------------
    # Document
    # -----------------------------------------------------

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=22 * mm,
        leftMargin=22 * mm,
        topMargin=22 * mm,
        bottomMargin=18 * mm,
        title="CareerPilot AI Career Roadmap",
        author="CareerPilot AI"
    )

    styles = create_styles()

    sections = parse_roadmap(
        roadmap
    )

    story = []

    # =====================================================
    # COVER / TITLE
    # =====================================================

    header_data = [
        [
            Paragraph(
                "CareerPilot AI",
                styles["title"]
            )
        ],
        [
            Paragraph(
                "Personalized Career Roadmap",
                styles["subtitle"]
            )
        ]
    ]

    header_table = Table(
        header_data,
        colWidths=[165 * mm]
    )

    header_table.setStyle(
        TableStyle(
            [
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
            ]
        )
    )

    story.append(
        header_table
    )

    story.append(
        Spacer(1, 12)
    )

    # =====================================================
    # PROFILE INFORMATION CARD
    # =====================================================

    profile_data = [
        [
            Paragraph(
                "<b>TARGET ROLE</b>",
                styles["small"]
            ),
            Paragraph(
                "<b>CURRENT LEVEL</b>",
                styles["small"]
            ),
            Paragraph(
                "<b>DURATION</b>",
                styles["small"]
            )
        ],
        [
            Paragraph(
                safe(target_role),
                styles["body"]
            ),
            Paragraph(
                safe(current_level),
                styles["body"]
            ),
            Paragraph(
                safe(time_available),
                styles["body"]
            )
        ]
    ]

    profile_table = Table(
        profile_data,
        colWidths=[
            55 * mm,
            55 * mm,
            55 * mm
        ]
    )

    profile_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    LIGHT_NAVY
                ),

                (
                    "BACKGROUND",
                    (0, 1),
                    (-1, 1),
                    colors.white
                ),

                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.8,
                    BORDER
                ),

                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    BORDER
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
                    8
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                )
            ]
        )
    )

    story.append(
        profile_table
    )

    story.append(
        Spacer(1, 15)
    )

    # =====================================================
    # SUMMARY
    # =====================================================

    if sections["summary"]:

        story.append(
            create_card(
                "ROADMAP SUMMARY",
                sections["summary"],
                BLUE,
                styles
            )
        )

        story.append(
            Spacer(1, 10)
        )

    # =====================================================
    # WEEKLY CARDS
    # =====================================================

    for week in sections["weeks"]:

        week_card = create_card(
            f"WEEK {week['number']}",
            week["content"],
            PURPLE,
            styles
        )

        story.append(
            KeepTogether(
                [
                    week_card,
                    Spacer(1, 8)
                ]
            )
        )

    # =====================================================
    # KEY GAPS
    # =====================================================

    if sections["gaps"]:

        story.append(
            Spacer(1, 5)
        )

        story.append(
            create_card(
                "KEY GAPS",
                sections["gaps"],
                RED,
                styles
            )
        )

        story.append(
            Spacer(1, 10)
        )

    # =====================================================
    # FINAL PROJECT
    # =====================================================

    if sections["project"]:

        story.append(
            create_card(
                "FINAL PROJECT",
                sections["project"],
                CYAN,
                styles
            )
        )

    # =====================================================
    # BUILD
    # =====================================================

    doc.build(
        story,
        onFirstPage=add_page_header_footer,
        onLaterPages=add_page_header_footer
    )

    buffer.seek(0)

    return buffer.getvalue()