from uuid import UUID

import pytest

from core.audit import record
from core.db import SessionLocal
from core.events import subscribe
from core.models import AgentAction


PRIYA_TRIP_ID = UUID("aaaaaaaa-1111-1111-1111-111111111111")


def test_record_writes_one_row_and_emits_after_commit():
    session = SessionLocal()
    events = []
    subscribe("action.recorded", events.append)
    before = session.query(AgentAction).count()

    try:
        action = record(session, PRIYA_TRIP_ID, "PLANNING", "Planning recovery")

        assert session.query(AgentAction).count() == before + 1
        assert action.detail == {}
        assert events == [
            {
                "trip_id": str(PRIYA_TRIP_ID),
                "payload": {"action_id": str(action.id)},
            }
        ]
    finally:
        session.rollback()
        if "action" in locals():
            session.delete(action)
            session.commit()
        session.close()


def test_record_rejects_unknown_stage():
    session = SessionLocal()
    try:
        with pytest.raises(ValueError, match="UNKNOWN"):
            record(session, PRIYA_TRIP_ID, "UNKNOWN", "Never written")
    finally:
        session.close()
