from io import BytesIO
from textwrap import wrap

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor


CONTENT_TYPES = {
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "pdf": "application/pdf",
}

SECTION_TITLES = {
    "summary": "SUMMARY",
    "skills": "TECHNICAL SKILLS",
    "projects": "PROJECTS",
    "experience": "EXPERIENCE",
    "education": "EDUCATION",
}


def generate_resume_document(
    rendered_content: dict, template_key: str, output_format: str
) -> bytes:
    if output_format == "docx":
        return _generate_docx(rendered_content, template_key)
    if output_format == "pdf":
        return _generate_pdf(rendered_content, template_key)
    raise ValueError("Unsupported output format")


def get_content_type(output_format: str) -> str:
    return CONTENT_TYPES[output_format]


def _template_settings(template_key: str) -> dict:
    if template_key == "compact":
        return {"font_size": 9.5, "bullet_size": 9.25, "margin": 0.45}
    if template_key == "executive":
        return {"font_size": 10.5, "bullet_size": 10.25, "margin": 0.65}
    return {"font_size": 10.0, "bullet_size": 9.75, "margin": 0.6}


def _section_order(rendered_content: dict) -> list[str]:
    return rendered_content.get("section_order") or [
        "summary",
        "skills",
        "projects",
        "experience",
        "education",
    ]


def _generate_docx(rendered_content: dict, template_key: str) -> bytes:
    settings = _template_settings(template_key)
    document = Document()
    section = document.sections[0]
    margin = Inches(settings["margin"])
    section.top_margin = margin
    section.bottom_margin = margin
    section.left_margin = margin
    section.right_margin = margin

    styles = document.styles
    styles["Normal"].font.name = "Calibri"
    styles["Normal"].font.size = Pt(settings["font_size"])
    styles["Heading 1"].font.name = "Calibri"
    styles["Heading 1"].font.size = Pt(11.5)
    styles["Heading 1"].font.bold = True
    styles["Heading 1"].font.color.rgb = RGBColor(31, 41, 55)

    _add_docx_header(document, rendered_content.get("header") or {})

    for section_key in _section_order(rendered_content):
        if section_key == "summary":
            _add_docx_summary(document, rendered_content.get("summary"))
        elif section_key == "skills":
            _add_docx_skills(document, rendered_content.get("skills") or [])
        elif section_key in {"projects", "experience"}:
            _add_docx_bullets(
                document,
                SECTION_TITLES[section_key],
                rendered_content.get(section_key) or [],
                settings["bullet_size"],
            )
        elif section_key == "education":
            _add_docx_lines(
                document,
                SECTION_TITLES[section_key],
                rendered_content.get("education") or [],
            )

    _add_docx_links(document, rendered_content.get("additional_links") or [])

    output = BytesIO()
    document.save(output)
    return output.getvalue()


def _add_docx_header(document: Document, header: dict) -> None:
    name = header.get("name") or "Candidate Name"
    title = document.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run(name)
    run.bold = True
    run.font.size = Pt(18)

    role_bits = [
        value
        for value in [header.get("target_role"), header.get("target_company")]
        if value
    ]
    if role_bits:
        role = document.add_paragraph(" at ".join(role_bits))
        role.alignment = WD_ALIGN_PARAGRAPH.CENTER
        role.runs[0].font.size = Pt(10)
        role.runs[0].font.color.rgb = RGBColor(75, 85, 99)

    links = header.get("links") or []
    if links:
        link_paragraph = document.add_paragraph()
        link_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for index, link in enumerate(links):
            if index:
                separator = link_paragraph.add_run(" | ")
                separator.font.color.rgb = RGBColor(156, 163, 175)
            run = link_paragraph.add_run(link.get("label") or "")
            run.font.size = Pt(9)
            run.font.color.rgb = RGBColor(55, 65, 81)


def _add_docx_heading(document: Document, title: str) -> None:
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.space_before = Pt(8)
    paragraph.paragraph_format.space_after = Pt(3)
    run = paragraph.add_run(title)
    run.bold = True
    run.font.size = Pt(10.5)
    run.font.color.rgb = RGBColor(17, 24, 39)


def _add_docx_summary(document: Document, summary: str) -> None:
    if not summary:
        return
    _add_docx_heading(document, SECTION_TITLES["summary"])
    paragraph = document.add_paragraph(summary)
    paragraph.paragraph_format.space_after = Pt(2)


def _add_docx_skills(document: Document, skills: list[dict]) -> None:
    if not skills:
        return
    _add_docx_heading(document, SECTION_TITLES["skills"])
    table = document.add_table(rows=0, cols=2)
    for group in skills:
        row = table.add_row()
        label_cell = row.cells[0]
        value_cell = row.cells[1]
        label_cell.width = Inches(1.1)
        value_cell.width = Inches(5.8)

        label_paragraph = label_cell.paragraphs[0]
        label_paragraph.paragraph_format.space_after = Pt(1)
        label = label_paragraph.add_run(f"{group['label']}:")
        label.bold = True
        label.font.size = Pt(9.75)

        value_paragraph = value_cell.paragraphs[0]
        value_paragraph.paragraph_format.space_after = Pt(1)
        values = value_paragraph.add_run(", ".join(group["items"]))
        values.font.size = Pt(9.75)


def _add_docx_bullets(
    document: Document, title: str, bullets: list, bullet_size: float
) -> None:
    if not bullets:
        return
    _add_docx_heading(document, title)
    for bullet in bullets:
        text, links = _item_text_and_links(bullet)
        paragraph = document.add_paragraph(text, style="List Bullet")
        paragraph.paragraph_format.space_after = Pt(1)
        paragraph.runs[0].font.size = Pt(bullet_size)
        if links:
            link_text = paragraph.add_run(f" ({_links_text(links)})")
            link_text.font.size = Pt(bullet_size)
            link_text.font.color.rgb = RGBColor(55, 65, 81)


