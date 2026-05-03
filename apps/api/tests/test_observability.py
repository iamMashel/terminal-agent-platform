import json
import logging

import anyio
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings
from app.core.logging import JsonFormatter
from app.core.observability import TRACE_ID_HEADER, TraceContext, log_event
from app.core.tracing import NoopTraceClient, build_trace_client
from app.main import app


def test_json_formatter_includes_trace_fields() -> None:
    record = logging.LogRecord(
        name="app.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello",
        args=(),
        exc_info=None,
    )
    record.event = "test.event"
    record.request_id = "request-1"
    record.trace_id = "trace-1"

    payload = json.loads(JsonFormatter().format(record))

    assert payload["level"] == "INFO"
    assert payload["logger"] == "app.test"
    assert payload["message"] == "hello"
    assert payload["event"] == "test.event"
    assert payload["request_id"] == "request-1"
    assert payload["trace_id"] == "trace-1"


def test_log_event_adds_structured_extra_fields(caplog) -> None:
    logger = logging.getLogger("app.test")
    context = TraceContext(request_id="request-1", trace_id="trace-1")

    with caplog.at_level(logging.INFO):
        log_event(logger, "test.event", context, "structured message")

    record = caplog.records[-1]
    assert record.event == "test.event"
    assert record.request_id == "request-1"
    assert record.trace_id == "trace-1"


def test_request_middleware_adds_trace_id_header() -> None:
    async def request_health() -> str:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")

        assert response.status_code == 200
        return response.headers[TRACE_ID_HEADER]

    trace_id = anyio.run(request_health)

    assert trace_id


def test_langfuse_tracing_defaults_to_noop_when_disabled() -> None:
    trace_client = build_trace_client(Settings(langfuse_enabled=False))

    assert isinstance(trace_client, NoopTraceClient)
