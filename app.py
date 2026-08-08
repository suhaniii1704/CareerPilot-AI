import streamlit as st
from pathlib import Path

from utils.resume_reader import extract_text
from utils.file_handler import save_resume
from utils.gemini_parser import parse_resume_ai

from utils.vector_store import create_vector_store
from utils.chat import chat_with_resume

from utils.pdf_report import generate_report

from utils.database import ( init_db, create_user, authenticate_user, save_analysis, get_user_analyses )

from utils.interview_coach import (start_interview,next_interview_question,evaluate_interview)

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

#-------------------
#Initialize Database
#-------------------
init_db()

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

if "interview_questions" not in st.session_state:
    st.session_state.interview_questions = None

if "interview_feedback" not in st.session_state:
    st.session_state.interview_feedback = {}

if "interview_active" not in st.session_state:
    st.session_state.interview_active = False

if "interview_history" not in st.session_state:
    st.session_state.interview_history = []

if "current_question" not in st.session_state:
    st.session_state.current_question = None

#Login session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False 

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

# ===================================================
# AUTHENTICATION
# ===================================================

if not st.session_state.logged_in:

    st.title("🔐 CareerPilot AI")
    st.subheader("Login or Create an Account")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    # ---------------- LOGIN ----------------

    with tab1:

        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button("Login", use_container_width=True):

            user = authenticate_user(login_email, login_password)

            if user:

                st.session_state.logged_in = True
                st.session_state.user_id = user[0]
                st.session_state.user_name = user[1]

                st.rerun()

            else:
                st.error("Invalid email or password")

    # ---------------- SIGN UP ----------------

    with tab2:

        signup_name = st.text_input("Full Name", key="signup_name")
        signup_email = st.text_input("Email Address", key="signup_email")
        signup_password = st.text_input(
            "Password",
            type="password",
            key="signup_password"
        )

        if st.button("Create Account", use_container_width=True):

            success = create_user(
                signup_name,
                signup_email,
                signup_password
            )

            if success:
                st.success("Account created successfully! Please login.")
            else:
                st.error("Email already exists.")

    st.stop()


# -----------------------------
# Sidebar
# -----------------------------


st.sidebar.markdown(f"### 👋 {st.session_state.user_name}")

st.sidebar.divider()

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




if st.sidebar.button("🚪 Logout", use_container_width=True):

    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_name = ""

    st.rerun()

menu = st.session_state.page

# ===================================================
# HOME PAGE - AI CAREER DASHBOARD
# ===================================================

