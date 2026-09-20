"""The detection -> plan link. Owner: Person A.

test_simulate.py covers the ordinary path (a plan is built and halts at the
gate). This covers the one outcome that has no happy ending: every option
breaks a hard constraint, so there is nothing to approve.

The plan must still be persisted and published — the rejection list is the most
valuable thing on the screen, and it is the only thing left when the agent has
to refuse.
"""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from core.db import SessionLocal
from core.events import subscribe
from core.models import (
    AgentAction,
    Flight,
    RecoveryPlan,
    Traveller,
    TravellerConstraint,
    Trip,
)
from main import app


@pytest.fixture
def impossible_deadline():
    """Every mock BOM->LHR option arrives after this deadline."""
    traveller_id, trip_id, flight_id = uuid4(), uuid4(), uuid4()
    with SessionLocal.begin() as session:
        traveller = Traveller(id=traveller_id, name="Impossible Deadline")
        session.add(TravellerConstraint(
            traveller=traveller,
            hard_arrival_by=datetime(2026, 9, 20, 7, tzinfo=timezone.utc),
            hard_arrival_reason="cannot be missed",
            max_fare_inr=90_000,
            max_stops=1,
            cabin="economy",
            auto_approve_under_inr=45_000,
        ))
        trip = Trip(
            id=trip_id, traveller=traveller, status="MONITORING",
            origin="BOM", destination="LHR",
        )
        session.add(Flight(
            id=flight_id, trip=trip, leg="outbound", carrier="AI",
            flight_number="AI131", origin="BOM", destination="LHR",
            scheduled_departure=datetime(2026, 9, 19, 21, tzinfo=timezone.utc),
            scheduled_arrival=datetime(2026, 9, 20, 6, 15, tzinfo=timezone.utc),
            status="SCHEDULED", fare_inr=48_200, cabin="economy",
        ))
    try:
        yield trip_id, flight_id
    finally:
        with SessionLocal.begin() as session:
            session.execute(delete(Traveller).where(Traveller.id == traveller_id))


def test_refusal_is_persisted_published_and_ends_in_recovery_failed(impossible_deadline):
    trip_id, flight_id = impossible_deadline
    failures = []
    subscribe("plan.failed", failures.append)

    response = TestClient(app).post(f"/simulate/cancellation?flight_id={flight_id}")
    assert response.status_code == 200

    with SessionLocal() as session:
        plan = session.scalars(
            select(RecoveryPlan).join(RecoveryPlan.disruption).where(
                RecoveryPlan.disruption.has(trip_id=trip_id)
            )
        ).one()
        assert plan.state == "FAILED"
        assert plan.chosen_option_id is None
        assert plan.evaluated_count == 4
        # The refusal is the product. Every option rejected, each with a reason.
        assert len(plan.rejections) == 4
        assert {rejection.rule for rejection in plan.rejections} == {"hard_arrival_by"}
        assert all(rejection.human_reason for rejection in plan.rejections)
        assert plan.explanation and plan.member_message

        assert session.get(Trip, trip_id).status == "RECOVERY_FAILED"
        stages = session.scalars(
            select(AgentAction.stage)
            .where(AgentAction.trip_id == trip_id)
            .order_by(AgentAction.at, AgentAction.id)
        ).all()
        assert stages == ["DETECTED", "PLANNING", "EVALUATED", "FAILED"]

    assert [event["payload"]["plan_id"] for event in failures] == [str(plan.id)]


def test_a_raising_subscriber_cannot_break_the_request_that_fired_it(impossible_deadline):
    """Detection emits from inside the caller's request; subscribers are isolated."""
    _, flight_id = impossible_deadline

    def explode(_message):
        raise RuntimeError("subscriber blew up")

    subscribe("disruption.detected", explode)
    assert TestClient(app).post(f"/simulate/cancellation?flight_id={flight_id}").status_code == 200
