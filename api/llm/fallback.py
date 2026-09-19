"""Templated strings for when the LLM is slow, rate-limited, or offline.

BUILD THIS FIRST, before the LLM client. Twenty minutes of work and it is the
difference between a graceful demo and a dead one on venue wifi.
"""


def explanation(plan) -> str:
    return (
        f"Evaluated {plan.evaluated_count} alternatives. "
        f"{len(plan.rejections)} were rejected on policy or traveller constraints. "
        f"Selected the highest-ranked remaining option."
    )


def member_message(plan) -> str:
    return (
        "Your flight was cancelled. We have rebooked you on the best available "
        "alternative that meets your travel constraints. Your hotel has been "
        "updated where needed."
    )
