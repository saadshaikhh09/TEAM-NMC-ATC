"""Trip state transitions. Owner: Person A.

One component owns state. If you need a trip to change status, call advance()
here — do not UPDATE trips.status from your own module.
"""

from datetime import datetime, timezone

from core.events import emit
from core.models import Trip

TRANSITIONS = {
    "CREATED":           {"MONITORING"},
    "MONITORING":        {"DISRUPTED", "RECOVERED"},
    "DISRUPTED":         {"PLANNING", "RECOVERY_FAILED"},
    "PLANNING":          {"AWAITING_APPROVAL", "EXECUTING", "RECOVERY_FAILED"},
    "AWAITING_APPROVAL": {"EXECUTING", "RECOVERY_FAILED"},
    "EXECUTING":         {"RECOVERED", "RECOVERY_FAILED"},
    "RECOVERED":         {"MONITORING"},
    "RECOVERY_FAILED":   {"PLANNING"},
}


def can(current: str, nxt: str) -> bool:
    return nxt in TRANSITIONS.get(current, set())


def advance(session, trip_id: str, nxt: str, *, commit: bool = True):
    trip = session.get(Trip, trip_id)
    if trip is None:
        raise ValueError(f"trip {trip_id} not found")
    if not can(trip.status, nxt):
        raise ValueError(f"illegal transition {trip.status} -> {nxt}")

    trip.status = nxt
    trip.updated_at = datetime.now(timezone.utc)
    if commit:
        session.commit()
    else:
        session.flush()
    session.refresh(trip)
    # Every status change reaches the dashboard from here, so no caller can forget.
    emit("trip.updated", {"trip_id": str(trip.id), "payload": {"status": trip.status}})
    return trip
