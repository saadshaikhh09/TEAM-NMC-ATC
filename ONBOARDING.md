# ONBOARDING — B, C and D start here

The spine is on `main` and verified. You are unblocked. This takes about ten
minutes, then you open Codex.

**Do not skip the reading.** Four people with four agents and no shared rules
produces four incompatible halves by hour 16.

---

## 1. Clone and branch

```bash
git clone https://github.com/saadshaikhh09/TEAM-NMC-ATC
cd travel-concierge

# pick YOURS
git checkout feat/b-monitor      # B
git checkout feat/c-web          # C
git checkout feat/d-providers    # D

git fetch origin
git rebase origin/main
git push --force-with-lease origin feat/<your-branch>
```

`--force-with-lease`, never plain `--force` — it refuses if someone else
pushed to your branch meanwhile.

Do this rebase at the start of **every** work block, not just today.

---

## 2. Environment

```bash
cp .env.example .env
```

Shahid sends the keys separately — never paste them in the group chat and
never commit `.env`. Confirm with `git status` that `.env` does not appear.

```bash
cd api
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

Use `python -m pip`, not bare `pip`. And use the venv — if you are on Anaconda
or miniconda, its base environment will fight you and you will lose an hour.

You must `source .venv/bin/activate` in every new terminal.

---

## 3. Database

You do **not** need Docker. If you do not already have Docker Desktop
installed, do not download it now.

macOS:

```bash
brew install postgresql@16
brew services start postgresql@16
echo 'export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

createuser -s concierge 2>/dev/null
createdb -O concierge concierge
psql -d concierge -c "ALTER USER concierge WITH PASSWORD 'concierge';"
```

Ubuntu / WSL: `sudo apt install postgresql-16`, then prefix the `createuser`
and `createdb` lines with `sudo -u postgres`.

Then, from the repo root:

```bash
make reset
```

`make reset` auto-detects Docker vs local postgres and applies schema, seed and
migrations. It ends by printing the traveller count.

---

## 4. Prove it works — all three of you

```bash
psql -U concierge -d concierge -c "select name from travellers;"
```

Three rows: Priya Sharma, Rohan Mehta, Ananya Iyer.

```bash
cd api && source .venv/bin/activate
python -m pytest tests -q
python -m core.quota
uvicorn main:app --port 8000
```

In another terminal:

```bash
curl -s localhost:8000/trips | python -m json.tool | head -40
```

You should see Priya with two flight legs, a hotel, and constraints including
`hard_arrival_by`. **If you get this far, your setup is correct.**

> Some modules raise `NotImplementedError` at import on purpose —
> `nuitee`, `aerodatabox`, `duffel`, `mock`, `llm/client`, most of `routes/`.
> That exception is the incompleteness signal the agent checks for. It means
> the scaffold is intact, not broken.

---

## 5. Read these — 20 minutes, not optional

1. `CONTEXT.md` — the Codex session protocol. This is the one that matters.
2. `ARCHITECTURE.md` — what we are building and the decisions behind it
3. `CONTRACT.md` — frozen data shapes. Changing it needs all four of us.
4. `TEAM.md` — your files, your branch, what you must not touch
5. `STATUS.md` — the task ledger

---

## 6. Four rules that will cost us the demo if broken

**API quota.** AeroDataBox and AviationStack are 500 requests **per month**
each. That is the entire project budget. `remaining()` shows **200** — that is
correct, development is capped at 40% so 300 stay reserved for the live run.
One verification call each. No loops, no retries, no "let me just check again."

**One writer to `agent_actions`.** Call `core.audit.record()`. Never INSERT
into that table yourself. The timeline is a dumb render of it, and a stray
write makes the whole screen garbage.

**One thing changes trip status.** `core.state_machine.advance()`. Never
`UPDATE trips SET status`.

**One door to the model.** Nothing outside `llm/` calls an LLM API.

---

## 7. Timestamps

The API serves **UTC** for all machine-readable timestamps, plus `*_local`
display strings (`arrival_local`, `departure_local`,
`hard_arrival_by_local`).

**Render the `_local` fields in UI, never the raw UTC.** Priya's deadline must
read 09:00 London. If it shows 13:30 the demo line stops making sense.

`core/timezones.py` has the IATA → timezone map. Use it rather than writing
your own.

---

## 8. Opening a Codex session

Every session starts with this. The protocol only fires if the agent reads it.

```
Read CONTEXT.md, ARCHITECTURE.md, CONTRACT.md, TEAM.md and STATUS.md in full.
I am Person <X> on branch feat/<branch>.
Task <ID>: <what>.
Verify dependencies first. If anything is incomplete, tell me and stop.
```

Shahid sends your full task prompt separately. Paste it whole — the ownership
rules in it are what stop four agents editing the same file.

### Asking the agent about the repo — `/graphify`

`graphify` indexes this whole repo into a knowledge graph so an agent can answer
"what calls this", "where does the plan state live", "trace the disruption path"
without you first explaining the project. One-time install:

```bash
uv tool install graphifyy    # or: pipx install graphifyy
graphify install             # registers the /graphify skill with your assistant
graphify update .            # build the graph — no LLM key needed
```

That writes `graphify-out/` (gitignored, so build your own — do not commit it):
`graph.json` for the agent, `GRAPH_REPORT.md` to read yourself, and `graph.html`
to open in a browser. Then in a session:

```
/graphify query "how does a cancellation become a recovery plan?"
/graphify explain "RecoveryPlan"
/graphify path "simulate" "AgentTimeline"
```

Re-run `graphify update .` after a big merge — it re-extracts only changed files.

---

## 9. Committing and merging

```bash
# during work
git add <files>
git commit -m "B3: simulate endpoint writes disruption and fires event"

# before you merge — the only gate
git pull --rebase origin main
make reset && cd api && python -m pytest tests -q && cd ..

git push origin feat/<your-branch>
git checkout main && git merge feat/<your-branch> && git push origin main
git checkout feat/<your-branch>
```

Commit messages carry the task ID so `git log` reads against `STATUS.md` at
hour 22 when something broke and nobody remembers when.

Merge every three hours even if your slice is incomplete but working. Long
branches are how we find out at hour 20 that two people built incompatible
halves.

**Nobody merges something that breaks `make reset` or `make test`.** That is
the only rule on main.

---

## 10. Update STATUS.md honestly

Your own rows only. Mark DONE **only after the verify command actually
passes** — not when you think you are finished.

This has already gone wrong twice today: a row said DONE while its check
failed, and a row said TODO while the code existed. Both cost an hour. A
ledger that lies is worse than no ledger.

---

## 11. Sync

Every three hours, fifteen minutes, standing. Three questions each:

- what is working
- what is blocking you
- **what are you cutting**

The third is the one teams skip and the one that saves them.
