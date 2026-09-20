"""Best-effort hotel geocoding through OpenStreetMap Nominatim."""

from __future__ import annotations

import json
import math
import threading
import time
from urllib import parse, request


_request_lock = threading.Lock()
_last_request_at = 0.0


def geocode_hotel(name: str, city: str, address: str | None) -> tuple[float, float] | None:
    global _last_request_at
    query = ", ".join(part.strip() for part in (name, address, city) if part and part.strip())
    url = "https://nominatim.openstreetmap.org/search?" + parse.urlencode(
        {"format": "jsonv2", "limit": 1, "q": query}
    )
    lookup = request.Request(
        url,
        headers={"User-Agent": "AeroConcierge/1.0 (hotel map lookup)"},
    )
    try:
        # ponytail: process-local throttle; use a shared limiter if this API runs multiple workers.
        with _request_lock:
            remaining = 1 - (time.monotonic() - _last_request_at)
            if remaining > 0:
                time.sleep(remaining)
            try:
                with request.urlopen(lookup, timeout=3) as response:
                    match = json.loads(response.read())[0]
            finally:
                _last_request_at = time.monotonic()
        latitude, longitude = float(match["lat"]), float(match["lon"])
        if not (math.isfinite(latitude) and math.isfinite(longitude)):
            return None
        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            return None
        return latitude, longitude
    except (OSError, TypeError, ValueError, KeyError, IndexError):
        return None
