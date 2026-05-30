"""Template-based personalized question generation (no OpenAI required)."""

from __future__ import annotations

import hashlib
import random
from typing import Any

from app.agents.question_generator.patterns import (
    pattern_allowed_for_category,
    patterns_for_session,
    templates_for_pattern,
)
from app.agents.question_generator.resume_anchors import (
    ResumeAnchor,
    anchor_for_slot,
    build_resume_anchor_plan,
)
from app.models.enums import InterviewCategory, InterviewDifficulty, QuestionType
from app.schemas.interview_questions_gen import GeneratedQuestion
from app.schemas.resume_extraction import ExtractedResumeData

_TIME_BY_DIFFICULTY = {
    InterviewDifficulty.BEGINNER: 120,
    InterviewDifficulty.INTERMEDIATE: 180,
    InterviewDifficulty.ADVANCED: 240,
}

_CATEGORY_TO_QTYPE: dict[InterviewCategory, QuestionType] = {
    InterviewCategory.HR: QuestionType.OPEN_ENDED,
    InterviewCategory.TECHNICAL: QuestionType.TECHNICAL,
    InterviewCategory.BEHAVIORAL: QuestionType.BEHAVIORAL,
    InterviewCategory.DSA: QuestionType.TECHNICAL,
    InterviewCategory.RESUME_BASED: QuestionType.SITUATIONAL,
    InterviewCategory.MIXED: QuestionType.TECHNICAL,
}

_GENERIC_ANCHORS = frozenset(
    {
        "your recent experience",
        "your recent work",
        "your background",
        "your core stack",
    },
)

# Distinct contexts when resume has no projects/skills (avoids identical fallbacks).
_SLOT_CONTEXTS = [
    "a recent feature you shipped",
    "a performance issue you debugged",
    "a code review that changed your approach",
    "integrating with a third-party API",
    "improving accessibility in a UI",
    "reducing bundle size or load time",
    "a test suite you designed or improved",
    "handling a production incident",
]


def build_heuristic_questions(
    *,
    target_role: str,
    session_category: InterviewCategory,
    difficulty: InterviewDifficulty,
    count: int,
    extracted: ExtractedResumeData | None,
    weak_areas: list[str],
    rag_snippets: list[str],
    existing_texts: list[str],
    generation_nonce: str | None = None,
) -> list[GeneratedQuestion]:
    """Generate non-repetitive questions from templates + resume anchors."""
    nonce = generation_nonce or "initial"
    rng = random.Random(
        _seed(target_role, session_category.value, difficulty.value, count, nonce),
    )
    variant_base = _seed("variant", nonce) % 10_000
    plan = _category_plan(session_category, count)
    pattern_plan = _pattern_plan(session_category, difficulty, count, rng, plan)
    anchor_plan = build_resume_anchor_plan(
        count,
        extracted,
        rng,
        session_category=session_category,
    )
    used_hashes: set[str] = {_norm_hash(t) for t in existing_texts}
    used_texts: set[str] = {t.strip().lower() for t in existing_texts if t.strip()}
    used_patterns: set[str] = set()
    projects = (extracted.projects if extracted else [])[:8]
    experience = (extracted.experience if extracted else [])[:6]
    skills = (extracted.skills if extracted else [])[:12]
    name = extracted.name if extracted else None

    questions: list[GeneratedQuestion] = []
    weak_pool = list(weak_areas)[:6]
    rag_pool = list(rag_snippets)[:8]

    for idx, cat in enumerate(plan):
        slot_anchor, source_hint = _slot_from_plan(
            anchor_plan,
            idx,
            projects,
            skills,
            session_category,
        )
        q = _build_one(
            rng=rng,
            order_index=idx,
            session_category=session_category,
            slot_category=cat,
            difficulty=difficulty,
            target_role=target_role,
            projects=projects,
            experience=experience,
            skills=skills,
            name=name,
            weak_areas=weak_pool,
            rag_snippets=rag_pool,
            used_hashes=used_hashes,
            used_texts=used_texts,
            used_patterns=used_patterns,
            variant=variant_base
            + idx
            + (
                (anchor_plan[idx].slot_variant * 17)
                if idx < len(anchor_plan) and anchor_plan[idx]
                else 0
            ),
            pattern=pattern_plan[idx],
            slot_anchor=slot_anchor,
            source_hint=source_hint,
            resume_source=(
                anchor_plan[idx].source
                if idx < len(anchor_plan) and anchor_plan[idx] is not None
                else None
            ),
        )
        if q and _try_append_question(questions, q, used_hashes, used_texts):
            pass

    questions = _finalize_unique_questions(
        questions=questions,
        count=count,
        plan=plan,
        pattern_plan=pattern_plan,
        anchor_plan=anchor_plan,
        session_category=session_category,
        difficulty=difficulty,
        target_role=target_role,
        extracted=extracted,
        projects=projects,
        experience=experience,
        skills=skills,
        name=name,
        weak_areas=weak_pool,
        rag_snippets=rag_pool,
        used_hashes=used_hashes,
        used_texts=used_texts,
        used_patterns=used_patterns,
        rng=rng,
        variant_base=variant_base,
    )

    return ensure_exact_question_count(
        questions=questions,
        count=count,
        target_role=target_role,
        session_category=session_category,
        difficulty=difficulty,
        extracted=extracted,
        weak_areas=weak_areas,
        rag_snippets=rag_snippets,
        generation_nonce=generation_nonce,
    )


