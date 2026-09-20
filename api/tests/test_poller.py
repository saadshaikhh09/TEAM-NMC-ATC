from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy import delete, select

from core.db import SessionLocal
from core.models import Disruption, Flight, Traveller, Trip
from monitor.poller import poll_due
from providers.base import FlightStatus


NOW = datetime(2026, 9, 19, 20, tzinfo=timezone.utc)
DEPARTURE = datetime(2026, 9, 19, 21, tzinfo=timezone.utc)
ARRIVAL = datetime(2026, 9, 20, 6, 15, tzinfo=timezone.utc)


@pytest.fixture
def due_flight():
    traveller_id, trip_id, flight_id = uuid4(), uuid4(), uuid4()
    with SessionLocal.begin() as session:
        traveller = Traveller(id=traveller_id, name="Poller Test")
        trip = Trip(
            id=trip_id, traveller=traveller, status="MONITORING",
            origin="BOM", destination="LHR",
        )
        session.add(Flight(
            id=flight_id, trip=trip, leg="outbound", carrier="AI",
            flight_number="AI131", origin="BOM", destination="LHR",
            scheduled_departure=DEPARTURE, scheduled_arrival=ARRIVAL,
            status="SCHEDULED", next_poll_at=NOW - timedelta(seconds=1),
        ))
    try:
        yield trip_id, flight_id
    finally:
        with SessionLocal.begin() as session:
            session.execute(delete(Traveller).where(Traveller.id == traveller_id))


class FakeStatusProvider:
    def __init__(self, status: str):
        self.status = status
        self.calls = []

    def get_status(self, carrier, flight_number, on):
        self.calls.append((carrier, flight_number, on))
        return FlightStatus(
            flight_number, self.status, DEPARTURE, None, ARRIVAL, None,
        )


def test_poll_due_persists_demo_resume_point(due_flight):
    _, flight_id = due_flight
    provider = FakeStatusProvider("SCHEDULED")
    with SessionLocal() as session:
        poll_due(
            session, provider, "simulated", now=NOW, demo_mode=True,
            demo_poll_seconds=15, flight_id=flight_id,
        )
    with SessionLocal() as session:
        flight = session.get(Flight, flight_id)
        assert flight.last_polled_at == NOW
        assert flight.next_poll_at == NOW + timedelta(seconds=15)
    assert ("AI", "AI131", datetime(2026, 9, 20, tzinfo=timezone.utc).date()) in provider.calls


def test_poll_due_routes_cancellation_through_detection(due_flight):
    trip_id, flight_id = due_flight
    provider = FakeStatusProvider("CANCELLED")
    with SessionLocal() as session:
        poll_due(session, provider, "simulated", now=NOW, demo_mode=True, flight_id=flight_id)
    with SessionLocal() as session:
        # Deliberately not asserting trip.status: once main.py is imported the
        # orchestrator is subscribed to disruption.detected and moves the trip on
        # past DISRUPTED, which would make this test depend on import order.
        # Detection's own transition is covered in test_state.py.
        assert session.get(Trip, trip_id).status != "MONITORING"
        assert session.get(Flight, flight_id).next_poll_at is None
        disruptions = session.scalars(select(Disruption).where(Disruption.flight_id == flight_id)).all()
        assert len(disruptions) == 1
        assert disruptions[0].source == "simulated"
