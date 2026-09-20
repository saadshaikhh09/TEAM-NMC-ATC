# breakdown.md — repository audit + build log

Sections 0–6 are the original read-only audit (audit date 2026-09-20, HEAD
`7a1847b` "Demo-1 Failed" on `feat/a-core`). **Section 7 is the build log** and
records what has actually changed since. Where the audit and the build log
disagree, the build log is current.

---

## 7. Build log

### Phase A step 1 — config loading ✅ DONE

`core/config.py:25` now resolves `.env` from the repository root
(`Path(__file__).resolve().parents[2] / ".env"`), matching how `policy()` and
`status_utils.config_value()` already found it. `provider_flight` /
`provider_hotel` were renamed to `provider_flight_status` /
`provider_flight_search` / `provider_hotel` to match the names `.env` actually
declares. Nothing read the old names, so the rename was inert.

*Verified* — `settings()` from `api/` now returns the real file: `duffel_api_key`
len 55, `gemini_api_key` len 53, `aviationstack_api_key` len 32. Before the fix
all three were `""`. Inline `# comments` in `.env` are stripped correctly
(`provider_flight_status == 'mock'`).

Note this makes `.env` live for the first time. `DEMO_MODE=true` and
`DATABASE_URL` happen to equal the old hardcoded defaults, so behaviour is
unchanged today — but **`DEMO_MODE=false` now actually does something**, which
it did not before. Audit §4.7 is resolved.

### Phase A step 2 — the orchestrator ✅ DONE

New file `api/planner/orchestrate.py`. Subscribes to `disruption.detected` in
`main.py` rather than being called from `detection.py`, so the poller and
`/simulate` both reach it by one path and Person B's file is untouched. It runs
`constraints.filter` → `hotel_impact.assess` → `rank.rank` → `gate.decide`,
persists `recovery_plans` + `plan_options` + `plan_rejections` + `hotel_changes`,
and then either halts at `AWAITING_APPROVAL` or calls `executor.run` directly.

It never raises into its caller: `detect()` has already committed a disruption
by the time it runs, so a planning crash records `FAILED` and escalates the trip
to `RECOVERY_FAILED` instead of 500-ing the request that reported the problem.

Two supporting fixes, both root-cause rather than local:

- **`core/events.py`** — `emit()` now isolates subscribers in a try/except.
  Previously one raising subscriber took down both the websocket feed and the
  request that fired the event. Regression test in `tests/test_orchestrate.py`.
- **`llm/fallback.py:19`** — `_chosen()` matched the option on `id` before
  `option_id`. On a persisted `plan_options` row `id` is the table's UUID, so
  the lookup silently found nothing and the member message read "we recommend
  opt_1" instead of "we recommend BA BA138". Order reversed; both shapes now
  work. Regression test in `tests/test_fallback.py`.

*Verified* — `POST /simulate/cancellation` on the seeded Priya trip produces one
`recovery_plans` row, and it matches CONTRACT.md's worked example exactly:

| Field | Value |
|---|---|
| `evaluated_count` | 4 |
| `chosen_option_id` | `opt_1` (BA138, 52,400) |
| `total_cost_delta_inr` | **4200** — the contract's example figure |
| `approval_reason` | `Fare 52,400 exceeds auto-approve threshold 45,000` |
| rejection 1 | `opt_2` · `max_fare_inr` · Fare 61,500 exceeds cap 60,000 |
| rejection 2 | `opt_4` · `hard_arrival_by` · Arrives 11:40, misses hard deadline 09:00 · *would have been 8,000 cheaper* |

**The ₹8,000 refusal is now a database row, not a frontend fixture.** Audit §4.1
is resolved.

### Phase A step 3 — `GET /disruptions/{id}/plan` ✅ DONE

Added to `routes/approvals.py` (same owner, and it reuses the existing
`_response(plan)` serialiser so one shape serves all three routes). Returns the
newest plan for the disruption, 404 when there is none.

*Verified* — the path is in `/openapi.json` and returns the full contract shape
including `rejections`, `hotel_change`, `explanation` and `member_message`.
Audit §4.2 is resolved.

### Phase A step 5 — the six missing WebSocket events ✅ DONE

Done inside step 2 rather than as a separate pass, each emitted from the one
place that owns the transition so no caller can forget:

| Event | Emitted from |
|---|---|
| `trip.updated` | `core/state_machine.py` `advance()` — covers every transition |
| `plan.ready` | `planner/orchestrate.py` |
| `plan.awaiting_approval` | `planner/orchestrate.py` |
| `plan.executing` | `planner/orchestrate.py` (auto path) + `routes/approvals.py` (manual) |
| `plan.executed` | `executor/run.py` |
| `plan.failed` | `executor/run.py` `_fail()` + `orchestrate._escalate()` |

