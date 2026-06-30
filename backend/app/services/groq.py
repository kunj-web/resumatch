import json
import asyncio
import re
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


SKILL_KEYWORDS = [
    "python",
    "javascript",
    "typescript",
    "java",
    "c++",
    "c#",
    "go",
    "ruby",
    "php",
    "react",
    "angular",
    "vue",
    "node.js",
    "node",
    "express",
    "django",
    "flask",
    "fastapi",
    "spring",
    "html",
    "css",
    "tailwind",
    "sql",
    "postgresql",
    "mysql",
    "mongodb",
    "redis",
    "graphql",
    "rest",
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "terraform",
    "jenkins",
    "git",
    "linux",
    "ci/cd",
    "machine learning",
    "data analysis",
    "pandas",
    "numpy",
    "tensorflow",
    "pytorch",
    "prompt engineering",
    "appsec",
    "bug bounty",
    "ctfs",
    "communication",
    "leadership",
    "problem solving",
    "collaboration",
]


SKILL_LABELS = {
    "aws": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
    "ci/cd": "CI/CD",
    "c++": "C++",
    "c#": "C#",
    "css": "CSS",
    "html": "HTML",
    "javascript": "JavaScript",
    "node": "Node.js",
    "node.js": "Node.js",
    "php": "PHP",
    "postgresql": "PostgreSQL",
    "appsec": "AppSec",
    "ctfs": "CTFs",
    "rest": "REST",
    "sql": "SQL",
    "typescript": "TypeScript",
}


def _empty_extraction() -> dict:
    return {
        "title": None,
        "company": None,
        "location": None,
        "location_type": None,
        "job_type": None,
        "salary_min": None,
        "salary_max": None,
        "salary_currency": "USD",
        "experience_min": None,
        "experience_max": None,
        "education": None,
        "required_skills": [],
        "preferred_skills": [],
    }


def _clean_value(value):
    if value is None:
        return None
    if isinstance(value, str):
        cleaned = re.sub(r"\s+", " ", value).strip(" \t:-|")
        if not cleaned or cleaned.lower() in {"n/a", "none", "null", "not specified"}:
            return None
        return cleaned
    return value


def _normalize_enum(value, allowed: set[str]) -> str | None:
    value = _clean_value(value)
    if not isinstance(value, str):
        return None

    normalized = value.lower().replace("_", "-").strip()
    normalized = re.sub(r"\s+", "-", normalized)
    aliases = {
        "fulltime": "full-time",
        "full-time": "full-time",
        "parttime": "part-time",
        "part-time": "part-time",
        "in-person": "onsite",
        "on-site": "onsite",
        "office": "onsite",
        "work-from-home": "remote",
    }
    normalized = aliases.get(normalized, normalized)
    return normalized if normalized in allowed else None


def _number(value) -> int | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        match = re.search(r"\d+(?:,\d{3})*(?:\.\d+)?", value)
        if match:
            number = float(match.group(0).replace(",", ""))
            suffix = value.lower()
            if re.search(r"\bk\b", suffix) or suffix.strip().endswith("k"):
                number *= 1000
            elif "lpa" in suffix or "lakh" in suffix:
                number *= 100000
            return int(number)
    return None


def _normalize_skills(value) -> list[dict]:
    if not isinstance(value, list):
        return []

    skills = []
    seen = set()
    for item in value:
        if isinstance(item, str):
            name = _clean_value(item)
            category = "other"
        elif isinstance(item, dict):
            name = _clean_value(item.get("name") or item.get("skill"))
            category = _clean_value(item.get("category")) or "other"
        else:
            continue

        if not name:
            continue
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        skills.append({"name": name, "category": category.lower()})
    return skills


def _normalize_extraction(data: dict | None) -> dict:
    normalized = _empty_extraction()
    if not isinstance(data, dict):
        return normalized

    normalized.update(
        {
            "title": _clean_value(data.get("title")),
            "company": _clean_value(data.get("company")),
            "location": _clean_value(data.get("location")),
            "location_type": _normalize_enum(
                data.get("location_type"), {"remote", "onsite", "hybrid"}
            ),
            "job_type": _normalize_enum(
                data.get("job_type"), {"full-time", "part-time", "contract", "internship"}
            ),
            "salary_min": _number(data.get("salary_min")),
            "salary_max": _number(data.get("salary_max")),
            "salary_currency": (_clean_value(data.get("salary_currency")) or "USD")[:3],
            "experience_min": _number(data.get("experience_min")),
            "experience_max": _number(data.get("experience_max")),
            "education": _clean_value(data.get("education")),
            "required_skills": _normalize_skills(data.get("required_skills")),
            "preferred_skills": _normalize_skills(data.get("preferred_skills")),
        }
    )
    return normalized


