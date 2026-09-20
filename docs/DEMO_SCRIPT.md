# Aero Concierge demo — 90 seconds

## Capture setup

- Record at 1920×1080, 100% browser zoom, with notifications hidden.
- Run `make reset`, then `./start.sh` immediately before recording.
- Open `http://localhost:5174/login` and use `demo@atc.local` / `DemoPass!2026`.
- Keep the cursor near the active control and use smooth, short scrolls.
- Boundary to say aloud: simulated disruption feed, deterministic decision logic, sandbox booking.

## Shot list and voiceover

### 0:00–0:10 — Establish the problem

**Screen:** Login, then the overview for Priya Sharma.

**Say:** “Aero Concierge watches a traveller’s whole itinerary, not just a flight. Priya must reach London before her nine-AM client presentation, and that hard constraint is stored before disruption happens.”

### 0:10–0:22 — Trigger the declared simulation

**Screen:** Open Priya’s recovery workspace and click **Simulate cancellation**.

**Say:** “I’m triggering the declared test harness. It writes the same disruption event as a live provider; everything after detection is the real planning and policy path.”

### 0:22–0:38 — Show the decision

**Screen:** Let the loading states resolve. Point to the recommended BA138 option and the rejected VS355 option.

**Say:** “The engine evaluates four deterministic alternatives. This Virgin option is eight thousand rupees cheaper, but it arrives at eleven-forty and misses Priya’s hard deadline, so the engine refuses it.”

### 0:38–0:54 — Show the approval boundary

**Screen:** Click **Review decision**. Pause on the reason, fare, hotel impact, and net change; click **Approve recovery**.

**Say:** “The chosen fare exceeds Priya’s auto-approval threshold, so the concierge stops for consent instead of silently spending. The traveller can see the exact flight and hotel impact before approving.”

### 0:54–1:12 — Deliver the payoff

**Screen:** Hold on **Trip recovered.**, the ticketed flight, total cost, and resolution time.

**Say:** “One approval completes the sandbox rebooking, moves the hotel dates, and records the member message. The confirmation is based on provider results—not generated text.”

### 1:12–1:24 — Show the real map and audit trail

**Screen:** Scroll to the live hotel map, then the agent timeline.

**Say:** “The hotel is now located on a real OpenStreetMap view, and every autonomous stage remains visible in the audit timeline.”

### 1:24–1:30 — Close

**Screen:** Hold on the final timeline.

**Say:** “Simulated feed, real decision logic, sandbox booking. Aero Concierge protects what the traveller actually cares about.”

## Preflight checklist

- [ ] `make reset` completed and Priya is `MONITORING`.
- [ ] Site, app, and API are healthy.
- [ ] Hotel map tiles are visible; if the network is unavailable, use the OpenStreetMap fallback link.
- [ ] Browser zoom is 100%, no bookmarks bar, no unrelated tabs.
- [ ] Microphone peaks below clipping and room noise is controlled.
- [ ] Final recording is under two minutes and exported as 1080p MP4/WebM.

## Judge-ready boundaries

- Core filtering, ranking, approval, state transitions, and audit writes are deterministic code.
- The model only narrates; it cannot write bookings or bypass constraints.
- Flight and hotel bookings use the deterministic sandbox provider.
- The map uses real OpenStreetMap tiles and cached hotel coordinates.
