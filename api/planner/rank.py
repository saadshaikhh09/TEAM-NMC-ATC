"""Deterministic scoring. Owner: Person A.

Runs ONLY on options that survived constraints.filter(). Weights come from
policy.yaml. The LLM never touches this file and never picks the flight.
"""
from dataclasses import dataclass

from providers.base import FlightOption


AXES = (
    "arrival_delay_minutes",
    "fare_delta_inr",
    "hotel_cost_delta_inr",
    "carrier_preference",
)


@dataclass(frozen=True)
class ScoredOption:
    option: FlightOption
    score: float
    rank: int
    raw: dict[str, float]
    components: dict[str, float]


def rank(
    survivors,
    original_flight,
    constraints,
    policy,
    hotel_cost_deltas: dict[str, int] | None = None,
) -> list[ScoredOption]:
    if not survivors:
        return []

    ranking = policy["ranking"]
    preferred = ranking["preferred_carriers"]
    hotel_cost_deltas = hotel_cost_deltas or {}
    rows = []

    for option in survivors:
        delay = max(
            0.0,
            (option.arrival - original_flight.scheduled_arrival).total_seconds() / 60,
        )
        carrier_preference = (
            preferred.index(option.carrier) / len(preferred)
            if option.carrier in preferred
            else 1.0
        )
        rows.append((option, {
            "arrival_delay_minutes": delay,
            "fare_delta_inr": float(option.fare_inr),
            "hotel_cost_delta_inr": float(hotel_cost_deltas.get(option.id, 0)),
            "carrier_preference": carrier_preference,
        }))

    bounds = {
        axis: (min(raw[axis] for _, raw in rows), max(raw[axis] for _, raw in rows))
        for axis in AXES
    }
    scored = []
    for option, raw in rows:
        components = {
            axis: 0.0 if low == high else (raw[axis] - low) / (high - low)
            for axis, (low, high) in bounds.items()
        }
        score = sum(
            components[axis] * ranking["weights"][axis]
            for axis in AXES
        )
        scored.append((option, score, raw, components))

    scored.sort(key=lambda row: (row[1], row[0].arrival, row[0].fare_inr, row[0].id))
    return [
        ScoredOption(option, score, position, raw, components)
        for position, (option, score, raw, components) in enumerate(scored, 1)
    ]
