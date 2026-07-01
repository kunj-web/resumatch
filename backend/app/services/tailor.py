import asyncio
import json
import logging
import re

from groq import APIStatusError, Groq

from app.core.config import settings
from app.services.resume_renderer import _extract_original_projects


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
- Preserve every original technical skill from the resume. Add supported missing skills after the original skills; do not replace the original skills list.
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
Do not invent anything. Preserve every original technical skill and add supported job skills after the original skills. Only rewrite resume lines when the resume clearly supports the keyword. Put unsupported gaps in unsupported_gaps.
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


def _extract_resume_skills(resume_text: str) -> list[str]:
    lines = _source_lines(resume_text)
    if not lines:
        return []

    skill_headings = {"skills", "technical skills", "technologies", "tech stack"}
    stop_headings = {
        "summary",
        "profile",
        "experience",
        "work experience",
        "professional experience",
        "projects",
        "project",
        "education",
        "certifications",
        "achievements",
    }

    skills = []
    in_skills = False
    for line in lines:
        raw_normalized = line.lower().strip()
        normalized = line.lower().strip(" :")
        if not in_skills:
            inline_skill_heading = next(
                (
                    heading
                    for heading in skill_headings
                    if raw_normalized.startswith(f"{heading}:")
                ),
                None,
            )
            if inline_skill_heading:
                _add_skill_tokens(skills, line.split(":", 1)[1])
                continue

        if normalized in skill_headings:
            in_skills = True
            continue
        if in_skills and normalized in stop_headings:
            break
        if not in_skills:
            continue

        cleaned = _clean_bullet_text(line)
        if not cleaned:
            continue

        _add_skill_tokens(skills, cleaned)

        if len(skills) >= 40:
            break

    return skills


def _add_skill_tokens(skills: list[str], text: str) -> None:
    cleaned = _clean_bullet_text(text)
    if ":" in cleaned:
        _, cleaned = cleaned.split(":", 1)

    for item in re.split(r",|;|\||•|▪|▫|‣|◦", cleaned):
        skill = _clean_bullet_text(item)
        if not skill or len(skill) > 60:
            continue
        if skill.lower() in {
            "languages",
            "frontend",
            "backend",
            "database",
            "databases",
            "tools",
            "frameworks",
            "libraries",
        }:
            continue
        if not any(existing.lower() == skill.lower() for existing in skills):
            skills.append(skill)


def _merge_skills(original_skills: list[str], tailored_skills: list) -> list[str]:
    merged = []
    for skill in list(original_skills or []) + list(tailored_skills or []):
        if isinstance(skill, dict):
            value = skill.get("name") or skill.get("keyword")
        else:
            value = skill

        value = _clean_bullet_text(str(value or ""))
        if not value:
            continue
        if not any(existing.lower() == value.lower() for existing in merged):
            merged.append(value)
    return merged


def _ensure_original_skills(draft: dict, resume_text: str) -> dict:
    sections = draft.setdefault("tailored_sections", {})
    original_skills = _extract_resume_skills(resume_text)
    if original_skills:
        sections["skills"] = _merge_skills(original_skills, sections.get("skills") or [])
    return draft


def _clean_bullet_text(line: str) -> str:
    line = re.sub(r"^[\s\-*•▪▫‣◦]+", "", line or "").strip()
    line = re.sub(r"^\d+[\).]\s+", "", line).strip()
    return re.sub(r"\s+", " ", line)


def _is_section_heading(line: str) -> bool:
    normalized = (line or "").lower().strip(" :")
    return normalized in {
        "summary",
        "profile",
        "skills",
        "technical skills",
        "experience",
        "work experience",
        "professional experience",
        "projects",
        "project",
        "personal projects",
        "academic projects",
        "education",
        "certifications",
        "achievements",
    }


