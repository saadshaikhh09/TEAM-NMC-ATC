"""Detection -> recovery plan. Owner: Person A.

The missing link. `planner/` and `executor/` were built and unit-tested but
nothing in a live request ever called them, so `recovery_plans` stayed empty and
every trip stopped at DISRUPTED.

This subscribes to `disruption.detected` and drives the existing modules in
order: constraints -> hotel impact -> rank -> gate -> (approval | execute).

It never raises into its caller. By the time we run, `detect()` has already
committed a disruption row; a planning crash must escalate to the traveller as
RECOVERY_FAILED, not 500 the request that reported the disruption.
"""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from core.audit import record
from core.config import policy as load_policy
from core.db import SessionLocal
from core.events import emit
from core.models import (
    Disruption,
    HotelChange,
    PlanOption,
    PlanRejection,
    RecoveryPlan,
    Trip,
)
from core.state_machine import advance, can
from core.timezones import local_str
from executor.gate import decide
from executor.run import run
from planner.constraints import filter as apply_constraints
from planner.hotel_impact import assess
from planner.rank import rank


_flight_provider = None
_hotel_provider = None


def configure(flight_provider, hotel_provider) -> None:
    global _flight_provider, _hotel_provider
    _flight_provider = flight_provider
    _hotel_provider = hotel_provider


def _event(trip_id, plan, **extra) -> dict:
    payload = {"plan_id": str(plan.id) if plan is not None else None}
    payload.update(extra)
    return {"trip_id": str(trip_id), "payload": payload}


def _constraints(trip: Trip) -> dict:
    """The traveller's rules as the planner wants them.

    `destination` is not a column on traveller_constraints, but
    constraints.filter needs an arrival airport to render rejection times in
    local time — without it a hard_arrival_by rejection raises.
    """
    row = trip.traveller.constraints
    deadline = getattr(row, "hard_arrival_by", None)
    return {
        "hard_arrival_by": deadline,
        "hard_arrival_by_local": local_str(deadline, trip.destination) if deadline else None,
        "hard_arrival_reason": getattr(row, "hard_arrival_reason", None),
        "max_fare_inr": getattr(row, "max_fare_inr", None),
        "max_stops": getattr(row, "max_stops", None),
        "cabin": getattr(row, "cabin", None),
        "avoid_carriers": getattr(row, "avoid_carriers", None),
        "auto_approve_under_inr": getattr(row, "auto_approve_under_inr", None),
        "destination": trip.destination,
    }


def _narrate(plan) -> tuple[str, str]:
    """Prose for the plan. Off the critical path: templated copy if the chain is down."""
    from llm import fallback

    try:
        from llm.explain import draft, explain

        return explain(plan), draft(plan)
    except Exception:
        return fallback.explanation(plan), fallback.member_message(plan)


def _escalate(session, trip_id, headline: str, plan=None) -> None:
    record(session, trip_id, "FAILED", headline, plan_id=plan.id if plan else None)
    if plan is not None:
        plan.state = "FAILED"
        session.commit()
    trip = session.get(Trip, trip_id)
    if trip is not None and can(trip.status, "RECOVERY_FAILED"):
        advance(session, trip_id, "RECOVERY_FAILED")
    emit("plan.failed", _event(trip_id, plan, error=headline))


