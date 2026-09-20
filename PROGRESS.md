# PROGRESS — delta ledger against the "finish the MVP" master prompt

Written 2026-09-20, continuing from `647b84d` ("feat(monitor): work in progress
before vishnu handoffs"). This session found the prior two commits
(`5eb0322` "Frontend v3 with backend update phase-1" and `647b84d`) had
already implemented the large majority of the acceptance checklist below.
This ledger records what was **verified by running the actual system**
(API smoke tests, `make test`, real browser QA at 320–1440px, keyboard nav,
reduced-motion emulation), not what the code merely claims to do. Two real
defects were found and fixed this session (see bottom).

Legend: DONE = verified working · PARTIAL = works but has a named gap ·
NOT STARTED = no implementation found.

---

## P0 — Backend correctness and security

| Item | State | Evidence / file(s) |
|---|---|---|
| Register/login/logout/session endpoints | DONE | `api/routes/auth.py`. Verified live: register → 201 + HttpOnly cookie, login rotates (deletes all prior sessions), logout invalidates token, `/auth/session` 401s after. |
| Adaptive password hashing | DONE | `api/core/auth.py:hash_password` — scrypt (n=2¹⁴, r=8, p=1), 16-byte salt, `hmac.compare_digest` verify. Never plaintext/raw-SHA/browser-side. |
| Opaque high-entropy session tokens, hash-only storage | DONE | `secrets.token_urlsafe(32)`; only `sha256(token)` stored in `sessions.token_hash` (UNIQUE). |
| Expiring sessions, HttpOnly+SameSite=Lax, Secure in prod, rotation, full logout invalidation | DONE | `SESSION_AGE=7d`; `secure=settings().environment=="production"`; login deletes all of the user's prior sessions before issuing a new one; logout deletes the presented token. Verified via curl + browser. |
| No tokens in localStorage | DONE | Cookie-only; `web/app/src/services/api.ts` uses `credentials: 'include'`, no token in JS-reachable storage. |
| Auth errors don't reveal account existence | DONE | `routes/auth.py` — login always returns the same `INVALID_LOGIN` message for unknown email or wrong password. (Register's 409-on-duplicate-email is standard signup UX, not a login oracle.) |
| Email normalized + unique | DONE | `normalize_email` casefolds + validates; `users.email UNIQUE` + `IntegrityError` → 409. |
| Ownership model on trips/timeline/disruptions/plans/approvals/profiles/WS | DONE | `core/ownership.py` (`trips_for`, `flights_for`, `plans_for`) joins through `Traveller.user_id`; every route in `routes/trips.py`/`routes/approvals.py` uses it. Verified live: user B gets 404 on user A's trip UUID, empty list on `/trips`, 404 on approving A's plan. |
| WebSocket scoped to authenticated account | DONE | `routes/ws.py` — origin check, cookie-session auth to open the socket, `_broadcast` looks up the trip's owner and only enqueues to that owner's connected clients. |
| Seeded travellers belong to a documented demo account | PARTIAL | `db/seed.sql` seeds travellers directly (no `users` row / no login credential) — seed data is visible via `make reset-local` but isn't reachable through the authenticated API surface (no user owns it). Real accounts created via `/auth/register` work end-to-end. Not fixed this session — no demo credential was specified anywhere to seed against; flagged as a genuine remaining gap, see bottom. |
| Migrations only, `db/schema.sql` in sync with models | DONE | `db/migrations/001..003` layered on `schema.sql`; `003_auth_ownership_and_trip_input.sql` adds users/sessions/ownership columns idempotently (`IF NOT EXISTS` guards, verified via `make test` reset). |
| `POST /trips` implemented | DONE | `routes/trips.py:create_trip` → `core/trip_service.persist_trip`, one transaction. |
| `/trips/extract` persists through the same shared trip-creation service | DONE | `extract_trip()` calls `llm.extract.extract()` for parsing then calls `create_trip()` directly (same function, same transaction path) — not a separate/disposable code path. Verified: with no LLM key configured it correctly 503s ("unavailable; enter manually") rather than faking a result — no fake success state. |
| Full trip validation (IATA, timestamps, ordering, hotel dates, numeric limits) | DONE | `core/trip_service.py` — `FlightInput`/`HotelInput`/`ConstraintInput`/`TripInput` validators. Verified live: malformed IATA, missing fields, and arrival-before-departure all produce actionable 422s. |
| Full rollback on dependent insert failure | DONE | `SessionLocal.begin()` context manager in `create_trip`/`persist_trip`; one transaction for traveller+constraints+trip+flights+hotel. |
| New trips appear immediately, survive restart, enter monitoring | DONE | Verified live: created a trip, killed and restarted `uvicorn`, GET still returned it with `status: MONITORING`. |
| Unknown-airport timezone KeyError removed | DONE | `core/timezones.py:timezone_name` raises an actionable `ValueError` ("An explicit IANA timezone is required for {code}") instead of a `KeyError`; the trust boundary (`TripInput`) accepts an explicit IANA override before this triggers. |
| Deterministic generic mock provider for arbitrary routes | DONE | `providers/mock.py:_generic_rows` — sha256-seeded, no `random()`, produces 3 valid alternatives for any route/cabin not in the seeded table. **Verified live end-to-end**: created a BOM→LHR trip for 2026-10-05 (outside the seeded Sept dates), simulated a cancellation, got 3 generic (`SK`/`AT`/`NX`) options, ranked, approved, executed to `EXECUTED`. |
| Approval/rejection idempotent + DB constraint + state guards | DONE | `approvals.UNIQUE(plan_id)` constraint; `_decide()` in `routes/approvals.py` returns the identical cached response on a repeat call, 409s on a conflicting decision, 409s if plan isn't `AWAITING_APPROVAL`. Verified live: double-reject → identical response; approve-after-reject → 409; cross-account reject → 404. |
| Escalation to DISRUPTED/RECOVERY_FAILED from every early state | DONE | `core/state_machine.py` TRANSITIONS table allows `DISRUPTED→RECOVERY_FAILED` and `PLANNING→RECOVERY_FAILED`; `planner/orchestrate.py:_escalate` + `on_disruption_detected`'s except-block calls it on any planning exception, never 500s the simulate/poll caller. |
| `make api` uses `api/.venv/bin/uvicorn`; `make test` uses venv Python | DONE | Already correct in `Makefile` (verified by reading it — no change needed). |
| Tests use a dedicated test DB, no dev `.env`/demo rows/paid providers | DONE | `make test` creates/reuses `concierge_test`, applies schema+seed+migrations fresh, runs with `TESTING=true` and every LLM key blank. `make test` → **113 passed**. |
| Fallback narration literal `None` fixed | DONE | `llm/fallback.py:_value()` coalesces `None`→default everywhere; `_cost_change(None)` → "has not been calculated"; `formatDelta` on the frontend does the same. Verified live: rendered plan text has no literal `None`. |
| Sequential blocking LLM narration fixed | DONE | `planner/orchestrate.py` computes deterministic fallback narration synchronously (`_narrate`), returns the plan immediately, then enriches with the real LLM call on a background `ThreadPoolExecutor(max_workers=2)` (`_queue_narration`) — never blocks the request/scheduler thread. |
| Transient plan-404 not shown as permanent failure | DONE | `web/app/src/screens/Pages.tsx:RecoveryPage` catches a 404 from `getPlan()` and renders "still being prepared" with a "Check again" retry, distinct from the "no disruption yet" empty state. |
| Stale in-flight frontend refetches | DONE | `web/app/src/lib/requestGate.ts` (`createRequestGate`) used by `useLoad()` in `Pages.tsx` — cancels/ignores a still-in-flight response once a newer request has been issued (route change, account switch). |
| CORS/proxy consistency across 5173/5174/production | DONE | `.env.example` CORS_ORIGINS includes both dev ports; `web/app/vite.config.ts` proxies `/auth,/trips,/approvals,/disruptions,/simulate,/health,/ws` to `:8000` so the app is same-origin in dev; `VITE_API_URL` override exists for a built bundle on another origin. |

