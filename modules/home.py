import streamlit as st
import pandas as pd
from utils.database import get_user_analyses


def show():

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