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


def local_time(dt: datetime, iata: str) -> datetime:
    return dt.astimezone(ZoneInfo(TIMEZONES[iata]))


def local_str(dt: datetime, iata: str) -> str:
    return local_time(dt, iata).strftime("%H:%M, %d %b")
