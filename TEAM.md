# TEAM.md — ownership, branches, and the rules that keep four people out of
# each other's way

---

## 1. The four seats

| | Person | Owns | Why this seat |
|---|---|---|---|
| **A** | **Shahid** | Domain spine → recovery engine → integrator | Strongest. Spine first because everyone is blocked on it; engine second because it is the product; integrator last because at hour 16 you are the one who can debug across three people's code. |
| **B** | | Monitor, provider interface, mock, Aviationstack, WebSocket | Owns detection end to end. `providers/base.py` is the first thing anyone pushes. |
| **C** | | Frontend, full-time from hour 1 | Never blocked. Builds against mocks from CONTRACT.md. |
| **D** | | Duffel adapter, notifications, **demo + video + submission** | The submission seat is a real job, not a leftover. |

**A does not take demo or submission.** The failure mode where the strongest
person is also doing the writeup at hour 30 is how teams miss deadlines with
working code. D owns that from hour 14.

**Pick the presenter now.** It should not be whoever is deepest in code at hour
24. They rehearse while others finish.

---

## 2. Branches

```
main                    protected by convention: always boots, always seeds
├── feat/a-core         Shahid — core/, db/, planner/, executor/, llm/
├── feat/b-monitor      B — monitor/, providers/base|mock|aviationstack, routes/simulate|ws
├── feat/c-web          C — web/
└── feat/d-providers    D — providers/duffel, notifications, docs/
```

Create them all at hour 0, right after the scaffold push:

```bash
for b in a-core b-monitor c-web d-providers; do
  git branch feat/$b main && git push -u origin feat/$b
done
```

### Merge rules

- Merge to `main` when your slice passes its own verify command. Not at hour 30.
- **Anybody may push to `main`.** Code review is a luxury you do not have.
- **Nobody merges something that breaks `make reset` or `make api`.** Run both
  before you merge. That is the only gate.
- Rebase on `main` before every merge: `git pull --rebase origin main`
- Merge at least every three hours even if the slice is incomplete but working.
  Long-lived branches are how you discover at hour 20 that two people built
  incompatible halves.

### Commit messages

`<task-id>: <what>` — e.g. `A6: constraints filter with rejection reasons`

The task ID makes `git log` readable against `STATUS.md`, which is what you
will be reading at hour 22 when something broke and nobody remembers when.

---

## 3. Feature ownership

**No feature is owned end to end by one person.** Every feature has a backend
slice and almost every one has a UI slice, which is always C. A feature has a
**primary** who is accountable for it working, plus contributors.

| # | Feature | Primary | Contributors | Task IDs |
|---|---|---|---|---|
| 1 | Manual trip entry + paste-booking extraction | **A** | C (form, paste box) | A11, C2 |
| 2 | Traveller constraints | **A** | C (display) | A1, A2, A5, C2 |
| 3 | Tiered polling scheduler + quota guard | **B** | A (quota.py) | B5, A12 |
| 4 | Detection + simulate endpoint | **B** | C (renders event) | B3, B4, B6, B7, B8, C6 |
| 5 | Filter with rejections, then rank | **A** | C (rejection panel) | A6, A7, C4 |
| 6 | Hotel impact + sandbox rebooking | **A** | **D** (Nuitee), C (display) | A8, D2, D3 |
| 7 | Approval gate — the autonomous switch | **A** | C (approval modal) | A9, A10, C5 |
| 8 | Agent timeline + notifications | **C** | A (audit rows), D (copy) | C3, A3, D4 |

A is primary on five of eight. That is correct — those are the decision logic,
which is the product.

### The two handoffs that will bite you

**Feature 6 spans A and D.** A decides a hotel change is needed and what the new
dates are; D performs it against Nuitee. Agree the boundary at hour 4 in one
line: A produces the `hotel_change` dict exactly as `CONTRACT.md` defines it,
D's `change_dates()` consumes exactly that and returns a `HotelConfirmation`.
Neither reaches past it.

**Feature 8 spans A, C and D.** A writes the rows, C renders them, D writes the
human copy in `headline`. Protection is the standing rule: only
`core/audit.py` writes to `agent_actions`. If D wants a different headline, D
asks A to change the string — D does not write a row.

### Load warning

A is primary on five features *and* is the integrator from hour 16. **A's hours
16–20 must stay free.** If A is still writing the LLM sidecar at hour 19,
nobody is debugging the integration.

If you are behind at hour 14, the thing to hand off is **A11**, the LLM
sidecar — the fallback strings already make the system work without it, so D
can take the explain/draft prompts while A integrates. Decide that at hour 14,
not hour 19.

---

## 4. File ownership matrix

**One file, one owner.** If you need a change in someone else's file, message
them. Do not edit it, even to fix an obvious bug.

