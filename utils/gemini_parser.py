import json

from google.genai.types import GenerateContentConfig

from utils.config import client, MODEL_NAME
from utils.prompts import RESUME_ANALYSIS_PROMPT


def parse_resume_ai(resume_text,target_role):

    print("=== GEMINI PARSER RUNNING ===")
    print(RESUME_ANALYSIS_PROMPT)
    """
    Sends the extracted resume text to Gemini and
    returns structured JSON.
    """

    prompt = RESUME_ANALYSIS_PROMPT.replace("<TARGET_ROLE>",target_role).replace(
    "<RESUME_TEXT>",
    resume_text)

    

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=GenerateContentConfig(
            temperature=0.2,
            response_mime_type="application/json"
        )
    )

    try:
        return json.loads(response.text)

    except Exception:

        return {
            "personal_information": {
                "name": "Not Found",
                "email": "Not Found",
                "phone": "Not Found",
                "linkedin": "Not Found",
                "github": "Not Found"
            },
            "skills": [],
            "education": [],
            "experience": [],
            "projects": [],
            "certifications": [],
            "ats_score": 0,
            "missing_skills": [],
            "suggestions": [
                "Unable to analyze resume."
            ]
        }