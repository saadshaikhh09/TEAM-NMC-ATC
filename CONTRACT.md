# CONTRACT — frozen at hour 1

These shapes and names are frozen. The frontend builds against them with mocks;
the backend fills them in. **Changing anything here requires all four people to
agree in person.** A silent change here is how you lose three hours at hour 16.

If you need a field that does not exist: say so in the group chat, get a yes,
change it here first, commit this file alone, then write code.

---

## Providers — who does what, and the budget

Four of the seven keys are in the build. Three are cut.

| Provider | Role | Owner | Budget | Notes |
|---|---|---|---|---|
| **AeroDataBox** | flight status, PRIMARY | B | **500/month**, 5/sec | richest status vocabulary, HTTPS |
| **AviationStack** | status cross-check only | B | **500/month** | HTTP only, key in plaintext, backend only |
| **Duffel** (test) | flight search + book | D | 30/min, ~120 searches | webhooks only for orders we booked |
| **Nuitee / LiteAPI** (sandbox) | hotel lifecycle | D | generous | no modify — cancel then rebook |
| **Mock** | **demo default** | B | infinite | deterministic, survives venue wifi |

Cut: **SerpAPI** (100/month, Google cache lags cancellations 10–30 min),
**FlightAPI.io** (20 trial credits = 10 calls total, unusable),
**Ignav** (returns booking *links* not bookings; `ignav_id` expires in minutes).

**The 500/month ceiling governs everything.** `DEMO_MODE=true` means no live
status call happens at all. Every live call goes through `core.quota.spend()`.
See `api/core/quota.py` before writing any provider code.

All provider statuses are normalised through `providers/status_map.py` into our
five values before anything else sees them. Unmapped values raise.

---

## REST endpoints

| Method | Path | Owner | Returns |
|---|---|---|---|
| GET | `/trips` | A | `Trip[]` |
| GET | `/trips/{id}` | A | `Trip` |
| POST | `/trips` | A | `Trip` (manual entry) |
| POST | `/trips/extract` | A | `Trip` (paste a booking email) |
| GET | `/trips/{id}/timeline` | A | `AgentAction[]` |
| POST | `/simulate/cancellation` | B | `Disruption` |
| POST | `/simulate/delay` | B | `Disruption` |
| GET | `/disruptions/{id}/plan` | A | `RecoveryPlan` |
| POST | `/approvals/{id}/approve` | A | `RecoveryPlan` |
| POST | `/approvals/{id}/reject` | A | `RecoveryPlan` |
| WS | `/ws` | B | `WsEvent` stream |

## WebSocket events

Event names are fixed strings. The frontend switches on `type`.

```
trip.updated
disruption.detected
plan.ready
plan.awaiting_approval
plan.executing
plan.executed
plan.failed
action.recorded
```

Envelope:

```json
{ "type": "disruption.detected", "trip_id": "...", "payload": { } }
```

---

## Core shapes

### Trip
```json
{
  "id": "uuid",
  "traveller_name": "Priya Sharma",
  "status": "MONITORING",
  "origin": "BOM",
  "destination": "LHR",
  "flights": [ "Flight" ],
  "hotels": [ "Hotel" ],
  "constraints": "Constraints"
}
```
`status` is one of:
`CREATED | MONITORING | DISRUPTED | PLANNING | AWAITING_APPROVAL | EXECUTING | RECOVERED | RECOVERY_FAILED`

### Flight
```json
{
  "id": "uuid",
  "leg": "outbound",
  "carrier": "AI",
  "flight_number": "AI131",
  "origin": "BOM",
  "destination": "LHR",
  "scheduled_departure": "2026-09-20T02:30:00+05:30",
  "scheduled_arrival": "2026-09-20T07:15:00+01:00",
  "status": "SCHEDULED",
  "next_poll_at": "2026-09-19T21:00:00+05:30"
}
```
`leg` is `outbound` or `return`.
`status` is `SCHEDULED | DELAYED | CANCELLED | DEPARTED | LANDED`.

### Hotel
```json
{
  "id": "uuid",
  "provider": "mock",
  "confirmation_number": "HTL-99213",
  "name": "Kensington Central",
  "city": "LON",
  "check_in": "2026-09-20",
  "check_out": "2026-09-25",
  "nightly_rate_inr": 9800,
  "modifiable": true,
  "status": "CONFIRMED"
}
```

### Constraints
Set by the traveller. The planner treats every field as a hard rule.
```json
{
  "hard_arrival_by": "2026-09-21T09:00:00+01:00",
  "hard_arrival_reason": "client presentation, cannot be missed",
  "max_fare_inr": 60000,
  "max_stops": 1,
  "cabin": "economy",
  "avoid_carriers": [],
  "auto_approve_under_inr": 45000
}
```

### Disruption
```json
{
  "id": "uuid",
  "trip_id": "uuid",
  "flight_id": "uuid",
  "kind": "CANCELLATION",
  "source": "simulated",
  "detected_at": "2026-09-19T14:03:11+05:30",
  "previous_status": "SCHEDULED",
  "new_status": "CANCELLED"
}
```
`kind` is `CANCELLATION | DELAY | SCHEDULE_CHANGE`.
`source` is `simulated | aviationstack | duffel`.

### FlightOption
What a provider returns from a search, normalised.
```json
{
  "id": "opt_1",
  "carrier": "BA",
  "flight_number": "BA138",
  "departure": "2026-09-20T13:40:00+05:30",
  "arrival": "2026-09-20T19:05:00+01:00",
  "stops": 0,
  "cabin": "economy",
  "fare_inr": 52400
}
```

### Rejection
Produced by the filter. **This is the money shot — never drop it.**
```json
{
  "option_id": "opt_4",
  "rule": "hard_arrival_by",
  "human_reason": "Arrives 11:40, misses hard deadline 09:00",
  "note": "would have been 8,000 cheaper"
}
```

### RecoveryPlan
```json
{
  "id": "uuid",
  "disruption_id": "uuid",
  "state": "AWAITING_APPROVAL",
  "evaluated_count": 14,
  "options": [ "FlightOption" ],
  "rejections": [ "Rejection" ],
  "chosen_option_id": "opt_1",
  "hotel_change": {
    "required": true,
    "new_check_in": "2026-09-21",
    "cost_delta_inr": -9800
  },
  "total_cost_delta_inr": 4200,
  "requires_approval": true,
  "approval_reason": "fare 52,400 exceeds auto-approve threshold 45,000",
  "explanation": "LLM prose, may be a templated fallback",
  "member_message": "LLM prose, may be a templated fallback"
}
```
`state` is `DRAFT | AWAITING_APPROVAL | APPROVED | REJECTED | EXECUTING | EXECUTED | FAILED`.

### AgentAction — the timeline
Every stage writes one of these. The frontend renders this table and nothing else.
```json
{
  "id": "uuid",
  "trip_id": "uuid",
  "at": "2026-09-19T14:03:11+05:30",
  "stage": "EVALUATED",
  "headline": "Evaluated 14 options, rejected 3 on policy",
  "detail": { },
  "duration_ms": 412
}
```
`stage` is one of:
`DETECTED | PLANNING | EVALUATED | AWAITING_APPROVAL | APPROVED | REBOOKED | HOTEL_SHIFTED | NOTIFIED | FAILED`
