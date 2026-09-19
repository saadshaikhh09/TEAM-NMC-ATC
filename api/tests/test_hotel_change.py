"""Tests for HotelProvider.change_dates() cancel-then-rebook lifecycle (Task D2).

All tests run against fakes/mocks without hitting any live network endpoints.
"""

from datetime import date
import pytest

from providers.base import HotelConfirmation, HotelOption, HotelProvider
from providers.nuitee import NuiteeHotelProvider


class FakeHotelProvider(HotelProvider):
    """A deterministic fake hotel provider for verifying change_dates contract."""

    def __init__(
        self,
        *,
        cancel_succeeds: bool = True,
        prebook_succeeds: bool = True,
        book_succeeds: bool = True,
    ) -> None:
        self.cancel_succeeds = cancel_succeeds
        self.prebook_succeeds = prebook_succeeds
        self.book_succeeds = book_succeeds
        self.cancelled_bookings: list[str] = []
        self.prebooked_rates: list[str] = []
        self.confirmed_bookings: list[tuple[str, str]] = []

    def search(self, city: str, check_in: date, check_out: date) -> list[HotelOption]:
        return [
            HotelOption(
                id="fake_htl_1",
                rate_id="rate_fake_123",
                name="Fake Hotel London",
                city=city,
                nightly_rate_inr=9800,
            )
        ]

    def prebook(self, rate_id: str) -> str:
        if not self.prebook_succeeds:
            raise RuntimeError("Fake prebook failed: room unavailable")
        self.prebooked_rates.append(rate_id)
        return f"PRE_{rate_id}"

    def book(self, prebook_id: str, guest: str) -> HotelConfirmation:
        if not self.book_succeeds:
            raise RuntimeError("Fake booking failed (409 Conflict): room rate expired")
        self.confirmed_bookings.append((prebook_id, guest))
        return HotelConfirmation(
            reference=f"BK_{prebook_id}",
            provider="fake_hotel",
            check_in=date(2026, 9, 21),
            check_out=date(2026, 9, 25),
            cost_delta_inr=0,
        )

    def cancel(self, booking_id: str) -> bool:
        if not self.cancel_succeeds:
            return False
        self.cancelled_bookings.append(booking_id)
        return True

    def change_dates(
        self,
        booking_id: str,
        rate_id: str,
        new_check_in: date,
        new_check_out: date,
        guest: str,
    ) -> HotelConfirmation:
        cancelled = self.cancel(booking_id)
        if not cancelled:
            raise RuntimeError(f"Hotel cancellation failed for {booking_id}; existing reservation retained")

        try:
            prebook_id = self.prebook(rate_id)
            confirmation = self.book(prebook_id, guest)
        except Exception as exc:
            raise RuntimeError(
                f"Hotel cancelled ({booking_id}) but rebook failed — traveller has a flight and no room"
            ) from exc

        return HotelConfirmation(
            reference=confirmation.reference,
            provider="fake_hotel",
            check_in=new_check_in,
            check_out=new_check_out,
            cost_delta_inr=confirmation.cost_delta_inr,
        )


def test_clean_date_shift_succeeds():
    provider = FakeHotelProvider(
        cancel_succeeds=True,
        prebook_succeeds=True,
        book_succeeds=True,
    )
    confirmation = provider.change_dates(
        booking_id="HTL-ORIGINAL-123",
        rate_id="rate_fake_123",
        new_check_in=date(2026, 9, 21),
        new_check_out=date(2026, 9, 25),
        guest="Priya Sharma",
    )

    assert provider.cancelled_bookings == ["HTL-ORIGINAL-123"]
    assert provider.prebooked_rates == ["rate_fake_123"]
    assert len(provider.confirmed_bookings) == 1
    assert confirmation.check_in == date(2026, 9, 21)
    assert confirmation.check_out == date(2026, 9, 25)
    assert confirmation.reference.startswith("BK_")


def test_cancel_fails_nothing_lost():
    provider = FakeHotelProvider(
        cancel_succeeds=False,
        prebook_succeeds=True,
        book_succeeds=True,
    )

    with pytest.raises(RuntimeError, match="existing reservation retained"):
        provider.change_dates(
            booking_id="HTL-ORIGINAL-123",
            rate_id="rate_fake_123",
            new_check_in=date(2026, 9, 21),
            new_check_out=date(2026, 9, 25),
            guest="Priya Sharma",
        )

    # Nothing should have been prebooked or booked
    assert provider.cancelled_bookings == []
    assert provider.prebooked_rates == []
    assert provider.confirmed_bookings == []


def test_rebook_fails_after_successful_cancel_reports_dangerous_failure():
    provider = FakeHotelProvider(
        cancel_succeeds=True,
        prebook_succeeds=True,
        book_succeeds=False,
    )

    with pytest.raises(RuntimeError, match="traveller has a flight and no room"):
        provider.change_dates(
            booking_id="HTL-ORIGINAL-123",
            rate_id="rate_fake_123",
            new_check_in=date(2026, 9, 21),
            new_check_out=date(2026, 9, 25),
            guest="Priya Sharma",
        )

    # Cancel did happen, but rebooking failed
    assert provider.cancelled_bookings == ["HTL-ORIGINAL-123"]
    assert provider.prebooked_rates == ["rate_fake_123"]
    assert provider.confirmed_bookings == []


def test_nuitee_provider_change_dates_clean():
    import httpx

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "DELETE" and "/bookings/HTL-EXISTING" in str(request.url):
            return httpx.Response(200, json={"data": {"status": "CANCELLED"}})
        if request.method == "POST" and "/bookings/prebook" in str(request.url):
            return httpx.Response(200, json={"data": {"prebookId": "PRE-NUI-1"}})
        if request.method == "POST" and "/bookings/book" in str(request.url):
            return httpx.Response(
                200,
                json={
                    "data": {
                        "bookingId": "BK-NUI-NEW",
                        "checkin": "2026-09-21",
                        "checkout": "2026-09-25",
                    }
                },
            )
        return httpx.Response(404)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    nuitee = NuiteeHotelProvider(api_key="sand_key", client=client)

    confirmation = nuitee.change_dates(
        booking_id="HTL-EXISTING",
        rate_id="rate_xyz",
        new_check_in=date(2026, 9, 21),
        new_check_out=date(2026, 9, 25),
        guest="Priya Sharma",
    )
    assert confirmation.reference == "BK-NUI-NEW"
    assert confirmation.check_in == date(2026, 9, 21)
    assert confirmation.check_out == date(2026, 9, 25)
