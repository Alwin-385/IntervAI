"""Qdrant storage for resume chunk embeddings."""

from __future__ import annotations

from uuid import NAMESPACE_DNS, uuid5

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.ai.providers.openai_provider import OpenAIEmbeddingProvider
from app.core.config import get_settings
from app.core.logging import get_logger
from app.schemas.resume_extraction import ResumeTextChunk

logger = get_logger(__name__)

COLLECTION = "resume_chunks"


def _client() -> QdrantClient:
    settings = get_settings()
    return QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
        timeout=settings.qdrant_timeout_seconds,
    )


def qdrant_is_reachable() -> bool:
    try:
        client = _client()
        client.get_collections()
        return True
    except Exception as exc:
        logger.warning("qdrant_unreachable", error=str(exc))
        return False


def qdrant_is_reachable_fast() -> bool:
    """Quick check with tight timeout — avoid blocking question generation."""
    settings = get_settings()
    try:
        client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=2.0,
        )
        client.get_collections()
        return True
    except Exception:
        return False


def _ensure_collection(client: QdrantClient, dimensions: int) -> None:
    collections = {c.name for c in client.get_collections().collections}
    if COLLECTION in collections:
        return
    client.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=dimensions, distance=Distance.COSINE),
    )
    logger.info("qdrant_collection_created", collection=COLLECTION)


def _point_id(resume_id: str, chunk_index: int) -> str:
    return str(uuid5(NAMESPACE_DNS, f"resume:{resume_id}:chunk:{chunk_index}"))


def index_resume_chunks_safe(
    *,
    resume_id: str,
    user_id: str,
    chunks: list[ResumeTextChunk],
    embedder: OpenAIEmbeddingProvider,
) -> int:
    """Index chunks; return 0 on failure without raising (keeps analysis fast)."""
    if not chunks:
        return 0
    if not qdrant_is_reachable():
        logger.info("resume_embed_skipped_qdrant_down", resume_id=resume_id)
        return 0
    try:
        return index_resume_chunks(
            resume_id=resume_id,
            user_id=user_id,
            chunks=chunks,
            embedder=embedder,
        )
    except Exception as exc:
        logger.warning("resume_embed_index_failed", resume_id=resume_id, error=str(exc))
        return 0


def index_resume_chunks(
    *,
    resume_id: str,
    user_id: str,
    chunks: list[ResumeTextChunk],
    embedder: OpenAIEmbeddingProvider,
) -> int:
    if not chunks:
        return 0
    client = _client()
    _ensure_collection(client, embedder.dimensions)

    texts = [c.text for c in chunks]
    vectors = embedder.embed_texts(texts)

    client.delete(
        collection_name=COLLECTION,
        points_selector=_resume_filter(resume_id),
    )

    points = [
        PointStruct(
            id=_point_id(resume_id, chunk.index),
            vector=vectors[i],
            payload={
                "resume_id": resume_id,
                "user_id": user_id,
                "chunk_index": chunk.index,
                "text": chunk.text[:2000],
                "char_start": chunk.char_start,
                "char_end": chunk.char_end,
            },
        )
        for i, chunk in enumerate(chunks)
    ]
    client.upsert(collection_name=COLLECTION, points=points)
    return len(points)


def _resume_filter(resume_id: str):
    from qdrant_client.models import FieldCondition, Filter, MatchValue

    return Filter(must=[FieldCondition(key="resume_id", match=MatchValue(value=resume_id))])


def search_resume_chunks_safe(
    *,
    resume_id: str,
    user_id: str,
    query_text: str,
    embedder: OpenAIEmbeddingProvider,
    limit: int = 8,
) -> list[str]:
    """Vector search over resume chunks; returns text snippets or [] on failure."""
    if not query_text.strip():
        return []
    if not qdrant_is_reachable():
        return []
    try:
        return search_resume_chunks(
            resume_id=resume_id,
            user_id=user_id,
            query_text=query_text,
            embedder=embedder,
            limit=limit,
        )
    except Exception as exc:
        logger.warning(
            "resume_chunk_search_failed",
            resume_id=resume_id,
            error=str(exc),
        )
        return []


def search_resume_chunks(
    *,
    resume_id: str,
    user_id: str,
    query_text: str,
    embedder: OpenAIEmbeddingProvider,
    limit: int = 8,
) -> list[str]:
    client = _client()
    _ensure_collection(client, embedder.dimensions)
    vector = embedder.embed_texts([query_text])[0]
    from qdrant_client.models import FieldCondition, Filter, MatchValue

    results = client.search(
        collection_name=COLLECTION,
        query_vector=vector,
        query_filter=Filter(
            must=[
                FieldCondition(key="resume_id", match=MatchValue(value=resume_id)),
                FieldCondition(key="user_id", match=MatchValue(value=user_id)),
            ],
        ),
        limit=limit,
    )
    snippets: list[str] = []
    for hit in results:
        text = (hit.payload or {}).get("text")
        if text and isinstance(text, str):
            snippets.append(text.strip())
    return snippets
