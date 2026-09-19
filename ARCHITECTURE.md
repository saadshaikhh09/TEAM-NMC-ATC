# ARCHITECTURE.md

The structure of this project, and the reasoning behind the parts that look
like they could have been done differently. Read this before `CONTEXT.md`'s
session protocol makes sense.

---

## 1. The shape

```
                  ┌──────────────────────────┐
                  │     Web dashboard        │
                  │  trip · timeline · approve│
                  └────────────┬─────────────┘
                     REST      │      WebSocket
                  ┌────────────▼─────────────┐
                  │        FastAPI           │
                  └────────────┬─────────────┘
                               │
   ┌──────────────┐  ┌─────────▼──────────┐  ┌──────────────┐
   │ LLM sidecar  ├╌╌┤   Orchestrator     ├╌╌┤  PostgreSQL  │
   │ explain·draft│  │ state machine+audit│  │ owns state   │
   └──────────────┘  └─────────┬──────────┘  └──────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
  ┌───────────┐        ┌───────────────┐      ┌─────────────┐
  │  Monitor  │        │Recovery planner│      │  Executor   │
  │detect+sim │        │ filter + rank  │      │policy gated │
  └─────┬─────┘        └───────┬────────┘      └──────┬──────┘
        └──────────────────────┼──────────────────────┘
                               ▼
                  ┌──────────────────────────┐
                  │    Provider adapters     │
                  │  one interface, MCP-ready│
                  └────────────┬─────────────┘
                 ┌─────────────┼─────────────┐
                 ▼             ▼             ▼
               Mock      Aviationstack     Duffel
            (demo default)   (status)    (search/book)
```

Dashed lines are non-authoritative: the LLM and the database hang off the
orchestrator but neither drives the flow.

---

## 2. Five decisions, and why

### The LLM has no downward arrow
The original design draft had `AI Agent Runtime` as a peer of the state machine
with its own path to the tool layer. That gives the model a private route to
the booking adapters, which contradicts the whole premise. Here it receives a
finished plan and returns prose. It cannot reach an adapter, cannot write a
row, cannot book anything.

That is not a limitation to apologise for. It is the strongest claim we have in
Q&A, and it is why our agent can never announce a rebooking that did not
happen.

### One orchestrator, not a state machine *and* a workflow engine
Two components that both claim to advance trip state is an ownership ambiguity
that costs hours at hour 16. One component owns transitions; everything else
calls `state_machine.advance()`.

### No Temporal, no Celery, no Redis
Durable execution solves a problem we do not have. The resume point is already
in the database: `flights.next_poll_at` plus `trips.status`. A poller that
reads state from Postgres on every tick is resumable by construction — kill the
process, restart it, it picks up where it left off.

Temporal would cost a server, a worker, the SDK, and workflow determinism
constraints (no `datetime.now()`, no random, no direct IO in workflow
functions) that bite at 2am when a replay diverges and nobody knows why.

### MCP is cut from the build, kept in the shape
`providers/base.py` is deliberately tool-shaped: four verbs, flat arguments,
normalised returns. Wrapping it in an MCP server later is mechanical. We get to
say truthfully that the provider layer is a tool interface, without betting the
demo on cross-process protocol debugging at hour 15.

### The hotel leg is a real write, not a mock
Nuitee/LiteAPI's sandbox performs an actual `prebook → book → cancel` round
trip and returns real confirmation numbers, free and with no card. That upgrades
the hotel leg from something we simulate to something we genuinely do.

One consequence to model honestly: **Nuitee has no modify endpoint.** A date
change is cancel-then-rebook, which means a real failure window — if `book()`
fails after `cancel()` succeeded, the traveller has no room. `HotelProvider`
exposes `change_dates()` rather than pretending `modify()` exists, and the
timeline records `HOTEL_SHIFTED` only after the rebook returns. On failure it
audits `FAILED` and escalates. A judge who asks "what happens if the second
call fails" should get a real answer.

