import pdfplumber
from io import BytesIO


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Takes raw PDF bytes, returns all extracted text as a single string.
    """
    text = ""
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:  # some pages might have no extractable text (e.g. scanned images)
                text += page_text + "\n"
    return text