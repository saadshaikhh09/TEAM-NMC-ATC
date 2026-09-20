"""Approve / reject a plan. Owner: Person A."""
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from core.audit import record
from core.db import SessionLocal
from core.events import emit
from core.auth import current_user
from core.models import Approval, RecoveryPlan, User
from core.ownership import plans_for
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


def _get_plan(session, plan_id: UUID, user_id, *, lock: bool = False) -> RecoveryPlan:
    query = plans_for(user_id).where(RecoveryPlan.id == plan_id)
    if lock:
        query = query.with_for_update()
    plan = session.scalar(query)
    if plan is None:
        raise HTTPException(status_code=404, detail="Recovery plan not found")
    return plan


@router.get("/disruptions/{disruption_id}/plan")
def plan_for_disruption(disruption_id: UUID, user: User = Depends(current_user)):
    """CONTRACT.md line 48. Same serialiser as approve/reject — one shape, one source."""
    with SessionLocal() as session:
        plan = session.scalars(
            plans_for(user.id)
            .where(RecoveryPlan.disruption_id == disruption_id)
            .order_by(RecoveryPlan.created_at.desc(), RecoveryPlan.id.desc())
        ).first()
        if plan is None:
            raise HTTPException(status_code=404, detail="No recovery plan for this disruption")
        return _response(plan)


def _decide(plan_id: UUID, decision: str, user_id):
    with SessionLocal.begin() as session:
        plan = _get_plan(session, plan_id, user_id, lock=True)
        trip_id = plan.disruption.trip_id
        existing = session.scalar(select(Approval).where(Approval.plan_id == plan.id))
        if existing:
            if existing.decision != decision:
                raise HTTPException(status_code=409, detail=f"Plan already {existing.decision.lower()}")
            result = _response(plan)
            return result, False
        if plan.state != "AWAITING_APPROVAL" or plan.disruption.trip.status != "AWAITING_APPROVAL":
            raise HTTPException(status_code=409, detail="Plan is not awaiting approval")
        target_plan_state = "EXECUTING" if decision == "APPROVED" else "REJECTED"
        target_trip_state = "EXECUTING" if decision == "APPROVED" else "RECOVERY_FAILED"
        record(
            session,
            trip_id,
            "APPROVED" if decision == "APPROVED" else "FAILED",
            "Recovery plan approved" if decision == "APPROVED" else "Recovery plan rejected by traveller",
            plan_id=plan.id,
            commit=False,
        )
        session.add(Approval(
            plan_id=plan.id,
            decision=decision,
            decided_at=datetime.now(timezone.utc),
        ))
        plan.state = target_plan_state
        advance(session, trip_id, target_trip_state, commit=False)
        session.flush()
        result = _response(plan)
    return result, True


@router.post("/approvals/{plan_id}/approve")
def approve(plan_id: UUID, user: User = Depends(current_user)):
    result, fresh = _decide(plan_id, "APPROVED", user.id)
    if not fresh:
        return result
    with SessionLocal() as session:
        plan = _get_plan(session, plan_id, user.id)
        trip_id = plan.disruption.trip_id
        emit(
            "plan.executing",
            {"trip_id": str(trip_id), "payload": {"plan_id": str(plan.id)}},
        )
        _execute(session, plan)
        session.refresh(plan)
        return _response(plan)


@router.post("/approvals/{plan_id}/reject")
def reject(plan_id: UUID, user: User = Depends(current_user)):
    return _decide(plan_id, "REJECTED", user.id)[0]
