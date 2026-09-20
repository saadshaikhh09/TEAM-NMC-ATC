-- Owner: Person A. Nobody else edits this file.

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Kept outside public so rehearsals can reset demo state without losing copy.
CREATE SCHEMA IF NOT EXISTS llm_cache;
CREATE TABLE IF NOT EXISTS llm_cache.responses (
    cache_key  TEXT PRIMARY KEY,
    response   TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email         TEXT NOT NULL UNIQUE,
    name          TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE sessions (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_sessions_user_id ON sessions (user_id);
CREATE INDEX idx_sessions_expires_at ON sessions (expires_at);

CREATE TABLE travellers (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    email           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_travellers_user_id ON travellers (user_id);

CREATE TABLE traveller_constraints (
    traveller_id        UUID PRIMARY KEY REFERENCES travellers(id) ON DELETE CASCADE,
    hard_arrival_by     TIMESTAMPTZ,
    hard_arrival_timezone TEXT,
    hard_arrival_reason TEXT,
    max_fare_inr        INTEGER,
    max_stops           INTEGER DEFAULT 1,
    cabin               TEXT DEFAULT 'economy',
    avoid_carriers      TEXT[] DEFAULT '{}',
    auto_approve_under_inr INTEGER
);

CREATE TABLE trips (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    traveller_id    UUID NOT NULL REFERENCES travellers(id) ON DELETE CASCADE,
    status          TEXT NOT NULL DEFAULT 'CREATED',
    origin          TEXT NOT NULL,
    destination     TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE flights (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id              UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    leg                  TEXT NOT NULL DEFAULT 'outbound',
    carrier              TEXT NOT NULL,
    flight_number        TEXT NOT NULL,
    origin               TEXT NOT NULL,
    destination          TEXT NOT NULL,
    origin_timezone      TEXT,
    destination_timezone TEXT,
    scheduled_departure  TIMESTAMPTZ NOT NULL,
    scheduled_arrival    TIMESTAMPTZ NOT NULL,
    status               TEXT NOT NULL DEFAULT 'SCHEDULED',
    booking_reference    TEXT,
    fare_inr             INTEGER,
    cabin                TEXT DEFAULT 'economy',
    next_poll_at         TIMESTAMPTZ,
    last_polled_at       TIMESTAMPTZ
);
CREATE INDEX idx_flights_next_poll ON flights (next_poll_at) WHERE status = 'SCHEDULED';

CREATE TABLE hotels (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id               UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    provider              TEXT NOT NULL DEFAULT 'mock',
    confirmation_number   TEXT,
    name                  TEXT NOT NULL,
    address               TEXT,
    city                  TEXT NOT NULL,
    city_timezone         TEXT,
    latitude              DOUBLE PRECISION CHECK (latitude IS NULL OR latitude BETWEEN -90 AND 90),
    longitude             DOUBLE PRECISION CHECK (longitude IS NULL OR longitude BETWEEN -180 AND 180),
    check_in              DATE NOT NULL,
    check_out             DATE NOT NULL,
    nightly_rate_inr      INTEGER,
    modifiable            BOOLEAN NOT NULL DEFAULT true,
    status                TEXT NOT NULL DEFAULT 'CONFIRMED'
);

CREATE TABLE disruptions (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id          UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    flight_id        UUID NOT NULL REFERENCES flights(id) ON DELETE CASCADE,
    kind             TEXT NOT NULL,
    source           TEXT NOT NULL,
    previous_status  TEXT,
    new_status       TEXT,
    detected_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE recovery_plans (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    disruption_id         UUID NOT NULL REFERENCES disruptions(id) ON DELETE CASCADE,
    state                 TEXT NOT NULL DEFAULT 'DRAFT',
    evaluated_count       INTEGER NOT NULL DEFAULT 0,
    chosen_option_id      TEXT,
    total_cost_delta_inr  INTEGER,
    requires_approval     BOOLEAN NOT NULL DEFAULT true,
    approval_reason       TEXT,
    explanation           TEXT,
    member_message        TEXT,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE plan_options (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id       UUID NOT NULL REFERENCES recovery_plans(id) ON DELETE CASCADE,
    option_id     TEXT NOT NULL,
    carrier       TEXT,
    flight_number TEXT,
    departure     TIMESTAMPTZ,
    arrival       TIMESTAMPTZ,
    stops         INTEGER,
    cabin         TEXT,
    fare_inr      INTEGER,
    score         NUMERIC,
    rank          INTEGER
);

-- The differentiator. Never drop rows from this table to save time.
CREATE TABLE plan_rejections (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id      UUID NOT NULL REFERENCES recovery_plans(id) ON DELETE CASCADE,
    option_id    TEXT NOT NULL,
    rule         TEXT NOT NULL,
    human_reason TEXT NOT NULL,
    note         TEXT
);

CREATE TABLE hotel_changes (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id           UUID NOT NULL REFERENCES recovery_plans(id) ON DELETE CASCADE,
    hotel_id          UUID NOT NULL REFERENCES hotels(id) ON DELETE CASCADE,
    required          BOOLEAN NOT NULL,
    new_check_in      DATE,
    new_check_out     DATE,
    cost_delta_inr    INTEGER,
    executed          BOOLEAN NOT NULL DEFAULT false
);

CREATE TABLE approvals (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id       UUID NOT NULL UNIQUE REFERENCES recovery_plans(id) ON DELETE CASCADE,
    decision      TEXT NOT NULL CHECK (decision IN ('APPROVED', 'REJECTED')),
    decided_at    TIMESTAMPTZ NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- The timeline. Every stage writes here BEFORE it acts.
CREATE TABLE agent_actions (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id      UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    plan_id      UUID REFERENCES recovery_plans(id) ON DELETE SET NULL,
    stage        TEXT NOT NULL,
    headline     TEXT NOT NULL,
    detail       JSONB NOT NULL DEFAULT '{}'::jsonb,
    duration_ms  INTEGER,
    at           TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_actions_trip_at ON agent_actions (trip_id, at);
