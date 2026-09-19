"""Trip state transitions. Owner: Person A.

One component owns state. If you need a trip to change status, call advance()
here — do not UPDATE trips.status from your own module.
"""

TRANSITIONS = {
    "CREATED":           {"MONITORING"},
    "MONITORING":        {"DISRUPTED", "RECOVERED"},
    "DISRUPTED":         {"PLANNING"},
    "PLANNING":          {"AWAITING_APPROVAL", "EXECUTING", "RECOVERY_FAILED"},
    "AWAITING_APPROVAL": {"EXECUTING", "RECOVERY_FAILED"},
    "EXECUTING":         {"RECOVERED", "RECOVERY_FAILED"},
    "RECOVERED":         {"MONITORING"},
    "RECOVERY_FAILED":   {"PLANNING"},
}


def can(current: str, nxt: str) -> bool:
    return nxt in TRANSITIONS.get(current, set())


def advance(session, trip_id: str, nxt: str):
    raise NotImplementedError("A4")
