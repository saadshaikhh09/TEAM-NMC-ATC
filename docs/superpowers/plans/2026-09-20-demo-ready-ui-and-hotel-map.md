# Demo-ready UI and Hotel Map Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver polished responsive app/site surfaces, real mapped hotel locations, and a reliable 90-second demo path.

**Architecture:** Extend the existing hotel contract with optional location data, geocode once at the backend write boundary, and render that data through a small MapLibre component modeled on MapCN. Keep all routes and existing state components; improve them in place and use the existing seeded recovery flow for recording.

**Tech Stack:** FastAPI, Pydantic, SQLAlchemy, PostgreSQL, React 19, TypeScript, MapLibre GL JS, CSS, Node test runner, Pytest, Playwright.

**Spec:** `docs/superpowers/specs/2026-09-20-demo-ready-ui-and-hotel-map-design.md`

## Global Constraints

- Do not create duplicate pages for screens already represented in `ui-ux/` and implemented in the app.
- Trip creation succeeds even when geocoding is unavailable.
- OpenStreetMap attribution stays visible on every live map.
- Seeded demo data remains deterministic and usable without geocoding.
- Use no new abstraction beyond the one geocoder function and one map component.
- Do not commit; the user requested implementation, not repository history changes.

## Review Focus

- Empty hotel address: geocode from hotel name and city without sending empty comma segments.
- Geocoder timeout or malformed JSON: persist the trip with null coordinates.
- Latitude/longitude bounds: reject invalid values at the API boundary.
- Missing coordinates in an old trip: show an accessible search link, never a broken/blank map.
- 320px viewport: controls remain within the viewport and navigation never covers the active field.

---

### Task 1: Persist hotel locations without making geocoding a hard dependency

**Files:**
- Create: `api/providers/geocoding.py`
- Create: `api/tests/test_geocoding.py`
- Create: `db/migrations/004_hotel_location.sql`
- Modify: `api/core/models.py`
- Modify: `api/core/trip_service.py`
- Modify: `api/routes/trips.py`
- Modify: `api/tests/test_trip_input.py`
- Modify: `api/tests/test_trips.py`
- Modify: `db/schema.sql`
- Modify: `db/seed.sql`

**Interfaces:**
- Produces: `geocode_hotel(name: str, city: str, address: str | None) -> tuple[float, float] | None`.
- Produces: hotel API fields `address`, `latitude`, and `longitude`.
- Consumes: the existing `HotelInput`, `persist_trip`, and trip serialization path.

- [ ] **Step 1: Add failing input and persistence tests**

  Add tests asserting coordinate bounds, successful injected geocoding persistence, and geocoder failure leaving coordinates null while returning HTTP 201.

- [ ] **Step 2: Run the focused tests and confirm RED**

  Run: `cd api && .venv/bin/python -m pytest tests/test_geocoding.py tests/test_trip_input.py tests/test_trips.py -q`

  Expected: failures because location fields and `geocode_hotel` do not exist.

- [ ] **Step 3: Implement the minimum geocoder and schema changes**

  Use `urllib.request` with a short timeout and URL-encoded `format=jsonv2&limit=1&q=...`; parse only finite in-range floats and return `None` for URL, JSON, or data errors. Add nullable database columns and seed coordinates for Kensington Central.

- [ ] **Step 4: Resolve location in the existing persistence path**

  If both coordinates are supplied, store them. Otherwise call `geocode_hotel`; assign the returned pair when present and continue unchanged when absent.

- [ ] **Step 5: Run focused and full API tests**

  Run the focused command from Step 2, then `make test`.

---

### Task 2: Render the hotel through a MapCN-style interactive map

**Files:**
- Create: `web/app/src/components/HotelMap.tsx`
- Modify: `web/app/src/components/HotelPolicyCard.tsx`
- Modify: `web/app/src/components/Skeletons.tsx`
- Modify: `web/app/src/types/index.ts`
- Modify: `web/app/src/main.tsx`
- Modify: `web/app/src/index.css`
- Modify: `web/app/tests/app-foundation.test.ts`
- Modify: `web/app/package.json`
- Modify: `web/app/package-lock.json`

**Interfaces:**
- Consumes: `Hotel.address`, `Hotel.latitude`, and `Hotel.longitude` from Task 1.
- Produces: `HotelMap({ hotel }: { hotel: Hotel })` with live-map and search-fallback states.

- [ ] **Step 1: Add failing source-contract tests**

  Assert that `HotelPolicyCard` renders `HotelMap`, the hotel type exposes nullable coordinates, the old `/assets/heathrow-map.png` reference is absent, and the map source includes OpenStreetMap attribution.

