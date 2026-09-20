"""Airport-local time formatting."""

from datetime import datetime
from zoneinfo import ZoneInfo


TIMEZONES = {
    "BOM": "Asia/Kolkata",
    "DEL": "Asia/Kolkata",
    "BLR": "Asia/Kolkata",
    "LHR": "Europe/London",
    "LON": "Europe/London",
    "SIN": "Asia/Singapore",
    "DXB": "Asia/Dubai",
}


def timezone_name(code: str, explicit: str | None = None) -> str:
    if explicit:
        try:
            ZoneInfo(explicit)
        except (KeyError, ValueError) as exc:
            raise ValueError(f"Invalid IANA timezone: {explicit}") from exc
        return explicit
    try:
        return TIMEZONES[code.upper()]
    except KeyError as exc:
        raise ValueError(f"An explicit IANA timezone is required for {code.upper()}") from exc


def local_time(dt: datetime, iata: str, explicit: str | None = None) -> datetime:
    return dt.astimezone(ZoneInfo(timezone_name(iata, explicit)))


def local_str(dt: datetime, iata: str, explicit: str | None = None) -> str:
    return local_time(dt, iata, explicit).strftime("%H:%M, %d %b")