## P1 — Real routing

| Item | State | Evidence |
|---|---|---|
| `react-router-dom` added, both surfaces | DONE | Already a dependency in both `package.json`s; wired in `main.tsx` (`BrowserRouter`). |
| Public routes `/`, `/how-it-works`, `/faq`, real 404 | DONE | `web/site/src/App.tsx`. Verified live, no overflow, no console errors, at all 7 breakpoints. |
| App routes: login/signup/app/trips/trips-new/trip-detail/recovery/profile + authed 404 + guards | DONE | `web/app/src/App.tsx` — `ProtectedShell` redirects to `/login` with `state.from` when unauthenticated; verified live: visiting `/app/trips` post-logout redirects to `/login`. |
| Dashboard no longer one unlabelled page | DONE | Route-appropriate panels in `screens/Pages.tsx` (`OverviewPage`, `TripsPage`, `TripDetailPage`, `RecoveryPage`, `NewTripPage`, `ProfilePage`), each with its own `PageHead`. |
| Deep links / back-forward / refresh on nested routes | DONE | Verified live: direct `goto` to `/app/trips/:id/recovery` renders correctly (BrowserRouter + server history fallback via `_redirects`). |
| Centralized public↔app URL | DONE | `web/site/src/lib/links.ts:appLink()` and `web/app/.env`'s `VITE_SITE_URL`/`VITE_APP_URL` — every cross-surface CTA goes through it. |

