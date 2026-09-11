import pytest
from app.services.proximity_engine import ProximityEngine

def test_proximity_engine_safe_clearance():
    engine = ProximityEngine(pixels_per_meter=50.0, warning_distance_m=3.0, critical_distance_m=1.5)
    
    # Worker at (100, 100), Vehicle at (600, 600) -> Distance ~ 707 px / 50 = ~14.1m
    workers = [{"track_id": 1, "bbox": [90, 80, 110, 120]}]
    vehicles = [{"track_id": 2, "bbox": [550, 550, 650, 650]}]

    alerts = engine.evaluate_proximity(workers, vehicles, current_time=0.0)
    assert len(alerts) == 0

def test_proximity_engine_warning_distance():
    engine = ProximityEngine(pixels_per_meter=50.0, warning_distance_m=3.0, critical_distance_m=1.5)
    
    # Distance ~ 100 px / 50 = 2.0m (between warning 3.0m and critical 1.5m)
    workers = [{"track_id": 1, "bbox": [100, 100, 120, 140]}]
    vehicles = [{"track_id": 2, "bbox": [200, 100, 240, 140]}]

    alerts = engine.evaluate_proximity(workers, vehicles, current_time=0.0)
    assert len(alerts) == 1
    assert alerts[0].severity == 3 # HIGH RISK WARNING
    assert alerts[0].distance_meters <= 3.0

def test_proximity_engine_critical_collision_envelope():
    engine = ProximityEngine(pixels_per_meter=50.0, warning_distance_m=3.0, critical_distance_m=1.5)
    
    # Distance ~ 50 px / 50 = 1.0m (below critical 1.5m)
    workers = [{"track_id": 1, "bbox": [100, 100, 120, 140]}]
    vehicles = [{"track_id": 2, "bbox": [150, 100, 190, 140]}]

    alerts = engine.evaluate_proximity(workers, vehicles, current_time=0.0)
    assert len(alerts) == 1
    assert alerts[0].severity == 4 # CRITICAL COLLISION