def ensure_exact_question_count(
    *,
    questions: list[GeneratedQuestion],
    count: int,
    target_role: str,
    session_category: InterviewCategory,
    difficulty: InterviewDifficulty,
    extracted: ExtractedResumeData | None,
    weak_areas: list[str],
    rag_snippets: list[str],
    generation_nonce: str | None = None,
) -> list[GeneratedQuestion]:
    """Always return exactly `count` unique questions."""
    nonce = generation_nonce or "pad"
    rng = random.Random(
        _seed(target_role, session_category.value, difficulty.value, count, nonce),
    )
    variant_base = _seed("variant", nonce) % 10_000
    plan = _category_plan(session_category, count)
    pattern_plan = _pattern_plan(session_category, difficulty, count, rng, plan)
    anchor_plan = build_resume_anchor_plan(
        count,
        extracted,
        rng,
        session_category=session_category,
    )
    used_hashes = {_norm_hash(q.question_text) for q in questions}
    used_texts = {_normalize_text_key(q.question_text) for q in questions}
    used_patterns: set[str] = set()
    projects = (extracted.projects if extracted else [])[:8]
    experience = (extracted.experience if extracted else [])[:6]
    skills = (extracted.skills if extracted else [])[:12]

    return _finalize_unique_questions(
        questions=questions,
        count=count,
        plan=plan,
        pattern_plan=pattern_plan,
        anchor_plan=anchor_plan,
        session_category=session_category,
        difficulty=difficulty,
        target_role=target_role,
        extracted=extracted,
        projects=projects,
        experience=experience,
        skills=skills,
        name=None,
        weak_areas=weak_areas,
        rag_snippets=rag_snippets,
        used_hashes=used_hashes,
        used_texts=used_texts,
        used_patterns=used_patterns,
        rng=rng,
        variant_base=variant_base,
    )


def _pattern_plan(
    session_category: InterviewCategory,
    difficulty: InterviewDifficulty,
    count: int,
    rng: random.Random,
    category_plan: list[InterviewCategory],
) -> list[str]:
    """Assign a distinct question shape per slot; mixed interviews use per-slot category pools."""
    if session_category == InterviewCategory.MIXED:
        out: list[str] = []
        for i, cat in enumerate(category_plan[:count]):
            pool = list(patterns_for_session(cat, difficulty))
            rng.shuffle(pool)
            pick = pool[i % len(pool)]
            if out and pick == out[-1] and len(pool) > 1:
                pick = pool[(i + 1) % len(pool)]
            out.append(pick)
        while len(out) < count:
            cat = category_plan[len(out) % len(category_plan)]
            pool = patterns_for_session(cat, difficulty)
            out.append(pool[len(out) % len(pool)])
        return out

    pool = list(patterns_for_session(session_category, difficulty))
    rng.shuffle(pool)
    if count <= len(pool):
        plan = pool[:count]
        rng.shuffle(plan)
        return plan

    plan: list[str] = []
    idx = 0
    while len(plan) < count:
        candidate = pool[idx % len(pool)]
        idx += 1
        if plan and candidate == plan[-1] and len(pool) > 1:
            candidate = pool[idx % len(pool)]
            idx += 1
        plan.append(candidate)
    return plan


