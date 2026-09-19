"""Response cache keyed by plan content. Owner: Person A.

This is worth more than the fallback chain.

You will rehearse the demo roughly thirty times against the same seeded plan.
Without a cache that is thirty identical LLM calls — free-tier rate limits,
thirty chances to be slow on stage, and thirty different wordings so you can
never rehearse the same pitch twice.

With it: one call, then instant replay. The demo becomes deterministic, which
is the same reason providers/mock.py has no randomness.

Key on a hash of the inputs that actually change the answer — chosen option,
rejections, hotel delta — not on a timestamp.

Persist in Postgres, not memory. `make reset` should NOT clear it: you want the
cache to survive the thirty resets you are about to do.
"""

import hashlib
import json
from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from core.db import SessionLocal
from core.models import LlmCache


def _value(item, name, default=None):
    return item.get(name, default) if isinstance(item, dict) else getattr(item, name, default)


def _hotel_change(plan):
    change = _value(plan, "hotel_change")
    if change is None:
        changes = _value(plan, "hotel_changes", [])
        change = changes[0] if changes else None
    return change


def key_for(plan) -> str:
    rejections = sorted(
        (
            {
                "option_id": _value(item, "option_id"),
                "rule": _value(item, "rule"),
                "human_reason": _value(item, "human_reason"),
                "note": _value(item, "note"),
            }
            for item in _value(plan, "rejections", [])
        ),
        key=lambda item: json.dumps(item, sort_keys=True),
    )
    payload = {
        "chosen_option_id": _value(plan, "chosen_option_id"),
        "rejections": rejections,
        "hotel_delta_inr": _value(_hotel_change(plan), "cost_delta_inr"),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def get(key: str) -> str | None:
    with SessionLocal() as session:
        return session.execute(
            select(LlmCache.response).where(LlmCache.cache_key == key)
        ).scalar_one_or_none()


def put(key: str, value: str) -> None:
    statement = insert(LlmCache).values(cache_key=key, response=value)
    with SessionLocal.begin() as session:
        session.execute(
            statement.on_conflict_do_update(
                index_elements=[LlmCache.cache_key], set_={"response": value}
            )
        )


def get_or_call(plan, provider: Callable[[], str | None]) -> str | None:
    key = key_for(plan)
    cached = get(key)
    if cached is not None:
        return cached
    # Concurrent misses may duplicate one call; add a DB lock if that ever matters.
    value = provider()
    if value is not None:
        put(key, value)
    return value
