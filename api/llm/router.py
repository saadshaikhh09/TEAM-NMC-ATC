"""Ordered LLM fallback chain. Owner: Person A.

    LLM_CHAIN=gemini,openrouter,xkiro

Tries each in order. First success wins. If all fail, or the total budget is
blown, returns None and the caller uses llm/fallback.py.

Three properties that matter more than the chain itself:

  1. NEVER RAISES. complete() returns str or None. The LLM is a sidecar; a
     dead model must not stop a rebooking.
  2. HARD BUDGET. Per-provider timeout plus a total budget. A live call over
     ~6 seconds kills a demo, so past LLM_TOTAL_BUDGET_SECONDS we stop trying
     and return the templated string.
  3. CIRCUIT BREAKER. A provider that fails is skipped for
     LLM_BREAKER_COOLDOWN seconds. Without this, a rate-limited Gemini costs
     you its full timeout on every single call for the rest of the hackathon.

Nothing outside this module calls an LLM API. Not llm/explain.py, not
llm/extract.py, not a route. One door.
"""
import time
from typing import Callable

_registry: dict[str, Callable[[str, str, float], str]] = {}
_breaker: dict[str, float] = {}      # provider -> retry-after epoch


def register(name: str, fn: Callable[[str, str, float], str]) -> None:
    """fn(system, user, timeout) -> str, or raises."""
    _registry[name] = fn


def _available(name: str) -> bool:
    return time.time() >= _breaker.get(name, 0)


def complete(system: str, user: str, cache_key: str | None = None) -> str | None:
    """Returns model text, or None if every provider failed. Never raises."""
    raise NotImplementedError("A11")


def status() -> dict[str, str]:
    """Which providers are live vs broken. Read this aloud at every sync —
    if two of three are tripped, you are one failure from templated output."""
    raise NotImplementedError("A11")