def _effective_category(
    session_category: InterviewCategory,
    slot_category: InterviewCategory,
) -> InterviewCategory:
    if session_category == InterviewCategory.MIXED:
        return slot_category
    return session_category


def _slot_from_plan(
    anchor_plan: list[ResumeAnchor | None],
    slot: int,
    projects: list[str],
    skills: list[str],
    session_category: InterviewCategory,
) -> tuple[str | None, str | None]:
    if session_category == InterviewCategory.HR:
        return None, None
    text, hint = anchor_for_slot(anchor_plan, slot, projects, skills)
    return text, hint


def _build_one(
    *,
    rng: random.Random,
    order_index: int,
    session_category: InterviewCategory,
    slot_category: InterviewCategory,
    difficulty: InterviewDifficulty,
    target_role: str,
    projects: list[str],
    experience: list[str],
    skills: list[str],
    name: str | None,
    weak_areas: list[str],
    rag_snippets: list[str],
    used_hashes: set[str],
    used_texts: set[str] | None = None,
    used_patterns: set[str] | None = None,
    variant: int = 0,
    pattern: str | None = None,
    slot_anchor: str | None = None,
    source_hint: str | None = None,
    resume_source: str | None = None,
) -> GeneratedQuestion | None:
    if used_texts is None:
        used_texts = set()
    category = _effective_category(session_category, slot_category)
    use_resume_anchor = session_category != InterviewCategory.HR
    if session_category == InterviewCategory.DSA:
        anchor = slot_anchor if (slot_anchor and resume_source) else None
        if not anchor:
            anchor = _pick_anchor(rng, projects, experience, skills, rag_snippets)
    elif use_resume_anchor and slot_anchor:
        anchor = slot_anchor
    elif category == InterviewCategory.HR:
        anchor = None
    else:
        anchor = slot_anchor or _pick_anchor(rng, projects, experience, skills, rag_snippets)

    weak = rng.choice(weak_areas) if weak_areas else None
    has_anchor = bool(anchor) and not _is_generic_anchor(anchor)

    pattern_order: list[str] = []
    if pattern and pattern_allowed_for_category(pattern, category):
        pattern_order.append(pattern)
    for p in patterns_for_session(category, difficulty):
        if p not in pattern_order and pattern_allowed_for_category(p, category):
            pattern_order.append(p)

    hint = source_hint
    if not hint and anchor and not _is_generic_anchor(anchor):
        hint = anchor[:200]

    for pat in pattern_order:
        if used_patterns is not None and pat in used_patterns and len(pattern_order) > 1:
            continue
        templates = templates_for_pattern(
            pat,
            category,
            difficulty,
            has_anchor=has_anchor,
            has_weak=bool(weak),
            resume_source=resume_source if category == InterviewCategory.RESUME_BASED else None,
        )
        if not templates:
            continue
        for attempt in range(min(40, len(templates) * 4)):
            tpl = templates[(variant + order_index + attempt) % len(templates)]
            text = tpl.format(
                role=target_role,
                anchor=anchor or "your recent work",
                skill=(
                    anchor
                    if resume_source == "skill" and anchor
                    else (rng.choice(skills) if skills else "your core stack")
                ),
                weak=weak or "a skill gap you are improving",
                name=name or "you",
                variant=variant + order_index + attempt,
            )
            h = _norm_hash(text)
            key = _normalize_text_key(text)
            if h in used_hashes or key in used_texts:
                continue
            if used_patterns is not None:
                used_patterns.add(pat)
            return GeneratedQuestion(
                question_text=text,
                category=category,
                difficulty=difficulty,
                question_type=_question_type_for_pattern(pat, category),
                expected_answer_points=_answer_points(category, difficulty, anchor, pat),
                evaluation_criteria=_eval_criteria(category, difficulty, pat),
                time_limit_seconds=_TIME_BY_DIFFICULTY[difficulty],
                order_index=order_index,
                source_hint=hint,
            )
    return None


