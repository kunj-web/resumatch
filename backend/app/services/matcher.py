import json
import asyncio
from groq import Groq
from app.core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)


MATCHER_PROMPT = """
You are a resume and job description matcher. Compare the resume text against the job requirements.

Return ONLY a valid JSON object with exactly this structure, no extra text:
{
  "match_score": number between 0 and 100,
  "matched_skills": ["skill1", "skill2"],
  "missing_skills": [
    {"name": "skill name", "category": "technical or soft or tool or certification or other"}
  ],
  "keyword_gaps": [
    {
      "keyword": "keyword name",
      "category": "technical or soft or tool or certification or other",
      "priority": "high or medium or low",
      "context": "why this keyword matters, e.g. mentioned 3 times in job description"
    }
  ]
}

Rules:
- match_score is based on how many required skills are present in the resume
- matched_skills are skills from required_skills that are found in the resume
- missing_skills are skills from required_skills that are NOT found in the resume
- keyword_gaps are the most important missing keywords the candidate should add to their resume
- priority high = mentioned multiple times or critical for the role
- priority medium = mentioned once or important but not critical
- priority low = nice to have
- Return only the JSON, no explanation, no markdown
"""


def _match_sync(resume_text: str, required_skills: list, preferred_skills: list) -> dict:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": MATCHER_PROMPT},
            {
                "role": "user",
                "content": f"""
Resume:
{resume_text}

Required Skills:
{json.dumps(required_skills)}

Preferred Skills:
{json.dumps(preferred_skills)}
"""
            }
        ],
        temperature=0.1,
        max_tokens=1000
    )

    content = response.choices[0].message.content.strip()

    # Strip any markdown code block variations
    if "```" in content:
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]

    content = content.strip()
    return json.loads(content)


async def match_resume_to_job(
    resume_text: str,
    required_skills: list,
    preferred_skills: list
) -> dict:
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        _match_sync,
        resume_text,
        required_skills,
        preferred_skills
    )
    return result