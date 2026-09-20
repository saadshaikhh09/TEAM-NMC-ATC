"""The most important test in the repo.

Proves the system produces usable member-facing text with every LLM key blank.
If this passes, no model outage can break the demo.
"""
from types import SimpleNamespace
from uuid import uuid4

from llm import fallback


def _plan():
    return SimpleNamespace(
        evaluated_count=14,
        options=[
            SimpleNamespace(
                id="opt_1",
                carrier="BA",
                flight_number="BA138",
                departure="2026-09-20T08:10:00+00:00",
                arrival="2026-09-20T18:05:00+00:00",
                fare_inr=52_400,
            )
        ],
        chosen_option_id="opt_1",
        rejections=[
            SimpleNamespace(
                option_id="opt_4",
                human_reason="Arrives 11:40, misses hard deadline 09:00",
                note="would have been 8,000 cheaper",
            )
        ],
        hotel_change=SimpleNamespace(
            required=True,
            new_check_in="2026-09-21",
            cost_delta_inr=-9_800,
        ),
        total_cost_delta_inr=4_200,
        approval_reason="fare 52,400 exceeds auto-approve threshold 45,000",
    )


def test_explanation_uses_recovery_plan_content_with_no_model():
    text = fallback.explanation(_plan())

    for expected in (
        "BA138",
        "opt_4",
        "Arrives 11:40, misses hard deadline 09:00",
        "2026-09-21",
        "9,800",
        "4,200",
        "fare 52,400 exceeds auto-approve threshold 45,000",
    ):
        assert expected in text


def test_names_the_flight_on_a_persisted_plan_row():
    """plan_options.id is the row's UUID; the option id lives in option_id."""
    plan = _plan()
    plan.options = [
        SimpleNamespace(
            id=uuid4(), option_id="opt_1", carrier="BA", flight_number="BA138",
            fare_inr=52_400,
        )
    ]

    assert "BA BA138" in fallback.explanation(plan)
    assert "BA BA138" in fallback.member_message(plan)


def test_member_message_is_a_recommendation_not_a_live_booking_claim():
    text = fallback.member_message(_plan())

    assert "BA138" in text
    assert "4,200" in text
    assert "approval" in text.lower()
    assert "rebooked" not in text.lower()
    assert "booking confirmed" not in text.lower()
