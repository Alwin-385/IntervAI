"""Production security middleware and utilities."""

from __future__ import annotations

import re
import time
from collections import defaultdict
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.logging import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Secure response headers
# ---------------------------------------------------------------------------

SECURE_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload",
}


class SecureHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        for header, value in SECURE_HEADERS.items():
            response.headers.setdefault(header, value)
        return response


# ---------------------------------------------------------------------------
# In-process rate limiter (per IP, sliding window)
# ---------------------------------------------------------------------------

class _RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window = window_seconds
        self._buckets: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, key: str) -> bool:
        now = time.monotonic()
        window_start = now - self.window
        hits = self._buckets[key]
        # Evict old entries
        while hits and hits[0] < window_start:
            hits.pop(0)
        if len(hits) >= self.max_requests:
            return False
        hits.append(now)
        return True


def _build_limiters() -> tuple[_RateLimiter, _RateLimiter, _RateLimiter]:
    try:
        from app.core.config import get_settings
        s = get_settings()
        return (
            _RateLimiter(s.rate_limit_default_rpm, 60),
            _RateLimiter(s.rate_limit_upload_rpm, 60),
            _RateLimiter(s.rate_limit_ai_rpm, 60),
        )
    except Exception:
        return (
            _RateLimiter(120, 60),
            _RateLimiter(10, 60),
            _RateLimiter(30, 60),
        )


_default_limiter, _upload_limiter, _ai_limiter = _build_limiters()

# URL prefixes that get tighter AI limits
_AI_PATHS = (
    "/api/v1/interviews",
    "/api/v1/answers",
    "/api/v1/roadmap",
    "/api/v1/analytics",
    "/api/v1/speech",
)
_UPLOAD_PATHS = ("/api/v1/resumes", "/api/resumes")


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding-window in-process rate limiter keyed by client IP."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        ip = _client_ip(request)
        path = request.url.path

        if any(path.startswith(p) for p in _UPLOAD_PATHS) and request.method == "POST":
            limiter = _upload_limiter
            limit_label = "upload"
        elif any(path.startswith(p) for p in _AI_PATHS):
            limiter = _ai_limiter
            limit_label = "ai"
        else:
            limiter = _default_limiter
            limit_label = "default"

        if not limiter.is_allowed(ip):
            logger.warning("rate_limit_hit", ip=ip, path=path, limit=limit_label)
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please slow down."},
                headers={"Retry-After": str(limiter.window)},
            )

        return await call_next(request)


# ---------------------------------------------------------------------------
# Prompt injection defence
# ---------------------------------------------------------------------------

_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?previous\s+(instructions?|prompts?)", re.IGNORECASE),
    re.compile(r"(system\s*prompt|you\s+are\s+now|act\s+as\s+an?\s+)", re.IGNORECASE),
    re.compile(r"(jailbreak|DAN\s+mode|disregard\s+(safety|guidelines))", re.IGNORECASE),
    re.compile(r"<\s*(system|assistant|human)\s*>", re.IGNORECASE),
    re.compile(r"\[\s*(INST|/INST|SYS|/SYS)\s*\]", re.IGNORECASE),
    re.compile(r"###\s*(Instruction|System|Human|Assistant)", re.IGNORECASE),
]

_MAX_USER_INPUT_LEN = 4_000  # chars — generous for long answers


def sanitize_user_input(text: str, *, field_name: str = "input") -> str:
    """Strip / reject obvious prompt-injection patterns. Returns cleaned text."""
    if not isinstance(text, str):
        return text  # type: ignore[return-value]

    if len(text) > _MAX_USER_INPUT_LEN:
        logger.warning("user_input_truncated", field=field_name, original_len=len(text))
        text = text[:_MAX_USER_INPUT_LEN]

    for pattern in _INJECTION_PATTERNS:
        if pattern.search(text):
            logger.warning(
                "prompt_injection_attempt",
                field=field_name,
                pattern=pattern.pattern[:60],
            )
            text = pattern.sub("[removed]", text)

    return text


# ---------------------------------------------------------------------------
# AI output sanitiser  (strip stray prompt markers from LLM responses)
# ---------------------------------------------------------------------------

_OUTPUT_STRIP_PATTERNS = [
    re.compile(r"<\s*(system|assistant|human)\s*>.*?<\s*/\s*(system|assistant|human)\s*>", re.IGNORECASE | re.DOTALL),
    re.compile(r"\[\s*(INST|/INST|SYS|/SYS)\s*\]", re.IGNORECASE),
    re.compile(r"###\s*(Instruction|System|Human|Assistant)\s*:", re.IGNORECASE),
]


def sanitize_ai_output(text: str) -> str:
    """Remove leaked prompt markers from LLM-generated text."""
    if not isinstance(text, str):
        return text  # type: ignore[return-value]
    for pattern in _OUTPUT_STRIP_PATTERNS:
        text = pattern.sub("", text)
    return text.strip()


# ---------------------------------------------------------------------------
# PDF / file upload validation
# ---------------------------------------------------------------------------

_PDF_MAGIC = b"%PDF-"
_MAX_PDF_BYTES = 5 * 1024 * 1024  # 5 MB


def validate_pdf_bytes(data: bytes, *, max_bytes: int = _MAX_PDF_BYTES) -> None:
    """Raise ValueError for invalid or oversized PDF uploads."""
    if not data:
        raise ValueError("Uploaded file is empty.")
    if len(data) > max_bytes:
        raise ValueError(f"File exceeds maximum size of {max_bytes // (1024 * 1024)} MB.")
    if not data.lstrip()[:5].startswith(_PDF_MAGIC):
        raise ValueError("Uploaded file does not appear to be a valid PDF.")
