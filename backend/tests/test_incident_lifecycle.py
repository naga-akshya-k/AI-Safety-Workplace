import pytest
from app.services.incident_manager import IncidentManager

def test_incident_manager_cooldown_and_escalation():
    mgr = IncidentManager(cooldown_seconds=15.0)

    # 1. Initial alert at t=100.0, Severity Level 2 (Medium) -> Should create
    create, esc, inc_id = mgr.should_create_incident(
        camera_id=1, event_type="PPE_VIOLATION", entity_id=10, current_severity=2, now=100.0
    )
    assert create is True
    assert esc is False

    # Simulate registered incident ID 101
    mgr.active_incidents[(1, "PPE_VIOLATION", 10)] = (100.0, 2, 101)

    # 2. Subsequent alert at t=105.0 (5s elapsed < 15s cooldown), same severity 2 -> Should NOT create duplicate
    create2, esc2, inc_id2 = mgr.should_create_incident(
        camera_id=1, event_type="PPE_VIOLATION", entity_id=10, current_severity=2, now=105.0
    )
    assert create2 is False
    assert inc_id2 == 101

    # 3. Escalation at t=108.0: Severity jumps to Level 4 (Critical) -> Must BYPASS cooldown!
    create3, esc3, inc_id3 = mgr.should_create_incident(
        camera_id=1, event_type="PPE_VIOLATION", entity_id=10, current_severity=4, now=108.0
    )
    assert create3 is True
    assert esc3 is True
    assert inc_id3 == 101

    # 4. After cooldown (t=130.0, 22s elapsed > 15s cooldown) -> Should create new window
    mgr.active_incidents[(1, "PPE_VIOLATION", 10)] = (108.0, 4, 102)
    create4, esc4, inc_id4 = mgr.should_create_incident(
        camera_id=1, event_type="PPE_VIOLATION", entity_id=10, current_severity=4, now=130.0
    )
    assert create4 is True
    assert esc4 is False
