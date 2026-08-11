import streamlit as st
from utils.interview_coach import (
    start_interview,
    next_interview_question,
    evaluate_interview
)
from utils.interview_pdf import generate_interview_pdf


def show():

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

        if st.button("🚀 Start Interview", use_container_width=True):

            if not st.session_state.interview_active:


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

                        st.session_state.interview_final_report = result

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

                    pdf_bytes = generate_interview_pdf(target_role, st.session_state.interview_history,
                                                       st.session_state.interview_final_report)
                    st.download_button(
                        label="📥 Download Interview Report (PDF)",
                        data=pdf_bytes,
                        file_name=f"CareerPilot_Interview_Report_{target_role}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                        )



                    st.success("🎉 Interview completed!")










