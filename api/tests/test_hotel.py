from datetime import date, datetime, timezone
from types import SimpleNamespace

from planner.hotel_impact import assess


POLICY = {"hotel": {"late_arrival_cutoff": "23:00"}}


def hotel(**changes):
    values = {
        "city": "LON",
        "check_in": date(2026, 9, 20),
        "check_out": date(2026, 9, 25),
        "nightly_rate_inr": 9_800,
        "modifiable": True,
    }
    values.update(changes)
    return SimpleNamespace(**values)


def arrival(value):
    return datetime.fromisoformat(value).astimezone(timezone.utc)


def test_arrival_a_day_late_shifts_check_in_and_reduces_cost():
    change = assess(hotel(), arrival("2026-09-21T18:00:00+01:00"), POLICY)

    assert change == {
        "required": True,
        "new_check_in": date(2026, 9, 21),
        "new_check_out": date(2026, 9, 25),
        "cost_delta_inr": -9_800,
    }


def test_late_arrival_on_check_in_date_moves_to_next_day():
    change = assess(hotel(), arrival("2026-09-20T23:40:00+01:00"), POLICY)

    assert change["required"] is True
    assert change["new_check_in"] == date(2026, 9, 21)
    assert change["cost_delta_inr"] == -9_800


def test_on_time_arrival_requires_no_change():
    change = assess(hotel(), arrival("2026-09-20T18:00:00+01:00"), POLICY)

    assert change == {
        "required": False,
        "new_check_in": date(2026, 9, 20),
        "new_check_out": date(2026, 9, 25),
        "cost_delta_inr": 0,
    }


def test_non_modifiable_hotel_still_reports_required_change():
    change = assess(
        hotel(modifiable=False),
        arrival("2026-09-21T18:00:00+01:00"),
        POLICY,
    )

    assert change["required"] is True


def test_checkout_moves_only_when_shift_would_make_stay_zero_nights():
    change = assess(hotel(), arrival("2026-09-25T12:00:00+01:00"), POLICY)

    assert change == {
        "required": True,
        "new_check_in": date(2026, 9, 25),
        "new_check_out": date(2026, 9, 26),
        "cost_delta_inr": -49_000,
    }
