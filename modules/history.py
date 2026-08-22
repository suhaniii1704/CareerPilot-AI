import streamlit as st
import json
from datetime import datetime

from utils.database import (
    # Resume Analysis
    get_user_analyses,
    get_analysis_by_id,
    delete_analysis,

    # Interviews
    get_user_interviews,
    get_interview_by_id,
    delete_interview,

    # Job Matches
    get_user_job_matches,
    get_job_match_by_id,
    delete_job_match,

    # Career Roadmaps
    get_user_roadmaps,
    get_roadmap_by_id,
    delete_roadmap
)


# =====================================================
# CONFIGURATION
# =====================================================

RECORDS_PER_PAGE = 10


# =====================================================
# PAGINATION
# =====================================================

def get_paginated_records(records, page_key):

    if page_key not in st.session_state:
        st.session_state[page_key] = 0

    total_records = len(records)

    total_pages = max(
        1,
        (total_records + RECORDS_PER_PAGE - 1)
        // RECORDS_PER_PAGE
    )

    current_page = st.session_state[page_key]

    if current_page >= total_pages:
        current_page = total_pages - 1
        st.session_state[page_key] = current_page

    start = current_page * RECORDS_PER_PAGE
    end = start + RECORDS_PER_PAGE

    return records[start:end], current_page, total_pages