*Verified* — a live websocket capture of one simulate-then-approve run shows 7 of
the 8 contract events. The 8th, `plan.failed`, is covered by
`tests/test_orchestrate.py` (nothing failed in the happy run). Audit §4.8 is
resolved.

### Phase A step 6 — the other two gate paths ✅ DONE (fell out of step 2)

All three seeded travellers now behave as designed, no extra code:

| Traveller | Outcome | Ends at |
|---|---|---|
| Priya (BOM→LHR) | halts for approval — fare 52,400 over her 45,000 threshold | `AWAITING_APPROVAL` → approve → `RECOVERED` |
| Ananya (BLR→DXB) | **auto-executes, no click** — 30,000 under her 35,000 threshold | `RECOVERED` |
| Rohan (DEL→SIN) | escalates — fare 62,000 over his 30,000 threshold | `AWAITING_APPROVAL` |

### Phase A step 4 — browser verification 🟡 AWAITING YOUR EYE

Backend is green end to end; the by-eye check is yours. Reproduce with:

```
make reset
cd api && ./.venv/bin/uvicorn main:app --port 8000   # terminal 1
make web                                             # terminal 2
```

then click **Simulate a cancellation**. A headless equivalent of the same flow
is `api/tests/manual_vertical_slice.py` (not collected by pytest — it needs a
running server).

### Tests

`cd api && ./.venv/bin/python -m pytest tests -q` → **96 passed**, after
`make reset`. Was 91 passed / 2 failed at audit time; the 2 failures were
database drift and are gone. Three tests changed and two files were added:

- `tests/test_simulate.py`, `tests/test_poller.py` — these asserted that a
  detected trip **stops** at `DISRUPTED` with `DETECTED` as its only timeline
  row. That was the bug, written down as a spec. They now assert the plan gets
  built; the poller test no longer asserts a trip status it does not own.
- `tests/test_orchestrate.py` (new) — the refusal path (every option rejected →
  plan still persisted and published → `RECOVERY_FAILED`) and subscriber isolation.
- `tests/test_fallback.py` — added the persisted-row shape.

### ⚠️ Open issue found while building: orchestration latency

A **cold** `POST /simulate/cancellation` takes **8–12 seconds**, all of it the
two `llm/explain.py` narration calls burning `LLM_TOTAL_BUDGET_SECONDS=8` each
against the broken gemini-first chain. Measured: 8.15s (Priya, cold), 11.67s
(Ananya, cold), 0.03–0.07s once the plan hash is cached or the breaker has
opened. This is audit §4.4 and §4.5 hitting a new caller, and it is the next
thing the Groq swap should fix. **Re-measure this after Groq** — the target is
a cold simulate under ~2s.

### Frontend build baseline (for the later ui-ux port)

`cd web/app && npm run build` → JS **285.34 kB** (gzip 84.11 kB), CSS **35.68 kB**
(gzip 11.02 kB). This is the "before" number for the ≤15% growth budget.

### Answers to the audit's open questions, from your four plan changes

- Q1 `DEMO_MODE` — option (a) stands, and `scripts/live_status.py` will be the
  only thing that spends status quota.
- Q3 gemini — dropped entirely. New chain is `groq → xkiro → openrouter`.
- Q4 AviationStack — **kept**, not removed. Test `https://` first; if the free
  tier refuses it, keep `http` plus a loud startup warning and rotate the key
  post-hackathon. AeroDataBox stays primary.
- Q6 `ui-ux/` vs `web/design/stitch/` — pick one, delete the duplicate, port the
  markup *into* the existing React components. Not a static-HTML rebuild.
- Q7 `flight_details_autonomous_monitor` — dropped, no contract fields.

### Still to do

Step 4 by-eye gate → `scripts/live_status.py` + one real call → Groq swap +
latency report → ui-ux port → Phase B live Duffel/Nuitee → MCP last if time.

---

## 0. The one-paragraph answer

The backend has a well-tested planner, ranker, policy gate and executor — and
**none of them are reachable from the running application.** Disruption
detection stops after writing one timeline row. Nothing constructs a recovery
plan, the `recovery_plans` table has 0 rows, and the endpoint the frontend calls
to fetch a plan is not registered on the server at all. The frontend is complete
and correct, and renders the full recovery story **only against its own local
mock fixtures**. There is no working end-to-end demo today. There is also no MCP
server of any kind.

---

## 1. What exists and actually runs today

Verdicts are deliberately ungenerous. "Works" means *I ran it and saw it work in
the running application*, not "it has passing unit tests".

### Backend — reachable at runtime

