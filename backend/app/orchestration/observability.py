"""Workflow tracing and structured observability (Phase 17)."""

from __future__ import annotations

import time
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any

import structlog

from app.core.logging import get_logger

logger = get_logger(__name__)


def new_workflow_id() -> str:
    return str(uuid.uuid4())


@dataclass
class WorkflowTrace:
    workflow_id: str
    agent: str
    step: str
    started_at: float = field(default_factory=time.perf_counter)
    metadata: dict[str, Any] = field(default_factory=dict)

    def elapsed_ms(self) -> float:
        return (time.perf_counter() - self.started_at) * 1000


@contextmanager
def trace_workflow(
    *,
    workflow_id: str,
    agent: str,
    step: str,
    **metadata: Any,
) -> Iterator[WorkflowTrace]:
    trace = WorkflowTrace(
        workflow_id=workflow_id,
        agent=agent,
        step=step,
        metadata=metadata,
    )
    structlog.contextvars.bind_contextvars(
        workflow_id=workflow_id,
        agent=agent,
        orchestration_step=step,
    )
    logger.info(
        "orchestration_step_start",
        workflow_id=workflow_id,
        agent=agent,
        step=step,
        **metadata,
    )
    try:
        yield trace
        logger.info(
            "orchestration_step_ok",
            workflow_id=workflow_id,
            agent=agent,
            step=step,
            duration_ms=round(trace.elapsed_ms(), 2),
        )
    except Exception as exc:
        logger.exception(
            "orchestration_step_failed",
            workflow_id=workflow_id,
            agent=agent,
            step=step,
            duration_ms=round(trace.elapsed_ms(), 2),
            error=str(exc),
        )
        raise
    finally:
        structlog.contextvars.unbind_contextvars(
            "workflow_id",
            "agent",
            "orchestration_step",
        )