def _json_from_response(content: str) -> dict:
    content = content.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
    if fenced:
        content = fenced.group(1)
    else:
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1 and end > start:
            content = content[start : end + 1]

    return json.loads(content)


def _meaningful_lines(raw_text: str) -> list[str]:
    lines = [re.sub(r"\s+", " ", line).strip() for line in raw_text.splitlines()]
    skip_patterns = (
        "applied on",
        "application",
        "company info",
        "cookie",
        "job description",
        "privacy",
        "terms",
        "sign in",
        "login",
        "careers",
        "skip to",
        "navigation",
    )
    return [
        line
        for line in lines
        if len(line) > 2 and not any(pattern in line.lower() for pattern in skip_patterns)
    ]


def _looks_like_title(line: str) -> bool:
    return bool(
        re.search(
            r"\b(engineer|developer|manager|analyst|designer|specialist|consultant|intern|lead|architect|scientist)\b",
            line,
            re.IGNORECASE,
        )
    )


def _looks_like_company(line: str) -> bool:
    lower = line.lower()
    if not line or len(line) > 80:
        return False
    if _looks_like_title(line):
        return False
    return not bool(
        re.search(
            r"https?://|@|apply|benefits|description|hybrid|job|location|overview|remote|requirement|salary",
            lower,
        )
    )


def _field_from_patterns(text: str, patterns: list[str]) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            return _clean_value(match.group(1))
    return None


def _extract_salary(text: str) -> tuple[int | None, int | None, str]:
    currency = "USD"
    if re.search(r"₹|INR|LPA|lakhs?", text, re.IGNORECASE):
        currency = "INR"
    elif re.search(r"£|GBP", text, re.IGNORECASE):
        currency = "GBP"
    elif re.search(r"€|EUR", text, re.IGNORECASE):
        currency = "EUR"

    salary_match = re.search(
        r"(?:salary|compensation|pay)[^\n:$]*[:\s$₹£€]*(?:USD|INR|GBP|EUR)?\s*([\d,.]+)\s*(k|lpa|lakhs?)?"
        r"(?:\s*(?:-|–|to)\s*(?:USD|INR|GBP|EUR)?\s*[$₹£€]?([\d,.]+)\s*(k|lpa|lakhs?)?)?",
        text,
        re.IGNORECASE,
    )
    if not salary_match:
        salary_match = re.search(
            r"(?:USD|INR|GBP|EUR)?\s*[$]\s*([\d,.]+)\s*(k)?"
            r"(?:\s*(?:-|–|to)\s*(?:USD|INR|GBP|EUR)?\s*[$]?([\d,.]+)\s*(k)?)",
            text,
            re.IGNORECASE,
        )
    if not salary_match:
        return None, None, currency

    low = _number(salary_match.group(1))
    high = _number(salary_match.group(3))
    multiplier = 1
    suffixes = " ".join(group or "" for group in salary_match.groups()[1:]).lower()
    if "k" in suffixes:
        multiplier = 1000
    elif "lpa" in suffixes or "lakh" in suffixes:
        multiplier = 100000

    return (
        low * multiplier if low is not None else None,
        high * multiplier if high is not None else None,
        currency,
    )


def _skills_from_text(text: str) -> list[dict]:
    found = []
    lower = text.lower()
    for skill in SKILL_KEYWORDS:
        pattern = r"(?<![\w+#.])" + re.escape(skill.lower()) + r"(?![\w+#.])"
        if re.search(pattern, lower):
            category = "soft" if skill in {"communication", "leadership", "problem solving", "collaboration"} else "technical"
            found.append({"name": SKILL_LABELS.get(skill, skill.title()), "category": category})
    return _normalize_skills(found)