| Module | Verdict | Evidence |
|---|---|---|
| `api/main.py` | **Works** | App boots; `curl :8000/health` → `{"ok":true}` |
| `api/core/db.py`, `core/models.py` | **Works** | `GET /trips` returns 3 seeded travellers |
| `api/routes/trips.py` (3 GETs) | **Works** | `/trips`, `/trips/{id}`, `/trips/{id}/timeline` all 200 |
| `api/routes/trips.py` `POST /trips` | **Stub** | `trips.py:198` — `raise NotImplementedError("A")` |
| `api/routes/trips.py` `POST /trips/extract` | **Partially works** | Route is live; the LLM behind it fails. See §1.3 |
| `api/routes/simulate.py` | **Works** | `POST /simulate/cancellation` → 201/409, writes a real `disruptions` row |
| `api/monitor/detection.py` | **Works** | Writes disruption, advances trip, records DETECTED, emits event |
| `api/monitor/poller.py`, `scheduler.py`, `runner.py` | **Works** | APScheduler tick observed repopulating `next_poll_at` |
| `api/core/audit.py`, `state_machine.py`, `events.py` | **Works** | DETECTED row observed in `/trips/{id}/timeline` |
| `api/routes/ws.py` | **Partially works** | Broadcasts, but only 2 of the 8 contract events are ever emitted |
| `api/core/quota.py` | **Works (as a blocker)** | `quota.py:73-74` — `DEMO_MODE=true` raises on every live status call |
| `api/routes/approvals.py` | **Unreachable** | Needs a `plan_id`; no plan row is ever created. See §4.1 |
| `api/routes/webhooks.py` | **Dead code in practice** | Requires a public HTTPS tunnel + a Duffel-booked order. Neither exists |

### Backend — tested but never invoked (dead code at runtime)

Verified by `grep -rn "from planner\|from executor" api --include="*.py"`:
the **only** non-test import is `api/routes/approvals.py:27`, which is itself
unreachable.

| Module | Verdict |
|---|---|
| `api/planner/constraints.py` (125L) | **Dead code** — filter + rejections. Never called by the app |
| `api/planner/rank.py` (80L) | **Dead code** — never called |
| `api/planner/hotel_impact.py` (32L) | **Dead code** — never called |
| `api/executor/gate.py` (80L) | **Dead code** — never called |
| `api/executor/run.py` (144L) | **Dead code** — only reachable via the unreachable approvals route |
| `api/llm/explain.py` | **Dead code** — nothing in a live path calls it |

These have unit tests and the tests pass. That is not the same as working.

### Backend — provider adapters

| Adapter | Verdict | Evidence |
|---|---|---|
| `providers/mock.py` | **Works** | The only provider the app actually uses |
| `providers/status_map.py` | **Works** | 91 passing tests cover it |
| `providers/duffel.py` | **Broken against the real API** | Key is valid (HTTP 201, 190 offers) but the adapter raises on every real response. See §4.3 |
| `providers/nuitee.py` | **Broken against the real API** | `GET /hotels/rates` → HTTP 200, `content-type: text/plain`, **empty body** → `JSONDecodeError` |
| `providers/aerodatabox.py` | **NOT TESTED** | I did not call it — 500 req/month is the whole project budget |
| `providers/aviationstack.py` | **NOT TESTED** | Same. `STATUS.md:19` records one successful call on 2026-09-19 |

### LLM layer

| Provider | Verdict | Measured |
|---|---|---|
| gemini | **Broken** | `404 Not Found` on `v1beta/models/gemini-2.0-flash:generateContent`, 0.49s, every call. First in the chain, so it trips the breaker on every cold start |
| openrouter | **Works but too slow** | Returned `'OK'` — in **31.72s**. `LLM_TIMEOUT_SECONDS=4`, so it normally times out |
| xkiro | **Works** | Returned `'OK'` in **2.58s**, inside the 4s budget |
| `llm/client.ask()` short prompt | **Works** | `'OK'` in 1.51s |
| `llm/extract.py` | **Broken** | Fails at **8.14s** — exactly `LLM_TOTAL_BUDGET_SECONDS=8`. `extract.py:29` inlines the entire Trip JSON schema into the prompt; no free-tier model finishes that inside the budget |
| `llm/fallback.py`, `llm/cache.py`, `llm/router.py` | **Works** | 91 passing tests; router never raises, breaker functions |

### Frontend

| Surface | Verdict |
|---|---|
| `web/app` (dashboard, :5174) | **Works** — builds clean, lints clean, renders against API or mocks |
| `web/site` (landing, :5173) | **Works** — independent build |
| `web/packages/tokens` | **Works** — shared Tailwind preset + CSS vars |

