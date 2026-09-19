import json
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from llm import cache, client, explain, extract, router
from main import app


def _plan():
    return SimpleNamespace(
        chosen_option_id="a15-opt",
        options=[SimpleNamespace(id="a15-opt", carrier="BA", flight_number="BA138")],
        rejections=[],
        hotel_change=SimpleNamespace(required=False, cost_delta_inr=0),
        total_cost_delta_inr=4_200,
        approval_reason="fare exceeds the auto-approve threshold",
    )


def _clear_plan_cache(plan):
    from sqlalchemy import delete
    from core.db import SessionLocal
    from core.models import LlmCache

    keys = [f"{purpose}:{cache.key_for(plan)}" for purpose in ("explain", "draft")]
    with SessionLocal.begin() as session:
        session.execute(delete(LlmCache).where(LlmCache.cache_key.in_(keys)))


def test_explain_and_draft_fall_back_with_every_key_blank(monkeypatch):
    plan = _plan()
    _clear_plan_cache(plan)
    for name in ("GEMINI_API_KEY", "OPENROUTER_API_KEY", "XKIRO_API_KEY"):
        monkeypatch.setenv(name, "")
    client._configured = False

    try:
        assert "BA138" in explain.explain(plan)
        assert "BA138" in explain.draft(plan)
    finally:
        _clear_plan_cache(plan)


def test_explain_and_draft_each_cache_the_model_response(monkeypatch):
    plan = _plan()
    _clear_plan_cache(plan)
    calls = []
    client._configured = True
    monkeypatch.setattr(
        router,
        "complete",
        lambda system, user, cache_key=None: calls.append(system) or "model copy",
    )

    try:
        assert explain.explain(plan) == "model copy"
        assert explain.explain(plan) == "model copy"
        assert explain.draft(plan) == "model copy"
        assert explain.draft(plan) == "model copy"
        assert len(calls) == 2
    finally:
        _clear_plan_cache(plan)


def test_extract_returns_only_a_complete_contract_trip(monkeypatch):
    response = {
        "id": "44444444-4444-4444-4444-444444444444",
        "traveller_name": "Priya Sharma",
        "status": "CREATED",
        "origin": "BOM",
        "destination": "LHR",
        "flights": [
            {
                "id": "55555555-5555-5555-5555-555555555555",
                "leg": "outbound",
                "carrier": "AI",
                "flight_number": "AI131",
                "origin": "BOM",
                "destination": "LHR",
                "scheduled_departure": "2026-09-19T21:00:00+00:00",
                "scheduled_arrival": "2026-09-20T06:15:00+00:00",
                "status": "SCHEDULED",
                "next_poll_at": None,
            }
        ],
        "hotels": [],
        "constraints": {
            "hard_arrival_by": None,
            "hard_arrival_reason": None,
            "max_fare_inr": None,
            "max_stops": 1,
            "cabin": "economy",
            "avoid_carriers": [],
            "auto_approve_under_inr": None,
            "hard_arrival_by_local": None,
        },
    }
    monkeypatch.setattr(client, "ask", lambda system, user: json.dumps(response))

    trip = extract.extract("Booking for AI131 from BOM to LHR")

    assert trip.model_dump(mode="json")["traveller_name"] == "Priya Sharma"
    assert len(trip.flights) == 1


def test_extract_failure_is_clear_and_never_returns_a_partial_trip(monkeypatch):
    monkeypatch.setattr(client, "ask", lambda system, user: None)

    with pytest.raises(extract.ExtractionError, match="unavailable"):
        extract.extract("booking text")

    response = TestClient(app).post(
        "/trips/extract", json={"pasted_booking_text": "booking text"}
    )
    assert response.status_code == 503
    assert "unavailable" in response.json()["detail"]
