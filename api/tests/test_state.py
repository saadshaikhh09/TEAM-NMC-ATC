from core.state_machine import can


def test_legal_transitions():
    assert can("MONITORING", "DISRUPTED")
    assert can("PLANNING", "AWAITING_APPROVAL")
    assert not can("MONITORING", "EXECUTING")
    assert not can("RECOVERED", "EXECUTING")
