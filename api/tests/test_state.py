from uuid import UUID

import pytest

from core.db import SessionLocal
from core.models import Trip
from core.state_machine import advance, can


PRIYA_TRIP_ID = UUID("aaaaaaaa-1111-1111-1111-111111111111")


def test_legal_transitions():
    assert can("MONITORING", "DISRUPTED")
    assert can("PLANNING", "AWAITING_APPROVAL")
    assert not can("MONITORING", "EXECUTING")
    assert not can("RECOVERED", "EXECUTING")
    assert can("DISRUPTED", "RECOVERY_FAILED")
    for early_state in ("PLANNING", "AWAITING_APPROVAL", "EXECUTING"):
        assert can(early_state, "RECOVERY_FAILED")


def test_advance_commits_legal_transition():
    session = SessionLocal()
    trip = session.get(Trip, PRIYA_TRIP_ID)
    before = trip.updated_at

    try:
        result = advance(session, PRIYA_TRIP_ID, "DISRUPTED")

        assert result.status == "DISRUPTED"
        assert result.updated_at > before
        session.expire_all()
        assert session.get(Trip, PRIYA_TRIP_ID).status == "DISRUPTED"
    finally:
        session.rollback()
        trip = session.get(Trip, PRIYA_TRIP_ID)
        trip.status = "MONITORING"
        session.commit()
        session.close()


def test_advance_rejects_illegal_transition_with_both_states():
    session = SessionLocal()
    try:
        with pytest.raises(ValueError, match="MONITORING.*EXECUTING"):
            advance(session, PRIYA_TRIP_ID, "EXECUTING")
        assert session.get(Trip, PRIYA_TRIP_ID).status == "MONITORING"
    finally:
        session.close()
