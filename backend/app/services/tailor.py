import asyncio
import json
import logging

from groq import APIStatusError, Groq

from app.core.config import settings


client = Groq(api_key=settings.GROQ_API_KEY)
logger = logging.getLogger(__name__)


TAILOR_PROMPT = """
You are an honest resume tailoring assistant.

Create an editable content draft for tailoring a resume to a job.

Return ONLY a valid JSON object with exactly this structure, no extra text:
{
  "version": 2,
  "tailored_sections": {
    "summary": "string or null",
    "skills": ["skill or keyword"],
    "experience": [
      {
        "role": "role/title exactly from resume, or null",
        "company": "company/organization exactly from resume, or null",
        "location": "location exactly from resume, or null",
        "dates": "date range exactly from resume, or null",
        "bullets": [
          {
            "original": "original bullet or source line from resume",
            "revised": "truthful revised bullet",
            "inserted_keywords": ["keyword"],
            "evidence": "short explanation of where the resume supports this revision"
          }
        ]
      }
    ],
    "projects": [
      {
        "name": "project name exactly from resume, or null",
        "links": [
          {
            "label": "visible link label exactly from resume",
            "url": "URL exactly from resume"
          }
        ],
        "tech_stack": ["technology from resume only"],
        "bullets": [
          {
            "original": "original bullet or source line from resume",
            "revised": "truthful revised bullet",
            "inserted_keywords": ["keyword"],
            "evidence": "short explanation of where the resume supports this revision"
          }
        ]
      }
    ],
    "education": [
      {
        "institution": "institution exactly from resume, or null",
        "degree": "degree exactly from resume, or null",
        "location": "location exactly from resume, or null",
        "dates": "date range exactly from resume, or null",
        "details": ["coursework, GPA, honors, or details from resume only"]
      }
    ],
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
- Do not invent project names, links, repositories, portfolio URLs, institutions, degrees, locations, or dates.
- Preserve all links from the original resume. If a project has a link, keep it with that project.
- Preserve every original project bullet/source point under its original project. You may rewrite each point for clarity and job relevance, but do not omit project points from the original resume.
- Preserve every original project from the resume, even if it is not directly relevant to the job.
- Preserve education from the original resume even if it is not directly relevant to the job.
- Preserve experience entries from the original resume. Tailor bullet wording only when supported.
- Only insert missing skills and keyword gaps when the original resume provides clear evidence.
- If a missing item is not clearly supported by the resume, put it in unsupported_gaps and do not insert it.
- Preserve the candidate's background. Improve wording only.
- Prefer concise resume bullets with action verbs and job-relevant keywords, but do not reduce the number of original project bullets.
- If no safe revision exists, return empty arrays for revised bullets and list unsupported gaps.
- Keep the legacy experience_bullets and project_bullets arrays populated with the same revised bullets for backward compatibility.
- Return only JSON, no markdown.
"""


COMPACT_TAILOR_PROMPT = """
You are an honest resume tailoring assistant.
Return ONLY valid JSON with this shape:
{
  "version": 2,
  "tailored_sections": {
    "summary": "string or null",
    "skills": ["skill"],
    "experience": [],
    "projects": [],
    "education": [],
    "experience_bullets": [
      {"original": "source line", "revised": "truthful rewrite", "inserted_keywords": ["keyword"], "evidence": "supporting source"}
    ],
    "project_bullets": [
      {"original": "source line", "revised": "truthful rewrite", "inserted_keywords": ["keyword"], "evidence": "supporting source"}
    ]
  },
  "inserted_keywords": ["keyword"],
  "unsupported_gaps": [{"name": "gap", "category": "technical or soft or tool or certification or education or other", "reason": "why unsupported"}],
  "ats_fixes": ["short fix"]
}
Do not invent anything. Only rewrite resume lines when the resume clearly supports the keyword. Put unsupported gaps in unsupported_gaps.
"""


def _limit_text(value: str, max_chars: int) -> str:
    value = value or ""
    if len(value) <= max_chars:
        return value
    return value[:max_chars].rsplit("\n", 1)[0].strip()


def _compact_items(items: list, max_items: int = 12) -> list:
    if not isinstance(items, list):
        return []
    return items[:max_items]


def _source_lines(source_text: str) -> list[str]:
    return [
        line.strip()
        for line in (source_text or "").splitlines()
        if line and line.strip()
    ]


