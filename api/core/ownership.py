"""Shared ownership filters for every private data path."""

from sqlalchemy import select

from core.models import Disruption, Flight, RecoveryPlan, Traveller, Trip


def trips_for(user_id):
    return select(Trip).join(Traveller).where(Traveller.user_id == user_id)


def flights_for(user_id):
    return select(Flight).join(Trip).join(Traveller).where(Traveller.user_id == user_id)


def plans_for(user_id):
    return (
        select(RecoveryPlan)
        .join(Disruption)
        .join(Trip)
        .join(Traveller)
        .where(Traveller.user_id == user_id)
    )
