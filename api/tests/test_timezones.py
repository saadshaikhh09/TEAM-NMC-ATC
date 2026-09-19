from datetime import datetime, timezone

import pytest

from core.timezones import local_str, local_time


def test_lhr_time_uses_london_daylight_saving():
    utc = datetime(2026, 9, 20, 6, 15, tzinfo=timezone.utc)

    assert local_time(utc, "LHR").isoformat() == "2026-09-20T07:15:00+01:00"
    assert local_str(utc, "LHR") == "07:15, 20 Sep"


def test_unknown_iata_raises():
    with pytest.raises(KeyError):
        local_time(datetime.now(timezone.utc), "XXX")