if menu == "🏠 Home":

    st.title("🚀 CareerPilot AI")
    st.subheader("Your Personalized AI Career Coach")

    # ===================================================
    # IF RESUME HAS BEEN ANALYZED
    # ===================================================

    if st.session_state.resume_data is not None:

        resume_data = st.session_state.resume_data
        target_role = st.session_state.target_role

        ats = resume_data["ats_score"]
        missing = len(resume_data["missing_skills"])

        # Resume Grade
        if ats >= 90:
            grade = "A+"
        elif ats >= 80:
            grade = "A"
        elif ats >= 70:
            grade = "B+"
        elif ats >= 60:
            grade = "B"
        else:
            grade = "C"

        # Role Match
        role_match = min(100, ats + 5)

        # Career Readiness
        career_readiness = min(100, ats - missing * 3 + 10)

        st.divider()

        st.markdown("## 📊 AI Career Dashboard")

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric("⭐ ATS Score", f"{ats}/100")

        with c2:
            st.metric("🏆 Grade", grade)

        with c3:
            st.metric("🎯 Role Match", f"{role_match}%")

        with c4:
            st.metric("⚠ Missing Skills", missing)

        st.divider()

        left, right = st.columns(2)

        # ===================================================
        # LEFT COLUMN - STRENGTHS
        # ===================================================

        with left:

            st.markdown("### 💪 Resume Strengths")

            strengths = []

            if len(resume_data["projects"]) >= 2:
                strengths.append("Strong project portfolio")

            if len(resume_data["certifications"]) >= 3:
                strengths.append("Excellent certifications")

            if "Python" in resume_data["skills"]:
                strengths.append("Strong Python skills")

            if "Machine Learning" in resume_data["skills"]:
                strengths.append("Machine Learning exposure")

            if not strengths:
                strengths.append("Resume uploaded successfully")

            for s in strengths:
                st.success(f"✔ {s}")

        # ===================================================
        # RIGHT COLUMN - IMPROVEMENTS
        # ===================================================

        with right:

            st.markdown("### ⚠ Areas to Improve")

            improvements = resume_data["missing_skills"][:4]

            if not improvements:
                improvements = [
                    "Add quantified achievements",
                    "Improve project descriptions"
                ]

            for i in improvements:
                st.warning(f"• {i}")

        st.divider()

        # ===================================================
        # RECOMMENDED ROLES
        # ===================================================

        st.markdown("### 🎯 Recommended Roles")

        role_cols = st.columns(4)

        recommended = [
            target_role or "Data Analyst",
            "Business Analyst",
            "ML Intern",
            "AI Engineer Intern"
        ]

        for col, role in zip(role_cols, recommended):
            with col:
                st.info(role)

        st.divider()

        # ===================================================
        # NEXT SKILLS
        # ===================================================

        st.markdown("### 📚 Recommended Next Skills")

        next_skills = (
            resume_data["missing_skills"][:5]
            if resume_data["missing_skills"]
            else ["Tableau", "Docker", "Azure"]
        )

        skill_cols = st.columns(len(next_skills))

        for col, skill in zip(skill_cols, next_skills):
            with col:
                st.markdown(
                    f"""
                    <div style='background:#1E293B;padding:15px;border-radius:12px;text-align:center;border:1px solid #334155;'>
                        <b>{skill}</b>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.divider()

        # ===================================================
        # CAREER READINESS
        # ===================================================

        st.markdown("### 📈 Career Readiness")

        st.progress(career_readiness / 100)
        st.caption(f"Overall placement readiness: {career_readiness}%")

        st.divider()

        # ===================================================
        # RESUME HISTORY
        # ===================================================

        st.markdown("### 🕒 Resume History")

        history = get_user_analyses(st.session_state.user_id)

        if history:

            import pandas as pd
        
            history_df = pd.DataFrame(
            history,
            columns=["Target Role", "ATS Score", "Date"]
            )

            history_df["Date"] = pd.to_datetime(
            history_df["Date"]
            ).dt.strftime("%d %b %Y %I:%M %p")
            st.dataframe(
                history_df,
               use_container_width=True,
              hide_index=True)
        else:
            st.info("No previous analyses found.")
            st.divider()
            st.success(
    "🎉 Resume analyzed successfully. Continue with Resume Chat, Interview Coach, or Job Match for deeper preparation."
)

    # ===================================================
    # BEFORE RESUME ANALYSIS
    # ===================================================

    else:

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

        st.info("📄 Upload and analyze your resume to unlock the AI Career Dashboard.")


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

# ===================================================
# CHAT-STYLE INTERVIEW COACH
# ===================================================

elif menu == "🎯 Interview Coach":

    st.title("🎯 Live AI Interview")
    st.write("Chat with an AI interviewer. Continue as long as you want and end the interview anytime.")

    if st.session_state.resume_data is None:

        st.warning("⚠ Please analyze your resume first.")

    else:

        target_role = st.session_state.target_role

        st.info(f"🎯 Interview for: {target_role}")

        if st.button("Reset Interview "):

            st.session_state.interview_active = False
            st.session_state.interview_history = []
            st.session_state.current_question = None
            st.session_state.interview_feedback = {}

            st.rerun()

        # Start interview
        if not st.session_state.interview_active:

            if st.button("🚀 Start Interview", use_container_width=True):

                with st.spinner("Starting interview..."):

                    first_q = start_interview(
                        st.session_state.resume_data,
                        target_role
                    )

                    st.session_state.interview_active = True
                    st.session_state.interview_history = []
                    st.session_state.current_question = first_q

                    st.rerun()

        else:

            # Display chat history
            for item in st.session_state.interview_history:

                with st.chat_message("assistant"):
                    st.write(item["question"])

                with st.chat_message("user"):
                    st.write(item["answer"])

            # Current question
            with st.chat_message("assistant"):
                question = st.session_state.current_question

                if isinstance(question, list):
                    clean = ""

                    for part in question:
                        if isinstance(part, dict) and "text" in part:
                            clean += part["text"]

                        elif hasattr(part, "text"):
                            clean += part.text

                        else:
                           clean += str(part)

                    question = clean

                st.markdown(question)

            # User answer
            answer = st.chat_input("Type your answer...")

            if answer:

                # Clean the current question before saving to history
                q = st.session_state.current_question
                if isinstance(q, list):
                    clean = ""

                    for part in q:

                          if isinstance(part, dict) and "text" in part:
                                 clean += part["text"]

                          elif hasattr(part, "text"):
                                 clean += part.text

                          else:
                                 clean += str(part)

                    q = clean.strip()
                st.session_state.interview_history.append({
                    "question": q,
                    "answer": answer
                    })


                with st.spinner("Thinking of the next question..."):

                    next_q = next_interview_question(
                        st.session_state.interview_history,
                        target_role
                    )

                    st.session_state.current_question = next_q

                st.rerun()

            st.divider()

            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    "Questions Asked",
                    len(st.session_state.interview_history)
                )

            with col2:

                if st.button("🛑 End Interview", use_container_width=True):

                    with st.spinner("Evaluating your interview..."):

                        result = evaluate_interview(
                            st.session_state.interview_history,
                            target_role
                        )

                    st.session_state.interview_active = False
                    st.session_state.current_question = None

                    st.subheader("📊 Interview Report")

                    st.markdown(
                        f"""
                        <div style="
                            background-color:#111827;
                            padding:20px;
                            border-radius:12px;
                            border:1px solid #374151;
                        ">
                            <pre style="
                                color:white;
                                white-space:pre-wrap;
                                font-family:inherit;
                                margin:0;
                            ">{result}</pre>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.success("🎉 Interview completed!")

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