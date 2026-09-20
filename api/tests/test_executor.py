from datetime import date, datetime, timezone
from uuid import UUID

import pytest
from sqlalchemy import delete, or_, select

from core.audit import record
from core.db import SessionLocal
from core.models import (
    AgentAction,
    Disruption,
    Flight,
    Hotel,
    HotelChange,
    PlanOption,
    PlanRejection,
    RecoveryPlan,
    Trip,
)
from executor.run import run
from providers.base import (
    BookingConfirmation,
    FlightProvider,
    FlightStatus,
    HotelConfirmation,
    HotelOption,
    HotelProvider,
)


PRIYA_TRIP_ID = UUID("aaaaaaaa-1111-1111-1111-111111111111")


class FakeFlightProvider(FlightProvider):
    def __init__(self, trace, *, fail=False):
        self.trace = trace
        self.fail = fail

    def get_status(self, carrier, flight_number, on) -> FlightStatus:
        raise AssertionError("status must not run during execution")

    def search(self, origin, destination, depart_after, cabin):
        raise AssertionError("search must not run during execution")

    def book(self, option_id, passenger):
        self.trace.append("flight.book")
        if self.fail:
            raise RuntimeError("flight provider unavailable")
        return BookingConfirmation("BOOK-123", "fake-flight", 52_400)


class FakeHotelProvider(HotelProvider):
    def __init__(self, trace, *, fail=False):
        self.trace = trace
        self.fail = fail

    def search(self, city, check_in, check_out):
        self.trace.append("hotel.search")
        return [HotelOption("hotel-1", "rate-1", "Kensington Central", city, 9_800)]

    def prebook(self, rate_id):
        raise AssertionError("run delegates the lifecycle to change_dates")

    def book(self, prebook_id, guest):
        raise AssertionError("run delegates the lifecycle to change_dates")

    def cancel(self, booking_id):
        raise AssertionError("run delegates the lifecycle to change_dates")

    def change_dates(self, booking_id, rate_id, new_check_in, new_check_out, guest):
        self.trace.append("hotel.change_dates")
        if self.fail:
            raise RuntimeError("hotel rebook failed")
        return HotelConfirmation(
            "HOTEL-456",
            "fake-hotel",
            new_check_in,
            new_check_out,
            -9_800,
        )


@pytest.fixture
def execution_plan():
    session = SessionLocal()
    trip = session.get(Trip, PRIYA_TRIP_ID)
    trip.status = "EXECUTING"
    session.commit()
    planning = record(session, trip.id, "PLANNING", "Planning recovery")
    planning_id = planning.id
    flight = session.scalar(
        select(Flight).where(Flight.trip_id == trip.id, Flight.leg == "outbound")
    )
    hotel = session.scalar(select(Hotel).where(Hotel.trip_id == trip.id))
    hotel_id = hotel.id
    original_hotel = (
        hotel.provider,
        hotel.confirmation_number,
        hotel.check_in,
        hotel.check_out,
    )
    disruption = Disruption(
        trip_id=trip.id,
        flight_id=flight.id,
        kind="CANCELLATION",
        source="simulated",
        previous_status="SCHEDULED",
        new_status="CANCELLED",
    )
    plan = RecoveryPlan(
        disruption=disruption,
        state="APPROVED",
        evaluated_count=2,
        chosen_option_id="opt_1",
        total_cost_delta_inr=4_200,
        requires_approval=False,
        options=[
            PlanOption(
                option_id="opt_1",
                carrier="BA",
                flight_number="BA138",
                departure=datetime(2026, 9, 20, 8, 10, tzinfo=timezone.utc),
                arrival=datetime(2026, 9, 20, 18, 5, tzinfo=timezone.utc),
                stops=0,
                cabin="economy",
                fare_inr=52_400,
                score=0.1,
                rank=1,
            ),
            PlanOption(
                option_id="opt_2",
                carrier="AI",
                flight_number="AI129",
                departure=datetime(2026, 9, 20, 4, 30, tzinfo=timezone.utc),
                arrival=datetime(2026, 9, 20, 14, 40, tzinfo=timezone.utc),
                stops=0,
                cabin="economy",
                fare_inr=61_500,
                score=0.2,
                rank=2,
            ),
        ],
        rejections=[
            PlanRejection(
                option_id="opt_4",
                rule="hard_arrival_by",
                human_reason="Arrives 11:40, misses hard deadline 09:00",
                note="would have been 8,000 cheaper",
            )
        ],
        hotel_changes=[
            HotelChange(
                hotel=hotel,
                required=True,
                new_check_in=date(2026, 9, 21),
                new_check_out=date(2026, 9, 25),
                cost_delta_inr=-9_800,
            )
        ],
    )

    try:
        yield session, plan, planning_id
    finally:
        session.rollback()
        plan_id = plan.id
        disruption_id = disruption.id
        session.close()
        with SessionLocal.begin() as cleanup:
            cleanup.execute(delete(Flight).where(
                Flight.trip_id == PRIYA_TRIP_ID, Flight.booking_reference == "BOOK-123"
            ))
            cleanup.execute(delete(AgentAction).where(or_(
                AgentAction.id == planning_id,
                AgentAction.plan_id == plan_id,
            )))
            if plan_id is not None:
                cleanup.execute(delete(RecoveryPlan).where(RecoveryPlan.id == plan_id))
            if disruption_id is not None:
                cleanup.execute(delete(Disruption).where(Disruption.id == disruption_id))
            stored_hotel = cleanup.get(Hotel, hotel_id)
            (
                stored_hotel.provider,
                stored_hotel.confirmation_number,
                stored_hotel.check_in,
                stored_hotel.check_out,
            ) = original_hotel
            cleanup.get(Trip, PRIYA_TRIP_ID).status = "MONITORING"


