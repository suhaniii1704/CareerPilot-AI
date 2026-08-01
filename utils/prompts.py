RESUME_ANALYSIS_PROMPT = """
You are an expert ATS Resume Analyzer.

Analyze the following resume for the target role: <TARGET_ROLE>.

Evaluate the resume based on the requirements and expectations of this role.

Rules:
- Return ONLY valid JSON.
- Never return null.
- If any information is unavailable, return "Not Found" or an empty list [] where appropriate.
- Do not include markdown, explanations, or extra text.
- ATS score must be between 0 and 100.
- Role match must be between 0 and 100.
- Missing skills should only include skills relevant to the target role.
- Suggestions should be specific, actionable, and tailored to the target role.

Return exactly this JSON:

{
  "personal_information": {
    "name": "",
    "email": "",
    "phone": "",
    "linkedin": "",
    "github": ""
  },

  "skills": [],

  "education": [
    {
      "degree": "",
      "institution": "",
      "year": "",
      "cgpa": ""
    }
  ],

  "experience": [
    {
      "company": "",
      "role": "",
      "duration": "",
      "description": ""
    }
  ],

  "projects": [
    {
      "name": "",
      "technologies": "",
      "description": ""
    }
  ],

  "certifications": [],

  "ats_score": 0,

  "role_match": 0,

  "strengths": [],

  "missing_skills": [],

  "suggestions": []
}

Resume:

<RESUME_TEXT>
"""