from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from utils.config import API_KEY, MODEL_NAME


def generate_roadmap(resume_data, target_role, level, duration):

    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=API_KEY,
        temperature=0.4
    )

    prompt = f"""
You are an expert career mentor.

Generate a personalized career roadmap.

Target role: {target_role}
Current level: {level}
Duration: {duration}

Resume data:
{resume_data}

Create a practical roadmap with:

WEEK 1-2:
- tasks

WEEK 3-4:
- tasks

WEEK 5-6:
- tasks

WEEK 7-8:
- tasks

Also include:

KEY GAPS:
- gaps

FINAL PROJECT:
- one strong portfolio project

Keep it concise, actionable, and realistic for a student.
"""

    response = llm.invoke([HumanMessage(content=prompt)])

    return response.content