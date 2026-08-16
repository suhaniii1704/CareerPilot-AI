import os
import tempfile

import streamlit as st
from google import genai

from utils.interview_coach import (
    start_interview,
    next_interview_question,
    evaluate_interview
)

from utils.interview_pdf import generate_interview_pdf

from utils.config import API_KEY, MODEL_NAME


# =========================================================
# GEMINI CLIENT FOR VOICE TRANSCRIPTION
# =========================================================

voice_client = genai.Client(
    api_key=API_KEY
)


# =========================================================
# HELPER: CLEAN GEMINI QUESTION
# =========================================================

def clean_question(question):

    if isinstance(question, list):

        clean = ""

        for part in question:

            if isinstance(part, dict) and "text" in part:
                clean += part["text"]

            elif hasattr(part, "text"):
                clean += part.text

            else:
                clean += str(part)

        return clean.strip()

    return str(question).strip()


# =========================================================
# VOICE → TEXT
# =========================================================

def transcribe_audio(audio_file):

    """
    Convert recorded interview audio into text using Gemini.
    """

    if audio_file is None:
        return None

    temp_path = None

    try:

        audio_bytes = audio_file.getvalue()

        if not audio_bytes:
            return None

        # -------------------------------------------------
        # Save audio temporarily
        # -------------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".wav"
        ) as temp_file:

            temp_file.write(audio_bytes)
            temp_path = temp_file.name

        # -------------------------------------------------
        # Upload audio to Gemini
        # -------------------------------------------------

        uploaded_audio = voice_client.files.upload(
            file=temp_path
        )

        # -------------------------------------------------
        # Transcription prompt
        # -------------------------------------------------

        response = voice_client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                uploaded_audio,
                """
Transcribe the candidate's spoken interview answer.

Return ONLY the transcription.

Do not:
- evaluate the answer
- summarize the answer
- add explanations
- add labels
- add quotation marks
- add commentary

Preserve the candidate's original meaning.
"""
            ]
        )

        if response.text:

            return response.text.strip()

        return None

    except Exception as e:

        st.error(
            f"❌ Voice transcription failed: {str(e)}"
        )

        return None

    finally:

        # -------------------------------------------------
        # Remove temporary file
        # -------------------------------------------------

        if temp_path and os.path.exists(temp_path):

            try:
                os.remove(temp_path)

            except Exception:
                pass


# =========================================================
# MAIN INTERVIEW PAGE
# =========================================================

