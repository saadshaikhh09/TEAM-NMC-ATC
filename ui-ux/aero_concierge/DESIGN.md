---
name: Aero Concierge
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#424656'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#727687'
  outline-variant: '#c2c6d8'
  surface-tint: '#0054d6'
  primary: '#0050cb'
  on-primary: '#ffffff'
  primary-container: '#0066ff'
  on-primary-container: '#f8f7ff'
  inverse-primary: '#b3c5ff'
  secondary: '#49607e'
  on-secondary: '#ffffff'
  secondary-container: '#c4dcff'
  on-secondary-container: '#49617f'
  tertiary: '#005e90'
  on-tertiary: '#ffffff'
  tertiary-container: '#0078b6'
  on-tertiary-container: '#f5f8ff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dae1ff'
  primary-fixed-dim: '#b3c5ff'
  on-primary-fixed: '#001849'
  on-primary-fixed-variant: '#003fa4'
  secondary-fixed: '#d2e4ff'
  secondary-fixed-dim: '#b0c8eb'
  on-secondary-fixed: '#001c37'
  on-secondary-fixed-variant: '#314865'
  tertiary-fixed: '#cce5ff'
  tertiary-fixed-dim: '#93ccff'
  on-tertiary-fixed: '#001d31'
  on-tertiary-fixed-variant: '#004b73'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 44px
    fontWeight: '700'
    lineHeight: 52px
    letterSpacing: -0.03em
  display-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 38px
    letterSpacing: -0.025em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 30px
    fontWeight: '600'
    lineHeight: 38px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
    letterSpacing: -0.005em
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
    letterSpacing: 0em
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0.005em
  code-flight:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.06em
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.08em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-mobile: 0.75rem
  margin: 2rem
  margin-mobile: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style
The design system embodies the calm, decisive authority of aviation operations paired with the friction-free responsiveness of contemporary high-end travel tech. Built for travelers experiencing unexpected itinerary disruptions (flight cancellations, gate reassignments, tight connections, automated rebooking), the interface must defuse anxiety instantly. 

The aesthetic is precision-driven **Corporate Modern** elevated with subtle **Tonal Glass layers**:
- **Tone:** Authoritative, reassuring, hyper-efficient, and crystalline.
- **Visual Personality:** Crisp architectural layouts, high-visibility status cues, rhythmic tabular flight data, and luminous brand blues that communicate operational control.
- **Emotional Mandate:** Turn chaotic travel disruptions into deterministic, self-resolving itineraries in seconds.

## Colors
The palette balances institutional airline authority with urgent clarity:

- **Primary (`#0066FF`)**: Vibrant Sky Cobalt. Powers decisive actions, live progress trajectories, and primary resolutions.
- **Secondary (`#0A2540`)**: Deep Stratus Navy. Supplies high-contrast structural weight, navigation bars, flight itinerary header cards, and primary text.
- **Tertiary (`#0284C7`)**: High-Altitude Cyan. Denotes supplemental details, flight segment connectors, and informative tags.
- **Neutral (`#64748B`)**: Cool Slate. Foundations range from crisp slate canvas (`#F8FAFC`) and boundary lines (`#E2E8F0`) to secondary metadata (`#64748B`) and dense midnight copy (`#0F172A`).
- **Functional / Disruption Accents**:
  - Critical / Cancellation: Crimson Alert (`#EF4444`)
  - Warning / Looming Connection Delay: Amber Radar (`#F97316`)
  - Confirmed / Auto-Rebooked: Jetstream Emerald (`#10B981`)

## Typography
Typography is paired specifically for mission-critical legibility:
- **Headlines (`Plus Jakarta Sans`)**: Clean, contemporary geometric letterforms that deliver immediate reassurance and modernity.
- **Body Text (`Inter`)**: High x-height, neutral legibility optimized for rapid reading under travel stress and diverse lighting conditions.
- **Flight & Operational Data (`JetBrains Mono`)**: Applied to IATA airport codes (e.g., `LHR -> JFK`), flight callsigns (`BA 0178`), timestamps, terminal/gate numbers, and PNR locators to prevent visual confusion and emphasize operational telemetry.

## Layout & Spacing
The layout implements a responsive fluid grid that anchors content to standard dashboard viewports on desktop and converts to unified single-column disruption streams on mobile devices.

