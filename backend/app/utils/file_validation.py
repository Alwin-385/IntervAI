"""Secure file validation for resume uploads."""

import re
from io import BytesIO
from pathlib import Path

from app.core.config import Settings
from app.core.exceptions import ValidationAppError

PDF_MAGIC = b"%PDF"
ALLOWED_MIME_TYPES = frozenset({"application/pdf", "application/x-pdf"})
SAFE_FILENAME = re.compile(r"^[a-zA-Z0-9._\-\s]+$")


def sanitize_filename(name: str) -> str:
    base = Path(name).name
    if not base or base in {".", ".."}:
        raise ValidationAppError("Invalid file name")
    cleaned = re.sub(r"[^\w.\- ]", "_", base).strip()
    if not cleaned.lower().endswith(".pdf"):
        cleaned = f"{cleaned}.pdf" if not cleaned.endswith(".") else f"{cleaned}pdf"
    return cleaned[:512]


def validate_pdf_upload(
    *,
    filename: str,
    content_type: str | None,
    data: bytes,
    settings: Settings,
) -> None:
    if len(data) == 0:
        raise ValidationAppError("Uploaded file is empty")

    if len(data) > settings.resume_max_size_bytes:
        max_mb = settings.resume_max_size_bytes / (1024 * 1024)
        raise ValidationAppError(f"File exceeds maximum size of {max_mb:.1f} MB")

    if not filename.lower().endswith(".pdf"):
        raise ValidationAppError("Only PDF files are allowed")

    if content_type and content_type.split(";")[0].strip().lower() not in ALLOWED_MIME_TYPES:
        raise ValidationAppError(
            f"Invalid content type '{content_type}'. Only PDF uploads are accepted.",
        )

    if not data.startswith(PDF_MAGIC):
        raise ValidationAppError("File content is not a valid PDF document")


def extract_pdf_text(data: bytes, max_chars: int = 50_000) -> str | None:
    """Extract plain text from PDF for search/metadata (best-effort)."""
    try:
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(data))
        parts: list[str] = []
        for page in reader.pages[:50]:
            text = page.extract_text()
            if text:
                parts.append(text)
        combined = "\n".join(parts).strip()
        return combined[:max_chars] if combined else None
    except Exception:
        return None