def _question_type_for_pattern(pattern: str, category: InterviewCategory) -> QuestionType:
    if pattern in (
        "star_story",
        "situational",
        "conflict_resolution",
        "leadership",
        "failure_lesson",
        "feedback",
        "prioritization",
    ):
        return QuestionType.BEHAVIORAL
    if pattern in ("motivation", "culture_fit", "career_goals", "strengths_gaps", "self_awareness"):
        return QuestionType.OPEN_ENDED
    if pattern in ("deep_dive", "metrics_impact", "redo_decision", "stakeholder"):
        return QuestionType.SITUATIONAL
    return _CATEGORY_TO_QTYPE.get(category, QuestionType.TECHNICAL)


def _templates_for(
    category: InterviewCategory,
    difficulty: InterviewDifficulty,
    has_anchor: bool,
    has_weak: bool,
) -> list[str]:
    role = "{role}"
    anchor = "{anchor}"
    skill = "{skill}"
    weak = "{weak}"

    if category == InterviewCategory.HR:
        base = [
            f"Why are you interested in this {role} position, and what would you bring in your first 90 days?",
            f"Walk me through your background and how it prepares you for {role}.",
            "Tell me about a time you received critical feedback. How did you respond?",
        ]
        if difficulty == InterviewDifficulty.ADVANCED:
            base.append(
                f"How do you handle ambiguity when priorities shift on a {role} team?",
            )
        return base

    if category == InterviewCategory.BEHAVIORAL:
        base = [
            "Describe a conflict on a team project. What was your role, and what was the outcome?",
            f"Give an example of leading work without formal authority — relevant to {role}.",
            "Tell me about a failure. What did you learn and change afterward?",
        ]
        if has_anchor:
            base.append(
                f"On {anchor}, what was the hardest interpersonal challenge and how did you handle it?",
            )
        return base

    if category == InterviewCategory.DSA:
        if difficulty == InterviewDifficulty.BEGINNER:
            return [
                f"How would you explain time vs space complexity for a problem you'd solve as a {role}?",
                "Given an array of integers, how would you find duplicates? Walk through your approach.",
                f"When would you use a hash map vs a sorted array for {role} interview problems?",
            ]
        if difficulty == InterviewDifficulty.ADVANCED:
            return [
                "Design an algorithm to merge k sorted streams efficiently. Discuss complexity and trade-offs.",
                f"How would you optimize search in a large dataset used by a {role}? Compare structures.",
            ]
        return [
            f"Walk through solving a two-pointer problem you might see for {role}. State edge cases.",
            "Explain BFS vs DFS with a scenario from {anchor}. Discuss when each fails.",
        ]

    if category == InterviewCategory.RESUME_BASED:
        return [
            f"On your project {anchor}: what was your specific contribution, and what metrics proved impact?",
            f"Deep dive into {anchor} — what technical decisions would you change today and why?",
            f"How does {anchor} demonstrate readiness for {role}? Be specific about stack and outcomes.",
            f"You listed {skill}. Where did you apply it in {anchor}, and what broke in production?",
            f"Walk me through {anchor} end-to-end as if I were the hiring manager for {role}.",
            f"What would you highlight from {anchor} on page one of your resume for {role}?",
            f"If you re-built {anchor} today, what architecture and tooling choices would you make?",
        ]

    if has_anchor and category == InterviewCategory.TECHNICAL:
        return [
            f"On your project {anchor}: what was your specific contribution, and what metrics proved impact?",
            f"Deep dive into {anchor} — what technical decisions would you change today and why?",
            f"How does {anchor} demonstrate readiness for {role}? Be specific about stack and outcomes.",
            f"You listed {skill}. Where did you apply it in {anchor}, and what broke in production?",
        ]

    if category == InterviewCategory.TECHNICAL:
        base = [
            f"As a {role}, how would you design an API for {anchor}? Cover auth, errors, and scaling.",
            f"Explain how {skill} fits into your architecture for {role}. What are common pitfalls?",
            f"Compare two approaches to caching for a service like {anchor}. When is each wrong?",
        ]
        if has_weak:
            base.append(
                f"You want to improve in {weak}. What concrete steps have you taken, and what would you do on the job?",
            )
        if difficulty == InterviewDifficulty.ADVANCED:
            base.append(
                f"For {role} at scale: how would you debug latency spikes in {anchor}?",
            )
        return base

    return [
        f"Mixed check-in: how does your experience with {anchor} support your {role} candidacy?",
        f"What is the strongest evidence on your resume that you can perform as a {role}?",
    ]


