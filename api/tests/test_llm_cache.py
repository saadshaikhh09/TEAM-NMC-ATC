from types import SimpleNamespace

from sqlalchemy import delete

from core.db import SessionLocal
from core.models import LlmCache
from llm import cache


def _plan(plan_id):
    return SimpleNamespace(
        id=plan_id,
        created_at="ignored timestamp",
        chosen_option_id="opt_1",
        rejections=[
            SimpleNamespace(
                option_id="opt_4",
                rule="hard_arrival_by",
                human_reason="misses hard deadline",
                note="would have been cheaper",
            )
        ],
        hotel_change=SimpleNamespace(
            required=True,
            new_check_in="2026-09-21",
            cost_delta_inr=-9_800,
        ),
    )


def test_key_uses_plan_content_not_identity():
    assert cache.key_for(_plan("plan-a")) == cache.key_for(_plan("plan-b"))


def test_second_identical_call_makes_no_provider_request():
    plan = _plan("plan-a")
    key = cache.key_for(plan)
    with SessionLocal.begin() as session:
        session.execute(delete(LlmCache).where(LlmCache.cache_key == key))

    provider_calls = 0

    def provider():
        nonlocal provider_calls
        provider_calls += 1
        return "stable response"

    try:
        assert cache.get_or_call(plan, provider) == "stable response"
        assert cache.get_or_call(_plan("plan-b"), provider) == "stable response"
        assert provider_calls == 1
    finally:
        with SessionLocal.begin() as session:
            session.execute(delete(LlmCache).where(LlmCache.cache_key == key))
