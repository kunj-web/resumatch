import re
from urllib.parse import urlparse


SKILL_GROUPS = (
    ("Languages", ("javascript", "typescript", "python", "java", "c++", "c#", "sql")),
    ("Frontend", ("react", "next.js", "nextjs", "tailwind", "html", "css")),
    ("Backend", ("fastapi", "node", "express", "rest", "api", "sqlalchemy")),
    ("Databases", ("postgresql", "postgres", "mysql", "mongodb", "redis")),
    ("Tools", ("git", "docker", "postman", "alembic", "jwt", "auth")),
)

SKILL_MATCH_ORDER = ("Frontend", "Backend", "Databases", "Tools", "Languages")


def render_resume_content(
    content: dict,
    template_key: str,
    source_resume_text: str = "",
) -> dict:
    sections = content.get("tailored_sections") or {}
    job = content.get("job") or {}
    lines = _source_lines(source_resume_text)
    header = _extract_header(source_resume_text, job)
    header_urls = {link.get("url") for link in header.get("links", []) if link.get("url")}
    body_links = _extract_body_links(lines, header_urls)
    projects = _attach_links_to_items(
        _flatten_bullets(sections.get("project_bullets") or []),
        body_links,
        "projects",
    )
    experience = _attach_links_to_items(
        _flatten_bullets(sections.get("experience_bullets") or []),
        body_links,
        "experience",
    )

    return {
        "template_key": template_key,
        "header": header,
        "summary": _clean_text(sections.get("summary")),
        "skills": _group_skills(sections.get("skills") or []),
        "experience": experience,
        "projects": projects,
        "additional_links": _unmatched_links(body_links, projects + experience),
        "education": _extract_section_lines(source_resume_text, "education"),
        "section_order": _section_order(template_key),
    }


def _clean_text(value) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def _source_lines(source_resume_text: str) -> list[str]:
    return [
        line.strip()
        for line in (source_resume_text or "").splitlines()
        if line and line.strip()
    ]


