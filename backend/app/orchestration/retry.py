"""Retry policies for orchestrated agent nodes (Phase 17)."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

from app.core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    base_delay_seconds: float = 0.5
    max_delay_seconds: float = 8.0
    exponential: bool = True

    def delay_for_attempt(self, attempt: int) -> float:
        if not self.exponential:
            return self.base_delay_seconds
        delay = self.base_delay_seconds * (2**attempt)
        return min(delay, self.max_delay_seconds)


def run_with_retry(
    fn: Callable[[], T],
    *,
    policy: RetryPolicy,
    workflow_id: str,
    agent: str,
    step: str,
) -> T:
    last_exc: Exception | None = None
    attempts = max(1, policy.max_attempts)
    for attempt in range(attempts):
        try:
            if attempt > 0:
                logger.info(
                    "orchestration_retry",
                    workflow_id=workflow_id,
                    agent=agent,
                    step=step,
                    attempt=attempt + 1,
                    max_attempts=attempts,
                )
            return fn()
        except Exception as exc:
            last_exc = exc
            logger.warning(
                "orchestration_attempt_failed",
                workflow_id=workflow_id,
                agent=agent,
                step=step,
                attempt=attempt + 1,
                error=str(exc),
            )
            if attempt < attempts - 1:
                time.sleep(policy.delay_for_attempt(attempt))
    assert last_exc is not None
    raise last_exc
