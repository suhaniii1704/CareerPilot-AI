from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import HexColor, white
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics


styles = getSampleStyleSheet()

TITLE = styles["Heading1"]
TITLE.alignment = TA_CENTER
TITLE.textColor = HexColor("#2563EB")

HEADING = styles["Heading2"]
HEADING.textColor = HexColor("#2563EB")

NORMAL = styles["BodyText"]


def blue_heading(text):
    return Paragraph(
        f"<font color='#2563EB'><b>{text}</b></font>",
        HEADING
    )


def section_space(elements):
    elements.append(Spacer(1, 0.25 * inch))

def create_cover_page(elements, resume_data, target_role):

    elements.append(Spacer(1,0.3*inch))

    elements.append(Paragraph(
        "🚀 CareerPilot AI",
        TITLE
    ))

    elements.append(
        Paragraph(
            "Professional Resume Analysis Report",
            NORMAL
        )
    )

    section_space(elements)

    info = resume_data["personal_information"]

    elements.append(
        blue_heading("Candidate")
    )

    elements.append(
        Paragraph(
            info["name"],
            NORMAL
        )
    )

    section_space(elements)

    elements.append(
        blue_heading("Target Role")
    )

    elements.append(
        Paragraph(
            target_role,
            NORMAL
        )
    )

    section_space(elements)

    ats = resume_data["ats_score"]

    color = "#4CAF50"

    if ats < 60:
        color = "#F44336"

    elif ats < 80:
        color = "#FF9800"

    elements.append(
        Paragraph(
            f"<font color='{color}' size='26'><b>{ats}/100</b></font>",
            TITLE
        )
    )

    if ats >= 80:

        status = "Excellent ATS Compatibility"

    elif ats >= 60:

        status = "Good ATS Compatibility"

    else:

        status = "Needs Improvement"

    elements.append(
        Paragraph(
            status,
            NORMAL
        )
    )

    elements.append(PageBreak())

def create_personal_info_page(elements, resume_data):

    info = resume_data["personal_information"]

    elements.append(
        blue_heading("👤 PERSONAL INFORMATION")
    )

    section_space(elements)

    data = [
        ["Field", "Information"],
        ["Name", info["name"]],
        ["Email", info["email"]],
        ["Phone", info["phone"]],
        ["LinkedIn", info["linkedin"]],
        ["GitHub", info["github"]]
    ]

    table = Table(
        data,
        colWidths=[2 * inch, 4 * inch]
    )

    table.setStyle(TableStyle([

        ("BACKGROUND", (0,0), (-1,0), HexColor("#2563EB")),
        ("TEXTCOLOR", (0,0), (-1,0), white),

        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),

        ("GRID", (0,0), (-1,-1), 0.5, HexColor("#D0D0D0")),

        ("BOTTOMPADDING", (0,0), (-1,0), 10),

        ("BACKGROUND", (0,1), (-1,-1), HexColor("#F8F9FA")),

        ("FONTNAME", (0,1), (-1,-1), "Helvetica"),

        ("ALIGN", (0,0), (-1,-1), "LEFT")
    ]))

    elements.append(table)

    section_space(elements)

def create_skills_section(elements, resume_data):

    elements.append(
        blue_heading("🛠 TECHNICAL SKILLS")
    )

    section_space(elements)

    skills = resume_data["skills"]

    if not skills:

        elements.append(
            Paragraph(
                "No skills found.",
                NORMAL
            )
        )

        return

    rows = []

    row = []

    for skill in skills:

        row.append(skill)

        if len(row) == 3:

            rows.append(row)
            row = []

    if row:

        while len(row) < 3:
            row.append("")

        rows.append(row)

    table = Table(
        rows,
        colWidths=[2 * inch] * 3
    )

    table.setStyle(TableStyle([

        ("BACKGROUND", (0,0), (-1,-1), HexColor("#EAF4FF")),

        ("GRID", (0,0), (-1,-1), 0.4, HexColor("#CFCFCF")),

        ("FONTNAME", (0,0), (-1,-1), "Helvetica-Bold"),

        ("TEXTCOLOR", (0,0), (-1,-1), HexColor("#1E3A8A")),

        ("ALIGN", (0,0), (-1,-1), "CENTER"),

        ("BOTTOMPADDING", (0,0), (-1,-1), 8),

        ("TOPPADDING", (0,0), (-1,-1), 8)

    ]))

    elements.append(table)

    elements.append(PageBreak())


def generate_report(resume_data, target_role, output_path):

    doc = SimpleDocTemplate(output_path)

    elements = []

    create_cover_page(elements,resume_data,target_role)

    create_personal_info_page(elements,resume_data)

    create_skills_section(elements,resume_data)

    create_education_section(elements,resume_data)

    create_experience_section(elements,resume_data)

    create_projects_section(elements,resume_data)

    create_certifications_section(elements,resume_data)

    create_missing_skills_section(
        elements,
        resume_data,
        target_role
    )

    create_suggestions_section(
        elements,
        resume_data
    )

    doc.build(elements)

