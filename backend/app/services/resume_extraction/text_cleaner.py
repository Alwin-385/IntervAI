"""Normalize and clean resume text extracted from PDFs."""

from __future__ import annotations

import re

# Hyphen must be first/last in a char class; do not use a raw bullet string in [...]
_LEADING_BULLET_RE = re.compile(r"^(?:[\u2022\u25CF\u25AA\u25E6\u00B7]|[*\-])\s*")
_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
_MULTI_SPACE_RE = re.compile(r"[ \t]{2,}")
_MULTI_NEWLINE_RE = re.compile(r"\n{3,}")
_EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w.-]+\.\w{2,}\b")
_URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)


def clean_resume_text(raw: str, *, max_chars: int = 80_000) -> str:
    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    text = _CONTROL_RE.sub("", text)
    text = _URL_RE.sub("", text)

    lines: list[str] = []
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            lines.append("")
            continue
        stripped = _LEADING_BULLET_RE.sub("- ", stripped)
        stripped = _MULTI_SPACE_RE.sub(" ", stripped)
        lines.append(stripped)

    text = "\n".join(lines)
    text = _MULTI_NEWLINE_RE.sub("\n\n", text)
    return text.strip()[:max_chars]
