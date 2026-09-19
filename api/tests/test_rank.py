from datetime import datetime, timezone
from random import Random
from types import SimpleNamespace

from planner.rank import rank
from providers.base import FlightOption


UTC = timezone.utc
AXES = {
    "arrival_delay_minutes",
    "fare_delta_inr",
    "hotel_cost_delta_inr",
    "carrier_preference",
}


def option(option_id, *, carrier="AI", arrival_hour=12, fare=50_000):
    return FlightOption(
        id=option_id,
        carrier=carrier,
        flight_number=f"{carrier}100",
        departure=datetime(2026, 9, 20, 6, tzinfo=UTC),
        arrival=datetime(2026, 9, 20, arrival_hour, tzinfo=UTC),
        stops=0,
        cabin="economy",
        fare_inr=fare,
    )


def ranking_policy(**weights):
    return {
        "ranking": {
            "preferred_carriers": ["AI", "BA"],
            "weights": {
                "arrival_delay_minutes": 0.0,
                "fare_delta_inr": 0.0,
                "hotel_cost_delta_inr": 0.0,
                "carrier_preference": 0.0,
                **weights,
            },
        }
    }


def test_fully_tied_options_are_stable_across_shuffled_inputs():
    original = SimpleNamespace(scheduled_arrival=datetime(2026, 9, 20, 12, tzinfo=UTC))
    options = [
        option("c", carrier="EK"),
        option("a", carrier="AI"),
        option("b", carrier="BA"),
    ]

    for seed in range(10):
        shuffled = Random(seed).sample(options, len(options))
        scored = rank(shuffled, original, {}, ranking_policy())
        assert [item.option.id for item in scored] == ["a", "b", "c"]
        assert [item.rank for item in scored] == [1, 2, 3]

    assert {item.option.id: item.raw["carrier_preference"] for item in scored} == {
        "a": 0.0,
        "b": 0.5,
        "c": 1.0,
    }


def test_changing_policy_weight_changes_the_winner():
    original = SimpleNamespace(scheduled_arrival=datetime(2026, 9, 20, 12, tzinfo=UTC))
    cheap_late = option("cheap", arrival_hour=14, fare=40_000)
    expensive_ontime = option("ontime", arrival_hour=12, fare=60_000)

    arrival_first = rank(
        [cheap_late, expensive_ontime],
        original,
        {},
        ranking_policy(arrival_delay_minutes=1.0),
    )
    fare_first = rank(
        [cheap_late, expensive_ontime],
        original,
        {},
        ranking_policy(fare_delta_inr=1.0),
    )

    assert arrival_first[0].option.id == "ontime"
    assert fare_first[0].option.id == "cheap"


def test_single_survivor_ranks_first_without_division_by_zero():
    original = SimpleNamespace(scheduled_arrival=datetime(2026, 9, 20, 12, tzinfo=UTC))
    survivor = option("only", carrier="EK", arrival_hour=11, fare=52_400)

    scored = rank(
        [survivor],
        original,
        {},
        ranking_policy(
            arrival_delay_minutes=0.45,
            fare_delta_inr=0.30,
            hotel_cost_delta_inr=0.15,
            carrier_preference=0.10,
        ),
        hotel_cost_deltas={"only": -9_800},
    )

    assert scored[0].rank == 1
    assert scored[0].score == 0.0
    assert scored[0].raw == {
        "arrival_delay_minutes": 0.0,
        "fare_delta_inr": 52_400.0,
        "hotel_cost_delta_inr": -9_800.0,
        "carrier_preference": 1.0,
    }
    assert scored[0].components == {axis: 0.0 for axis in AXES}
