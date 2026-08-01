import re


def extract_name(text):
    """
    Extract candidate name.
    Assumes the first non-empty line is the name.
    """

    lines = text.split("\n")

    for line in lines:
        line = line.strip()

        if line:
            return line

    return "Not Found"


def extract_email(text):
    """
    Extract email address.
    """

    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    match = re.search(pattern, text)

    if match:
        return match.group()

    return "Not Found"


def extract_phone(text):
    """
    Extract Indian phone number.
    """

    pattern = r"(?:\+91[\s-]?)?[6-9]\d{9}"

    match = re.search(pattern, text)

    if match:
        return match.group()

    return "Not Found"


def extract_linkedin(text):
    """
    Extract LinkedIn profile.
    """

    pattern = r"(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+"

    match = re.search(pattern, text, re.IGNORECASE)

    return match.group(0) if match else "Not Found"


def extract_github(text):
    """
    Extract GitHub profile URL.
    """

    pattern = r"https?://(?:www\.)?github\.com/[^\s]+"

    match = re.search(pattern, text)

    if match:
        return match.group()

    return "Not Found"

def extract_skills(text):
    """
    Extract skills from the resume.
    """

    skills = []

    skill_keywords = [

        # Programming
        "Python",
        "SQL",
        "JavaScript",
        "HTML",
        "CSS",
        "Java",

        # Data Science
        "Pandas",
        "NumPy",
        "Scikit-learn",
        "TensorFlow",
        "Machine Learning",
        "Deep Learning",
        "Natural Language Processing",

        # Visualization
        "Power BI",
        "Excel",
        "Matplotlib",
        "Seaborn",

        # Web
        "React.js",
        "Node.js",
        "RESTful APIs",

        # Tools
        "Git",
        "Linux",
        "Jupyter Notebook",
        "Google Cloud Platform",
        "VS Code",

        # AI
        "Gemini AI",
        "Generative AI"

    ]

    text_lower = text.lower()

    for skill in skill_keywords:

        if skill.lower() in text_lower:
            skills.append(skill)

    return sorted(list(set(skills)))


def parse_resume(text):

    print("===== PARSER V2 RUNNING =====")

    resume_data = {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "linkedin": extract_linkedin(text),
        "github": extract_github(text),
        "skills": extract_skills(text)
    }

    print(resume_data)

    return resume_data