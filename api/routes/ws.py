"""Broadcast the frozen event envelope to connected dashboard clients."""

from __future__ import annotations

import asyncio
from contextlib import suppress
from threading import Lock

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from core.auth import SESSION_COOKIE, browser_origin_allowed, user_for_token
from core.db import SessionLocal
from core.events import subscribe
from core.models import Traveller, Trip


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

_clients: dict[int, tuple[asyncio.AbstractEventLoop, asyncio.Queue, object]] = {}
_lock = Lock()


def _broadcast(event_type: str, message: dict) -> None:
    envelope = {
        "type": event_type,
        "trip_id": message["trip_id"],
        "payload": message["payload"],
    }
    try:
        trip_id = message["trip_id"]
        with SessionLocal() as db:
            owner_id = db.scalar(
                select(Traveller.user_id).join(Trip).where(Trip.id == trip_id)
            )
    except (KeyError, ValueError):
        return
    with _lock:
        clients = [client for client in _clients.values() if client[2] == owner_id]
    for loop, queue, _ in clients:
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
    if not browser_origin_allowed(websocket.headers.get("origin"), websocket.headers.get("host")):
        await websocket.close(code=4403)
        return
    user = user_for_token(websocket.cookies.get(SESSION_COOKIE))
    if user is None:
        await websocket.close(code=4401)
        return
    await websocket.accept()
    queue: asyncio.Queue = asyncio.Queue()
    client_id = id(queue)
    with _lock:
        _clients[client_id] = (asyncio.get_running_loop(), queue, user.id)
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
