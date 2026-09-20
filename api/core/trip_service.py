"""Validate booking input, then persist the complete trip in one transaction."""

from __future__ import annotations

import re
from datetime import date, datetime, timezone
from typing import Literal
from uuid import UUID
from zoneinfo import ZoneInfo

from pydantic import AwareDatetime, BaseModel, Field, field_validator, model_validator
from sqlalchemy import select

from core.models import Flight, Hotel, Traveller, TravellerConstraint, Trip, User
from core.timezones import timezone_name
from providers.geocoding import geocode_hotel


IATA = re.compile(r"^[A-Z]{3}$")


class FlightInput(BaseModel):
    leg: Literal["outbound", "return"] = "outbound"
    carrier: str = Field(min_length=2, max_length=3)
    flight_number: str = Field(min_length=2, max_length=12)
    origin: str
    destination: str
    scheduled_departure: datetime
    scheduled_arrival: datetime
    origin_timezone: str | None = None
    destination_timezone: str | None = None
    booking_reference: str | None = Field(default=None, max_length=64)
    fare_inr: int | None = Field(default=None, ge=0)
    cabin: str = Field(default="economy", min_length=1, max_length=32)

    @field_validator("origin", "destination")
    @classmethod
    def valid_iata(cls, value: str) -> str:
        code = value.strip().upper()
        if not IATA.fullmatch(code):
            raise ValueError("IATA airport codes must contain exactly three letters")
        return code

    @field_validator("carrier")
    @classmethod
    def valid_carrier(cls, value: str) -> str:
        code = value.strip().upper()
        if not re.fullmatch(r"[A-Z0-9]{2,3}", code):
            raise ValueError("carrier must be a two or three character airline code")
        return code

    @field_validator("flight_number")
    @classmethod
    def valid_number(cls, value: str) -> str:
        number = value.strip().upper()
        if not re.fullmatch(r"[A-Z0-9]{2,12}", number):
            raise ValueError("flight number must be 2 to 12 letters or digits")
        return number

    @model_validator(mode="after")
    def validate_flight(self):
        if self.origin == self.destination:
            raise ValueError("flight origin and destination must differ")
        self.origin_timezone = timezone_name(self.origin, self.origin_timezone)
        self.destination_timezone = timezone_name(self.destination, self.destination_timezone)
        if self.scheduled_departure.tzinfo is None:
            self.scheduled_departure = self.scheduled_departure.replace(
                tzinfo=ZoneInfo(self.origin_timezone)
            )
        if self.scheduled_arrival.tzinfo is None:
            self.scheduled_arrival = self.scheduled_arrival.replace(
                tzinfo=ZoneInfo(self.destination_timezone)
            )
        if self.scheduled_arrival <= self.scheduled_departure:
            raise ValueError("arrival must be after departure")
        self.carrier = self.carrier.strip().upper()
        self.flight_number = self.flight_number.strip().upper()
        return self


class HotelInput(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    address: str | None = Field(default=None, max_length=240)
    city: str = Field(min_length=2, max_length=80)
    city_timezone: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    check_in: date
    check_out: date
    confirmation_number: str | None = Field(default=None, max_length=64)
    nightly_rate_inr: int | None = Field(default=None, ge=0)
    modifiable: bool = True

    @model_validator(mode="after")
    def validate_hotel(self):
        if self.check_out <= self.check_in:
            raise ValueError("hotel check-out must be after check-in")
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("hotel latitude and longitude must both be provided")
        self.address = self.address.strip() if self.address and self.address.strip() else None
        self.city_timezone = timezone_name(self.city, self.city_timezone)
        return self


class ConstraintInput(BaseModel):
    hard_arrival_by: AwareDatetime | None = None
    hard_arrival_timezone: str | None = None
    hard_arrival_reason: str | None = Field(default=None, max_length=500)
    max_fare_inr: int | None = Field(default=None, ge=0)
    max_stops: int | None = Field(default=1, ge=0, le=4)
    cabin: str = Field(default="economy", min_length=1, max_length=32)
    avoid_carriers: list[str] = Field(default_factory=list, max_length=20)
    auto_approve_under_inr: int | None = Field(default=None, ge=0)

    @field_validator("avoid_carriers")
    @classmethod
    def valid_carriers(cls, values: list[str]) -> list[str]:
        codes = [value.strip().upper() for value in values]
        if any(not re.fullmatch(r"[A-Z0-9]{2,3}", code) for code in codes):
            raise ValueError("each avoided carrier must be a two or three character code")
        return list(dict.fromkeys(codes))


class TripInput(BaseModel):
    traveller_name: str = Field(min_length=1, max_length=120)
    origin: str
    destination: str
    outbound: FlightInput
    return_flight: FlightInput | None = None
    hotel: HotelInput | None = None
    constraints: ConstraintInput = Field(default_factory=ConstraintInput)

    @field_validator("origin", "destination")
    @classmethod
    def valid_iata(cls, value: str) -> str:
        code = value.strip().upper()
        if not IATA.fullmatch(code):
            raise ValueError("IATA airport codes must contain exactly three letters")
        return code

    @field_validator("traveller_name")
    @classmethod
    def valid_name(cls, value: str) -> str:
        name = value.strip()
        if not name:
            raise ValueError("traveller name is required")
        return name

    @model_validator(mode="after")
    def validate_trip(self):
        if (self.outbound.origin, self.outbound.destination) != (self.origin, self.destination):
            raise ValueError("outbound route must match the trip origin and destination")
        self.outbound.leg = "outbound"
        if self.return_flight:
            if (self.return_flight.origin, self.return_flight.destination) != (
                self.destination, self.origin
            ):
                raise ValueError("return route must reverse the outbound route")
            if self.return_flight.scheduled_departure <= self.outbound.scheduled_arrival:
                raise ValueError("return departure must be after outbound arrival")
            self.return_flight.leg = "return"
        if self.constraints.hard_arrival_by:
            self.constraints.hard_arrival_timezone = timezone_name(
                self.destination, self.constraints.hard_arrival_timezone
            )
        return self


def persist_trip(db, user_id: UUID, data: TripInput) -> Trip:
    traveller = db.scalar(
        select(Traveller).where(
            Traveller.user_id == user_id, Traveller.name == data.traveller_name.strip()
        )
    )
    if traveller is None:
        user = db.get(User, user_id)
        traveller = Traveller(user_id=user_id, name=data.traveller_name.strip(), email=user.email)
        db.add(traveller)
        db.flush()
    constraints = traveller.constraints or TravellerConstraint(traveller_id=traveller.id)
    for key, value in data.constraints.model_dump().items():
        setattr(constraints, key, value)
    db.add(constraints)

    trip = Trip(
        traveller_id=traveller.id, status="MONITORING", origin=data.origin,
        destination=data.destination,
    )
    db.add(trip)
    db.flush()
    for item in filter(None, (data.outbound, data.return_flight)):
        db.add(Flight(
            trip_id=trip.id, **item.model_dump(), status="SCHEDULED",
            next_poll_at=datetime.now(timezone.utc),
        ))
    if data.hotel:
        hotel = data.hotel.model_dump()
        if hotel["latitude"] is None:
            coordinates = geocode_hotel(data.hotel.name, data.hotel.city, data.hotel.address)
            if coordinates:
                hotel["latitude"], hotel["longitude"] = coordinates
        db.add(Hotel(trip_id=trip.id, **hotel))
    db.flush()
    return trip
