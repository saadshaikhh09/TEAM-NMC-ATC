from datetime import datetime

from fastapi.testclient import TestClient

from main import app


PRIYA_TRIP_ID = "aaaaaaaa-1111-1111-1111-111111111111"
client = TestClient(app)


def test_list_trips_matches_contract():
    response = client.get("/trips")

    assert response.status_code == 200
    trips = response.json()
    assert len(trips) == 3

    priya = next(trip for trip in trips if trip["traveller_name"] == "Priya Sharma")
    assert set(priya) == {
        "id",
        "traveller_name",
        "status",
        "origin",
        "destination",
        "flights",
        "hotels",
        "constraints",
    }
    assert {flight["leg"] for flight in priya["flights"]} == {"outbound", "return"}
    assert priya["constraints"]["hard_arrival_reason"] == (
        "Client presentation in London, cannot be missed"
    )
    for flight in priya["flights"]:
        for field in ("scheduled_departure", "scheduled_arrival", "next_poll_at"):
            assert datetime.fromisoformat(flight[field]).utcoffset() is not None


def test_get_trip_returns_priya():
    response = client.get(f"/trips/{PRIYA_TRIP_ID}")

    assert response.status_code == 200
    assert response.json()["traveller_name"] == "Priya Sharma"


def test_timeline_returns_agent_actions():
    response = client.get(f"/trips/{PRIYA_TRIP_ID}/timeline")

    assert response.status_code == 200
    assert response.json() == []
