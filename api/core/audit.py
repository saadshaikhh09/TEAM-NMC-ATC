"""The timeline writer. Owner: Person A.

RULE: only this module writes to agent_actions. Every other module calls
record(). If you find yourself writing an INSERT into agent_actions somewhere
else, stop — you are about to make the timeline render garbage.
"""
from typing import Any

from core.events import emit
from core.models import AgentAction


STAGES = {
    "DETECTED", "PLANNING", "EVALUATED", "AWAITING_APPROVAL",
    "APPROVED", "REBOOKED", "HOTEL_SHIFTED", "NOTIFIED", "FAILED",
}


def record(
    session,
    trip_id: str,
    stage: str,
    headline: str,
    detail: dict[str, Any] | None = None,
    plan_id: str | None = None,
    duration_ms: int | None = None,
):
    """Write one timeline row, then broadcast it. Call BEFORE doing the work."""
    if stage not in STAGES:
        raise ValueError(f"unknown stage {stage!r}; see CONTRACT.md")

    action = AgentAction(
        trip_id=trip_id,
        plan_id=plan_id,
        stage=stage,
        headline=headline,
        detail={} if detail is None else detail,
        duration_ms=duration_ms,
    )
    session.add(action)
    session.commit()
    session.refresh(action)
    emit(
        "action.recorded",
        {
            "trip_id": str(action.trip_id),
            "payload": {"action_id": str(action.id)},
        },
    )
    return action
