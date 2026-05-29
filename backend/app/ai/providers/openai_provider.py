"""OpenAI chat + embeddings implementation."""

from __future__ import annotations

import json

from openai import OpenAI

from app.core.config import Settings


class OpenAILLMProvider:
    name = "openai"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: OpenAI | None = None
        self._model = settings.openai_chat_model

    def _get_client(self) -> OpenAI:
        if self._client is None:
            if not self._settings.openai_api_key:
                raise ValueError("OpenAI API key is not configured")
            self._client = OpenAI(
                api_key=self._settings.openai_api_key,
                timeout=self._settings.openai_request_timeout_seconds,
                max_retries=1,
            )
        return self._client

    def is_available(self) -> bool:
        return bool(self._settings.openai_api_key)

    def complete_json(self, *, system: str, user: str, temperature: float = 0.2) -> str:
        response = self._get_client().chat.completions.create(
            model=self._model,
            temperature=temperature,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response from OpenAI")
        return content


class OpenAIEmbeddingProvider:
    name = "openai-embeddings"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: OpenAI | None = None
        self._model = settings.openai_embedding_model
        self._dimensions = settings.openai_embedding_dimensions

    def _get_client(self) -> OpenAI:
        if self._client is None:
            if not self._settings.openai_api_key:
                raise ValueError("OpenAI API key is not configured")
            self._client = OpenAI(
                api_key=self._settings.openai_api_key,
                timeout=self._settings.openai_request_timeout_seconds,
                max_retries=1,
            )
        return self._client

    def is_available(self) -> bool:
        return bool(self._settings.openai_api_key)

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        response = self._get_client().embeddings.create(
            model=self._model,
            input=texts,
            dimensions=self._dimensions,
        )
        return [item.embedding for item in response.data]
