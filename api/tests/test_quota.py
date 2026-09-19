from datetime import date as real_date
from types import SimpleNamespace

import pytest
from sqlalchemy import text

from core import quota
from core.db import SessionLocal


TEST_MONTH = "2099-01"


class TestDate:
    @classmethod
    def today(cls):
        return real_date(2099, 1, 1)


@pytest.fixture(autouse=True)
def isolated_quota_month(monkeypatch):
    monkeypatch.setattr(quota, "date", TestDate)
    with SessionLocal.begin() as session:
        session.execute(
            text("DELETE FROM api_quota WHERE year_month = :year_month"),
            {"year_month": TEST_MONTH},
        )
    yield
    with SessionLocal.begin() as session:
        session.execute(
            text("DELETE FROM api_quota WHERE year_month = :year_month"),
            {"year_month": TEST_MONTH},
        )


def configure(monkeypatch, *, demo_mode=False, fraction=1.0):
    monkeypatch.setattr(
        quota,
        "settings",
        lambda: SimpleNamespace(
            demo_mode=demo_mode,
            quota_dev_budget_fraction=fraction,
            quota_aerodatabox_monthly=500,
            quota_aviationstack_monthly=500,
        ),
        raising=False,
    )


def test_spend_increments(monkeypatch):
    configure(monkeypatch)

    quota.spend("aerodatabox", 2)

    assert quota.remaining("aerodatabox") == 498
    assert quota.report() == {"aerodatabox": 498, "aviationstack": 500}


def test_spend_raises_when_budget_would_be_exceeded(monkeypatch):
    configure(monkeypatch, fraction=0.002)
    quota.spend("aviationstack")

    with pytest.raises(quota.QuotaExceeded):
        quota.spend("aviationstack")

    assert quota.remaining("aviationstack") == 0


def test_demo_mode_blocks_without_spending(monkeypatch):
    configure(monkeypatch, demo_mode=True)

    with pytest.raises(quota.QuotaExceeded, match="DEMO_MODE"):
        quota.spend("aerodatabox")

    with SessionLocal() as session:
        used = session.execute(
            text(
                "SELECT used FROM api_quota "
                "WHERE provider = :provider AND year_month = :year_month"
            ),
            {"provider": "aerodatabox", "year_month": TEST_MONTH},
        ).scalar_one_or_none()
    assert used is None


def test_counter_survives_a_new_session(monkeypatch):
    configure(monkeypatch)
    quota.spend("aviationstack", 3)

    with SessionLocal() as session:
        used = session.execute(
            text(
                "SELECT used FROM api_quota "
                "WHERE provider = :provider AND year_month = :year_month"
            ),
            {"provider": "aviationstack", "year_month": TEST_MONTH},
        ).scalar_one()

    assert used == 3
