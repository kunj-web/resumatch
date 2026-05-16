import pdfplumber
import io


def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    return text.strip()


def clean_text(text: str) -> str:
    # Remove excessive whitespace and blank lines
    lines = [line.strip() for line in text.splitlines()]
    non_empty = [line for line in lines if line]
    return "\n".join(non_empty)


def parse_resume(file_bytes: bytes) -> str:
    raw_text = extract_text_from_pdf(file_bytes)
    cleaned = clean_text(raw_text)
    return cleaned
