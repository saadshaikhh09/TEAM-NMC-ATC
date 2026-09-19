"""Provider interface. Owner: Person B. PUSH THIS IN HOUR 1 — A is blocked.

This is deliberately tool-shaped: four verbs, flat arguments, normalised
returns. Wrapping it in an MCP server later is a mechanical change.

Nobody edits this file except B, and only with a message in the group chat.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class FlightStatus:
    flight_number: str
    status: str                      # SCHEDULED | DELAYED | CANCELLED | DEPARTED | LANDED
    scheduled_departure: datetime
    estimated_departure: datetime | None
    scheduled_arrival: datetime
    estimated_arrival: datetime | None
    gate: str | None = None
    terminal: str | None = None


@dataclass
class FlightOption:
    id: str
    carrier: str
    flight_number: str
    departure: datetime
    arrival: datetime
    stops: int
    cabin: str
    fare_inr: int


@dataclass
class BookingConfirmation:
    reference: str
    provider: str
    fare_inr: int


@dataclass
class HotelOption:
    id: str
    rate_id: str
    name: str
    city: str
    nightly_rate_inr: int


@dataclass
class HotelConfirmation:
    reference: str
    provider: str
    check_in: date
    check_out: date
    cost_delta_inr: int


class FlightProvider(ABC):
    @abstractmethod
    def get_status(self, carrier: str, flight_number: str, on: date) -> FlightStatus: ...

    @abstractmethod
    def search(self, origin: str, destination: str, depart_after: datetime,
               cabin: str) -> list[FlightOption]: ...

    @abstractmethod
    def book(self, option_id: str, passenger: str) -> BookingConfirmation: ...


class HotelProvider(ABC):
    """Nuitee/LiteAPI has no modify endpoint — a date change is
    cancel-then-rebook. The interface models that honestly rather than
    pretending modify() exists, because planner/hotel_impact.py needs to know
    the difference (a cancel-rebook can fail halfway; a modify cannot).
    """

    @abstractmethod
    def search(self, city: str, check_in: date, check_out: date) -> list[HotelOption]: ...

    @abstractmethod
    def prebook(self, rate_id: str) -> str:
        """Hold a room. Returns prebook_id. Nuitee: POST /bookings/prebook."""

    @abstractmethod
    def book(self, prebook_id: str, guest: str) -> HotelConfirmation:
        """Confirm. Nuitee: POST /bookings/book. 409 means the room went."""

    @abstractmethod
    def cancel(self, booking_id: str) -> bool:
        """Nuitee: DELETE /bookings/{id}."""

    def change_dates(self, booking_id: str, rate_id: str, new_check_in: date,
                     new_check_out: date, guest: str) -> HotelConfirmation:
        """Cancel-then-rebook, in that order. Owner: D.

        If book() fails after cancel() succeeded, the traveller has no room.
        Record HOTEL_SHIFTED only after book() returns. On failure, audit
        FAILED and escalate — never leave the timeline claiming a shift that
        did not happen.
        """
        raise NotImplementedError("D2")
