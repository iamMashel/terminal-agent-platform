from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.observability import ObservabilityMiddleware
from app.core.tracing import build_trace_client
from app.routes.chat import router as chat_router
from app.routes.commands import router as commands_router
from app.routes.health import router as health_router


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings)
    app = FastAPI(title=settings.app_name)

    app.add_middleware(
        ObservabilityMiddleware,
        service_name=settings.service_name,
        trace_client=build_trace_client(settings),
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(chat_router)
    app.include_router(commands_router)
    return app


app = create_app()
