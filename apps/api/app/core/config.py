from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Terminal Agent API"
    service_name: str = "terminal-agent-api"
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
