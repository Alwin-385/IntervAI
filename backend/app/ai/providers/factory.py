"""Resolve LLM and embedding providers from settings."""

from __future__ import annotations

from app.ai.providers.heuristic_provider import build_heuristic_analysis
from app.ai.providers.openai_provider import OpenAIEmbeddingProvider, OpenAILLMProvider
from app.core.config import Settings, get_settings

__all__ = ["build_heuristic_analysis", "get_embedding_provider", "get_llm_provider"]


def get_llm_provider(settings: Settings | None = None) -> OpenAILLMProvider:
    return OpenAILLMProvider(settings or get_settings())


def get_embedding_provider(settings: Settings | None = None) -> OpenAIEmbeddingProvider:
    return OpenAIEmbeddingProvider(settings or get_settings())
