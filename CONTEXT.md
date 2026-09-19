# CONTEXT.md — how to work in this repo

**This file is for the coding agent. Read it in full at the start of every
session, before writing a single line.**

If you are a human: this is also the file that stops four people from writing
the same function four different ways at 3am. Read it once, then let the agent
enforce it.

---

## 1. What we are building

An autonomous travel-disruption concierge for hackathon PS-8. A flight is
cancelled; the system detects it, searches alternatives, eliminates the ones
that violate the traveller's own constraints, ranks what survives, rebooks
inside policy, shifts the hotel, and explains what it did.

**The boundary we state out loud:** simulated disruption feed, real decision
logic, sandbox booking. We do not claim live airline write access, and the
agent must never generate copy that implies we do.

**The clock:** started 09:00 Saturday, submission 17:00 Sunday. 32 hours
wall-clock, roughly 24–26 usable after submission mechanics and sleep.

---

## 2. The one architectural rule

> **Deterministic code decides. The LLM narrates.**

The model explains a chosen plan and drafts a message. It does not pick the
flight, does not write to the database, and has no path to a provider adapter.

If a task would put the LLM in the decision path, that task is wrong. Say so
and stop. This is not a style preference — it is the thing that prevents the
failure where the model announces a rebooking that never happened.

Second rule, nearly as important: **only `core/audit.py` writes to
`agent_actions`.** Every module calls `audit.record(...)`. The frontend
timeline is a dumb render of that one table, so a stray INSERT somewhere else
makes the timeline render garbage.

---

## 3. Session protocol — follow this every time

### Step 1 — Load the context
Read, in this order: `CONTEXT.md` (this file), `ARCHITECTURE.md`,
`CONTRACT.md`, `TEAM.md`, `STATUS.md`.

### Step 2 — Identify the task
Find the task ID in `STATUS.md` (A1, B3, C4, …). If the user has described work
that has no ID in the ledger, ask which ID it belongs to before starting. Work
that is not in the ledger is work nobody else can see.

### Step 3 — Check ownership
Look up the task's owner in `TEAM.md`. **If the current user is not the owner
of every file the task touches, stop and say so.** Do not edit another person's
files, even to fix an obvious bug — report it instead. Two people editing one
file is how a 32-hour build loses three hours to a merge.

### Step 4 — Verify the dependencies are actually done

This is the step that matters most, and the one an agent will naturally skip.

For every entry in the task's `Depends on` column:

1. Read the state in `STATUS.md`.
2. **Do not trust it.** Run the `Verify with` command from that row, or import
   the module and check that it does not raise `NotImplementedError`.
3. A file existing is not the same as a file working. Every stub in this repo
   raises `NotImplementedError("<task-id>")` on purpose — that exception *is*
   the incompleteness signal.

**If any dependency fails verification, STOP. Do not start the task.**

Report to the user in exactly this shape:

```
BLOCKED — cannot start <TASK ID>.

Missing dependency: <DEP ID> — <what it should do>
Owner: <person>
Status in STATUS.md: <what it claims>
Actual state: <what you found — e.g. "providers/base.py raises
              NotImplementedError('B1')">

<TASK ID> needs <specific thing> from <DEP ID> before it can be written.

Options:
  1. Ask <owner> to finish <DEP ID> — this is the correct move.
  2. Work on <alternative task ID> from this owner's list instead.

I have not written any code. Tell me which you want.
```

**Do not work around a missing dependency.** Specifically, never:

- write a stub, shim, or placeholder implementation of another person's module
- inline a copy of their logic "temporarily"
- change `CONTRACT.md` to avoid needing their output
- mark anything DONE in `STATUS.md` that you did not verify

Every one of those creates work that has to be deleted later, and the deletion
happens at hour 20 when nobody has the time.

### Step 5 — Restate before writing
State in two or three lines: the task ID, which files you will touch, and which
`CONTRACT.md` shapes you will produce or consume. If a shape you need is not in
`CONTRACT.md`, stop — that needs a team decision, not an invention.

### Step 6 — Write it
Smallest thing that satisfies the verify command. No extra features, no
refactors of code you do not own, no dependencies not already in
`requirements.txt`.

### Step 7 — Verify and report
Run the `Verify with` command. Then update **only your own row** in
`STATUS.md`, and only if it passed. Report: task ID, files changed, verify
output, anything you noticed but did not touch.

---

## 4. Things the agent must refuse

- Editing a file owned by someone else (`TEAM.md` has the matrix)
- Changing anything in `CONTRACT.md` without an explicit instruction that the
  team has agreed to it
