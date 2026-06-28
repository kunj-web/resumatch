import asyncio
import json

from groq import Groq

from app.core.config import settings


client = Groq(api_key=settings.GROQ_API_KEY)


TAILOR_PROMPT = """
You are an honest resume tailoring assistant.

Create an editable content draft for tailoring a resume to a job.

Return ONLY a valid JSON object with exactly this structure, no extra text:
{
  "version": 1,
  "tailored_sections": {
    "summary": "string or null",
    "skills": ["skill or keyword"],
    "experience_bullets": [
      {
        "original": "original bullet or source line from resume",
        "revised": "truthful revised bullet",
        "inserted_keywords": ["keyword"],
        "evidence": "short explanation of where the resume supports this revision"
      }
    ],
    "project_bullets": [
      {
        "original": "original project bullet or source line from resume",
        "revised": "truthful revised project bullet",
        "inserted_keywords": ["keyword"],
        "evidence": "short explanation of where the resume supports this revision"
      }
    ]
  },
  "inserted_keywords": ["keyword"],
  "unsupported_gaps": [
    {
      "name": "missing skill or keyword",
      "category": "technical or soft or tool or certification or education or other",
      "reason": "why it was not inserted"
    }
  ],
  "ats_fixes": ["short actionable fix"]
}

Hard rules:
- Do not invent experience.
- Do not invent education.
- Do not invent certifications.
- Do not invent employers, titles, dates, tools, metrics, achievements, or years of experience.
- Only insert missing skills and keyword gaps when the original resume provides clear evidence.
- If a missing item is not clearly supported by the resume, put it in unsupported_gaps and do not insert it.
- Preserve the candidate's background. Improve wording only.
- Prefer concise resume bullets with action verbs and job-relevant keywords.
- If no safe revision exists, return empty arrays for revised bullets and list unsupported gaps.
- Return only JSON, no markdown.
"""


def _extract_json(content: str) -> dict:
    content = content.strip()

    if "```" in content:
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]

    parsed = json.loads(content.strip())
    if not isinstance(parsed, dict):
        raise ValueError("Tailoring response must be a JSON object")
    return parsed


def _tailor_sync(
    resume_text: str,
    job_description: str,
    required_skills: list,
    preferred_skills: list,
    missing_skills: list,
    keyword_gaps: list,
) -> dict:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": TAILOR_PROMPT},
            {
                "role": "user",
                "content": f"""
Original Resume:
{resume_text}

Job Description:
{job_description}

Required Skills:
{json.dumps(required_skills)}

Preferred Skills:
{json.dumps(preferred_skills)}

Missing Skills:
{json.dumps(missing_skills)}

Keyword Gaps:
{json.dumps(keyword_gaps)}
""",
            },
        ],
        temperature=0.1,
        max_tokens=2500,
    )

    content = response.choices[0].message.content
    return _extract_json(content)


async def tailor_resume_to_job(
    resume_text: str,
    job_description: str,
    required_skills: list,
    preferred_skills: list,
    missing_skills: list,
    keyword_gaps: list,
) -> dict:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        _tailor_sync,
        resume_text,
        job_description,
        required_skills,
        preferred_skills,
        missing_skills,
        keyword_gaps,
    )
