"""GET/POST trips, timeline. Owner: Person A."""

from datetime import date, datetime
from typing import Any, Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    computed_field,
    field_serializer,
)
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from core.db import SessionLocal
from core.models import AgentAction as AgentActionRow
from core.models import Trip as TripRow
from core.models import Traveller
from core.timezones import local_str


router = APIRouter()


class Flight(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    leg: Literal["outbound", "return"]
    carrier: str
    flight_number: str
    origin: str
    destination: str
    scheduled_departure: AwareDatetime
    scheduled_arrival: AwareDatetime
    status: Literal["SCHEDULED", "DELAYED", "CANCELLED", "DEPARTED", "LANDED"]
    next_poll_at: AwareDatetime | None

    @computed_field
    @property
    def departure_local(self) -> str:
        return local_str(self.scheduled_departure, self.origin)

    @computed_field
    @property
    def arrival_local(self) -> str:
        return local_str(self.scheduled_arrival, self.destination)

    @field_serializer("scheduled_departure", "scheduled_arrival", "next_poll_at")
    def serialize_timestamp(self, value: datetime | None) -> str | None:
        return value.isoformat() if value else None


class Hotel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    provider: str
    confirmation_number: str | None
    name: str
    city: str
    check_in: date
    check_out: date
    nightly_rate_inr: int | None
    modifiable: bool
    status: str


class Constraints(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    hard_arrival_by: AwareDatetime | None
    hard_arrival_reason: str | None
    max_fare_inr: int | None
    max_stops: int | None
    cabin: str | None
    avoid_carriers: list[str] | None
    auto_approve_under_inr: int | None
    hard_arrival_by_local: str | None = None

    @field_serializer("hard_arrival_by")
    def serialize_timestamp(self, value: datetime | None) -> str | None:
        return value.isoformat() if value else None


class Trip(BaseModel):
    id: UUID
    traveller_name: str
    status: Literal[
        "CREATED",
        "MONITORING",
        "DISRUPTED",
        "PLANNING",
        "AWAITING_APPROVAL",
        "EXECUTING",
        "RECOVERED",
        "RECOVERY_FAILED",
    ]
    origin: str
    destination: str
    flights: list[Flight]
    hotels: list[Hotel]
    constraints: Constraints


class AgentAction(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    trip_id: UUID
    at: AwareDatetime
    stage: Literal[
        "DETECTED",
        "PLANNING",
        "EVALUATED",
        "AWAITING_APPROVAL",
        "APPROVED",
        "REBOOKED",
        "HOTEL_SHIFTED",
        "NOTIFIED",
        "FAILED",
    ]
    headline: str
    detail: dict[str, Any]
    duration_ms: int | None


def _response(trip: TripRow) -> Trip:
    return Trip(
        id=trip.id,
        traveller_name=trip.traveller.name,
        status=trip.status,
        origin=trip.origin,
        destination=trip.destination,
        flights=sorted(trip.flights, key=lambda flight: flight.leg),
        hotels=sorted(trip.hotels, key=lambda hotel: hotel.check_in),
        constraints=Constraints.model_validate(trip.traveller.constraints).model_copy(
            update={
                "hard_arrival_by_local": local_str(
                    trip.traveller.constraints.hard_arrival_by, trip.destination
                )
                if trip.traveller.constraints.hard_arrival_by
                else None
            }
        ),
    )


@router.get("/trips", response_model=list[Trip])
def list_trips():
    with SessionLocal() as session:
        trips = session.scalars(
            select(TripRow)
            .options(
                joinedload(TripRow.traveller).joinedload(Traveller.constraints),
                selectinload(TripRow.flights),
                selectinload(TripRow.hotels),
            )
            .order_by(TripRow.created_at, TripRow.id)
        ).all()
        return [_response(trip) for trip in trips]


@router.get("/trips/{trip_id}", response_model=Trip)
def get_trip(trip_id: UUID):
    with SessionLocal() as session:
        trip = session.scalars(
            select(TripRow)
            .where(TripRow.id == trip_id)
            .options(
                joinedload(TripRow.traveller).joinedload(Traveller.constraints),
                selectinload(TripRow.flights),
                selectinload(TripRow.hotels),
            )
        ).one_or_none()
        if trip is None:
            raise HTTPException(status_code=404, detail="Trip not found")
        return _response(trip)


@router.get("/trips/{trip_id}/timeline", response_model=list[AgentAction])
def get_timeline(trip_id: UUID):
    with SessionLocal() as session:
        if session.get(TripRow, trip_id) is None:
            raise HTTPException(status_code=404, detail="Trip not found")
        return session.scalars(
            select(AgentActionRow)
            .where(AgentActionRow.trip_id == trip_id)
            .order_by(AgentActionRow.at, AgentActionRow.id)
        ).all()


@router.post("/trips")
def create_trip():
    raise NotImplementedError("A")


@router.post("/trips/extract")
def extract_trip():
    raise NotImplementedError("A")
