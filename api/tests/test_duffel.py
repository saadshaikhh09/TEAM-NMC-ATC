from datetime import datetime, timezone
import httpx
import pytest

from providers.base import BookingConfirmation, FlightOption
from providers.duffel import DuffelFlightProvider


def test_duffel_search_normalises_flight_options():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert "/air/offer_requests" in str(request.url)
        assert request.headers.get("Duffel-Version") == "v2"
        assert request.headers.get("Authorization") == "Bearer duffel_test_key"

        data = {
            "data": {
                "id": "off_req_123",
                "offers": [
                    {
                        "id": "off_1",
                        "total_amount": "52400.00",
                        "total_currency": "INR",
                        "slices": [
                            {
                                "segments": [
                                    {
                                        "operating_carrier": {"iata_code": "BA"},
                                        "operating_carrier_flight_number": "BA138",
                                        "departing_at": "2026-09-20T08:10:00Z",
                                        "arriving_at": "2026-09-20T18:05:00Z",
                                    }
                                ]
                            }
                        ],
                    }
                ],
            }
        }
        return httpx.Response(200, json=data)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = DuffelFlightProvider(api_key="duffel_test_key", client=client)

    depart_after = datetime(2026, 9, 20, 0, 0, tzinfo=timezone.utc)
    options = provider.search("BOM", "LHR", depart_after, "economy")

    assert len(options) == 1
    assert options[0] == FlightOption(
        id="off_1",
        carrier="BA",
        flight_number="BA138",
        departure=datetime(2026, 9, 20, 8, 10, tzinfo=timezone.utc),
        arrival=datetime(2026, 9, 20, 18, 5, tzinfo=timezone.utc),
        stops=0,
        cabin="economy",
        fare_inr=52400,
    )


def test_duffel_book_returns_confirmation():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert "/air/orders" in str(request.url)
        data = {
            "data": {
                "id": "ord_999",
                "booking_reference": "XYZ789",
                "total_amount": "52400.00",
            }
        }
        return httpx.Response(201, json=data)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = DuffelFlightProvider(api_key="duffel_test_key", client=client)

    confirmation = provider.book("off_1", "Priya Sharma")
    assert confirmation == BookingConfirmation(
        reference="XYZ789",
        provider="duffel",
        fare_inr=52400,
    )


def test_duffel_get_status_raises_not_implemented():
    provider = DuffelFlightProvider(api_key="duffel_test_key")
    with pytest.raises(NotImplementedError):
        provider.get_status("BA", "BA138", datetime(2026, 9, 20).date())
