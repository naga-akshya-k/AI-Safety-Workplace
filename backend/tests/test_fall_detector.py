import pytest
import numpy as np
from app.services.fall_detector import FallDetector, FallDetectionState

def test_spine_angle_upright():
    # Construct 17 keypoints for standing worker
    # 5: l_sh, 6: r_sh, 11: l_hip, 12: r_hip
    kps = np.zeros((17, 3), dtype=np.float32)
    # Shoulders at y=100
    kps[5] = [90, 100, 0.9]
    kps[6] = [110, 100, 0.9]
    # Hips at y=180
    kps[11] = [95, 180, 0.9]
    kps[12] = [105, 180, 0.9]

    angle = FallDetector.calculate_spine_angle(kps)
    assert angle > 70.0 # Vertical spine

def test_spine_angle_fallen():
    kps = np.zeros((17, 3), dtype=np.float32)
    # Worker lying down horizontally on ground (y ~ 400)
    # Shoulders at x=200, y=400
    kps[5] = [200, 390, 0.9]
    kps[6] = [200, 410, 0.9]
    # Hips at x=280, y=400
    kps[11] = [280, 395, 0.9]
    kps[12] = [280, 405, 0.9]

    angle = FallDetector.calculate_spine_angle(kps)
    assert angle < 25.0 # Horizontal spine

def test_fall_state_machine_immobility_alarm():
    detector = FallDetector(immobility_threshold_seconds=2.0)
    
    # Recumbent pose keypoints
    kps = np.zeros((17, 3), dtype=np.float32)
    kps[5] = [200, 400, 0.9]
    kps[6] = [200, 400, 0.9]
    kps[11] = [280, 400, 0.9]
    kps[12] = [280, 400, 0.9]
    bbox = [180.0, 380.0, 320.0, 420.0]

    # Frame 1 at t=0.0: Transitions to RECUMBENT, but not yet critical
    res1 = detector.evaluate_track(track_id=1, bbox=bbox, keypoints=kps.tolist(), current_time=0.0)
    assert res1["state"] == FallDetectionState.RECUMBENT
    assert res1["is_hazard"] is False

    # Frame 2 at t=1.0: Still recumbent, under 2.0s threshold
    res2 = detector.evaluate_track(track_id=1, bbox=bbox, keypoints=kps.tolist(), current_time=1.0)
    assert res2["state"] == FallDetectionState.RECUMBENT
    assert res2["is_hazard"] is False

    # Frame 3 at t=2.5: Immobility exceeds 2.0s -> Escalates to CRITICAL_MAN_DOWN!
    res3 = detector.evaluate_track(track_id=1, bbox=bbox, keypoints=kps.tolist(), current_time=2.5)
    assert res3["state"] == FallDetectionState.CRITICAL_MAN_DOWN
    assert res3["is_hazard"] is True
    assert res3["immobility_seconds"] >= 2.0
