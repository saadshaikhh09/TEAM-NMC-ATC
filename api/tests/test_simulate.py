from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from core.db import SessionLocal
from core.events import subscribe
from core.models import AgentAction, Disruption, Flight, Traveller, Trip
from main import app


@pytest.fixture
def flight_ids():
    traveller_id, trip_id, flight_id = uuid4(), uuid4(), uuid4()
    with SessionLocal.begin() as session:
        traveller = Traveller(id=traveller_id, name="Simulation Test")
        trip = Trip(
            id=trip_id, traveller=traveller, status="MONITORING",
            origin="BOM", destination="LHR",
        )
        session.add(Flight(
            id=flight_id, trip=trip, leg="outbound", carrier="AI",
            flight_number="AI131", origin="BOM", destination="LHR",
            scheduled_departure=datetime(2026, 9, 19, 21, tzinfo=timezone.utc),
            scheduled_arrival=datetime(2026, 9, 20, 6, 15, tzinfo=timezone.utc),
            status="SCHEDULED",
        ))
    try:
        yield trip_id, flight_id
    finally:
        with SessionLocal.begin() as session:
            session.execute(delete(Traveller).where(Traveller.id == traveller_id))


def test_cancellation_writes_one_disruption_and_broadcasts(flight_ids):
    trip_id, flight_id = flight_ids
    events = []
    subscribe("disruption.detected", events.append)
    client = TestClient(app)

    response = client.post(f"/simulate/cancellation?flight_id={flight_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["trip_id"] == str(trip_id)
    assert body["flight_id"] == str(flight_id)
    assert body["kind"] == "CANCELLATION"
    assert body["source"] == "simulated"
    assert body["previous_status"] == "SCHEDULED"
    assert body["new_status"] == "CANCELLED"
    assert body["detected_at"].endswith("+00:00")

    again = client.post(f"/simulate/cancellation?flight_id={flight_id}")
    assert again.status_code == 200
    assert again.json()["id"] == body["id"]
    assert events == [{"trip_id": str(trip_id), "payload": {"disruption_id": body["id"]}}]

    with SessionLocal() as session:
        assert session.get(Trip, trip_id).status == "DISRUPTED"
        assert session.get(Flight, flight_id).status == "CANCELLED"
        assert len(session.scalars(select(Disruption).where(Disruption.trip_id == trip_id)).all()) == 1
        actions = session.scalars(select(AgentAction).where(AgentAction.trip_id == trip_id)).all()
        assert [action.stage for action in actions] == ["DETECTED"]


def test_delay_uses_same_detection_path(flight_ids):
    trip_id, flight_id = flight_ids
    response = TestClient(app).post(f"/simulate/delay?flight_id={flight_id}")
    assert response.status_code == 200
    assert response.json()["kind"] == "DELAY"
    assert response.json()["new_status"] == "DELAYED"
    with SessionLocal() as session:
        assert session.get(Trip, trip_id).status == "DISRUPTED"