## P2 — States and ui-ux coverage

| Item | State | Evidence |
|---|---|---|
| Loading/empty/success/error states | DONE | `Pages.tsx` — every page has an explicit `loading`/`error`/`empty`/`data` branch using `Skeletons.tsx` and `EmptyState.tsx`. Verified live: fresh account → "The concierge has nothing to watch" empty state, not a blank screen. |
| No feature hidden behind `plan !== null` with no explanation | DONE | `RecoveryPage` distinguishes "no disruption yet" vs "plan still preparing" (transient 404) vs each `plan.state` (`FAILED`/`REJECTED`/`AWAITING_APPROVAL`/`EXECUTED`) with copy for each. |
| ui-ux/ artifact → route/component mapping | DONE (see STATUS.md decision log) | Documented decisions already on record: 404 artwork → `EmptyState` (no unreachable route needed once routing shipped — still valid as the "everything failed" state); hotel map → abstract locator in `HotelPolicyCard`, explicitly not a fake Google Maps ("no map SDK, no key budget, a fake map on a trust screen is worse than none"); flight-alternatives/flight-status/hotel-policy loading states → `Skeletons.tsx`; confirmation → `ConfirmationCard.tsx`; radar visualization → `RadarPanel.tsx`; profile dropdown → `ProfileMenu.tsx`. `site.html` → ported into `web/site` React components (C12). |

## P3 — Visual system

| Item | State | Evidence |
|---|---|---|
| ATC logo from `op.pdf`, favicons, manifest | DONE | `atc-logo.png`, `favicon.png`, `icon-512.png`, `manifest.webmanifest` present in both `web/app/public` and `web/site/public`; old `vite.svg`/`react.svg`/`favicon.svg`/`icons.svg` removed (confirmed via `git show 5eb0322` diff — deletions present). |
| Aircraft-window hero, correct transparency | DONE | Verified visually via screenshot (`/tmp/hero.png`) — real photographed window, blue sky, no black rectangle. |
| Semantic design tokens + typeface stack | DONE | Plus Jakarta Sans / Newsreader / JetBrains Mono via `@fontsource-variable/*` (self-hosted, no hotlink); ATC navy/aviation-blue palette in `site.css`/`index.css`. |
| Cinematic aircraft-window homepage, scroll-through, CTAs, skip link, reduced-motion | DONE | `WindowIntro.tsx` — scroll-driven scale/opacity via `requestAnimationFrame`, `prefers-reduced-motion` early-return. Verified live: skip link is first tab stop with a 3px focus outline; reduced-motion emulation collapses the intro to a static state (opacity 1, no transform). |
| "Five stages" sticky stacked-card section | DONE | `.stage-card { position: sticky; top: 6.5rem…16.5rem }` in `site.css`, mobile fallback to `position: relative`. Verified live at 1440px (cards stack while scrolling) and confirmed reduced-motion reveals all 5 immediately. |
| Progress bar: 0→100%, no overflow, recalculates, `scaleX()`, no per-scroll-frame re-render | DONE | `SiteHeader.tsx` — `requestAnimationFrame`-batched scroll handler + `ResizeObserver` on `documentElement` + `document.fonts.ready` hook; `.progress-line { transform-origin: left }`. Verified live: `scaleX(0)` at top, `scaleX(1)` at bottom, stays inside `.progress-track` (`overflow: hidden`). |
| No horizontal overflow at 320/375/390/768/1024/1280/1440 | DONE | Verified live via `scrollWidth === clientWidth` at all 7 breakpoints on `/`, `/how-it-works`, `/faq`, unknown route, and on `/app`, `/app/trips`, `/app/trips/new`, `/app/profile` while authenticated. |
| WCAG 2.2 AA basics | PARTIAL → mostly DONE this session | Found and fixed two real defects (below). Spot-checked contrast is dark-navy-on-white / white-on-navy throughout (high contrast by construction); did not run a full axe-core sweep — see remaining limitations. |

