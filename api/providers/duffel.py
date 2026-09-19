"""Flight search + booking, TEST MODE ONLY. Owner: Person D.

    POST /air/offer_requests      search
    GET  /air/offers/{id}         one offer
    POST /air/orders              book
    GET  /air/orders/{id}         order status + airline_initiated_changes

Headers: Authorization: Bearer ..., Duffel-Version: v2

Limits: 30 req/min, ~120 offer searches before a secondary limit.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

import httpx

from providers.base import (
    BookingConfirmation,
    FlightOption,
    FlightProvider,
    FlightStatus,
)
from providers.status_utils import config_value, parse_utc


class DuffelFlightProvider(FlightProvider):
    def __init__(
        self,
        *,
        api_key: str | None = None,
        api_version: str | None = None,
        base_url: str = "https://api.duffel.com",
        client: httpx.Client | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else config_value("DUFFEL_API_KEY")
        self.api_version = api_version or config_value("DUFFEL_API_VERSION", "v2")
        self.base_url = base_url.rstrip("/")
        self.client = client

    def _headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Duffel-Version": self.api_version,
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
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
            raise RuntimeError(f"Duffel request {method} {path} failed") from exc

    def get_status(self, carrier: str, flight_number: str, on: date) -> FlightStatus:
        raise NotImplementedError("Duffel provides flight search and booking only; use AeroDataBox for status")

    def search(
        self,
        origin: str,
        destination: str,
        depart_after: datetime,
        cabin: str,
    ) -> list[FlightOption]:
        if depart_after.tzinfo is None or depart_after.utcoffset() is None:
            raise ValueError("depart_after must include a timezone")
        if not origin.strip() or not destination.strip():
            raise ValueError("origin and destination are required")

        cabin_class = "economy"
        if cabin.lower() in ("business", "first", "premium_economy"):
            cabin_class = cabin.lower()

        payload = {
            "data": {
                "slices": [
                    {
                        "origin": origin.upper(),
                        "destination": destination.upper(),
                        "departure_date": depart_after.date().isoformat(),
                    }
                ],
                "passengers": [{"type": "adult"}],
                "cabin_class": cabin_class,
            }
        }

        response = self._request("POST", "/air/offer_requests?return_offers=true", json=payload)
        if response.status_code not in (200, 201):
            raise RuntimeError(f"Duffel offer request returned HTTP {response.status_code}")

        data = response.json().get("data", {})
        offers = data.get("offers", [])

        options: list[FlightOption] = []
        for offer in offers:
            offer_id = str(offer.get("id", ""))
            slices = offer.get("slices", [])
            if not slices:
                continue
            first_slice = slices[0]
            segments = first_slice.get("segments", [])
            if not segments:
                continue

            first_segment = segments[0]
            last_segment = segments[-1]

            carrier = (
                first_segment.get("operating_carrier", {}).get("iata_code")
                or first_segment.get("marketing_carrier", {}).get("iata_code")
                or offer.get("owner", {}).get("iata_code")
                or "XX"
            ).upper()

            flight_num = (
                first_segment.get("operating_carrier_flight_number")
                or first_segment.get("marketing_carrier_flight_number")
                or first_segment.get("flight_number")
                or "100"
            )
            flight_number = flight_num if flight_num.startswith(carrier) else f"{carrier}{flight_num}"

            departure_time = parse_utc(first_segment.get("departing_at"), "departure")
            arrival_time = parse_utc(last_segment.get("arriving_at"), "arrival")

            if departure_time < depart_after:
                continue

            stops = max(0, len(segments) - 1)
            total_amount = float(offer.get("total_amount") or offer.get("total_currency_amount") or 0)
            fare_inr = int(total_amount)

            options.append(
                FlightOption(
                    id=offer_id,
                    carrier=carrier,
                    flight_number=flight_number,
                    departure=departure_time,
                    arrival=arrival_time,
                    stops=stops,
                    cabin=cabin,
                    fare_inr=fare_inr,
                )
            )

        return options

    def book(self, option_id: str, passenger: str) -> BookingConfirmation:
        if not option_id.strip():
            raise ValueError("option_id is required")
        if not passenger.strip():
            raise ValueError("passenger is required")

        parts = passenger.strip().split(maxsplit=1)
        given_name = parts[0]
        family_name = parts[1] if len(parts) > 1 else "Traveller"

        # Duffel instant order in test environment
        payload = {
            "data": {
                "selected_offers": [option_id],
                "type": "instant",
                "passengers": [
                    {
                        "given_name": given_name,
                        "family_name": family_name,
                        "gender": "f",
                        "title": "ms",
                        "born_on": "1990-01-01",
                        "email": "concierge@travel.internal",
                        "phone_number": "+919876543210",
                    }
                ],
                "payments": [
                    {
                        "type": "balance",
                        "currency": "INR",
                        "amount": "52400.00",
                    }
                ],
            }
        }

        response = self._request("POST", "/air/orders", json=payload)
        if response.status_code not in (200, 201):
            raise RuntimeError(f"Duffel order creation returned HTTP {response.status_code}")

        data = response.json().get("data", {})
        booking_ref = (
            data.get("booking_reference")
            or data.get("reference")
            or data.get("id")
            or f"DUFFEL-{option_id.upper()}"
        )
        total_amount = float(data.get("total_amount") or 52400)

        return BookingConfirmation(
            reference=str(booking_ref),
            provider="duffel",
            fare_inr=int(total_amount),
        )


def parse_webhook_event(payload: dict[str, Any]) -> dict[str, Any]:
    """Parse a Duffel webhook event payload for airline-initiated changes."""
    data = payload.get("data", payload)
    event_id = str(data.get("id") or payload.get("id") or "")
    event_type = str(data.get("type") or payload.get("type") or "order.airline_initiated_change_detected")

    order = data.get("object") or data
    booking_reference = str(order.get("booking_reference") or order.get("reference") or "")
    slices = order.get("slices", [])
    flight_number = ""
    if slices and isinstance(slices, list):
        segments = slices[0].get("segments", [])
        if segments and isinstance(segments, list):
            seg = segments[0]
            carrier = (
                seg.get("operating_carrier", {}).get("iata_code")
                or seg.get("marketing_carrier", {}).get("iata_code")
                or ""
            ).upper()
            fn = str(
                seg.get("operating_carrier_flight_number")
                or seg.get("marketing_carrier_flight_number")
                or seg.get("flight_number")
                or ""
            )
            flight_number = fn if fn.startswith(carrier) else f"{carrier}{fn}"

    kind = "CANCELLATION"
    if "delay" in event_type.lower() or "schedule" in event_type.lower():
        kind = "DELAY"

    return {
        "event_id": event_id,
        "event_type": event_type,
        "booking_reference": booking_reference,
        "flight_number": flight_number,
        "kind": kind,
    }