The dashboard is the healthiest part of the repo. Its problem is that the
backend never gives it a plan to render.

---

## 2. What is mocked or hardcoded

### Backend

| File:line | What is faked |
|---|---|
| `api/main.py:34` | `approvals.configure(MockFlightProvider(), MockHotelProvider())` — **hardcoded**. There is no provider factory for search/booking. `PROVIDER_FLIGHT_SEARCH` and `PROVIDER_HOTEL` in `.env` are read by nothing |
| `api/providers/mock.py:42` | `_OPTIONS = {...}` — the hardcoded flight option table the whole demo ranks over |
| `api/providers/mock.py:67-150` | Every method returns fixed data: `get_status`, `search`, `book`, hotel `search`/`prebook`/`book`/`cancel` |
| `api/routes/simulate.py:22` | `PRIYA_TRIP_ID = UUID("aaaaaaaa-1111-...")` — hardcoded demo trip id used when no `flight_id` is passed |
| `api/monitor/runner.py:23-24` | `if settings().demo_mode: return MockFlightProvider(), "simulated"` — a hard guard that cannot be overridden by `PROVIDER_FLIGHT_STATUS` |
| `api/core/quota.py:73-74` | `DEMO_MODE=true` → `raise QuotaExceeded("DEMO_MODE blocks live status API calls")`. **No live status call is possible today** |
| `db/seed.sql` | Three deterministic travellers. Correct and intentional |

### Frontend

| File | What is faked |
|---|---|
| `web/app/src/mocks/trips.ts` (65L) | One full Trip fixture |
| `web/app/src/mocks/plan.ts` (82L) | The RecoveryPlan — options, rejections, hotel change. **This is the only place a recovery plan exists anywhere in the running system** |
| `web/app/src/mocks/timeline.ts` (89L) | The full 9-stage agent timeline |
| `web/app/src/services/mock.ts:10-11` | `approvePlan`/`rejectPlan` return `{...recoveryPlan, state:'APPROVED'}` — fake writes |
| `web/app/src/services/index.ts:63-77` | `loadSnapshot()` silently falls back to mocks when the API fails |

The fallback **is** surfaced in the UI — the header shows "Mock data" — so it is
not disguised. But the demo currently *depends* on that fallback to look complete.

### Test fixtures that hide real-world bugs

| File:line | Problem |
|---|---|
| `api/tests/test_duffel.py:30` | Fixture uses `"2026-09-20T08:10:00Z"` (tz-aware). Real Duffel returns `"2026-09-22T09:40:00"` (naive). The test passes; the real call raises |
| `api/tests/test_duffel.py:22-23` | Fixture uses `"total_currency": "INR"`. Real Duffel returned **USD**. No conversion exists anywhere |

---

## 3. Integration status table

| Integration | EXISTS? | WIRED TO UI? | LIVE KEY? | TESTED? |
|---|---|---|---|---|
| **Flight MCP** | ❌ **NOT FOUND IN REPO** — cut at hour 0 (`STATUS.md:96`). `providers/base.py` is an MCP-*shaped* ABC, not a server or client | n/a | n/a | n/a |
| **Hotel MCP** | ❌ **NOT FOUND IN REPO** — same | n/a | n/a | n/a |
| **Flight status** (AeroDataBox) | ✅ `providers/aerodatabox.py` | ⚠️ Indirectly, via the monitor | ✅ set (len 36) | ❌ Never called. Blocked by `DEMO_MODE` |
| **Flight status** (AviationStack) | ✅ `providers/aviationstack.py` | ⚠️ Indirectly | ✅ set (len 32) | ⚠️ One call on 2026-09-19 per `STATUS.md:19`. **`.env` uses `http://`, not https — key travels in the query string in plaintext** |
| **Flight search/book** (Duffel) | ✅ `providers/duffel.py` | ❌ Never instantiated — `main.py:34` hardcodes the mock | ✅ **valid — returned 190 real offers** | ❌ **Adapter crashes on every real response** |
| **Hotel lifecycle** (Nuitee/LiteAPI) | ✅ `providers/nuitee.py` | ❌ Never instantiated | ✅ set (len 41) | ❌ **HTTP 200, empty `text/plain` body → JSONDecodeError** |
| **LLM — reasoning/decision** | ⚠️ `llm/explain.py` exists | ❌ **Dead code — nothing calls it** | ✅ 3 keys set | ❌ Never invoked in a live path |
| **LLM — extraction** | ✅ `llm/extract.py` | ✅ `POST /trips/extract` → `BookingImport.tsx` | ✅ | ❌ **Fails at the 8s budget every time** |
| **LLM — transport** | ✅ `llm/router.py` + 3 adapters | n/a | gemini ❌404 · openrouter ✅31.7s · xkiro ✅2.6s | ✅ Probed live today |
| **Rebooking / execution** | ✅ `executor/run.py` | ❌ Unreachable | uses mock providers | ❌ Never runs |
| **Notification** | ⚠️ `llm/explain.py` + `fallback.py` produce text | ❌ Only via a plan that never exists | n/a | ❌ |
| **Payment** | ❌ **NOT FOUND IN REPO** | n/a | n/a | n/a |
| **Weather / Maps** | ❌ **NOT FOUND IN REPO** | n/a | n/a | n/a |
| **Frontend → backend** | ✅ `services/api.ts` | ✅ **All 10 served endpoints wired** | n/a | ✅ Verified through the vite proxy today |

