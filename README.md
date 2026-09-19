# Autonomous Travel-Disruption Concierge

PS-8. An agent that detects flight disruptions, evaluates alternatives against
traveller constraints and policy, rebooks, shifts the hotel, and explains itself.

**Our boundary, stated up front:** simulated disruption feed, real decision
logic, sandbox booking. We do not claim live airline write access.

## Read these before writing any code

1. `CONTEXT.md` — how to work in this repo, and the Codex session protocol
2. `ARCHITECTURE.md` — what the structure is and why
3. `CONTRACT.md` — the frozen data shapes. Do not change without a team call.
4. `TEAM.md` — who owns which files and branches
5. `STATUS.md` — what is actually done right now

## Quick start

```bash
cp .env.example .env     # fill in keys
make db                  # postgres with schema + seed
cd api && pip install -r requirements.txt
make api                 # http://localhost:8000/docs
cd web && npm install && npm run dev
```

## Demo reset

```bash
make reset
```