- [ ] **Step 2: Run the app tests and confirm RED**

  Run: `cd web/app && npm test`

  Expected: failures because `HotelMap` and location fields are missing.

- [ ] **Step 3: Install MapLibre and implement the component**

  Run: `cd web/app && npm install maplibre-gl`

  Create one MapLibre map with an OSM raster source, a marker, navigation controls, cleanup on unmount, a descriptive label, and an OpenStreetMap search link fallback for null coordinates.

- [ ] **Step 4: Replace the static image and match its loading geometry**

  Render `HotelMap` in the existing card and add a map rectangle to `HotelPolicySkeleton`; keep existing policy/date content.

- [ ] **Step 5: Run tests, lint, and build**

  Run: `cd web/app && npm test && npm run lint && npm run build`.

---

### Task 3: Fix audited form and mobile-layout defects

**Files:**
- Modify: `web/app/src/screens/Pages.tsx`
- Modify: `web/app/src/components/AppShell.tsx`
- Modify: `web/app/src/index.css`
- Modify: `web/app/tests/app-foundation.test.ts`
- Modify: `web/site/tests/browser-qa.mjs`

**Interfaces:**
- Consumes: the hotel fields from Task 1.
- Produces: aligned controls and non-overlapping mobile navigation.

- [ ] **Step 1: Add failing form and navigation checks**

  Add source assertions for hotel `address` and `modifiable` controls. In browser QA, compare cabin-select height with a neighboring input and assert the mobile nav bottom is above or equal to the main content top only when in normal flow, with no fixed positioning.

- [ ] **Step 2: Run tests and confirm RED**

  Run: `cd web/app && npm test`

  Expected: the new control assertions fail.

- [ ] **Step 3: Implement the controls and payload mapping**

  Add optional hotel address and a native checkbox for modifiable dates; send its boolean rather than hardcoding `true`.

- [ ] **Step 4: Fix root CSS selectors and mobile navigation positioning**

  Apply shared styling to `input, select, textarea`; style the checkbox separately; place mobile nav in flow beneath the header and make it sticky at the top on narrow screens so it cannot cover page content.

- [ ] **Step 5: Make browser QA portable**

  Launch bundled Playwright Chromium by default and honor optional `QA_BROWSER_CHANNEL` when explicitly supplied.

- [ ] **Step 6: Run app tests, lint, build, and browser QA**

  Run frontend commands, start the stack, then run `cd web/site && npm run qa`.

---

### Task 4: Polish the existing demo moments and recording guide

**Files:**
- Modify: `web/app/src/components/ConfirmationCard.tsx`
- Modify: `web/app/src/screens/Pages.tsx`
- Modify: `web/app/src/index.css`
- Modify: `docs/DEMO_SCRIPT.md`
- Modify: `docs/BACKUP_VIDEO.md`
- Delete: `docs/demo-script.md`

**Interfaces:**
- Consumes: the existing recovery plan, actions, hotel card, and skeleton components.
- Produces: a compact executed-state hero and one canonical recording guide.

- [ ] **Step 1: Add a failing app source check for the demo payoff**

  Assert the confirmation component contains the “Trip recovered” outcome and that the recovery page keeps the existing auditable timeline after the confirmation.

- [ ] **Step 2: Run app tests and confirm RED**

  Run: `cd web/app && npm test`.

- [ ] **Step 3: Refine existing recovery and confirmation markup/CSS**

  Strengthen the executed-state headline and summary grid, reduce above-the-fold clutter, and keep rejected options, mapped hotel, and timeline in the same page.

- [ ] **Step 4: Consolidate the demo documentation**

  Update the 90-second sequence to the actual clicks and visible labels, add capture settings and a preflight checklist, and remove the case-only duplicate script.

- [ ] **Step 5: Run all static verification**

  Run app and site tests, lint, and builds; run `git diff --check`.

---

### Task 5: End-to-end visual verification

**Files:**
- Modify only files from Tasks 1–4 if a verified regression requires a fix.

**Interfaces:**
- Consumes: the complete stack.
- Produces: screenshots and command evidence for the final handoff.

- [ ] **Step 1: Reset and launch the complete stack**

  Run `make reset`, then `./start.sh`.

- [ ] **Step 2: Run browser QA and inspect screenshots**

  Run `cd web/site && npm run qa`; inspect mobile and desktop screenshots for form alignment, navigation clearance, map rendering/fallback, loading shapes, and executed confirmation hierarchy.

- [ ] **Step 3: Run the final verification suite fresh**

  Run `make test`, both frontend test/lint/build command sets, and `git diff --check`.

- [ ] **Step 4: Audit the diff against the design**

  Confirm every spec bullet has a corresponding file change or verification result, and report any remaining external dependency such as live map-tile availability.

