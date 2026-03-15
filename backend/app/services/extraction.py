"""
Text extraction service.

Supports:
  - PDF  → PyMuPDF (fitz)
  - DOCX → python-docx
  - Images (PNG, JPG, TIFF, BMP) → Tesseract OCR via pytesseract
"""
import os
import io
from pathlib import Path

import fitz  # PyMuPDF
import docx
import pytesseract
from PIL import Image


# ── Helpers ────────────────────────────────────────────────────────────────

def _clean(text: str) -> str:
    """Remove excessive blank lines and strip leading/trailing whitespace."""
    lines = [line.strip() for line in text.splitlines()]
    cleaned = "\n".join(line for line in lines if line)
    return cleaned.strip()


# ── Extractors ─────────────────────────────────────────────────────────────

def extract_from_pdf(file_bytes: bytes) -> str:
    """Extract plain text from a PDF file using PyMuPDF."""
    text_parts = []
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text_parts.append(page.get_text("text"))
    return _clean("\n".join(text_parts))


def extract_from_docx(file_bytes: bytes) -> str:
    """Extract plain text from a DOCX file using python-docx."""
    document = docx.Document(io.BytesIO(file_bytes))
    paragraphs = [para.text for para in document.paragraphs if para.text.strip()]
    return _clean("\n".join(paragraphs))


def extract_from_image(file_bytes: bytes) -> str:
    """Extract text from an image using Tesseract OCR."""
    image = Image.open(io.BytesIO(file_bytes))
    # Tesseract config: output as plain text, use English + Hindi
    custom_config = r"--oem 3 --psm 6"
    text = pytesseract.image_to_string(image, lang="eng", config=custom_config)
    return _clean(text)


# ── Main dispatcher ────────────────────────────────────────────────────────

SUPPORTED_EXTENSIONS = {
    ".pdf": "pdf",
    ".docx": "docx",
    ".doc": "docx",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".tiff": "image",
    ".bmp": "image",
    ".webp": "image",
}


def get_file_type(filename: str) -> str:
    """Return the file type category based on extension."""
    ext = Path(filename).suffix.lower()
    return SUPPORTED_EXTENSIONS.get(ext, "unsupported")


def extract_text(file_bytes: bytes, filename: str) -> tuple[str, str]:
    """
    Extract text from an uploaded file.

    Returns:
        (extracted_text, file_type)

    Raises:
        ValueError: if the file type is not supported or extraction fails.
    """
    file_type = get_file_type(filename)

    if file_type == "unsupported":
        ext = Path(filename).suffix.lower()
        raise ValueError(
            f"File type '{ext}' is not supported. "
            f"Supported types: PDF, DOCX, PNG, JPG, TIFF, BMP."
        )

    try:
        if file_type == "pdf":
            text = extract_from_pdf(file_bytes)
        elif file_type == "docx":
            text = extract_from_docx(file_bytes)
        elif file_type == "image":
            text = extract_from_image(file_bytes)
        else:
            raise ValueError(f"Unhandled file type: {file_type}")
    except Exception as exc:
        raise ValueError(f"Failed to extract text from '{filename}': {exc}") from exc

    if not text:
        raise ValueError(
            f"No text could be extracted from '{filename}'. "
            "The document may be empty or image-only (try uploading the image directly)."
        )

    return text, file_type
