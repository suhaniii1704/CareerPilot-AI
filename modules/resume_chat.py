import os
import tempfile

import streamlit as st
from google import genai

from utils.chat import chat_with_resume
from utils.config import API_KEY, MODEL_NAME


# =========================================================
# GEMINI CLIENT FOR VOICE TRANSCRIPTION
# =========================================================

voice_client = genai.Client(
    api_key=API_KEY
)


# =========================================================
# VOICE → TEXT
# =========================================================

def transcribe_audio(audio_file):

    """
    Convert user's spoken Resume Chat question
    into text using Gemini.
    """

    if audio_file is None:
        return None

    temp_path = None

    try:

        audio_bytes = audio_file.getvalue()

        if not audio_bytes:
            return None

        # -------------------------------------------------
        # Save temporary audio
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
        # Transcribe
        # -------------------------------------------------

        response = voice_client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                uploaded_audio,
                """
Transcribe the user's spoken question.

Return ONLY the transcription.

Do not:
- answer the question
- summarize it
- add explanations
- add labels
- add quotation marks
- add commentary

Preserve the user's original meaning.
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
# MAIN PAGE
# =========================================================

def show():

    st.title("💬 Resume Chat")

    # =====================================================
    # CHECK VECTOR STORE
    # =====================================================

    if st.session_state.vector_store is None:

        st.warning(
            "⚠️ Please upload and analyze your resume first."
        )

        return

    # =====================================================
    # INITIALIZE CHAT HISTORY
    # =====================================================

    if "messages" not in st.session_state:

        st.session_state.messages = [
            {
                "role": "assistant",
                "content":
                "👋 Hi! I'm **CareerPilot AI**.\n\n"
                "Ask me anything about your resume or career."
            }
        ]

    # =====================================================
    # CLEAR CHAT
    # =====================================================

    col1, col2 = st.columns([5, 1])

    with col2:

        if st.button(
            "🗑 Clear Chat"
        ):

            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content":
                    "👋 Hi! I'm **CareerPilot AI**.\n\n"
                    "Ask me anything about your resume or career."
                }
            ]

            st.rerun()

    # =====================================================
    # DISPLAY CHAT HISTORY
    # =====================================================

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )

    # =====================================================
    # SUGGESTED QUESTIONS
    # =====================================================

    st.markdown(
        "### 💡 Suggested Questions"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button(
            "📄 Summarize Resume"
        ):

            st.session_state.quick_prompt = (
                "Summarize my resume."
            )

        if st.button(
            "🛠️ Technical Skills"
        ):

            st.session_state.quick_prompt = (
                "What are my technical skills?"
            )

    with col2:

        if st.button(
            "💼 Suitable Job Roles"
        ):

            st.session_state.quick_prompt = (
                "What jobs can I apply for?"
            )

        if st.button(
            "🚀 Best Project"
        ):

            st.session_state.quick_prompt = (
                "Which is my strongest project?"
            )

    with col3:

        if st.button(
            "📚 Learn Next"
        ):

            st.session_state.quick_prompt = (
                "What should I learn next?"
            )

        if st.button(
            "🎤 Interview Questions"
        ):

            st.session_state.quick_prompt = (
                "Ask me interview questions based on my resume."
            )

    # =====================================================
    # CHAT INPUT WITH MICROPHONE
    # =====================================================

    user_response = st.chat_input(
        "Ask about your resume...",
        key="resume_chat_input",
        accept_audio=True,
        audio_sample_rate=16000
    )

    # =====================================================
    # QUICK PROMPT
    # =====================================================

    if "quick_prompt" in st.session_state:

        prompt = st.session_state.quick_prompt

        del st.session_state.quick_prompt

    else:

        prompt = None

    # =====================================================
    # PROCESS CHAT INPUT
    # =====================================================

    if user_response:

        # -------------------------------------------------
        # TEXT INPUT
        # -------------------------------------------------

        if user_response.text:

            prompt = (
                user_response.text.strip()
            )

        # -------------------------------------------------
        # VOICE INPUT
        # -------------------------------------------------

        elif user_response.audio:

            with st.spinner(
                "🎙️ Converting your voice to text..."
            ):

                prompt = transcribe_audio(
                    user_response.audio
                )

            if prompt:

                st.success(
                    "✅ Voice question transcribed!"
                )

            else:

                st.warning(
                    "⚠️ I couldn't understand your "
                    "voice input. Please try again."
                )

                return

        # -------------------------------------------------
        # PROCESS PROMPT
        # -------------------------------------------------

        if prompt:

            # ---------------------------------------------
            # ADD USER MESSAGE
            # ---------------------------------------------

            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": prompt
                }
            )

            with st.chat_message(
                "user"
            ):

                st.markdown(
                    prompt
                )

            # ---------------------------------------------
            # GET AI RESPONSE
            # ---------------------------------------------

            with st.chat_message(
                "assistant"
            ):

                with st.spinner(
                    "CareerPilot AI is thinking..."
                ):

                    answer = chat_with_resume(
                        st.session_state.vector_store,
                        prompt
                    )

                st.markdown(
                    answer
                )

            # ---------------------------------------------
            # SAVE AI RESPONSE
            # ---------------------------------------------

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer
                }
            )

            st.rerun()