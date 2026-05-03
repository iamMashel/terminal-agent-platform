from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Terminal Agent API"
    service_name: str = "terminal-agent-api"
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