def _answer_points(
    category: InterviewCategory,
    difficulty: InterviewDifficulty,
    anchor: str | None,
    pattern: str | None = None,
) -> list[str]:
    base = [
        "Clear structure (context → action → result)",
        "Specific examples, not generic claims",
    ]
    if anchor and not _is_generic_anchor(anchor):
        base.append(f"References {anchor[:80]} with technical or business detail")
    if pattern in (
        "coding_walkthrough",
        "trace_example",
        "complexity_deep_dive",
        "optimization_challenge",
    ):
        base.extend(["States time/space complexity", "Covers edge cases and test strategy"])
    elif category == InterviewCategory.DSA:
        base.extend(["States time/space complexity", "Covers edge cases and test strategy"])
    if pattern in (
        "star_story",
        "situational",
        "conflict_resolution",
        "leadership",
        "failure_lesson",
    ):
        base.append("Uses STAR format with measurable outcome")
    elif category == InterviewCategory.BEHAVIORAL:
        base.append("Uses STAR format with measurable outcome")
    if pattern in ("compare_structures", "tradeoff_choice", "system_design"):
        base.append("Discusses trade-offs, alternatives, and when each option fails")
    if difficulty == InterviewDifficulty.ADVANCED:
        base.append("Discusses trade-offs, alternatives, and lessons learned")
    return base[:5]


def _eval_criteria(
    category: InterviewCategory,
    difficulty: InterviewDifficulty,
    pattern: str | None = None,
) -> list[str]:
    criteria = [
        "Clarity and relevance to the question",
        "Depth appropriate to stated difficulty",
    ]
    if pattern in ("debug_scenario", "observability") or category in (
        InterviewCategory.TECHNICAL,
        InterviewCategory.DSA,
        InterviewCategory.RESUME_BASED,
    ):
        criteria.append("Technical accuracy and justified design choices")
    if pattern in ("motivation", "culture_fit", "career_goals") or category == InterviewCategory.HR:
        criteria.append("Authentic motivation and role alignment")
    if (
        pattern in ("star_story", "conflict_resolution", "feedback")
        or category == InterviewCategory.BEHAVIORAL
    ):
        criteria.append("Ownership, reflection, and outcome metrics")
    if difficulty == InterviewDifficulty.ADVANCED:
        criteria.append("Anticipates follow-ups and edge cases")
    return criteria[:5]


def _category_plan(session_category: InterviewCategory, count: int) -> list[InterviewCategory]:
    if session_category != InterviewCategory.MIXED:
        return [session_category] * count
    rotation = [
        InterviewCategory.TECHNICAL,
        InterviewCategory.BEHAVIORAL,
        InterviewCategory.HR,
        InterviewCategory.DSA,
        InterviewCategory.RESUME_BASED,
    ]
    return [rotation[i % len(rotation)] for i in range(count)]


def _pick_anchor(
    rng: random.Random,
    projects: list[str],
    experience: list[str],
    skills: list[str],
    rag: list[str],
) -> str | None:
    pool: list[str] = []
    for p in projects:
        pool.append(p.split("\n", 1)[0].strip()[:120])
    for e in experience:
        pool.append(e.split("\n", 1)[0].strip()[:120])
    for r in rag:
        pool.append(r[:120])
    if not pool and skills:
        return skills[0]
    return rng.choice(pool) if pool else None


def _norm_hash(text: str) -> str:
    return hashlib.sha256(text.lower().strip().encode()).hexdigest()[:16]


def _normalize_text_key(text: str) -> str:
    return " ".join(text.lower().split())


def _try_append_question(
    questions: list[GeneratedQuestion],
    q: GeneratedQuestion,
    used_hashes: set[str],
    used_texts: set[str],
) -> bool:
    key = _normalize_text_key(q.question_text)
    h = _norm_hash(q.question_text)
    if h in used_hashes or key in used_texts:
        return False
    used_hashes.add(h)
    used_texts.add(key)
    questions.append(q)
    return True


