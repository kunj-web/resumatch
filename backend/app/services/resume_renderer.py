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
PROFILE_URL_KEYWORDS = ("linkedin", "github", "portfolio")


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
    original_projects = _extract_original_projects(lines)
    projects = _normalize_projects(
        sections.get("projects") or [],
        sections.get("project_bullets") or [],
        body_links,
        original_projects,
    )
    experience = _normalize_experience(
        sections.get("experience") or [],
        sections.get("experience_bullets") or [],
        body_links,
    )
    education = _normalize_education(
        sections.get("education") or [],
        _extract_section_lines(source_resume_text, "education"),
    )
    extra_sections = _extract_extra_sections(source_resume_text)

    return {
        "template_key": template_key,
        "header": header,
        "summary": _clean_text(sections.get("summary")),
        "skills": _group_skills(sections.get("skills") or []),
        "experience": experience,
        "projects": projects,
        "additional_links": _unmatched_links(body_links, projects + experience),
        "education": education,
        "extra_sections": extra_sections,
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
    urls = _dedupe_values(
        _extract_urls(header_text, emails)
        + _extract_profile_urls(lines, emails)
    )
    phones = sorted(
        set(
            match.strip()
            for match in re.findall(
                r"(?:\+?\d[\d\s().-]{7,}\d)",
                header_text,
            )
        )
    )
    location = _extract_location(header_lines, emails, phones)

    links = []
    if location:
        links.append({"label": location, "url": "", "type": "location"})
    for email in emails[:1]:
        links.append({"label": email, "url": f"mailto:{email}", "type": "email"})
    for phone in phones[:1]:
        links.append({"label": phone, "url": _phone_url(phone), "type": "phone"})
    for url in urls:
        links.append(
            {
                "label": _profile_link_label(url),
                "url": url,
                "type": _profile_link_type(url),
            }
        )

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


def _extract_profile_urls(lines: list[str], emails: list[str]) -> list[str]:
    urls = []
    email_domains = {email.split("@", 1)[1].lower() for email in emails if "@" in email}
    current_section = ""

    for line in lines:
        normalized = line.lower().strip(":")
        if _is_section_heading(normalized):
            current_section = normalized
            continue

        lower_line = line.lower()
        if current_section and current_section not in {"", "summary", "profile"}:
            if not any(keyword in lower_line for keyword in ("linkedin", "portfolio")):
                continue

        if not any(keyword in lower_line for keyword in PROFILE_URL_KEYWORDS):
            continue

        for url in _extract_body_urls(line):
            domain = urlparse(url).netloc.lower().removeprefix("www.")
            if domain in email_domains:
                continue
            if _is_profile_url(url, lower_line) and url not in urls:
                urls.append(url)

    return urls


def _is_profile_url(url: str, source_line: str = "") -> bool:
    parsed = urlparse(url)
    domain = parsed.netloc.lower().removeprefix("www.")
    path_parts = [part for part in parsed.path.strip("/").split("/") if part]

    if "linkedin.com" in domain:
        return True
    if any(keyword in source_line for keyword in ("portfolio", "netlify", "vercel")):
        return True
    if "github.com" in domain:
        return len(path_parts) <= 1 or "github" in source_line and not _looks_like_project_line(source_line)
    return "portfolio" in source_line


def _looks_like_project_line(line: str) -> bool:
    return bool(re.search(r"\b(api|app|platform|system|tool|project|saas)\b", line.lower()))


def _extract_body_links(lines: list[str], header_urls: set[str]) -> list[dict]:
    links = []
    current_section = ""
    for index, line in enumerate(lines):
        normalized = line.lower().strip(":")
        if _is_section_heading(normalized):
            current_section = normalized
            continue

        for url in _extract_body_urls(line):
            if url in header_urls:
                continue
            link = {
                "label": _body_link_label(url, line),
                "url": url,
                "section": current_section,
                "source_line": line,
                "source_index": index,
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


def _profile_link_type(url: str) -> str:
    display = _display_url(url).lower()
    if "linkedin" in display:
        return "linkedin"
    if "github" in display:
        return "github"
    return "portfolio"


def _profile_link_label(url: str) -> str:
    link_type = _profile_link_type(url)
    if link_type == "linkedin":
        return "LinkedIn"
    if link_type == "github":
        return "GitHub"
    return "Portfolio"


def _body_link_label(url: str, source_line: str = "") -> str:
    lower_line = source_line.lower()
    display = _display_url(url).lower()
    if "github" in lower_line or "github.com" in display:
        return "GitHub"
    if "demo" in lower_line or "live" in lower_line:
        return "Live"
    if "portfolio" in lower_line:
        return "Portfolio"
    return _display_url(url)


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


def _normalize_projects(
    projects: list,
    fallback_bullets: list,
    links: list[dict],
    original_projects: list[dict],
) -> list[dict]:
    normalized = []
    for project in projects:
        if not isinstance(project, dict):
            continue

        name = _clean_text(project.get("name"))
        project_links = _dedupe_links(project.get("links") or [])
        bullets = _bullet_objects(project.get("bullets") or [])
        bullets = _merge_original_project_bullets(name, bullets, original_projects)
        tech_stack = [_clean_text(item) for item in project.get("tech_stack") or []]
        tech_stack = [item for item in tech_stack if item]

        matched_links = _project_links_for_entry(name, links)
        project_links = _dedupe_links(project_links + matched_links)

        if name or bullets or project_links or tech_stack:
            normalized.append(
                {
                    "kind": "project",
                    "title": name,
                    "meta": ", ".join(tech_stack),
                    "links": project_links,
                    "bullets": bullets,
                }
            )

    if normalized:
        normalized = _append_missing_original_projects(normalized, original_projects, links)
        return normalized

    return [
        {
            "kind": "project",
            "title": "",
            "meta": "",
            "links": item["links"],
            "bullets": [{"text": item["text"], "links": []}],
        }
        for item in _attach_links_to_items(
            _flatten_bullets(fallback_bullets),
            links,
            "projects",
        )
    ] or _projects_from_original_resume(original_projects, links)


def _normalize_experience(
    entries: list,
    fallback_bullets: list,
    links: list[dict],
) -> list[dict]:
    normalized = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue

        role = _clean_text(entry.get("role"))
        company = _clean_text(entry.get("company"))
        location = _clean_text(entry.get("location"))
        dates = _clean_text(entry.get("dates"))
        bullets = _bullet_objects(entry.get("bullets") or [])
        title = " - ".join(part for part in [role, company] if part)
        meta = " | ".join(part for part in [location, dates] if part)

        matched_links = [
            link
            for link in links
            if "experience" in (link.get("section") or "")
        ]

        if title or meta or bullets or matched_links:
            normalized.append(
                {
                    "kind": "experience",
                    "title": title,
                    "meta": meta,
                    "links": _dedupe_links(matched_links),
                    "bullets": bullets,
                }
            )

    if normalized:
        return normalized

    return [
        {
            "kind": "experience",
            "title": "",
            "meta": "",
            "links": item["links"],
            "bullets": [{"text": item["text"], "links": []}],
        }
        for item in _attach_links_to_items(
            _flatten_bullets(fallback_bullets),
            links,
            "experience",
        )
    ]


def _normalize_education(entries: list, fallback_lines: list[str]) -> list[dict]:
    normalized = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue

        institution = _clean_text(entry.get("institution"))
        degree = _clean_text(entry.get("degree"))
        location = _clean_text(entry.get("location"))
        dates = _clean_text(entry.get("dates"))
        details = [_clean_text(item) for item in entry.get("details") or []]
        details = [item for item in details if item]

        if institution or degree or location or dates or details:
            normalized.append(
                {
                    "institution": institution,
                    "degree": degree,
                    "meta": " | ".join(part for part in [location, dates] if part),
                    "details": details,
                }
            )

    if normalized:
        return normalized

    return [{"raw": line} for line in fallback_lines]


def _bullet_objects(items: list) -> list[dict]:
    bullets = []
    for item in items:
        if isinstance(item, dict):
            text = _clean_text(item.get("revised") or item.get("text") or item.get("original"))
            links = _dedupe_links(item.get("links") or [])
        else:
            text = _clean_text(item)
            links = []

        if text:
            bullets.append({"text": text, "links": links})
    return bullets


def _extract_original_projects(lines: list[str]) -> list[dict]:
    project_lines = _section_body_lines(lines, "projects")
    projects = []
    current = None

    for line in project_lines:
        if _is_link_annotation_line(line):
            continue

        if _is_bullet_line(line):
            bullet = _clean_bullet_line(line)
            if bullet and current:
                current["bullets"].append(bullet)
            continue

        if current and current["bullets"] and not _looks_like_project_title(line):
            current["bullets"][-1] = _clean_text(f"{current['bullets'][-1]} {line}")
            continue

        if _looks_like_project_title(line):
            if current:
                projects.append(current)
            name, tech_stack = _parse_project_title(line)
            current = {"name": name, "tech_stack": tech_stack, "bullets": []}
            continue

    if current:
        projects.append(current)

    return [project for project in projects if project.get("name") or project.get("bullets")]


def _section_body_lines(lines: list[str], section_name: str) -> list[str]:
    collected = []
    in_section = False
    for line in lines:
        normalized = line.lower().strip(":")
        if normalized == section_name:
            in_section = True
            continue
        if in_section and _is_section_heading(normalized):
            break
        if in_section:
            collected.append(line)
    return collected


def _is_link_annotation_line(line: str) -> bool:
    lower_line = line.lower()
    return (
        "mailto:" in lower_line
        or "tel:" in lower_line
        or bool(_extract_body_urls(line))
    )


def _is_bullet_line(line: str) -> bool:
    stripped = line.strip()
    return bool(re.match(r"^(?:[•*.-]|\(cid:\d+\))\s+", stripped))


def _clean_bullet_line(line: str) -> str:
    return _clean_text(re.sub(r"^(?:[•*.-]|\(cid:\d+\))\s+", "", line.strip()))


def _looks_like_project_title(line: str) -> bool:
    stripped = line.strip()
    if not stripped or not stripped[0].isupper():
        return False
    if _extract_body_urls(line):
        return True
    if re.search(r"\b(GitHub|Live|Demo|Portfolio)\b", line, flags=re.I):
        return True
    if re.search(r"\([^)]{2,}\)", line):
        return True
    return False


def _parse_project_title(line: str) -> tuple[str, list[str]]:
    without_links = re.sub(r"https?://\S+|www\.\S+", "", line)
    without_labels = re.sub(r"\b(?:GitHub|Live|Demo|Portfolio)\b", "", without_links, flags=re.I)
    match = re.search(r"\(([^)]*)\)", without_labels)
    tech_stack = []
    if match:
        tech_stack = [
            _clean_text(item)
            for item in re.split(r",|/", match.group(1))
            if _clean_text(item)
        ]
        name = _clean_text(without_labels[: match.start()])
    else:
        name = _clean_text(without_labels)

    name = re.sub(r"[§|#]+", "", name).strip()
    return name, tech_stack


def _merge_original_project_bullets(
    name: str, bullets: list[dict], original_projects: list[dict]
) -> list[dict]:
    original_project = _matching_original_project(name, original_projects)
    if not original_project:
        return bullets

    original_bullets = original_project.get("bullets") or []
    if len(bullets) < len(original_bullets):
        merged = list(bullets)
        for original_bullet in original_bullets[len(bullets) :]:
            merged.append({"text": original_bullet, "links": []})
        return merged

    merged = list(bullets)
    for original_bullet in original_bullets:
        if not _bullet_already_preserved(original_bullet, merged):
            merged.append({"text": original_bullet, "links": []})
    return merged


def _append_missing_original_projects(
    normalized: list[dict], original_projects: list[dict], links: list[dict]
) -> list[dict]:
    result = list(normalized)
    existing_names = [_clean_text(project.get("title")).lower() for project in result]
    for original_project in original_projects:
        name = _clean_text(original_project.get("name"))
        if not name:
            continue
        if any(name.lower() == existing or name.lower() in existing for existing in existing_names):
            continue
        result.append(_original_project_entry(original_project, links))
    return result


def _projects_from_original_resume(
    original_projects: list[dict], links: list[dict]
) -> list[dict]:
    return [_original_project_entry(project, links) for project in original_projects]


def _original_project_entry(project: dict, links: list[dict]) -> dict:
    name = _clean_text(project.get("name"))
    matched_links = _project_links_for_entry(name, links)
    return {
        "kind": "project",
        "title": name,
        "meta": ", ".join(project.get("tech_stack") or []),
        "links": _dedupe_links(matched_links),
        "bullets": [
            {"text": bullet, "links": []}
            for bullet in project.get("bullets") or []
            if _clean_text(bullet)
        ],
    }


def _matching_original_project(name: str, original_projects: list[dict]) -> dict | None:
    clean_name = _clean_text(name).lower()
    if not clean_name:
        return None
    name_words = _significant_words(clean_name)
    for project in original_projects:
        project_name = _clean_text(project.get("name")).lower()
        if clean_name == project_name or clean_name in project_name or project_name in clean_name:
            return project
        if name_words and len(name_words & _significant_words(project_name)) >= 1:
            return project
    return None


def _bullet_already_preserved(original_bullet: str, bullets: list[dict]) -> bool:
    original_words = _significant_words(original_bullet)
    for bullet in bullets:
        candidate_words = _significant_words(bullet.get("text") or "")
        if not original_words:
            continue
        overlap = len(original_words & candidate_words)
        if overlap >= min(5, max(2, len(original_words) // 2)):
            return True
    return False


def _link_matches_item(link: dict, item: str, section_key: str) -> bool:
    link_section = (link.get("section") or "").lower()
    if section_key == "projects" and "project" in link_section:
        return True
    if section_key == "experience" and "experience" in link_section:
        return True

    source_words = set(re.findall(r"[a-z0-9]+", (link.get("source_line") or "").lower()))
    item_words = set(re.findall(r"[a-z0-9]+", (item or "").lower()))
    return len(source_words & item_words) >= 2


def _project_links_for_entry(name: str, links: list[dict]) -> list[dict]:
    if not name:
        return []

    name_words = _significant_words(name)
    matched = []
    for link in links:
        link_section = (link.get("section") or "").lower()
        if "project" not in link_section:
            continue

        source_line = (link.get("source_line") or "").lower()
        source_words = _significant_words(source_line)
        if name.lower() in source_line or len(name_words & source_words) >= 1:
            matched.append(link)

    return matched


def _significant_words(value: str) -> set[str]:
    ignored = {"the", "and", "with", "using", "project", "github", "live", "demo"}
    return {
        word
        for word in re.findall(r"[a-z0-9]+", (value or "").lower())
        if len(word) >= 3 and word not in ignored
    }


def _extract_location(
    header_lines: list[str], emails: list[str], phones: list[str]
) -> str:
    for line in header_lines:
        if not any(email in line for email in emails) and not any(
            phone in line for phone in phones
        ):
            continue

        cleaned = line
        for email in emails:
            cleaned = cleaned.replace(email, "")
        for phone in phones:
            cleaned = cleaned.replace(phone, "")
        cleaned = re.sub(r"\(cid:\d+\)", " ", cleaned)
        cleaned = re.sub(r"[+#|§]+", " ", cleaned)
        cleaned = _clean_text(cleaned)
        if cleaned and not _extract_body_urls(cleaned):
            return cleaned.strip(" -")
    return ""


def _phone_url(phone: str) -> str:
    digits = re.sub(r"[^\d+]", "", phone)
    if not digits:
        return ""
    if not digits.startswith("+"):
        digits = f"+{digits}"
    return f"tel:{digits}"


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


def _dedupe_values(values: list[str]) -> list[str]:
    deduped = []
    for value in values:
        if value and value not in deduped:
            deduped.append(value)
    return deduped


def _is_section_heading(normalized_line: str) -> bool:
    return normalized_line in {
        "summary",
        "profile",
        "skills",
        "technical skills",
        "experience",
        "projects",
        "education",
        "certifications",
    }


def _unmatched_links(links: list[dict], items: list[dict]) -> list[dict]:
    used_urls = {
        link.get("url")
        for item in items
        for link in (
            item.get("links", [])
            + [
                bullet_link
                for bullet in item.get("bullets", [])
                for bullet_link in bullet.get("links", [])
            ]
        )
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


def _extract_extra_sections(source_resume_text: str) -> list[dict]:
    known_sections = {
        "summary",
        "profile",
        "skills",
        "technical skills",
        "experience",
        "work experience",
        "professional experience",
        "projects",
        "education",
    }
    allowed_sections = {
        "certifications",
        "certificates",
        "achievements",
        "awards",
        "publications",
        "volunteering",
        "leadership",
        "coursework",
        "additional information",
    }
    lines = _source_lines(source_resume_text)
    sections = []
    current_title = ""
    current_lines = []

    for line in lines:
        normalized = line.lower().strip(":")
        if normalized in known_sections or normalized in allowed_sections:
            if current_title and current_lines:
                sections.append(
                    {"title": current_title, "items": _clean_section_items(current_lines)}
                )
            current_title = line.strip(":")
            current_lines = []
            continue

        if current_title:
            current_lines.append(line)

    if current_title and current_lines:
        sections.append({"title": current_title, "items": _clean_section_items(current_lines)})

    return [
        section
        for section in sections
        if section["title"].lower() in allowed_sections and section["items"]
    ]


def _clean_section_items(lines: list[str]) -> list[str]:
    items = []
    for line in lines:
        clean_line = _clean_text(re.sub(r"^[•*.-]\s*", "", line))
        if clean_line and clean_line not in items:
            items.append(clean_line)
    return items[:8]


def _section_order(template_key: str) -> list[str]:
    if template_key == "technical":
        return ["skills", "projects", "experience", "education"]
    if template_key == "executive":
        return ["summary", "experience", "skills", "projects", "education"]
    return ["summary", "skills", "projects", "experience", "education"]
