"""In-process event bus. Owner: Person A.

Deliberately not Celery, not Temporal. The trips row is the resume point —
a poller that reads state from Postgres on every tick is already resumable.
"""
import traceback
from collections import defaultdict
from typing import Callable

_subscribers: dict[str, list[Callable]] = defaultdict(list)


def subscribe(event: str, fn: Callable) -> None:
    _subscribers[event].append(fn)


def emit(event: str, payload: dict) -> None:
    for fn in _subscribers.get(event, []):
        try:
            fn(payload)
        except Exception:
            # Subscribers are isolated. Detection emits from inside the request
            # that reported the disruption — a raising planner must not take the
            # websocket feed and that request down with it.
            traceback.print_exc()
