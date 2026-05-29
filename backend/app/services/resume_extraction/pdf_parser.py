"""PDF text extraction with PyMuPDF and pdfplumber fallbacks."""

from __future__ import annotations

from io import BytesIO

from app.core.logging import get_logger

logger = get_logger(__name__)

MAX_PAGES = 25


def extract_raw_text_from_pdf(data: bytes) -> str:
    """Extract raw text; PyMuPDF first, fallbacks only when needed."""
    text = _extract_with_pymupdf(data)
    if _is_usable(text):
        return text

    text = _extract_with_pypdf(data)
    if _is_usable(text):
        return text

    text = _extract_with_pdfplumber(data)
    if _is_usable(text):
        return text

    raise ValueError("Could not extract readable text from PDF")


def _is_usable(text: str | None) -> bool:
    return bool(text and len(text.strip()) >= 20)


def _extract_with_pymupdf(data: bytes) -> str | None:
    try:
        import fitz

        doc = fitz.open(stream=data, filetype="pdf")
        parts: list[str] = []
        for page in doc[:MAX_PAGES]:
            parts.append(page.get_text("text"))
        doc.close()
        return "\n".join(parts).strip() or None
    except Exception as exc:
        logger.debug("pymupdf_extract_failed", error=str(exc))
        return None


def _extract_with_pdfplumber(data: bytes) -> str | None:
    try:
        import pdfplumber

        parts: list[str] = []
        with pdfplumber.open(BytesIO(data)) as pdf:
            for page in pdf.pages[:MAX_PAGES]:
                page_text = page.extract_text()
                if page_text:
                    parts.append(page_text)
        return "\n".join(parts).strip() or None
    except Exception as exc:
        logger.debug("pdfplumber_extract_failed", error=str(exc))
        return None


def _extract_with_pypdf(data: bytes) -> str | None:
    try:
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(data))
        parts: list[str] = []
        for page in reader.pages[:MAX_PAGES]:
            page_text = page.extract_text()
            if page_text:
                parts.append(page_text)
        return "\n".join(parts).strip() or None
    except Exception as exc:
        logger.debug("pypdf_extract_failed", error=str(exc))
        return None
