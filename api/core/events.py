"""In-process event bus. Owner: Person A.

Deliberately not Celery, not Temporal. The trips row is the resume point —
a poller that reads state from Postgres on every tick is already resumable.
"""
from collections import defaultdict
from typing import Callable

_subscribers: dict[str, list[Callable]] = defaultdict(list)


def subscribe(event: str, fn: Callable) -> None:
    _subscribers[event].append(fn)


def emit(event: str, payload: dict) -> None:
    for fn in _subscribers.get(event, []):
        fn(payload)
