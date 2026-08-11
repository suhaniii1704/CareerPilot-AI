import streamlit as st

from utils.database import ( init_db, create_user, authenticate_user)

from modules import home,resume_analysis, interview_coach,resume_chat

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

if "interview_active" not in st.session_state:
    st.session_state.interview_active = False

if "interview_history" not in st.session_state:
    st.session_state.interview_history = []

if "interview_final_report" not in st.session_state:
    st.session_state.interview_final_report = None

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

    st.session_state.interview_active = False
    st.session_state.interview_history = []
    st.session_state.current_question = None
    st.session_state.interview_final_report = None

    st.rerun()

menu = st.session_state.page

# ===================================================
# HOME PAGE - AI CAREER DASHBOARD
# ===================================================

if menu == "🏠 Home":

   home.show()


# ===================================================
# RESUME ANALYSIS
# ===================================================
elif menu == "📄 Resume Analysis":
        resume_analysis.show()
    


                
# ===================================================
# RESUME CHAT
# ===================================================
elif menu == "💬 Resume Chat":
    resume_chat.show()


# ===================================================
# INTERVIEW COACH
#===================================================
elif menu == "🎯 Interview Coach":
    interview_coach.show()



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