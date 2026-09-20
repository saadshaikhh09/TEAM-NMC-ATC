# Demo-ready UI and hotel map design

## Goal

Make the public site and authenticated app visually dependable for a 90-second product demo, close the concrete form and responsive-layout gaps found in the rendered audit, and replace the static hotel image with a real interactive map.

## Scope

- Keep the existing public-site information architecture and intentional scroll-led hero.
- Keep the existing authenticated routes and reuse the implemented login, overview, trip, recovery, confirmation, profile, 404, and skeleton components.
- Normalize form controls, expose hotel flexibility and address inputs, remove mobile navigation overlap, and strengthen recovery/confirmation hierarchy.
- Store optional hotel address and coordinates in Postgres and return them through the existing trip API.
- Geocode a hotel once, server-side, during trip creation. A lookup failure must never prevent trip creation.
- Render an interactive MapLibre map following MapCN's component approach, using OpenStreetMap tiles with visible attribution. If coordinates are unavailable, render a useful OpenStreetMap search link instead of a fake map.
- Make the browser QA runner use installed Chromium by default so the demo checks do not depend on Microsoft Edge.
- Update the existing demo recording guide to match the actual interface and deterministic seeded flow.

## Architecture

The existing `TripInput -> persist_trip -> Trip response` flow remains the single write path. `HotelInput` gains `address` plus nullable `latitude` and `longitude`; when coordinates are absent, a small geocoder uses the hotel name, address, and city, observes the public Nominatim request rate, and returns `None` on network or parse failure. Coordinates are persisted on the hotel row so rendering never repeatedly geocodes.

The browser receives coordinates in the existing `Trip` payload. `HotelMap` owns the MapLibre lifecycle and is rendered by `HotelPolicyCard`; it imports MapLibre CSS, creates one marker and navigation controls, and destroys the map on unmount. It uses the OpenStreetMap raster tile endpoint with required attribution rather than MapCN's default CARTO style.

UI polish stays in existing components and CSS. No duplicate pages, design system, map provider abstraction, autocomplete service, or demo-only backend is added.

## Data contract

Hotel input and output gain:

```text
address: string | null
latitude: number | null   (-90 through 90)
longitude: number | null  (-180 through 180)
modifiable: boolean
```

The seeded Kensington hotel includes stable coordinates so the recorded demo works offline apart from map tiles. User-created hotels attempt geocoding, but failed geocoding leaves both coordinates null.

## User experience

- All text, date, number, and select controls share the same height, border, focus ring, and typography.
- Hotel entry includes an optional street address and a plain-language “dates can be changed” control.
- Mobile navigation sits in document flow below the header instead of covering form fields and cards.
- Hotel cards show a live map when coordinates exist and a clear location-search fallback otherwise.
- The executed recovery state leads with the existing confirmation card, with flight, hotel, savings/cost, and timeline information remaining visible below.
- Skeletons preserve the live card dimensions, including the hotel map area.

## Error and privacy behavior

- The geocoder sends only the entered hotel/location query, uses an identifying user agent, times out quickly, and never sends account or booking data.
- Geocoding errors are swallowed at the integration boundary and do not roll back the trip transaction.
- Invalid supplied coordinates are rejected by Pydantic before persistence.
- Map construction failure leaves the location fallback usable.

## Verification

- API tests cover coordinate validation, successful geocoding persistence, and non-fatal geocoding failure.
- App source tests cover the new route contract and guard against restoring a static hotel image.
- Browser QA checks select/input height parity and verifies mobile navigation does not overlap the main content.
- Run API tests, both frontend test/lint/build commands, and responsive browser QA with fresh screenshots.