def _extract_resume_summary(resume_text: str) -> str:
    lines = _source_lines(resume_text)
    if not lines:
        return ""

    headings = {
        "summary",
        "profile",
        "professional summary",
        "career summary",
        "objective",
    }
    stop_headings = {
        "skills",
        "technical skills",
        "experience",
        "work experience",
        "professional experience",
        "projects",
        "education",
        "certifications",
        "achievements",
    }

    for index, line in enumerate(lines):
        normalized = line.lower().strip(" :")
        if normalized not in headings:
            continue

        summary_lines = []
        for next_line in lines[index + 1 :]:
            next_normalized = next_line.lower().strip(" :")
            if next_normalized in stop_headings:
                break
            summary_lines.append(next_line)
            if len(" ".join(summary_lines)) >= 600:
                break

        return " ".join(summary_lines).strip()

    return ""


def _ensure_summary(draft: dict, resume_text: str) -> dict:
    sections = draft.setdefault("tailored_sections", {})
    if sections.get("summary"):
        return draft

    summary = _extract_resume_summary(resume_text)
    if summary:
        sections["summary"] = summary
    return draft


def ensure_resume_summary(draft: dict, resume_text: str) -> dict:
    return _ensure_summary(draft, resume_text)


def _item_name(item) -> str | None:
    if isinstance(item, str):
        return item.strip() or None
    if isinstance(item, dict):
        value = item.get("name") or item.get("keyword")
        return str(value).strip() if value else None
    return None


def _unsupported_gap(item) -> dict | None:
    name = _item_name(item)
    if not name:
        return None
    category = item.get("category") if isinstance(item, dict) else "other"
    return {
        "name": name,
        "category": category or "other",
        "reason": "AI tailoring could not complete safely; review this gap manually before adding it.",
    }


def fallback_tailored_draft(
    resume_text: str,
    required_skills: list,
    preferred_skills: list,
    missing_skills: list,
    keyword_gaps: list,
) -> dict:
    skill_names = []
    for item in _compact_items((required_skills or []) + (preferred_skills or []), 16):
        name = _item_name(item)
        if name and name not in skill_names:
            skill_names.append(name)

    unsupported_gaps = []
    for item in _compact_items((missing_skills or []) + (keyword_gaps or []), 16):
        gap = _unsupported_gap(item)
        if gap and all(existing["name"] != gap["name"] for existing in unsupported_gaps):
            unsupported_gaps.append(gap)

    return {
        "version": 2,
        "generation_mode": "fallback",
        "tailored_sections": {
            "summary": _extract_resume_summary(resume_text),
            "skills": skill_names,
            "experience": [],
            "projects": [],
            "education": [],
            "experience_bullets": [],
            "project_bullets": [],
        },
        "inserted_keywords": [],
        "unsupported_gaps": unsupported_gaps,
        "ats_fixes": [
            "AI tailoring could not complete for this request. Review the unsupported gaps and add only skills that are already supported by your resume."
        ],
    }


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
    try:
        return _tailor_sync_with_limits(
            prompt=TAILOR_PROMPT,
            resume_text=resume_text,
            job_description=job_description,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            missing_skills=missing_skills,
            keyword_gaps=keyword_gaps,
            resume_chars=11000,
            job_chars=6000,
            max_tokens=2200,
        )
    except Exception as exc:
        if isinstance(exc, APIStatusError) and exc.status_code == 413:
            logger.info("Retrying resume tailoring with compact prompt after 413")
            try:
                return _tailor_sync_with_limits(
                    prompt=COMPACT_TAILOR_PROMPT,
                    resume_text=resume_text,
                    job_description=job_description,
                    required_skills=required_skills,
                    preferred_skills=preferred_skills,
                    missing_skills=missing_skills,
                    keyword_gaps=keyword_gaps,
                    resume_chars=6500,
                    job_chars=3000,
                    max_tokens=1600,
                )
            except Exception:
                logger.exception("Compact resume tailoring retry failed; using fallback draft")
        else:
            logger.exception("Resume tailoring failed; using fallback draft")

        return fallback_tailored_draft(
            resume_text=resume_text,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            missing_skills=missing_skills,
            keyword_gaps=keyword_gaps,
        )


def _tailor_sync_with_limits(
    prompt: str,
    resume_text: str,
    job_description: str,
    required_skills: list,
    preferred_skills: list,
    missing_skills: list,
    keyword_gaps: list,
    resume_chars: int,
    job_chars: int,
    max_tokens: int,
) -> dict:
    user_content = f"""
Original Resume:
{_limit_text(resume_text, resume_chars)}

Job Description:
{_limit_text(job_description, job_chars)}

Required Skills:
{json.dumps(_compact_items(required_skills))}

Preferred Skills:
{json.dumps(_compact_items(preferred_skills))}

Missing Skills:
{json.dumps(_compact_items(missing_skills))}

Keyword Gaps:
{json.dumps(_compact_items(keyword_gaps))}
"""

    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_content},
        ],
        temperature=0.1,
        max_tokens=max_tokens,
    )

    content = response.choices[0].message.content
    return _ensure_summary(_extract_json(content), resume_text)


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
