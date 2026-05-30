"""
Evidence-based resume scoring rubric (ATS, role fit, impact, sections).

Mirrors criteria used by professional resume analyzers: keyword alignment to the
target role, section completeness, quantified impact, formatting parseability,
skill–experience consistency, and project depth.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.schemas.resume_analyzer import AnalysisScores, ATSBreakdown, StructuredResumeAnalysis
from app.schemas.resume_extraction import ExtractedResumeData

ACTION_VERBS = frozenset(
    {
        "built",
        "developed",
        "designed",
        "implemented",
        "led",
        "managed",
        "improved",
        "reduced",
        "increased",
        "delivered",
        "launched",
        "optimized",
        "automated",
        "created",
        "engineered",
        "deployed",
        "migrated",
        "scaled",
        "achieved",
        "collaborated",
        "mentored",
        "analyzed",
        "researched",
        "maintained",
    }
)

STANDARD_SECTIONS = frozenset(
    {"experience", "education", "skills", "projects", "summary", "certifications"},
)

TECH_CATALOG = [
    "Python",
    "Java",
    "JavaScript",
    "TypeScript",
    "React",
    "Next.js",
    "Node.js",
    "SQL",
    "Docker",
    "Kubernetes",
    "AWS",
    "Azure",
    "GCP",
    "Git",
    "CI/CD",
    "C++",
    "C#",
    "Go",
    "Rust",
    "HTML",
    "CSS",
    "Tailwind",
    "FastAPI",
    "Django",
    "Flask",
    "Spring",
    "PostgreSQL",
    "MySQL",
    "MongoDB",
    "Redis",
    "Kafka",
    "Spark",
    "TensorFlow",
    "PyTorch",
    "Pandas",
    "NumPy",
    "Scikit-learn",
    "Figma",
    "Selenium",
    "Jest",
]


@dataclass(frozen=True)
class RoleProfile:
    keywords: tuple[str, ...]
    technologies: tuple[str, ...]
    emphasis: str  # short note for feedback


ROLE_PROFILES: dict[str, RoleProfile] = {
    "software engineer": RoleProfile(
        ("software", "engineering", "algorithms", "data structures", "agile", "api"),
        ("Python", "Java", "Git", "SQL", "Docker"),
        "full-stack or backend fundamentals with shipped code",
    ),
    "frontend developer": RoleProfile(
        ("frontend", "ui", "responsive", "accessibility", "web", "component"),
        ("JavaScript", "TypeScript", "React", "HTML", "CSS"),
        "modern UI frameworks and performance-aware frontends",
    ),
    "backend developer": RoleProfile(
        ("backend", "api", "microservices", "database", "rest", "scalability"),
        ("Python", "Java", "SQL", "Docker", "PostgreSQL"),
        "API design, persistence, and reliability",
    ),
    "full stack developer": RoleProfile(
        ("full stack", "frontend", "backend", "api", "database", "deployment"),
        ("JavaScript", "React", "Node.js", "SQL", "Docker"),
        "end-to-end ownership from UI to data layer",
    ),
    "data scientist": RoleProfile(
        ("machine learning", "statistics", "model", "analysis", "python", "visualization"),
        ("Python", "SQL", "Pandas", "Scikit-learn", "TensorFlow"),
        "experimentation, modeling, and clear business impact",
    ),
    "machine learning engineer": RoleProfile(
        ("machine learning", "deep learning", "model", "deployment", "mlops", "pipeline"),
        ("Python", "PyTorch", "TensorFlow", "Docker", "AWS"),
        "training pipelines and production ML systems",
    ),
    "devops engineer": RoleProfile(
        ("devops", "ci/cd", "infrastructure", "automation", "monitoring", "kubernetes"),
        ("Docker", "Kubernetes", "AWS", "CI/CD", "Terraform"),
        "reliable delivery and observable production systems",
    ),
    "cloud engineer": RoleProfile(
        ("cloud", "aws", "azure", "infrastructure", "security", "iac"),
        ("AWS", "Docker", "Kubernetes", "Terraform", "Linux"),
        "cloud architecture and cost-aware operations",
    ),
    "mobile developer": RoleProfile(
        ("mobile", "android", "ios", "app", "ui", "performance"),
        ("Kotlin", "Swift", "React", "Java", "Firebase"),
        "native or cross-platform app delivery",
    ),
    "qa engineer": RoleProfile(
        ("testing", "qa", "automation", "selenium", "quality", "regression"),
        ("Selenium", "Jest", "Java", "Python", "CI/CD"),
        "test strategy and automated coverage",
    ),
    "product manager": RoleProfile(
        ("product", "roadmap", "stakeholder", "metrics", "user", "prioritization"),
        ("Agile", "SQL", "Analytics", "Figma", "Jira"),
        "outcomes, discovery, and cross-functional leadership",
    ),
    "business analyst": RoleProfile(
        ("requirements", "stakeholder", "analysis", "documentation", "process"),
        ("SQL", "Excel", "Power BI", "Agile", "Jira"),
        "clear requirements and data-informed recommendations",
    ),
    "ui/ux designer": RoleProfile(
        ("ux", "ui", "wireframe", "prototype", "user research", "design system"),
        ("Figma", "Adobe", "HTML", "CSS", "Accessibility"),
        "user-centered flows and visual craft",
    ),
    "cybersecurity analyst": RoleProfile(
        ("security", "vulnerability", "incident", "compliance", "risk", "siem"),
        ("Linux", "Python", "AWS", "Networking", "SIEM"),
        "threat detection and secure architecture",
    ),
    "database administrator": RoleProfile(
        ("database", "sql", "backup", "performance", "replication", "tuning"),
        ("PostgreSQL", "MySQL", "SQL", "AWS", "Linux"),
        "data integrity, performance, and availability",
    ),
}


@dataclass
class ResumeAudit:
    """Signals gathered from extraction + full text."""

    role: str
    profile: RoleProfile
    text: str
    text_lower: str
    extracted: ExtractedResumeData
    skills: list[str]
    experience: list[str]
    projects: list[str]
    education: list[str]
    internships: list[str]
    certifications: list[str]
    achievements: list[str]
    contact: dict[str, str]
    technologies_found: list[str]
    keyword_hits: list[str]
    keyword_misses: list[str]
    tech_hits: list[str]
    tech_misses: list[str]
    bullets_with_metrics: int
    bullets_total: int
    bullets_with_action_verbs: int
    sections_detected: set[str]
    formatting_issues: list[str]
    findings: list[str] = field(default_factory=list)

    def note(self, message: str) -> None:
        self.findings.append(message)


def resolve_role_profile(target_role: str | None) -> tuple[str, RoleProfile]:
    role = (target_role or "Software Engineer").strip()
    key = role.lower()
    if key in ROLE_PROFILES:
        return role, ROLE_PROFILES[key]
    for known, profile in ROLE_PROFILES.items():
        if known in key or key in known:
            return role, profile
    return role, ROLE_PROFILES["software engineer"]


def audit_resume(
    extracted: ExtractedResumeData,
    *,
    target_role: str | None,
    cleaned_text: str,
) -> ResumeAudit:
    role, profile = resolve_role_profile(target_role)
    text = cleaned_text or ""
    text_lower = text.lower()

    skills = list(extracted.skills or [])
    experience = list(extracted.experience or [])
    projects = list(extracted.projects or [])
    education = list(extracted.education or [])
    internships = list(extracted.internships or [])
    certifications = list(extracted.certifications or [])
    achievements = list(extracted.achievements or [])
    contact = dict(extracted.contact or {})

    blob = _combined_blob(text_lower, skills, experience, projects, internships, education)

    keyword_hits = [kw for kw in profile.keywords if _keyword_present(kw, blob)]
    keyword_misses = [kw for kw in profile.keywords if kw not in keyword_hits][:6]

    technologies_found = _detect_technologies(text, skills)
    tech_hits = [t for t in profile.technologies if t.lower() in blob or t in technologies_found]
    tech_misses = [t for t in profile.technologies if t not in tech_hits][:5]

    bullets_total, bullets_with_metrics, bullets_with_action_verbs = _analyze_bullets(
        experience + internships + projects + achievements,
    )

    sections_detected = _detect_sections(text_lower, extracted)

    formatting_issues = _formatting_issues(text, sections_detected)

    audit = ResumeAudit(
        role=role,
        profile=profile,
        text=text,
        text_lower=text_lower,
        extracted=extracted,
        skills=skills,
        experience=experience,
        projects=projects,
        education=education,
        internships=internships,
        certifications=certifications,
        achievements=achievements,
        contact=contact,
        technologies_found=technologies_found,
        keyword_hits=keyword_hits,
        keyword_misses=keyword_misses,
        tech_hits=tech_hits,
        tech_misses=tech_misses,
        bullets_with_metrics=bullets_with_metrics,
        bullets_total=bullets_total,
        bullets_with_action_verbs=bullets_with_action_verbs,
        sections_detected=sections_detected,
        formatting_issues=formatting_issues,
    )

    if not contact.get("email"):
        audit.note("Missing professional email in contact block.")
    if not experience and not internships:
        audit.note("No experience or internship entries — high risk for ATS and recruiters.")
    if len(skills) < 5:
        audit.note("Skills section is thin relative to competitive applicants.")
    if bullets_total and bullets_with_metrics / max(bullets_total, 1) < 0.25:
        audit.note("Few bullets include quantified impact (%, numbers, scale).")
    if keyword_misses:
        audit.note(f"Role keywords underrepresented: {', '.join(keyword_misses[:4])}.")
    if tech_misses:
        audit.note(f"Expected tools for {role} not evidenced: {', '.join(tech_misses[:3])}.")

    return audit


def score_resume(audit: ResumeAudit) -> StructuredResumeAnalysis:
    """Produce validated scores and narrative feedback from audit evidence."""
    ats_breakdown = _score_ats(audit)
    technical = _score_technical(audit)
    projects = _score_projects(audit)
    experience = _score_experience(audit)
    communication = _score_communication(audit)
    quality = _score_quality(audit, technical, projects, experience, communication)

    ats_score = _clamp(
        ats_breakdown.keyword_match * 0.35
        + ats_breakdown.section_completeness * 0.30
        + ats_breakdown.formatting * 0.20
        + ats_breakdown.contact_info * 0.15,
    )

    role_readiness = _clamp(
        ats_score * 0.22
        + technical * 0.28
        + experience * 0.28
        + projects * 0.14
        + communication * 0.08,
    )

    scores = AnalysisScores(
        ats_score=round(ats_score, 1),
        resume_quality_score=round(quality, 1),
        technical_skill_score=round(technical, 1),
        project_strength_score=round(projects, 1),
        communication_score=round(communication, 1),
        role_readiness_score=round(role_readiness, 1),
    )

    missing_keywords = _missing_keywords_display(audit)
    missing_technologies = audit.tech_misses[:6]

    return StructuredResumeAnalysis(
        version="2",
        role_target=audit.role,
        scores=scores,
        ats_breakdown=ats_breakdown,
        strengths=_strengths(audit, scores),
        weaknesses=_weaknesses(audit, scores),
        missing_keywords=missing_keywords,
        missing_technologies=missing_technologies,
        recommendations=_recommendations(audit, scores),
        interview_topics=_interview_topics(audit),
        recruiter_feedback=_recruiter_feedback(audit, scores),
        formatting_issues=audit.formatting_issues,
        extracted_skills=audit.skills[:40],
        technologies=audit.technologies_found[:30],
        projects_summary=[_headline(p) for p in audit.projects[:6]],
        experience_summary=[_headline(e) for e in (audit.experience + audit.internships)[:6]],
        skill_radar={
            "Technical": scores.technical_skill_score,
            "Projects": scores.project_strength_score,
            "Experience": round(experience, 1),
            "Communication": scores.communication_score,
            "ATS Fit": scores.ats_score,
        },
        embeddings_indexed=0,
    )


def _score_ats(audit: ResumeAudit) -> ATSBreakdown:
    kw_total = max(len(audit.profile.keywords), 1)
    keyword_match = _clamp(100 * len(audit.keyword_hits) / kw_total)

    section_score = 0.0
    if "experience" in audit.sections_detected or audit.experience or audit.internships:
        section_score += 28
    if "education" in audit.sections_detected or audit.education:
        section_score += 22
    if "skills" in audit.sections_detected or audit.skills:
        section_score += 25
    if "projects" in audit.sections_detected or audit.projects:
        section_score += 15
    if audit.certifications:
        section_score += 5
    if audit.achievements:
        section_score += 5
    section_completeness = _clamp(section_score)

    formatting = 88.0
    for issue in audit.formatting_issues:
        if "very long" in issue.lower():
            formatting -= 18
        elif "headings" in issue.lower():
            formatting -= 15
        elif "caps" in issue.lower():
            formatting -= 10
        elif "special" in issue.lower():
            formatting -= 8
    formatting = _clamp(formatting)

    contact_info = 25.0
    if audit.contact.get("email"):
        contact_info += 45
    if audit.contact.get("phone"):
        contact_info += 12
    if audit.contact.get("linkedin"):
        contact_info += 10
    if audit.contact.get("github"):
        contact_info += 8
    contact_info = _clamp(contact_info)

    return ATSBreakdown(
        keyword_match=round(keyword_match, 1),
        formatting=round(formatting, 1),
        section_completeness=round(section_completeness, 1),
        contact_info=round(contact_info, 1),
    )


def _score_technical(audit: ResumeAudit) -> float:
    score = 20.0
    skill_count = len(audit.skills)
    if skill_count >= 12:
        score += 22
    elif skill_count >= 8:
        score += 16
    elif skill_count >= 5:
        score += 10
    elif skill_count >= 3:
        score += 4
    else:
        score -= 5

    role_skill_overlap = sum(
        1 for s in audit.skills if _keyword_present(s, " ".join(audit.profile.technologies).lower())
    )
    score += min(18, role_skill_overlap * 4)

    score += min(20, len(audit.tech_hits) * 5)
    score -= min(15, len(audit.tech_misses) * 3)

    evidenced = _skills_evidenced_in_work(audit)
    score += min(15, evidenced * 5)
    if skill_count >= 6 and evidenced < 2:
        score -= 8

    return _clamp(score)


def _score_projects(audit: ResumeAudit) -> float:
    if not audit.projects:
        return _clamp(28.0 if audit.experience else 35.0)

    score = 30.0
    score += min(25, len(audit.projects) * 8)

    quality_points = 0.0
    for proj in audit.projects[:6]:
        pl = proj.lower()
        if len(proj) >= 80:
            quality_points += 4
        if re.search(r"\d+%|\d+\+|\$[\d,]+|\d+\s*(users|ms|sec|days|k|m)", pl):
            quality_points += 6
        if any(t.lower() in pl for t in audit.technologies_found[:15]):
            quality_points += 3

    score += min(30, quality_points)
    if len(audit.projects) == 1 and all(len(p) < 40 for p in audit.projects):
        score -= 12

    return _clamp(score)


def _score_experience(audit: ResumeAudit) -> float:
    entries = audit.experience + audit.internships
    if not entries:
        return 32.0

    score = 35.0
    score += min(30, len(entries) * 10)

    depth = 0.0
    for entry in entries[:8]:
        el = entry.lower()
        if len(entry) >= 100:
            depth += 5
        if re.search(r"\d+%|\d+\+|\$[\d,]+|\d+\s*(users|ms|sec|days)", el):
            depth += 8
        if any(v in el.split() for v in ACTION_VERBS):
            depth += 4

    score += min(28, depth)
    if audit.bullets_total and audit.bullets_with_metrics / audit.bullets_total < 0.2:
        score -= 10

    return _clamp(score)


def _score_communication(audit: ResumeAudit) -> float:
    score = 40.0
    if audit.bullets_total:
        metric_ratio = audit.bullets_with_metrics / audit.bullets_total
        verb_ratio = audit.bullets_with_action_verbs / audit.bullets_total
        score += min(30, metric_ratio * 45)
        score += min(20, verb_ratio * 25)
    if audit.extracted.name:
        score += 5
    if audit.education:
        score += 5
    if len(audit.text) < 400:
        score -= 15
    return _clamp(score)


def _score_quality(
    audit: ResumeAudit,
    technical: float,
    projects: float,
    experience: float,
    communication: float,
) -> float:
    base = (technical + projects + experience + communication) / 4
    penalty = min(12, len(audit.formatting_issues) * 4)
    bonus = 5 if audit.certifications else 0
    bonus += 5 if audit.achievements else 0
    return _clamp(base - penalty + bonus)


def _strengths(audit: ResumeAudit, scores: AnalysisScores) -> list[str]:
    out: list[str] = []
    if scores.ats_score >= 72:
        out.append(
            f"ATS alignment is solid for {audit.role} "
            f"({len(audit.keyword_hits)}/{len(audit.profile.keywords)} role keywords detected).",
        )
    if audit.bullets_with_metrics >= 2:
        out.append(
            f"Quantified outcomes appear in {audit.bullets_with_metrics} bullets — recruiters value measurable impact.",
        )
    if len(audit.skills) >= 8:
        out.append(
            f"Skills inventory ({len(audit.skills)} items) supports technical screening for {audit.role}."
        )
    if audit.projects and scores.project_strength_score >= 65:
        out.append("Projects section shows applied work beyond coursework or job titles alone.")
    if audit.experience or audit.internships:
        out.append("Professional or internship history is present and parseable by ATS.")
    if audit.contact.get("linkedin") or audit.contact.get("github"):
        out.append("Online profiles included — speeds recruiter verification.")
    if not out:
        out.append("Foundation is present; tighten role keywords and add metric-driven bullets.")
    return out[:6]


def _weaknesses(audit: ResumeAudit, scores: AnalysisScores) -> list[str]:
    out: list[str] = []
    if scores.ats_score < 60:
        out.append(
            "ATS compatibility is weak — headings, keywords, or contact may block automated parsing."
        )
    if audit.keyword_misses:
        out.append(
            f"Target-role keywords missing or buried: {', '.join(_title(kw) for kw in audit.keyword_misses[:4])}.",
        )
    if audit.tech_misses:
        out.append(
            f"Stack gaps vs typical {audit.role} postings: {', '.join(audit.tech_misses[:4])}."
        )
    if not audit.experience and not audit.internships:
        out.append(
            "No employment or internship narrative — readiness score is capped without work history."
        )
    if audit.bullets_total and audit.bullets_with_metrics / audit.bullets_total < 0.3:
        out.append(
            "Most bullets lack numbers (%, scale, latency, revenue) — hard to justify seniority or impact."
        )
    if len(audit.skills) >= 8 and _skills_evidenced_in_work(audit) < 3:
        out.append(
            "Several listed skills are not reinforced in experience or project bullets (credibility risk)."
        )
    if scores.project_strength_score < 50 and audit.role.lower().find("engineer") >= 0:
        out.append(
            "Project depth is below typical bar for engineering roles — expand tech + outcome per project."
        )
    return out[:6] or [
        "Review section order and mirror language from job descriptions for your target role."
    ]


def _recommendations(audit: ResumeAudit, scores: AnalysisScores) -> list[str]:
    recs: list[str] = []
    if audit.keyword_misses:
        recs.append(
            f"Weave these {audit.role} terms into summary and top bullets: "
            f"{', '.join(_title(k) for k in audit.keyword_misses[:4])}.",
        )
    if audit.tech_misses:
        recs.append(
            f"If you have exposure to {audit.tech_misses[0]}, add one bullet with context; otherwise build a small demo project.",
        )
    if audit.bullets_with_metrics < 3:
        recs.append(
            "Rewrite 3–5 bullets as: Action verb + task + metric (e.g. reduced latency 40%, 10k users)."
        )
    if scores.ats_score < 70:
        recs.append(
            "Use standard headings (Experience, Education, Skills, Projects) and a single-column layout for ATS."
        )
    if not audit.contact.get("linkedin") and "engineer" in audit.role.lower():
        recs.append("Add LinkedIn and GitHub links near contact — expected for technical roles.")
    recs.append(
        f"Customize a version of this resume for each posting; emphasize {audit.profile.emphasis}."
    )
    return recs[:7]


def _interview_topics(audit: ResumeAudit) -> list[str]:
    topics = [
        f"Role fit for {audit.role}: strongest evidence in your resume",
        "Behavioral: STAR story for your biggest measurable outcome",
    ]
    if audit.projects:
        topics.append(f"Project deep dive: {_headline(audit.projects[0])}")
    if audit.tech_hits:
        topics.append(f"Technical screen: {audit.tech_hits[0]} fundamentals and tradeoffs")
    if audit.experience:
        topics.append(f"Experience walkthrough: {_headline(audit.experience[0])}")
    if audit.keyword_misses:
        topics.append(f"How you would ramp on: {_title(audit.keyword_misses[0])}")
    return topics[:7]


def _recruiter_feedback(audit: ResumeAudit, scores: AnalysisScores) -> str:
    name = audit.extracted.name or "This candidate"
    readiness = scores.role_readiness_score
    if readiness >= 78:
        verdict = "would likely pass ATS and merit a recruiter screen"
    elif readiness >= 62:
        verdict = "is borderline — strong phone screen if top bullets show clear metrics"
    else:
        verdict = "needs substantive revision before competitive screening"

    kw_pct = int(100 * len(audit.keyword_hits) / max(len(audit.profile.keywords), 1))
    metric_note = (
        f"{audit.bullets_with_metrics} of {audit.bullets_total} bullets include measurable results"
        if audit.bullets_total
        else "add bullet-level metrics throughout"
    )

    return (
        f"Reviewing for {audit.role}: {name} {verdict}. "
        f"Role keyword coverage is about {kw_pct}%; {metric_note}. "
        f"ATS subscores — keywords {scores.ats_score:.0f}/formatting/contact reflected in breakdown. "
        f"Priority: align vocabulary with the job description, prove listed skills in experience/projects, "
        f"and keep sections machine-readable. {audit.profile.emphasis.capitalize()} should be obvious in the first half of page one."
    )


def _missing_keywords_display(audit: ResumeAudit) -> list[str]:
    display: list[str] = []
    for kw in audit.keyword_misses[:6]:
        label = _title(kw)
        if label not in display:
            display.append(label)
    for extra in (f"{audit.role} experience", "impact metrics", "cross-functional collaboration"):
        if len(display) >= 6:
            break
        if extra.lower() not in audit.text_lower and extra not in display:
            display.append(extra)
    return display[:6]


# --- helpers ---


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _headline(text: str) -> str:
    line = text.split("\n", 1)[0].strip().lstrip("-• ")
    return line[:200]


def _title(s: str) -> str:
    return s.strip().title() if s.islower() or s.isupper() else s.strip()


def _combined_blob(
    text_lower: str,
    skills: list[str],
    experience: list[str],
    projects: list[str],
    internships: list[str],
    education: list[str],
) -> str:
    parts = [text_lower, " ".join(skills).lower()]
    for block in experience + projects + internships + education:
        parts.append(block.lower())
    return " ".join(parts)


def _keyword_present(keyword: str, blob: str) -> bool:
    k = keyword.lower().strip()
    if not k:
        return False
    if k in blob:
        return True
    if " " in k:
        return k in blob
    return bool(re.search(rf"\b{re.escape(k)}\b", blob))


def _detect_technologies(text: str, skills: list[str]) -> list[str]:
    found: list[str] = []
    blob = f"{text} {' '.join(skills)}".lower()
    for tech in TECH_CATALOG:
        if tech.lower() in blob and tech not in found:
            found.append(tech)
    return found


def _detect_sections(text_lower: str, extracted: ExtractedResumeData) -> set[str]:
    found: set[str] = set()
    for name in STANDARD_SECTIONS:
        if re.search(rf"\b{re.escape(name)}\b", text_lower):
            found.add(name)
    if extracted.experience or extracted.internships:
        found.add("experience")
    if extracted.education:
        found.add("education")
    if extracted.skills:
        found.add("skills")
    if extracted.projects:
        found.add("projects")
    if extracted.certifications:
        found.add("certifications")
    if re.search(r"\b(summary|profile|objective)\b", text_lower):
        found.add("summary")
    return found


def _formatting_issues(text: str, sections: set[str]) -> list[str]:
    issues: list[str] = []
    if len(text) > 14000:
        issues.append(
            "Resume text is very long — tighten to 1–2 pages for ATS and recruiter skim time."
        )
    if len(sections) < 3:
        issues.append(
            "Standard section headings (Experience, Education, Skills) may be missing for ATS parsers."
        )
    caps_words = len(re.findall(r"\b[A-Z]{4,}\b", text))
    if caps_words > 12:
        issues.append("Excessive ALL CAPS can reduce ATS parsing quality.")
    if text.count("|") + text.count("♦") + text.count("►") > 8:
        issues.append("Heavy use of special characters/tables may confuse ATS parsers.")
    return issues


def _analyze_bullets(blocks: list[str]) -> tuple[int, int, int]:
    total = 0
    with_metrics = 0
    with_verbs = 0
    metric_re = re.compile(
        r"\d+%|\d+\+|\$[\d,]+|\b\d+[kKmMbB]?\b|\d+\s*(users|customers|ms|sec|seconds|days|months|years|x)",
        re.I,
    )
    for block in blocks:
        for line in block.split("\n"):
            line = line.strip().lstrip("-•* ")
            if len(line) < 12:
                continue
            total += 1
            if metric_re.search(line):
                with_metrics += 1
            first = line.split()[0].lower().rstrip("ed.ing") if line.split() else ""
            if any(line.lower().startswith(v) for v in ACTION_VERBS) or first in ACTION_VERBS:
                with_verbs += 1
    return total, with_metrics, with_verbs


def _skills_evidenced_in_work(audit: ResumeAudit) -> int:
    work = " ".join(audit.experience + audit.projects + audit.internships).lower()
    count = 0
    for skill in audit.skills[:20]:
        token = skill.lower().strip()
        if len(token) >= 2 and token in work:
            count += 1
    return count
