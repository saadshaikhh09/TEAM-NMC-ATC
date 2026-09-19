# STATUS — the single source of truth for what is done

Update your own rows only. Update them **when the verify command passes**, not
when you think you are finished. A row marked DONE that does not verify is worse
than a row marked BLOCKED, because it makes three other people build on air.

States: `TODO` · `WIP` · `DONE` · `BLOCKED` · `CUT`

---

## Hour-0 gate (all four, before any product code)

**Each verification call below costs real monthly quota. ONE call each. Do not
loop, do not retry in a shell history, do not let anyone "just check it again".**

| Item | Owner | State | Note |
|---|---|---|---|
| AeroDataBox: one status call succeeds | B | TODO | 1 of 500 spent |
| AviationStack: one status call succeeds | B | DONE | AI131 returned DEPARTED on 2026-09-19; 1 quota-guarded call. |
| Duffel test: one offers call succeeds | D | WIP | 30/min; key unconfigured in .env, schema documented |
| Nuitee sandbox: search → prebook → book → cancel round trip | D | WIP | free sandbox; key unconfigured in .env, lifecycle documented |
| LLM key returns a completion | A | TODO | |
| Repo pushed, everyone cloned | A | TODO | |
| CONTRACT.md read by all four | all | TODO | |
| Hackathon rubric + submission format confirmed | D | DONE | Sun 17:00 deadline; repo+video+writeup; docs/SUBMISSION.md |
| **Everyone has read core/quota.py** | all | TODO | 500/month is the whole budget |

---

## Build ledger

| ID | Deliverable | Owner | Depends on | State | Verify with |
|---|---|---|---|---|---|
| A1 | `db/schema.sql` applies clean | A | — | DONE | `make reset` |
| A2 | `core/models.py` | A | A1 | DONE | `python -c "import core.models"` |
| A3 | `core/audit.py` record() | A | A2 | DONE | `pytest tests/test_audit.py` |
| A4 | `core/state_machine.py` | A | A2 | DONE | `pytest tests/test_state.py` |
| A5 | `db/seed.sql` — 3 travellers | A | A1 | DONE | `make reset` then GET /trips |
| B1 | `providers/base.py` signatures | B | — | DONE | `python -c "import providers.base"` |
| B2 | `providers/mock.py` all 4 methods | B | B1 | DONE | `pytest tests/test_mock.py` |
| B3 | `routes/simulate.py` | B | A2,A3 | DONE | `curl -XPOST :8000/simulate/cancellation` |
| B4 | `routes/ws.py` broadcast | B | A3 | DONE | browser console shows event |
| B5 | `monitor/scheduler.py` tiered poll | B | A2 | DONE | `pytest tests/test_scheduler.py` |
| B6 | `providers/aerodatabox.py` (primary) | B | B1,A12 | DONE | `pytest tests/test_status_map.py` |
| B7 | `providers/aviationstack.py` (cross-check) | B | B1,A12 | DONE | one live call, once |
| B8 | `providers/status_map.py` | B | — | DONE | `pytest tests/test_status_map.py` |
| C1 | Independent mock-first `web/app` + `web/site` builds | C | — | DONE | `npm run dev` in each surface |
| C2 | Trip card | C | C1 | DONE | visual |
| C3 | **Agent timeline** | C | C1 | DONE | visual |
| C4 | Rejection panel | C | C1 | DONE | visual |
| C5 | Approval modal | C | C1 | DONE | visual |
| C6 | WS live updates | C | B4 | DONE | visual — all 8 types switched; only `disruption.detected` + `action.recorded` are emitted by the API today |
| C7 | Flight alternatives + live status + hotel policy + confirmation cards | C | C1 | DONE | `npm run build && npm run lint` clean; all four verified in browser on the mock path |
| C8 | Radar panel, profile menu, empty state, loading skeletons | C | C1 | DONE | visual — skeletons and empty state verified by forcing a stalled and a failed load |
| C9 | Interaction layer: scroll reveal, hover lift, tooltips | C | C7,C8 | DONE | tooltip opens on hover and keyboard focus; no horizontal overflow at 390/768/1440 |
| C11 | Operations bar (trip switcher + simulate) and booking import | C | C1,B3 | DONE | `npm run build && npm run lint` clean; `/simulate/*` and `/trips/extract` verified against the running API |
| D1 | `providers/duffel.py` search + book | D | B1 | DONE | `pytest tests/test_duffel.py` |
| D2 | `HotelProvider.change_dates()` cancel-then-rebook | D | D3 | DONE | `pytest tests/test_hotel_change.py` |
| D3 | `providers/nuitee.py` full lifecycle | D | B1 | DONE | `pytest tests/test_nuitee.py` |
| D4 | Notification panel data | D | A3 | DONE | `pytest tests/test_timeline_copy.py` |
| D5 | Demo script written | D | — | DONE | read aloud in 90s |
| D6 | Backup video recorded | D | all | DONE | `docs/BACKUP_VIDEO.md` |
| D7 | Submission writeup | D | — | DONE | `docs/SUBMISSION.md` |
| D8 | *(optional, h18+)* Duffel webhook receiver | D | D1 | DONE | `pytest tests/test_webhooks.py` |
| A6 | `planner/constraints.py` filter + rejections | A | B1,A2 | DONE | `pytest tests/test_filter.py` |
| A7 | `planner/rank.py` | A | A6 | DONE | `pytest tests/test_rank.py` |
| A8 | `planner/hotel_impact.py` | A | A2 | DONE | `pytest tests/test_hotel.py` |
| A9 | `executor/gate.py` approval threshold | A | A7 | DONE | `pytest tests/test_gate.py` |
| A10 | `executor/run.py` | A | A9,B1 | DONE | `pytest tests/test_executor.py` |
| A11 | `llm/fallback.py` templated strings | A | — | DONE | `pytest tests/test_fallback.py` |
| A13 | `llm/router.py` chain + breaker | A | A11 | DONE | returns None with all keys blank |
| A14 | `llm/cache.py` | A | A2 | DONE | second identical call makes no request |
| A15 | `llm/` explain + draft + extract | A | A13 | DONE | works with every key blank |
| A12 | `core/quota.py` budget guard | A | A2 | DONE | `pytest tests/test_quota.py` |

