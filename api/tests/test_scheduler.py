from monitor.scheduler import next_poll_interval
from datetime import timedelta


def test_tiers():
    assert next_poll_interval(2) == timedelta(minutes=15)
    assert next_poll_interval(23.9) == timedelta(minutes=15)
    assert next_poll_interval(48) == timedelta(hours=6)
    assert next_poll_interval(200) == timedelta(hours=12)
