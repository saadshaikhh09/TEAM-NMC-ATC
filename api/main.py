"""FastAPI entrypoint. Owner: Person A.

Routers are mounted here. Each router file has exactly one owner — see TEAM.md.
Do not add business logic to this file.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


# TODO(A):  from routes import trips, approvals;  app.include_router(...)
# TODO(B):  from routes import simulate, ws;      app.include_router(...)
