from datetime import date
import httpx
import pytest

from providers.base import HotelConfirmation, HotelOption
from providers.nuitee import NuiteeHotelProvider


def test_nuitee_search_parses_hotel_options():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert "/hotels/rates" in str(request.url)
        assert request.headers.get("X-API-Key") == "sand_test_key"
        data = {
            "data": [
                {
                    "hotelId": "htl_101",
                    "name": "Kensington Central",
                    "rates": [
                        {"rateId": "rate_abc", "retailRate": {"total": {"amount": 9800}}}
                    ],
                }
            ]
        }
        return httpx.Response(200, json=data)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = NuiteeHotelProvider(api_key="sand_test_key", client=client)
    options = provider.search("LON", date(2026, 9, 21), date(2026, 9, 25))

    assert len(options) == 1
    assert options[0] == HotelOption(
        id="htl_101",
        rate_id="rate_abc",
        name="Kensington Central",
        city="LON",
        nightly_rate_inr=9800,
    )


def test_nuitee_search_invalid_dates():
    provider = NuiteeHotelProvider(api_key="sand_test_key")
    with pytest.raises(ValueError, match="check_out must be after check_in"):
        provider.search("LON", date(2026, 9, 25), date(2026, 9, 21))


def test_nuitee_prebook_returns_id():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert "/bookings/prebook" in str(request.url)
        return httpx.Response(200, json={"data": {"prebookId": "pre_999"}})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = NuiteeHotelProvider(api_key="sand_test_key", client=client)
    prebook_id = provider.prebook("rate_abc")
    assert prebook_id == "pre_999"


def test_nuitee_prebook_conflict_409():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(409, json={"error": {"message": "Rate expired"}})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = NuiteeHotelProvider(api_key="sand_test_key", client=client)
    with pytest.raises(RuntimeError, match="409 Conflict"):
        provider.prebook("rate_abc")


def test_nuitee_book_and_cancel_lifecycle():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST" and "/bookings/book" in str(request.url):
            return httpx.Response(
                200,
                json={
                    "data": {
                        "bookingId": "BK-7788",
                        "checkin": "2026-09-21",
                        "checkout": "2026-09-25",
                        "status": "CONFIRMED",
                    }
                },
            )
        if request.method == "DELETE" and "/bookings/BK-7788" in str(request.url):
            return httpx.Response(200, json={"data": {"status": "CANCELLED"}})
        return httpx.Response(404)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = NuiteeHotelProvider(api_key="sand_test_key", client=client)

    confirmation = provider.book("pre_999", "Priya Sharma")
    assert confirmation.reference == "BK-7788"
    assert confirmation.provider == "nuitee"
    assert confirmation.check_in == date(2026, 9, 21)
    assert confirmation.check_out == date(2026, 9, 25)

    cancelled = provider.cancel("BK-7788")
    assert cancelled is True