def show_pagination(page_key, current_page, total_pages):

    if total_pages <= 1:
        return

    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button(
            "← Previous",
            key=f"{page_key}_previous",
            disabled=current_page == 0,
            use_container_width=True
        ):
            st.session_state[page_key] -= 1
            st.rerun()

    with col2:
        st.markdown(
            f"""
            <div style="text-align:center; padding-top:8px;">
                Page {current_page + 1} of {total_pages}
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        if st.button(
            "Next →",
            key=f"{page_key}_next",
            disabled=current_page >= total_pages - 1,
            use_container_width=True
        ):
            st.session_state[page_key] += 1
            st.rerun()


# =====================================================
# JOB MATCH HISTORY
# =====================================================

def show_job_match_history():

    st.subheader("📊 Job Match History")

    if st.button(
        "← Back to My History",
        key="back_job_match"
    ):
        st.session_state.history_category = None
        st.session_state.selected_job_match_id = None
        st.rerun()

    matches = get_user_job_matches(
        st.session_state.user_id
    )

    if not matches:
        st.info("No Job Match analyses found yet.")
        return

    st.markdown("### Previous Job Matches")

    page_matches, current_page, total_pages = (
        get_paginated_records(
            matches,
            "job_match_page"
        )
    )

    for match in page_matches:

        match_id, target_role, score, created_at = match

        with st.container(border=True):

            st.markdown(f"### 🎯 {target_role}")

            st.write(f"**Match Score:** {score}/100")

            st.caption(
                f"Created: {datetime.fromisoformat(created_at).strftime('%d %b %Y, %I:%M %p')}"
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "👁️ View Report",
                    key=f"view_match_{match_id}",
                    use_container_width=True
                ):
                    st.session_state.selected_job_match_id = match_id
                    st.rerun()

            with col2:
                if st.button(
                    "🗑️ Delete",
                    key=f"delete_match_{match_id}",
                    use_container_width=True
                ):
                    delete_job_match(
                        st.session_state.user_id,
                        match_id
                    )

                    if (
                        st.session_state.get(
                            "selected_job_match_id"
                        ) == match_id
                    ):
                        st.session_state.selected_job_match_id = None

                    st.rerun()

        # INLINE REPORT
        if (
            st.session_state.get(
                "selected_job_match_id"
            ) == match_id
        ):

            record = get_job_match_by_id(
                st.session_state.user_id,
                match_id
            )

            if record:

                (
                    _,
                    report_role,
                    _,
                    report_score,
                    result,
                    _
                ) = record

                with st.container(border=True):

                    col1, col2 = st.columns([4, 1])

                    with col1:
                        st.subheader(
                            f"📋 {report_role} — Job Match Report"
                        )

                    with col2:
                        if st.button(
                            "✕ Close",
                            key=f"close_match_{match_id}",
                            use_container_width=True
                        ):
                            st.session_state.selected_job_match_id = None
                            st.rerun()

                    st.metric(
                        "Match Score",
                        f"{report_score}/100"
                    )

                    st.markdown(result)

    show_pagination(
        "job_match_page",
        current_page,
        total_pages
    )


# =====================================================
# INTERVIEW HISTORY
# =====================================================

def show_interview_history():

    st.subheader("🎯 Interview History")

    if st.button(
        "← Back to My History",
        key="back_interview"
    ):
        st.session_state.history_category = None
        st.session_state.selected_interview_id = None
        st.rerun()

    interviews = get_user_interviews(
        st.session_state.user_id
    )

    if not interviews:
        st.info("No interview history found yet.")
        return

    st.markdown("### Previous Interviews")

    page_interviews, current_page, total_pages = (
        get_paginated_records(
            interviews,
            "interview_page"
        )
    )

    for interview in page_interviews:

        interview_id, target_role, created_at = interview

        with st.container(border=True):

            st.markdown(f"### 🎯 {target_role}")

            st.caption(
                f"Created: {datetime.fromisoformat(created_at).strftime('%d %b %Y, %I:%M %p')}"
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "👁️ View Report",
                    key=f"view_interview_{interview_id}",
                    use_container_width=True
                ):
                    st.session_state.selected_interview_id = interview_id
                    st.rerun()

            with col2:
                if st.button(
                    "🗑️ Delete",
                    key=f"delete_interview_{interview_id}",
                    use_container_width=True
                ):
                    delete_interview(
                        st.session_state.user_id,
                        interview_id
                    )

                    if (
                        st.session_state.get(
                            "selected_interview_id"
                        ) == interview_id
                    ):
                        st.session_state.selected_interview_id = None

                    st.rerun()

        # INLINE REPORT
        if (
            st.session_state.get(
                "selected_interview_id"
            ) == interview_id
        ):

            record = get_interview_by_id(
                st.session_state.user_id,
                interview_id
            )

            if record:

                (
                    _,
                    report_role,
                    _,
                    final_report,
                    created_at
                ) = record

                with st.container(border=True):

                    col1, col2 = st.columns([4, 1])

                    with col1:
                        st.subheader(
                            f"📋 {report_role} — Interview Report"
                        )

                    with col2:
                        if st.button(
                            "✕ Close",
                            key=f"close_interview_{interview_id}",
                            use_container_width=True
                        ):
                            st.session_state.selected_interview_id = None
                            st.rerun()

                    st.caption(
                        f"Completed: {datetime.fromisoformat(created_at).strftime('%d %b %Y, %I:%M %p')}"
                    )

                    st.markdown(final_report)

    show_pagination(
        "interview_page",
        current_page,
        total_pages
    )


# =====================================================
# RESUME ANALYSIS HISTORY
# =====================================================

def show_resume_history():

    st.subheader("📄 Resume Analysis History")

    if st.button(
        "← Back to My History",
        key="back_resume"
    ):
        st.session_state.history_category = None
        st.session_state.selected_analysis_id = None
        st.rerun()

    analyses = get_user_analyses(
        st.session_state.user_id
    )

    if not analyses:
        st.info("No resume analyses found yet.")
        return

    st.markdown("### Previous Resume Analyses")

    page_analyses, current_page, total_pages = (
        get_paginated_records(
            analyses,
            "resume_page"
        )
    )

    for analysis in page_analyses:

        analysis_id, target_role, ats_score, created_at = analysis

        with st.container(border=True):

            st.markdown(f"### 📄 {target_role}")

            st.write(
                f"**ATS Score:** {ats_score}/100"
            )

            st.caption(
                f"Created: {datetime.fromisoformat(created_at).strftime('%d %b %Y, %I:%M %p')}"
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "👁️ View Analysis",
                    key=f"view_analysis_{analysis_id}",
                    use_container_width=True
                ):
                    st.session_state.selected_analysis_id = analysis_id
                    st.rerun()

            with col2:
                if st.button(
                    "🗑️ Delete",
                    key=f"delete_analysis_{analysis_id}",
                    use_container_width=True
                ):
                    delete_analysis(
                        st.session_state.user_id,
                        analysis_id
                    )

                    if (
                        st.session_state.get(
                            "selected_analysis_id"
                        ) == analysis_id
                    ):
                        st.session_state.selected_analysis_id = None

                    st.rerun()

        # INLINE ANALYSIS
        if (
            st.session_state.get(
                "selected_analysis_id"
            ) == analysis_id
        ):

            record = get_analysis_by_id(
                st.session_state.user_id,
                analysis_id
            )

            if record:

                (
                    _,
                    report_role,
                    report_score,
                    resume_json,
                    _
                ) = record

                with st.container(border=True):

                    col1, col2 = st.columns([4, 1])

                    with col1:
                        st.subheader(
                            f"📋 {report_role} — Resume Analysis"
                        )

                    with col2:
                        if st.button(
                            "✕ Close",
                            key=f"close_analysis_{analysis_id}",
                            use_container_width=True
                        ):
                            st.session_state.selected_analysis_id = None
                            st.rerun()

                    # -----------------------------------------
                    # LOAD SAVED RESUME DATA
                    # -----------------------------------------

                    try:

                        resume_data = json.loads(resume_json)

                        # ATS SCORE
                        st.metric(
                            "⭐ ATS Score",
                            f"{report_score}/100"
                        )

                        st.divider()

                        # -------------------------------------
                        # PERSONAL INFORMATION
                        # -------------------------------------

                        st.markdown(
                            "### 👤 Personal Information"
                        )

                        personal_info = resume_data.get(
                            "personal_information",
                            {}
                        )

                        col1, col2 = st.columns(2)

                        with col1:

                            st.write(
                                f"**Name:** {personal_info.get('name', 'Not Found')}"
                            )

                            st.write(
                                f"**Email:** {personal_info.get('email', 'Not Found')}"
                            )

                            st.write(
                                f"**Phone:** {personal_info.get('phone', 'Not Found')}"
                            )

                        with col2:

                            st.write(
                                f"**LinkedIn:** {personal_info.get('linkedin', 'Not Found')}"
                            )

                            st.write(
                                f"**GitHub:** {personal_info.get('github', 'Not Found')}"
                            )

                        st.divider()

                        # -------------------------------------
                        # TECHNICAL SKILLS
                        # -------------------------------------

                        st.markdown(
                            "### 🛠 Technical Skills"
                        )

                        skills = resume_data.get(
                            "skills",
                            []
                        )

                        if skills:
                            st.write(" • ".join(skills))
                        else:
                            st.info(
                                "No skills found."
                            )

                        st.divider()

                        # -------------------------------------
                        # EDUCATION
                        # -------------------------------------

                        st.markdown(
                            "### 🎓 Education"
                        )

                        education = resume_data.get(
                            "education",
                            []
                        )

                        if education:

                            for edu in education:

                                with st.container(border=True):

                                    st.write(
                                        f"**Degree:** {edu.get('degree', 'Not Found')}"
                                    )

                                    st.write(
                                        f"**Institution:** {edu.get('institution', 'Not Found')}"
                                    )

                                    st.write(
                                        f"**Year:** {edu.get('year', 'Not Found')}"
                                    )

                                    st.write(
                                        f"**CGPA:** {edu.get('cgpa', 'Not Found')}"
                                    )

                        else:
                            st.info(
                                "No education information found."
                            )

                        st.divider()

                        # -------------------------------------
                        # EXPERIENCE
                        # -------------------------------------

                        st.markdown(
                            "### 💼 Experience"
                        )

                        experience = resume_data.get(
                            "experience",
                            []
                        )

                        if experience:

                            for exp in experience:

                                with st.container(border=True):

                                    st.write(
                                        f"**Role:** {exp.get('role', 'Not Found')}"
                                    )

                                    st.write(
                                        f"**Company:** {exp.get('company', 'Not Found')}"
                                    )

                                    st.write(
                                        f"**Duration:** {exp.get('duration', 'Not Found')}"
                                    )

                                    st.write(
                                        f"**Description:** {exp.get('description', 'Not Found')}"
                                    )

                        else:
                            st.info(
                                "No experience information found."
                            )

                        st.divider()

                        # -------------------------------------
                        # PROJECTS
                        # -------------------------------------

                        st.markdown(
                            "### 📂 Projects"
                        )

                        projects = resume_data.get(
                            "projects",
                            []
                        )

                        if projects:

                            for project in projects:

                                with st.container(border=True):

                                    st.write(
                                        f"**Project:** {project.get('name', 'Not Found')}"
                                    )

                                    technologies = project.get(
                                        "technologies",
                                        "Not Found"
                                    )

                                    if isinstance(
                                        technologies,
                                        list
                                    ):
                                        technologies = (
                                            ", ".join(
                                                technologies
                                            )
                                        )

                                    st.write(
                                        f"**Technologies:** {technologies}"
                                    )

                                    st.write(
                                        f"**Description:** {project.get('description', 'Not Found')}"
                                    )

                        else:
                            st.info(
                                "No projects found."
                            )

                        st.divider()

                        # -------------------------------------
                        # CERTIFICATIONS
                        # -------------------------------------

                        st.markdown(
                            "### 🏆 Certifications"
                        )

                        certifications = resume_data.get(
                            "certifications",
                            []
                        )

                        if certifications:

                            for cert in certifications:

                                st.success(
                                    f"✓ {cert}"
                                )

                        else:
                            st.info(
                                "No certifications found."
                            )

                        st.divider()

                        # -------------------------------------
                        # MISSING SKILLS
                        # -------------------------------------

                        st.markdown(
                            f"### 🎯 Missing Skills for {report_role}"
                        )

                        missing_skills = resume_data.get(
                            "missing_skills",
                            []
                        )

                        if missing_skills:

                            for skill in missing_skills:

                                st.warning(
                                    f"• {skill}"
                                )

                        else:

                            st.success(
                                "No major missing skills found."
                            )

                        st.divider()

                        # -------------------------------------
                        # AI SUGGESTIONS
                        # -------------------------------------

                        st.markdown(
                            "### 💡 AI Improvement Suggestions"
                        )

                        suggestions = resume_data.get(
                            "suggestions",
                            []
                        )

                        if suggestions:

                            for suggestion in suggestions:

                                st.info(
                                    f"💡 {suggestion}"
                                )

                        else:

                            st.info(
                                "No suggestions available."
                            )

                    except Exception as e:

                        st.error(
                            "Could not load this saved analysis."
                        )

    show_pagination(
        "resume_page",
        current_page,
        total_pages
    )


# =====================================================
# CAREER ROADMAP HISTORY
# =====================================================

def show_roadmap_history():

    st.subheader("🗺️ Career Roadmap History")

    if st.button(
        "← Back to My History",
        key="back_roadmap"
    ):
        st.session_state.history_category = None
        st.session_state.selected_roadmap_id = None
        st.rerun()

    roadmaps = get_user_roadmaps(
        st.session_state.user_id
    )

    if not roadmaps:
        st.info("No career roadmaps found yet.")
        return

    st.markdown("### Previous Career Roadmaps")

    page_roadmaps, current_page, total_pages = (
        get_paginated_records(
            roadmaps,
            "roadmap_page"
        )
    )

    for roadmap in page_roadmaps:

        (
            roadmap_id,
            target_role,
            current_level,
            duration,
            created_at
        ) = roadmap

        with st.container(border=True):

            st.markdown(
                f"### 🗺️ {target_role}"
            )

            st.write(
                f"**Current Level:** {current_level}"
            )

            st.write(
                f"**Duration:** {duration}"
            )

            st.caption(
                f"Created: {datetime.fromisoformat(created_at).strftime('%d %b %Y, %I:%M %p')}"
            )

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "👁️ View Roadmap",
                    key=f"view_roadmap_{roadmap_id}",
                    use_container_width=True
                ):
                    st.session_state.selected_roadmap_id = roadmap_id
                    st.rerun()

            with col2:

                if st.button(
                    "🗑️ Delete",
                    key=f"delete_roadmap_{roadmap_id}",
                    use_container_width=True
                ):
                    delete_roadmap(
                        st.session_state.user_id,
                        roadmap_id
                    )

                    if (
                        st.session_state.get(
                            "selected_roadmap_id"
                        ) == roadmap_id
                    ):
                        st.session_state.selected_roadmap_id = None

                    st.rerun()

        # INLINE ROADMAP
        if (
            st.session_state.get(
                "selected_roadmap_id"
            ) == roadmap_id
        ):

            record = get_roadmap_by_id(
                st.session_state.user_id,
                roadmap_id
            )

            if record:

                (
                    _,
                    report_role,
                    report_level,
                    report_duration,
                    roadmap_result,
                    _
                ) = record

                with st.container(border=True):

                    col1, col2 = st.columns([4, 1])

                    with col1:

                        st.subheader(
                            f"🗺️ {report_role} — Career Roadmap"
                        )

                    with col2:

                        if st.button(
                            "✕ Close",
                            key=f"close_roadmap_{roadmap_id}",
                            use_container_width=True
                        ):
                            st.session_state.selected_roadmap_id = None
                            st.rerun()

                    st.write(
                        f"**Current Level:** {report_level}"
                    )

                    st.write(
                        f"**Duration:** {report_duration}"
                    )

                    st.divider()

                    st.markdown(
                        roadmap_result
                    )

    show_pagination(
        "roadmap_page",
        current_page,
        total_pages
    )


# =====================================================
# MAIN HISTORY PAGE
# =====================================================

def show_history():

    if "history_category" not in st.session_state:
        st.session_state.history_category = None

    # CATEGORY ROUTING

    if st.session_state.history_category == "job_match":
        show_job_match_history()
        return

    if st.session_state.history_category == "interview":
        show_interview_history()
        return

    if st.session_state.history_category == "resume":
        show_resume_history()
        return

    if st.session_state.history_category == "roadmap":
        show_roadmap_history()
        return

    # MAIN HISTORY MENU

    st.title("🕘 My History")

    st.write(
        "Access and manage your previous CareerPilot AI activities."
    )

    st.divider()

    st.subheader(
        "Choose a category"
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "📄 Resume Analysis",
            use_container_width=True
        ):
            st.session_state.history_category = "resume"
            st.rerun()

        if st.button(
            "📊 Job Matches",
            use_container_width=True
        ):
            st.session_state.history_category = "job_match"
            st.rerun()

    with col2:

        if st.button(
            "🎯 Interviews",
            use_container_width=True
        ):
            st.session_state.history_category = "interview"
            st.rerun()

        if st.button(
            "🗺️ Career Roadmaps",
            use_container_width=True
        ):
            st.session_state.history_category = "roadmap"
            st.rerun()