# Autonomous Travel-Disruption Concierge

PS-8. An agent that detects flight disruptions, evaluates alternatives against
traveller constraints and policy, rebooks, shifts the hotel, and explains
itself.

**Our boundary, stated up front:** simulated disruption feed, real decision
logic, sandbox booking. We do not claim live airline write access. The demo
drives simulated statuses — on-time, delayed, cancelled — so the passenger
experience is reproducible without touching live airline availability.

---

## The problem

Flight delays and cancellations leave passengers stranded, uncertain, and
under pressure to make urgent decisions. Finding an alternative is hardest
exactly when it matters most: limited availability, rebooking cost, and a
destination they still have to reach.

The information is scattered. Passengers check flight status in one place,
search alternatives in another, and compare prices in a third — while dealing
with the stress of a trip that has already gone wrong.

- Uncertainty about delays and cancellations.
- Difficulty finding suitable alternatives at short notice.
- Unexpected rebooking expense against a limited budget.
- Time-consuming searches across multiple services.
- No clear next step.

**What we build against:** a concierge that explains what happened to the
journey and guides the passenger to alternatives that fit their travel details
and their rebooking budget — enough information to make an informed decision,
not a wall of options.

---

## Read these before writing any code

Twenty minutes, in this order. Skipping them is how four people write four
versions of the same function.

1. `CONTEXT.md` — how to work in this repo, and the Codex session protocol
2. `ARCHITECTURE.md` — what the structure is and why
3. `CONTRACT.md` — the frozen data shapes. Do not change without a team call.
4. `TEAM.md` — who owns which files, which branch you are on
5. `STATUS.md` — what is actually done right now

---

## Run it

Five minutes from clone to a moving timeline: database, API, dashboard, then
fire a disruption from the UI.

### Running locally

Once you've done the one-time setup below (database, `api/.venv`, `npm
install` in both `web/` dirs), start the whole stack — API, site, app —
with one command from the repo root:

```bash
./start.sh              # everything
./start.sh --api-only   # just the FastAPI backend
./start.sh --web-only   # just the site + app dev servers
./start.sh --help
```

Or `make dev`, which just calls `./start.sh`.

It reuses the exact commands from `make api` / `make web` / `make site`,
runs preflight checks (venv, `node_modules`, Postgres reachability +
migrations, free ports — with a fix command printed for each failure),
waits for `/health` before declaring readiness, then prints the site,
app, and API-docs URLs plus the seeded demo login. Output from each
service is interleaved and prefixed (`[api]`, `[site]`, `[app]`).
Ctrl-C stops everything and frees the ports — no orphaned uvicorn or
vite processes left behind.

### 1. Clone and branch

```bash
git clone https://github.com/saadshaikhh09/TEAM-NMC-ATC && cd travel-concierge
git checkout feat/<your-branch>     # a-core · b-monitor · c-web · d-providers
cp .env.example .env                # ask Shahid for the keys
```

### 2. Database — pick ONE path

Both give you the same database. Use whichever you can get running in five
minutes; do not download Docker Desktop mid-hackathon if you do not already
have it.

<details open>
<summary><b>Path A — local postgres (no Docker). Recommended if unsure.</b></summary>

macOS:

```bash
brew install postgresql@16
brew services start postgresql@16
echo 'export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

createuser -s concierge 2>/dev/null
createdb -O concierge concierge
psql -d concierge -c "ALTER USER concierge WITH PASSWORD 'concierge';"

