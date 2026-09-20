from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy import func, select

from core.auth import hash_token
from core.db import SessionLocal
from core.models import Trip, UserSession
from core.trip_service import TripInput
from main import app


def registration(email="alex@example.com"):
    return {"name": "Alex Morgan", "email": email, "password": "StrongPass!2026"}


def trip_payload(name="Alex Morgan"):
    return {
        "traveller_name": name,
        "origin": "BOM",
        "destination": "LHR",
        "outbound": {
            "carrier": "AI",
            "flight_number": "AI131",
            "origin": "BOM",
            "destination": "LHR",
            "scheduled_departure": "2026-10-01T10:00:00+05:30",
            "scheduled_arrival": "2026-10-01T15:30:00+01:00",
            "fare_inr": 42000,
        },
        "constraints": {"max_fare_inr": 70000, "max_stops": 1},
    }


def test_register_session_login_failure_success_logout_and_duplicate_email():
    client = TestClient(app)
    assert client.get("/auth/session").status_code == 401
    created = client.post("/auth/register", json=registration())
    assert created.status_code == 201
    assert client.get("/auth/session").json()["email"] == "alex@example.com"
    assert TestClient(app).post("/auth/register", json=registration()).status_code == 409

    assert client.post("/auth/logout").status_code == 204
    assert client.get("/auth/session").status_code == 401
    assert client.post(
        "/auth/login", json={"email": "alex@example.com", "password": "wrong"}
    ).status_code == 401
    assert client.post(
        "/auth/login", json={"email": " ALEX@example.com ", "password": "StrongPass!2026"}
    ).status_code == 200


def test_expired_session_is_rejected():
    client = TestClient(app)
    client.post("/auth/register", json=registration("expired@example.com"))
    token = client.cookies.get("atc_session")
    with SessionLocal.begin() as db:
        row = db.scalar(select(UserSession).where(UserSession.token_hash == hash_token(token)))
        row.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    assert client.get("/auth/session").status_code == 401


def test_manual_trip_persists_and_is_denied_to_another_account():
    owner = TestClient(app)
    other = TestClient(app)
    owner.post("/auth/register", json=registration("owner@example.com"))
    other.post("/auth/register", json=registration("other@example.com"))

    created = owner.post("/trips", json=trip_payload())
    assert created.status_code == 201
    trip_id = created.json()["id"]
    assert any(item["id"] == trip_id for item in owner.get("/trips").json())
    assert other.get(f"/trips/{trip_id}").status_code == 404
    assert other.get(f"/trips/{trip_id}/timeline").status_code == 404


def test_invalid_dependent_input_rolls_back_everything():
    client = TestClient(app)
    client.post("/auth/register", json=registration("rollback@example.com"))
    with SessionLocal() as db:
        before = db.scalar(select(func.count()).select_from(Trip))
    payload = trip_payload("Rollback User") | {
        "hotel": {
            "name": "Invalid Hotel", "city": "LON",
            "check_in": "2026-10-05", "check_out": "2026-10-04",
        }
    }
    assert client.post("/trips", json=payload).status_code == 422
    with SessionLocal() as db:
        assert db.scalar(select(func.count()).select_from(Trip)) == before


def test_extract_uses_the_same_persistence_sink(monkeypatch):
    client = TestClient(app)
    client.post("/auth/register", json=registration("extract@example.com"))
    parsed = TripInput.model_validate(trip_payload("Extract User"))
    monkeypatch.setattr("llm.extract.extract", lambda _text: parsed)

    response = client.post("/trips/extract", json={"pasted_booking_text": "AI booking"})
    assert response.status_code == 201
    assert response.json()["traveller_name"] == "Extract User"
    assert any(item["id"] == response.json()["id"] for item in client.get("/trips").json())


def test_new_trip_can_recover_and_shift_an_imported_hotel_booking():
    client = TestClient(app)
    assert client.post("/auth/register", json=registration("hotel-flow@example.com")).status_code == 201
    payload = trip_payload("Hotel Flow") | {
        "hotel": {
            "name": "London demo stay", "city": "LON",
            "check_in": "2026-09-30", "check_out": "2026-10-05",
            "confirmation_number": "IMPORTED-123", "nightly_rate_inr": 9000,
        },
        "constraints": {"max_stops": 2, "auto_approve_under_inr": 100000},
    }
    created = client.post("/trips", json=payload)
    assert created.status_code == 201
    trip_id = created.json()["id"]
    flight_id = created.json()["flights"][0]["id"]

    disruption = client.post(f"/simulate/cancellation?flight_id={flight_id}")
    assert disruption.status_code == 200
    plan_url = f"/disruptions/{disruption.json()['id']}/plan"
    plan = client.get(plan_url)
    assert plan.status_code == 200
    if plan.json()["state"] == "AWAITING_APPROVAL":
        assert client.post(f"/approvals/{plan.json()['id']}/approve").status_code == 200

    final_plan = client.get(plan_url).json()
    final_trip = client.get(f"/trips/{trip_id}").json()
    assert final_plan["state"] == "EXECUTED"
    assert final_trip["status"] == "RECOVERED"
    assert any(flight["booking_reference"] == "MOCK-" + final_plan["chosen_option_id"].upper()
               for flight in final_trip["flights"])
    assert final_trip["hotels"][0]["confirmation_number"].startswith("MOCK-")
    assert final_trip["hotels"][0]["check_in"] != "2026-09-30"
