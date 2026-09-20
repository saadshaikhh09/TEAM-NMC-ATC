from fastapi.testclient import TestClient

from core.events import emit
from main import app
from tests.helpers import login_demo


def test_websocket_broadcasts_frozen_envelope():
    client = login_demo(TestClient(app))
    with client.websocket_connect("/ws") as websocket:
        emit(
            "disruption.detected",
            {"trip_id": "aaaaaaaa-1111-1111-1111-111111111111", "payload": {"disruption_id": "disruption-1"}},
        )
        assert websocket.receive_json() == {
            "type": "disruption.detected",
            "trip_id": "aaaaaaaa-1111-1111-1111-111111111111",
            "payload": {"disruption_id": "disruption-1"},
        }