def create_education_section(elements, resume_data):

    elements.append(
        blue_heading("🎓 EDUCATION")
    )

    section_space(elements)

    for edu in resume_data["education"]:

        data = [
            ["Degree", edu["degree"]],
            ["Institution", edu["institution"]],
            ["Year", edu["year"]],
            ["CGPA", edu["cgpa"]]
        ]

        table = Table(
            data,
            colWidths=[1.7 * inch, 4.3 * inch]
        )

        table.setStyle(TableStyle([

            ("BACKGROUND", (0,0), (0,-1), HexColor("#2563EB")),
            ("TEXTCOLOR", (0,0), (0,-1), white),

            ("BACKGROUND", (1,0), (1,-1), HexColor("#F8F9FA")),

            ("GRID", (0,0), (-1,-1), 0.5, HexColor("#DDDDDD")),

            ("FONTNAME", (0,0), (-1,-1), "Helvetica-Bold"),

            ("BOTTOMPADDING", (0,0), (-1,-1), 8)

        ]))

        elements.append(table)

        section_space(elements)

def create_experience_section(elements, resume_data):

    elements.append(
        blue_heading("💼 EXPERIENCE")
    )

    section_space(elements)

    for exp in resume_data["experience"]:

        elements.append(
            Paragraph(
                f"<b>{exp['role']}</b>",
                HEADING
            )
        )

        elements.append(
            Paragraph(
                f"<b>Company:</b> {exp['company']}",
                NORMAL
            )
        )

        elements.append(
            Paragraph(
                f"<b>Duration:</b> {exp['duration']}",
                NORMAL
            )
        )

        elements.append(
            Paragraph(
                exp["description"],
                NORMAL
            )
        )

        section_space(elements)

    elements.append(PageBreak())

def create_projects_section(elements, resume_data):

    elements.append(
        blue_heading("📂 PROJECTS")
    )

    section_space(elements)

    for project in resume_data["projects"]:

        elements.append(
            Paragraph(
                f"<font color='#2563EB'><b>{project['name']}</b></font>",
                HEADING
            )
        )

        elements.append(
            Paragraph(
                f"<b>Tech Stack:</b> {project['technologies']}",
                NORMAL
            )
        )

        elements.append(
            Paragraph(
                project["description"],
                NORMAL
            )
        )

        section_space(elements)

def create_certifications_section(elements, resume_data):

    elements.append(
        blue_heading("🏆 CERTIFICATIONS")
    )

    section_space(elements)

    certs = resume_data["certifications"]

    if not certs:

        elements.append(
            Paragraph(
                "No certifications found.",
                NORMAL
            )
        )

        return

    for cert in certs:

        table = Table(
            [[cert]],
            colWidths=[6 * inch]
        )

        table.setStyle(TableStyle([

            ("BACKGROUND",(0,0),(-1,-1),HexColor("#E8F5E9")),

            ("TEXTCOLOR",(0,0),(-1,-1),HexColor("#1B5E20")),

            ("GRID",(0,0),(-1,-1),0.5,HexColor("#4CAF50")),

            ("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),

            ("BOTTOMPADDING",(0,0),(-1,-1),8),

            ("TOPPADDING",(0,0),(-1,-1),8)

        ]))

        elements.append(table)

        elements.append(Spacer(1,8))

def create_missing_skills_section(elements, resume_data, target_role):

    elements.append(
        blue_heading(f"🎯 MISSING SKILLS FOR {target_role.upper()}")
    )

    section_space(elements)

    skills = resume_data["missing_skills"]

    if not skills:

        elements.append(
            Paragraph(
                "<font color='green'><b>No major missing skills found.</b></font>",
                NORMAL
            )
        )

        return

    for skill in skills:

        table = Table(
            [[skill]],
            colWidths=[6 * inch]
        )

        table.setStyle(TableStyle([

            ("BACKGROUND",(0,0),(-1,-1),HexColor("#FFF3E0")),

            ("TEXTCOLOR",(0,0),(-1,-1),HexColor("#E65100")),

            ("GRID",(0,0),(-1,-1),0.5,HexColor("#FF9800")),

            ("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),

            ("BOTTOMPADDING",(0,0),(-1,-1),8),

            ("TOPPADDING",(0,0),(-1,-1),8)

        ]))

        elements.append(table)

        elements.append(Spacer(1,6))

def create_suggestions_section(elements, resume_data):

    if "suggestions" not in resume_data:

        return

    elements.append(
        blue_heading("💡 AI IMPROVEMENT SUGGESTIONS")
    )

    section_space(elements)

    for suggestion in resume_data["suggestions"]:

        elements.append(

            Paragraph(

                f"• {suggestion}",

                NORMAL

            )

        )

        elements.append(Spacer(1,6))
