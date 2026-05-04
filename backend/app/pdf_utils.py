from io import BytesIO
from pypdf import PdfReader

def extract_pdf_text(file_bytes: bytes) -> tuple[str, int]:
    """Return (full_text, page_count). Raises ValueError if no text extracted."""
    reader = PdfReader(BytesIO(file_bytes))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    full = "\n\n".join(p.strip() for p in pages if p.strip())
    if not full:
        raise ValueError("Could not extract any text from this PDF.")
    return full, len(reader.pages)
