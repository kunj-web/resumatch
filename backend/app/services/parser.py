import pdfplumber
import io
from docx import Document


def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    return text.strip()


def extract_text_from_docx(file_bytes: bytes) -> str:
    document = Document(io.BytesIO(file_bytes))
    parts = []

    for paragraph in document.paragraphs:
        if paragraph.text:
            parts.append(paragraph.text)

    for table in document.tables:
        for row in table.rows:
            row_text = " ".join(
                cell.text.strip() for cell in row.cells if cell.text.strip()
            )
            if row_text:
                parts.append(row_text)

    return "\n".join(parts).strip()


def clean_text(text: str) -> str:
    # Remove excessive whitespace and blank lines
    lines = [line.strip() for line in text.splitlines()]
    non_empty = [line for line in lines if line]
    return "\n".join(non_empty)


def parse_resume(file_bytes: bytes, file_type: str) -> str:
    if file_type == "pdf":
        raw_text = extract_text_from_pdf(file_bytes)
    elif file_type == "docx":
        raw_text = extract_text_from_docx(file_bytes)
    else:
        raise ValueError("Unsupported resume file type")

    cleaned = clean_text(raw_text)
    return cleaned
