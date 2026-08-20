import streamlit as st

from utils.job_match import analyze_job_match
from utils.job_match_pdf import generate_job_match_pdf


def show():

    st.title("📊 AI Job Match")

    # Initialize session state
    if "job_match_result" not in st.session_state:
        st.session_state.job_match_result = None

    if "job_match_score" not in st.session_state:
        st.session_state.job_match_score = None

    if "job_match_jd" not in st.session_state:
        st.session_state.job_match_jd = ""

    if st.session_state.resume_data is None:
        st.warning("⚠ Please analyze your resume first.")
        return

    target_role = st.session_state.target_role

    st.info(f"🎯 Resume analyzed for: {target_role}")

    if (st.session_state.job_match_jd
        and "job_match_jd_input" not in st.session_state):
        st.session_state.job_match_jd_input = st.session_state.job_match_jd

    jd = st.text_area(
        "Paste the Job Description",
        height=300,
        placeholder="Paste the internship or job description here...",
        key="job_match_jd_input"

    )

    # Analyze button
    if st.button("🚀 Analyze Match", use_container_width=True):

        if not jd.strip():
            st.warning("Please paste a job description.")
            return

        with st.spinner("Analyzing match..."):

            result = analyze_job_match(
                st.session_state.resume_data,
                jd
            )

            # Convert Gemini content parts to plain text
            if isinstance(result, list):
                result = "".join(
                    part.get("text", "") for part in result
                )

                # Extract score
                score = "0"
                for line in result.split("\n"):
                    if line.strip().startswith("MATCH SCORE:"):
                        score_text = line.replace("MATCH SCORE:", "").strip()
                         # Extract only the numeric score
                        import re
                        match = re.search(r"\d{1,3}", score_text)

                        if match:
                            score = match.group(0)

                        break

           

            # Save in session
            st.session_state.job_match_result = result
            st.session_state.job_match_jd = st.session_state.job_match_jd_input
            st.session_state.job_match_score = score

            st.rerun()

    # Clear button
    if st.session_state.job_match_result is not None:

        if st.button("🗑️ Clear Report", use_container_width=True):

            st.session_state.job_match_result = None
            st.session_state.job_match_jd = ""
            st.session_state.job_match_score = None

            st.rerun()

    # Render saved report
    if st.session_state.job_match_result is not None:

        result = st.session_state.job_match_result
        score = st.session_state.job_match_score or "0"

        report_body = "\n".join(
            line for line in result.split("\n")
            if not line.startswith("MATCH SCORE:")
        )

        st.subheader("📋 Job Match Report")

        with st.container(border=True):

            # Highlighted score
            st.markdown(
                f"""
                <div style="text-align:center;padding:10px 0 20px 0;">
                <div style="color:#60a5fa;font-size:18px;font-weight:700;">
                    MATCH SCORE
                </div>

                <div style="margin-top:8px;">
                    <span style="color:#3b82f6;font-size:56px;font-weight:800;">
                        {score}
                    </span>
                <span style="color:#9ca3af;font-size:24px;">/100</span>
                </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.divider()

            # Report body
            st.markdown(report_body)

            st.divider()

            # PDF download
            pdf_bytes = generate_job_match_pdf(
                target_role,st.session_state.job_match_jd,
                result
            )

            st.download_button(
                label="📥 Download Job Match Report (PDF)",
                data=pdf_bytes,
                file_name="CareerPilot_Job_Match_Report.pdf",
                mime="application/pdf",
                use_container_width=True
            )