psql -U concierge -d concierge -f db/schema.sql
psql -U concierge -d concierge -f db/seed.sql
```

Ubuntu/WSL: `sudo apt install postgresql-16`, then `sudo -u postgres` for the
`createuser`/`createdb` lines, rest identical.

Then apply the migrations, which `db/schema.sql` does not include:

```bash
for f in db/migrations/*.sql; do psql -U concierge -d concierge -f "$f"; done
```

</details>

<details>
<summary><b>Path B — Docker. Only if Docker Desktop is already installed.</b></summary>

```bash
docker compose up -d
```

Schema and seed apply automatically on first boot. Migrations do not — run
`make reset` once afterwards to apply `db/migrations/`.

</details>

Either way, **`make reset` is your reset command.** It detects Docker, falls
back to local postgres, and applies the migrations in both cases.

### 3. Verify

```bash
psql -U concierge -d concierge -c "select name from travellers;"
```

Three rows — Priya Sharma, Rohan Mehta, Ananya Iyer. If you get three names,
your database is correct. If not, stop and fix it before writing code.

### 4. Backend

Use a virtualenv. `make api` and `make test` both call whichever `python` is on
your PATH, so a conda base environment will run them without pytest installed
and fail in a way that looks like a code error.

```bash
cd api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd .. && make api                    # http://localhost:8000/docs
```

Smoke test it in another shell — this hits no provider and costs no quota:

```bash
curl -s localhost:8000/health                        # {"ok":true}
curl -s localhost:8000/trips | python3 -m json.tool  # three travellers
```

### 5. Frontend

`web/` is **not** an npm workspace. It holds two independent surfaces, each
with its own `package.json`, and each runs on its own port. Install them
separately.

Both are long-running, so give each its own shell. From the repo root:

```bash
(cd web/app  && cp .env.example .env && npm install && npm run dev)   # :5174 — the dashboard
(cd web/site && npm install && npm run dev)                           # :5173 — the landing page
```

Once installed, `make web` and `make site` are the shortcuts.

The dashboard is the one judges look at. In dev it proxies `/trips`,
`/approvals`, `/disruptions`, `/simulate`, `/health` and `/ws` to `:8000`, so
it is same-origin and needs no CORS entry. Leave `VITE_API_URL` blank unless
you are serving a built bundle from a different origin than the API.

You do not need the API to open the dashboard. If `:8000` is unreachable it
falls back to contract-shaped mocks and renders the same screen — that is
deliberate, so a dead venue wifi cannot take the demo down. The header tells
you which one you are looking at: **Live**, **Polling**, or **Mock data**.

### 6. Run the demo

With the API and the dashboard both up, at `http://localhost:5174`:

1. **Reset first.** `make reset`. The tests and the demo both assume the
   pristine seed, and a half-disrupted database is the most common reason a
   rehearsal does not reproduce.
2. **Pick a traveller** in the navy operations bar at the top. Each seeded trip
   demonstrates a different gate path — Priya the hard-deadline refusal, Rohan
   the fare-cap escalation, Ananya the clean auto-rebook.
3. **Simulate a cancellation.** That button is `POST /simulate/cancellation`.
   It writes the same `disruptions` row and fires the same `disruption.detected`
   event as a real poll, which is why the pitch line "simulated feed, real
   decision logic" is honest. Say it out loud; do not hide the endpoint.
4. **Watch the timeline.** It is a dumb render of the `agent_actions` table, so
   whatever the agent actually recorded is what you see — including where it
   stopped if it broke. On the live API path you should now get five to seven
   rows, not one:

   ```
   DETECTED           AI131 cancellation detected
   PLANNING           Searching alternatives BOM to LHR
   EVALUATED          Evaluated 4 options, rejected 2 on policy
   AWAITING_APPROVAL  Fare 52,400 exceeds auto-approve threshold 45,000
   ```

5. **Read the rejection panel out loud.** This is the pitch. `opt_4` was
   ₹8,000 cheaper and was refused anyway, because it lands after Priya's 09:00
   London deadline. The agent says so in words a non-engineer can read.
6. **Approve.** The modal fires `POST /approvals/{id}/approve`; the timeline
   gains `APPROVED → REBOOKED → NOTIFIED` and the trip reaches `RECOVERED`.

> **First run is slow.** A cold cancellation takes 8–12s, all of it the two
> `llm/explain.py` narration calls burning their budget against a slow chain. It
> is cached by plan hash afterwards, so every rehearsal of the same plan is
> instant. It is not a hang. Filling in `GROQ_API_KEY` is the fix.

Firing the same kind twice on the same leg never moves the screen. `detect()`
either hands back the disruption it already wrote, or answers `409 flight … is
already CANCELLED` — and neither writes a timeline row or emits an event. The
bar checks the leg's status first and tells you, rather than reporting a
success that changed nothing. `make reset` is how you rehearse again.

Each seeded traveller exercises a different branch of the policy gate, and all
three now run end to end on the live API:

| Traveller | What the gate does | Where it ends |
|---|---|---|
| **Priya** BOM→LHR | halts for approval — 52,400 over her 45,000 threshold | `AWAITING_APPROVAL` → approve → `RECOVERED` |
| **Ananya** BLR→DXB | **auto-rebooks with no click** — 30,000 is under her threshold | `RECOVERED` |
| **Rohan** DEL→SIN | escalates — 62,000 over his 30,000 threshold | `AWAITING_APPROVAL` |

> **Fixed 2026-09-20 (was a known gap).** `GET /disruptions/{id}/plan` is now
> registered, and `planner/orchestrate.py` runs the planner off
> `disruption.detected`, so the live API path renders the full recovery — plan
> banner, alternatives, rejection panel, approval modal, confirmation card. The
> header should read **Live**. You no longer have to kill the API to demo the
> recovery story; if you find yourself on **Mock data**, the API is down, and
> that is now a bug rather than the plan.

---

## Commands

| Command | Does |
|---|---|
| `make reset` | Drop, reapply schema + seed **+ `db/migrations/`**. Detects Docker, else local postgres. |
| `make reset-local` | Local postgres only, and **skips migrations** — you will not get `quota` or `llm_cache`. Prefer `make reset`. |
| `make api` | uvicorn on :8000 |
| `make web` | Dashboard dev server on :5174 |
| `make site` | Landing page dev server on :5173 |
| `make test` | pytest — activate `api/.venv` first |

You will run the reset command roughly thirty times during rehearsal. It must
produce an identical database every time — which is also why
`providers/mock.py` has no randomness.

`make test` runs against the live database, so **reset before you run it.**
Against a drifted database `tests/test_trips.py` fails on a `next_poll_at` that
detection has already nulled and a timeline that is no longer empty. Those two
failures mean the database moved, not that the code broke.

---

## Two rules that will cost you the demo if broken

**API quota.** AeroDataBox and AviationStack are **500 requests per month
each** — that is the entire project budget. Our own 15-minute polling tier is
96 calls per flight per day, and we will rehearse about thirty times.

- `DEMO_MODE=true` means no live status call happens at all. Leave it true.
- Every live call goes through `core.quota.spend()`. Never `httpx` direct.
- Tests never call a live provider.
- Verifying a key is **one** call. No loops, no "let me just check again."

**One door to the model.** Nothing outside `llm/` calls an LLM API. Use
`llm.client.ask()`. It returns `str | None` and never raises — a dead model
must not stop a rebooking. Write `llm/fallback.py` before any adapter;
`tests/test_fallback.py` must pass with every key blank.

Full rules in `CONTEXT.md` §4.

---

## The LLM chain

```
LLM_CHAIN=groq,xkiro,openrouter
```

Tried left to right, first success wins. **A name with no registered adapter is
skipped, not an error** (`router.py:120`), so the chain is safe to list ahead of
the keys. If every provider fails, `llm/fallback.py` produces the same copy from
a template and the demo continues — the model is a sidecar, never the decision.

| Provider | Role | State |
|---|---|---|
| `groq` | primary | OpenAI-compatible, reuses `llm/providers/openai_compatible.py`. Needs a key **and** a model. |
| `xkiro` | working fallback | verified at 2.58s |
| `openrouter` | last resort | correct but ~31.7s against a 4s timeout, so in practice always times out |
| ~~`gemini`~~ | **dropped** | the key was an `AQ.` OAuth token, not an `AIza…` Generative Language key — 404 on every call, from the front of the chain |

### Adding your Groq key

1. Get a key at [console.groq.com/keys](https://console.groq.com/keys) — it
   starts with `gsk_`. Paste it on the `GROQ_API_KEY=` line in `.env`.
2. **Pick the model from the API, not from memory.** Groq retires model ids, and
   a stale one 404s on every call:

   ```bash
   set -a && source .env && set +a
   curl -s https://api.groq.com/openai/v1/models \
     -H "Authorization: Bearer $GROQ_API_KEY" | python3 -m json.tool
   ```

   Put a fast production chat model from that list on `GROQ_MODEL=`.
3. Restart the API and confirm it registered:

   ```bash
   cd api && ./.venv/bin/python -c "from llm import router; router.configure(); print(sorted(router._registry))"
   ```

   `groq` must appear. **Both the key and the model must be set** — the router
   registers nothing if either is blank, and the chain silently falls through to
   xkiro.

This is worth doing before rehearsing: the two narration calls per plan are the
entire reason a cold cancellation currently takes 8–12 seconds.

---

## Branches

```
main                 always boots, always seeds
├── feat/a-core      Shahid — core/, db/, planner/, executor/, llm/
├── feat/b-monitor   monitor/, providers/base|mock|status_map|aerodatabox|aviationstack
├── feat/c-web       web/
└── feat/d-providers providers/duffel|nuitee, docs/
```

One file, one owner — see the matrix in `TEAM.md` §4. If you need a change in
someone else's file, message them. Do not edit it, even to fix an obvious bug.

Merge to `main` when your slice passes its verify command. Rebase first, and
run the reset + `make test` before you merge — that is the only gate.

```bash
git pull --rebase origin main
make reset && make test
git add -A && git commit -m "A6: constraints filter with rejections"
git push origin feat/a-core
```

Commit messages carry the task ID so `git log` reads against `STATUS.md` at
hour 22 when something broke and nobody remembers when.

---

## Starting a Codex session

Open every session with this. The protocol in `CONTEXT.md` only fires if the
agent has read it.

```
Read CONTEXT.md, ARCHITECTURE.md, CONTRACT.md, TEAM.md, STATUS.md in full.
I am Person <X> on branch feat/<branch>.
Task <ID>: <what>.
Verify dependencies first. If anything is incomplete, tell me and stop.
```

The agent will check `STATUS.md`, refuse to trust it, run the verify command,
and emit a BLOCKED report rather than stubbing another person's module.

---

## Checkpoints

| Hour | Must be true | If not |
|---|---|---|
| 1 | Keys verified, CONTRACT frozen | Drop Duffel, mock only |
| 5 | Simulate fires an event visible in the browser | Cut the hotel leg |
| 9 | Ranked options with rejections returned | Cut LLM extraction |
| 13 | End-to-end manual path works, ugly is fine | Freeze features, polish only |
| 16 | Autonomous path works | Ship manual only, say so in the pitch |
| 24 | Backup video recorded | Stop coding and record it now |
| 26 | **HARD FREEZE** | — |