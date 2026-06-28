from io import BytesIO
from textwrap import wrap

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt


CONTENT_TYPES = {
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "pdf": "application/pdf",
}


def generate_resume_document(content: dict, template_key: str, output_format: str) -> bytes:
    if output_format == "docx":
        return _generate_docx(content, template_key)
    if output_format == "pdf":
        return _generate_pdf(content, template_key)
    raise ValueError("Unsupported output format")


def get_content_type(output_format: str) -> str:
    return CONTENT_TYPES[output_format]


def _get_sections(content: dict) -> dict:
    return content.get("tailored_sections") or {}


def _flatten_bullets(items: list) -> list[str]:
    bullets = []
    for item in items or []:
        if isinstance(item, dict):
            value = item.get("revised") or item.get("original")
        else:
            value = str(item)
        if value:
            bullets.append(value.strip())
    return bullets


def _document_lines(content: dict) -> list[tuple[str, str]]:
    sections = _get_sections(content)
    lines: list[tuple[str, str]] = []

    summary = sections.get("summary")
    if summary:
        lines.append(("heading", "Professional Summary"))
        lines.append(("paragraph", summary))

    skills = [skill for skill in sections.get("skills") or [] if skill]
    if skills:
        lines.append(("heading", "Skills"))
        lines.append(("paragraph", ", ".join(skills)))

    experience_bullets = _flatten_bullets(sections.get("experience_bullets") or [])
    if experience_bullets:
        lines.append(("heading", "Experience"))
        for bullet in experience_bullets:
            lines.append(("bullet", bullet))

    project_bullets = _flatten_bullets(sections.get("project_bullets") or [])
    if project_bullets:
        lines.append(("heading", "Projects"))
        for bullet in project_bullets:
            lines.append(("bullet", bullet))

    ats_fixes = [fix for fix in content.get("ats_fixes") or [] if fix]
    if ats_fixes:
        lines.append(("heading", "Additional ATS Notes"))
        for fix in ats_fixes:
            lines.append(("bullet", fix))

    return lines


def _generate_docx(content: dict, template_key: str) -> bytes:
    document = Document()
    section = document.sections[0]
    section.top_margin = Inches(0.55)
    section.bottom_margin = Inches(0.55)
    section.left_margin = Inches(0.65)
    section.right_margin = Inches(0.65)

    styles = document.styles
    styles["Normal"].font.name = "Calibri"
    styles["Normal"].font.size = Pt(10.5)
    styles["Heading 1"].font.name = "Calibri"
    styles["Heading 1"].font.size = Pt(13)
    styles["Heading 1"].font.bold = True

    if template_key in {"executive", "modern_professional"}:
        title = document.add_paragraph()
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = title.add_run("Tailored Resume")
        run.bold = True
        run.font.size = Pt(15)

    for line_type, text in _document_lines(content):
        if line_type == "heading":
            document.add_heading(text, level=1)
        elif line_type == "bullet":
            document.add_paragraph(text, style="List Bullet")
        else:
            document.add_paragraph(text)

    output = BytesIO()
    document.save(output)
    return output.getvalue()


def _escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _generate_pdf(content: dict, template_key: str) -> bytes:
    text_lines: list[str] = []
    if template_key in {"executive", "modern_professional"}:
        text_lines.extend(["Tailored Resume", ""])

    for line_type, text in _document_lines(content):
        if line_type == "heading":
            text_lines.extend(["", text.upper()])
        elif line_type == "bullet":
            text_lines.extend(f"- {line}" for line in wrap(text, width=92))
        else:
            text_lines.extend(wrap(text, width=96))

    if not text_lines:
        text_lines = ["Tailored Resume"]

    pages = []
    current_page: list[str] = []
    for line in text_lines:
        current_page.append(line)
        if len(current_page) >= 48:
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
    font_id = add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    for page_lines in pages:
        commands = ["BT", "/F1 10 Tf", "50 760 Td", "14 TL"]
        for line in page_lines:
            commands.append(f"({_escape_pdf_text(line)}) Tj")
            commands.append("T*")
        commands.append("ET")
        stream = "\n".join(commands).encode("latin-1", errors="replace")
        content_id = add_object(
            b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n"
            + stream
            + b"\nendstream"
        )
        page_id = add_object(
            f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 {font_id} 0 R >> >> "
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
