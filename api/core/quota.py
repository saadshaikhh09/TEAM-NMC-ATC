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


class QuotaExceeded(RuntimeError):
    pass


def spend(provider: str, n: int = 1) -> None:
    """Record n calls against provider's monthly budget, or raise.

    Counter persists in Postgres so a process restart does not reset it.
    Raise QuotaExceeded rather than returning False — a silent skip produces
    a stale status, which is worse than a loud failure.
    """
    raise NotImplementedError("A12")


def remaining(provider: str) -> int:
    raise NotImplementedError("A12")


def report() -> dict[str, int]:
    """Print this at every three-hour sync. Owner A reads it aloud."""
    raise NotImplementedError("A12")