| Path | Owner | Notes |
|---|---|---|
| `CONTRACT.md` | **all four** | Frozen at hour 1. Changing it needs everyone's yes. |
| `STATUS.md` | each person, own rows only | Never edit another person's row. |
| `ARCHITECTURE.md` `CONTEXT.md` | A | |
| `policy.yaml` | A | |
| `db/schema.sql` `db/seed.sql` | A | |
| `api/main.py` | A | Routers only. No logic here, ever. |
| `api/core/**` | A | `audit.py` is the only writer to `agent_actions`. |
| `api/planner/**` | A | |
| `api/executor/**` | A | |
| `api/llm/**` | A | |
| `api/routes/trips.py` `approvals.py` | A | |
| `api/core/quota.py` | A | Every live call goes through this. |
| `api/monitor/**` | B | |
| `api/providers/base.py` | B | **Push in hour 1 — A is blocked without it.** |
| `api/providers/mock.py` | B | Deterministic. No `random()`. |
| `api/providers/status_map.py` | B | Unmapped values raise. No fallthrough. |
| `api/providers/aerodatabox.py` | B | Primary status. 500/month. |
| `api/providers/aviationstack.py` | B | Cross-check only. 500/month. HTTP only. |
| `api/routes/simulate.py` `ws.py` | B | |
| `web/**` | C | Entirely. Nobody else opens this directory. |
| `api/providers/duffel.py` | D | |
| `api/providers/nuitee.py` | D | Real sandbox hotel lifecycle. |
| `docs/**` | D | |
| `requirements.txt` | A | Ask before adding a library. |
| `web/package.json` | C | |

### The three coupling points

These are where four-person teams break. Everything else moves independently.

| Interface | Written by | Needed by | Deadline |
|---|---|---|---|
| `CONTRACT.md` | all four, together | everyone | hour 1 |
| `providers/base.py` | B | A | hour 1 |
| `core/models.py` + `audit.record()` | A | B, D | hour 2 |

If those three land on time, you get roughly eight hours where nobody is
blocked on anybody. That is the entire point of the split.

---

## 5. Hour 0 — do this before any product code

All four in parallel, then regroup:

| Person | Task |
|---|---|
| A | Run `scaffold.sh`, push to `main`, create the four branches, verify LLM key, **write `core/quota.py` (A12) before anyone writes a provider** |
| B | **One** AeroDataBox call, **one** AviationStack call. Record the status strings you get back into `status_map.py`. Then stop — you have spent 2 of 1000. |
| C | `npm create` in `web/`, hello world running |
| D | Duffel test → one offers call. Nuitee sandbox → full search/prebook/book/cancel round trip. **Confirm rubric, submission format, deadline, and whether PS-8 is a sponsor track.** |

Then sit down for 25 minutes and read `CONTRACT.md` together. Say out loud that
it is frozen. That meeting buys you eight hours.

If a key does not issue in 20 minutes, the plan changes — and you need to know
at hour 0, not hour 9.

---

## 6. Standing rules

**Sync every three hours. Fifteen minutes, standing up.** Three questions each:
what is working, what is blocking you, what are you cutting. The third question
is the one teams skip and the one that saves them.

**Sleep in shifts.** Four people awake for 32 hours produce nonsense from hour
16 onward, and hour 16 is when integration happens. Two down from hour 18 to
23, two down from 23 to 04. Nobody negotiates this at hour 17.

**`make reset` is sacred.** Seed data lives in the repo. Anyone can restore a
clean demo state in one command. You will run it thirty times during rehearsal
and it must produce an identical result every time — which is why
`providers/mock.py` has no randomness.

**The whiteboard has eight features on it.** When someone proposes a ninth at
hour 14, the answer is no, and the whiteboard is why.

**Default the demo to Mock.** Duffel and Nuitee live are a second run if the
network holds.

**Nobody calls a live status API casually.** AeroDataBox and AviationStack are
500 requests per month *each* — that is the entire project budget, and a
15-minute poll on three travellers burns 288 a day. `DEMO_MODE=true` blocks
every live status call, and it stays true unless A says otherwise. A reads
`quota.report()` aloud at every three-hour sync. Anyone who writes a polling
loop against a live endpoint during development has spent the pitch.

**Build the templated LLM fallback before the LLM client.** Twenty minutes, and
it is the difference between a graceful demo and a dead one.

---

## 7. Schedule

| Hours | A (Shahid) | B | C | D |
|---|---|---|---|---|
| 0–1 | scaffold, branches, CONTRACT | key check, `base.py` | web init | key check, **rubric + deadline** |
| 1–4 | schema, models, audit, state machine | mock provider | trip card | Duffel search |
| 4–8 | constraints filter + rejections | simulate, WebSocket | **timeline** | Duffel book, seed help |
| 8–12 | rank, hotel impact | tiered scheduler | rejection panel | notification panel |
| 12–16 | **gate (autonomous)**, executor | Aviationstack | approval modal, WS live | **demo script** |
| 16–20 | LLM sidecar + fallback | integration support | polish | rehearsal setup |
| 20–24 | **integration, debugging** | integration | integration | **record backup video** |
| 24–26 | freeze, rehearse ×10 | rehearse | rehearse | **submit** |

Sleep shifts overlay this. Move things around freely — but the hour-24 video
and the hour-26 freeze do not move.

---

## 8. What to do when you are blocked

1. Check `STATUS.md` for the dependency's state.
2. **Verify it yourself.** A stub raising `NotImplementedError` is the signal.
3. Message the owner with the task ID.
4. **Switch to another task on your own list.** Do not stub their module, do
   not inline a copy of their logic, do not change `CONTRACT.md` to route
   around them. All three create work that gets deleted at hour 20.
5. If you are blocked for more than 30 minutes, escalate to A. Reassigning a
   task is cheap; four people idling is not.
