"""AviationStack status cross-check; never automatic primary failover."""

from __future__ import annotations

from datetime import date, datetime

import httpx

from core import quota
from providers.base import BookingConfirmation, FlightOption, FlightProvider, FlightStatus
from providers.status_map import normalise
from providers.status_utils import config_value, flight_key, parse_utc


class AviationStackProvider(FlightProvider):
    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else config_value("AVIATIONSTACK_API_KEY")
        configured = base_url or config_value("AVIATIONSTACK_BASE", "https://api.aviationstack.com/v1")
        # Current AviationStack plans support HTTPS. Never put a key on HTTP.
        self.base_url = configured.replace("http://", "https://", 1).rstrip("/")
        if not self.base_url.startswith("https://"):
            raise ValueError("AVIATIONSTACK_BASE must be an HTTPS URL")
        self.client = client

    def get_status(self, carrier: str, flight_number: str, on: date) -> FlightStatus:
        if not self.api_key:
            raise ValueError("AVIATIONSTACK_API_KEY is not configured")
        if flight_key(flight_number)[: len(carrier)] != carrier.upper():
            raise ValueError("flight number does not match carrier")
        params = {
            "access_key": self.api_key,
            "flight_iata": flight_key(flight_number),
        }
        quota.spend("aviationstack")
        try:
            if self.client is None:
                with httpx.Client(timeout=6.0) as client:
                    response = client.get(f"{self.base_url}/flights", params=params)
            else:
                response = self.client.get(f"{self.base_url}/flights", params=params)
        except httpx.HTTPError:
            # The request URL contains access_key. Do not chain the exception.
            raise RuntimeError("AviationStack status request failed") from None
        if response.status_code != 200:
            raise RuntimeError(f"AviationStack returned HTTP {response.status_code}")

        payload = response.json()
        if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
            raise ValueError("AviationStack returned an unexpected response shape")
        matches = [
            row for row in payload["data"]
            if flight_key(str((row.get("flight") or {}).get("iata") or "")) == flight_key(flight_number)
            and row.get("flight_date") == on.isoformat()
        ]
        if len(matches) != 1:
            raise LookupError(f"expected one AviationStack flight on {on}, got {len(matches)}")

        row = matches[0]
        departure = row["departure"]
        arrival = row["arrival"]
        status = normalise("aviationstack", row["flight_status"])
        if status == "SCHEDULED" and (departure.get("delay") or 0) > 0:
            status = "DELAYED"
        return FlightStatus(
            flight_number=flight_key(str(row["flight"]["iata"])),
            status=status,
            scheduled_departure=parse_utc(departure["scheduled"], "scheduled departure"),
            estimated_departure=parse_utc(departure["estimated"], "estimated departure")
            if departure.get("estimated") else None,
            scheduled_arrival=parse_utc(arrival["scheduled"], "scheduled arrival"),
            estimated_arrival=parse_utc(arrival["estimated"], "estimated arrival")
            if arrival.get("estimated") else None,
            gate=departure.get("gate"),
            terminal=departure.get("terminal"),
        )

    def search(self, origin: str, destination: str, depart_after: datetime,
               cabin: str) -> list[FlightOption]:
        raise NotImplementedError("AviationStack provides status only")

    def book(self, option_id: str, passenger: str) -> BookingConfirmation:
        raise NotImplementedError("AviationStack provides status only")
