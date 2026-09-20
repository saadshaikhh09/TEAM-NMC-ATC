"""Small helpers shared by the two status-only provider adapters."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import dotenv_values


def config_value(name: str, default: str = "") -> str:
    """Read an environment value, falling back to the repository's .env."""
    value = os.getenv(name)
    if value is None and os.getenv("TESTING", "").lower() != "true":
        value = dotenv_values(Path(__file__).resolve().parents[2] / ".env").get(name)
    return str(value).strip() if value is not None else default


def parse_utc(value: str | None, field: str) -> datetime:
    if not value:
        raise ValueError(f"missing {field}")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} has no timezone")
    return parsed.astimezone(timezone.utc)


def flight_key(value: str) -> str:
    return "".join(char for char in value.upper() if char.isalnum())
