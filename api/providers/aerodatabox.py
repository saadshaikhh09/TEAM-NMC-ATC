"""AeroDataBox status adapter for the RapidAPI single-day flight endpoint."""

from __future__ import annotations

from datetime import date, datetime

import httpx

from core import quota
from providers.base import BookingConfirmation, FlightOption, FlightProvider, FlightStatus
from providers.status_map import normalise
from providers.status_utils import config_value, flight_key, parse_utc


class AeroDataBoxProvider(FlightProvider):
    def __init__(
        self,
        *,
        api_key: str | None = None,
        host: str | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else config_value("AERODATABOX_API_KEY")
        self.host = host or config_value("AERODATABOX_HOST", "aerodatabox.p.rapidapi.com")
        self.client = client

    def get_status(self, carrier: str, flight_number: str, on: date) -> FlightStatus:
        if not self.api_key:
            raise ValueError("AERODATABOX_API_KEY is not configured")
        if flight_key(flight_number)[: len(carrier)] != carrier.upper():
            raise ValueError("flight number does not match carrier")

        # The current RapidAPI OpenAPI spec uses this path and returns an array.
        url = f"https://{self.host}/flights/Number/{flight_key(flight_number)}/{on.isoformat()}"
        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.host,
        }
        quota.spend("aerodatabox")
        try:
            if self.client is None:
                with httpx.Client(timeout=6.0) as client:
                    response = client.get(url, headers=headers, params={"dateLocalRole": "Departure"})
            else:
                response = self.client.get(url, headers=headers, params={"dateLocalRole": "Departure"})
        except httpx.HTTPError as exc:
            raise RuntimeError("AeroDataBox status request failed") from exc
        if response.status_code == 204:
            raise LookupError("AeroDataBox returned no flight for that date")
        if response.status_code == 403:
            raise RuntimeError("AeroDataBox endpoint is unavailable on this plan")
        if response.status_code != 200:
            raise RuntimeError(f"AeroDataBox returned HTTP {response.status_code}")

        rows = response.json()
        if not isinstance(rows, list):
            raise ValueError("AeroDataBox returned an unexpected response shape")
        matches = [row for row in rows if flight_key(str(row.get("number", ""))) == flight_key(flight_number)]
        if len(matches) != 1:
            raise LookupError(f"expected one AeroDataBox flight, got {len(matches)}")
        row = matches[0]
        departure = row["departure"]
        arrival = row["arrival"]
        return FlightStatus(
            flight_number=flight_key(str(row["number"])),
            status=normalise("aerodatabox", row["status"]),
            scheduled_departure=parse_utc(departure["scheduledTime"]["utc"], "scheduled departure"),
            estimated_departure=parse_utc(departure["revisedTime"]["utc"], "revised departure")
            if departure.get("revisedTime") else None,
            scheduled_arrival=parse_utc(arrival["scheduledTime"]["utc"], "scheduled arrival"),
            estimated_arrival=parse_utc(arrival["revisedTime"]["utc"], "revised arrival")
            if arrival.get("revisedTime") else None,
            gate=departure.get("gate"),
            terminal=departure.get("terminal"),
        )

    def search(self, origin: str, destination: str, depart_after: datetime,
               cabin: str) -> list[FlightOption]:
        raise NotImplementedError("AeroDataBox provides status only")

    def book(self, option_id: str, passenger: str) -> BookingConfirmation:
        raise NotImplementedError("AeroDataBox provides status only")
