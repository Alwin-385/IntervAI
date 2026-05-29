"""LLM and embedding provider abstraction."""

from __future__ import annotations

from typing import Protocol


class LLMProvider(Protocol):
    @property
    def name(self) -> str: ...

    def is_available(self) -> bool: ...

    def complete_json(self, *, system: str, user: str, temperature: float = 0.2) -> str: ...


class EmbeddingProvider(Protocol):
    @property
    def name(self) -> str: ...

    def is_available(self) -> bool: ...

    def embed_texts(self, texts: list[str]) -> list[list[float]]: ...

    @property
    def dimensions(self) -> int: ...
