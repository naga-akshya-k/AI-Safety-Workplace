import pytest
import time
from app.services.zone_engine import ZoneEngine

def test_ground_contact_point():
    # Box: [x1, y1, x2, y2]
    bbox = [100.0, 50.0, 200.0, 250.0]
    # Without keypoints, bottom center is ((100+200)/2, 250) = (150, 250)
    pt = ZoneEngine.get_ground_contact_point(bbox)
    assert pt == (150.0, 250.0)

    # With ankle keypoints (indices 15 & 16)
    kps = [[0.0, 0.0, 0.0]] * 17
    kps[15] = [140.0, 248.0, 0.9] # left ankle
    kps[16] = [160.0, 250.0, 0.9] # right ankle
    pt_kps = ZoneEngine.get_ground_contact_point(bbox, kps)
    assert pt_kps == (150.0, 249.0)

def test_zone_violation_and_dwell_persistence():
    engine = ZoneEngine()
    zones = [{
        "id": 1,
        "name": "Robotic Danger Area",
        "zone_type": "EXCLUSION_ZONE",
        "polygon_coords": [[100, 100], [300, 100], [300, 300], [100, 300]],
        "severity_level": 4,
        "dwell_threshold_seconds": 2.0
    }]
    engine.update_zones(zones)

    # Point outside zone: (50, 50)
    v_outside = engine.evaluate_track(track_id=10, ground_pt=(50.0, 50.0), current_time=100.0)
    assert len(v_outside) == 0

    # Point inside zone at t=100.0 (dwell = 0s < threshold 2.0s)
    v_inside_t0 = engine.evaluate_track(track_id=10, ground_pt=(200.0, 200.0), current_time=100.0)
    assert len(v_inside_t0) == 0 # Not yet reached dwell threshold

    # Point inside zone at t=101.5 (dwell = 1.5s < threshold 2.0s)
    v_inside_t1 = engine.evaluate_track(track_id=10, ground_pt=(200.0, 200.0), current_time=101.5)
    assert len(v_inside_t1) == 0

    # Point inside zone at t=102.5 (dwell = 2.5s >= threshold 2.0s) -> VIOLATION
    v_inside_t2 = engine.evaluate_track(track_id=10, ground_pt=(200.0, 200.0), current_time=102.5)
    assert len(v_inside_t2) == 1
    assert v_inside_t2[0].zone_name == "Robotic Danger Area"
    assert v_inside_t2[0].severity == 4
    assert v_inside_t2[0].dwell_time >= 2.0

    # Point exits zone at t=103.0
    v_exit = engine.evaluate_track(track_id=10, ground_pt=(400.0, 400.0), current_time=103.0)
    assert len(v_exit) == 0
