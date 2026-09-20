---
name: Aero Concierge Premium
colors:
  surface: '#f8f9fb'
  surface-dim: '#e2e8f0'
  surface-bright: '#ffffff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f1f5f9'
  surface-container: '#e8edf4'
  surface-container-high: '#dbe3ee'
  surface-container-highest: '#cbd5e1'
  on-surface: '#191c1e'
  on-surface-variant: '#424751'
  inverse-surface: '#2e3132'
  inverse-on-surface: '#f0f1f3'
  outline: '#e2e8f0'
  outline-variant: '#cbd5e1'
  surface-tint: '#235eac'
  primary: '#004287'
  on-primary: '#ffffff'
  primary-container: '#e0edff'
  on-primary-container: '#0f3a73'
  inverse-primary: '#aac7ff'
  secondary: '#006a6a'
  on-secondary: '#ffffff'
  secondary-container: '#d1f4f4'
  on-secondary-container: '#007070'
  tertiary: '#6e3300'
  on-tertiary: '#ffffff'
  tertiary-container: '#924600'
  on-tertiary-container: '#ffc8a7'
  error: '#dc2626'
  on-error: '#ffffff'
  error-container: '#fee2e2'
  on-error-container: '#93000a'
  primary-fixed: '#d6e3ff'
  primary-fixed-dim: '#aac7ff'
  on-primary-fixed: '#001b3e'
  on-primary-fixed-variant: '#00458d'
  secondary-fixed: '#7ff5f4'
  secondary-fixed-dim: '#60d8d8'
  on-secondary-fixed: '#002020'
  on-secondary-fixed-variant: '#004f50'
  tertiary-fixed: '#ffdbc7'
  tertiary-fixed-dim: '#ffb688'
  on-tertiary-fixed: '#311300'
  on-tertiary-fixed-variant: '#733600'
  background: '#f8f9fb'
  on-background: '#191c1e'
  surface-variant: '#e1e2e4'
  accent-gradient-start: '#1E5AA8'
  accent-gradient-end: '#0FA3A3'
  success: '#059669'
  success-container: '#d1fae5'
  warning: '#d97706'
typography:
  display-lg:
    fontFamily: Newsreader
    fontSize: 48px
    fontWeight: '400'
    lineHeight: 56px
  display-lg-mobile:
    fontFamily: Newsreader
    fontSize: 32px
    fontWeight: '400'
    lineHeight: 40px
  headline-lg:
    fontFamily: Newsreader
    fontSize: 32px
    fontWeight: '400'
    lineHeight: 40px
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  title-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
  title-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 22px
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  label-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.25rem
  gutter-lg: 2rem
  margin: 1rem
  margin-md: 2rem
  margin-lg: 3rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
---

---
name: Aero Concierge Premium
colors:
  surface: '#f8f9fb'
  surface-dim: '#e2e8f0'
  surface-bright: '#ffffff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f1f5f9'
  surface-container: '#e8edf4'
  surface-container-high: '#dbe3ee'
  surface-container-highest: '#cbd5e1'
  primary: '#1E5AA8'
  primary-container: '#e0edff'
  on-primary: '#ffffff'
  on-primary-container: '#0f3a73'
  secondary: '#0FA3A3'
  secondary-container: '#d1f4f4'
  on-secondary: '#ffffff'
  accent-gradient-start: '#1E5AA8'
  accent-gradient-end: '#0FA3A3'
  success: '#059669'
  success-container: '#d1fae5'
  warning: '#d97706'
  error: '#dc2626'
  error-container: '#fee2e2'
  outline: '#e2e8f0'
  outline-variant: '#cbd5e1'
typography:
  primary: 'Plus Jakarta Sans', sans-serif
  display-accent: 'Newsreader', 'Playfair Display', Georgia, serif
  mono: 'JetBrains Mono', monospace
motion:
  spring-press: 'transform 0.15s cubic-bezier(0.34, 1.56, 0.64, 1)'
  spring-scale: 'active:scale-[0.985] transition-all duration-150 ease-out'
  scroll-reveal: 'opacity-0 translate-y-4 transition-all duration-500 ease-out'
elevation:
  card: '0 1px 3px 0 rgb(0 0 0 / 0.04), 0 1px 2px -1px rgb(0 0 0 / 0.04)'
  card-hover: '0 10px 15px -3px rgb(0 0 0 / 0.06), 0 4px 6px -4px rgb(0 0 0 / 0.03)'
  pressed: '0 1px 1px 0 rgb(0 0 0 / 0.04)'
---

# Aero Concierge Premium Refinements

## Design Principles & Motion System
- **Subtle Spring / Bounce Press Feedback**: Interactive cards, buttons, and pill toggles incorporate a restrained, refined press state (`active:scale-[0.985]` with `cubic-bezier(0.34, 1.56, 0.64, 1)` and slight elevation depression), delivering immediate tactile feedback on desktop click without visual gaudiness.
- **Selective AI Gradients**: Purely reserved for high-emphasis system agency indicators (e.g. `linear-gradient(135deg, #1E5AA8 0%, #0FA3A3 100%)` on the autonomous agent scanning/discovery badge or live telemetry pulse). Backgrounds, utility buttons, and standard cards remain clean solid white or neutral slate.
- **Expressive Emotional Typographic Accent**: Introduces a tailored display serif (`Newsreader` / refined editorial serif with soft italic nuance) exclusively for relief/milestone moments (such as "You're all set" on the confirmation screen), providing warmth and closure while technical data and body copy remain strictly geometric sans-serif (`Plus Jakarta Sans`).
- **Progressive Scroll-Based Reveals**: Longer dashboards feature staggered `IntersectionObserver` fade-up transitions (`translate-y-4` to `translate-y-0` and `opacity-0` to `opacity-100`) to visually clarify progressive loading rhythm.
- **Screen-to-Screen Transition Continuity**: Structural alert drawers slide in smoothly from top on disruption discovery; resolution confirmation unfolds with gentle opacity and container expansion.
