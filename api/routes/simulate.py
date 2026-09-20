"""The declared test harness. Owner: Person B.

POST /simulate/cancellation writes the SAME disruptions row and fires the SAME
event as a real detection. The rest of the system cannot tell the difference —
which is exactly why we can say "simulated feed, real decision logic" honestly.

Say that sentence out loud in the pitch. Do not hide this endpoint.
"""
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import AwareDatetime, BaseModel, ConfigDict, field_serializer
from sqlalchemy import select

from core.db import SessionLocal
from core.auth import current_user
from core.models import Flight, User
from core.ownership import flights_for
from monitor.detection import detect


router = APIRouter()


class DisruptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    trip_id: UUID
    flight_id: UUID
    kind: str
    source: str
    detected_at: AwareDatetime
    previous_status: str
    new_status: str

    @field_serializer("detected_at")
    def serialize_timestamp(self, value: datetime) -> str:
        return value.isoformat()


def _simulate(kind: str, flight_id: UUID | None, user_id) -> DisruptionResponse:
    with SessionLocal() as session:
        if flight_id is None:
            flight_id = session.scalar(
                flights_for(user_id).with_only_columns(Flight.id).where(
                    Flight.leg == "outbound"
                ).order_by(Flight.scheduled_departure)
            )
        elif session.scalar(
            flights_for(user_id).with_only_columns(Flight.id).where(Flight.id == flight_id)
        ) is None:
            raise HTTPException(status_code=404, detail="Flight not found")
        if flight_id is None:
            raise HTTPException(status_code=404, detail="Flight not found")
        try:
            disruption = detect(session, flight_id, kind, "simulated")
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return DisruptionResponse.model_validate(disruption)


@router.post("/simulate/cancellation", response_model=DisruptionResponse)
def simulate_cancellation(
    flight_id: UUID | None = None, user: User = Depends(current_user)
) -> DisruptionResponse:
    return _simulate("CANCELLATION", flight_id, user.id)


@router.post("/simulate/delay", response_model=DisruptionResponse)
def simulate_delay(
    flight_id: UUID | None = None, user: User = Depends(current_user)
) -> DisruptionResponse:
    return _simulate("DELAY", flight_id, user.id)
