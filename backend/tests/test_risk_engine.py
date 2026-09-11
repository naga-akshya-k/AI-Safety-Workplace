import pytest
from app.services.risk_engine import RiskEngine

def test_risk_engine_normal_clean_scene():
    assessments = RiskEngine.evaluate_risk(
        zone_violations=[],
        ppe_results=[{"track_id": 1, "compliant": True, "missing_items": []}],
        fall_results=[{"track_id": 1, "is_hazard": False}],
        proximity_alerts=[],
        sensor_events=[],
        fire_smoke_events=[]
    )
    assert len(assessments) == 0

def test_risk_engine_fall_critical_escalation():
    assessments = RiskEngine.evaluate_risk(
        zone_violations=[],
        ppe_results=[],
        fall_results=[{
            "track_id": 5,
            "is_hazard": True,
            "spine_angle": 12.5,
            "immobility_seconds": 4.2
        }],
        proximity_alerts=[],
        sensor_events=[],
        fire_smoke_events=[]
    )
    assert len(assessments) == 1
    assert assessments[0].risk_level == 4 # CRITICAL
    assert assessments[0].event_type == "WORKER_FALL"
    assert "Worker #5 recumbent pose detected" in assessments[0].reasoning

def test_risk_engine_exclusion_zone_escalation():
    assessments = RiskEngine.evaluate_risk(
        zone_violations=[{
            "zone_id": 2,
            "zone_name": "High Voltage Room",
            "zone_type": "EXCLUSION_ZONE",
            "severity": 4,
            "dwell_time": 6.5,
            "track_id": 3
        }],
        ppe_results=[],
        fall_results=[],
        proximity_alerts=[],
        sensor_events=[],
        fire_smoke_events=[]
    )
    assert len(assessments) == 1
    assert assessments[0].risk_level == 4
    assert assessments[0].event_type == "ZONE_INTRUSION"
    assert "High Voltage Room" in assessments[0].reasoning