def _extract_project_bullets(resume_text: str) -> list[dict]:
    lines = _source_lines(resume_text)
    project_headings = {
        "projects",
        "project",
        "personal projects",
        "academic projects",
        "key projects",
    }
    stop_headings = {
        "education",
        "experience",
        "work experience",
        "professional experience",
        "skills",
        "technical skills",
        "certifications",
        "achievements",
        "summary",
        "profile",
    }

    in_projects = False
    bullets = []
    for line in lines:
        normalized = line.lower().strip(" :")
        if normalized in project_headings:
            in_projects = True
            continue
        if in_projects and normalized in stop_headings:
            break
        if not in_projects:
            continue

        cleaned = _clean_bullet_text(line)
        if not cleaned or _is_section_heading(cleaned):
            continue
        if re.fullmatch(r"https?://\S+|www\.\S+", cleaned, re.IGNORECASE):
            continue

        starts_like_bullet = bool(re.match(r"^\s*(?:[-*•▪▫‣◦]|\d+[\).])\s+", line))
        has_resume_signal = bool(
            re.search(
                r"\b(built|created|developed|designed|implemented|integrated|deployed|optimized|automated|used|using|with|api|app|model|system|dashboard|platform)\b",
                cleaned,
                re.IGNORECASE,
            )
        )
        if not starts_like_bullet and (len(cleaned) < 45 or not has_resume_signal):
            continue

        if any(item["original"].lower() == cleaned.lower() for item in bullets):
            continue

        bullets.append(
            {
                "original": cleaned,
                "revised": cleaned,
                "inserted_keywords": [],
                "evidence": "Preserved from the original resume project section.",
            }
        )
        if len(bullets) >= 12:
            break

    return bullets


def _project_section_lines(resume_text: str) -> list[str]:
    lines = _source_lines(resume_text)
    collected = []
    in_projects = False
    for line in lines:
        normalized = line.lower().strip(" :")
        if normalized in {
            "projects",
            "project",
            "personal projects",
            "academic projects",
            "key projects",
        }:
            in_projects = True
            continue
        if in_projects and _is_section_heading(line):
            break
        if in_projects:
            collected.append(line)
    return collected


def _urls_from_text(text: str) -> list[str]:
    return re.findall(
        r"(?:(?:https?://|www\.)[\w.-]+\.[a-zA-Z]{2,}(?:/[\w./?%&=+#-]+)?)",
        text or "",
    )


def _link_label(url: str) -> str:
    lower_url = url.lower()
    if "github" in lower_url:
        return "GitHub"
    if "linkedin" in lower_url:
        return "LinkedIn"
    if "demo" in lower_url or "vercel" in lower_url or "netlify" in lower_url:
        return "Live"
    return "Link"


def _parse_project_title_with_links(line: str) -> tuple[str, list[str], list[dict]]:
    urls = _urls_from_text(line)
    without_links = re.sub(r"https?://\S+|www\.\S+", "", line)
    without_labels = re.sub(
        r"\b(?:GitHub|Live|Demo|Portfolio|Link)\b",
        "",
        without_links,
        flags=re.I,
    )
    match = re.search(r"\(([^)]*)\)", without_labels)
    tech_stack = []
    if match:
        tech_stack = [
            _clean_bullet_text(item)
            for item in re.split(r",|/", match.group(1))
            if _clean_bullet_text(item)
        ]
        name = _clean_bullet_text(without_labels[: match.start()])
    else:
        name = _clean_bullet_text(without_labels)

    links = [{"label": _link_label(url), "url": url} for url in urls]
    return name, tech_stack, links


def _looks_like_project_title_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped or not stripped[0].isupper():
        return False
    return bool(
        _urls_from_text(line)
        or re.search(r"\b(GitHub|Live|Demo|Portfolio)\b", line, flags=re.I)
        or re.search(r"\([^)]{2,}\)", line)
    )