- Adding a library that is not already in `requirements.txt` or `package.json`
- Putting the LLM anywhere in the decision path
- Writing to `agent_actions` from outside `core/audit.py`
- Adding a feature not on the list of eight in `ARCHITECTURE.md`
- Marking a task DONE without running its verify command
- Introducing randomness into `providers/mock.py` — the demo must be identical
  on every run or the pitch cannot be scripted

### Quota rules — refuse these without exception

AeroDataBox and AviationStack are capped at **500 requests per month each**.
That is the entire budget for the whole project, and thirty rehearsals will
destroy it.

- **Never call a live status API from a test.** Fake the response.
- **Never call a live status API while `DEMO_MODE=true`.** Mock only.
- **Never write a retry loop, a polling loop, or a "just check it once more"
  against a live status endpoint** during development.
- **Never call `httpx` directly from a provider module.** Every live call goes
  through `core.quota.spend()` first.
- If asked to verify a key, make **exactly one** call and say how many of the
  500 remain.
- `providers/status_map.py` must raise on an unmapped value. Do not add a
  default fallthrough — a silently mis-mapped status is a missed cancellation.

AviationStack HTTPS was verified with the configured key. Never call it from
frontend code, and never log a URL containing the key.

### LLM rules

- **Never call a model API outside `llm/`.** One door: `llm.client.ask()`.
  No direct `httpx` to Gemini or OpenRouter from a route, a planner, or a test.
- **Never let an LLM call raise into the caller.** The router returns
  `str | None`. A dead model must never stop a rebooking.
- **Write `llm/fallback.py` before any adapter.** `tests/test_fallback.py` must
  pass with every key blank. If it does not, stop and fix that first.
- **Never skip the cache** for explain/draft. Thirty rehearsals of one plan is
  one call, and it is what makes the demo text identical every run.
- **Never remove the per-provider timeout or the circuit breaker** to "make it
  more reliable". Without the breaker, one throttled provider costs its full
  timeout on every call for the rest of the hackathon.
- Do not add a fourth LLM provider. Three plus the fallback is past the point
  of diminishing returns.

If asked to do any of these, say which rule it breaks and ask for confirmation.

---

## 5. Prompting patterns that work here

**Good — scoped, IDs named, contract referenced:**
> Task A6. Implement `planner/constraints.py`. Read CONTRACT.md for the
> Rejection shape and policy.yaml for the rules. Return
> `(survivors, rejections)`. Every rejection needs a `human_reason` a
> non-engineer can read. Check B1 is done first.

**Bad — unscoped, invites the agent to invent:**
> Build the filtering logic for flights

**Good — explicitly blocked-aware:**
> Task A10, executor/run.py. If B1 or A9 aren't verifiable, tell me and stop.

**Good — end of a work block:**
> Update my rows in STATUS.md for anything whose verify command now passes.
> Do not touch rows owned by anyone else.

---

## 6. Checkpoints — the agent should enforce these

If the current hour is past a checkpoint and its condition is not met, say so
before starting new work.

| Hour | Must be true | If not |
|---|---|---|
| 1 | Hour-0 gate all DONE, CONTRACT frozen | Drop Duffel, mock only |
| 5 | Simulate fires an event visible in the browser | Cut the hotel leg (A8) |
| 9 | Ranked options with rejections returned | Cut LLM extraction |
| 13 | End-to-end manual path works, ugly is fine | Freeze features, polish only |
| 16 | Autonomous path (A9) works | Ship manual only, say so in the pitch |
| 24 | Backup video recorded | Stop coding and record it now |
| 26 | **HARD FREEZE** | — |

The hour-26 freeze is not advisory. Venue wifi will betray someone, and a
recorded demo has saved more teams than any architecture decision.

---

## 7. Build order inside a feature

Always: **manual path first, autonomous layer second.**

The difference between them is one boolean and one comparison in
`executor/gate.py`. Build the whole pipeline with the approval gate always on,
get it working end to end, then flip the threshold. That is a 30-minute
addition at hour 12, not a second system — and if you fall behind, the thing
you are missing is a feature rather than a half-wired mess.

---

## 8. Glossary — use these words, not synonyms

| Term | Means |
|---|---|
| **Disruption** | A detected flight status change. Row in `disruptions`. |
| **Recovery plan** | Ranked options + rejections + hotel impact. Row in `recovery_plans`. |
| **Rejection** | An option eliminated by a hard rule, with a human-readable reason. |
| **Gate** | The auto-rebook vs ask-the-user decision in `executor/gate.py`. |
| **Timeline** | The rendered `agent_actions` table. Never call it a log. |
| **Sidecar** | The LLM. Off the critical path, no route to adapters. |
| **Simulate** | Our declared test harness. Never called "fake" or hidden. |