### Gmail ingestion replaced by paste-extraction
An unverified Google app, a sensitive scope, test-user setup and IMAP parsing —
a full person-day and the most fragile thing we could put on stage. The paste
flow gives the same AI-extraction moment in one hour. If we get ahead, the
Gmail feature worth adding is **drafting** a message to the hotel, not reading
the inbox: a draft landing in a real inbox is an unfakeable write to the outside
world, and reading produces something you could have typed yourself.

---

## 3. The eight features

Eight is the number. When someone proposes a ninth at hour 14, the answer is no.

| # | Feature | Owner | Why it is in |
|---|---|---|---|
| 1 | Manual trip entry + paste-booking extraction | A | Our only guaranteed input path |
| 2 | Traveller constraints, stored per person | A | The differentiator |
| 3 | Tiered polling scheduler | B | Real engineering, one pure function, one slide |
| 4 | Detection + declared simulate endpoint | B | Nothing works without it |
| 5 | Filter with logged rejections, then rank | A | Makes #2 visible |
| 6 | Hotel impact + **real sandbox rebooking** | A + D | In the brief; Nuitee makes this an actual write, not a mock |
| 7 | Approval gate with auto-rebook threshold | A | Turns "autonomous" from a claim into a demonstrated behaviour |
| 8 | Agent timeline + live notifications | C | The screen judges look at |

Round-trip flights fold into #1 and #3 at near-zero cost — a second row on the
trip, same scheduler, same code path. Not a ninth feature.

**Cut on purpose:** hotel selection map, Gmail inbox ingestion, a separate
hotel scheduler, refund processing, MCP transport, Temporal, multi-passenger,
voice, SMS, calendar sync.

**Added only if ahead at hour 16:** Gmail draft to hotel/airline, LLM-drafted
refund summary.

---

## 4. Layout

```
travel-concierge/
├── CONTEXT.md          agent protocol — read first
├── ARCHITECTURE.md     this file
├── CONTRACT.md         frozen shapes. changing it needs all four
├── TEAM.md             ownership matrix + branches
├── STATUS.md           what is actually done
├── policy.yaml         the credibility artifact — judge-readable
├── docker-compose.yml
├── Makefile
├── db/
│   ├── schema.sql      owner A, nobody else
│   └── seed.sql        owner A, deterministic, three travellers
├── api/
│   ├── main.py         routers only, no logic
│   ├── core/           A — config, db, models, state_machine, events, audit
│   ├── monitor/        B — scheduler (tiered cadence), poller
│   ├── planner/        A — constraints, rank, hotel_impact
│   ├── executor/       A — gate, run
│   ├── providers/      B owns base/mock/aviationstack · D owns duffel
│   ├── llm/            A — client, extract, explain, fallback
│   ├── routes/         A owns trips/approvals · B owns simulate/ws
│   └── tests/
├── web/                C, entirely
└── docs/
    ├── DEMO_SCRIPT.md  D
    └── SUBMISSION.md   D
```

---

## 5. The runtime flow

```
Disruption detected          monitor/poller.py or routes/simulate.py
        │                    writes disruptions row, audit DETECTED
        ▼
Options ranked               planner/constraints.py -> (survivors, rejections)
        │                    planner/rank.py -> scored, using policy.yaml weights
        │                    audit EVALUATED  ("14 evaluated, 3 rejected")
        ▼
Policy gate                  executor/gate.py
        │                    under threshold + no violations -> fire
        │                    otherwise -> approvals, audit AWAITING_APPROVAL
        ▼
Actions executed             executor/run.py
        │                    flight first, THEN hotel (hotel reads new arrival)
        │                    audit REBOOKED, HOTEL_SHIFTED
        ▼
Member notified              llm/explain.py + llm/fallback.py
                             audit NOTIFIED
```

