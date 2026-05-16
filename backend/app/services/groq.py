import json
import asyncio
from groq import Groq
from app.core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)


EXTRACTION_PROMPT = """
You are a job description parser. Extract structured information from the job description below.

Return ONLY a valid JSON object with exactly this structure, no extra text:
{
  "title": "job title or null",
  "company": "company name or null",
  "location": "city, state/country or null",
  "location_type": "remote or onsite or hybrid or null",
  "job_type": "full-time or part-time or contract or internship or null",
  "salary_min": number or null,
  "salary_max": number or null,
  "salary_currency": "USD or relevant currency, default USD",
  "experience_min": number or null,
  "experience_max": number or null,
  "education": "degree requirement or null",
  "required_skills": [
    {"name": "skill name", "category": "technical or soft or tool or certification or other"}
  ],
  "preferred_skills": [
    {"name": "skill name", "category": "technical or soft or tool or certification or other"}
  ]
}

Rules:
- salary_min and salary_max must be numbers only, no currency symbols
- experience_min and experience_max are years as numbers
- required_skills are explicitly marked as required or must have
- preferred_skills are marked as nice to have, preferred, or bonus
- If a field is not mentioned, return null
- Return only the JSON, no explanation, no markdown
"""


def _extract_sync(raw_text: str) -> dict:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": EXTRACTION_PROMPT},
            {"role": "user", "content": f"Job Description:\n{raw_text}"},
        ],
        temperature=0.1,
        max_tokens=1000,
    )

    content = response.choices[0].message.content.strip()

    # Strip any markdown code block variations
    if "```" in content:
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]

    content = content.strip()
    return json.loads(content)


async def extract_job_details(raw_text: str) -> dict:
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _extract_sync, raw_text)
    return result
