# Web — Owner: Person C

Person C initialises this directory with whichever they already know:

    npm create vite@latest . -- --template react-ts     # faster to start
    npx create-next-app@latest .                        # if you prefer Next

**Build order is not negotiable:**

1. Fetch `GET /trips`, render the trip card
2. **Agent timeline** — this is hour 3, not hour 20. It is a dumb render of
   `GET /trips/{id}/timeline`. Highest-value pixels on the screen.
3. Rejection panel — the list from `plan.rejections`, each with `human_reason`
4. Approval modal
5. WebSocket live updates last

Until the backend exists, build against `src/mocks/` using the exact shapes in
CONTRACT.md. You should never be blocked on anyone.

Pace the timeline render so each stage lands visibly over ~6 seconds. An
autonomous rebook that completes instantly looks like nothing happened — that
is a deliberate UI choice and you should be ready to say so.
