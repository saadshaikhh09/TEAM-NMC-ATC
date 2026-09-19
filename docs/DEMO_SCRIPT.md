# Demo script — Owner: Person D. Written by hour 14, not hour 26.

Target: 90 seconds. Rehearse ten times against `make reset`.

**Opening line, said before anything else:**
> "Simulated disruption feed, real decision logic, sandbox booking."

| Beat | Seconds | What is on screen |
|---|---|---|
| 1. Trip card, all green | 0–10 | Priya, BOM to LHR, hotel attached, monitoring |
| 2. Fire the cancellation | 10–15 | Timeline begins moving |
| 3. Evaluated 14, rejected 3 | 15–35 | Rejection panel, rules visible |
| 4. **The refusal** | 35–50 | Cheaper, faster flight rejected: misses the 09:00 deadline |
| 5. Auto-rebooked, hotel shifted | 50–70 | No click. Confirmation numbers land. |
| 6. Second run — Rohan | 70–85 | Fare over threshold, agent stops and asks |
| 7. Closing line | 85–90 | See below |

**Closing line:**
> "We didn't build a travel app. We built a constraint-solving disruption
> engine — airlines are just the first vertical."

Only say that if `planner/rank.py` actually operates on a generic option with a
constraints dict. If it is threaded with IATA codes, say "the pattern
generalises" instead.

## Answers to prepare

- *"Is this really autonomous?"* — Auto-rebook fires with no human input under
  the policy threshold. Above it we escalate on purpose. Both paths are in the
  demo.
- *"What is your detection latency?"* — Processing latency from event receipt
  is X ms. Detection latency in production is bounded by the poll interval,
  which is tiered: 12h, 6h, 15min as departure approaches.
- *"Do you handle missed connections?"* — The schema carries multi-leg
  itineraries. The planner is single-leg in this build.
- *"Why not MCP?"* — The provider layer is a tool interface; wrapping it in MCP
  is mechanical. We spent the hours on the decision engine instead.
