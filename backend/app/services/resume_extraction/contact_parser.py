"""Extract labeled contact fields from resume header/footer text."""

from __future__ import annotations

import re

_CONTACT_LABELS: dict[str, tuple[str, ...]] = {
    "email": ("email", "e-mail", "mail"),
    "phone": ("phone", "mobile", "tel", "telephone", "contact no", "contact number"),
    "linkedin": ("linkedin",),
    "github": ("github", "git hub"),
    "address": ("address",),
    "website": ("website", "portfolio", "web"),
}

_INVALID_ADDRESS_RE = re.compile(
    r"(dashboard|platform|project|developer|intern|engineer|software|"
    r"college|university|bachelor|technology|github|linkedin|http|www|@|"
    r"certification|achievement|skill|experience|education|nptel|swayam)",
    re.IGNORECASE,
)

_GEO_HINT_RE = re.compile(
    r"(,\s*[A-Za-z]{2,}|\b\d{6}\b|"
    r"\b(india|kerala|tamil|karnataka|maharashtra|delhi|mumbai|chennai|"
    r"kochi|kottayam|bangalore|hyderabad|pune|state|district|pin)\b)",
    re.IGNORECASE,
)

_EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w.-]+\.\w{2,}\b")
_PHONE_RE = re.compile(
    r"(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{3,4}(?:[\s.-]?\d+)?",
)
_LINKEDIN_RE = re.compile(
    r"(?:https?://)?(?:www\.)?linkedin\.com[/\w\-.%]+",
    re.IGNORECASE,
)
_GITHUB_RE = re.compile(
    r"(?:https?://)?(?:www\.)?github\.com[/\w\-.%]+",
    re.IGNORECASE,
)
_URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
_LABELED_LINE_RE = re.compile(
    r"^[\s\-•]*([a-z][a-z\s/-]{1,24})\s*[:\-]\s*(.+)$",
    re.IGNORECASE,
)


def parse_contact_fields(text: str) -> dict[str, str]:
    """Return contact map with keys: email, phone, linkedin, github, address, website."""
    contact: dict[str, str] = {}
    if not text.strip():
        return contact

    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped or len(stripped) > 500:
            continue
        _apply_labeled_line(stripped, contact)
        _apply_inline_patterns(stripped, contact)

    if contact.get("address") and not is_plausible_address(contact["address"]):
        del contact["address"]

    return contact


def parse_header_address(preamble: str, name: str | None) -> str | None:
    """Address lines immediately after the candidate name in the resume header."""
    lines = [line.strip() for line in preamble.split("\n") if line.strip()]
    if not lines:
        return None

    start = 0
    if name:
        name_lower = name.lower()
        for idx, line in enumerate(lines[:10]):
            if line.lower() == name_lower or name_lower in line.lower():
                start = idx + 1
                break
        else:
            start = 1

    parts: list[str] = []
    for line in lines[start : start + 3]:
        if _is_contact_line(line):
            break
        if is_plausible_address(line):
            parts.append(line)
        elif parts:
            break

    if not parts:
        return None
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:2])


def is_plausible_address(value: str) -> bool:
    text = value.strip()
    if len(text) < 4 or len(text) > 160:
        return False
    if _INVALID_ADDRESS_RE.search(text):
        return False
    if _EMAIL_RE.search(text) or _LINKEDIN_RE.search(text) or _GITHUB_RE.search(text):
        return False
    if _PHONE_RE.search(text) and sum(c.isdigit() for c in text) >= 8:
        return False
    if re.search(r"\b(19|20)\d{2}\b", text):
        return False
    return bool(_GEO_HINT_RE.search(text) or re.search(r"\d{1,5}\s+\w+", text))


def _normalize_label(label: str) -> str | None:
    normalized = label.strip().lower().replace("_", " ")
    for key, aliases in _CONTACT_LABELS.items():
        if normalized in aliases:
            return key
        if key != "address" and any(alias in normalized for alias in aliases):
            return key
    return None


def _apply_labeled_line(line: str, contact: dict[str, str]) -> None:
    match = _LABELED_LINE_RE.match(line)
    if not match:
        return
    key = _normalize_label(match.group(1))
    if not key:
        return
    value = match.group(2).strip()
    if not value or key in contact:
        return
    if key == "address" and not is_plausible_address(value):
        return
    contact[key] = _clean_value(key, value)


def _apply_inline_patterns(line: str, contact: dict[str, str]) -> None:
    for email in _EMAIL_RE.findall(line):
        if "email" not in contact:
            contact["email"] = email

    if "phone" not in contact:
        phone_match = _PHONE_RE.search(line)
        if phone_match and not _EMAIL_RE.search(phone_match.group(0)):
            candidate = phone_match.group(0).strip()
            if sum(c.isdigit() for c in candidate) >= 8:
                contact["phone"] = candidate

    for url in _LINKEDIN_RE.findall(line):
        if "linkedin" not in contact:
            contact["linkedin"] = url

    for url in _GITHUB_RE.findall(line):
        if "github" not in contact:
            contact["github"] = url

    if "website" not in contact and "github" not in line.lower() and "linkedin" not in line.lower():
        for url in _URL_RE.findall(line):
            lowered = url.lower()
            if "github.com" in lowered or "linkedin.com" in lowered:
                continue
            contact["website"] = url
            break


def _is_contact_line(line: str) -> bool:
    lowered = line.lower()
    return bool(
        _EMAIL_RE.search(line)
        or _LINKEDIN_RE.search(line)
        or _GITHUB_RE.search(line)
        or ("github.com" in lowered)
        or ("linkedin.com" in lowered)
        or (_PHONE_RE.search(line) and sum(c.isdigit() for c in line) >= 8)
    )


def _clean_value(key: str, value: str) -> str:
    if key == "email":
        match = _EMAIL_RE.search(value)
        return match.group(0) if match else value
    if key == "linkedin":
        match = _LINKEDIN_RE.search(value)
        return match.group(0) if match else value
    if key == "github":
        match = _GITHUB_RE.search(value)
        return match.group(0) if match else value
    if key == "phone":
        match = _PHONE_RE.search(value)
        return match.group(0).strip() if match else value
    return value.strip()[:500]
