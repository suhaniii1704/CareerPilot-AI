import re
import html

import streamlit as st

from utils.roadmap import generate_roadmap
from utils.roadmap_pdf import generate_roadmap_pdf


# =========================================================
# TEXT CLEANING
# =========================================================

def clean_text(text):

    if not text:
        return ""

    text = str(text)

    # Remove markdown artifacts
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

    # Remove accidental section labels
    text = re.sub(
        r"^\s*(SUMMARY|ROADMAP SUMMARY)\s*:?\s*$",
        "",
        text,
        flags=re.IGNORECASE | re.MULTILINE
    )

    return text.strip()


# =========================================================
# HTML BODY FORMATTER
# =========================================================

def format_body(text):

    text = clean_text(text)

    if not text:
        return ""

    # Escape HTML from AI output
    text = html.escape(text)

    lines = text.split("\n")

    formatted = []

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # Bullet point
        if line.startswith("- "):
            content = line[2:].strip()

            formatted.append(
                "<div style='margin:7px 0;'>• "
                + content
                + "</div>"
            )

        elif line.startswith("• "):
            content = line[2:].strip()

            formatted.append(
                "<div style='margin:7px 0;'>• "
                + content
                + "</div>"
            )

        else:
            formatted.append(
                "<div style='margin:6px 0;'>"
                + line
                + "</div>"
            )

    return "".join(formatted)

# =========================================================
# CARD
# =========================================================

