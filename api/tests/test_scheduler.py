from monitor.scheduler import effective_poll_interval, next_poll_interval
from datetime import timedelta


def test_tiers():
    assert next_poll_interval(2) == timedelta(minutes=15)
    assert next_poll_interval(23.9) == timedelta(minutes=15)
    assert next_poll_interval(48) == timedelta(hours=6)
    assert next_poll_interval(200) == timedelta(hours=12)


def test_demo_override_and_boundary():
    assert next_poll_interval(24) == timedelta(minutes=15)
    assert next_poll_interval(168) == timedelta(hours=6)
    assert effective_poll_interval(200, demo_mode=True, demo_poll_seconds=15) == timedelta(seconds=15)
    assert effective_poll_interval(200, demo_mode=False, demo_poll_seconds=15) == timedelta(hours=12)