**Invariant:** every stage writes an `agent_actions` row *before* it acts. The
frontend timeline has no knowledge of the workflow — it renders that table. Add
a stage and the timeline shows it for free; break mid-flow and the timeline
shows exactly where it stopped.

---

## 6. Providers — four of seven, and the budget that governs everything

| Provider | Role | Budget |
|---|---|---|
| **AeroDataBox** | flight status, primary | **500/month**, 5/sec, HTTPS |
| **AviationStack** | status cross-check only | **500/month**, HTTP only |
| **Duffel** (test) | flight search + booking | 30/min, ~120 searches |
| **Nuitee / LiteAPI** (sandbox) | hotel lifecycle | generous |
| **Mock** | **demo default** | infinite |

**Cut:** SerpAPI — 100 searches/month and it reads Google's cache, which lags a
cancellation by 10–30 minutes, so it is useless for the one thing we need.
FlightAPI.io — 20 trial credits at 2 credits per call is ten calls total,
unusable. Ignav — returns booking *links* to complete on the airline's site,
not bookings, and `ignav_id` expires in minutes, so it cannot survive a plan
sitting in an approval queue.

### The quota ceiling is the real constraint

500 requests per month, per status provider. Our own tiered schedule at
15-minute polling inside the last 24 hours is **96 calls per flight per day**.
Three seeded travellers is 288/day. Idle running exhausts a month of quota in
under two days — and we will rehearse the demo roughly thirty times.

Therefore:

1. `DEMO_MODE=true` means **no live status call happens at all.** Mock only.
   This is a quota guard, not a convenience.
2. Tests never call a live provider.
3. Development is capped at a fraction of the month (`QUOTA_DEV_BUDGET_FRACTION`)
   so there is headroom for one live run on stage.
4. Every live call goes through `core/quota.spend()`. A provider module calling
   `httpx` directly is a bug.

This is the difference between having a live API to show a judge and having a
429 on stage.

### Status normalisation
Each provider speaks a different vocabulary. AeroDataBox alone has fourteen
values including `CanceledUncertain` and `Diverted`. Everything passes through
`providers/status_map.py` into our five values before anything else sees it,
and an unmapped value **raises** rather than falling through — a silent
fallthrough is how you miss a cancellation.

We do not build automatic AeroDataBox → AviationStack failover. Normalising two
providers into one live path costs hours and protects against an outage that
will not happen in 90 seconds. AviationStack exists so we can say we
cross-verified, and as a manual switch if AeroDataBox is down at hour 20.

AviationStack's free tier is **HTTP only** — the key travels in plaintext.
Backend only, never the browser, never logged in full.

### Duffel webhooks — optional, not the detection path
Duffel fires `order.airline_initiated_change_detected`, but only for orders
booked through Duffel; you cannot subscribe to arbitrary flight numbers. In
test mode those change events are simulated, which means we *could* book a test
order and receive a genuine webhook — a stronger story than our own POST
endpoint.

It is an hour-18 upgrade at best: it needs a public HTTPS tunnel, webhook
registration, deduplication on `id` (delivery is at-least-once), and a 2xx
inside 30 seconds. Detection ships on polling plus the declared simulate
endpoint. If the webhook lands, it is a bonus beat in the demo.

### The latency number, stated correctly
We inject the disruption ourselves, so "detected in 0.3s" would be measuring
our own HTTP round trip. Report it as **processing latency from event receipt**,
and state the production detection bound separately: it is the poll interval,
which is tiered.

```
> 7 days out   ->  every 12 hours
1 to 7 days    ->  every 6 hours
< 24 hours     ->  every 15 minutes
```

In demo mode this is overridden to `DEMO_POLL_SECONDS`. The tiered schedule is
a production argument; the demo runs fast. Knowing the difference is worth more
than the number.

---

## 7. The LLM chain

Three keys, tried in order, with the templated fallback underneath:

```
LLM_CHAIN=gemini,openrouter,xkiro   ->  llm/fallback.py
```