- **Desktop (>= 1024px)**: 12-column grid, max-width 1280px, centered with `margin: 2rem` and `gutter: 1.5rem`. Enables side-by-side comparison between the disrupted flight and prospective automated rebooking proposals.
- **Tablet (768px - 1023px)**: 8-column layout with collapsed secondary telemetry into expandable sheet views.
- **Mobile (< 768px)**: 4-column layout, `margin-mobile: 1rem` and `gutter-mobile: 0.75rem`. Urgent resolution actions lock into fixed bottom sheets to facilitate single-thumb resolution while navigating transit hubs.

## Elevation & Depth
Depth prioritizes scanning speed through structured tonal layering and calibrated ambient shadows tinted with Deep Stratus Navy (`#0A2540`):

- **Surface Floor (`Level 0`)**: `#F8FAFC`. The canvas background.
- **Resting Layer (`Level 1`)**: `#FFFFFF` with a crisp 1px perimeter border (`#E2E8F0`) and an ambient shadow: `0 1px 3px 0 rgba(10, 37, 64, 0.04), 0 1px 2px -1px rgba(10, 37, 64, 0.02)`. Used for passive cards, secondary flight legs, and baggage status modules.
- **Raised Interactive Layer (`Level 2`)**: `#FFFFFF` with shadow: `0 4px 6px -1px rgba(10, 37, 64, 0.06), 0 2px 4px -2px rgba(10, 37, 64, 0.04)`. Applied to proposed replacement itineraries and primary interactive blocks.
- **Overlay & Critical Focus (`Level 3`)**: Subtle frosted glass background blur (`backdrop-filter: blur(12px)`) at `rgba(255, 255, 255, 0.88)` with shadow: `0 20px 25px -5px rgba(10, 37, 64, 0.1), 0 8px 10px -6px rgba(10, 37, 64, 0.04)`. Employed for emergency modal alerts, gate change banners, and 1-tap rebooking confirmation sheets.

## Shapes
A unified **Rounded (Scale 2)** geometry is applied across all surfaces. 
- Base controls (inputs, buttons, segment toggles) feature `0.5rem` (8px) radius.
- Cards, boarding passes, and flight itinerary containers feature `rounded-lg` (`1rem` / 16px).
- Modals, full alert sheets, and bottom navigation sheets use `rounded-xl` (`1.5rem` / 24px).
- Airline tags, status chips, and flight progress nodes use fully pill-shaped radii for swift categorization.

## Components

### Buttons & Quick Triggers
- **Primary ("Accept Rebooking")**: Solid `#0066FF`, white text, 44px min height, `font-weight: 600`. Subtle hover shift to `#0052CC`. Active state scales down 1% for tactile response.
- **Secondary ("Browse Alternatives")**: Crisp `#FFFFFF` surface with `#E2E8F0` border, `#0A2540` text. Hover background shifts to `#F1F5F9`.
- **Urgent / Decline ("Cancel Leg & Refund")**: Light crimson background (`#FEF2F2`) with `#DC2626` text. Hover shifts to `#FEE2E2`.
- **Focus Rings**: Strict high-visibility dual ring: `2px` white offset followed by a `2px` solid `#0066FF` ring.

### Form Inputs & Selectors
- Background: `#FFFFFF`. Border: `1px solid #CBD5E1`. Roundedness: `0.5rem`.
- Padding: `0.625rem 0.875rem`. Font: `Inter` 14px.
- States: Focus shifts border to `#0066FF` with `box-shadow: 0 0 0 3px rgba(0, 102, 255, 0.15)`. Error states shift border to `#EF4444` with matching crimson glow.

### Status Chips & Flight Badges
- Pill-shaped (`9999px`), `0.25rem 0.625rem` padding, uppercase `JetBrains Mono` 10px font.
- **Disrupted / Cancelled**: Background `#FEE2E2`, Text `#B91C1C`.
- **Delayed**: Background `#FFEDD5`, Text `#C2410C`.
- **On Time / Confirmed**: Background `#D1FAE5`, Text `#047857`.

### Flight Cards & Itinerary Modules
- Divided visual layout: Upper section displays carrier badge, flight code, and dynamic disruption status badge; lower section highlights departure/arrival times in `Plus Jakarta Sans` 20px with mono IATA codes (`SFO`, `LHR`).
- Connecting segment visualizations display a horizontal dashed path colored in `#CBD5E1`, populated with a dynamic pin indicating current automated re-routing progress.

### Lists & Activity Logs
- Dividers use ultra-subtle `#F1F5F9`. Each entry displays an inline monospaced UTC/local timestamp, a bold event label, and a short resolution note.