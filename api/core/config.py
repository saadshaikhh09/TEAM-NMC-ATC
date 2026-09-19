"""Settings + policy loader. Owner: Person A."""
from functools import lru_cache
from pathlib import Path

import yaml
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://concierge:concierge@localhost:5432/concierge"
    demo_mode: bool = True
    demo_poll_seconds: int = 15
    provider_flight: str = "mock"
    provider_hotel: str = "mock"
    llm_provider: str = "gemini"
    gemini_api_key: str = ""
    openai_api_key: str = ""
    aviationstack_api_key: str = ""
    duffel_api_key: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def settings() -> Settings:
    return Settings()


@lru_cache
def policy() -> dict:
    """Loads policy.yaml. Nothing in the engine hardcodes a limit."""
    path = Path(__file__).resolve().parents[2] / "policy.yaml"
    return yaml.safe_load(path.read_text())
