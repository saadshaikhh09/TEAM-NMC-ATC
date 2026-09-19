"""Paste-a-booking-email -> structured trip JSON. Owner: Person A.

Replaces Gmail OAuth ingestion. Same extraction moment, no consent screen,
no scope review, nothing to break on stage. Always schema-validate the output
before it touches the database.
"""

import json

from pydantic import ValidationError

from llm import client


class ExtractionError(ValueError):
    pass


def extract(pasted_booking_text: str):
    """Return a fully validated CONTRACT Trip or raise a user-facing failure."""
    from routes.trips import Trip

    if not pasted_booking_text.strip():
        raise ExtractionError("Booking text is empty; enter the trip manually.")

    response = client.ask(
        "Extract the booking into the supplied Trip schema. Return JSON only; do not "
        "invent missing required values.",
        f"Trip schema: {json.dumps(Trip.model_json_schema())}\n\n"
        f"Booking text:\n{pasted_booking_text}",
    )
    if response is None:
        raise ExtractionError(
            "Booking extraction is unavailable; enter the complete trip manually."
        )

    try:
        trip = Trip.model_validate_json(response)
    except (ValidationError, ValueError) as exc:
        raise ExtractionError(
            "Booking extraction did not produce a complete trip; enter it manually."
        ) from exc
    if not trip.flights:
        raise ExtractionError(
            "Booking extraction did not include a flight; enter the trip manually."
        )
    return trip
