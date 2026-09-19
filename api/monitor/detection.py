"""Persist a detected flight disruption for simulation and status polling."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from core.audit import record
from core.events import emit
from core.models import Disruption, Flight
from core.state_machine import advance


KINDS = {"CANCELLATION": "CANCELLED", "DELAY": "DELAYED"}
SOURCES = {"simulated", "aerodatabox", "aviationstack", "duffel"}


def detect(session: Session, flight_id: UUID, kind: str, source: str) -> Disruption:
    """Write the disruption and timeline once, then publish its event."""
    if kind not in KINDS:
        raise ValueError(f"unsupported disruption kind {kind!r}")
    if source not in SOURCES:
        raise ValueError(f"unsupported disruption source {source!r}")
    flight = session.get(Flight, flight_id)
    if flight is None:
        raise LookupError(f"flight {flight_id} not found")

    new_status = KINDS[kind]
    if flight.status == new_status:
        existing = (
            session.query(Disruption)
            .filter_by(flight_id=flight_id, kind=kind, new_status=new_status)
            .order_by(Disruption.detected_at.desc())
            .first()
        )
        if existing is not None:
            return existing
        raise ValueError(f"flight {flight_id} is already {new_status}")
    if flight.trip.status != "MONITORING":
        raise ValueError(f"trip {flight.trip_id} is {flight.trip.status}, not MONITORING")

    previous_status = flight.status
    flight.status = new_status
    flight.next_poll_at = None
    disruption = Disruption(
        trip_id=flight.trip_id,
        flight_id=flight.id,
        kind=kind,
        source=source,
        previous_status=previous_status,
        new_status=new_status,
    )
    session.add(disruption)
    session.commit()
    session.refresh(disruption)

    advance(session, flight.trip_id, "DISRUPTED")
    record(
        session,
        flight.trip_id,
        "DETECTED",
        f"{flight.flight_number} {kind.lower().replace('_', ' ')} detected",
        {"disruption_id": str(disruption.id), "source": source},
    )
    emit(
        "disruption.detected",
        {"trip_id": str(flight.trip_id), "payload": {"disruption_id": str(disruption.id)}},
    )
    return disruption
