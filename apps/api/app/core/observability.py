import logging
from dataclasses import dataclass
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.tracing import TraceClient

TRACE_ID_HEADER = "x-trace-id"


@dataclass(frozen=True)
class TraceContext:
    request_id: str
    trace_id: str


def create_trace_context() -> TraceContext:
    request_id = str(uuid4())
    return TraceContext(request_id=request_id, trace_id=request_id)


def get_trace_context(request: Request) -> TraceContext:
    context = getattr(request.state, "trace_context", None)

    if isinstance(context, TraceContext):
        return context

    context = create_trace_context()
    request.state.trace_context = context
    return context


def log_event(
    logger: logging.Logger,
    event: str,
    context: TraceContext,
    message: str,
    level: int = logging.INFO,
) -> None:
    logger.log(
        level,
        message,
        extra={
            "event": event,
            "request_id": context.request_id,
            "trace_id": context.trace_id,
        },
    )


class ObservabilityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, service_name: str, trace_client: TraceClient) -> None:
        super().__init__(app)
        self.service_name = service_name
        self.trace_client = trace_client
        self.logger = logging.getLogger("app.request")

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        context = create_trace_context()
        request.state.trace_context = context

        log_event(
            self.logger,
            "request.started",
            context,
            f"{request.method} {request.url.path} started",
        )

        with self.trace_client.span(
            context,
            "http.request",
            {
                "method": request.method,
                "path": request.url.path,
                "service": self.service_name,
            },
        ):
            response = await call_next(request)
        response.headers[TRACE_ID_HEADER] = context.trace_id

        log_event(
            self.logger,
            "request.completed",
            context,
            f"{request.method} {request.url.path} completed with {response.status_code}",
        )

        return response
