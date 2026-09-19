import time

import pytest

from llm import router


@pytest.fixture(autouse=True)
def empty_router(monkeypatch):
    router._registry.clear()
    router._breaker.clear()
    monkeypatch.setenv("LLM_CHAIN", "gemini,openrouter,xkiro")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "4")
    monkeypatch.setenv("LLM_TOTAL_BUDGET_SECONDS", "8")
    monkeypatch.setenv("LLM_BREAKER_COOLDOWN", "60")


def test_all_blank_keys_register_nothing_and_return_none(monkeypatch):
    for name in ("GEMINI_API_KEY", "OPENROUTER_API_KEY", "XKIRO_API_KEY"):
        monkeypatch.setenv(name, "")

    router.configure()

    assert router.status() == {}
    assert router.complete("system", "user") is None


def test_chain_uses_four_second_provider_timeout():
    seen = []
    router.register("gemini", lambda system, user, timeout: seen.append(timeout) or "ok")

    assert router.complete("system", "user") == "ok"
    assert seen == [4.0]


def test_failure_is_swallowed_and_provider_is_skipped_for_sixty_seconds(monkeypatch):
    now = [1_000.0]
    monkeypatch.setattr(router.time, "monotonic", lambda: now[0])
    calls = {"gemini": 0, "openrouter": 0}

    def failed(system, user, timeout):
        calls["gemini"] += 1
        raise RuntimeError("provider down")

    def working(system, user, timeout):
        calls["openrouter"] += 1
        return "fallback provider"

    router.register("gemini", failed)
    router.register("openrouter", working)

    assert router.complete("system", "user") == "fallback provider"
    assert router.complete("system", "user") == "fallback provider"
    assert calls == {"gemini": 1, "openrouter": 2}

    now[0] += 61
    assert router.complete("system", "user") == "fallback provider"
    assert calls == {"gemini": 2, "openrouter": 3}


def test_total_budget_stops_before_next_provider(monkeypatch):
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "0.02")
    monkeypatch.setenv("LLM_TOTAL_BUDGET_SECONDS", "0.02")
    later_calls = 0

    def slow(system, user, timeout):
        time.sleep(0.1)
        return "too late"

    def later(system, user, timeout):
        nonlocal later_calls
        later_calls += 1
        return "must not run"

    router.register("gemini", slow)
    router.register("openrouter", later)

    started = time.monotonic()
    assert router.complete("system", "user") is None
    assert time.monotonic() - started < 0.08
    assert later_calls == 0
