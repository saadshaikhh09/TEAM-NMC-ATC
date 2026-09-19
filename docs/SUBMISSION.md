# PS-8: Autonomous Travel-Disruption Concierge
### Team Submission Writeup — Team NMC-ATC

**Repository:** `https://github.com/saadshaikhh09/TEAM-NMC-ATC`  
**Team Members:**
- **Shahid** (Person A) — Domain spine, recovery planner, policy engine, audit trail
- **Vishnu** (Person B) — Disruption monitor, tiered scheduler, status provider adapters, WebSocket stream
- **Saad** (Person C) — Web dashboard, live agent timeline, rejection panel, approval modals
- **Atif** (Person D) — Duffel & Nuitee provider integrations, notification copy, demo, backup video & submission

---

## 1. Executive Summary & The Core Differentiator

When flights are cancelled or delayed, passengers are overwhelmed by fragmented options across multiple portals under intense time pressure. Most AI travel agents simply sort alternatives by lowest price or shortest duration. 

**Our differentiator:** Our concierge **actively refuses options that violate the traveller's declared constraints**, explaining why in plain English a non-engineer immediately understands.

> **The Defining Demo Moment:**
> For a passenger traveling for an indispensable 09:00 AM presentation, the engine identifies a flight that is both faster and ₹8,000 cheaper. Rather than selecting it, the engine **rejects** it:
> 
> *`"Rejected — arrives 11:40, misses hard deadline 09:00 (would have saved ₹8,000)"`*
> 
> It declines the cost savings to protect the traveller's actual real-world goal.

---

## 2. The Core Architecture Rule

> **Deterministic code decides. The LLM narrates.**

In mission-critical travel operations, putting a probabilistic Large Language Model in the autonomous decision or database-write path creates hallucinations and untraceable bookings. 

In our architecture:
1. **Deterministic Decision Engine:** Hard constraints, policy rules, ranking weights (`policy.yaml`), and threshold gates are computed in strict, deterministic Python code.
2. **LLM Narration Sidecar:** The model receives completed plans and drafts passenger-facing explanations and WhatsApp messages. It has **zero downward path** to database writes or booking adapters.
3. **Resilience & Fallback Guarantee:** If every LLM provider is rate-limited or offline, our templated fallback generates 100% of member communications without stalling execution.

---

## 3. The Declared Boundary

We state our operating boundary clearly and transparently:
- **Simulated disruption feed:** High-speed event simulation (`/simulate/cancellation`, `/simulate/delay`) to provide reproducible, zero-latency demos without burning monthly API quotas.
- **Real decision logic:** Complete constraint evaluation, scoring, and policy gating.
- **Sandbox booking writes:** Real API round-trips against Duffel and Nuitee/LiteAPI sandboxes.
- **No live airline write access claimed:** Airlines do not grant write access to third-party hackathon builds; we model airline and hotel interactions honestly.

---

## 4. Key Capabilities & The 8 Core Features

1. **Traveller Constraints Engine:** Per-person rules (e.g., hard arrival deadlines, cabin class, carrier exclusions) enforced as hard filters before ranking.
2. **Filter with Rejections:** Generates clear, human-readable rejection reasons stored in the audit trail.
3. **Multi-Leg Hotel Impact & Date Shift:** Automatically recalculates hotel dates when flight arrivals shift. Because hotel APIs lack modify endpoints, we implement a safe **cancel-then-rebook** lifecycle with transparent error reporting if rebooking fails.
4. **Tiered Polling Scheduler:** Intelligent cadence saving 90%+ API quota (12h cadence >7 days out, 6h cadence 1–7 days out, 15m cadence <24h).
5. **Policy Approval Gate:** Pure autonomous execution for bookings under the corporate threshold (e.g. ₹45,000); halts at `AWAITING_APPROVAL` with clear escalation reason when exceeded.
6. **Live Agent Timeline:** Powered by a strict single-writer pattern (`core/audit.py` $\rightarrow$ `agent_actions`) rendering live stage-by-stage status over WebSockets.
7. **Multi-Provider Adapters:** Unified tool-shaped provider interface supporting AeroDataBox, AviationStack, Duffel, Nuitee, and Mock.
8. **Paste-Booking Extraction:** Ingests raw booking itineraries and extracts structured trip data.

---

## 5. Judge Q&A & Edge Cases

- **Q: What happens if the flight rebooks but the hotel date change fails?**  
  *A:* The timeline records `REBOOKED` followed by `FAILED`. It never records a false `HOTEL_SHIFTED`. The trip enters `RECOVERY_FAILED` and alerts operators with the exact error.
- **Q: How is detection latency measured?**  
  *A:* Processing latency from disruption event receipt to rebooking is sub-second. Production detection is bounded by our tiered polling intervals.
- **Q: Is this truly autonomous?**  
  *A:* Yes. Both fully autonomous and human-in-the-loop approval paths operate on the same state machine governed by `executor/gate.py`.

---

## 6. Verification & Reproducibility

To reproduce the complete demo on a clean environment:
```bash
# 1. Reset database with seeded trips
make reset

# 2. Run backend API
make api

# 3. Launch frontend dashboard
make web

# 4. Trigger disruption simulation
curl -X POST http://localhost:8000/simulate/cancellation
```
All unit tests run hermetically:
```bash
cd api && python -m pytest tests/ -v
```
