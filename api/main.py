"""FastAPI entrypoint. Owner: Person A.

Routers are mounted here. Each router file has exactly one owner — see TEAM.md.
Do not add business logic to this file.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from monitor.runner import start_monitor, stop_monitor
from providers.mock import MockFlightProvider, MockHotelProvider
from routes import approvals, simulate, trips, webhooks, ws

app = FastAPI(title="Travel Disruption Concierge", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"ok": True}


app.include_router(trips.router)
app.include_router(approvals.router)
app.include_router(simulate.router)
app.include_router(ws.router)
app.include_router(webhooks.router)
approvals.configure(MockFlightProvider(), MockHotelProvider())
app.add_event_handler("startup", start_monitor)
app.add_event_handler("shutdown", stop_monitor)
