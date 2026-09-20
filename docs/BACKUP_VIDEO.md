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

## Recording sequence

Follow the canonical shot list in `docs/DEMO_SCRIPT.md`. The critical visual checkpoints are:

| Timestamp | Screen Focus | Voiceover Cue |
|---|---|---|
| **0:00–0:10** | Priya overview | Hard 09:00 London deadline |
| **0:10–0:22** | Declared cancellation button | Simulated feed, real event path |
| **0:22–0:38** | Alternatives and rejection | Four evaluated; cheaper VS355 refused |
| **0:38–0:54** | Approval modal | Fare exceeds auto-approval threshold |
| **0:54–1:12** | **Trip recovered.** | Ticketed flight, hotel impact, total cost |
| **1:12–1:24** | Live hotel map and timeline | Real location and auditable stages |
| **1:24–1:30** | Closing hold | Simulated feed, real logic, sandbox booking |

---

## Rehearsal & Verification Checklist

- [x] Script timed under 90s (`docs/DEMO_SCRIPT.md`)
- [ ] Map tiles loaded before recording; all decision and booking behavior remains deterministic
- [x] Audio track clear with no background noise
- [x] High-definition resolution (1080p / 16:9)
- [ ] Video file saved as `docs/demo_backup.mp4` or `docs/demo_backup.webm`
