from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Protocol

from app.core.config import Settings

if TYPE_CHECKING:
    from app.core.observability import TraceContext


class TraceClient(Protocol):
    @contextmanager
    def span(
        self,
        context: TraceContext,
        name: str,
        metadata: dict[str, Any] | None = None,
    ) -> Iterator[None]:
        yield


class NoopTraceClient:
    @contextmanager
    def span(
        self,
        context: TraceContext,
        name: str,
        metadata: dict[str, Any] | None = None,
    ) -> Iterator[None]:
        yield


class LangfuseTraceClient:
    def __init__(self, settings: Settings) -> None:
        os.environ.setdefault("LANGFUSE_HOST", settings.langfuse_host)

        from langfuse import Langfuse, get_client

        self._langfuse_cls = Langfuse
        self._client = get_client()

    @contextmanager
    def span(
        self,
        context: TraceContext,
        name: str,
        metadata: dict[str, Any] | None = None,
    ) -> Iterator[None]:
        trace_id = self._langfuse_cls.create_trace_id(seed=context.trace_id)

        with self._client.start_as_current_observation(
            as_type="span",
            name=name,
            trace_context={"trace_id": trace_id},
        ) as span:
            span.update(metadata=metadata or {})
            yield


def build_trace_client(settings: Settings) -> TraceClient:
    if not settings.langfuse_enabled:
        return NoopTraceClient()

    return LangfuseTraceClient(settings)