def _finalize_unique_questions(
    *,
    questions: list[GeneratedQuestion],
    count: int,
    plan: list[InterviewCategory],
    pattern_plan: list[str],
    anchor_plan: list[ResumeAnchor | None],
    session_category: InterviewCategory,
    difficulty: InterviewDifficulty,
    target_role: str,
    extracted: ExtractedResumeData | None,
    projects: list[str],
    experience: list[str],
    skills: list[str],
    name: str | None,
    weak_areas: list[str],
    rag_snippets: list[str],
    used_hashes: set[str],
    used_texts: set[str],
    used_patterns: set[str],
    rng: random.Random,
    variant_base: int,
) -> list[GeneratedQuestion]:
    """Drop duplicate texts, then fill remaining slots with guaranteed-unique questions."""
    unique: list[GeneratedQuestion] = []
    for q in questions:
        _try_append_question(unique, q, used_hashes, used_texts)

    attempts = 0
    max_attempts = count * 120
    emergency_frames = [
        "Describe a concrete example from {anchor} when you had to make a fast decision as a {role}. (Angle {n})",
        "What would you do differently on {anchor} if you restarted today as a {role}? (Angle {n})",
        "Tell me about a metric you improved related to {anchor}. How did you measure it? (Angle {n})",
        "What was the riskiest choice you made on {anchor}, and how did you mitigate it? (Angle {n})",
        "How did you validate that {anchor} was working for users? (Angle {n})",
        "What feedback did you get on {anchor}, and what changed as a result? (Angle {n})",
        "Which part of {anchor} would you demo in five minutes to a hiring manager? (Angle {n})",
        "What did you learn from {anchor} that you still apply as a {role}? (Angle {n})",
        "If {anchor} had half the budget, what would you cut first? (Angle {n})",
        "Who did you collaborate with on {anchor}, and how did you divide ownership? (Angle {n})",
    ]

    while len(unique) < count and attempts < max_attempts:
        attempts += 1
        slot = len(unique)
        cat = plan[slot % len(plan)]
        slot_anchor, source_hint = _slot_from_plan(
            anchor_plan,
            slot,
            projects,
            skills,
            session_category,
        )
        anchor_variant = 0
        resume_source = None
        if slot < len(anchor_plan) and anchor_plan[slot] is not None:
            resume_source = anchor_plan[slot].source
            anchor_variant = anchor_plan[slot].slot_variant

        q = _build_one(
            rng=rng,
            order_index=slot,
            session_category=session_category,
            slot_category=cat,
            difficulty=difficulty,
            target_role=target_role,
            projects=projects,
            experience=experience,
            skills=skills,
            name=name,
            weak_areas=weak_areas,
            rag_snippets=rag_snippets,
            used_hashes=used_hashes,
            used_texts=used_texts,
            used_patterns=used_patterns,
            variant=variant_base + slot + attempts * 31 + anchor_variant * 17,
            pattern=pattern_plan[slot % len(pattern_plan)],
            slot_anchor=slot_anchor,
            source_hint=source_hint,
            resume_source=resume_source,
        )
        if q and _try_append_question(unique, q, used_hashes, used_texts):
            q.order_index = slot
            continue

        category = _effective_category(session_category, cat)
        anchor = slot_anchor or _SLOT_CONTEXTS[slot % len(_SLOT_CONTEXTS)]
        frame = emergency_frames[(slot + attempts) % len(emergency_frames)]
        emergency = frame.format(
            anchor=anchor,
            role=target_role,
            n=slot + attempts + 1,
        )
        if _try_append_question(
            unique,
            GeneratedQuestion(
                question_text=emergency,
                category=category,
                difficulty=difficulty,
                question_type=_CATEGORY_TO_QTYPE.get(category, QuestionType.TECHNICAL),
                expected_answer_points=_answer_points(category, difficulty, anchor),
                evaluation_criteria=_eval_criteria(category, difficulty),
                time_limit_seconds=_TIME_BY_DIFFICULTY[difficulty],
                order_index=slot,
                source_hint=source_hint,
            ),
            used_hashes,
            used_texts,
        ):
            continue

    if len(unique) < count:
        raise ValueError(
            f"Could only generate {len(unique)} unique questions out of {count} requested.",
        )

    for idx, q in enumerate(unique[:count]):
        q.order_index = idx
    return unique[:count]


def _is_generic_anchor(anchor: str | None) -> bool:
    if not anchor:
        return True
    return anchor.lower().strip() in _GENERIC_ANCHORS


