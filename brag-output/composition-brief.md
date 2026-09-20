# Hyperframes Composition Brief: ATC — Autonomous Travel-Disruption Concierge

## Objective
Create a short launch-style brag video for ATC, an agent that detects flight disruptions, evaluates rebooking alternatives against the traveller's own constraints, and either auto-rebooks or asks for approval — showing every rejected option and why.

## Output
- Composition directory: `brag-output/composition/`
- Rendered video: `brag-output/brag.mp4`
- Format: landscape — 1920x1080
- Duration: ~19 seconds (15-25s range)

## Source Material
- Project root: `/Users/shahidmalek123gmail.com/Desktop/hackaton/travel-concierge`
- Primary files read: `README.md`, `web/site/src/sections/Hero.tsx`, `web/packages/tokens/tailwind.preset.js`, `web/site/src/site.css`, `web/app/src/components/RejectionPanel.tsx`, `web/app/src/components/ApprovalModal.tsx`, `web/app/src/screens/Pages.tsx`
- Product name: ATC (Autonomous Travel-Disruption Concierge)
- Tagline / strongest claim: "Never manage a cancelled flight alone again." / "Cheaper did not mean better."
- Key UI or visual moment to recreate: the Hero.tsx ops-console mockup — navy browser chrome, red disruption banner, navy "Recovery planner" telemetry bar, two ranked option cards (Virgin Atlantic Rank 1 Rebooked vs. American Airlines Rank 2) — plus the amber `RejectionPanel` component's "Cheaper did not mean better" moment and the agent timeline's status progression (DETECTED → EVALUATED → AWAITING_APPROVAL → APPROVED → REBOOKED → RECOVERED).
- Copy that must appear verbatim:
  - "Flight BA 143 cancelled by airline"
  - "Evaluated 6 options, rejected 3 on your constraints"
  - "Cheaper did not mean better."
  - "Booked and written to the trip timeline"
  - "Never manage a cancelled flight alone again."

## Creative Direction
- Tone preset: polished
- Creative direction: airline ops command center — confident, procedural, a little tense at the top, resolved and clean by the end
- Interpretation: fewer/longer-held scenes (5 scenes for ~19s), restrained motion (slides, crossfades — no cartoon bounce), typography and status chips carry energy instead of frantic cutting. The rejection-panel beat is the one place allowed a sharper emphasis, since it's the thesis of the video.
- Angle: The product's own UI already contains the punchline — a rejection panel that turns down a cheaper option because it misses the traveller's deadline. This isn't a booking bot, it's a judgment call rendered as software. The video walks straight through that moment: disruption hits → agent reasons in public → the "obviously wrong" cheap option gets rejected on camera → the right one gets booked.
- Hook: Dark navy field, a mono status chip pulses `MONITORING BA 143`, flips red to `CANCELLED`, serif headline slams in: "Your flight just got cancelled."
- Outro / punchline: "Never manage a cancelled flight alone again." + mono badge "ATC — policy-gated rebooking, explained."
- Avoid:
  - Generic SaaS language ("streamline your workflow", etc.)
  - Abstract filler visuals — every scene must show real product copy/UI
  - Unrelated visual redesign — stay inside the existing navy/sky/amber palette and the site's own card/chip conventions

