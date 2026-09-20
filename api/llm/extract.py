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
    """Return validated creation input; persistence remains a separate transaction."""
    from core.trip_service import TripInput

    if not pasted_booking_text.strip():
        raise ExtractionError("Booking text is empty; enter the trip manually.")

    response = client.ask(
        "Extract the booking into the supplied Trip schema. Return JSON only; do not "
        "invent missing required values.",
        f"Trip schema: {json.dumps(TripInput.model_json_schema())}\n\n"
        f"Booking text:\n{pasted_booking_text}",
    )
    if response is None:
        raise ExtractionError(
            "Booking extraction is unavailable; enter the complete trip manually."
        )

    try:
        trip = TripInput.model_validate_json(response)
    except (ValidationError, ValueError) as exc:
        raise ExtractionError(
            "Booking extraction did not produce a complete trip; enter it manually."
        ) from exc
    return trip
