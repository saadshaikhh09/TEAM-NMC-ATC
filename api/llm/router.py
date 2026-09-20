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
import os
import queue
import threading
import time
from typing import Callable

from dotenv import load_dotenv

_registry: dict[str, Callable[[str, str, float], str]] = {}
_breaker: dict[str, float] = {}      # provider -> retry-after monotonic time


def register(name: str, fn: Callable[[str, str, float], str]) -> None:
    """fn(system, user, timeout) -> str, or raises."""
    _registry[name] = fn


def _available(name: str) -> bool:
    return time.monotonic() >= _breaker.get(name, 0)


def _seconds(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


def configure() -> None:
    """Register only fully configured providers from the environment."""
    from llm.providers import gemini, openai_compatible

    if os.getenv("TESTING", "").lower() != "true":
        load_dotenv()
    _registry.clear()

    # groq is OpenAI-compatible, so it needs no adapter of its own. Registered
    # only when BOTH key and model are set: Groq retires model ids, and a
    # guessed one fails as a 404 on every call for the rest of the session.
    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    groq_model = os.getenv("GROQ_MODEL", "").strip()
    if groq_key and groq_model:
        register(
            "groq",
            openai_compatible.make(
                os.getenv("GROQ_BASE", "https://api.groq.com/openai/v1"),
                groq_key,
                groq_model,
            ),
        )

    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    if gemini_key:
        register(
            "gemini",
            gemini.make(gemini_key, os.getenv("GEMINI_MODEL", "gemini-2.0-flash")),
        )

    openrouter_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if openrouter_key:
        register(
            "openrouter",
            openai_compatible.make(
                os.getenv("OPENROUTER_BASE", "https://openrouter.ai/api/v1"),
                openrouter_key,
                os.getenv("OPENROUTER_MODEL", ""),
            ),
        )

    xkiro_key = os.getenv("XKIRO_API_KEY", "").strip()
    xkiro_base = os.getenv("XKIRO_BASE", "").strip()
    xkiro_model = os.getenv("XKIRO_MODEL", "").strip()
    if xkiro_key and xkiro_base and xkiro_model:
        register(
            "xkiro",
            openai_compatible.make(xkiro_base, xkiro_key, xkiro_model),
        )


def _call(
    fn: Callable[[str, str, float], str],
    system: str,
    user: str,
    timeout: float,
) -> str | None:
    result: queue.Queue[tuple[bool, str | None]] = queue.Queue(maxsize=1)

    def run() -> None:
        try:
            value = fn(system, user, timeout)
            result.put((True, value.strip() if isinstance(value, str) else None))
        except Exception:
            result.put((False, None))

    threading.Thread(target=run, daemon=True).start()
    try:
        ok, value = result.get(timeout=timeout)
        return value if ok and value else None
    except queue.Empty:
        return None


def complete(system: str, user: str, cache_key: str | None = None) -> str | None:
    """Returns model text, or None if every provider failed. Never raises."""
    try:
        timeout = max(0.0, _seconds("LLM_TIMEOUT_SECONDS", 4))
        deadline = time.monotonic() + max(
            0.0, _seconds("LLM_TOTAL_BUDGET_SECONDS", 8)
        )
        cooldown = max(0.0, _seconds("LLM_BREAKER_COOLDOWN", 60))
        chain = os.getenv("LLM_CHAIN", "gemini,openrouter,xkiro").split(",")

        for name in (item.strip() for item in chain):
            fn = _registry.get(name)
            if fn is None or not _available(name):
                continue
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return None
            value = _call(fn, system, user, min(timeout, remaining))
            if value is not None:
                return value
            _breaker[name] = time.monotonic() + cooldown
        return None
    except Exception:
        return None


def status() -> dict[str, str]:
    """Which providers are live vs broken. Read this aloud at every sync —
    if two of three are tripped, you are one failure from templated output."""
    return {
        name: "ready" if _available(name) else "cooldown"
        for name in _registry
    }
