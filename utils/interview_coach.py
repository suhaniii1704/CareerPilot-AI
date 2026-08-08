from langchain_google_genai import ChatGoogleGenerativeAI
from utils.config import API_KEY

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=API_KEY,
    temperature=0.7
)

def extract_text(response):
    content = response.content

    if isinstance(content, list):
        text = ""

        for part in content:
            if isinstance(part, dict) and "text" in part:
                text += part["text"]
            elif hasattr(part, "text"):
                text += part.text
            else:
                text += str(part)

        return text.strip()

    return str(content).strip()

def start_interview(resume_data, target_role):

    skills = ", ".join(resume_data.get("skills", []))

    projects = ", ".join(
        [p.get("name", "") for p in resume_data.get("projects", [])]
    )

    prompt = f"""
You are a professional interviewer for a {target_role} role.

Candidate skills: {skills}
Candidate projects: {projects}

Ask ONLY the first interview question.

Make it conversational and relevant to the candidate's background.

Return only the question.
"""

    response = llm.invoke(prompt)
    return response.content


def next_interview_question(chat_history, target_role):

    conversation = "\n".join([
        f"Interviewer: {m['question']}\nCandidate: {m['answer']}"
        for m in chat_history
    ])

    prompt = f"""
You are conducting a live interview for a {target_role} role.

Previous conversation:
{conversation}

Ask the NEXT interview question.

Rules:
- Ask only ONE question.
- Make it follow up naturally from the candidate's previous answer.
- Mix technical, project, problem-solving, and behavioral questions.
- Keep it conversational.
- Do not repeat previous questions.

Return only the question.
"""

    response = llm.invoke(prompt)
    return response.content


def evaluate_interview(chat_history, target_role):

    conversation = "\n".join([
        f"Q: {m['question']}\nA: {m['answer']}"
        for m in chat_history
    ])

    prompt = f"""
You are an expert interviewer for {target_role} roles.

Evaluate the complete interview.

Conversation:
{conversation}

Provide:

Overall Score: X/10

Technical Skills:
- ...

Communication:
- ...

Problem Solving:
- ...

Strengths:
- ...

Areas to Improve:
- ...

Final Recommendation:
- Hire
- Consider
- Needs Improvement

Return plain text only.
"""

    response = llm.invoke(prompt)
    return extract_text(response)