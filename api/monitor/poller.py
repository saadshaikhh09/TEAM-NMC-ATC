"""Polls flights whose next_poll_at is due. Owner: Person B.

Resumable by construction: state lives in the flights row, not in memory.
Kill the process, restart it, it picks up from the database.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.config import settings
from core.models import Flight, Trip
from core.timezones import local_time
from monitor.detection import detect
from monitor.scheduler import effective_poll_interval
from providers.base import FlightProvider


def poll_due(
    session: Session,
    provider: FlightProvider,
    source: str,
    *,
    now: datetime | None = None,
    demo_mode: bool | None = None,
    demo_poll_seconds: int | None = None,
    flight_id: UUID | None = None,
) -> int:
    """Poll due monitoring flights and persist each new resume point.

    The caller supplies the provider and its disruption source. A failed status
    call leaves the flight due for a later run; it never advances the poll time.
    """
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("now must include a timezone")
    config = settings()
    demo_mode = config.demo_mode if demo_mode is None else demo_mode
    demo_poll_seconds = (
        config.demo_poll_seconds if demo_poll_seconds is None else demo_poll_seconds
    )

    query = (
        select(Flight)
        .join(Trip)
        .where(
            Trip.status == "MONITORING",
            Flight.next_poll_at <= now,
            Flight.status.not_in(("CANCELLED", "LANDED")),
        )
        .order_by(Flight.next_poll_at, Flight.id)
        .with_for_update(skip_locked=True)
    )
    if flight_id is not None:
        query = query.where(Flight.id == flight_id)
    due = session.scalars(query).all()
    polled = 0
    for flight in due:
        flight_date = local_time(
            flight.scheduled_departure, flight.origin, flight.origin_timezone
        ).date()
        status = provider.get_status(flight.carrier, flight.flight_number, flight_date)
        if status.status in ("CANCELLED", "DELAYED") and status.status != flight.status:
            kind = "CANCELLATION" if status.status == "CANCELLED" else "DELAY"
            flight.last_polled_at = now
            detect(session, flight.id, kind, source)
            polled += 1
            continue

        flight.status = status.status
        flight.last_polled_at = now
        if status.status == "LANDED":
            flight.next_poll_at = None
        else:
            hours_to_departure = (flight.scheduled_departure - now).total_seconds() / 3600
            flight.next_poll_at = now + effective_poll_interval(
                hours_to_departure,
                demo_mode=demo_mode,
                demo_poll_seconds=demo_poll_seconds,
            )
        session.commit()
        polled += 1
    return polled
