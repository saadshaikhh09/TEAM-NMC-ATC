"""SQLAlchemy models. Owner: Person A. Mirrors db/schema.sql exactly.

If you change this file, change schema.sql in the same commit.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKey, Integer, Numeric, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class LlmCache(Base):
    __tablename__ = "responses"
    __table_args__ = {"schema": "llm_cache"}

    cache_key: Mapped[str] = mapped_column(Text, primary_key=True)
    response: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    email: Mapped[str] = mapped_column(Text, unique=True)
    name: Mapped[str] = mapped_column(Text)
    password_hash: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )

    sessions: Mapped[list[UserSession]] = relationship(back_populates="user")
    travellers: Mapped[list[Traveller]] = relationship(back_populates="user")


class UserSession(Base):
    __tablename__ = "sessions"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    token_hash: Mapped[str] = mapped_column(Text, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )

    user: Mapped[User] = relationship(back_populates="sessions")


class Traveller(Base):
    __tablename__ = "travellers"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(Text)
    email: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )

    user: Mapped[User] = relationship(back_populates="travellers")
    constraints: Mapped[TravellerConstraint | None] = relationship(
        back_populates="traveller"
    )
    trips: Mapped[list[Trip]] = relationship(back_populates="traveller")


class TravellerConstraint(Base):
    __tablename__ = "traveller_constraints"

    traveller_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("travellers.id", ondelete="CASCADE"),
        primary_key=True,
    )
    hard_arrival_by: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    hard_arrival_timezone: Mapped[str | None] = mapped_column(Text)
    hard_arrival_reason: Mapped[str | None] = mapped_column(Text)
    max_fare_inr: Mapped[int | None] = mapped_column(Integer)
    max_stops: Mapped[int | None] = mapped_column(Integer, server_default=text("1"))
    cabin: Mapped[str | None] = mapped_column(Text, server_default=text("'economy'"))
    avoid_carriers: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text), server_default=text("'{}'::text[]")
    )
    auto_approve_under_inr: Mapped[int | None] = mapped_column(Integer)

    traveller: Mapped[Traveller] = relationship(back_populates="constraints")


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    traveller_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("travellers.id", ondelete="CASCADE")
    )
    status: Mapped[str] = mapped_column(Text, server_default=text("'CREATED'"))
    origin: Mapped[str] = mapped_column(Text)
    destination: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )

    traveller: Mapped[Traveller] = relationship(back_populates="trips")
    flights: Mapped[list[Flight]] = relationship(back_populates="trip")
    hotels: Mapped[list[Hotel]] = relationship(back_populates="trip")
    disruptions: Mapped[list[Disruption]] = relationship(back_populates="trip")
    actions: Mapped[list[AgentAction]] = relationship(back_populates="trip")


class Flight(Base):
    __tablename__ = "flights"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    trip_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE")
    )
    leg: Mapped[str] = mapped_column(Text, server_default=text("'outbound'"))
    carrier: Mapped[str] = mapped_column(Text)
    flight_number: Mapped[str] = mapped_column(Text)
    origin: Mapped[str] = mapped_column(Text)
    destination: Mapped[str] = mapped_column(Text)
    origin_timezone: Mapped[str | None] = mapped_column(Text)
    destination_timezone: Mapped[str | None] = mapped_column(Text)
    scheduled_departure: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    scheduled_arrival: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(Text, server_default=text("'SCHEDULED'"))
    booking_reference: Mapped[str | None] = mapped_column(Text)
    fare_inr: Mapped[int | None] = mapped_column(Integer)
    cabin: Mapped[str | None] = mapped_column(Text, server_default=text("'economy'"))
    next_poll_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_polled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    trip: Mapped[Trip] = relationship(back_populates="flights")
    disruptions: Mapped[list[Disruption]] = relationship(back_populates="flight")


class Hotel(Base):
    __tablename__ = "hotels"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    trip_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE")
    )
    provider: Mapped[str] = mapped_column(Text, server_default=text("'mock'"))
    confirmation_number: Mapped[str | None] = mapped_column(Text)
    name: Mapped[str] = mapped_column(Text)
    city: Mapped[str] = mapped_column(Text)
    city_timezone: Mapped[str | None] = mapped_column(Text)
    check_in: Mapped[date] = mapped_column(Date)
    check_out: Mapped[date] = mapped_column(Date)
    nightly_rate_inr: Mapped[int | None] = mapped_column(Integer)
    modifiable: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
    status: Mapped[str] = mapped_column(Text, server_default=text("'CONFIRMED'"))

    trip: Mapped[Trip] = relationship(back_populates="hotels")
    changes: Mapped[list[HotelChange]] = relationship(back_populates="hotel")


class Disruption(Base):
    __tablename__ = "disruptions"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    trip_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE")
    )
    flight_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("flights.id", ondelete="CASCADE")
    )
    kind: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(Text)
    previous_status: Mapped[str | None] = mapped_column(Text)
    new_status: Mapped[str | None] = mapped_column(Text)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )

    trip: Mapped[Trip] = relationship(back_populates="disruptions")
    flight: Mapped[Flight] = relationship(back_populates="disruptions")
    plans: Mapped[list[RecoveryPlan]] = relationship(back_populates="disruption")


class RecoveryPlan(Base):
    __tablename__ = "recovery_plans"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    disruption_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("disruptions.id", ondelete="CASCADE")
    )
    state: Mapped[str] = mapped_column(Text, server_default=text("'DRAFT'"))
    evaluated_count: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    chosen_option_id: Mapped[str | None] = mapped_column(Text)
    total_cost_delta_inr: Mapped[int | None] = mapped_column(Integer)
    requires_approval: Mapped[bool] = mapped_column(
        Boolean, server_default=text("true")
    )
    approval_reason: Mapped[str | None] = mapped_column(Text)
    explanation: Mapped[str | None] = mapped_column(Text)
    member_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )

    disruption: Mapped[Disruption] = relationship(back_populates="plans")
    options: Mapped[list[PlanOption]] = relationship(back_populates="plan")
    rejections: Mapped[list[PlanRejection]] = relationship(back_populates="plan")
    hotel_changes: Mapped[list[HotelChange]] = relationship(back_populates="plan")
    approvals: Mapped[list[Approval]] = relationship(back_populates="plan")
    actions: Mapped[list[AgentAction]] = relationship(back_populates="plan")


class PlanOption(Base):
    __tablename__ = "plan_options"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    plan_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("recovery_plans.id", ondelete="CASCADE")
    )
    option_id: Mapped[str] = mapped_column(Text)
    carrier: Mapped[str | None] = mapped_column(Text)
    flight_number: Mapped[str | None] = mapped_column(Text)
    departure: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    arrival: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    stops: Mapped[int | None] = mapped_column(Integer)
    cabin: Mapped[str | None] = mapped_column(Text)
    fare_inr: Mapped[int | None] = mapped_column(Integer)
    score: Mapped[Decimal | None] = mapped_column(Numeric)
    rank: Mapped[int | None] = mapped_column(Integer)

    plan: Mapped[RecoveryPlan] = relationship(back_populates="options")


class PlanRejection(Base):
    __tablename__ = "plan_rejections"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    plan_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("recovery_plans.id", ondelete="CASCADE")
    )
    option_id: Mapped[str] = mapped_column(Text)
    rule: Mapped[str] = mapped_column(Text)
    human_reason: Mapped[str] = mapped_column(Text)
    note: Mapped[str | None] = mapped_column(Text)

    plan: Mapped[RecoveryPlan] = relationship(back_populates="rejections")


class HotelChange(Base):
    __tablename__ = "hotel_changes"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    plan_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("recovery_plans.id", ondelete="CASCADE")
    )
    hotel_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("hotels.id", ondelete="CASCADE")
    )
    required: Mapped[bool] = mapped_column(Boolean)
    new_check_in: Mapped[date | None] = mapped_column(Date)
    new_check_out: Mapped[date | None] = mapped_column(Date)
    cost_delta_inr: Mapped[int | None] = mapped_column(Integer)
    executed: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))

    plan: Mapped[RecoveryPlan] = relationship(back_populates="hotel_changes")
    hotel: Mapped[Hotel] = relationship(back_populates="changes")


class Approval(Base):
    __tablename__ = "approvals"
    __table_args__ = (
        UniqueConstraint("plan_id", name="uq_approvals_plan_id"),
        CheckConstraint("decision IN ('APPROVED', 'REJECTED')", name="ck_approvals_decision"),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    plan_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("recovery_plans.id", ondelete="CASCADE")
    )
    decision: Mapped[str] = mapped_column(Text)
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )

    plan: Mapped[RecoveryPlan] = relationship(back_populates="approvals")


class AgentAction(Base):
    __tablename__ = "agent_actions"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    trip_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE")
    )
    plan_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("recovery_plans.id", ondelete="SET NULL")
    )
    stage: Mapped[str] = mapped_column(Text)
    headline: Mapped[str] = mapped_column(Text)
    detail: Mapped[dict[str, Any]] = mapped_column(
        JSONB, server_default=text("'{}'::jsonb")
    )
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )

    trip: Mapped[Trip] = relationship(back_populates="actions")
    plan: Mapped[RecoveryPlan | None] = relationship(back_populates="actions")
