"""Deterministic demo providers. No network, quota usage, or random values."""

from __future__ import annotations

from datetime import date, datetime, timezone

from providers.base import (
    BookingConfirmation,
    FlightOption,
    FlightProvider,
    FlightStatus,
    HotelConfirmation,
    HotelOption,
    HotelProvider,
)


def _utc(value: str) -> datetime:
    return datetime.fromisoformat(value).astimezone(timezone.utc)


_FLIGHTS = {
    ("AI", "AI131", date(2026, 9, 20)): (
        _utc("2026-09-19T21:00:00+00:00"),
        _utc("2026-09-20T06:15:00+00:00"),
    ),
    ("AI", "AI132", date(2026, 9, 25)): (
        _utc("2026-09-25T12:00:00+00:00"),
        _utc("2026-09-25T21:10:00+00:00"),
    ),
    ("6E", "6E1051", date(2026, 9, 20)): (
        _utc("2026-09-20T18:20:00+00:00"),
        _utc("2026-09-21T00:05:00+00:00"),
    ),
    ("EK", "EK569", date(2026, 9, 20)): (
        _utc("2026-09-19T22:50:00+00:00"),
        _utc("2026-09-20T03:05:00+00:00"),
    ),
}


_OPTIONS = {
    ("BOM", "LHR"): (
        ("opt_1", "BA", "BA138", "2026-09-20T08:10:00+00:00", "2026-09-20T18:05:00+00:00", 0, 52400),
        ("opt_2", "AI", "AI129", "2026-09-20T04:30:00+00:00", "2026-09-20T14:40:00+00:00", 0, 61500),
        ("opt_3", "EK", "EK501", "2026-09-20T00:30:00+00:00", "2026-09-20T19:30:00+00:00", 1, 58000),
        # Shorter and INR 8,000 cheaper than opt_1, but after Priya's 09:00 London deadline.
        ("opt_4", "VS", "VS355", "2026-09-21T02:00:00+00:00", "2026-09-21T10:40:00+00:00", 0, 44400),
    ),
    ("DEL", "SIN"): (
        ("opt_r1", "SQ", "SQ403", "2026-09-21T04:00:00+00:00", "2026-09-21T09:45:00+00:00", 0, 62000),
        ("opt_r2", "AI", "AI380", "2026-09-21T06:00:00+00:00", "2026-09-21T13:30:00+00:00", 1, 72000),
    ),
    ("BLR", "DXB"): (
        ("opt_a1", "EK", "EK567", "2026-09-20T06:00:00+00:00", "2026-09-20T10:10:00+00:00", 0, 30000),
    ),
}


class MockFlightProvider(FlightProvider):
    def get_status(self, carrier: str, flight_number: str, on: date) -> FlightStatus:
        key = (carrier.upper(), flight_number.upper(), on)
        try:
            departure, arrival = _FLIGHTS[key]
        except KeyError as exc:
            raise ValueError(f"no mock status for {key}") from exc
        return FlightStatus(
            flight_number=flight_number.upper(),
            status="SCHEDULED",
            scheduled_departure=departure,
            estimated_departure=None,
            scheduled_arrival=arrival,
            estimated_arrival=None,
        )

    def search(self, origin: str, destination: str, depart_after: datetime,
               cabin: str) -> list[FlightOption]:
        if depart_after.tzinfo is None or depart_after.utcoffset() is None:
            raise ValueError("depart_after must include a timezone")
        if cabin != "economy":
            return []
        rows = _OPTIONS.get((origin.upper(), destination.upper()), ())
        return [
            FlightOption(option_id, carrier, number, _utc(departure), _utc(arrival),
                         stops, cabin, fare)
            for option_id, carrier, number, departure, arrival, stops, fare in rows
            if _utc(departure) >= depart_after
        ]

    def book(self, option_id: str, passenger: str) -> BookingConfirmation:
        if not passenger.strip():
            raise ValueError("passenger is required")
        for rows in _OPTIONS.values():
            for candidate_id, _, _, _, _, _, fare in rows:
                if candidate_id == option_id:
                    return BookingConfirmation(
                        reference=f"MOCK-{option_id.upper()}",
                        provider="mock",
                        fare_inr=fare,
                    )
        raise ValueError(f"unknown mock flight option {option_id!r}")


_HOTELS = {
    "LON": ("hotel_lon", "rate_lon", "Kensington Central", 9800),
    "SIN": ("hotel_sin", "rate_sin", "Bugis Riverside", 7200),
    "DXB": ("hotel_dxb", "rate_dxb", "Downtown Dubai", 8500),
}


class MockHotelProvider(HotelProvider):
    def __init__(self) -> None:
        self._rates: dict[str, tuple[date, date]] = {}
        self._prebooks: dict[str, str] = {}
        self._bookings: set[str] = set()

    def search(self, city: str, check_in: date, check_out: date) -> list[HotelOption]:
        if check_out <= check_in:
            raise ValueError("check_out must be after check_in")
        city = city.upper()
        if city not in _HOTELS:
            return []
        option_id, rate_id, name, nightly_rate = _HOTELS[city]
        self._rates[rate_id] = (check_in, check_out)
        return [HotelOption(option_id, rate_id, name, city, nightly_rate)]

    def prebook(self, rate_id: str) -> str:
        if rate_id not in self._rates:
            raise ValueError(f"unknown mock hotel rate {rate_id!r}")
        prebook_id = f"PREBOOK-{rate_id.upper()}"
        self._prebooks[prebook_id] = rate_id
        return prebook_id

    def book(self, prebook_id: str, guest: str) -> HotelConfirmation:
        if not guest.strip():
            raise ValueError("guest is required")
        try:
            rate_id = self._prebooks[prebook_id]
        except KeyError as exc:
            raise ValueError(f"unknown mock prebook {prebook_id!r}") from exc
        check_in, check_out = self._rates[rate_id]
        reference = f"MOCK-{rate_id.upper()}"
        self._bookings.add(reference)
        return HotelConfirmation(reference, "mock", check_in, check_out, 0)

    def cancel(self, booking_id: str) -> bool:
        if booking_id not in self._bookings:
            return False
        self._bookings.remove(booking_id)
        return True
