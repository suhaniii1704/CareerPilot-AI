import streamlit as st
from utils.chat import chat_with_resume


def show():

    
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