def show():

    st.title("🎯 Live AI Interview")

    st.write(
        "Chat with an AI interviewer. "
        "Continue as long as you want and end the interview anytime."
    )

    # =====================================================
    # CHECK RESUME
    # =====================================================

    if st.session_state.resume_data is None:

        st.warning(
            "⚠️ Please analyze your resume first."
        )

        return

    target_role = st.session_state.target_role

    st.info(
        f"🎯 Interview for: {target_role}"
    )

    # =====================================================
    # INITIALIZE SESSION STATE
    # =====================================================

    if "interview_active" not in st.session_state:
        st.session_state.interview_active = False

    if "interview_history" not in st.session_state:
        st.session_state.interview_history = []

    if "current_question" not in st.session_state:
        st.session_state.current_question = None

    if "interview_final_report" not in st.session_state:
        st.session_state.interview_final_report = None

    # =====================================================
    # RESET INTERVIEW
    # =====================================================

    if st.button(
        "🔄 Reset Interview",
        use_container_width=True
    ):

        st.session_state.interview_active = False

        st.session_state.interview_history = []

        st.session_state.current_question = None

        st.session_state.interview_final_report = None

        st.rerun()

    # =====================================================
    # START INTERVIEW
    # =====================================================

    if st.button(
        "🚀 Start Interview",
        use_container_width=True
    ):

        if not st.session_state.interview_active:

            with st.spinner(
                "Starting interview..."
            ):

                first_question = start_interview(
                    st.session_state.resume_data,
                    target_role
                )

            st.session_state.interview_active = True

            st.session_state.interview_history = []

            st.session_state.current_question = first_question

            st.session_state.interview_final_report = None

            st.rerun()

    # =====================================================
    # ACTIVE INTERVIEW
    # =====================================================

    if st.session_state.interview_active:

        # -------------------------------------------------
        # DISPLAY PREVIOUS QUESTIONS / ANSWERS
        # -------------------------------------------------

        for item in st.session_state.interview_history:

            with st.chat_message("assistant"):

                st.write(
                    item["question"]
                )

            with st.chat_message("user"):

                st.write(
                    item["answer"]
                )

        # -------------------------------------------------
        # DISPLAY CURRENT QUESTION
        # -------------------------------------------------

        question = clean_question(
            st.session_state.current_question
        )

        with st.chat_message("assistant"):

            st.markdown(
                question
            )

        st.divider()

        # =================================================
        # COMBINED TEXT + VOICE CHAT INPUT
        # =================================================

        user_response = st.chat_input(
            "Type your answer or record your voice...",
            key="interview_chat_input",
            accept_audio=True,
            audio_sample_rate=16000
        )

        # =================================================
        # PROCESS USER RESPONSE
        # =================================================

        if user_response:

            answer = None

            # -------------------------------------------------
            # TEXT ANSWER
            # -------------------------------------------------

            if user_response.text:

                answer = user_response.text.strip()

            # -------------------------------------------------
            # VOICE ANSWER
            # -------------------------------------------------

            elif user_response.audio:

                with st.spinner(
                    "🎙️ Converting your voice answer to text..."
                ):

                    answer = transcribe_audio(
                        user_response.audio
                    )

                if answer:

                    st.success(
                        "✅ Voice answer transcribed successfully!"
                    )

                    with st.expander(
                        "📝 View Transcribed Answer",
                        expanded=True
                    ):

                        st.write(answer)

            # -------------------------------------------------
            # VALID ANSWER
            # -------------------------------------------------

            if answer:

                # ---------------------------------------------
                # SAVE ANSWER
                # ---------------------------------------------

                st.session_state.interview_history.append(
                    {
                        "question": question,
                        "answer": answer
                    }
                )

                # ---------------------------------------------
                # GENERATE NEXT QUESTION
                # ---------------------------------------------

                with st.spinner(
                    "🤖 Thinking of the next question..."
                ):

                    next_question = next_interview_question(
                        st.session_state.interview_history,
                        target_role
                    )

                st.session_state.current_question = next_question

                st.rerun()

            else:

                st.warning(
                    "⚠️ I couldn't detect an answer. "
                    "Please type an answer or record your voice."
                )

        # =================================================
        # INTERVIEW STATISTICS
        # =================================================

        st.divider()

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Questions Answered",
                len(
                    st.session_state.interview_history
                )
            )

        # =================================================
        # END INTERVIEW
        # =================================================

        with col2:

            if st.button(
                "🛑 End Interview",
                use_container_width=True
            ):

                if not st.session_state.interview_history:

                    st.warning(
                        "Please answer at least one question "
                        "before ending the interview."
                    )

                else:

                    with st.spinner(
                        "🧠 Evaluating your interview..."
                    ):

                        result = evaluate_interview(
                            st.session_state.interview_history,
                            target_role
                        )

                    st.session_state.interview_final_report = result

                    st.session_state.interview_active = False

                    st.session_state.current_question = None

                    st.rerun()

    # =====================================================
    # FINAL INTERVIEW REPORT
    # =====================================================

    if (
        not st.session_state.interview_active
        and st.session_state.interview_final_report
    ):

        st.subheader(
            "📊 Interview Report"
        )

        result = (
            st.session_state.interview_final_report
        )

        # -------------------------------------------------
        # REPORT DISPLAY
        # -------------------------------------------------

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

        # -------------------------------------------------
        # GENERATE PDF
        # -------------------------------------------------

        pdf_bytes = generate_interview_pdf(
            target_role,
            st.session_state.interview_history,
            st.session_state.interview_final_report
        )

        st.download_button(
            label="📥 Download Interview Report (PDF)",
            data=pdf_bytes,
            file_name=(
                f"CareerPilot_Interview_Report_"
                f"{target_role}.pdf"
            ),
            mime="application/pdf",
            use_container_width=True
        )

        st.success(
            "🎉 Interview completed!"
        )