## Visual Identity
- Background: `#F8FAFC` light scenes, `#0A2540` navy for hook/outro and browser chrome/telemetry bar
- Text: `#0A2540` navy on light backgrounds, white on navy
- Accent: `#0284C7` sky blue (primary/auto-approved), `#10B981` emerald (success/booked), `#F59E0B` amber (rejection panel), `#EF4444` red (disruption alert)
- Display font: Newsreader (serif; italic used for emphasis, matching the real hero's "flight alone" treatment)
- Body font: Plus Jakarta Sans
- Mono font: JetBrains Mono — status chips, badges, timestamps, rule names (e.g. `MONITORING BA 143`, `Rejected · opt_4 · hard_arrival_deadline`)
- Visual references from the project: `web/site/src/sections/Hero.tsx` (ops-console mockup — this is the primary visual to recreate), `web/app/src/components/RejectionPanel.tsx` (amber panel), `web/app/src/components/AgentTimeline.tsx` (status ticks), `web/packages/tokens/tailwind.preset.js` (exact palette values)

## Storyboard
Use the storyboard in `brag-output/brag-plan.md` as the creative contract. Full scene-by-scene detail, sequencing, and audio-coupled ideas are specified there — follow it exactly for what appears and in what order; Hyperframes owns exact timing/mechanics.

Scene summary:
1. Hook — 2.5s — mono status chip flips MONITORING → CANCELLED; headline "Your flight just got cancelled."; subline "3h 40m before departure."
2. Console reveal — 4.5s — ops-console mockup slides in: red disruption banner ("Flight BA 143 cancelled by airline · Gate 24C"), then navy telemetry bar ("Recovery planner … Evaluated 6 options, rejected 3 on your constraints").
3. Rejection panel (thesis) — 5s — amber panel headline "Cheaper did not mean better."; rejection card reveals "Rejected · opt_4 · hard_arrival_deadline" / "Lands after Priya's 09:00 London deadline" / "₹8,000 cheaper" pill.
4. Winning option + recovery timeline — 4.5s — Virgin Atlantic VS 302 card, Rank 1, +₹0, Score 98.4, green "Booked and written to the trip timeline" check; agent timeline ticks DETECTED → EVALUATED → AWAITING_APPROVAL → APPROVED → REBOOKED → RECOVERED.
5. Outro — 2.5s — navy full-bleed, serif italic "Never manage a cancelled flight alone again.", mono badge "ATC — policy-gated rebooking, explained."

## Audio
- Audio role: sparse professional accents over a restrained tech/ops music bed
- Audio arc: quiet tension under the cancellation → light procedural energy through the console/reasoning beats → one restrained swell at the rejection-panel thesis → settles to a calm, confident resolve for the outro
- Music: `happy-beats-business-moves-vol-12-by-ende-dot-app.mp3` ("steady and clean" — recommended for `polished`/`cinematic`), copied to `brag-output/composition/assets/music/`
- Music treatment: start low (~0.15-0.2) under the hook, ease up slightly (~0.3) through the console reveal, brief emphasis under the rejection-panel headline, settle and fade under the outro line. Never above 0.4 for the bed.
- Music cue guidance: bundled preset at `<skill-dir>/assets/music/cues/happy-beats-business-moves-vol-12-by-ende-dot-app.music-cues.{md,json}` — tempo ≈ 110 BPM, duration 117s (plenty of headroom for a 19s cut, use from 0s). Candidate strong-cue locks within the plan's 0-19s window: ~2.19-2.73s (status-chip CANCELLED flip / scene 1→2), ~6.56-7.09s (rejection-panel headline landing, scene 2→3), ~8.74s (rejection-card reveal thud, strongest cue in window at 0.99), ~13.11s (winning-card checkmark / timeline completing, scene 3→4 area). Use 1-3 of these, not all four; prefer whichever best preserves the plan's scene durations and readability. Beat grid (~0.55s spacing) available for the sequential timeline-tick reveals in scene 4 — snap to every other beat so the six status labels stay readable, not a strobe.
- Audio-reactive treatment: subtle — the status chip's glow / navy telemetry bar's ambient pulse may breathe faintly with RMS; no waveform/equalizer visuals
- Audio-coupled moments:
  - Scene 1, status chip flip — sharp small tick synced to the color change
  - Scene 2, disruption banner arrival — soft alert chime (restrained, not sirenlike)
  - Scene 3, rejection card reveal — card-arrival thud, the video's one firmer hit
  - Scene 4, timeline ticking through 6 states — soft successive ticks, snapped to the beat grid per the readability note above
  - Scene 4, approve/checkmark landing — light click + confirm chime
  - Scene 5, outro — none beyond the music's own fade
- SFX selection guidance: favor `impact/impactSoft_medium_*` or `interface/drop_001/002` for the disruption banner and rejection-card reveals; `interface/click_*` or `ui/mouseclick1` for the approve/checkmark moment; a single restrained `interface/bong_001` or `impact/impactBell_heavy_*` only if it fits the rejection-panel emphasis without feeling triumphant this early. Keep everything in the "polished" energy tier — 2-3 subtle SFX total plus the small per-tick accents in scene 4, nothing aggressive.
- SFX analysis guidance: read `<skill-dir>/assets/sfx/sfx-analysis.md`; prefer low/medium high-frequency-risk files since several moments repeat (the six timeline ticks) and this is a polished/restrained tone.
- Exact SFX choice: Hyperframes should choose filenames, timestamps, density, and volume based on the implemented animation.
- Audio files: copy the chosen music (and any Hyperframes-selected SFX) into `brag-output/composition/assets/`

## Hyperframes Instructions
Load the composition-building Hyperframes domain skills — `hyperframes-core` (composition contract + `data-*` timing), `hyperframes-animation` (motion), `hyperframes-creative` (design spec, beats, audio-reactive), `hyperframes-keyframes` (seek-safe keyframes), and `hyperframes-cli` (lint/check/render). `/brag` is its own workflow: do not enter the `hyperframes` entry-point intent interview and do not route into its generic promo / launch-video workflow. Prefer native Hyperframes conventions over anything in `/brag`.

Requirements:
- Show at least one real UI, copy, or visual element from the source project (the Hero.tsx console mockup and RejectionPanel are the required centerpieces).
- Keep all text readable in the final render — respect the reading-time floors noted in `brag-plan.md` (short labels ~0.8s settled, sentences ~0.3s/word).
- Keep the video within 15-25 seconds (target ~19s).
- Include the planned music/SFX layer — audio was not disabled by the user.
- Treat `/brag` audio notes as guidance, not a fixed cue sheet. Choose exact SFX after the visual animation exists.
- Treat music cue metadata as optional timing hints; ignore cues that hurt readability, scene pacing, or the product story. Use only 1-3 strong-cue locks total.
- Use SFX to support motion and interaction: card sounds for card-like reveals (rejection card, option card), short announcement cues for the rejection-panel payoff, click/confirm for the approve moment, restraint elsewhere.
- Honor the planned music treatment (low start, slight build, one restrained swell, fade under outro).
- Wire at least one subtle audio-reactive visual element (RMS/bass modulating glow/presence on an existing element — the telemetry bar or chip glow are good candidates). If extraction is unavailable, document that and skip rather than blocking the render.
- Use local assets for audio and any required runtime/media dependencies.
- Run `hyperframes check` before render — it is brag's single gate.
