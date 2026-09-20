"""Approve / reject a plan. Owner: Person A."""
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from core.audit import record
from core.db import SessionLocal
from core.events import emit
from core.models import Approval, RecoveryPlan
from core.state_machine import advance


router = APIRouter()
_flight_provider = None
_hotel_provider = None


def configure(flight_provider, hotel_provider) -> None:
    global _flight_provider, _hotel_provider
    _flight_provider = flight_provider
    _hotel_provider = hotel_provider


def _execute(session, plan):
    if _flight_provider is None or _hotel_provider is None:
        raise RuntimeError("approval providers are not configured")
    from executor.run import run

    return run(session, plan, _flight_provider, _hotel_provider)


def _response(plan) -> dict:
    options = sorted(plan.options, key=lambda option: option.rank or 0)
    change = plan.hotel_changes[0] if plan.hotel_changes else None
    return {
        "id": str(plan.id),
        "disruption_id": str(plan.disruption_id),
        "state": plan.state,
        "evaluated_count": plan.evaluated_count,
        "options": [
            {
                "id": option.option_id,
                "carrier": option.carrier,
                "flight_number": option.flight_number,
                "departure": option.departure,
                "arrival": option.arrival,
                "stops": option.stops,
                "cabin": option.cabin,
                "fare_inr": option.fare_inr,
            }
            for option in options
        ],
        "rejections": [
            {
                "option_id": rejection.option_id,
                "rule": rejection.rule,
                "human_reason": rejection.human_reason,
                "note": rejection.note,
            }
            for rejection in plan.rejections
        ],
        "chosen_option_id": plan.chosen_option_id,
        "hotel_change": {
            "required": change.required,
            "new_check_in": change.new_check_in,
            "new_check_out": change.new_check_out,
            "cost_delta_inr": change.cost_delta_inr,
        } if change else None,
        "total_cost_delta_inr": plan.total_cost_delta_inr,
        "requires_approval": plan.requires_approval,
        "approval_reason": plan.approval_reason,
        "explanation": plan.explanation,
        "member_message": plan.member_message,
    }


def _get_plan(session, plan_id: UUID) -> RecoveryPlan:
    plan = session.get(RecoveryPlan, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Recovery plan not found")
    return plan


@router.get("/disruptions/{disruption_id}/plan")
def plan_for_disruption(disruption_id: UUID):
    """CONTRACT.md line 48. Same serialiser as approve/reject — one shape, one source."""
    with SessionLocal() as session:
        plan = session.scalars(
            select(RecoveryPlan)
            .where(RecoveryPlan.disruption_id == disruption_id)
            .order_by(RecoveryPlan.created_at.desc(), RecoveryPlan.id.desc())
        ).first()
        if plan is None:
            raise HTTPException(status_code=404, detail="No recovery plan for this disruption")
        return _response(plan)


@router.post("/approvals/{plan_id}/approve")
def approve(plan_id: UUID):
    with SessionLocal() as session:
        plan = _get_plan(session, plan_id)
        trip_id = plan.disruption.trip_id
        record(
            session,
            trip_id,
            "APPROVED",
            "Recovery plan approved",
            plan_id=plan.id,
        )
        session.add(Approval(
            plan_id=plan.id,
            decision="APPROVED",
            decided_at=datetime.now(timezone.utc),
        ))
        plan.state = "EXECUTING"
        session.commit()
        advance(session, trip_id, "EXECUTING")
        emit(
            "plan.executing",
            {"trip_id": str(trip_id), "payload": {"plan_id": str(plan.id)}},
        )
        _execute(session, plan)
        session.refresh(plan)
        return _response(plan)


@router.post("/approvals/{plan_id}/reject")
def reject(plan_id: UUID):
    with SessionLocal() as session:
        plan = _get_plan(session, plan_id)
        trip_id = plan.disruption.trip_id
        record(
            session,
            trip_id,
            "FAILED",
            "Recovery plan rejected by traveller",
            plan_id=plan.id,
        )
        session.add(Approval(
            plan_id=plan.id,
            decision="REJECTED",
            decided_at=datetime.now(timezone.utc),
        ))
        plan.state = "REJECTED"
        session.commit()
        advance(session, trip_id, "RECOVERY_FAILED")
        return _response(plan)
