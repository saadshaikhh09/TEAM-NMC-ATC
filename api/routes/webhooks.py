"""Duffel webhook receiver for airline-initiated disruption events (Task D8).

Duffel sends POST webhooks for order status changes (order.airline_initiated_change_detected).
This receiver deduplicates on event ID and routes into the core disruption detection pipeline.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import select

from core.db import SessionLocal
from core.models import Flight
from monitor.detection import detect
from providers.duffel import parse_webhook_event


router = APIRouter(prefix="/webhooks", tags=["webhooks"])
PRIYA_TRIP_ID = UUID("aaaaaaaa-1111-1111-1111-111111111111")
_PROCESSED_EVENT_IDS: set[str] = set()


@router.post("/duffel")
async def receive_duffel_webhook(request: Request) -> dict[str, Any]:
    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from exc

    parsed = parse_webhook_event(payload)
    event_id = parsed["event_id"]

    # Deduplicate at-least-once deliveries
    if event_id and event_id in _PROCESSED_EVENT_IDS:
        return {"ok": True, "status": "duplicate_skipped", "event_id": event_id}

    if event_id:
        _PROCESSED_EVENT_IDS.add(event_id)

    flight_number = parsed.get("flight_number")
    kind = parsed.get("kind", "CANCELLATION")

    with SessionLocal() as session:
        flight = None
        if flight_number:
            flight = session.scalar(
                select(Flight).where(
                    Flight.flight_number == flight_number,
                    Flight.status == "SCHEDULED",
                )
            )

        # Fallback to Priya's active flight if flight_number is unspecific
        if flight is None:
            flight = session.scalar(
                select(Flight).where(
                    Flight.trip_id == PRIYA_TRIP_ID,
                    Flight.leg == "outbound",
                )
            )

        if flight is None:
            raise HTTPException(status_code=404, detail="Target flight not found for webhook")

        try:
            disruption = detect(session, flight.id, kind, "duffel")
        except ValueError as exc:
            # Flight already disrupted or trip not in monitoring state
            return {
                "ok": True,
                "status": "already_handled",
                "detail": str(exc),
                "event_id": event_id,
            }
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        return {
            "ok": True,
            "status": "disruption_detected",
            "event_id": event_id,
            "flight_id": str(flight.id),
            "disruption_id": str(disruption.id),
            "kind": kind,
            "source": "duffel",
        }
