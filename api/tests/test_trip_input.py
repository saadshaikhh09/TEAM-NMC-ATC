from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from core.trip_service import FlightInput, HotelInput, TripInput
from core.timezones import timezone_name


def flight(**overrides):
    data = {
        "carrier": "AI",
        "flight_number": "AI101",
        "origin": "JFK",
        "destination": "NRT",
        "scheduled_departure": "2026-10-01T10:00:00-04:00",
        "scheduled_arrival": "2026-10-02T13:30:00+09:00",
        "origin_timezone": "America/New_York",
        "destination_timezone": "Asia/Tokyo",
    }
    data.update(overrides)
    return FlightInput(**data)


def test_unknown_airports_require_explicit_valid_timezones():
    assert timezone_name("JFK", "America/New_York") == "America/New_York"
    with pytest.raises(ValueError, match="timezone is required"):
        timezone_name("ZZZ")
    with pytest.raises(ValueError, match="Invalid IANA timezone"):
        timezone_name("ZZZ", "Mars/Olympus")


def test_trip_input_validates_route_and_chronology():
    parsed = TripInput(
        traveller_name="Alex Morgan",
        origin="JFK",
        destination="NRT",
        outbound=flight(),
    )
    assert parsed.outbound.origin == "JFK"

    with pytest.raises(ValidationError, match="arrival must be after departure"):
        flight(scheduled_arrival="2026-10-01T08:00:00-04:00")
    with pytest.raises(ValidationError, match="outbound route"):
        TripInput(
            traveller_name="Alex Morgan",
            origin="JFK",
            destination="SIN",
            outbound=flight(),
        )


def test_naive_flight_times_are_interpreted_in_declared_airport_timezones():
    parsed = flight(
        scheduled_departure="2026-10-01T10:00",
        scheduled_arrival="2026-10-02T12:00",
    )

    assert parsed.scheduled_departure.isoformat() == "2026-10-01T10:00:00-04:00"
    assert parsed.scheduled_arrival.isoformat() == "2026-10-02T12:00:00+09:00"


def test_hotel_coordinates_are_paired_and_bounded():
    valid = {
        "name": "Kensington Central",
        "city": "LON",
        "check_in": "2026-10-01",
        "check_out": "2026-10-03",
    }
    parsed = HotelInput(**valid, latitude=51.4994, longitude=-0.1918)
    assert (parsed.latitude, parsed.longitude) == (51.4994, -0.1918)

    with pytest.raises(ValidationError, match="both be provided"):
        HotelInput(**valid, latitude=51.4994)
    with pytest.raises(ValidationError, match="less than or equal to 90"):
        HotelInput(**valid, latitude=91, longitude=0)
    with pytest.raises(ValidationError, match="less than or equal to 180"):
        HotelInput(**valid, latitude=0, longitude=181)
