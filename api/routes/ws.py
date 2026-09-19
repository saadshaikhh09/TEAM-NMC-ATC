"""Broadcast the frozen event envelope to connected dashboard clients."""

from __future__ import annotations

import asyncio
from contextlib import suppress
from threading import Lock

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from core.events import subscribe


router = APIRouter()
EVENT_TYPES = (
    "trip.updated",
    "disruption.detected",
    "plan.ready",
    "plan.awaiting_approval",
    "plan.executing",
    "plan.executed",
    "plan.failed",
    "action.recorded",
)

_clients: dict[int, tuple[asyncio.AbstractEventLoop, asyncio.Queue]] = {}
_lock = Lock()


def _broadcast(event_type: str, message: dict) -> None:
    envelope = {
        "type": event_type,
        "trip_id": message["trip_id"],
        "payload": message["payload"],
    }
    with _lock:
        clients = list(_clients.values())
    for loop, queue in clients:
        try:
            loop.call_soon_threadsafe(queue.put_nowait, envelope)
        except RuntimeError:
            # A disconnected client's loop may close between snapshot and send.
            pass


for _event_type in EVENT_TYPES:
    subscribe(_event_type, lambda message, event_type=_event_type: _broadcast(event_type, message))


async def _send(websocket: WebSocket, queue: asyncio.Queue) -> None:
    while True:
        await websocket.send_json(await queue.get())


@router.websocket("/ws")
async def websocket_events(websocket: WebSocket) -> None:
    await websocket.accept()
    queue: asyncio.Queue = asyncio.Queue()
    client_id = id(queue)
    with _lock:
        _clients[client_id] = (asyncio.get_running_loop(), queue)
    sender = asyncio.create_task(_send(websocket, queue))
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        with _lock:
            _clients.pop(client_id, None)
        sender.cancel()
        with suppress(asyncio.CancelledError):
            await sender