**This is a quota and latency win, not a reliability one.** The LLM is already
off the critical path — a rebooking completes whether or not a model answers.
Do not spend more than an hour here.

What the chain actually buys:

- **Rehearsal headroom.** Thirty rehearsals × several calls each will trip a
  free-tier rate limit. Three keys is three budgets.
- **Latency.** A rate-limited provider that hangs for its full timeout on every
  call is worse than no provider. The circuit breaker skips it for 60 seconds
  after a failure.

Three properties the router must have:

1. **Never raises.** `complete()` returns `str | None`.
2. **Hard budget.** Per-provider timeout (4s) plus a total budget (8s). A live
   call over about six seconds kills a demo.
3. **Circuit breaker.** Without it, a throttled Gemini costs you its full
   timeout on every call for the rest of the hackathon.

An unset key is skipped at registration, so a blank `XKIRO_API_KEY` never costs
a timeout.

### The cache matters more than the chain

`llm/cache.py` keys responses on plan content — chosen option, rejections,
hotel delta. Thirty rehearsals of the same seeded plan become **one** API call.

Beyond quota, this makes the demo deterministic: the same explanation, worded
identically, every run. That is the same reason `providers/mock.py` has no
randomness — you cannot rehearse a pitch against text that changes each time.
The cache persists in Postgres and survives `make reset`.

### On xkiro

Verify at hour 0 whether it speaks the OpenAI chat API (`POST
{base}/chat/completions`, Bearer token). If it does,
`llm/providers/openai_compatible.py` works untouched and you only fill in three
env vars. If it does not, write a sibling adapter — **timeboxed to 20 minutes.**
Two working providers plus the fallback is already more resilience than this
demo needs.

### The test that proves it

`tests/test_fallback.py` runs with every LLM key blank and asserts the system
still produces usable member-facing text. If that passes, no model outage can
break the demo. Write `llm/fallback.py` **before** any adapter.

---

## 8. Constraints — what they are and why they win

A constraint is a rule the **traveller declared**, which the planner uses to
eliminate flights before ranking. Not airline policy — we never claim to know
that. That distinction is what makes it defensible.

Every team on PS-8 will show an agent picking the cheapest or fastest option.
Ranking by price is not interesting. The interesting moment is the agent
looking at a cheaper, faster flight and saying *not for this person*.

**The demo constraint is a hard arrival deadline:**

```yaml
traveller: priya_sharma
hard_arrival_by: "2026-09-21T09:00+01:00"
reason: "client presentation, cannot be missed"
```

The agent finds something ₹8,000 cheaper arriving 11:40. It rejects it:

> **Rejected — arrives 11:40, misses hard deadline 09:00** (₹8,000 cheaper)

Nobody can argue with that. It needs zero domain knowledge to defend, it is
obviously something a real traveller would specify, and it produces the moment:
the agent declining money to protect the human's actual goal.

A second axis — a fare cap breach that **escalates** rather than rejects —
shows two kinds of constraint behaviour in one demo. Richer than either alone.

We considered an accessibility constraint and rejected it: airlines are
required to provide wheelchair assistance on essentially any flight, so a
travel-domain judge would immediately ask why it rules anything out. A rule we
cannot defend in one sentence is a rule that collapses the demo it anchors.

---

## 9. Known gaps — say these before a judge finds them

- **Missed connections.** The brief names cancellations *and* missed
  connections. The schema carries multi-leg itineraries; the planner is
  single-leg in this build. That is the honest answer.
- **Autonomy.** No airline grants rebooking write access to a hackathon team.
  Simulated feed, real logic, sandbox booking — said out loud, early.
- **Generalisation.** The closing line about airlines being the first vertical
  only holds if `planner/rank.py` operates on a generic option with a
  constraints dict. If it is threaded with IATA codes, the honest line is "the
  pattern generalises," not "the code does."
