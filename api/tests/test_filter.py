from datetime import datetime, timezone
from types import SimpleNamespace

from core.config import policy
from planner.constraints import filter
from providers.base import FlightOption


def option(option_id: str, arrival: datetime, fare_inr: int, departure: datetime) -> FlightOption:
    return FlightOption(
        id=option_id,
        carrier="BA",
        flight_number="BA138",
        departure=departure,
        arrival=arrival,
        stops=0,
        cabin="economy",
        fare_inr=fare_inr,
    )


def basic_constraints(**overrides):
    values = {
        "hard_arrival_by": None,
        "hard_arrival_by_local": None,
        "max_fare_inr": 60_000,
        "max_stops": 1,
        "cabin": "economy",
        "avoid_carriers": [],
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def basic_option(**overrides):
    values = {
        "id": "candidate",
        "carrier": "BA",
        "flight_number": "BA138",
        "departure": datetime(2026, 9, 20, 8, 0, tzinfo=timezone.utc),
        "arrival": datetime(2026, 9, 20, 18, 0, tzinfo=timezone.utc),
        "stops": 0,
        "cabin": "economy",
        "fare_inr": 52_000,
    }
    values.update(overrides)
    return FlightOption(**values)


def test_cheaper_faster_option_is_rejected_for_missing_hard_arrival_deadline():
    constraints = SimpleNamespace(
        hard_arrival_by=datetime(2026, 9, 21, 8, 0, tzinfo=timezone.utc),
        hard_arrival_by_local="09:00, 21 Sep",
        max_fare_inr=60_000,
        max_stops=1,
        cabin="economy",
        avoid_carriers=[],
    )
    accepted = option(
        "accepted",
        datetime(2026, 9, 21, 7, 30, tzinfo=timezone.utc),
        60_000,
        datetime(2026, 9, 20, 18, 0, tzinfo=timezone.utc),
    )
    cheaper_faster = option(
        "cheaper-faster",
        datetime(2026, 9, 21, 10, 40, tzinfo=timezone.utc),
        52_000,
        datetime(2026, 9, 21, 2, 40, tzinfo=timezone.utc),
    )

    survivors, rejections = filter([accepted, cheaper_faster], constraints, policy())

    assert survivors == [accepted]
    assert rejections == [
        {
            "option_id": "cheaper-faster",
            "rule": "hard_arrival_by",
            "human_reason": "Arrives 11:40, misses hard deadline 09:00",
            "note": "would have been 8,000 cheaper",
        }
    ]


def test_fare_over_traveller_cap_is_rejected():
    candidate = basic_option(fare_inr=72_000)

    survivors, rejections = filter([candidate], basic_constraints(), policy())

    assert survivors == []
    assert rejections == [
        {
            "option_id": "candidate",
            "rule": "max_fare_inr",
            "human_reason": "Fare 72,000 exceeds cap 60,000",
            "note": None,
        }
    ]


def test_policy_fare_ceiling_caps_a_higher_traveller_limit():
    candidate = basic_option(fare_inr=95_000)

    survivors, rejections = filter(
        [candidate], basic_constraints(max_fare_inr=100_000), policy()
    )

    assert survivors == []
    assert rejections[0]["human_reason"] == "Fare 95,000 exceeds cap 90,000"


def test_option_over_effective_stop_limit_is_rejected():
    candidate = basic_option(stops=2)

    survivors, rejections = filter([candidate], basic_constraints(), policy())

    assert survivors == []
    assert rejections[0] == {
        "option_id": "candidate",
        "rule": "max_stops",
        "human_reason": "2 stops, limit is 1",
        "note": None,
    }


def test_cabin_downgrade_is_rejected_when_policy_disallows_it():
    candidate = basic_option(cabin="economy")

    survivors, rejections = filter(
        [candidate], basic_constraints(cabin="business"), policy()
    )

    assert survivors == []
    assert rejections[0] == {
        "option_id": "candidate",
        "rule": "cabin",
        "human_reason": "Business cabin, downgrade not permitted",
        "note": None,
    }


def test_avoided_carrier_is_rejected():
    candidate = basic_option(carrier="BA")

    survivors, rejections = filter(
        [candidate], basic_constraints(avoid_carriers=["BA"]), policy()
    )

    assert survivors == []
    assert rejections[0] == {
        "option_id": "candidate",
        "rule": "avoid_carriers",
        "human_reason": "BA is on your avoid-carriers list",
        "note": None,
    }


def test_first_matching_rule_produces_exactly_one_rejection():
    candidate = basic_option(fare_inr=72_000, stops=2)

    survivors, rejections = filter([candidate], basic_constraints(), policy())

    assert survivors == []
    assert len(rejections) == 1
    assert rejections[0]["rule"] == "max_fare_inr"


def test_empty_options_returns_both_empty_outputs():
    assert filter([], basic_constraints(), policy()) == ([], [])
