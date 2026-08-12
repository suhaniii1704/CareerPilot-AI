import streamlit as st

from utils.roadmap import generate_roadmap
from utils.roadmap_pdf import generate_roadmap_pdf


def show():

    st.title("🧠 AI Career Roadmap")

    if st.session_state.resume_data is None:

        st.warning("⚠ Please analyze your resume first.")

        return

    st.info(
        f"📄 Using analyzed resume for: {st.session_state.target_role}"
    )

    # Initialize session state
    if "roadmap_result" not in st.session_state:
        st.session_state.roadmap_result = None

    if "roadmap_role" not in st.session_state:
        st.session_state.roadmap_role = ""

    if "roadmap_level" not in st.session_state:
        st.session_state.roadmap_level = ""

    if "roadmap_duration" not in st.session_state:
        st.session_state.roadmap_duration = ""

    # Inputs
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

    level = st.radio(
        "Current level",
        ["Beginner", "Intermediate", "Advanced"],
        horizontal=True
    )

    duration = st.radio(
        "Time available",
        ["1 Month", "3 Months", "6 Months"],
        horizontal=True
    )

    # Generate roadmap
    if st.button("🚀 Generate Roadmap", use_container_width=True):

        with st.spinner("Creating personalized roadmap..."):

            roadmap = generate_roadmap(
                st.session_state.resume_data,
                target_role,
                level,
                duration
            )

            if isinstance(roadmap, list):

                roadmap = "".join(
                    part.get("text", "")
                    for part in roadmap
                )

            st.session_state.roadmap_result = roadmap
            st.session_state.roadmap_role = target_role
            st.session_state.roadmap_level = level
            st.session_state.roadmap_duration = duration

            st.rerun()

    # Render roadmap
    if st.session_state.roadmap_result is not None:

        roadmap = st.session_state.roadmap_result
        summary = roadmap.split("### WEEK 1-2:")[0]

        week12 = ""
        week34 = ""
        week56 = ""
        week78 = ""
        gaps = ""
        project = ""

        if "### WEEK 1-2:" in roadmap:
            week12 = roadmap.split("### WEEK 1-2:")[1]

        if "### WEEK 3-4:" in week12:
            week34 = week12.split("### WEEK 3-4:")[1]
            week12 = week12.split("### WEEK 3-4:")[0]

        if "### WEEK 5-6:" in week34:
            week56 = week34.split("### WEEK 5-6:")[1]
            week34 = week34.split("### WEEK 5-6:")[0]

        if "### WEEK 7-8:" in week56:
             week78 = week56.split("### WEEK 7-8:")[1]
             week56 = week56.split("### WEEK 7-8:")[0]

        if "### KEY GAPS:" in week78:
            gaps = week78.split("### KEY GAPS:")[1]
            week78 = week78.split("### KEY GAPS:")[0]

        if "### FINAL PROJECT:" in week78:
           project = week78.split("### FINAL PROJECT:")[1]
           gaps = week78.split("### FINAL PROJECT:")[0]

        st.subheader("📋 Personalized Career Roadmap")

        # Main container
        with st.container(border=True):

            # Header box
             st.markdown(f"""
             <div style="background:#111827;border:1px solid #374151;border-radius:16px;padding:24px;margin-bottom:18px;color:white;text-align:center;">

             <div style="color:#60a5fa;font-size:18px;font-weight:700;">TARGET ROLE</div>
             
             <div style="font-size:28px;font-weight:800;margin-top:6px;">{st.session_state.roadmap_role}</div>
            
             <div style="color:#9ca3af;margin-top:6px;">{st.session_state.roadmap_level} • {st.session_state.roadmap_duration}</div>
             </div>
             """,
            unsafe_allow_html=True
            )

            # Summary box
             st.markdown(f"""
             <div style="background:#0f172a;border:1px solid #2563eb;border-radius:16px;padding:22px;margin-bottom:18px;color:white;">
             <div style="color:#60a5fa;font-size:18px;font-weight:700;margin-bottom:10px;">📝 ROADMAP SUMMARY</div>
             {summary.replace('***', '')
              .replace('**', '')
              .replace(chr(10), '<br>').replace('---','').replace('###','')}
            </div>
            """,
            unsafe_allow_html=True
            )

             def card(title, body, color, icon):
                 st.markdown(f"""
                <div style="background:#111827;border:1px solid {color};border-radius:16px;padding:22px;margin-bottom:18px;color:white;">
                <div style="color:{color};font-size:20px;font-weight:800;margin-bottom:12px;">{icon} {title}</div>
                {body.replace('***', '').replace('**', '').replace(chr(10), '<br>').replace('---','')}
                </div>
                """,
                unsafe_allow_html=True
                )

             if week12:
                card("WEEK 1-2", week12, "#8b5cf6", "📅")

             if week34:
               card("WEEK 3-4", week34, "#8b5cf6", "📅")

             if week56:
               card("WEEK 5-6", week56, "#8b5cf6", "📅")

             if week78:
               card("WEEK 7-8", week78, "#8b5cf6", "📅")

             if gaps:
                card("KEY GAPS", gaps, "#ef4444", "⚠️")

             if project:
                card("FINAL PROJECT", project, "#06b6d4", "🚀")

        # PDF
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

        # Clear
        if st.button("🗑️ Clear Roadmap", use_container_width=True):

            st.session_state.roadmap_result = None
            st.session_state.roadmap_role = ""
            st.session_state.roadmap_level = ""
            st.session_state.roadmap_duration = ""

            st.rerun()