**SDKs in use:** no vendor SDKs. Every provider and every LLM adapter is
hand-rolled `httpx` (`requirements.txt`: `httpx==0.27.2`). No `openai`, no
`google-generativeai`, no `duffel-api`, no `mcp` package anywhere.

---

## 4. The critical gap list

Ordered by how much each one blocks.

### 4.1 — No orchestrator between detection and a recovery plan  ⛔ BLOCKS EVERYTHING

`monitor/detection.py` ends at `emit("disruption.detected", ...)` (line 66).
Nothing then runs the planner. Verified:

```
$ grep -rn "from planner\|from executor" api --include="*.py" | grep -v tests
api/routes/approvals.py:27:    from executor.run import run
```

```
$ psql -U concierge -d concierge -c "select count(*) from recovery_plans;"
 0
```

Consequence: `planner/`, `executor/` and `llm/explain.py` — roughly 460 lines of
tested logic, the actual product — never execute. The trip reaches `DISRUPTED`
and stops there forever.

### 4.2 — `GET /disruptions/{id}/plan` is not registered  ⛔ BLOCKS THE WHOLE UI STORY

CONTRACT.md line 48 specifies it. The live server does not have it:

```
$ curl -s :8000/openapi.json | jq -r '.paths | keys[]'
/approvals/{plan_id}/approve   /health          /simulate/delay   /trips/{trip_id}
/approvals/{plan_id}/reject    /simulate/cancellation   /trips    /trips/{trip_id}/timeline
/trips/extract                 /webhooks/duffel
```

The frontend calls it correctly (`services/api.ts:22`) and gets a 404, so
`planFor()` returns null on every live load. **On the live API path the plan
banner, `FlightAlternativesCard`, `RejectionPanel`, `ApprovalModal` and
`ConfirmationCard` never render.** The ₹8,000 refusal — the entire pitch — exists
only in `web/app/src/mocks/plan.ts`.

### 4.3 — Duffel adapter cannot parse a real Duffel response  ⛔ BLOCKS LIVE FLIGHT DATA

Two independent bugs. The key itself is fine — raw HTTP returned **HTTP 201 with
190 offers** (sample: `KU 0304`, `206.66 USD`).

1. **Timezone.** `duffel.py:139` → `status_utils.py:25` raises
   `ValueError: departure has no timezone`. Real Duffel sends
   `"2026-09-22T09:40:00"` with no offset; `parse_utc` demands one.
2. **Currency.** `duffel.py:145` — `fare_inr = int(total_amount)`. No FX
   conversion exists in the repo. A real 206.66 USD offer becomes `fare_inr=206`,
   which sails under every constraint (fare cap 60,000, auto-approve 45,000). The
   gate would auto-approve everything.

### 4.4 — LLM extraction cannot complete inside its budget  🔶 BLOCKS THE "AI moment"

`extract()` fails at 8.14s against `LLM_TOTAL_BUDGET_SECONDS=8`. Cause:
`extract.py:29` inlines `Trip.model_json_schema()` into the prompt. Combined with
gemini 404-ing first and openrouter taking 31.7s, the budget is gone before a
working provider gets a real attempt.

### 4.5 — gemini is misconfigured  🔶

`404` on `v1beta/models/gemini-2.0-flash:generateContent`. The configured key
begins `AQ.` — an OAuth-style token, not a `AIza…` Generative Language API key.
Being first in `LLM_CHAIN`, it burns a round trip and trips the breaker on every
cold start before a working provider is tried.

### 4.6 — Nuitee hotel search returns an empty body  🔶 BLOCKS LIVE HOTEL DATA

`GET {NUITEE_BASE}/hotels/rates` → HTTP 200, `content-type: text/plain`, body
empty. LiteAPI v3.0's rates endpoint is a **POST** with a JSON body; the adapter
sends a GET with query params (`nuitee.py:60-72`). Likely wrong method and shape,
not a bad key — but unproven.

