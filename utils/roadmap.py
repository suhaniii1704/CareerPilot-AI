from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from utils.config import API_KEY, MODEL_NAME


def generate_roadmap(resume_data, target_role, level, duration):

    # --------------------------------------------------
    # Determine number of weeks from selected duration
    # --------------------------------------------------

    duration_map = {
        "1 Month": 4,
        "3 Months": 12,
        "6 Months": 24
    }

    weeks = duration_map.get(duration, 4)

    # --------------------------------------------------
    # Gemini model
    # --------------------------------------------------

    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=API_KEY,
        temperature=0.4
    )

    # --------------------------------------------------
    # Build dynamic week headings
    # --------------------------------------------------

    week_sections = ""

    for week in range(1, weeks + 1):

        week_sections += f"""
WEEK {week}:
- Objective:
- Tasks:
  - Task 1
  - Task 2
  - Task 3
"""

    # --------------------------------------------------
    # Prompt
    # --------------------------------------------------

    prompt = f"""
You are an expert AI career mentor.

Create a personalized career roadmap for the user.

TARGET ROLE:
{target_role}

CURRENT LEVEL:
{level}

SELECTED DURATION:
{duration}

TOTAL NUMBER OF WEEKS:
{weeks}

RESUME DATA:
{resume_data}

==================================================
IMPORTANT OUTPUT RULES
==================================================

The selected duration MUST control the roadmap length.

If the duration is 1 Month:
Generate EXACTLY 4 weeks.

If the duration is 3 Months:
Generate EXACTLY 12 weeks.

If the duration is 6 Months:
Generate EXACTLY 24 weeks.

DO NOT generate 8 weeks unless the selected duration is 3 Months
and the requested roadmap explicitly requires that structure.

You MUST generate exactly {weeks} weekly sections.

Use the following exact heading format:

WEEK 1:
WEEK 2:
WEEK 3:
...

WEEK {weeks}:

Do NOT combine weeks.

Do NOT use:
WEEK 1-2
WEEK 3-4
WEEK 5-6
WEEK 7-8

Each week must be its own section.

==================================================
ROADMAP STRUCTURE
==================================================

Start with a short personalized summary before WEEK 1.

Then generate:

{week_sections}

After the weekly roadmap, generate:

KEY GAPS:

List the most important skill, experience, portfolio,
or resume gaps identified from the user's resume.

Then generate:

FINAL PROJECT:

Suggest ONE strong portfolio project that:

- matches the target role
- uses skills the user already has
- helps close important skill gaps
- is realistic for the selected duration
- can be added to GitHub
- can be demonstrated to recruiters

==================================================
PERSONALIZATION RULES
==================================================

Base the roadmap on the actual resume.

Prioritize skills that are relevant to the target role.

Do not recommend random technologies without explaining
their relevance.

For beginners, start with fundamentals.

For intermediate users, emphasize practical projects,
advanced skills, deployment and portfolio quality.

For advanced users, emphasize production systems,
system design, advanced tools and industry readiness.

The roadmap should progressively become more difficult.

The final weeks should focus on:

- portfolio
- interview preparation
- resume improvement
- GitHub
- applications
- networking

Do not invent qualifications that are not present in the resume.

Keep each week's content concise but useful.

Each week should contain:
1. A clear objective.
2. Three practical tasks.

==================================================
FINAL OUTPUT FORMAT
==================================================

SUMMARY:

Write a short personalized career roadmap summary.

WEEK 1:
Objective:
...

Tasks:
- ...
- ...
- ...

WEEK 2:
Objective:
...

Tasks:
- ...
- ...
- ...

Continue until WEEK {weeks}.

KEY GAPS:
- ...
- ...
- ...

FINAL PROJECT:
Project Name:
...

Description:
...

Tech Stack:
...

Why this project is suitable:
...

Return ONLY the roadmap.
"""

    # --------------------------------------------------
    # Generate response
    # --------------------------------------------------

    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )

    return response.content