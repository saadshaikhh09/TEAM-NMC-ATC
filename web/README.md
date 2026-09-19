# Web — Owner: Saad

The app renders exclusively from `app/src/mocks/` during development. All
backend access goes through `app/src/services/`, whose default implementation
returns those mocks. Swapping to the real API is one import change in that
module; components never fetch directly.

## Backend endpoints (not wired yet)

- `GET /trips`
- `GET /trips/{id}`
- `GET /trips/{id}/timeline`
- `GET /disruptions/{id}/plan`
- `POST /approvals/{id}/approve`
- `POST /approvals/{id}/reject`
- `WS /ws`

**Build order is not negotiable:**

1. Render the trip card from mocks
2. **Agent timeline** — this is hour 3, not hour 20. It is a dumb render of
   `GET /trips/{id}/timeline`. Highest-value pixels on the screen.
3. Rejection panel — the list from `plan.rejections`, each with `human_reason`
4. Approval modal
5. WebSocket live updates last

Build against `app/src/mocks/` using the exact shapes in CONTRACT.md. You should
never be blocked on anyone.

Pace the timeline render so each stage lands visibly over ~6 seconds. An
autonomous rebook that completes instantly looks like nothing happened — that
is a deliberate UI choice and you should be ready to say so.