def _heuristic_extract(raw_text: str) -> dict:
    result = _empty_extraction()
    text = raw_text or ""
    lines = _meaningful_lines(text)
    compact_text = "\n".join(lines)

    result["title"] = _field_from_patterns(
        compact_text,
        [
            r"^\s*(?:job\s*title|position|role)\s*[:\-]\s*(.+)$",
            r"\b(?:hiring|opening)\s+(?:for\s+)?(?:an?\s+)?([A-Z][^\n,|]{3,80})",
        ],
    )
    result["company"] = _field_from_patterns(
        compact_text,
        [
            r"^\s*(?:company|organization|employer)\s*[:\-]\s*(.+)$",
            r"^\s*(?:at|with)\s+([A-Z][A-Za-z0-9&.,' -]{2,80})$",
        ],
    )
    result["location"] = _field_from_patterns(
        compact_text,
        [r"^\s*(?:location|work\s*location|job\s*location)\s*[:\-]\s*(.+)$"],
    )

    if not result["title"]:
        for line in lines[:12]:
            lower = line.lower()
            if (
                4 <= len(line) <= 90
                and not re.search(r"https?://|@|apply|about|overview|description", lower)
                and _looks_like_title(line)
            ):
                result["title"] = _clean_value(line)
                break

    if not result["company"]:
        if lines and result["title"] and _looks_like_company(lines[0]):
            result["company"] = _clean_value(lines[0])

    if not result["company"]:
        for index, line in enumerate(lines[:12]):
            if line.lower().startswith("about ") and len(line.split()) <= 6:
                result["company"] = _clean_value(line[6:])
                break
            if index > 0 and result["title"] and line != result["title"]:
                if _looks_like_company(line):
                    result["company"] = _clean_value(line)
                    break

    lowered = compact_text.lower()
    if "hybrid" in lowered:
        result["location_type"] = "hybrid"
    elif "remote" in lowered or "work from home" in lowered:
        result["location_type"] = "remote"
    elif "onsite" in lowered or "on-site" in lowered or "in office" in lowered:
        result["location_type"] = "onsite"

    if re.search(r"\bintern(ship)?\b", lowered):
        result["job_type"] = "internship"
    elif "contract" in lowered:
        result["job_type"] = "contract"
    elif "part-time" in lowered or "part time" in lowered:
        result["job_type"] = "part-time"
    elif "full-time" in lowered or "full time" in lowered:
        result["job_type"] = "full-time"

    result["salary_min"], result["salary_max"], result["salary_currency"] = _extract_salary(compact_text)

    exp_match = re.search(
        r"(\d+)\s*(?:\+|-\s*(\d+))?\s*(?:years?|yrs?)\s+(?:of\s+)?experience",
        compact_text,
        re.IGNORECASE,
    )
    if exp_match:
        result["experience_min"] = _number(exp_match.group(1))
        result["experience_max"] = _number(exp_match.group(2))

    education = _field_from_patterns(
        compact_text,
        [r"^\s*(?:education|degree)\s*[:\-]\s*(.+)$"],
    )
    if not education:
        degree_match = re.search(
            r"\b((?:bachelor(?:'s)?|master(?:'s)?|ph\.?d|doctorate|b\.?s\.?(?![a-z])|b\.?a\.?(?![a-z])|m\.?s\.?(?![a-z])|m\.?b\.?a\.?(?![a-z]))[^.\n]{0,80})\b",
            compact_text,
            re.IGNORECASE,
        )
        education = degree_match.group(1) if degree_match else None
    result["education"] = _clean_value(education)
    result["required_skills"] = _skills_from_text(compact_text)

    return _normalize_extraction(result)


def _extract_sync(raw_text: str) -> dict:
    fallback = _heuristic_extract(raw_text)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": EXTRACTION_PROMPT},
                {"role": "user", "content": f"Job Description:\n{raw_text}"},
            ],
            temperature=0.1,
            max_tokens=1500,
        )

        content = response.choices[0].message.content or ""
        extracted = _normalize_extraction(_json_from_response(content))
    except Exception as e:
        print("GROQ EXTRACTION FALLBACK:", type(e).__name__, str(e))
        return fallback

    for key, value in fallback.items():
        if extracted.get(key) in (None, [], "") and value not in (None, [], ""):
            extracted[key] = value

    return extracted


async def extract_job_details(raw_text: str) -> dict:
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _extract_sync, raw_text)
    return result
