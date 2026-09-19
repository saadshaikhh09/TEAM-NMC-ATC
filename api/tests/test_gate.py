from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from core.db import SessionLocal
from core.models import AgentAction, Approval, Disruption, Flight, RecoveryPlan, Trip
from executor.gate import decide
from main import app
from routes import approvals


POLICY = {
    "rebooking": {"auto_approve_under_inr": 45_000},
    "hotel": {"auto_modify_under_inr": 15_000},
}
PRIYA_TRIP_ID = UUID("aaaaaaaa-1111-1111-1111-111111111111")


def plan(*, fare=40_000, rejections=None, hotel_required=False,
         hotel_cost=0, hotel_modifiable=True):
    return SimpleNamespace(
        chosen_option=SimpleNamespace(id="opt_1", fare_inr=fare),
        rejections=[] if rejections is None else rejections,
        hotel_change={
            "required": hotel_required,
            "new_check_in": None,
            "new_check_out": None,
            "cost_delta_inr": hotel_cost,
        },
        hotel=SimpleNamespace(modifiable=hotel_modifiable),
    )


def constraints(threshold=45_000):
    return SimpleNamespace(auto_approve_under_inr=threshold)


def test_in_policy_cheap_rebook_is_automatic():
    assert decide(plan(), constraints(), POLICY) == ("AUTO", None)


def test_traveller_threshold_is_stricter_than_policy_threshold():
    assert decide(plan(fare=40_000), constraints(35_000), POLICY) == (
        "APPROVAL",
        "Fare 40,000 exceeds auto-approve threshold 35,000",
    )


def test_rejection_on_chosen_option_forces_approval():
    rejection = {
        "option_id": "opt_1",
        "human_reason": "Arrives 11:40, misses hard deadline 09:00",
    }
    assert decide(plan(rejections=[rejection]), constraints(), POLICY) == (
        "APPROVAL",
        rejection["human_reason"],
    )


def test_non_modifiable_hotel_forces_approval():
    assert decide(
        plan(hotel_required=True, hotel_modifiable=False),
        constraints(),
        POLICY,
    ) == (
        "APPROVAL",
        "Hotel is not modifiable — cancel and rebook needs approval",
    )


def test_hotel_cost_over_auto_modify_threshold_forces_approval():
    assert decide(
        plan(hotel_required=True, hotel_cost=20_000),
        constraints(),
        POLICY,
    ) == (
        "APPROVAL",
        "Hotel change 20,000 exceeds auto-modify threshold 15,000",
    )


def test_missing_traveller_threshold_requires_approval():
    assert decide(plan(), constraints(None), POLICY) == (
        "APPROVAL",
        "Traveller auto-approve threshold is not set",
    )


@pytest.fixture
def pending_plan():
    with SessionLocal.begin() as session:
        trip = session.get(Trip, PRIYA_TRIP_ID)
        flight = session.scalar(
            select(Flight).where(Flight.trip_id == PRIYA_TRIP_ID, Flight.leg == "outbound")
        )
        trip.status = "AWAITING_APPROVAL"
        disruption = Disruption(
            trip_id=trip.id,
            flight_id=flight.id,
            kind="CANCELLATION",
            source="simulated",
            previous_status="SCHEDULED",
            new_status="CANCELLED",
            detected_at=datetime.now(timezone.utc),
        )
        plan_row = RecoveryPlan(disruption=disruption, state="AWAITING_APPROVAL")
        session.add(plan_row)
        session.flush()
        plan_id = plan_row.id

    try:
        yield plan_id
    finally:
        with SessionLocal.begin() as session:
            session.execute(delete(AgentAction).where(AgentAction.plan_id == plan_id))
            session.execute(delete(Approval).where(Approval.plan_id == plan_id))
            session.execute(delete(RecoveryPlan).where(RecoveryPlan.id == plan_id))
            session.execute(
                delete(Disruption).where(Disruption.trip_id == PRIYA_TRIP_ID)
            )
            session.get(Trip, PRIYA_TRIP_ID).status = "MONITORING"


def test_approve_records_decision_and_executes_plan(pending_plan, monkeypatch):
    executed = []

    def execute(session, plan_row):
        executed.append(plan_row.id)
        return {"id": str(plan_row.id), "state": "EXECUTING"}

    monkeypatch.setattr(approvals, "_execute", execute)
    response = TestClient(app).post(f"/approvals/{pending_plan}/approve")

    assert response.status_code == 200
    assert executed == [pending_plan]
    with SessionLocal() as session:
        assert session.get(Trip, PRIYA_TRIP_ID).status == "EXECUTING"
        assert session.scalar(
            select(Approval.decision).where(Approval.plan_id == pending_plan)
        ) == "APPROVED"
        assert session.scalar(
            select(AgentAction.stage).where(AgentAction.plan_id == pending_plan)
        ) == "APPROVED"


def test_reject_records_decision_and_fails_recovery(pending_plan):
    response = TestClient(app).post(f"/approvals/{pending_plan}/reject")

    assert response.status_code == 200
    assert response.json()["state"] == "REJECTED"
    with SessionLocal() as session:
        assert session.get(Trip, PRIYA_TRIP_ID).status == "RECOVERY_FAILED"
        assert session.scalar(
            select(Approval.decision).where(Approval.plan_id == pending_plan)
        ) == "REJECTED"
        assert session.scalar(
            select(AgentAction.stage).where(AgentAction.plan_id == pending_plan)
        ) == "FAILED"
