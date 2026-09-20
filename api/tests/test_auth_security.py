from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from core.auth import hash_password, hash_token, normalize_email, validate_password, verify_password
from main import app
from tests.helpers import login_demo


def test_passwords_are_adaptively_hashed_and_verified():
    encoded = hash_password("StrongPass!2026")

    assert encoded.startswith("scrypt$")
    assert "StrongPass!2026" not in encoded
    assert verify_password("StrongPass!2026", encoded)
    assert not verify_password("wrong", encoded)


def test_email_and_password_validation():
    assert normalize_email("  Demo@ATC.Local ") == "demo@atc.local"
    with pytest.raises(ValueError, match="12 characters"):
        validate_password("Short1!")
    with pytest.raises(ValueError, match="uppercase"):
        validate_password("alllowercase!2026")


def test_session_tokens_are_only_represented_by_a_stable_hash():
    first = hash_token("opaque-session-token")

    assert first == hash_token("opaque-session-token")
    assert first != "opaque-session-token"
    assert len(first) == 64


def test_cookie_writes_and_websocket_reject_foreign_browser_origins():
    client = login_demo(TestClient(app))
    assert client.post(
        "/simulate/cancellation", headers={"Origin": "https://attacker.example"}
    ).status_code == 403
    with pytest.raises(WebSocketDisconnect) as denied:
        with client.websocket_connect("/ws", headers={"Origin": "https://attacker.example"}):
            pass
    assert denied.value.code == 4403
