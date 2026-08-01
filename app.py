import streamlit as st
from pathlib import Path

from utils.resume_reader import extract_text
from utils.file_handler import save_resume
from utils.gemini_parser import parse_resume_ai

from utils.vector_store import create_vector_store
from utils.chat import chat_with_resume

from utils.pdf_report import generate_report


BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="CareerPilot AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    section[data-testid="stSidebar"] {
        width: 380px !important;
    }

    section[data-testid="stSidebar"] > div {
        width: 380px !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Session State
# -----------------------------
if "page" not in st.session_state:
    st.session_state.page = "🏠 Home"

if "vector_store" not in st.session_state:
    st.session_state.vector_store=None

if "resume_data" not in st.session_state:
    st.session_state.resume_data = None

if "resume_uploaded" not in st.session_state:
    st.session_state.resume_uploaded = False

if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = ""

if "target_role" not in st.session_state:
    st.session_state.target_role = ""

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.markdown(
    """
    <h1 style='font-size:38px; margin-bottom:0;'>
        🚀 CareerPilot AI
    </h1>
    """,
    unsafe_allow_html=True
)


st.sidebar.markdown(
    """
    <h3 style='font-size:28px; margin-bottom:0;'>
         Your Personalized AI Career Coach
    </h3>
    """,
    unsafe_allow_html=True
)


if st.sidebar.button("🏠 Home", use_container_width=True):
    st.session_state.page = "🏠 Home"

if st.sidebar.button("📄 Resume Analysis", use_container_width=True):
    st.session_state.page = "📄 Resume Analysis"

if st.sidebar.button("💬 Resume Chat", use_container_width=True):
    st.session_state.page = "💬 Resume Chat"

if st.sidebar.button("🎯 Interview Coach", use_container_width=True):
    st.session_state.page = "🎯 Interview Coach"

if st.sidebar.button("📊 Job Match", use_container_width=True):
    st.session_state.page = "📊 Job Match"

if st.sidebar.button("🧭 Career Advisor", use_container_width=True):
    st.session_state.page = "🧭 Career Advisor"

menu = st.session_state.page

# ===================================================
# HOME PAGE
# ===================================================
if menu == "🏠 Home":

    st.title("🚀 CareerPilot AI")
    st.subheader("Your Personalized AI Career Coach")

    st.write("""
Welcome to **CareerPilot AI**.

This platform helps students prepare for placements through personalized AI guidance.

### What can CareerPilot AI do?

- 📄 Analyze your resume
- 💬 Chat with your resume
- 🎯 Generate personalized interview questions
- 📊 Compare your resume with a Job Description
- 🧭 Suggest career improvements

**Let's build your career together! 🚀**
""")

# ===================================================
# RESUME ANALYSIS
#====================================================

# ===================================================
# RESUME ANALYSIS
# ===================================================
elif menu == "📄 Resume Analysis":

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




                
# ===================================================
# RESUME CHAT
# ===================================================
elif menu == "💬 Resume Chat":

    st.title("💬 Resume Chat")

    if st.session_state.vector_store is None:

        st.warning("⚠️ Please upload and analyze your resume first.")

    else:

        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content":
                    "👋 Hi! I'm **CareerPilot AI**.\n\n"
                    "Ask me anything about your resume or career."
                }
            ]

        col1, col2 = st.columns([5,1])

        with col2:

            if st.button("🗑 Clear Chat"):

                st.session_state.messages = [
                    {
                        "role":"assistant",
                        "content":
                        "👋 Hi! I'm **CareerPilot AI**.\n\n"
                        "Ask me anything about your resume or career."
                    }
                ]

                st.rerun()

        # Display chat history

        for message in st.session_state.messages:

            with st.chat_message(message["role"]):

                st.markdown(message["content"])

        # Chat input

        st.markdown("### 💡 Suggested Questions")

        col1, col2, col3 = st.columns(3)
        with col1:

            if st.button("📄 Summarize Resume"):
                st.session_state.quick_prompt = "Summarize my resume."

            if st.button("🛠️ Technical Skills"):
                 st.session_state.quick_prompt = "What are my technical skills?"

        with col2:
            if st.button("💼 Suitable Job Roles"):
                 st.session_state.quick_prompt = "What jobs can I apply for?"

            if st.button("🚀 Best Project"):
                st.session_state.quick_prompt = "Which is my strongest project?"

        with col3:
            if st.button("📚 Learn Next"):
                st.session_state.quick_prompt = "What should I learn next?"

            if st.button("🎤 Interview Questions"):
                st.session_state.quick_prompt = "Ask me interview questions based on my resume."

        prompt = st.chat_input("Ask about your resume...")
        if "quick_prompt" in st.session_state:

            prompt = st.session_state.quick_prompt
            del st.session_state.quick_prompt
            
        if prompt:
            st.session_state.messages.append(
                {
                    "role":"user",
                    "content":prompt
                }
            )

            with st.chat_message("user"):

                st.markdown(prompt)

            with st.chat_message("assistant"):

                with st.spinner("CareerPilot AI is thinking..."):

                    answer = chat_with_resume(
                        st.session_state.vector_store,
                        prompt
                    )

                    st.markdown(answer)

            st.session_state.messages.append(
                {
                    "role":"assistant",
                    "content":answer
                }
            )

            st.rerun()
# ===================================================
# INTERVIEW COACH
# ===================================================
elif menu == "🎯 Interview Coach":

    st.title("🎯 Interview Coach")
    st.info("Interview Coach module coming soon...")

# ===================================================
# JOB MATCH
# ===================================================
elif menu == "📊 Job Match":

    st.title("📊 Job Match")
    st.info("Job Match module coming soon...")

# ===================================================
# CAREER ADVISOR
# ===================================================
elif menu == "🧭 Career Advisor":

    st.title("🧭 Career Advisor")
    st.info("Career Advisor module coming soon...")