### 4.7 — Config is read from two different roots  🔶 SILENT MISCONFIGURATION

- `core/config.py:25` — `env_file = ".env"`, resolved relative to the **current
  working directory**. `make api` runs `cd api && uvicorn …`, and **`api/.env`
  does not exist.** So `settings()` silently uses the hardcoded defaults in
  `config.py:10-22`, not your `.env`.
- It works today only by coincidence: `DATABASE_URL` in `.env` is byte-identical
  to the default, and `demo_mode` defaults to `True`. **Setting `DEMO_MODE=false`
  in `.env` would change nothing.**
- Meanwhile `providers/status_utils.py:15` and `router.configure()`'s
  `load_dotenv()` *do* find the repo-root `.env`. Two config paths, two roots.
- Name mismatch: `config.py:13-14` declares `provider_flight` / `provider_hotel`;
  `.env` declares `PROVIDER_FLIGHT_STATUS` / `PROVIDER_FLIGHT_SEARCH` /
  `PROVIDER_HOTEL`. Only `PROVIDER_FLIGHT_STATUS` is read by anything
  (`runner.py:25`). The other two are inert.

### 4.8 — Only 2 of 8 contract WebSocket events are emitted  🔸

```
$ grep -rn 'emit(' api --include="*.py" | grep -v tests | grep -v "def emit"
api/monitor/detection.py:66   →  disruption.detected
api/core/audit.py:43          →  action.recorded
```

`plan.ready`, `plan.awaiting_approval`, `plan.executing`, `plan.executed`,
`plan.failed`, `trip.updated` are **NOT FOUND IN REPO** as emit sites. The
frontend switch handles all eight, so it is ready; the backend simply never
sends six of them. This is a direct consequence of 4.1.

### 4.9 — `DEMO_MODE=true` hard-blocks every live status call  🔸 BY DESIGN

`quota.py:73-74` raises on any live status call while `DEMO_MODE=true`. This is
deliberate quota protection (500 req/month total, ~30 rehearsals planned), not a
bug — but it means **"use real flight data" and "keep the quota guard" are
mutually exclusive as currently written.** See Open Questions.

### 4.10 — `POST /trips` is a stub  🔸

`trips.py:198` — `raise NotImplementedError("A")`. Extraction can therefore only
ever preview a trip, never save one. The UI already states this honestly.

---

## 5. Shortest path to a working demo

Each step is verifiable by running the command shown. **DEMO-CRITICAL** steps are
required for a demo to exist at all.

### Phase A — make the existing logic reachable (mock providers, no network)

> This alone produces a complete, honest, end-to-end demo. Do this before
> touching any live integration.

1. **DEMO-CRITICAL — Fix config loading.** Point `core/config.py:25` at the repo
   root (`Path(__file__).resolve().parents[2] / ".env"`) so `settings()` reads
   the real file. Reconcile `provider_flight`/`provider_hotel` with the `.env`
   names.
   *Verify:* `python -c "from core.config import settings; print(settings())"`
   from `api/` shows values from `.env`, not defaults.

2. **DEMO-CRITICAL — Add the orchestrator.** After `detect()` commits, run
   `planner.constraints` → `planner.rank` → `planner.hotel_impact` →
   `executor.gate`, persist a `recovery_plans` row plus `plan_options` /
   `plan_rejections` / `hotel_changes`, record `PLANNING` + `EVALUATED`, and emit
   `plan.ready` / `plan.awaiting_approval`.
   *Verify:* `POST /simulate/cancellation` then
   `psql -c "select id,state,evaluated_count from recovery_plans;"` → one row.

3. **DEMO-CRITICAL — Add `GET /disruptions/{id}/plan`.** Reuse the existing
   `approvals._response(plan)` serialiser so one shape serves both routes.
   *Verify:* `curl :8000/disruptions/<id>/plan | jq .rejections` → non-empty.

4. **DEMO-CRITICAL — Run the vertical slice in the browser.** `make reset`, start
   API + `make web`, click **Simulate a cancellation**.
   *Verify by eye:* timeline fills past DETECTED; rejection panel shows the
   ₹8,000 refusal; approval modal opens; approve → `EXECUTED` +
   ConfirmationCard. Header must read **Live**, not **Mock data**.

5. **DEMO-CRITICAL — Emit the remaining six events** from the orchestrator and
   executor.
   *Verify:* browser devtools WS frames show `plan.ready`, `plan.executing`,
   `plan.executed`.

6. Nice-to-have — auto-approve path for Ananya, escalation path for Rohan.
   *Verify:* fire on each trip; one executes with no click, one halts at
   `AWAITING_APPROVAL`.

