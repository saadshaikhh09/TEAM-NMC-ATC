from datetime import date, datetime, timezone

import httpx
import pytest

from core.quota import QuotaExceeded
from providers.aviationstack import AviationStackProvider


FLIGHT = {
    "flight_date": "2026-09-20",
    "flight_status": "scheduled",
    "flight": {"iata": "AI131"},
    "departure": {
        "scheduled": "2026-09-19T21:00:00+00:00",
        "estimated": "2026-09-19T22:00:00+00:00",
        "delay": 60,
        "gate": "G4",
        "terminal": "2",
    },
    "arrival": {
        "scheduled": "2026-09-20T06:15:00+00:00",
        "estimated": "2026-09-20T07:15:00+00:00",
    },
}


def test_cross_check_filters_date_and_spends_before_http(monkeypatch):
    events = []
    monkeypatch.setattr("providers.aviationstack.quota.spend", lambda name: events.append(name))

    def respond(request):
        events.append("http")
        assert request.url.scheme == "https"
        assert request.url.path == "/v1/flights"
        assert request.url.params["flight_iata"] == "AI131"
        assert request.url.params["access_key"] == "test-key"
        return httpx.Response(200, json={"data": [
            {**FLIGHT, "flight_date": "2026-09-19", "flight_status": "landed"},
            FLIGHT,
        ]})

    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        status = AviationStackProvider(
            api_key="test-key", base_url="http://api.aviationstack.com/v1", client=client,
        ).get_status("AI", "AI131", date(2026, 9, 20))
    assert events == ["aviationstack", "http"]
    assert status.status == "DELAYED"
    assert status.estimated_arrival == datetime(2026, 9, 20, 7, 15, tzinfo=timezone.utc)


def test_empty_result_is_error(monkeypatch):
    monkeypatch.setattr("providers.aviationstack.quota.spend", lambda _: None)
    with httpx.Client(transport=httpx.MockTransport(
        lambda _: httpx.Response(200, json={"data": []})
    )) as client:
        with pytest.raises(LookupError, match="expected one"):
            AviationStackProvider(api_key="test-key", client=client).get_status(
                "AI", "AI131", date(2026, 9, 20)
            )


def test_quota_refusal_prevents_http(monkeypatch):
    def deny(_):
        raise QuotaExceeded("demo mode")

    monkeypatch.setattr("providers.aviationstack.quota.spend", deny)
    with httpx.Client(transport=httpx.MockTransport(lambda _: pytest.fail("HTTP was called"))) as client:
        with pytest.raises(QuotaExceeded):
            AviationStackProvider(api_key="test-key", client=client).get_status(
                "AI", "AI131", date(2026, 9, 20)
            )


def test_connection_error_does_not_expose_key(monkeypatch):
    monkeypatch.setattr("providers.aviationstack.quota.spend", lambda _: None)

    def fail(request):
        raise httpx.ConnectError("failure", request=request)

    with httpx.Client(transport=httpx.MockTransport(fail)) as client:
        with pytest.raises(RuntimeError) as error:
            AviationStackProvider(api_key="secret-key", client=client).get_status(
                "AI", "AI131", date(2026, 9, 20)
            )
    assert "secret-key" not in str(error.value)
