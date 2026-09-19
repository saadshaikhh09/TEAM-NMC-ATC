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

## Setup

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

Your reset command is **`make reset-local`**.

</details>

<details>
<summary><b>Path B — Docker. Only if Docker Desktop is already installed.</b></summary>

```bash
docker compose up -d
```

Schema and seed apply automatically on first boot.
Your reset command is **`make reset`**.

</details>

### 3. Verify

```bash
psql -U concierge -d concierge -c "select name from travellers;"
```

Three rows — Priya Sharma, Rohan Mehta, Ananya Iyer. If you get three names,
your database is correct. If not, stop and fix it before writing code.

### 4. Backend

```bash
cd api && pip install -r requirements.txt
python -c "import sys; sys.path.insert(0,'.'); \
  import core.quota, providers.status_map, providers.base, \
  llm.router, llm.cache, llm.providers.gemini; \
  from llm import fallback; print('OK')"
```

> Only those modules import cleanly. `nuitee`, `aerodatabox`, `duffel`,
> `client`, `models`, `mock` and everything in `routes/` raise
> `NotImplementedError` **at import, on purpose**. That exception is the
> incompleteness signal the coding agent checks for. Seeing it means the
> scaffold is intact, not broken.

```bash
make api          # http://localhost:8000/docs
```

### 5. Frontend (Person C)

```bash
cd web && npm install && npm run dev
```

---

## Commands

| Command | Does |
|---|---|
| `make reset-local` | Drop, reapply schema + seed. **Local postgres.** |
| `make reset` | Same, via Docker. |
| `make api` | uvicorn on :8000 |
| `make web` | Frontend dev server |
| `make test` | pytest |

You will run the reset command roughly thirty times during rehearsal. It must
produce an identical database every time — which is also why
`providers/mock.py` has no randomness.

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
make reset-local && make test
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