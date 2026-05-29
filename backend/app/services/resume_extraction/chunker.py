"""Split cleaned resume text into overlapping chunks for downstream RAG."""

from __future__ import annotations

from app.schemas.resume_extraction import ResumeTextChunk

DEFAULT_CHUNK_SIZE = 900
DEFAULT_OVERLAP = 120


def chunk_resume_text(
    text: str,
    *,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> list[ResumeTextChunk]:
    if not text.strip():
        return []

    chunks: list[ResumeTextChunk] = []
    start = 0
    index = 0
    length = len(text)

    while start < length:
        end = min(start + chunk_size, length)
        if end < length:
            boundary = text.rfind("\n", start, end)
            if boundary > start + chunk_size // 2:
                end = boundary
        segment = text[start:end].strip()
        if segment:
            chunks.append(
                ResumeTextChunk(
                    index=index,
                    text=segment,
                    char_start=start,
                    char_end=end,
                )
            )
            index += 1
        if end >= length:
            break
        start = max(end - overlap, start + 1)

    return chunks