### Phase B — swap in live data (only after Phase A is green)

7. **DEMO-CRITICAL if "real calls" is non-negotiable — Fix the Duffel adapter.**
   Accept naive datetimes (treat as origin-airport local, or UTC), and add an
   explicit USD→INR conversion with the rate and its source recorded on the
   option.
   *Verify:* `DuffelFlightProvider().search("BOM","LHR",…)` returns options with
   tz-aware datetimes and `fare_inr` in the tens of thousands.

8. **Add a provider factory** so `main.py:34` stops hardcoding mocks and honours
   `PROVIDER_FLIGHT_SEARCH` / `PROVIDER_HOTEL`.
   *Verify:* `PROVIDER_FLIGHT_SEARCH=duffel` produces Duffel option ids in the
   plan.

9. **Fix Nuitee** — almost certainly POST-with-body on LiteAPI v3.0.
   *Verify:* `search("LON", …)` returns ≥1 `HotelOption`; then a full
   prebook → book → cancel round trip in sandbox.

10. **Fix the LLM chain.** Replace the gemini key with a real Generative Language
    API key (or drop gemini from `LLM_CHAIN`), demote the 31s openrouter model,
    put xkiro first. Raise `LLM_TOTAL_BUDGET_SECONDS` for extraction only, or
    shrink the prompt in `extract.py:29` to a hand-written field list instead of
    the full JSON schema.
    *Verify:* `POST /trips/extract` returns a Trip instead of 503.

11. Nice-to-have — `POST /trips` so an extracted trip can actually be saved.

12. Nice-to-have — one live AeroDataBox status call on stage. **Costs quota; see
    Open Questions.**

---

## 6. Open questions for you

1. **`DEMO_MODE` vs "real calls".** Your Phase 2 rule 3 says every call must fire
   against real endpoints. But `quota.py:73` hard-blocks all live *status* calls
   while `DEMO_MODE=true`, and AeroDataBox + AviationStack are 500 requests/month
   **total** for the project, with ~30 rehearsals planned. Which do you want?
   (a) keep `DEMO_MODE=true`, live Duffel + Nuitee + LLM only, simulated status;
   (b) `DEMO_MODE=false` and spend real status quota on every rehearsal.
   I recommend (a) — it satisfies "real calls" for three of four integrations and
   is what `docs/DEMO_SCRIPT.md` already promises out loud.

2. **There is no MCP anywhere.** Your brief names a "flight MCP" and "hotel MCP".
   They do not exist and were cut on purpose (`STATUS.md:96`, `ARCHITECTURE.md:77`).
   Do you want me to (a) leave the direct `providers/` adapters as they are, or
   (b) actually build MCP servers wrapping them? (b) is real work and buys nothing
   for the demo, but it would make the brief literally true.

