"""Normalise every provider's status vocabulary into ours. Owner: Person B.

Each provider speaks a different language. The rest of the codebase only ever
sees our five values. Anything unmapped raises — a silent fallthrough is how
you miss a cancellation.

    ours:  SCHEDULED | DELAYED | CANCELLED | DEPARTED | LANDED
"""

AERODATABOX = {
    "Unknown": "SCHEDULED",
    "Expected": "SCHEDULED",
    "CheckIn": "SCHEDULED",
    "Boarding": "SCHEDULED",
    "GateClosed": "SCHEDULED",
    "Delayed": "DELAYED",
    "Departed": "DEPARTED",
    "EnRoute": "DEPARTED",
    "Approaching": "DEPARTED",
    "Landed": "LANDED",
    "Arrived": "LANDED",
    "Cancelled": "CANCELLED",
    "Canceled": "CANCELLED",
    "CanceledUncertain": "CANCELLED",   # treat as cancelled, flag in detail
    "Diverted": "CANCELLED",            # for our purposes: itinerary is broken
}

AVIATIONSTACK = {
    "scheduled": "SCHEDULED",
    "active": "DEPARTED",
    "landed": "LANDED",
    "cancelled": "CANCELLED",
    "incident": "CANCELLED",
    "diverted": "CANCELLED",
}


def normalise(provider: str, raw: str) -> str:
    table = {"aerodatabox": AERODATABOX, "aviationstack": AVIATIONSTACK}[provider]
    if raw not in table:
        raise ValueError(f"unmapped {provider} status {raw!r} — add it to status_map")
    return table[raw]