def _parse_original_projects_for_tailor(resume_text: str) -> list[dict]:
    projects = []
    current = None
    for line in _project_section_lines(resume_text):
        if _looks_like_project_title_line(line):
            if current:
                projects.append(current)
            name, tech_stack, links = _parse_project_title_with_links(line)
            current = {
                "name": name or None,
                "links": links,
                "tech_stack": tech_stack,
                "bullets": [],
            }
            continue

        cleaned = _clean_bullet_text(line)
        if not cleaned or _is_section_heading(cleaned):
            continue
        if _urls_from_text(cleaned) and current:
            current["links"].extend(
                {"label": _link_label(url), "url": url} for url in _urls_from_text(cleaned)
            )
            continue

        starts_like_bullet = bool(re.match(r"^\s*(?:[-*•▪▫‣◦]|\d+[\).])\s+", line))
        if current and (starts_like_bullet or len(cleaned) >= 35):
            current["bullets"].append(cleaned)

    if current:
        projects.append(current)

    return [
        project
        for project in projects
        if project.get("name") or project.get("links") or project.get("bullets")
    ]


def _bullet_entry_from_text(text: str) -> dict:
    cleaned = _clean_bullet_text(text)
    return {
        "original": cleaned,
        "revised": cleaned,
        "inserted_keywords": [],
        "evidence": "Preserved from the original resume project section.",
    }


def _original_projects_as_tailored_entries(
    resume_text: str, replacement_bullets: list | None = None
) -> list[dict]:
    original_projects = _extract_original_projects(_source_lines(resume_text))
    if not original_projects:
        original_projects = _parse_original_projects_for_tailor(resume_text)
    entries = []
    replacements = list(replacement_bullets or [])
    cursor = 0
    for project in original_projects:
        bullets = []
        for bullet in project.get("bullets") or []:
            replacement = replacements[cursor] if cursor < len(replacements) else None
            cursor += 1
            if isinstance(replacement, dict):
                candidate = {
                    "original": replacement.get("original") or bullet,
                    "revised": replacement.get("revised")
                    or replacement.get("text")
                    or replacement.get("original")
                    or bullet,
                    "inserted_keywords": replacement.get("inserted_keywords") or [],
                    "evidence": replacement.get("evidence")
                    or "Preserved from the original resume project section.",
                }
            else:
                candidate = _bullet_entry_from_text(replacement or bullet)

            if _clean_bullet_text(candidate.get("revised")):
                bullets.append(candidate)

        if project.get("name") or bullets:
            entries.append(
                {
                    "name": project.get("name") or None,
                    "links": project.get("links") or [],
                    "tech_stack": project.get("tech_stack") or [],
                    "bullets": bullets,
                }
            )

    return entries


def _ensure_project_bullets(draft: dict, resume_text: str) -> dict:
    sections = draft.setdefault("tailored_sections", {})
    projects = sections.get("projects") or []
    if any(project.get("bullets") for project in projects if isinstance(project, dict)):
        return draft

    original_projects = _original_projects_as_tailored_entries(
        resume_text, sections.get("project_bullets") or []
    )
    if original_projects:
        sections["projects"] = original_projects
        sections["project_bullets"] = [
            bullet
            for project in original_projects
            for bullet in project.get("bullets") or []
        ]
        return draft

    if not sections.get("project_bullets"):
        project_bullets = _extract_project_bullets(resume_text)
        if project_bullets:
            sections["project_bullets"] = project_bullets
    return draft


def _ensure_summary(draft: dict, resume_text: str) -> dict:
    sections = draft.setdefault("tailored_sections", {})
    if not sections.get("summary"):
        summary = _extract_resume_summary(resume_text)
        if summary:
            sections["summary"] = summary
    _ensure_original_skills(draft, resume_text)
    _ensure_project_bullets(draft, resume_text)
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
    original_projects = _original_projects_as_tailored_entries(resume_text)
    job_skill_names = []
    for item in _compact_items((required_skills or []) + (preferred_skills or []), 16):
        name = _item_name(item)
        if name:
            job_skill_names.append(name)
    skill_names = _merge_skills(_extract_resume_skills(resume_text), job_skill_names)

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
            "projects": original_projects,
            "education": [],
            "experience_bullets": [],
            "project_bullets": [
                bullet
                for project in original_projects
                for bullet in project.get("bullets") or []
            ],
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
