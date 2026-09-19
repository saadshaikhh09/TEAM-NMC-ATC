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
| AviationStack: one status call succeeds | B | TODO | 1 of 500 spent. HTTP only. |
| Duffel test: one offers call succeeds | D | TODO | 30/min |
| Nuitee sandbox: search → prebook → book → cancel round trip | D | TODO | free sandbox |
| LLM key returns a completion | A | TODO | |
| Repo pushed, everyone cloned | A | TODO | |
| CONTRACT.md read by all four | all | TODO | |
| Hackathon rubric + submission format confirmed | D | TODO | |
| **Everyone has read core/quota.py** | all | TODO | 500/month is the whole budget |

---

## Build ledger

| ID | Deliverable | Owner | Depends on | State | Verify with |
|---|---|---|---|---|---|
| A1 | `db/schema.sql` applies clean | A | — | TODO | `make reset` |
| A2 | `core/models.py` | A | A1 | TODO | `python -c "import core.models"` |
| A3 | `core/audit.py` record() | A | A2 | TODO | `pytest tests/test_audit.py` |
| A4 | `core/state_machine.py` | A | A2 | TODO | `pytest tests/test_state.py` |
| A5 | `db/seed.sql` — 3 travellers | A | A1 | TODO | `make reset` then GET /trips |
| B1 | `providers/base.py` signatures | B | — | TODO | `python -c "import providers.base"` |
| B2 | `providers/mock.py` all 4 methods | B | B1 | TODO | `pytest tests/test_mock.py` |
| B3 | `routes/simulate.py` | B | A2,A3 | TODO | `curl -XPOST :8000/simulate/cancellation` |
| B4 | `routes/ws.py` broadcast | B | A3 | TODO | browser console shows event |
| B5 | `monitor/scheduler.py` tiered poll | B | A2 | TODO | `pytest tests/test_scheduler.py` |
| B6 | `providers/aerodatabox.py` (primary) | B | B1,A12 | TODO | `pytest tests/test_status_map.py` |
| B7 | `providers/aviationstack.py` (cross-check) | B | B1,A12 | TODO | one live call, once |
| B8 | `providers/status_map.py` | B | — | TODO | `pytest tests/test_status_map.py` |
| C1 | `web/` runs, calls GET /trips | C | — | TODO | `npm run dev` |
| C2 | Trip card | C | C1 | TODO | visual |
| C3 | **Agent timeline** | C | C1 | TODO | visual |
| C4 | Rejection panel | C | C1 | TODO | visual |
| C5 | Approval modal | C | C1 | TODO | visual |
| C6 | WS live updates | C | B4 | TODO | visual |
| D1 | `providers/duffel.py` search + book | D | B1 | TODO | returns confirmation |
| D2 | `HotelProvider.change_dates()` cancel-then-rebook | D | D3 | TODO | `pytest tests/test_hotel_change.py` |
| D3 | `providers/nuitee.py` full lifecycle | D | B1 | TODO | sandbox booking id returns |
| D4 | Notification panel data | D | A3 | TODO | GET timeline |
| D5 | Demo script written | D | — | TODO | read aloud in 90s |
| D6 | Backup video recorded | D | all | TODO | file exists |
| D7 | Submission writeup | D | — | TODO | submitted |
| D8 | *(optional, h18+)* Duffel webhook receiver | D | D1 | TODO | real POST arrives |
| A6 | `planner/constraints.py` filter + rejections | A | B1,A2 | TODO | `pytest tests/test_filter.py` |
| A7 | `planner/rank.py` | A | A6 | TODO | `pytest tests/test_rank.py` |
| A8 | `planner/hotel_impact.py` | A | A2 | TODO | `pytest tests/test_hotel.py` |
| A9 | `executor/gate.py` approval threshold | A | A7 | TODO | `pytest tests/test_gate.py` |
| A10 | `executor/run.py` | A | A9,B1 | TODO | end-to-end passes |
| A11 | `llm/` explain + draft + fallback | A | A7 | TODO | works with LLM off |
| A12 | `core/quota.py` budget guard | A | A2 | TODO | `pytest tests/test_quota.py` |

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