3. **Gemini key.** The configured value starts `AQ.` and 404s. Is that an OAuth
   token pasted into the wrong variable? A Generative Language API key from
   [aistudio.google.com/apikey](https://aistudio.google.com/apikey) starts `AIza`.
   Should I just drop gemini from `LLM_CHAIN` and lead with xkiro (2.6s, works)?

4. **`AVIATIONSTACK_BASE` is `http://`, not `https://`.** `CONTRACT.md:19` says
   HTTPS was verified and warns the key is in the query string. Over plain HTTP
   that key is sent in cleartext. Was this downgraded deliberately (free tier
   often blocks HTTPS)? If so, that provider should not be used at all.

5. **Duffel currency.** Real offers come back in USD. What INR rate do you want —
   a hardcoded constant recorded in `policy.yaml`, or a live FX call? Nothing in
   the repo converts currency today.

6. **`ui-ux/` vs `web/design/stitch/`.** These are duplicates (`diff -rq` shows
   only a stray `.DS_Store` and a `DESIGN (1).md`). Which is the source of truth?
   Note that `ui-ux/` is **static HTML mockups**, not React — the real component
   library is `web/app/src/components/` (18 components, already built from those
   mockups). Your Phase 2 rule 1 says reuse `ui-ux/` as-is; I read that as "reuse
   the existing React components in `web/app`, don't redesign" — confirm?

7. **`flight_details_autonomous_monitor_animated_interactive`** is the one mockup
   with no implementation. Its three sections — *50-Minute Lead Warning*, *Seat &
   Cabin Parity*, *Autonomous Compensation* — have **no corresponding field in
   CONTRACT.md**, and refund processing is explicitly cut (`ARCHITECTURE.md:125`).
   Drop it, or extend the contract?

8. **Branch.** HEAD is `feat/a-core` at "Demo-1 Failed", which is also
   `origin/main`. `dev` is the stated PR target. Which branch should Phase 2 work
   land on?

---

## Appendix — inventory

### `ui-ux/` (13 folders; static HTML mockups + 2 design specs)

| Folder | Contents | Rendered by |
|---|---|---|
| `aero_concierge` | `DESIGN.md` — palette, type, spacing | `web/packages/tokens/` |
| `aero_concierge_premium` | `DESIGN.md` | same |
| `atc_404_disrupted_flight_path_animated_interactive` | `code.html` 649L | `EmptyState.tsx` |
| `atc_concierge_portal_minimal_radar_visualization` | `code.html` 520L | `RadarPanel.tsx` |
| `atc_concierge_profile_dropdown_panel_animated_interactive` | `code.html` 540L | `ProfileMenu.tsx` |
| `atc_confirmation_page_animated_interactive` | `code.html` 815L | `ConfirmationCard.tsx` |
| `atc_flight_alternatives_loading_state` | `code.html` 495L | `Skeletons.tsx` |
| `atc_flight_status_loading_state` | `code.html` 284L | `Skeletons.tsx` |
| `atc_hotel_policy_loading_state` | `code.html` 405L | `Skeletons.tsx` |
| `atc_realistic_google_maps_hotel_policy_concierge` | `code.html` 1253L | `HotelPolicyCard.tsx` (abstract locator, no map SDK) |
| `flight_cancellation_alternatives_animated_interactive` | `code.html` 1078L | `FlightAlternativesCard.tsx` |
| `flight_details_autonomous_monitor_animated_interactive` | `code.html` 793L | **NOT IMPLEMENTED** — see Q7 |
| `high_detail_satellite_..._london_heathrow` | `screen.png` only, no code | **CUT** (`ARCHITECTURE.md:124`) |
| `live_flight_status_animated_interactive_concierge` | `code.html` 1090L | `LiveFlightStatusCard.tsx` |

### `web/app/src/components/` (18 components, 2537 LOC total)

`AgentTimeline` · `ApprovalModal` · `AppShell` · `BookingImport` · `ConfirmationCard` ·
`EmptyState` · `FlightAlternativesCard` · `HotelPolicyCard` · `LiveFlightStatusCard` ·
`OperationsBar` · `ProfileMenu` · `RadarPanel` · `RejectionPanel` · `Reveal` ·
`Skeletons` · `Tooltip` · `TripCard` · plus `screens/Dashboard.tsx`

### Dependencies

**Python** (`api/requirements.txt`, 11 packages): `fastapi==0.115.0`,
`uvicorn[standard]==0.30.6`, `sqlalchemy==2.0.35`, `psycopg[binary]>=3.2.4`,
`pydantic==2.9.2`, `pydantic-settings==2.5.2`, `python-dotenv==1.0.1`,
`httpx==0.27.2`, `apscheduler==3.10.4`, `pyyaml==6.0.2`, `pytest==8.3.3`.
No `pyproject.toml` at the repo root. No MCP, LLM or vendor SDK packages.

**Node** (identical in `web/app` and `web/site`): runtime is React 19 + three
`@fontsource-variable` packages and nothing else. Dev: vite 8, TypeScript 6,
tailwind 3.4, oxlint, postcss, autoprefixer.

### Environment keys (`/.env` — values redacted; presence only)

**Set:** `DATABASE_URL`, `AERODATABOX_API_KEY`, `AVIATIONSTACK_API_KEY`,
`DUFFEL_API_KEY`, `NUITEE_API_KEY`, `GEMINI_API_KEY`, `OPENROUTER_API_KEY`,
`XKIRO_API_KEY`.
**Empty:** none.
**Not present as files:** `web/app/.env`, `web/site/.env` (only `.env.example`).

Models configured: `gemini-2.0-flash`, `nvidia/nemotron-3-ultra-550b-a55b:free`,
`qwen/qwen3.8-omni-flash:free`.

### Tests

`cd api && ./.venv/bin/python -m pytest tests -q` → **91 passed, 2 failed**.
Both failures are database drift, not code: `test_trips.py` expects the pristine
seed but detection has nulled `next_poll_at` and written a timeline row. Run
`make reset` first and they pass.

### Git history (72 commits, 2026-09-19 → 2026-09-20)

Four contributors: Shahid-Malek (A — core/db/planner/executor/llm),
VishnuPatel9009 (B — monitor/providers), Atif Malik (D — duffel/nuitee/docs),
saadshaikhh09 (C — web). Ledger IDs A1–A16, B1–B8, C0–C5, D0–D8 are all committed.
HEAD is `7a1847b` "Demo-1 Failed" — consistent with this audit: every part was
built, none of the parts were connected.
