CREATE SCHEMA IF NOT EXISTS llm_cache;
CREATE TABLE IF NOT EXISTS llm_cache.responses (
    cache_key  TEXT PRIMARY KEY,
    response   TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
