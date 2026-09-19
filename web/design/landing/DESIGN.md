---
name: ATC — Autonomous Travel-Disruption Concierge (Landing Page)
colors:
  navy: '#0A2540'
  navy-900: '#06182B'
  navy-800: '#0A2540'
  navy-700: '#0F3254'
  navy-50: '#F0F5FA'
  sky-brand: '#0284C7'
  sky-brand-hover: '#0369A1'
  sky-tint: '#E0F2FE'
  sky-subtle: '#F0F9FF'
  slate-brand: '#64748B'
  slate-light: '#94A3B8'
  slate-border: '#E2E8F0'
  slate-bg: '#F8FAFC'
  surface: '#FFFFFF'
  surface-muted: '#F8FAFC'
  success: '#10B981'
  success-emerald-600: '#059669'
  warning: '#F59E0B'
  error-red-600: '#DC2626'
  error-bg: '#FEF2F2'
  error-border: '#FECACA'
typography:
  display-lg:
    fontFamily: Newsreader
    usage: hero headline, section headlines, window-intro copy
  title-lg:
    fontFamily: Plus Jakarta Sans
    fontWeight: '600'
    usage: nav wordmark, card titles
  title-md:
    fontFamily: Plus Jakarta Sans
    fontWeight: '600'
    usage: buttons, labels
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontWeight: '600'
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontWeight: '600'
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontWeight: '400'
  body-md:
    fontFamily: Plus Jakarta Sans
    fontWeight: '400'
  label-md:
    fontFamily: Plus Jakarta Sans
    fontWeight: '600'
  label-sm:
    fontFamily: JetBrains Mono
    fontWeight: '500'
    usage: metrics, timestamps, monospace status text
radius:
  sm: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
elevation:
  card: 0 1px 3px rgba(10,37,64,0.06)
  card-hover: 0 10px 15px -3px rgba(10,37,64,0.12)
  floating-mockup: 0 25px 50px -12px rgba(10,37,64,0.16), 0 0 0 1px rgba(100,116,139,0.16)
  cta-panel: 0 20px 40px rgba(10,37,64,0.25)
motion:
  shimmer-sweep: 'light sweep across primary CTA buttons, 4.5s infinite'
  gentle-float: 'floating dashboard mockup, translateY ±7px, 6s ease-in-out infinite'
  radar-beam-sweep: 'radar icon rotation, 5s linear infinite'
  dash-flow: 'animated dashed route line, 2s linear infinite'
  soft-glow: 'pulsing box-shadow on rebooking badge, 3s ease-in-out infinite'
  starlight-pulse: 'scroll-progress-bar leading sparkle, 1.8s ease-in-out infinite'
  reveal-on-scroll: 'IntersectionObserver fade+translateY(22px) on section entry, 0.65s cubic-bezier(0.16,1,0.3,1)'
  faq-accordion: 'grid-template-rows 0fr to 1fr, 0.35s cubic-bezier(0.16,1,0.3,1)'
  nav-underline: 'link hover underline width 0% to 100%, 0.25s'
  counter-ticker: 'requestAnimationFrame count-up with exponential ease-out, 1.6s'
  window-intro-reveal: 'see Window-to-Clouds Intro System below'
accessibility:
  prefers-reduced-motion: 'all animations, reveals, and the window-intro are disabled/skipped; content shown in final state immediately'
---

# ATC Landing Page — Design Reference

## Structure
1. **Window-to-clouds scroll intro** — full-viewport pinned section, plays before the site header appears
2. **Nav bar** — fixed, fades in once the intro window is mostly open, solidifies with a shadow on scroll
3. **Hero** — status pill, two-line display headline, supporting copy, dual CTAs, floating 3D dashboard mockup showing a live disruption + rebooking flow
4. **Trust strip** — avatar cluster, animated counters (14,000+ flyers, 99.8% resolution), alliance/partner badges
5. **"How ATC Operates" architecture section** — numbered phases (ingestion, detection, rebooking, hotel resolution, notification), each a full-width card with metrics and icon chips
6. **FAQ accordion** — single-open accordion, 6 questions
7. **Final CTA panel** — dark rounded panel with ambient glow decorators, single primary button
8. **Footer** — wordmark, product/company/legal link columns, live-status indicator

## Window-to-Clouds Intro System
A `280vh` wrapper section (`#window-intro`) contains a `position: sticky` viewport-height layer. Inside it:
- `#intro-sky` — gradient sky background with five soft-blurred cloud shapes, each independently drifting via CSS keyframe animation
- `#intro-cabin` — dark cabin-wall gradient with a **CSS mask radial-gradient** hole (no image asset) whose radius is driven by the `--window-r` custom property
- `#intro-rim` — a bordered circle matching the hole's current radius, giving the illusion of a physical window frame
- `#intro-copy` — two lines of Newsreader display text ("We detect it first." / "We fix it for you.") that fade out early in the scroll

**Scroll-driven values** (computed in JS from scroll position within the wrapper, 0–1 progress):
- Window radius: eases from ~12% of the smaller viewport dimension up to full-screen coverage by 72% scroll progress, using a cubic ease-in-out curve
- Copy opacity: fades to 0 by 35% progress
- Rim opacity: fades out just as the radius finishes growing (94–100% of growth)
- Intro layer opacity: fades out entirely between 80–100% scroll progress, revealing the nav bar and hero underneath
- Nav bar opacity: fades in between 35–65% scroll progress

## Color Usage Rules
- `navy` (#0A2540) is the primary text/dark-surface color — headers, footer, dark CTA panel, cabin gradient
- `sky-brand` (#0284C7) is the single interactive/accent color — buttons, links, active states, live-status pills, radar/telemetry icons
- `slate` tones are reserved for secondary text and borders only, never as a primary action color
- `error`/`warning`/`success` colors are used exclusively inside the dashboard mockup to represent disruption states (cancelled/delayed/resolved) — never as general UI accents

## Anti-patterns (avoid when extending this page)
- Do not introduce a second accent color alongside `sky-brand` — the palette is intentionally single-accent
- Do not apply `reveal-on-scroll` to elements above the fold that are visible on load — it's for content the user scrolls to
- Do not skip the `prefers-reduced-motion` block when adding new animated elements — every animation in this file has a corresponding disable rule
