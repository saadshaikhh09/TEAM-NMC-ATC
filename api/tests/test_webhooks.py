from unittest.mock import MagicMock, patch
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient

from main import app
from providers.duffel import parse_webhook_event


@pytest.fixture
def client():
    return TestClient(app)


def test_parse_webhook_event_cancellation():
    payload = {
        "data": {
            "id": "evt_test_123",
            "type": "order.airline_initiated_change_detected",
            "object": {
                "id": "ord_123",
                "booking_reference": "AI131",
                "slices": [
                    {
                        "segments": [
                            {
                                "operating_carrier": {"iata_code": "AI"},
                                "operating_carrier_flight_number": "AI131",
                            }
                        ]
                    }
                ],
            },
        }
    }
    parsed = parse_webhook_event(payload)
    assert parsed["event_id"] == "evt_test_123"
    assert parsed["flight_number"] == "AI131"
    assert parsed["kind"] == "CANCELLATION"


def test_parse_webhook_event_delay():
    payload = {
        "data": {
            "id": "evt_delay_456",
            "type": "order.schedule_change",
            "object": {
                "slices": [
                    {
                        "segments": [
                            {
                                "marketing_carrier": {"iata_code": "BA"},
                                "flight_number": "138",
                            }
                        ]
                    }
                ]
            },
        }
    }
    parsed = parse_webhook_event(payload)
    assert parsed["event_id"] == "evt_delay_456"
    assert parsed["flight_number"] == "BA138"
    assert parsed["kind"] == "DELAY"


def test_duffel_webhook_receiver_deduplication(client):
    payload = {
        "data": {
            "id": "evt_dedup_unique_1",
            "type": "order.airline_initiated_change_detected",
            "object": {"booking_reference": "AI131"},
        }
    }

    mock_disruption = MagicMock()
    mock_disruption.id = uuid4()

    mock_flight = MagicMock()
    mock_flight.id = uuid4()

    with patch("routes.webhooks.SessionLocal") as mock_session_ctx, patch(
        "routes.webhooks.detect", return_value=mock_disruption
    ) as mock_detect:
        session = MagicMock()
        session.scalar.return_value = mock_flight
        mock_session_ctx.return_value.__enter__.return_value = session

        # First delivery
        res1 = client.post("/webhooks/duffel", json=payload)
        assert res1.status_code == 200
        assert res1.json()["status"] == "disruption_detected"
        assert mock_detect.call_count == 1

        # Duplicate delivery
        res2 = client.post("/webhooks/duffel", json=payload)
        assert res2.status_code == 200
        assert res2.json()["status"] == "duplicate_skipped"
        # Should not call detect again
        assert mock_detect.call_count == 1
