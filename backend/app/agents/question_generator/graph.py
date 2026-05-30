"""LangGraph workflow for personalized interview question generation."""

from __future__ import annotations

import json
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from app.agents.question_generator.heuristic import build_heuristic_questions
from app.agents.question_generator.prompts import SYSTEM_PROMPT, USER_TEMPLATE
from app.ai.providers.factory import get_embedding_provider, get_llm_provider
from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.enums import InterviewCategory, InterviewDifficulty
from app.schemas.interview_questions_gen import GeneratedQuestion
from app.schemas.resume_extraction import ExtractedResumeData
from app.vectorstore.resume_vectors import qdrant_is_reachable_fast, search_resume_chunks_safe

logger = get_logger(__name__)


class QuestionGenState(TypedDict, total=False):
    session_id: str
    target_role: str
    session_category: str
    difficulty: str
    question_count: int
    resume_id: str | None
    user_id: str
    cleaned_text: str
    extracted_data: dict[str, Any]
    weak_areas: list[str]
    existing_questions: list[str]
    generation_nonce: str
    rag_snippets: list[str]
    questions: list[dict[str, Any]]
    error: str | None


def _load_context(state: QuestionGenState) -> QuestionGenState:
    return state


def _retrieve_rag(state: QuestionGenState) -> QuestionGenState:
    settings = get_settings()
    if (
        settings.interview_questions_skip_rag
        or not state.get("resume_id")
        or not qdrant_is_reachable_fast()
    ):
        return {**state, "rag_snippets": []}

    embedder = get_embedding_provider(settings)
    if not embedder.is_available():
        return {**state, "rag_snippets": []}

    role = state.get("target_role") or "Software Engineer"
    category = state.get("session_category") or "mixed"
    query = (
        f"Interview questions for {role} {category} role: "
        f"projects skills experience achievements technical behavioral"
    )
    snippets = search_resume_chunks_safe(
        resume_id=state["resume_id"],
        user_id=state.get("user_id") or "",
        query_text=query,
        embedder=embedder,
        limit=8,
    )
    logger.info(
        "question_gen_rag",
        resume_id=state.get("resume_id"),
        chunks=len(snippets),
    )
    return {**state, "rag_snippets": snippets}


def _generate_questions(state: QuestionGenState) -> QuestionGenState:
    settings = get_settings()
    count = int(state.get("question_count") or 5)
    target_role = state.get("target_role") or "Software Engineer"
    session_category = InterviewCategory(state.get("session_category") or "mixed")
    difficulty = InterviewDifficulty(state.get("difficulty") or "intermediate")
    extracted = ExtractedResumeData.model_validate(state.get("extracted_data") or {})
    weak_areas = list(state.get("weak_areas") or [])
    existing = list(state.get("existing_questions") or [])
    rag = list(state.get("rag_snippets") or [])

    use_llm = (
        settings.interview_questions_use_openai
        and bool(settings.openai_api_key)
        and not settings.interview_questions_heuristic_only
    )

    questions = build_heuristic_questions(
        target_role=target_role,
        session_category=session_category,
        difficulty=difficulty,
        count=count,
        extracted=extracted,
        weak_areas=weak_areas,
        rag_snippets=rag,
        existing_texts=existing,
        generation_nonce=state.get("generation_nonce"),
    )

    if use_llm:
        try:
            llm_questions = _generate_with_llm(
                target_role=target_role,
                session_category=session_category,
                difficulty=difficulty,
                count=count,
                extracted=extracted,
                cleaned_text=state.get("cleaned_text") or "",
                weak_areas=weak_areas,
                existing=existing,
                rag=rag,
            )
            if len(llm_questions) >= count:
                questions = llm_questions
                logger.info("question_gen_llm_ok", count=len(questions))
        except Exception as exc:
            logger.warning("question_gen_llm_failed", error=str(exc))

    from app.agents.question_generator.heuristic import ensure_exact_question_count

    questions = ensure_exact_question_count(
        questions=questions,
        count=count,
        target_role=target_role,
        session_category=session_category,
        difficulty=difficulty,
        extracted=extracted,
        weak_areas=weak_areas,
        rag_snippets=rag,
        generation_nonce=state.get("generation_nonce"),
    )

    return {
        **state,
        "questions": [q.model_dump() for q in questions],
    }


def _generate_with_llm(
    *,
    target_role: str,
    session_category: InterviewCategory,
    difficulty: InterviewDifficulty,
    count: int,
    extracted: ExtractedResumeData,
    cleaned_text: str,
    weak_areas: list[str],
    existing: list[str],
    rag: list[str],
) -> list[GeneratedQuestion]:
    llm = get_llm_provider()
    resume_context = _format_resume_context(extracted, cleaned_text, rag)
    mix_instruction = _mix_instruction(session_category, count)
    user_msg = USER_TEMPLATE.format(
        count=count,
        target_role=target_role,
        category=session_category.value,
        difficulty=difficulty.value,
        resume_context=resume_context[:14000],
        weak_areas="\n".join(f"- {w}" for w in weak_areas) or "(none listed)",
        existing_questions="\n".join(f"- {q[:200]}" for q in existing) or "(none)",
        mix_instruction=mix_instruction,
    )
    raw = llm.complete_json(system=SYSTEM_PROMPT, user=user_msg)
    payload = json.loads(raw)
    items = payload.get("questions") or []
    out: list[GeneratedQuestion] = []
    for _idx, item in enumerate(items[: count * 2]):
        try:
            item = dict(item)
            item["order_index"] = len(out)
            if "time_limit_seconds" not in item:
                item["time_limit_seconds"] = 180
            if item.get("category") == "mixed":
                item["category"] = session_category.value
            out.append(GeneratedQuestion.model_validate(item))
        except Exception:
            continue
        if len(out) >= count:
            break
    return out


def _format_resume_context(
    extracted: ExtractedResumeData,
    cleaned_text: str,
    rag: list[str],
) -> str:
    parts = [json.dumps(extracted.model_dump(), indent=2)[:6000]]
    if cleaned_text:
        parts.append("\n--- Resume text ---\n" + cleaned_text[:8000])
    if rag:
        parts.append("\n--- Retrieved chunks ---\n" + "\n---\n".join(rag[:8]))
    return "\n".join(parts)


def _mix_instruction(category: InterviewCategory, count: int) -> str:
    if category != InterviewCategory.MIXED:
        return f"All questions should focus on {category.value} style."
    per = max(1, count // 5)
    return f"Distribute ~{per} each across HR, technical, behavioral, DSA, and resume-based angles."


def _build_graph():
    graph = StateGraph(QuestionGenState)
    graph.add_node("load", _load_context)
    graph.add_node("retrieve", _retrieve_rag)
    graph.add_node("generate", _generate_questions)
    graph.set_entry_point("load")
    graph.add_edge("load", "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)
    return graph.compile()


_compiled_graph = None


def run_question_generator(initial: QuestionGenState) -> QuestionGenState:
    """Run pipeline steps directly (linear graph) — avoids LangGraph invoke stalls."""
    state: QuestionGenState = dict(initial)
    state = _load_context(state)
    state = _retrieve_rag(state)
    state = _generate_questions(state)
    return state


def run_question_generator_via_graph(initial: QuestionGenState) -> QuestionGenState:
    """Optional compiled LangGraph path (same steps)."""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = _build_graph()
    return _compiled_graph.invoke(initial)
