-- Owner: Person A. Three demo travellers. Deterministic — no random values.
-- `make reset` reapplies this. You will run it ~30 times during rehearsal.

-- 1. Priya — the hard deadline case. THIS IS THE DEMO.
INSERT INTO users (id, email, name, password_hash)
VALUES (
  '00000000-0000-0000-0000-000000000001', 'demo@atc.local', 'ATC Demo',
  'scrypt$16384$8$1$1408139bf1ed45fda9d245b116b0d042$5562d1ddc249f92dd6acc2b5cfbb50c30b8126f8925a1c045dff1385da5f4baa697d56462553616cee549bd84e5693e94f531fa083e71c00f134cdd35cb67cab'
);

WITH t AS (
  INSERT INTO travellers (id, user_id, name, email)
  VALUES ('11111111-1111-1111-1111-111111111111', '00000000-0000-0000-0000-000000000001', 'Priya Sharma', 'priya@example.com')
  RETURNING id
)
INSERT INTO traveller_constraints
  (traveller_id, hard_arrival_by, hard_arrival_reason, max_fare_inr, max_stops, cabin, auto_approve_under_inr)
SELECT id,
       '2026-09-21T09:00:00+01:00',
       'Client presentation in London, cannot be missed',
       60000, 1, 'economy', 45000
FROM t;

INSERT INTO trips (id, traveller_id, status, origin, destination)
VALUES ('aaaaaaaa-1111-1111-1111-111111111111',
        '11111111-1111-1111-1111-111111111111',
        'MONITORING', 'BOM', 'LHR');

INSERT INTO flights (trip_id, leg, carrier, flight_number, origin, destination,
                     scheduled_departure, scheduled_arrival, booking_reference, fare_inr, cabin, next_poll_at)
VALUES
 ('aaaaaaaa-1111-1111-1111-111111111111', 'outbound', 'AI', 'AI131', 'BOM', 'LHR',
  '2026-09-20T02:30:00+05:30', '2026-09-20T07:15:00+01:00', 'PNR-AX91', 48200, 'economy', now()),
 ('aaaaaaaa-1111-1111-1111-111111111111', 'return', 'AI', 'AI132', 'LHR', 'BOM',
  '2026-09-25T13:00:00+01:00', '2026-09-26T02:40:00+05:30', 'PNR-AX91', 0, 'economy', now());

INSERT INTO hotels (trip_id, confirmation_number, name, city, check_in, check_out, nightly_rate_inr, modifiable)
VALUES ('aaaaaaaa-1111-1111-1111-111111111111', 'HTL-99213', 'Kensington Central', 'LON',
        '2026-09-20', '2026-09-25', 9800, true);

-- 2. Rohan — the fare-cap escalation case.
WITH t AS (
  INSERT INTO travellers (id, user_id, name, email)
  VALUES ('22222222-2222-2222-2222-222222222222', '00000000-0000-0000-0000-000000000001', 'Rohan Mehta', 'rohan@example.com')
  RETURNING id
)
INSERT INTO traveller_constraints
  (traveller_id, max_fare_inr, max_stops, cabin, auto_approve_under_inr)
SELECT id, 70000, 1, 'economy', 30000 FROM t;

INSERT INTO trips (id, traveller_id, status, origin, destination)
VALUES ('bbbbbbbb-2222-2222-2222-222222222222',
        '22222222-2222-2222-2222-222222222222',
        'MONITORING', 'DEL', 'SIN');

INSERT INTO flights (trip_id, leg, carrier, flight_number, origin, destination,
                     scheduled_departure, scheduled_arrival, booking_reference, fare_inr, cabin, next_poll_at)
VALUES ('bbbbbbbb-2222-2222-2222-222222222222', 'outbound', '6E', '6E1051', 'DEL', 'SIN',
        '2026-09-20T23:50:00+05:30', '2026-09-21T08:05:00+08:00', 'PNR-RM22', 29400, 'economy', now());

INSERT INTO hotels (trip_id, confirmation_number, name, city, check_in, check_out, nightly_rate_inr, modifiable)
VALUES ('bbbbbbbb-2222-2222-2222-222222222222', 'HTL-44120', 'Bugis Riverside', 'SIN',
        '2026-09-21', '2026-09-24', 7200, false);

-- 3. Ananya — the clean auto-rebook case. Nothing exotic. Proves the happy path.
WITH t AS (
  INSERT INTO travellers (id, user_id, name, email)
  VALUES ('33333333-3333-3333-3333-333333333333', '00000000-0000-0000-0000-000000000001', 'Ananya Iyer', 'ananya@example.com')
  RETURNING id
)
INSERT INTO traveller_constraints
  (traveller_id, max_fare_inr, max_stops, cabin, auto_approve_under_inr)
SELECT id, 40000, 2, 'economy', 35000 FROM t;

INSERT INTO trips (id, traveller_id, status, origin, destination)
VALUES ('cccccccc-3333-3333-3333-333333333333',
        '33333333-3333-3333-3333-333333333333',
        'MONITORING', 'BLR', 'DXB');

INSERT INTO flights (trip_id, leg, carrier, flight_number, origin, destination,
                     scheduled_departure, scheduled_arrival, booking_reference, fare_inr, cabin, next_poll_at)
VALUES ('cccccccc-3333-3333-3333-333333333333', 'outbound', 'EK', 'EK569', 'BLR', 'DXB',
        '2026-09-20T04:20:00+05:30', '2026-09-20T07:05:00+04:00', 'PNR-AI73', 22100, 'economy', now());
