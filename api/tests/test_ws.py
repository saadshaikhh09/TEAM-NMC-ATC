from fastapi.testclient import TestClient

from core.events import emit
from main import app


def test_websocket_broadcasts_frozen_envelope():
    with TestClient(app).websocket_connect("/ws") as websocket:
        emit(
            "disruption.detected",
            {"trip_id": "trip-1", "payload": {"disruption_id": "disruption-1"}},
        )
        assert websocket.receive_json() == {
            "type": "disruption.detected",
            "trip_id": "trip-1",
            "payload": {"disruption_id": "disruption-1"},
        }
