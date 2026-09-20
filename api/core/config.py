"""Settings + policy loader. Owner: Person A."""
from functools import lru_cache
import os
from pathlib import Path

import yaml
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://concierge:concierge@localhost:5432/concierge"
    demo_mode: bool = True
    demo_poll_seconds: int = 15
    provider_flight_status: str = "mock"
    provider_flight_search: str = "mock"
    provider_hotel: str = "mock"
    llm_provider: str = "gemini"
    gemini_api_key: str = ""
    openai_api_key: str = ""
    aviationstack_api_key: str = ""
    duffel_api_key: str = ""
    quota_aerodatabox_monthly: int = 500
    quota_aviationstack_monthly: int = 500
    quota_dev_budget_fraction: float = 0.4
    environment: str = "development"
    testing: bool = False
    cors_origins: str = "http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174"

    class Config:
        # Absolute, not ".env": `make api` runs from api/, where no .env exists,
        # and a relative path there silently yields the defaults above.
        # Test runs must use only explicit environment variables. In particular,
        # never load a developer's real database URL or paid-provider keys.
        env_file = None if os.environ.get("TESTING", "").lower() == "true" else Path(__file__).resolve().parents[2] / ".env"
        extra = "ignore"


@lru_cache
def settings() -> Settings:
    return Settings()


@lru_cache
def policy() -> dict:
    """Loads policy.yaml. Nothing in the engine hardcodes a limit."""
    path = Path(__file__).resolve().parents[2] / "policy.yaml"
    return yaml.safe_load(path.read_text())
