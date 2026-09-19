"""Hotel search + REAL sandbox booking lifecycle. Owner: Person D.

    GET    /hotels/search          find
    GET    /hotels/rates           rates for a property
    POST   /bookings/prebook       hold          -> prebook_id
    POST   /bookings/book          confirm       -> booking_id
    GET    /bookings/{id}          retrieve
    DELETE /bookings/{id}          cancel

Header: X-API-Key: sand_...
"""

from __future__ import annotations

from datetime import date
from typing import Any

import httpx

from providers.base import HotelConfirmation, HotelOption, HotelProvider
from providers.status_utils import config_value


class NuiteeHotelProvider(HotelProvider):
    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else config_value("NUITEE_API_KEY")
        self.base_url = (base_url or config_value("NUITEE_BASE", "https://api.liteapi.travel/v3.0")).rstrip("/")
        self.client = client

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> httpx.Response:
        url = f"{self.base_url}{path}"
        headers = self._headers()
        try:
            if self.client is not None:
                return self.client.request(method, url, headers=headers, params=params, json=json)
            with httpx.Client(timeout=10.0) as client:
                return client.request(method, url, headers=headers, params=params, json=json)
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Nuitee request {method} {path} failed") from exc

    def search(self, city: str, check_in: date, check_out: date) -> list[HotelOption]:
        if check_out <= check_in:
            raise ValueError("check_out must be after check_in")
        if not city.strip():
            raise ValueError("city is required")

        response = self._request(
            "GET",
            "/hotels/rates",
            params={
                "cityName": city,
                "checkin": check_in.isoformat(),
                "checkout": check_out.isoformat(),
                "currency": "INR",
                "guestNationality": "IN",
                "adults": 1,
            },
        )
        if response.status_code != 200:
            raise RuntimeError(f"Nuitee hotel search returned HTTP {response.status_code}")

        payload = response.json()
        data = payload.get("data", payload)
        hotels = data if isinstance(data, list) else data.get("hotels", [])

        options: list[HotelOption] = []
        for hotel in hotels:
            hotel_id = str(hotel.get("hotelId") or hotel.get("id", ""))
            name = str(hotel.get("name") or hotel.get("hotelName", "Hotel"))
            rates = hotel.get("rates") or hotel.get("roomTypes", [])
            for rate in rates:
                rate_id = str(rate.get("rateId") or rate.get("id", ""))
                nightly_price = int(
                    rate.get("retailRate", {}).get("total", {}).get("amount")
                    or rate.get("nightlyRate")
                    or rate.get("price", 0)
                )
                if rate_id:
                    options.append(
                        HotelOption(
                            id=hotel_id,
                            rate_id=rate_id,
                            name=name,
                            city=city.upper(),
                            nightly_rate_inr=nightly_price,
                        )
                    )
        return options

    def prebook(self, rate_id: str) -> str:
        if not rate_id.strip():
            raise ValueError("rate_id is required")

        response = self._request(
            "POST",
            "/bookings/prebook",
            json={"rateId": rate_id},
        )
        if response.status_code == 409:
            raise RuntimeError("Room rate expired or unavailable (409 Conflict)")
        if response.status_code not in (200, 201):
            raise RuntimeError(f"Nuitee prebook returned HTTP {response.status_code}")

        payload = response.json()
        data = payload.get("data", payload)
        prebook_id = str(data.get("prebookId") or data.get("id", ""))
        if not prebook_id:
            raise ValueError("Nuitee prebook response missing prebookId")
        return prebook_id

    def book(self, prebook_id: str, guest: str) -> HotelConfirmation:
        if not prebook_id.strip():
            raise ValueError("prebook_id is required")
        if not guest.strip():
            raise ValueError("guest is required")

        parts = guest.strip().split(maxsplit=1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else "Guest"

        response = self._request(
            "POST",
            "/bookings/book",
            json={
                "prebookId": prebook_id,
                "guest": {
                    "firstName": first_name,
                    "lastName": last_name,
                    "email": "concierge@travel.internal",
                },
            },
        )
        if response.status_code == 409:
            raise RuntimeError("Room rate expired or unavailable during booking (409 Conflict)")
        if response.status_code not in (200, 201):
            raise RuntimeError(f"Nuitee booking returned HTTP {response.status_code}")

        payload = response.json()
        data = payload.get("data", payload)
        reference = str(
            data.get("bookingId")
            or data.get("bookingReference")
            or data.get("reference")
            or data.get("id", "")
        )
        check_in_str = data.get("checkin") or data.get("check_in")
        check_out_str = data.get("checkout") or data.get("check_out")

        check_in = date.fromisoformat(check_in_str) if check_in_str else date.today()
        check_out = date.fromisoformat(check_out_str) if check_out_str else date.today()

        return HotelConfirmation(
            reference=reference,
            provider="nuitee",
            check_in=check_in,
            check_out=check_out,
            cost_delta_inr=0,
        )

    def cancel(self, booking_id: str) -> bool:
        if not booking_id.strip():
            raise ValueError("booking_id is required")

        response = self._request("DELETE", f"/bookings/{booking_id}")
        if response.status_code in (200, 204):
            return True
        if response.status_code == 404:
            return False
        payload = response.json()
        status = payload.get("data", {}).get("status", "")
        if status.upper() in ("CANCELLED", "CANCELED", "SUCCESS"):
            return True
        return False

    def change_dates(
        self,
        booking_id: str,
        rate_id: str,
        new_check_in: date,
        new_check_out: date,
        guest: str,
    ) -> HotelConfirmation:
        """Cancel then rebook in order.

        If cancel fails: existing reservation is retained.
        If rebook fails after cancel: raises explicit error that traveller has no room.
        """
        cancelled = self.cancel(booking_id)
        if not cancelled:
            raise RuntimeError(f"Hotel cancellation failed for {booking_id}; existing reservation retained")

        prebook_id = self.prebook(rate_id)
        try:
            confirmation = self.book(prebook_id, guest)
        except Exception as exc:
            raise RuntimeError(
                f"Hotel cancelled ({booking_id}) but rebook failed — traveller has a flight and no room"
            ) from exc

        return HotelConfirmation(
            reference=confirmation.reference,
            provider="nuitee",
            check_in=new_check_in,
            check_out=new_check_out,
            cost_delta_inr=confirmation.cost_delta_inr,
        )
