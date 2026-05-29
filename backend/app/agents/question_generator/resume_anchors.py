"""Plan which resume section each question should reference (balanced, not one project)."""

from __future__ import annotations

import random
from dataclasses import dataclass

from app.models.enums import InterviewCategory
from app.schemas.resume_extraction import ExtractedResumeData

# Resume-based interviews: ~65% projects, ~35% other sections (experience, skills, etc.)
RESUME_BASED_PROJECT_RATIO = 0.65
# Technical / behavioral with resume: lighter project weight
TECHNICAL_PROJECT_RATIO = 0.45
BEHAVIORAL_PROJECT_RATIO = 0.40
DSA_PROJECT_RATIO = 0.20


@dataclass(frozen=True)
class ResumeAnchor:
    """One resume line item used to personalize a question."""

    source: str  # project | experience | skill | education | certification | achievement | internship
    text: str
    display: str  # shown in UI source_hint
    slot_variant: int = 0  # disambiguates template rotation when anchors must repeat


def _line(raw: str, max_len: int = 100) -> str:
    return raw.split("\n", 1)[0].strip()[:max_len]


def _collect_other_anchors(extracted: ExtractedResumeData) -> list[ResumeAnchor]:
    out: list[ResumeAnchor] = []
    for exp in extracted.experience[:6]:
        line = _line(exp)
        if line:
            out.append(ResumeAnchor("experience", line, f"Experience: {line[:70]}"))
    for skill in extracted.skills[:10]:
        s = skill.strip()[:80]
        if s:
            out.append(ResumeAnchor("skill", s, f"Skill: {s[:70]}"))
    for edu in extracted.education[:4]:
        line = _line(edu)
        if line:
            out.append(ResumeAnchor("education", line, f"Education: {line[:70]}"))
    for cert in extracted.certifications[:4]:
        line = _line(cert)
        if line:
            out.append(ResumeAnchor("certification", line, f"Certification: {line[:70]}"))
    for ach in extracted.achievements[:4]:
        line = _line(ach)
        if line:
            out.append(ResumeAnchor("achievement", line, f"Achievement: {line[:70]}"))
    for intern in extracted.internships[:4]:
        line = _line(intern)
        if line:
            out.append(ResumeAnchor("internship", line, f"Internship: {line[:70]}"))
    return out


def _all_resume_anchors(extracted: ExtractedResumeData) -> list[ResumeAnchor]:
    """Every distinct resume line item (projects first, then other sections)."""
    anchors: list[ResumeAnchor] = []
    for text in [_line(p) for p in extracted.projects[:8] if p and p.strip()]:
        anchors.append(ResumeAnchor("project", text, f"Project: {text[:70]}"))
    anchors.extend(_collect_other_anchors(extracted))
    return anchors


def build_resume_anchor_plan(
    count: int,
    extracted: ExtractedResumeData | None,
    rng: random.Random,
    *,
    session_category: InterviewCategory,
) -> list[ResumeAnchor | None]:
    """Per-question resume focus; balances projects with other resume sections."""
    if not extracted or count <= 0:
        return [None] * count

    projects = [_line(p) for p in extracted.projects[:8] if p and p.strip()]
    others = _collect_other_anchors(extracted)

    ratio = _project_ratio_for_category(session_category)
    use_resume = session_category in (
        InterviewCategory.RESUME_BASED,
        InterviewCategory.TECHNICAL,
        InterviewCategory.BEHAVIORAL,
        InterviewCategory.MIXED,
    )
    if session_category == InterviewCategory.DSA and (projects or others):
        use_resume = True
    if session_category == InterviewCategory.HR:
        use_resume = False

    if not use_resume or (not projects and not others):
        return [None] * count

    project_anchors = [
        ResumeAnchor("project", t, f"Project: {t[:70]}") for t in projects
    ]
    project_slots = 0
    if project_anchors:
        project_slots = max(1, min(len(project_anchors), round(count * ratio)))
        if not others:
            project_slots = min(count, len(project_anchors))

    slots: list[ResumeAnchor] = []
    if project_slots:
        rng.shuffle(project_anchors)
        for i in range(project_slots):
            slots.append(project_anchors[i % len(project_anchors)])

    other_slots = count - len(slots)
    if other_slots > 0 and others:
        rng.shuffle(others)
        seen_other: set[tuple[str, str]] = set()
        for anchor in others:
            key = (anchor.source, anchor.text)
            if key in seen_other:
                continue
            seen_other.add(key)
            slots.append(anchor)
            if len(slots) >= count:
                break
        idx = 0
        while len(slots) < count and others:
            anchor = others[idx % len(others)]
            slots.append(
                ResumeAnchor(
                    anchor.source,
                    anchor.text,
                    anchor.display,
                    slot_variant=len(slots),
                ),
            )
            idx += 1
    elif other_slots > 0 and project_anchors:
        for i in range(other_slots):
            text = projects[(project_slots + i) % len(projects)]
            slots.append(
                ResumeAnchor(
                    "project",
                    text,
                    f"Project: {text[:70]}",
                    slot_variant=project_slots + i,
                ),
            )

    rng.shuffle(slots)

    # Extend without cloning the same (source, text, variant) tuple
    full_pool = _all_resume_anchors(extracted)
    rng.shuffle(full_pool)
    variant = 0
    while len(slots) < count and full_pool:
        base = full_pool[len(slots) % len(full_pool)]
        slots.append(
            ResumeAnchor(
                base.source,
                base.text,
                base.display,
                slot_variant=variant,
            ),
        )
        variant += 1

    return (slots + [None] * count)[:count]


def _project_ratio_for_category(category: InterviewCategory) -> float:
    if category == InterviewCategory.RESUME_BASED:
        return RESUME_BASED_PROJECT_RATIO
    if category == InterviewCategory.TECHNICAL:
        return TECHNICAL_PROJECT_RATIO
    if category == InterviewCategory.BEHAVIORAL:
        return BEHAVIORAL_PROJECT_RATIO
    if category == InterviewCategory.DSA:
        return DSA_PROJECT_RATIO
    if category == InterviewCategory.MIXED:
        return 0.50
    return 0.0


def anchor_for_slot(
    plan: list[ResumeAnchor | None],
    slot: int,
    projects: list[str],
    skills: list[str],
) -> tuple[str | None, str | None]:
    """Return (anchor text, source_hint display) for a slot."""
    if slot < len(plan) and plan[slot] is not None:
        a = plan[slot]
        return a.text, a.display
    if projects:
        t = projects[slot % len(projects)].split("\n", 1)[0].strip()[:80]
        return t, f"Project: {t[:70]}"
    if skills:
        s = skills[slot % len(skills)].strip()[:80]
        return s, f"Skill: {s[:70]}"
    return None, None
