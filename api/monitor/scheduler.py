"""Tiered polling cadence. Owner: Person B.

This is a slide. A judge will ask how polling every 15 minutes scales — the
answer is that we don't poll every flight every 15 minutes.

    > 7 days out   -> every 12 hours
    1 to 7 days    -> every 6 hours
    < 24 hours     -> every 15 minutes

In DEMO_MODE this is overridden to DEMO_POLL_SECONDS. The tiered schedule is a
production argument; the demo runs fast.
"""
from datetime import timedelta


def next_poll_interval(hours_to_departure: float) -> timedelta:
    if hours_to_departure <= 24:
        return timedelta(minutes=15)
    if hours_to_departure <= 168:
        return timedelta(hours=6)
    return timedelta(hours=12)
