import pytest
from providers.status_map import normalise


def test_cancellation_variants_all_map():
    for raw in ("Cancelled", "Canceled", "CanceledUncertain", "Diverted"):
        assert normalise("aerodatabox", raw) == "CANCELLED"
    for raw in ("cancelled", "incident", "diverted"):
        assert normalise("aviationstack", raw) == "CANCELLED"


def test_unmapped_raises_loudly():
    with pytest.raises(ValueError):
        normalise("aerodatabox", "SomethingNew")
    with pytest.raises(ValueError):
        normalise("aerodatabox", "Unknown")
