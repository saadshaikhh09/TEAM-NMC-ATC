"""Run the database-backed monitor from the API process."""

from __future__ import annotations

from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler

from core.config import settings
from core.db import SessionLocal
from monitor.poller import poll_due
from providers.aerodatabox import AeroDataBoxProvider
from providers.aviationstack import AviationStackProvider
from providers.mock import MockFlightProvider
from providers.status_utils import config_value


_scheduler: BackgroundScheduler | None = None


def _status_provider():
    # Demo mode is a hard guard: even a live provider setting cannot spend quota.
    if settings().demo_mode:
        return MockFlightProvider(), "simulated"
    name = config_value("PROVIDER_FLIGHT_STATUS", "mock").lower()
    if name == "mock":
        return MockFlightProvider(), "simulated"
    if name == "aerodatabox":
        return AeroDataBoxProvider(), "aerodatabox"
    if name == "aviationstack":
        return AviationStackProvider(), "aviationstack"
    raise ValueError(f"unknown PROVIDER_FLIGHT_STATUS {name!r}")


def run_monitor_once() -> int:
    provider, source = _status_provider()
    with SessionLocal() as session:
        return poll_due(session, provider, source)


def start_monitor() -> None:
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        return
    interval_seconds = settings().demo_poll_seconds if settings().demo_mode else 60
    if interval_seconds < 1:
        raise ValueError("monitor tick interval must be positive")
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        run_monitor_once,
        "interval",
        seconds=interval_seconds,
        next_run_time=datetime.now(timezone.utc),
        max_instances=1,
        coalesce=True,
        id="flight-monitor",
    )
    scheduler.start()
    _scheduler = scheduler


def stop_monitor() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
