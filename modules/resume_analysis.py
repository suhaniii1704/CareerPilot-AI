import streamlit as st
from pathlib import Path

from utils.resume_reader import extract_text
from utils.file_handler import save_resume
from utils.gemini_parser import parse_resume_ai
from utils.vector_store import create_vector_store
from utils.pdf_report import generate_report
from utils.database import save_analysis


BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)



def show():
    st.title("📄 Resume Analysis")
    st.write("Upload your resume to begin analysis.")

    # Initialize session state
    if "resume_path" not in st.session_state:
        st.session_state.resume_path = ""

    uploaded_file = st.file_uploader(
        "Choose your Resume",
        type=["pdf", "docx"]
    )

    # Upload Resume
    if uploaded_file is not None:

        save_path = save_resume(uploaded_file, UPLOAD_DIR)

        st.session_state.resume_path = str(save_path)
        st.session_state.uploaded_file_name = uploaded_file.name

        st.success("✅ Resume uploaded successfully!")

    # Show uploaded file name even after switching tabs
    if st.session_state.uploaded_file_name:

        st.write("**📄 File Name**")
        st.success(st.session_state.uploaded_file_name)

    st.subheader("🎯 Job Preferences")

    target_role = st.text_input(
        "Target Job Role",
        value=st.session_state.target_role,
        placeholder="Example: Data Scientist"
    )

    # Analyze Button
    if st.button("🚀 Analyze Resume", use_container_width=True):

        if st.session_state.resume_path == "":

            st.error("Please upload a resume first.")

        else:

            with st.spinner("AI is analyzing your resume..."):

                resume_text = extract_text(
                    st.session_state.resume_path
                )

                st.session_state.vector_store = create_vector_store(
                    resume_text
                )

                resume_data = parse_resume_ai(
                    resume_text,
                    target_role
                )

                st.session_state.resume_data = resume_data
                st.session_state.resume_uploaded = True
                st.session_state.target_role = target_role

                # Save analysis to database
                save_analysis(
                    st.session_state.user_id,
                    target_role,
                    resume_data
                    )

                
            st.success("✅ Analysis Complete!")

    # -------------------------------
    # DISPLAY RESULTS
    # -------------------------------

    if st.session_state.resume_data is not None:

        resume_data = st.session_state.resume_data
        target_role = st.session_state.target_role

        
                            

        st.divider()

        st.subheader("⭐ ATS Score")

        ats = resume_data["ats_score"]

        st.metric(
            label="Resume Score",
            value=f"{ats}/100"
        )

        st.progress(ats / 100)

        st.divider()

        st.subheader("📄 Resume Summary")

        col1, col2 = st.columns(2)

        with col1:

            st.write("**👤 Name**")
            st.write(resume_data["personal_information"]["name"])

            st.write("**📱 Phone**")
            st.write(resume_data["personal_information"]["phone"])

            st.write("**📧 Email**")
            st.write(resume_data["personal_information"]["email"])

            st.subheader("🎓 Education")

            for edu in resume_data["education"]:

                with st.container(border=True):

                    st.write(f"**Degree:** {edu['degree']}")
                    st.write(f"**Institution:** {edu['institution']}")
                    st.write(f"**Year:** {edu['year']}")
                    st.write(f"**CGPA:** {edu['cgpa']}")

            st.subheader("💼 Experience")

            for exp in resume_data["experience"]:

                with st.container(border=True):

                    st.write(f"**Company:** {exp['company']}")
                    st.write(f"**Role:** {exp['role']}")
                    st.write(f"**Duration:** {exp['duration']}")
                    st.write(exp["description"])

            st.subheader("📂 Projects")
            
            for project in resume_data["projects"]:
            
                    with st.container(border=True):
            
                        st.write(f"**{project['name']}**")
                        st.write(project["technologies"])
                        st.write(project["description"])


        with col2:

            st.write("**🔗 LinkedIn**")
            st.write(resume_data["personal_information"]["linkedin"])

            st.write("**💻 GitHub**")
            st.write(resume_data["personal_information"]["github"])

            st.subheader("🛠 Skills")

            if resume_data["skills"]:

                skills_html = ""

                for skill in resume_data["skills"]:

                    skills_html += f"""
                    <span style="
                    background-color:#4CAF50;
                    color:white;
                    padding:8px 15px;
                    border-radius:20px;
                    margin:5px;
                    display:inline-block;
                    font-size:14px;
                    font-weight:bold;">
                    {skill}
                </span>"""

                st.markdown(
                    skills_html,
                    unsafe_allow_html=True
                )

            else:
                st.info("No skills found.")

            

            st.subheader("🏆 Certifications")

            if resume_data["certifications"]:

                for cert in resume_data["certifications"]:
                    st.success(cert)

            else:
                st.info("No certifications found.")

        

            st.subheader(f"🎯 Missing Skills for {target_role}")

            if resume_data["missing_skills"]:

              missing_html = ""

              for skill in resume_data["missing_skills"]:
                  missing_html += f"""
                <span style="
                background-color:#FF9800;
                color:white;
                padding:8px 15px;
                border-radius:20px;
                margin:5px;
                display:inline-block;
                font-size:14px;
                font-weight:bold;">
                {skill}
                 </span>"""

            st.markdown(
                missing_html,
                unsafe_allow_html=True
            )
            

            if "suggestions" in resume_data:

              

               st.subheader("💡 Improvement Suggestions")

               for suggestion in resume_data["suggestions"]:

                  st.info(suggestion)

        report_path="resume_analysis_report.pdf"
        generate_report(resume_data,target_role,report_path)
        with open(report_path,"rb") as pdf:

            st.divider()

            st.download_button(
            label="Download Analysis Report",
            data=pdf,
            file_name=f"{resume_data['personal_information']['name']}_CareerPilot_Report.pdf",
            mime="application/pdf",
            use_container_width=True
            )

            st.caption("Professionally generated by CareerPilot AI")

