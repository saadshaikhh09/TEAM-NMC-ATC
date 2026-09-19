# Demo Script (90 Seconds) — Owner: Person D (Atif)

**Target:** Exactly 90 seconds read aloud. Rehearse against clean `make reset` with `DEMO_MODE=true`.

---

## The Spoken Script (Timed Word-for-Word)

### [0:00 – 0:15] The Setup & The Constraint
> **Spoken:**
> *"This is Priya Sharma. She is traveling from Mumbai to London for a critical client presentation tomorrow morning. Notice her declared hard constraint right here on screen before anything happens: she must arrive by 09:00 AM London time. No exceptions."*
>
> **On Screen:** Dashboard showing Priya's active trip card (BOM -> LHR), status `MONITORING`, attached hotel at Kensington Central, and constraints card prominently displaying `hard_arrival_by: 09:00` with reason *"client presentation, cannot be missed"*.

---

### [0:15 – 0:30] Disruption Detection
> **Spoken:**
> *"Her flight Air India AI131 gets cancelled. The event lands instantly in our dashboard over WebSocket. Watch the timeline start moving autonomously."*
>
> **On Screen:** Disruption event triggers (`POST /simulate/cancellation`). Status flips to `DISRUPTED`, then `PLANNING`. The agent timeline begins filling stage by stage in real time.

---

### [0:30 – 0:45] The Decision Engine at Work
> **Spoken:**
> *"The concierge evaluates 14 alternative flights across carriers. It doesn't just look for cheap tickets — it enforces her personal constraints and corporate policy first."*
>
> **On Screen:** Timeline records `EVALUATED: Evaluated 14 options, rejected 3 on policy`. Rejection panel reveals discarded options with clear human-readable explanations.

---

### [0:45 – 1:05] THE MOMENT — The Refusal
> **Spoken:**
> *"Look at this rejection right here. The engine found a flight that is both cheaper and faster. But look at the reason: it arrives at 11:40 AM. It could have saved her 8,000 rupees. It didn't, because she would have missed her presentation. Deterministic code protects what the traveler actually cares about."*
>
> **On Screen:** Rejection card highlighted: `Rejected — arrives 11:40, misses hard deadline 09:00 (₹8,000 cheaper)`.

---

### [1:05 – 1:20] Policy Gate & Sandbox Rebooking
> **Spoken:**
> *"The surviving option is within her company's auto-approval budget. The policy gate fires: the new British Airways flight is rebooked in sandbox. Because her arrival shifted by a day, the hotel check-in date automatically shifts at Kensington Central, and a drafted WhatsApp message is ready with the full rationale."*
>
> **On Screen:** Status moves to `EXECUTING` -> `REBOOKED` -> `HOTEL_SHIFTED` -> `NOTIFIED`. Booking references appear on the trip card. Member notification panel shows the LLM-narrated summary with fallback guarantee.

---

### [1:20 – 1:30] The Boundary & Closing
> **Spoken:**
> *"Our boundary, stated plainly: simulated disruption feed, real decision logic, sandbox booking. We didn't build a travel booking interface — we built a constraint-solving disruption engine."*
>
> **On Screen:** Full recovered trip view with complete auditable timeline from detection to resolution.

---

## Timed Pacing Checklist

- [x] **0:00–0:15:** Trip card & hard constraint (Priya, BOM -> LHR, 09:00 deadline)
- [x] **0:15–0:30:** Simulation event lands, timeline begins moving
- [x] **0:30–0:45:** 14 evaluated, 3 rejected on policy
- [x] **0:45–1:05:** **The Refusal:** Cheaper flight declined to protect the 09:00 presentation deadline ("could have saved ₹8,000...")
- [x] **1:05–1:20:** Policy gate auto-rebook + hotel date shift + notification narration
- [x] **1:20–1:30:** The boundary (simulated feed, real logic, sandbox booking) & closing tagline

**Word count:** ~210 words (~140 words/minute = ~90 seconds).

---

## Judge Q&A Defense — Know These Cold

### 1. "What happens if the flight books and the hotel date change fails?"
> **Answer:** *"The timeline records `REBOOKED` then `FAILED`. It never writes a `HOTEL_SHIFTED` action that didn't happen. The trip lands in `RECOVERY_FAILED` and immediately escalates for human intervention with the exact failure stage recorded in Postgres."*

### 2. "Is this truly autonomous or does a human click?"
> **Answer:** *"It has two distinct paths in the same codebase. When the fare and delay are below policy thresholds, the gate auto-executes with zero human clicks. When an option breaches policy (like Rohan's trip), it halts at `AWAITING_APPROVAL` with the exact violation reason rendered in the modal."*

### 3. "What is your disruption detection latency?"
> **Answer:** *"Our event processing latency from receipt to rebooking is sub-second. In production, status detection is bounded by our tiered polling schedule: every 12 hours >7 days out, every 6 hours 1–7 days out, and every 15 minutes within 24 hours of departure."*

### 4. "How do you ensure the LLM doesn't hallucinate a fake booking?"
> **Answer:** *"Our core architecture rule: Deterministic code decides; the LLM only narrates. The LLM has zero downward path to database writes or provider adapters. If every model API is down or blank, our templated fallback generates 100% of the member copy without failing."*

### 5. "Do you handle multi-leg missed connections?"
> **Answer:** *"The schema carries multi-leg itineraries (`leg: outbound | return`). In this hackathon build, the constraint planner evaluates single-leg disruptions end-to-end."*

### 6. "Why not MCP?"
> **Answer:** *"Our provider interface in `providers/base.py` is strictly tool-shaped (four flat verbs, normalized dataclasses). Wrapping it in MCP is a mechanical transport change; we chose to spend our hackathon hours perfecting the constraint-solving engine."*
