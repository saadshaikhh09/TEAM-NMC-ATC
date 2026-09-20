"""Registration and server-side cookie sessions."""

from datetime import datetime, timezone

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from core.auth import (
    SESSION_COOKIE, clear_session_cookie, create_session, current_user, hash_password,
    invalidate_token, normalize_email, set_session_cookie, verify_password,
)
from core.db import SessionLocal
from core.models import Traveller, TravellerConstraint, User, UserSession


router = APIRouter(prefix="/auth", tags=["auth"])
INVALID_LOGIN = "Invalid email or password"


class Credentials(BaseModel):
    email: str
    password: str


class Registration(Credentials):
    name: str = Field(min_length=1, max_length=120)


def _response(user: User) -> dict:
    return {"id": str(user.id), "name": user.name, "email": user.email}


@router.post("/register", status_code=201)
def register(payload: Registration, response: Response):
    try:
        email = normalize_email(payload.email)
        password_hash = hash_password(payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    try:
        with SessionLocal.begin() as db:
            user = User(email=email, name=payload.name.strip(), password_hash=password_hash)
            db.add(user)
            db.flush()
            traveller = Traveller(user_id=user.id, name=user.name, email=email)
            db.add(traveller)
            db.flush()
            db.add(TravellerConstraint(traveller_id=traveller.id))
            token, expires_at = create_session(db, user.id)
            result = _response(user)
    except IntegrityError as exc:
        raise HTTPException(status_code=409, detail="An account with this email already exists") from exc
    set_session_cookie(response, token, expires_at)
    return result


@router.post("/login")
def login(payload: Credentials, response: Response):
    try:
        email = normalize_email(payload.email)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=INVALID_LOGIN) from exc
    with SessionLocal.begin() as db:
        user = db.scalar(select(User).where(User.email == email))
        if user is None or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=401, detail=INVALID_LOGIN)
        db.execute(delete(UserSession).where(UserSession.user_id == user.id))
        token, expires_at = create_session(db, user.id)
        result = _response(user)
    set_session_cookie(response, token, expires_at)
    return result


@router.post("/logout", status_code=204)
def logout(response: Response, atc_session: str | None = Cookie(default=None)):
    with SessionLocal.begin() as db:
        invalidate_token(db, atc_session)
    clear_session_cookie(response)


@router.get("/session")
def session(user: User = Depends(current_user)):
    return _response(user)
