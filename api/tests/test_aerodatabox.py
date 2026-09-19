from datetime import date, datetime, timezone

import httpx
import pytest

from core.quota import QuotaExceeded
from providers.aerodatabox import AeroDataBoxProvider


FLIGHT = {
    "number": "AI 131",
    "status": "CanceledUncertain",
    "departure": {
        "scheduledTime": {"utc": "2026-09-19T21:00:00Z"},
        "revisedTime": {"utc": "2026-09-19T22:00:00Z"},
        "gate": "G4",
        "terminal": "2",
    },
    "arrival": {"scheduledTime": {"utc": "2026-09-20T06:15:00Z"}},
}


def test_status_uses_current_endpoint_and_quota_first(monkeypatch):
    events = []
    monkeypatch.setattr("providers.aerodatabox.quota.spend", lambda name: events.append(name))

    def respond(request):
        events.append("http")
        assert request.url.path == "/flights/Number/AI131/2026-09-20"
        assert request.url.params["dateLocalRole"] == "Departure"
        assert request.headers["X-RapidAPI-Key"] == "test-key"
        return httpx.Response(200, json=[FLIGHT])

    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        status = AeroDataBoxProvider(api_key="test-key", client=client).get_status(
            "AI", "AI131", date(2026, 9, 20)
        )
    assert events == ["aerodatabox", "http"]
    assert status.status == "CANCELLED"
    assert status.scheduled_departure == datetime(2026, 9, 19, 21, tzinfo=timezone.utc)
    assert status.estimated_departure == datetime(2026, 9, 19, 22, tzinfo=timezone.utc)
    assert status.gate == "G4"


def test_quota_refusal_prevents_http(monkeypatch):
    def deny(_):
        raise QuotaExceeded("demo mode")

    monkeypatch.setattr("providers.aerodatabox.quota.spend", deny)
    with httpx.Client(transport=httpx.MockTransport(lambda _: pytest.fail("HTTP was called"))) as client:
        with pytest.raises(QuotaExceeded):
            AeroDataBoxProvider(api_key="test-key", client=client).get_status(
                "AI", "AI131", date(2026, 9, 20)
            )


def test_unmapped_status_raises(monkeypatch):
    monkeypatch.setattr("providers.aerodatabox.quota.spend", lambda _: None)
    with httpx.Client(transport=httpx.MockTransport(
        lambda _: httpx.Response(200, json=[{**FLIGHT, "status": "Unexpected"}])
    )) as client:
        with pytest.raises(ValueError, match="unmapped"):
            AeroDataBoxProvider(api_key="test-key", client=client).get_status(
                "AI", "AI131", date(2026, 9, 20)
            )
