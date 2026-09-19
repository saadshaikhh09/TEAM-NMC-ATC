CREATE TABLE IF NOT EXISTS api_quota (
    provider   TEXT NOT NULL,
    year_month TEXT NOT NULL,
    used       INTEGER NOT NULL DEFAULT 0 CHECK (used >= 0),
    PRIMARY KEY (provider, year_month)
);
