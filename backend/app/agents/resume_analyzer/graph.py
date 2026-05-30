"""Resume analysis pipeline — fast, direct steps (no background thread)."""

from __future__ import annotations

import json
from typing import Any, TypedDict

from app.agents.resume_analyzer.prompts import SYSTEM_PROMPT, USER_TEMPLATE
from app.ai.providers.factory import (
    build_heuristic_analysis,
    get_embedding_provider,
    get_llm_provider,
)
from app.core.config import get_settings
from app.core.logging import get_logger
from app.schemas.resume_analyzer import AnalysisProgress, StructuredResumeAnalysis
from app.schemas.resume_extraction import ExtractedResumeData, ResumeTextChunk
from app.services.resume_analysis_progress import persist_analysis_progress
from app.vectorstore.resume_vectors import index_resume_chunks_safe

logger = get_logger(__name__)


class AnalyzerState(TypedDict, total=False):
    resume_id: str
    analysis_id: str
    user_id: str
    target_role: str | None
    cleaned_text: str
    extracted_data: dict[str, Any]
    chunks: list[dict[str, Any]]
    embeddings_indexed: int
    analysis: dict[str, Any]


def _analyze_step(state: AnalyzerState) -> AnalyzerState:
    aid = state.get("analysis_id")
    extracted = ExtractedResumeData.model_validate(state.get("extracted_data") or {})
    target_role = state.get("target_role") or "Software Engineer"
    cleaned = state.get("cleaned_text") or ""
    settings = get_settings()

    if aid:
        persist_analysis_progress(
            aid,
            AnalysisProgress(
                step="analysis", percent=60, message="Running recruiter-style review…"
            ),
        )

    analysis: StructuredResumeAnalysis | None = None
    use_llm = not settings.resume_analysis_heuristic_only and bool(settings.openai_api_key)

    if use_llm:
        llm = get_llm_provider(settings)
        try:
            user_msg = USER_TEMPLATE.format(
                target_role=target_role,
                extracted_json=json.dumps(extracted.model_dump(), indent=2)[:8000],
                cleaned_text=cleaned[:20000],
            )
            raw = llm.complete_json(system=SYSTEM_PROMPT, user=user_msg)
            payload = json.loads(raw)
            payload["role_target"] = payload.get("role_target") or target_role
            analysis = StructuredResumeAnalysis.model_validate(payload)
            logger.info("resume_analysis_llm_ok", analysis_id=aid)
        except Exception as exc:
            logger.warning("resume_llm_analysis_failed", error=str(exc), analysis_id=aid)

    if analysis is None:
        analysis = build_heuristic_analysis(
            extracted,
            target_role=target_role,
            cleaned_text=cleaned,
        )

    analysis.embeddings_indexed = state.get("embeddings_indexed", 0)
    return {**state, "analysis": analysis.model_dump()}


def _embed_step(state: AnalyzerState) -> AnalyzerState:
    settings = get_settings()
    if settings.resume_analysis_skip_embeddings:
        return {**state, "embeddings_indexed": 0}

    chunks = [ResumeTextChunk.model_validate(c) for c in state.get("chunks") or []]
    indexed = 0
    embedder = get_embedding_provider(settings)
    if embedder.is_available() and chunks:
        indexed = index_resume_chunks_safe(
            resume_id=state["resume_id"],
            user_id=state["user_id"],
            chunks=chunks,
            embedder=embedder,
        )

    if state.get("analysis"):
        merged = dict(state["analysis"])
        merged["embeddings_indexed"] = indexed
        return {**state, "embeddings_indexed": indexed, "analysis": merged}
    return {**state, "embeddings_indexed": indexed}


def run_resume_analyzer(
    *,
    resume_id: str,
    analysis_id: str,
    user_id: str,
    target_role: str | None,
    cleaned_text: str,
    extracted_data: dict[str, Any],
    chunks: list[dict[str, Any]],
) -> StructuredResumeAnalysis:
    state: AnalyzerState = {
        "resume_id": resume_id,
        "analysis_id": analysis_id,
        "user_id": user_id,
        "target_role": target_role,
        "cleaned_text": cleaned_text,
        "extracted_data": extracted_data,
        "chunks": chunks,
        "embeddings_indexed": 0,
    }
    state = _analyze_step(state)
    state = _embed_step(state)
    raw = state.get("analysis")
    if not raw:
        raise RuntimeError("Analyzer produced no output")
    return StructuredResumeAnalysis.model_validate(raw)