---

## Fixed this session

1. **Duplicate `<h1>` on the site homepage.** `WindowIntro.tsx` renders an `<h1>` ("When plans break…") and `Hero.tsx` rendered a second `<h1>` ("Never manage a cancelled flight alone again.") on the same page (`/`). Found via the browser accessibility tree. Fixed: `web/site/src/sections/Hero.tsx` heading demoted to `<h2>`. Rebuilt + relinted clean.
2. **Footer nav links under the WCAG 2.5.8 24px touch-target minimum.** `SiteFooter.tsx`'s "On this page"/"Try it" links were block-level (not inline-in-a-sentence, so not exempt) at 20px tall with no padding. Fixed: added `inline-block py-1.5`. Rebuilt + relinted clean; verified live no more sub-24px targets in the footer at 375px viewport.

## Verification run this session (commands + results)

```
make test
  → 113 passed, 2 warnings in 2.58s

web/app: npm run build   → ✓ built in 537ms (0 errors)
web/app: npm run lint    → oxlint, exit 0
web/site: npm run build  → ✓ built in ~520-540ms (0 errors)
web/site: npm run lint   → oxlint, exit 0

GET /health                                → {"ok":true}
POST /auth/register (A, B)                 → 201, HttpOnly+SameSite=lax cookie set
GET /auth/session                          → 200 while authed, 401 after logout
POST /trips (A)                            → 201, persisted
GET /trips/{A's id} as B                   → 404
GET /trips as B                            → []
GET /trips (no cookie)                     → 401
kill+restart uvicorn, GET /trips/{id}      → 200, data intact
POST /auth/logout, then GET /auth/session  → 401
POST /trips/extract (no LLM key)           → 503 with actionable message, no fake data
POST /simulate/cancellation → GET plan     → AWAITING_APPROVAL, real generic-mock options
POST /approvals/{id}/reject twice          → identical 200 response both times
POST /approvals/{id}/approve after reject  → 409 "Plan already rejected"
POST /approvals/{id}/reject as user B      → 404
Full browser flow: signup → /app → new trip
  → /app/trips/new → created → /app/trips/:id
  → simulate cancellation → /recovery
  → generic mock options (SK/AT/NX) ranked
  → approve → EXECUTED
  → profile → log out → /login
  → direct nav to /app/trips → redirected to /login
Overflow check (scrollWidth===clientWidth), 320–1440px:
  site: /, /how-it-works, /faq, unknown route — all clean
  app (authenticated): /app, /app/trips, /app/trips/new, /app/profile — all clean
Keyboard: first Tab lands on skip link, 3px solid focus outline
prefers-reduced-motion emulated: window-intro static, all 5 stage cards opacity 1
```

## Genuine remaining limitations

- **Demo login credentials.** No demo/seeded user account exists — `db/seed.sql` inserts traveller rows directly, not through `/auth/register`, so there is no password to hand a judge/reviewer. Use `POST /auth/register` to create a fresh account (e.g. `demo@example.com` / `CorrectHorse1!Battery` — 12+ chars, upper/lower/number/symbol) and build a trip from there; every code path (manual entry, simulate, plan, approve, execute) works from a clean account, verified above. Seeding a real login-capable demo account was out of scope for this pass since no target demo email was specified — flag before a live demo.
- **`/trips/extract` requires a configured LLM key.** With every LLM key blank (the checked-in dev `.env`), extraction correctly 503s rather than faking a result. This is intentional (no fake success states) but means the paste-a-booking flow needs a real `GROQ_API_KEY` (or another chain provider) to demonstrate live.
- **No full axe-core/Lighthouse accessibility sweep was run** — verification here was targeted (heading structure, focus order/visibility, touch targets, reduced motion, contrast by inspection). A full automated a11y audit was not executed this session.
- **Duffel/Nuitee/AeroDataBox/AviationStack live keys are unconfigured** in this environment (by design — `DEMO_MODE=true`, mock providers are the default per `TEAM.md`/`ARCHITECTURE.md`). Everything above was verified against the mock provider path, which is also the documented demo default.
