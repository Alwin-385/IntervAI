"""Heuristic structured extraction from cleaned resume text."""

from __future__ import annotations

import re

from app.schemas.resume_extraction import ExtractedResumeData
from app.services.resume_extraction.contact_parser import (
    is_plausible_address,
    parse_contact_fields,
    parse_header_address,
)

_SECTION_ALIASES: dict[str, tuple[str, ...]] = {
    "education": ("education", "academic", "qualification", "university", "college"),
    "experience": ("experience", "work history", "employment", "professional experience"),
    "projects": ("projects", "personal projects", "key projects"),
    "skills": ("skills", "technical skills", "core competencies", "technologies"),
    "certifications": ("certifications", "certificates", "licenses"),
    "internships": ("internships", "internship"),
    "achievements": ("achievements", "awards", "honors", "accomplishments"),
    "summary": ("summary", "profile", "about me", "objective"),
}

_SECTION_HEADER_RE = re.compile(
    r"^[\s\-•]*([A-Za-z][A-Za-z\s/&]{2,40})\s*[:\-]?\s*$",
    re.MULTILINE,
)
_EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.\w{2,}")
_PHONE_RE = re.compile(r"(\+?\d[\d\s().-]{7,}\d)")
_LINKEDIN_RE = re.compile(r"linkedin\.com", re.IGNORECASE)
_GITHUB_RE = re.compile(r"github\.com", re.IGNORECASE)


def parse_structured_resume(text: str) -> ExtractedResumeData:
    sections = _split_sections(text)
    preamble = sections.pop("preamble", "")
    _strip_trailing_contact_from_sections(sections)

    contact = parse_contact_fields(preamble)
    tail_blob = "\n".join(text.split("\n")[-18:])
    for key, value in parse_contact_fields(tail_blob).items():
        if key == "address":
            continue
        contact.setdefault(key, value)
    if not contact:
        contact = parse_contact_fields(_contact_lines_from_body(text))

    name = _extract_name(preamble or text.split("\n", 8)[0], sections, contact)

    header_address = parse_header_address(preamble, name)
    if header_address:
        contact["address"] = header_address
    elif contact.get("address") and not is_plausible_address(contact["address"]):
        contact.pop("address", None)

    return ExtractedResumeData(
        name=name,
        contact=contact,
        education=_section_items(sections, "education"),
        experience=_section_items(sections, "experience"),
        projects=_section_items(sections, "projects"),
        skills=_parse_skills(sections.get("skills", "")),
        certifications=_section_items(sections, "certifications"),
        internships=_section_items(sections, "internships"),
        achievements=_section_items(sections, "achievements"),
    )


def _split_sections(text: str) -> dict[str, str]:
    matches = list(_SECTION_HEADER_RE.finditer(text))
    if not matches:
        return {"preamble": text}

    sections: dict[str, str] = {}
    preamble = text[: matches[0].start()].strip()
    if preamble:
        sections["preamble"] = preamble

    for idx, match in enumerate(matches):
        header = match.group(1).strip().lower()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        key = _normalize_section_key(header)
        if key in sections:
            sections[key] = f"{sections[key]}\n{body}"
        else:
            sections[key] = body

    return sections


def _strip_trailing_contact_from_sections(sections: dict[str, str]) -> None:
    """Move trailing contact lines out of the last content section."""
    for key in list(sections.keys()):
        if key == "preamble":
            continue
        body = sections[key]
        lines = body.split("\n")
        while lines and _looks_like_contact_line(lines[-1].strip()):
            lines.pop()
        sections[key] = "\n".join(lines).strip()


def _looks_like_contact_line(line: str) -> bool:
    return bool(
        _EMAIL_RE.search(line)
        or _LINKEDIN_RE.search(line)
        or _GITHUB_RE.search(line)
        or (_PHONE_RE.search(line) and not re.search(r"[a-z]{4,}", line.lower()))
    )


def _contact_lines_from_body(text: str) -> str:
    lines = text.split("\n")
    picks: list[str] = []
    for line in list(lines[:12]) + list(lines[-12:]):
        stripped = line.strip()
        if stripped and _looks_like_contact_line(stripped):
            picks.append(stripped)
    return "\n".join(dict.fromkeys(picks))


def _normalize_section_key(header: str) -> str:
    normalized = header.strip().lower()
    for key, aliases in _SECTION_ALIASES.items():
        if normalized in aliases or any(alias in normalized for alias in aliases):
            return key
    return normalized


def _section_items(sections: dict[str, str], key: str) -> list[str]:
    body = sections.get(key, "")
    if not body:
        return []
    items: list[str] = []
    for block in re.split(r"\n{2,}", body):
        formatted = _format_entry_block(block)
        if formatted and not _looks_like_contact_line(formatted.split("\n", 1)[0]):
            items.append(formatted[:2000])
    if not items:
        current: list[str] = []
        for line in body.split("\n"):
            stripped = line.strip()
            if not stripped:
                if current:
                    entry = _format_entry_block("\n".join(current))
                    if entry:
                        items.append(entry[:2000])
                    current = []
                continue
            if stripped.startswith("- ") and current and not current[-1].strip().startswith("- "):
                entry = _format_entry_block("\n".join(current))
                if entry:
                    items.append(entry[:2000])
                current = [stripped]
            else:
                current.append(stripped)
        if current:
            entry = _format_entry_block("\n".join(current))
            if entry:
                items.append(entry[:2000])
    return items[:30]


def _format_entry_block(block: str) -> str:
    """Normalize a section entry: title line + bullet lines."""
    lines = [ln.strip() for ln in block.strip().split("\n") if ln.strip()]
    if not lines:
        return ""
    title = lines[0].lstrip("- ").strip()
    bullets = [ln.lstrip("- ").strip() for ln in lines[1:] if ln.lstrip("- ").strip()]
    if not bullets:
        return title
    bullet_text = "\n".join(f"• {b}" for b in bullets)
    return f"{title}\n{bullet_text}"


def _parse_skills(skills_text: str) -> list[str]:
    if not skills_text:
        return []
    tokens = re.split(r"[,;|\n•●▪·]", skills_text)
    skills = [t.strip() for t in tokens if 1 < len(t.strip()) <= 80]
    return list(dict.fromkeys(skills))[:60]


def _extract_name(
    preamble: str,
    sections: dict[str, str],
    contact: dict[str, str],
) -> str | None:
    candidates = preamble.split("\n")[:8]
    for line in candidates:
        candidate = line.strip()
        if not candidate or len(candidate) > 80:
            continue
        if _looks_like_contact_line(candidate):
            continue
        if re.search(r"\d{3,}", candidate):
            continue
        lowered = candidate.lower()
        if any(
            word in lowered
            for word in ("resume", "curriculum", "vitae", "profile", "summary", "objective")
        ):
            continue
        if 2 <= len(candidate.split()) <= 6:
            return candidate

    if contact.get("email"):
        local = contact["email"].split("@")[0].replace(".", " ").replace("_", " ")
        parts = [p.capitalize() for p in local.split() if p.isalpha()]
        if 2 <= len(parts) <= 4:
            return " ".join(parts)
    return None