def _add_docx_lines(document: Document, title: str, lines: list[str]) -> None:
    if not lines:
        return
    _add_docx_heading(document, title)
    for line in lines:
        paragraph = document.add_paragraph(line)
        paragraph.paragraph_format.space_after = Pt(1)


def _add_docx_links(document: Document, links: list[dict]) -> None:
    if not links:
        return
    _add_docx_heading(document, "LINKS")
    for link in links:
        paragraph = document.add_paragraph(link.get("label") or link.get("url") or "")
        paragraph.paragraph_format.space_after = Pt(1)


def _pdf_lines(rendered_content: dict) -> list[tuple[str, str]]:
    header = rendered_content.get("header") or {}
    lines: list[tuple[str, str]] = [
        ("name", header.get("name") or "Candidate Name"),
    ]

    role_bits = [
        value
        for value in [header.get("target_role"), header.get("target_company")]
        if value
    ]
    if role_bits:
        lines.append(("meta", " at ".join(role_bits)))

    links = [link.get("label") for link in header.get("links") or [] if link.get("label")]
    if links:
        lines.append(("meta", " | ".join(links)))

    for section_key in _section_order(rendered_content):
        if section_key == "summary" and rendered_content.get("summary"):
            lines.append(("heading", SECTION_TITLES["summary"]))
            lines.extend(("paragraph", line) for line in wrap(rendered_content["summary"], 96))
        elif section_key == "skills" and rendered_content.get("skills"):
            lines.append(("heading", SECTION_TITLES["skills"]))
            for group in rendered_content["skills"]:
                label = f"{group['label']}:"
                values = ", ".join(group["items"])
                lines.append(("paragraph", f"{label:<14} {values}"))
        elif section_key in {"projects", "experience"} and rendered_content.get(section_key):
            lines.append(("heading", SECTION_TITLES[section_key]))
            for bullet in rendered_content[section_key]:
                text, links = _item_text_and_links(bullet)
                if links:
                    text = f"{text} ({_links_text(links)})"
                wrapped = wrap(text, width=92)
                if wrapped:
                    lines.append(("bullet", wrapped[0]))
                    lines.extend(("indent", line) for line in wrapped[1:])
        elif section_key == "education" and rendered_content.get("education"):
            lines.append(("heading", SECTION_TITLES["education"]))
            lines.extend(("paragraph", line) for line in rendered_content["education"])

    if rendered_content.get("additional_links"):
        lines.append(("heading", "LINKS"))
        for link in rendered_content["additional_links"]:
            lines.append(("paragraph", link.get("label") or link.get("url") or ""))

    return lines


def _item_text_and_links(item) -> tuple[str, list[dict]]:
    if isinstance(item, dict):
        return item.get("text") or "", item.get("links") or []
    return str(item), []


def _links_text(links: list[dict]) -> str:
    return " | ".join(link.get("label") or link.get("url") or "" for link in links)


def _escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _generate_pdf(rendered_content: dict, template_key: str) -> bytes:
    content_lines = _pdf_lines(rendered_content)
    pages = []
    current_page: list[tuple[str, str]] = []

    for line in content_lines:
        current_page.append(line)
        if len(current_page) >= 52:
            pages.append(current_page)
            current_page = []
    if current_page:
        pages.append(current_page)

    objects: list[bytes] = []
    page_refs = []

    def add_object(body: str | bytes) -> int:
        if isinstance(body, str):
            body = body.encode("latin-1", errors="replace")
        objects.append(body)
        return len(objects)

    catalog_id = add_object("<< /Type /Catalog /Pages 2 0 R >>")
    pages_id = add_object(b"")
    font_id = add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>")
    bold_font_id = add_object(
        "<< /Type /Font /Subtype /Type1 /BaseFont /Courier-Bold >>"
    )

    for page_lines in pages:
        commands = ["BT", "50 762 Td", "13 TL"]
        for line_type, text in page_lines:
            if line_type == "name":
                commands.extend(["/F2 17 Tf", f"({_escape_pdf_text(text)}) Tj", "T*"])
            elif line_type == "heading":
                commands.extend(["T*", "/F2 10 Tf", f"({_escape_pdf_text(text)}) Tj", "T*"])
            elif line_type == "bullet":
                commands.extend(["/F1 9.5 Tf", f"(- {_escape_pdf_text(text)}) Tj", "T*"])
            elif line_type == "indent":
                commands.extend(["/F1 9.5 Tf", f"(  {_escape_pdf_text(text)}) Tj", "T*"])
            else:
                commands.extend(["/F1 9.5 Tf", f"({_escape_pdf_text(text)}) Tj", "T*"])
        commands.append("ET")

        stream = "\n".join(commands).encode("latin-1", errors="replace")
        content_id = add_object(
            b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n"
            + stream
            + b"\nendstream"
        )
        page_id = add_object(
            f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 {font_id} 0 R /F2 {bold_font_id} 0 R >> >> "
            f"/Contents {content_id} 0 R >>"
        )
        page_refs.append(page_id)

    kids = " ".join(f"{page_id} 0 R" for page_id in page_refs)
    objects[pages_id - 1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_refs)} >>".encode(
        "latin-1"
    )

    output = BytesIO()
    output.write(b"%PDF-1.4\n")
    offsets = [0]
    for index, body in enumerate(objects, start=1):
        offsets.append(output.tell())
        output.write(f"{index} 0 obj\n".encode("ascii"))
        output.write(body)
        output.write(b"\nendobj\n")

    xref_offset = output.tell()
    output.write(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.write(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.write(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.write(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF"
        ).encode("ascii")
    )
    return output.getvalue()
