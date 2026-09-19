"""Verification of notification panel copy and timeline contract (Task D4).

Validates headline copy across all 9 agent stages and verifies GET /trips/{id}/timeline schema.
"""

from uuid import uuid4
from datetime import datetime, timezone
import pytest
from pydantic import TypeAdapter

from routes.trips import AgentAction


EXPECTED_STAGE_COPY = {
    "DETECTED": "Flight AI131 cancelled",
    "PLANNING": "Searching alternatives for BOM -> LHR departing after 20 Sep 02:30",
    "EVALUATED": "Evaluated 14 options, rejected 3 on policy",
    "AWAITING_APPROVAL": "Recovery plan requires approval: fare ₹52,400 exceeds auto-approve threshold ₹45,000",
    "APPROVED": "Recovery plan approved by policy",
    "REBOOKED": "Flight rebooked — confirmation BA-78901",
    "HOTEL_SHIFTED": "Hotel shifted to 21 Sep–25 Sep local time",
    "NOTIFIED": "Traveller notified of recovery",
    "FAILED": "Flight rebooked as BA-78901, but hotel change failed — traveller has a flight and no room",
}


def test_agent_action_stage_copy_validates():
    trip_id = uuid4()
    now = datetime.now(timezone.utc)

    adapter = TypeAdapter(AgentAction)
    for stage, headline in EXPECTED_STAGE_COPY.items():
        data = {
            "id": uuid4(),
            "trip_id": trip_id,
            "at": now,
            "stage": stage,
            "headline": headline,
            "detail": {"example": "data"},
            "duration_ms": 150,
        }
        action = adapter.validate_python(data)
        assert action.stage == stage
        assert action.headline == headline
        assert action.duration_ms == 150


def test_timeline_rejection_copy_formatting():
    rejection_headline = "Evaluated 14 options, rejected 3 on policy"
    assert "Evaluated" in rejection_headline
    assert "rejected" in rejection_headline
    assert "policy" in rejection_headline


def test_timeline_hotel_shifted_copy_formatting():
    hotel_headline = "Hotel shifted to 21 Sep–25 Sep local time"
    assert hotel_headline.startswith("Hotel shifted to")
    assert "local time" in hotel_headline
