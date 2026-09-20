"""Password and opaque-session primitives plus the shared auth dependency."""

from __future__ import annotations

import hashlib
import hmac
import re
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit
from uuid import UUID

from fastapi import Cookie, HTTPException, Response
from sqlalchemy import delete, select

from core.config import settings
from core.db import SessionLocal
from core.models import User, UserSession


SESSION_COOKIE = "atc_session"
SESSION_AGE = timedelta(days=7)
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_email(value: str) -> str:
    email = value.strip().casefold()
    if len(email) > 254 or not _EMAIL.fullmatch(email):
        raise ValueError("Enter a valid email address")
    return email


def validate_password(value: str) -> str:
    if len(value) < 12:
        raise ValueError("Password must be at least 12 characters")
    if len(value) > 128:
        raise ValueError("Password must be at most 128 characters")
    for pattern, name in ((r"[A-Z]", "uppercase"), (r"[a-z]", "lowercase"),
                          (r"\d", "number"), (r"[^A-Za-z0-9]", "symbol")):
        if not re.search(pattern, value):
            article = "an" if name[0] in "aeiou" else "a"
            raise ValueError(f"Password must include {article} {name} character")
    return value


def hash_password(password: str) -> str:
    validate_password(password)
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return f"scrypt$16384$8$1${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, n, r, p, salt, expected = encoded.split("$")
        if algorithm != "scrypt":
            return False
        actual = hashlib.scrypt(
            password.encode(), salt=bytes.fromhex(salt), n=int(n), r=int(r), p=int(p)
        )
        return hmac.compare_digest(actual, bytes.fromhex(expected))
    except (ValueError, TypeError):
        return False


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def browser_origin_allowed(origin: str | None, host: str | None) -> bool:
    """Reject cross-origin cookie actions even when a browser cannot read CORS output."""
    if origin is None:
        return True  # CLI clients and server-to-server calls have no Origin header.
    parsed = urlsplit(origin)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.path or parsed.query:
        return False
    configured = {item.strip().rstrip("/") for item in settings().cors_origins.split(",")}
    return origin.rstrip("/") in configured or parsed.netloc == host


def create_session(db, user_id: UUID) -> tuple[str, datetime]:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + SESSION_AGE
    db.add(UserSession(user_id=user_id, token_hash=hash_token(token), expires_at=expires_at))
    return token, expires_at


def set_session_cookie(response: Response, token: str, expires_at: datetime) -> None:
    response.set_cookie(
        SESSION_COOKIE, token, expires=expires_at, httponly=True,
        secure=settings().environment == "production", samesite="lax", path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE, httponly=True, samesite="lax", path="/")


def user_for_token(token: str | None) -> User | None:
    if not token:
        return None
    with SessionLocal() as db:
        user = db.scalar(
            select(User).join(UserSession).where(
                UserSession.token_hash == hash_token(token),
                UserSession.expires_at > datetime.now(timezone.utc),
            )
        )
        if user is None:
            return None
        db.expunge(user)
        return user


def current_user(atc_session: str | None = Cookie(default=None)) -> User:
    user = user_for_token(atc_session)
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


def invalidate_token(db, token: str | None) -> None:
    if token:
        db.execute(delete(UserSession).where(UserSession.token_hash == hash_token(token)))