def plan_for(session, disruption: Disruption) -> RecoveryPlan:
    """Build, persist and dispatch the recovery plan for one disruption."""
    if _flight_provider is None or _hotel_provider is None:
        raise RuntimeError("orchestrator providers are not configured")

    flight = disruption.flight
    trip = disruption.trip
    policy = load_policy()
    constraints = _constraints(trip)

    record(
        session,
        trip.id,
        "PLANNING",
        f"Searching alternatives {flight.origin} to {flight.destination}",
        {"disruption_id": str(disruption.id)},
    )
    advance(session, trip.id, "PLANNING")

    # A replacement may not depart before the flight it replaces.
    options = _flight_provider.search(
        flight.origin,
        flight.destination,
        flight.scheduled_departure,
        flight.cabin or "economy",
    )
    survivors, rejections = apply_constraints(options, constraints, policy)

    hotel = trip.hotels[0] if trip.hotels else None
    hotel_deltas = (
        {
            option.id: assess(hotel, option.arrival, policy)["cost_delta_inr"]
            for option in survivors
        }
        if hotel is not None
        else {}
    )
    scored = rank(survivors, flight, constraints, policy, hotel_deltas)

    plan = RecoveryPlan(
        disruption_id=disruption.id,
        state="DRAFT",
        evaluated_count=len(options),
        requires_approval=True,
    )
    session.add(plan)
    session.flush()

    for item in scored:
        session.add(
            PlanOption(
                plan_id=plan.id,
                option_id=item.option.id,
                carrier=item.option.carrier,
                flight_number=item.option.flight_number,
                departure=item.option.departure,
                arrival=item.option.arrival,
                stops=item.option.stops,
                cabin=item.option.cabin,
                fare_inr=item.option.fare_inr,
                score=Decimal(str(round(item.score, 6))),
                rank=item.rank,
            )
        )
    for rejection in rejections:
        session.add(PlanRejection(plan_id=plan.id, **rejection))

    change = None
    if hotel is not None and scored:
        change = HotelChange(
            plan_id=plan.id, hotel_id=hotel.id, **assess(hotel, scored[0].option.arrival, policy)
        )
        session.add(change)
    session.commit()
    session.refresh(plan)

    record(
        session,
        trip.id,
        "EVALUATED",
        f"Evaluated {len(options)} option{'' if len(options) == 1 else 's'}, "
        f"rejected {len(rejections)} on policy",
        {
            "evaluated": len(options),
            "rejected": len(rejections),
            "survivors": len(survivors),
        },
        plan_id=plan.id,
    )

    if not scored:
        # The rejection list is still the most valuable thing on screen, so the
        # plan is persisted and published before the trip is failed.
        plan.approval_reason = "No option satisfies your hard constraints"
        plan.explanation, plan.member_message = _narrate(plan)
        session.commit()
        emit("plan.ready", _event(trip.id, plan, disruption_id=str(disruption.id)))
        _escalate(session, trip.id, "No option satisfies the traveller's hard constraints", plan)
        return plan

    chosen = scored[0]
    plan.chosen_option_id = chosen.option.id
    plan.total_cost_delta_inr = (
        chosen.option.fare_inr
        - (flight.fare_inr or 0)
        + (change.cost_delta_inr if change is not None and change.required else 0)
    )
    session.commit()
    session.refresh(plan)

    mode, reason = decide(plan, constraints, policy)
    plan.requires_approval = mode == "APPROVAL"
    plan.approval_reason = reason
    plan.explanation, plan.member_message = _narrate(plan)
    session.commit()
    emit("plan.ready", _event(trip.id, plan, disruption_id=str(disruption.id)))

    if plan.requires_approval:
        plan.state = "AWAITING_APPROVAL"
        session.commit()
        record(
            session,
            trip.id,
            "AWAITING_APPROVAL",
            reason or "Traveller approval required",
            plan_id=plan.id,
        )
        advance(session, trip.id, "AWAITING_APPROVAL")
        emit("plan.awaiting_approval", _event(trip.id, plan, reason=reason))
        return plan

    plan.state = "EXECUTING"
    session.commit()
    advance(session, trip.id, "EXECUTING")
    emit("plan.executing", _event(trip.id, plan))
    run(session, plan, _flight_provider, _hotel_provider)
    session.refresh(plan)
    return plan


def on_disruption_detected(message: dict) -> None:
    """Event-bus entry point. Opens its own session; detect() has already committed."""
    try:
        disruption_id = UUID(message["payload"]["disruption_id"])
    except (KeyError, TypeError, ValueError):
        return
    with SessionLocal() as session:
        disruption = session.get(Disruption, disruption_id)
        if disruption is None:
            return
        trip_id = disruption.trip_id
        try:
            plan_for(session, disruption)
        except Exception as exc:  # planning must escalate, never 500 the reporter
            session.rollback()
            _escalate(session, trip_id, f"Planning failed: {exc}")