---

## Checkpoints

| Hour | Must be true | If not |
|---|---|---|
| 1 | Hour-0 gate all DONE, CONTRACT frozen | Drop Duffel, mock only |
| 5 | B3 + B4 + A1..A3 DONE — simulate fires an event in the browser | Cut hotel leg (A8) |
| 9 | A6 + A7 DONE — ranked options with rejections | Cut LLM extraction |
| 13 | End-to-end manual path: cancel → plan → approve → rebooked | Freeze, polish only |
| 16 | A9 autonomous path DONE | Ship manual only, say so |
| 26 | **HARD FREEZE.** Seed, record, submit | — |

---

## Decision log

Append a line whenever you cut something or change a shape. One line, no prose.

- (hour 0) Chose Aviationstack for status, Duffel for search/book, Mock as demo default.
- (hour 0) Temporal rejected: Postgres row + next_poll_at gives resumability free.
- (hour 0) MCP layer cut from build; provider interface kept MCP-shaped.
- (hour 0) Gmail ingestion cut; paste-booking extraction replaces it.
- (hour 0) Hotel map cut.
- (A16) Machine-readable timestamps are UTC; Flight and Constraints add airport-local display fields.
- (B3/B5) Added `aerodatabox` to `Disruption.source` for the primary live polling path.
- (B7) AviationStack HTTPS worked with the configured key; public free pricing now lists 100 requests/month, so A should confirm the account cap before enabling routine live polling.
- (A7) ScoredOption is planner-internal; API still returns FlightOption[] in ranked order. Hotel cost per option is injected by the caller.
- (A12/B7) Confirmed AeroDataBox and AviationStack quotas are 500 requests/month each.
- (A14) LLM cache added as `llm_cache.responses`, outside schema public so a psql `make reset` keeps rehearsal copy; `docker compose down -v` still wipes it.
- (C0) App palette is Aero Concierge; landing retains its authored navy/sky palette.
- (C7) TripCard no longer renders flight legs or the hotel; LiveFlightStatusCard and HotelPolicyCard own those, so live status is not duplicated in two places.
- (C8) The 404 design ships as EmptyState, not a route. The app has no router, so a 404 page would be unreachable; the artwork covers "API and mocks both failed" instead.
- (C8) HotelPolicyCard draws an abstract locator, not a map. No map SDK and no key budget, and a fake map on a trust-critical screen is worse than no map.
- (C9) Motion is CSS-only, no animation dependency, and every animation is disabled under `prefers-reduced-motion`.
- (C11) Mocks keep read surfaces alive; they do not fake new writes. `/simulate/*` and `/trips/extract` are disabled on the mock path with the reason on screen, because a simulate that changes nothing and an extraction that returns Priya would both misreport what happened.
- (C11) `/trips/extract` renders as a preview that says nothing was saved. `llm/extract.py` validates and returns a Trip without touching the database, and storing one needs `POST /trips`, which is still `NotImplementedError`.
- (C11) `GET /health` left unwired. It is not in CONTRACT.md and the WS status already drives the connection indicator, so a second liveness signal would only be able to disagree with the first.
- (C11) **Blocked, not cut:** `GET /disruptions/{id}/plan` (CONTRACT line 48) is not registered on the server — `/openapi.json` has no such path, so `planFor()` returns null on every live load. Nothing calls `planner/` either: `detect()` stops at DETECTED, so no `recovery_plans` row is ever written. The plan banner, alternatives, rejection panel, approval modal and confirmation card therefore render on the mock path only. The frontend already calls the endpoint correctly and needs no change when A lands it.
- (C10) `types/index.ts` now marks six fields nullable to match the API's Pydantic models: `Flight.next_poll_at`, `Hotel.confirmation_number`, `Hotel.nightly_rate_inr`, `Constraints.max_fare_inr`, `Constraints.hard_arrival_by_local`, `AgentAction.duration_ms`. The types previously said required; every one of them rendered wrong against a live API. Not a CONTRACT change — the frontend types were wrong about what the backend already sends.
