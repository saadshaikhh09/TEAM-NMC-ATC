from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from core.db import SessionLocal
from core.events import subscribe
from core.models import AgentAction, Disruption, Flight, RecoveryPlan, Traveller, Trip
from main import app
from tests.helpers import DEMO_USER_ID, login_demo


@pytest.fixture
def flight_ids():
    traveller_id, trip_id, flight_id = uuid4(), uuid4(), uuid4()
    with SessionLocal.begin() as session:
        traveller = Traveller(id=traveller_id, user_id=DEMO_USER_ID, name="Simulation Test")
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
    client = login_demo(TestClient(app))

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
        assert session.get(Flight, flight_id).status == "CANCELLED"
        assert len(session.scalars(select(Disruption).where(Disruption.trip_id == trip_id)).all()) == 1

        # Detection is no longer the end of the line: main.py subscribes the
        # orchestrator, so one simulated cancellation produces a persisted plan
        # and carries the trip to the gate's verdict.
        assert session.get(Trip, trip_id).status == "AWAITING_APPROVAL"
        plan = session.scalars(
            select(RecoveryPlan).where(RecoveryPlan.disruption_id == UUID(body["id"]))
        ).one()
        assert plan.state == "AWAITING_APPROVAL"
        assert plan.requires_approval is True
        assert plan.chosen_option_id
        assert plan.evaluated_count > 0

        actions = session.scalars(
            select(AgentAction)
            .where(AgentAction.trip_id == trip_id)
            .order_by(AgentAction.at, AgentAction.id)
        ).all()
        assert [action.stage for action in actions] == [
            "DETECTED", "PLANNING", "EVALUATED", "AWAITING_APPROVAL",
        ]


def test_delay_uses_same_detection_path(flight_ids):
    trip_id, flight_id = flight_ids
    response = login_demo(TestClient(app)).post(f"/simulate/delay?flight_id={flight_id}")
    assert response.status_code == 200
    assert response.json()["kind"] == "DELAY"
    assert response.json()["new_status"] == "DELAYED"
    with SessionLocal() as session:
        # Same path as a cancellation: detect, plan, halt at the gate.
        assert session.get(Trip, trip_id).status == "AWAITING_APPROVAL"
