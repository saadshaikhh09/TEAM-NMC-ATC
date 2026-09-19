# Backup Demo Video — Owner: Person D (Atif)

**Deadline:** Hour 24 (Hard checkpoint — NOT negotiable).

---

## Video Specifications

- **Target Duration:** 90 seconds (Max allowed: 2 minutes).
- **Environment:** `DEMO_MODE=true` against seeded database.
- **Provider Mode:** Deterministic Mock (`providers/mock.py`).
- **File Name / Format:** `docs/demo_backup.mp4` / `docs/demo_backup.webm`.

---

## Pre-Recording Setup

Run clean reset immediately before recording:
```bash
make reset
make api
make web
```

---

## Recording Sequence (Following `docs/DEMO_SCRIPT.md`)

| Timestamp | Screen Focus | Voiceover Cue |
|---|---|---|
| **0:00–0:15** | Dashboard (Priya Sharma, BOM $\rightarrow$ LHR) | *"Notice her declared hard constraint: arrive by 09:00 AM London time."* |
| **0:15–0:30** | Fire Cancellation via `POST /simulate/cancellation` | *"Her flight AI131 is cancelled. The timeline starts moving."* |
| **0:30–0:45** | Rejection panel pops up | *"The concierge evaluates 14 options, enforcing constraints first."* |
| **0:45–1:05** | **The Refusal:** Highlight 11:40 AM flight rejection | *"It could have saved ₹8,000. It didn't, because she would have missed her presentation."* |
| **1:05–1:20** | Auto-rebook & hotel date shift | *"British Airways flight booked, hotel shifted at Kensington Central, WhatsApp notification ready."* |
| **1:20–1:30** | Timeline review & closing | *"Simulated disruption feed, real decision logic, sandbox booking."* |

---

## Rehearsal & Verification Checklist

- [x] Script timed under 90s (`docs/DEMO_SCRIPT.md`)
- [x] Zero network calls during demo (`DEMO_MODE=true`)
- [x] Audio track clear with no background noise
- [x] High-definition resolution (1080p / 16:9)
- [x] Video file saved and committed into `docs/`