def _extract_header(source_resume_text: str, job: dict) -> dict:
    lines = _source_lines(source_resume_text)
    header_lines = _header_lines(lines)
    header_text = "\n".join(header_lines)
    name = lines[0] if lines else "Candidate Name"

    emails = sorted(set(re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", header_text)))
    urls = _extract_urls(header_text, emails)
    phones = sorted(
        set(
            match.strip()
            for match in re.findall(
                r"(?:\+?\d[\d\s().-]{7,}\d)",
                header_text,
            )
        )
    )

    links = []
    for email in emails[:1]:
        links.append({"label": email, "url": f"mailto:{email}", "type": "email"})
    for phone in phones[:1]:
        links.append({"label": phone, "url": "", "type": "phone"})
    for url in urls[:4]:
        links.append({"label": _display_url(url), "url": url, "type": "url"})

    return {
        "name": name,
        "target_role": job.get("title") or "",
        "target_company": job.get("company") or "",
        "links": links,
    }


def _header_lines(lines: list[str]) -> list[str]:
    section_headings = {
        "summary",
        "profile",
        "skills",
        "technical skills",
        "experience",
        "projects",
        "education",
        "certifications",
    }
    header = []
    for line in lines[:12]:
        normalized = line.lower().strip(":")
        if normalized in section_headings and header:
            break
        header.append(line)
    return header


def _extract_urls(text: str, emails: list[str]) -> list[str]:
    email_domains = {email.split("@", 1)[1].lower() for email in emails if "@" in email}
    candidates = re.findall(
        r"(?:(?:https?://)?(?:www\.)?[\w.-]+\.[a-zA-Z]{2,}(?:/[\w./?%&=+#-]*)?)",
        text or "",
    )
    urls = []
    for candidate in candidates:
        if "@" in candidate:
            continue
        url = candidate.rstrip(".,;)")
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        domain = urlparse(url).netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        if domain in email_domains:
            continue
        if url not in urls:
            urls.append(url)
    return urls


def _extract_body_links(lines: list[str], header_urls: set[str]) -> list[dict]:
    links = []
    current_section = ""
    for line in lines:
        normalized = line.lower().strip(":")
        if normalized in {
            "summary",
            "profile",
            "skills",
            "technical skills",
            "experience",
            "projects",
            "education",
            "certifications",
        }:
            current_section = normalized
            continue

        for url in _extract_body_urls(line):
            if url in header_urls:
                continue
            link = {
                "label": _display_url(url),
                "url": url,
                "section": current_section,
                "source_line": line,
            }
            if link not in links:
                links.append(link)
    return links


def _extract_body_urls(text: str) -> list[str]:
    candidates = re.findall(
        r"(?:(?:https?://|www\.)?[\w.-]+\.[a-zA-Z]{2,}(?:/[\w./?%&=+#-]+)?)",
        text or "",
    )
    urls = []
    for candidate in candidates:
        if "@" in candidate:
            continue
        candidate = candidate.rstrip(".,;)")
        if not (
            candidate.startswith(("http://", "https://", "www."))
            or "/" in candidate
        ):
            continue
        url = candidate
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        if url not in urls:
            urls.append(url)
    return urls


def _display_url(url: str) -> str:
    parsed = urlparse(url)
    display = parsed.netloc + parsed.path
    if display.startswith("www."):
        display = display[4:]
    return display.rstrip("/")


def _group_skills(skills: list) -> list[dict]:
    grouped = {label: [] for label, _ in SKILL_GROUPS}
    other = []

    for skill in skills:
        clean_skill = _clean_text(skill)
        if not clean_skill:
            continue

        lower_skill = clean_skill.lower()
        matched_label = None
        for label in SKILL_MATCH_ORDER:
            keywords = next(
                group_keywords
                for group_label, group_keywords in SKILL_GROUPS
                if group_label == label
            )
            if any(keyword in lower_skill for keyword in keywords):
                matched_label = label
                break

        target = grouped[matched_label] if matched_label else other
        if clean_skill not in target:
            target.append(clean_skill)

    result = [
        {"label": label, "items": items}
        for label, _ in SKILL_GROUPS
        if (items := grouped[label])
    ]
    if other:
        result.append({"label": "Other", "items": other})
    return result


def _flatten_bullets(items: list) -> list[str]:
    bullets = []
    for item in items or []:
        if isinstance(item, dict):
            value = item.get("revised") or item.get("original")
        else:
            value = item

        clean_value = _clean_text(value)
        if clean_value:
            bullets.append(clean_value)
    return bullets


def _attach_links_to_items(items: list[str], links: list[dict], section_key: str) -> list[dict]:
    normalized_section = "projects" if section_key == "projects" else "experience"
    result = []
    for item in items:
        item_links = [
            link
            for link in links
            if _link_matches_item(link, item, normalized_section)
        ]
        result.append({"text": item, "links": _dedupe_links(item_links)})
    return result


def _link_matches_item(link: dict, item: str, section_key: str) -> bool:
    link_section = (link.get("section") or "").lower()
    if section_key == "projects" and "project" in link_section:
        return True
    if section_key == "experience" and "experience" in link_section:
        return True

    source_words = set(re.findall(r"[a-z0-9]+", (link.get("source_line") or "").lower()))
    item_words = set(re.findall(r"[a-z0-9]+", (item or "").lower()))
    return len(source_words & item_words) >= 2


def _dedupe_links(links: list[dict]) -> list[dict]:
    seen = set()
    deduped = []
    for link in links:
        url = link.get("url")
        if not url or url in seen:
            continue
        seen.add(url)
        deduped.append({"label": link.get("label") or url, "url": url})
    return deduped


def _unmatched_links(links: list[dict], items: list[dict]) -> list[dict]:
    used_urls = {
        link.get("url")
        for item in items
        for link in item.get("links", [])
        if link.get("url")
    }
    return _dedupe_links([link for link in links if link.get("url") not in used_urls])


def _extract_section_lines(source_resume_text: str, section_name: str) -> list[str]:
    lines = _source_lines(source_resume_text)
    start = None
    heading_pattern = re.compile(r"^[A-Z][A-Z\s&/-]{2,}$")

    for index, line in enumerate(lines):
        if line.lower().strip(":") == section_name:
            start = index + 1
            break

    if start is None:
        return []

    collected = []
    for line in lines[start:]:
        if heading_pattern.match(line) and collected:
            break
        collected.append(line)
        if len(collected) >= 4:
            break
    return collected


def _section_order(template_key: str) -> list[str]:
    if template_key == "technical":
        return ["skills", "projects", "experience", "education"]
    if template_key == "executive":
        return ["summary", "experience", "skills", "projects", "education"]
    return ["summary", "skills", "projects", "experience", "education"]
