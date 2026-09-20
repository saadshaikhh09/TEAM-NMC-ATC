# Brag Plan: ATC — Autonomous Travel-Disruption Concierge

## What is this app?
An agent that watches your flight, catches the cancellation before the gate announcement does, and rebooks it against your own budget and deadline rules — showing you every alternative it turned down, and why, in plain English.

## The angle
The product's own UI already contains the punchline: a rejection panel titled "Cheaper did not mean better," where a ₹8,000-cheaper option is refused because it lands after the traveller's hard deadline. That's the whole pitch in one screen — this isn't a booking bot, it's a judgment call rendered as software. The video's job is to walk straight through that moment: disruption hits → agent reasons in public → the "obviously wrong" cheap option gets rejected on camera → the right one gets booked.

## Hook (first 2-3 seconds)
Dark navy field. A single mono status chip pulses: `MONITORING BA 143`. It flips to red mid-beat: `CANCELLED`. Serif display line slams in underneath: "Your flight just got cancelled." Small mono line: "3h 40m before departure."

## Key moments (the middle)
- The ops-console mockup materializes: red disruption banner ("Flight BA 143 cancelled by airline · Gate 24C"), then the navy telemetry bar beneath it reasoning out loud — "Evaluated 6 options, rejected 3 on your constraints."
- The rejection panel, in amber: "Cheaper did not mean better." A rejected option card reveals underneath it — ₹8,000 cheaper, refused because it lands after the 09:00 London deadline.
- The winning option card (Virgin Atlantic VS 302, Rank 1, +₹0, Score 98.4) gets a green "Booked and written to the trip timeline" check, and the agent timeline ticks through DETECTED → EVALUATED → AWAITING_APPROVAL → APPROVED → REBOOKED → RECOVERED in quick succession.

## Outro / punchline
Full-bleed navy. Serif italic line from the site's own hero copy: "Never manage a cancelled flight alone again." Mono wordmark/badge: `ATC — policy-gated rebooking, explained.`

## User flow worth showing
1. **Entry**: scheduled poll detects BA 143 cancelled, trip flips to DISRUPTED.
2. **Key action**: recovery planner evaluates alternatives against the traveller's own constraints, rejects the ones that violate them (cheaper ≠ better), ranks the rest.
3. **Result**: auto-rebooked / sent for one-click approval, timeline reaches RECOVERED.

This is the real product flow (agent timeline, rejection panel, approval modal, confirmation card in `web/app/src/components/`), not just the landing page — the landing page's hero mockup happens to render this exact flow, so it doubles as both source material and the visual.

## Tone
- Preset: polished
- Creative direction: airline ops command center — confident, procedural, a little tense at the top, resolved and clean at the bottom
- Interpretation: fewer, longer-held scenes; restrained motion (slides, crossfades, no cartoon bounce); typography and status chips carry the energy instead of frantic cuts; the amber rejection beat is allowed one sharper hit since it's the thesis of the video.

## Format: landscape — 1920x1080
## Duration: ~19s

## Visual identity (from the project)
- Background: `#F8FAFC` (light scenes) / `#0A2540` navy (hook + outro)
- Accent: `#0284C7` sky blue (primary actions, "Auto-approved" glow); `#10B981` emerald (success/booked); `#F59E0B`/amber (rejection panel); `#EF4444` red (disruption alert)
- Text: `#0A2540` navy on light, white on navy
- Display font: Newsreader (serif, italic used for emphasis — matches "flight alone" in the real hero)
- Body font: Plus Jakarta Sans
- Mono font: JetBrains Mono — used for status chips, badges, timestamps, rule names
- Strongest visual element: the Hero.tsx browser-chrome mockup (`web/site/src/sections/Hero.tsx`) — navy browser bar, red disruption banner, navy telemetry bar, two ranked option cards. Recreate this faithfully; it's already a finished piece of UI design.

## Share copy (draft)
Your flight just got cancelled. Ours already knows — and it can show you every option it turned down, and why.

## Audio direction
- Role: sparse professional accents over a restrained tech/ops music bed
- Music: moody, minimal corporate-tech track, ~90-100 BPM, low synth pulse with a quiet urgency at the top that resolves into something calmer by the outro — exact bundled track chosen by Hyperframes at composition time
- Music treatment: starts low under the hook (barely there), builds slightly through the console reveal, brief restrained swell under the rejection-panel reveal (the thesis beat), settles/fades for the outro line
- Music cue guidance: bundled-track cues to be read/detected at composition time; target strong cues at (a) the CANCELLED status flip (~0.5-1s in), (b) the rejection-panel headline landing (~mid-video), (c) the green "Booked" check / timeline completing (~three-quarters), (d) outro line settle. Beat-grid window for the DETECTED→RECOVERED timeline tick sequence — space each tick to at least every-other-beat so labels stay readable, not a rapid strobe.
- Audio-reactive treatment: subtle — the status chip glow / navy telemetry bar pulse may breathe faintly with the music, nothing waveform-y
- SFX posture: sparse, motion-matched, professional restraint — a status-flip tick, a soft alert chime on the disruption banner, a card-arrival thud on the rejection card, a light click + confirm chime on approve, no cartoon whooshes
- Audio-coupled moments: status chip flip (tick), disruption banner arrival (alert chime, restrained not sirenlike), rejection card reveal (thud), timeline items ticking through in sequence (soft successive ticks, spaced to the beat-grid), approve click (click + confirm chime)
- Restraint rule: no comedic stingers, no over-the-top whoosh library sounds, no cheerful chimes on the disruption beat — the cancellation moment stays serious even though the resolution is satisfying

