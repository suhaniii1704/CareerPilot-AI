from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from utils.config import API_KEY,MODEL_NAME


def analyze_job_match(resume_data, job_description):

    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=API_KEY,
        temperature=0.3
    )

    prompt = f"""
You are an expert ATS and career coach.

Analyze how well the following resume matches the job description.

Resume:
{resume_data}

Job Description:
{job_description}

Return the response in this exact format:

MATCH SCORE: number/100

MISSING KEYWORDS:
- keyword 1
- keyword 2
- keyword 3

STRENGTHS:
- strength 1
- strength 2
- strength 3

AI SUGGESTIONS:
- suggestion 1
- suggestion 2
- suggestion 3
"""

    response = llm.invoke([HumanMessage(content=prompt)])

    return response.content