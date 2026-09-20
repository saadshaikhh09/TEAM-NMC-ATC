CREATE TABLE IF NOT EXISTS users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email         TEXT NOT NULL UNIQUE,
    name          TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO users (id, email, name, password_hash)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'demo@atc.local',
    'ATC Demo',
    'scrypt$16384$8$1$1408139bf1ed45fda9d245b116b0d042$5562d1ddc249f92dd6acc2b5cfbb50c30b8126f8925a1c045dff1385da5f4baa697d56462553616cee549bd84e5693e94f531fa083e71c00f134cdd35cb67cab'
) ON CONFLICT (email) DO NOTHING;

CREATE TABLE IF NOT EXISTS sessions (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions (user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions (expires_at);

ALTER TABLE travellers ADD COLUMN IF NOT EXISTS user_id UUID;
UPDATE travellers SET user_id = '00000000-0000-0000-0000-000000000001' WHERE user_id IS NULL;
ALTER TABLE travellers ALTER COLUMN user_id SET NOT NULL;
DO $$ BEGIN
    ALTER TABLE travellers ADD CONSTRAINT travellers_user_id_fkey
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
CREATE INDEX IF NOT EXISTS idx_travellers_user_id ON travellers (user_id);

ALTER TABLE traveller_constraints ADD COLUMN IF NOT EXISTS hard_arrival_timezone TEXT;
ALTER TABLE flights ADD COLUMN IF NOT EXISTS origin_timezone TEXT;
ALTER TABLE flights ADD COLUMN IF NOT EXISTS destination_timezone TEXT;
ALTER TABLE hotels ADD COLUMN IF NOT EXISTS city_timezone TEXT;

ALTER TABLE approvals ALTER COLUMN decision SET NOT NULL;
ALTER TABLE approvals ALTER COLUMN decided_at SET NOT NULL;
DO $$ BEGIN
    ALTER TABLE approvals ADD CONSTRAINT uq_approvals_plan_id UNIQUE (plan_id);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
DO $$ BEGIN
    ALTER TABLE approvals ADD CONSTRAINT ck_approvals_decision
        CHECK (decision IN ('APPROVED', 'REJECTED'));
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