def _slot_anchor(
    slot: int,
    projects: list[str],
    skills: list[str],
) -> str:
    if projects:
        return projects[slot % len(projects)].split("\n", 1)[0].strip()[:80]
    if skills:
        return skills[slot % len(skills)].strip()[:80]
    return _SLOT_CONTEXTS[slot % len(_SLOT_CONTEXTS)]


def _dedupe_preserve_order(
    questions: list[GeneratedQuestion],
    *,
    used_hashes: set[str] | None = None,
) -> list[GeneratedQuestion]:
    """Drop duplicate texts within `questions`; optionally sync hashes into `used_hashes`."""
    seen: set[str] = set()
    out: list[GeneratedQuestion] = []
    for q in questions:
        h = _norm_hash(q.question_text)
        if h in seen:
            continue
        seen.add(h)
        out.append(q)
    if used_hashes is not None:
        used_hashes.update(seen)
    return out


def _append_unique(
    questions: list[GeneratedQuestion],
    *,
    texts: list[str],
    used_hashes: set[str],
    used_texts: set[str],
    category: InterviewCategory,
    difficulty: InterviewDifficulty,
    target_role: str,
    anchor: str | None,
    order_index: int,
    source_hint: str | None = None,
) -> bool:
    for text in texts:
        q = GeneratedQuestion(
            question_text=text,
            category=category,
            difficulty=difficulty,
            question_type=_CATEGORY_TO_QTYPE.get(category, QuestionType.TECHNICAL),
            expected_answer_points=_answer_points(category, difficulty, anchor, None),
            evaluation_criteria=_eval_criteria(category, difficulty, None),
            time_limit_seconds=_TIME_BY_DIFFICULTY[difficulty],
            order_index=order_index,
            source_hint=source_hint
            or (anchor[:200] if anchor and not _is_generic_anchor(anchor) else None),
        )
        if _try_append_question(questions, q, used_hashes, used_texts):
            return True
    return False


def _last_resort_texts(
    category: InterviewCategory,
    difficulty: InterviewDifficulty,
    target_role: str,
    anchor: str,
    slot: int,
    variant_base: int,
    skill: str,
) -> list[str]:
    """Unique interviewer questions when primary and extra banks are exhausted."""
    role = target_role

    if category == InterviewCategory.DSA:
        if difficulty == InterviewDifficulty.BEGINNER:
            return [
                f"Explain the difference between an array and a linked list. When would you pick each as a {role}?",
                "How would you find duplicate values in a list? Walk through steps and time complexity.",
                "Given a string, how would you check if it is a palindrome? Discuss edge cases.",
                f"How would you merge two sorted arrays? Describe your approach for a {role} interview.",
                f"When implementing {anchor}, how would you decide between a hash map and a set?",
                f"Describe how you would test UI state logic related to {skill} without flaky tests.",
                "What is the time complexity of searching in a balanced binary search tree? Give an example.",
                f"How would you handle {anchor} if input size could grow to millions of items?",
            ]
        return [
            f"Design a function to rate-limit API calls for {anchor}. What data structure would you use?",
            f"How would you detect a cycle in a graph representing dependencies for {anchor}?",
            f"Optimize lookup for {anchor}: compare trie vs hash table vs sorted array.",
        ]

    if category == InterviewCategory.TECHNICAL:
        return [
            f"How would you structure components when building {anchor} as a {role}?",
            f"What metrics would you track after releasing work like {anchor}?",
            f"How would you roll back a bad deploy related to {anchor}?",
        ]

    if category == InterviewCategory.BEHAVIORAL:
        return [
            f"Tell me about a time you improved {anchor}. What was the measurable outcome?",
            f"Describe a disagreement while working on {anchor}. How was it resolved?",
        ]

    return [
        f"What was the hardest technical decision in {anchor}, and what would you do differently?",
        f"How does {anchor} show you are ready for {role}? Be specific.",
        f"Walk me through how {skill} helped you deliver {anchor}.",
        f"Imagine you join as {role}: how would you apply lessons from {anchor} in week one?",
    ]


def _seed(*parts: Any) -> int:
    raw = "|".join(str(p) for p in parts)
    return int(hashlib.md5(raw.encode()).hexdigest()[:8], 16)
