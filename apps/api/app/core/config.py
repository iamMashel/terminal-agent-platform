from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Terminal Agent API"
    service_name: str = "terminal-agent-api"
    log_level: str = "INFO"
    langfuse_enabled: bool = False
    langfuse_host: str = "https://cloud.langfuse.com"
    llm_provider: str = "mock"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-haiku-4-5-20251001"
    anthropic_max_tokens: int = 512
    anthropic_retry_attempts: int = 2
    database_url: str = "sqlite:///./terminal_agent.db"
    execution_image: str = "alpine:3.20"
    execution_timeout_seconds: int = 30
    execution_memory_limit: str = "128m"
    execution_cpu_quota: int = 50000
    execution_cpu_period: int = 100000
    execution_user: str = "65534:65534"
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="API_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