## Storyboard

### Scene 1 — Hook — 2.5s
Dark navy full-bleed field. A mono status chip, top-left-of-center, reads `MONITORING BA 143` with a small pulsing dot (matches the site's live-poll dot). Mid-beat it flips: dot and border turn red, text swaps to `CANCELLED`. Serif display line slams in below, white: "Your flight just got cancelled." Small mono line under it settles in: "3h 40m before departure."
Sequential/interaction: yes — status chip flips state (green pulse → red), then headline slams, then mono subline settles after the headline (don't stack all three at once).
Audio intent: quiet tension, a single sharp alert beat on the flip, not alarming
Audio-coupled idea: status-flip tick synced to the chip color change
Music: low synth pulse enters, barely audible
Transition mood: hard cut → Scene 2

### Scene 2 — Console reveal — 4.5s
Cut to the ops-console mockup (recreated from `Hero.tsx`): navy browser chrome bar with traffic-light dots and the `concierge.atc.travel/monitor/BA-143` address pill, sliding/fading in as a whole card. Inside: the red disruption banner appears first — "Flight BA 143 cancelled by airline" + "Gate 24C" chip + "Detected 3h 40m before departure." Beat later, the navy telemetry bar beneath it arrives: a spinning `auto_awesome`-style icon, "Recovery planner," a green "Auto-approved" pulse dot, and the reasoning line typing or counting in: "Evaluated 6 options, rejected 3 on your constraints."
Sequential/interaction: yes — disruption banner first, telemetry bar second (~0.8-1s later), reasoning line types/settles last within the bar.
Audio intent: procedural, agent-is-working energy, calm competence
Audio-coupled idea: soft alert chime on the disruption banner's arrival; a light UI-whoosh on the whole card's entrance
Music: pulse continues, slight build
Transition mood: clean wipe/crossfade → Scene 3

### Scene 3 — Rejection panel (the thesis) — 5s
Cut to the amber rejection panel, full width: mono eyebrow "Your rules decided first," bold headline "Cheaper did not mean better." Beneath it, one rejection card reveals: mono line "Rejected · opt_4 · hard_arrival_deadline," bold reason "Lands after Priya's 09:00 London deadline," and a pill on the right: "₹8,000 cheaper." Hold on this long enough to read both the headline and the card in full.
Sequential/interaction: yes — headline lands first (slam-then-hold), rejection card reveals ~0.6s after, its two text pieces (rule label, reason) can stagger slightly but the price pill and reason must be simultaneous-readable, not racing.
Audio intent: this is the "aha" — a firmer, more deliberate hit than the rest of the video, restrained not comedic
Audio-coupled idea: a single card-arrival thud under the rejection card's entrance; brief restrained music swell under the headline
Music: brief swell, the video's one instant of real emphasis
Transition mood: clean wipe → Scene 4

### Scene 4 — Winning option + recovery timeline — 4.5s
Cut to the winning option card from the hero mockup: "Virgin Atlantic · VS 302," green "Rank 1 · Rebooked" chip, "+₹0 net change," "Score 98.4," and the line "Booked and written to the trip timeline" gets a green checkmark as it settles. Beneath/beside it, the agent timeline ticks through in quick succession: DETECTED → EVALUATED → AWAITING_APPROVAL → APPROVED → REBOOKED → RECOVERED, each label appearing and getting a check, spaced to the beat-grid so they're readable, not a blur.
Sequential/interaction: yes — option card settles first, then the six timeline labels tick in one by one (fast but beat-spaced, per the plan's readability floor for short labels).
Audio intent: resolution, quiet satisfaction, competence confirmed
Audio-coupled idea: a light click + confirm chime as the checkmark lands on the option card; soft successive ticks for each timeline label
Music: settling down from the Scene 3 swell
Transition mood: soft crossfade → Scene 5

### Scene 5 — Outro / punchline — 2.5s
Full-bleed navy, matching Scene 1. Centered serif italic line (site's own hero copy): "Never manage a cancelled flight alone again." Below it, a small mono badge: "ATC — policy-gated rebooking, explained."
Sequential/interaction: none — single composed frame, headline settles then badge fades in under it.
Audio intent: calm close, confidence without triumphalism
Audio-coupled idea: none beyond the music's own fade
Music: fades to a soft resolved tail, ends
Transition mood: — (end)

**Music mood for this video:** cinematic-restrained / professional-tech, tension-to-resolve arc
**Audio summary:** A quiet synth pulse opens under real tension (the cancellation), a light procedural energy carries the console and reasoning beats, one restrained swell marks the rejection-panel thesis, then everything settles into a calm, confident resolve under the outro line — sparse, motion-matched SFX throughout, no comedic or triumphant stingers.
