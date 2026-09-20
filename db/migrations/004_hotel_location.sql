ALTER TABLE hotels
  ADD COLUMN IF NOT EXISTS address TEXT,
  ADD COLUMN IF NOT EXISTS latitude DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS longitude DOUBLE PRECISION;

DO $$ BEGIN
  ALTER TABLE hotels ADD CONSTRAINT hotels_latitude_bounds
    CHECK (latitude IS NULL OR latitude BETWEEN -90 AND 90);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  ALTER TABLE hotels ADD CONSTRAINT hotels_longitude_bounds
    CHECK (longitude IS NULL OR longitude BETWEEN -180 AND 180);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

