from datetime import date, datetime, timezone

import pytest

from providers.mock import MockFlightProvider, MockHotelProvider


def test_priya_has_cheaper_faster_option_that_misses_deadline():
    provider = MockFlightProvider()
    options = provider.search("BOM", "LHR", datetime(2026, 9, 19, 21, tzinfo=timezone.utc), "economy")
    chosen = next(option for option in options if option.id == "opt_1")
    rejected = next(option for option in options if option.id == "opt_4")

    assert rejected.fare_inr == chosen.fare_inr - 8000
    assert rejected.arrival - rejected.departure < chosen.arrival - chosen.departure
    assert rejected.arrival > datetime(2026, 9, 21, 8, tzinfo=timezone.utc)
    assert options == provider.search("BOM", "LHR", datetime(2026, 9, 19, 21, tzinfo=timezone.utc), "economy")


def test_mock_flight_status_and_booking():
    provider = MockFlightProvider()
    status = provider.get_status("AI", "AI131", date(2026, 9, 20))
    assert status.status == "SCHEDULED"
    assert status.scheduled_departure.tzinfo is timezone.utc
    assert provider.book("opt_1", "Priya Sharma").reference == "MOCK-OPT_1"
    with pytest.raises(ValueError, match="unknown mock flight option"):
        provider.book("missing", "Priya Sharma")


def test_mock_hotel_lifecycle():
    provider = MockHotelProvider()
    options = provider.search("LON", date(2026, 9, 21), date(2026, 9, 25))
    assert len(options) == 1
    prebook_id = provider.prebook(options[0].rate_id)
    booking = provider.book(prebook_id, "Priya Sharma")
    assert booking.check_in == date(2026, 9, 21)
    assert booking.check_out == date(2026, 9, 25)
    assert booking.reference == "MOCK-RATE_LON"
    assert provider.cancel(booking.reference)
    assert not provider.cancel(booking.reference)


def test_arbitrary_route_has_deterministic_flight_options_and_booking():
    provider = MockFlightProvider()
    depart_after = datetime(2026, 10, 1, 14, tzinfo=timezone.utc)

    first = provider.search("JFK", "NRT", depart_after, "economy")
    second = provider.search("JFK", "NRT", depart_after, "economy")

    assert first == second
    assert len(first) >= 2
    assert all(option.departure >= depart_after for option in first)
    assert provider.book(first[0].id, "Alex Morgan").reference.startswith("MOCK-")
