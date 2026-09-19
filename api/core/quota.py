"""API call budget guard. Owner: Person A. WRITE THIS BEFORE ANY LIVE CALL.

The arithmetic nobody did:

    AeroDataBox  free tier: 500 requests / MONTH
    AviationStack free tier: 500 requests / MONTH

    Our own tiered schedule at 15-minute polling inside the last 24 hours
    is 96 calls per flight per day. Three seeded travellers = 288/day.
    We exhaust a month of quota in under two days of idle running.

    Worse: we will rehearse the demo roughly thirty times. If a rehearsal
    touches a live status API, the quota is gone before the pitch.

So:

  1. DEMO_MODE=true means NO live status call happens. Ever. Mock only.
  2. Tests never call a live provider. If a test needs a status, it fakes one.
  3. Development is capped at QUOTA_DEV_BUDGET_FRACTION of the month, so
     there is headroom left for the one live run on stage.
  4. Every live call goes through spend(). A provider module that calls
     httpx directly is a bug, and reviewing for it is worth the two minutes.

This is not defensive over-engineering. It is the difference between having a
live API to show a judge and having a 429 on stage.
"""
from datetime import date

from sqlalchemy import text

from core.config import settings
from core.db import SessionLocal


HARD_MONTHLY_LIMIT = 500
PROVIDERS = {
    "aerodatabox": "quota_aerodatabox_monthly",
    "aviationstack": "quota_aviationstack_monthly",
}


class QuotaExceeded(RuntimeError):
    pass


def _budget(provider: str) -> int:
    try:
        setting_name = PROVIDERS[provider]
    except KeyError as exc:
        raise ValueError(f"unknown quota provider {provider!r}") from exc

    config = settings()
    fraction = config.quota_dev_budget_fraction
    if not 0 <= fraction <= 1:
        raise ValueError("QUOTA_DEV_BUDGET_FRACTION must be between 0 and 1")
    return int(min(getattr(config, setting_name), HARD_MONTHLY_LIMIT) * fraction)


def _year_month() -> str:
    return date.today().strftime("%Y-%m")


def spend(provider: str, n: int = 1) -> None:
    """Record n calls against provider's monthly budget, or raise.

    Counter persists in Postgres so a process restart does not reset it.
    Raise QuotaExceeded rather than returning False — a silent skip produces
    a stale status, which is worse than a loud failure.
    """
    budget = _budget(provider)
    if n < 1:
        raise ValueError("quota spend must be at least 1")
    if settings().demo_mode:
        raise QuotaExceeded("DEMO_MODE blocks live status API calls")

    with SessionLocal.begin() as session:
        used = session.execute(
            text(
                """
                INSERT INTO api_quota AS quota (provider, year_month, used)
                SELECT :provider, :year_month, :n
                WHERE :n <= :budget
                ON CONFLICT (provider, year_month) DO UPDATE
                SET used = quota.used + EXCLUDED.used
                WHERE quota.used + EXCLUDED.used <= :budget
                RETURNING used
                """
            ),
            {
                "provider": provider,
                "year_month": _year_month(),
                "n": n,
                "budget": budget,
            },
        ).scalar_one_or_none()
        if used is None:
            raise QuotaExceeded(f"{provider} monthly development budget exhausted")


def remaining(provider: str) -> int:
    budget = _budget(provider)
    with SessionLocal() as session:
        used = session.execute(
            text(
                "SELECT used FROM api_quota "
                "WHERE provider = :provider AND year_month = :year_month"
            ),
            {"provider": provider, "year_month": _year_month()},
        ).scalar_one_or_none()
    return max(0, budget - (used or 0))


def report() -> dict[str, int]:
    """Print this at every three-hour sync. Owner A reads it aloud."""
    return {provider: remaining(provider) for provider in PROVIDERS}