def render_card(title, body, color, icon):

    if not body or not body.strip():
        return

    body_html = format_body(body)

    st.markdown(
        f"""
        <div style="
        background:#111827;
        border:1px solid {color};
        border-radius:16px;
        padding:22px;
        margin:0 0 18px 0;
        color:white;
        box-sizing:border-box;
        ">

        <div style="
        color:{color};
        font-size:20px;
        font-weight:800;
        margin-bottom:16px;
        ">
        {icon} {title}
        </div>

        <div style="
        color:#f3f4f6;
        font-size:16px;
        line-height:1.7;
        ">
        {body_html}
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# ROADMAP PARSER
# =========================================================

def parse_roadmap(roadmap):

    roadmap = str(roadmap)

    roadmap = roadmap.replace(
        "\r\n",
        "\n"
    )

    roadmap = roadmap.strip()

    sections = {
        "summary": "",
        "weeks": [],
        "gaps": "",
        "project": ""
    }

    # -----------------------------------------------------
    # Find WEEK headings dynamically
    #
    # Supports:
    #
    # WEEK 1:
    # ### WEEK 1:
    # WEEK 12:
    # ### WEEK 24:
    # -----------------------------------------------------

    week_pattern = re.compile(
        r"(?im)^\s*#{0,6}\s*WEEK\s+(\d+)\s*:?\s*$"
    )

    matches = list(
        week_pattern.finditer(roadmap)
    )

    # -----------------------------------------------------
    # Find KEY GAPS
    # -----------------------------------------------------

    gaps_pattern = re.compile(
        r"(?im)^\s*#{0,6}\s*KEY\s+GAPS\s*:?\s*$"
    )

    gaps_match = gaps_pattern.search(roadmap)

    # -----------------------------------------------------
    # Find FINAL PROJECT
    # -----------------------------------------------------

    project_pattern = re.compile(
        r"(?im)^\s*#{0,6}\s*FINAL\s+PROJECT\s*:?\s*$"
    )

    project_match = project_pattern.search(roadmap)

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    first_section_positions = []

    if matches:
        first_section_positions.append(
            matches[0].start()
        )

    if gaps_match:
        first_section_positions.append(
            gaps_match.start()
        )

    if project_match:
        first_section_positions.append(
            project_match.start()
        )

    if first_section_positions:

        first_position = min(
            first_section_positions
        )

        summary = roadmap[:first_position]

    else:

        summary = roadmap

    sections["summary"] = clean_text(summary)

    # -----------------------------------------------------
    # WEEK CARDS
    # -----------------------------------------------------

    for index, match in enumerate(matches):

        week_number = int(
            match.group(1)
        )

        start = match.end()

        # End at next week
        end_candidates = []

        if index + 1 < len(matches):

            end_candidates.append(
                matches[index + 1].start()
            )

        # End at KEY GAPS
        if gaps_match and gaps_match.start() > start:

            end_candidates.append(
                gaps_match.start()
            )

        # End at FINAL PROJECT
        if project_match and project_match.start() > start:

            end_candidates.append(
                project_match.start()
            )

        if end_candidates:

            end = min(
                end_candidates
            )

        else:

            end = len(roadmap)

        content = roadmap[start:end].strip()

        if content:

            sections["weeks"].append(
                {
                    "number": week_number,
                    "content": clean_text(content)
                }
            )

    # -----------------------------------------------------
    # KEY GAPS
    # -----------------------------------------------------

    if gaps_match:

        gaps_start = gaps_match.end()

        if project_match and project_match.start() > gaps_start:

            gaps_end = project_match.start()

        else:

            gaps_end = len(roadmap)

        sections["gaps"] = clean_text(
            roadmap[gaps_start:gaps_end]
        )

    # -----------------------------------------------------
    # FINAL PROJECT
    # -----------------------------------------------------

    if project_match:

        project_start = project_match.end()

        sections["project"] = clean_text(
            roadmap[project_start:]
        )

    return sections


# =========================================================
# MAIN SHOW FUNCTION
# =========================================================

def show():

    st.title("🧠 AI Career Roadmap")

    # -----------------------------------------------------
    # Resume requirement
    # -----------------------------------------------------

    if st.session_state.resume_data is None:

        st.warning(
            "⚠️ Please analyze your resume first."
        )

        return

    st.info(
        f"📄 Using analyzed resume for: "
        f"{st.session_state.target_role}"
    )

    # -----------------------------------------------------
    # Session state
    # -----------------------------------------------------

    if "roadmap_result" not in st.session_state:

        st.session_state.roadmap_result = None

    if "roadmap_role" not in st.session_state:

        st.session_state.roadmap_role = ""

    if "roadmap_level" not in st.session_state:

        st.session_state.roadmap_level = ""

    if "roadmap_duration" not in st.session_state:

        st.session_state.roadmap_duration = ""

    # -----------------------------------------------------
    # Target role
    # -----------------------------------------------------

    target_role = st.selectbox(
        "Choose your target role",
        [
            "Data Analyst",
            "Data Scientist",
            "Machine Learning Engineer",
            "AI Engineer",
            "Backend Developer",
            "Full Stack Developer",
            "Software Engineer"
        ]
    )

    # -----------------------------------------------------
    # Current level
    # -----------------------------------------------------

    level = st.radio(
        "Current level",
        [
            "Beginner",
            "Intermediate",
            "Advanced"
        ],
        horizontal=True
    )

    # -----------------------------------------------------
    # Duration
    # -----------------------------------------------------

    duration = st.radio(
        "Time available",
        [
            "1 Month",
            "3 Months",
            "6 Months"
        ],
        horizontal=True
    )

    # Show what duration means
    duration_weeks = {
        "1 Month": 4,
        "3 Months": 12,
        "6 Months": 24
    }

    st.caption(
        f"📅 Your roadmap will contain "
        f"**{duration_weeks[duration]} weekly milestones**."
    )

    # -----------------------------------------------------
    # Generate
    # -----------------------------------------------------

    if st.button(
        "🚀 Generate Roadmap",
        use_container_width=True
    ):

        with st.spinner(
            f"Creating your {duration} personalized roadmap..."
        ):

            roadmap = generate_roadmap(
                st.session_state.resume_data,
                target_role,
                level,
                duration
            )

            # Handle Gemini content parts
            if isinstance(roadmap, list):

                roadmap = "".join(
                    part.get("text", "")
                    for part in roadmap
                    if isinstance(part, dict)
                )

            st.session_state.roadmap_result = roadmap

            st.session_state.roadmap_role = (
                target_role
            )

            st.session_state.roadmap_level = (
                level
            )

            st.session_state.roadmap_duration = (
                duration
            )

            st.rerun()

    # =====================================================
    # DISPLAY ROADMAP
    # =====================================================

    if st.session_state.roadmap_result is not None:

        roadmap = st.session_state.roadmap_result

        sections = parse_roadmap(
            roadmap
        )

        st.subheader(
            "📋 Personalized Career Roadmap"
        )

        # =================================================
        # MAIN REPORT CONTAINER
        # =================================================

        with st.container(border=True):

            # ---------------------------------------------
            # TARGET ROLE CARD
            # ---------------------------------------------

            st.markdown(
                f"""
                <div style="
                background:#111827;
                border:1px solid #374151;
                border-radius:16px;
                padding:24px;
                margin-bottom:18px;
                color:white;
                text-align:center;
                ">

                <div style="
                color:#60a5fa;
                font-size:17px;
                font-weight:700;
                ">
                🎯 TARGET ROLE
                </div>

                <div style="
                font-size:30px;
                font-weight:800;
                margin-top:7px;
                ">
                        {html.escape(
                            st.session_state.roadmap_role
                        )}
                    </div>

                <div style="
                color:#9ca3af;
                margin-top:8px;
                font-size:16px;
                ">
                        {html.escape(
                            st.session_state.roadmap_level
                        )}
                        &nbsp;•&nbsp;
                        {html.escape(
                            st.session_state.roadmap_duration
                        )}
                </div>

                </div>
                """,
                unsafe_allow_html=True
            )

            # ---------------------------------------------
            # SUMMARY
            # ---------------------------------------------

            render_card(
                "ROADMAP SUMMARY",
                sections["summary"],
                "#3b82f6",
                "📝"
            )

            # ---------------------------------------------
            # DYNAMIC WEEK CARDS
            # ---------------------------------------------

            for week in sections["weeks"]:

                render_card(
                    f"WEEK {week['number']}",
                    week["content"],
                    "#8b5cf6",
                    "📅"
                )

            # ---------------------------------------------
            # KEY GAPS
            # ---------------------------------------------

            render_card(
                "KEY GAPS",
                sections["gaps"],
                "#ef4444",
                "⚠️"
            )

            # ---------------------------------------------
            # FINAL PROJECT
            # ---------------------------------------------

            render_card(
                "FINAL PROJECT",
                sections["project"],
                "#06b6d4",
                "🚀"
            )

        # =================================================
        # PDF
        # =================================================

        pdf_bytes = generate_roadmap_pdf(
            st.session_state.roadmap_role,
            st.session_state.roadmap_level,
            st.session_state.roadmap_duration,
            st.session_state.roadmap_result
        )

        st.download_button(
            label="📥 Download Roadmap (PDF)",
            data=pdf_bytes,
            file_name="CareerPilot_Career_Roadmap.pdf",
            mime="application/pdf",
            use_container_width=True
        )

        # =================================================
        # CLEAR
        # =================================================

        if st.button(
            "🗑️ Clear Roadmap",
            use_container_width=True
        ):

            st.session_state.roadmap_result = None
            st.session_state.roadmap_role = ""
            st.session_state.roadmap_level = ""
            st.session_state.roadmap_duration = ""

            st.rerun()