def stages(session, plan, planning_id):
    return session.scalars(
        select(AgentAction.stage)
        .where(or_(AgentAction.id == planning_id, AgentAction.plan_id == plan.id))
        .order_by(AgentAction.at, AgentAction.id)
    ).all()


def test_happy_path_persists_plan_and_writes_all_five_stages(execution_plan):
    session, plan, planning_id = execution_plan
    trace = []

    result = run(
        session,
        plan,
        FakeFlightProvider(trace),
        FakeHotelProvider(trace),
    )

    assert result["ok"] is True
    assert trace == ["flight.book", "hotel.search", "hotel.change_dates"]
    assert stages(session, plan, planning_id) == [
        "PLANNING",
        "APPROVED",
        "REBOOKED",
        "HOTEL_SHIFTED",
        "NOTIFIED",
    ]
    session.expire_all()
    stored = session.get(RecoveryPlan, plan.id)
    assert stored.state == "EXECUTED"
    assert [(item.option_id, item.rank) for item in stored.options] == [
        ("opt_1", 1),
        ("opt_2", 2),
    ]
    assert len(stored.rejections) == 1
    assert stored.hotel_changes[0].executed is True
    assert session.get(Trip, PRIYA_TRIP_ID).status == "RECOVERED"
    assert session.scalar(select(Flight).where(
        Flight.trip_id == PRIYA_TRIP_ID, Flight.booking_reference == "BOOK-123"
    )) is not None


def test_flight_failure_records_failed_without_rebooked(execution_plan):
    session, plan, planning_id = execution_plan
    trace = []

    result = run(
        session,
        plan,
        FakeFlightProvider(trace, fail=True),
        FakeHotelProvider(trace),
    )

    assert result == {"ok": False, "error": "Flight rebooking failed: flight provider unavailable"}
    assert trace == ["flight.book"]
    assert stages(session, plan, planning_id) == ["PLANNING", "APPROVED", "FAILED"]
    assert session.get(Trip, PRIYA_TRIP_ID).status == "RECOVERY_FAILED"


def test_hotel_failure_records_rebooked_then_failed_without_hotel_shifted(execution_plan):
    session, plan, planning_id = execution_plan
    trace = []

    result = run(
        session,
        plan,
        FakeFlightProvider(trace),
        FakeHotelProvider(trace, fail=True),
    )

    assert result["ok"] is False
    assert "flight and no room" in result["error"]
    assert trace == ["flight.book", "hotel.search", "hotel.change_dates"]
    assert stages(session, plan, planning_id) == [
        "PLANNING",
        "APPROVED",
        "REBOOKED",
        "FAILED",
    ]
    assert session.get(Trip, PRIYA_TRIP_ID).status == "RECOVERY_FAILED"
