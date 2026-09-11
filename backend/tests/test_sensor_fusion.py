import pytest
from app.services.sensor_fusion import SensorFusionEngine

def test_sensor_fusion_normal_telemetry():
    fusion = SensorFusionEngine()
    fusion.update_sensor_reading("temp_1", "TEMPERATURE", 32.5)
    fusion.update_sensor_reading("gas_1", "TOXIC_GAS", 2.0)
    
    anomalies = fusion.evaluate_telemetry()
    assert len(anomalies) == 0

def test_sensor_fusion_toxic_gas_critical_spike():
    fusion = SensorFusionEngine()
    # Critical threshold for toxic gas is 25.0 ppm
    fusion.update_sensor_reading("gas_1", "TOXIC_GAS", 28.5)
    
    anomalies = fusion.evaluate_telemetry()
    assert len(anomalies) == 1
    assert anomalies[0].severity == 4
    assert anomalies[0].sensor_type == "TOXIC_GAS"

def test_sensor_fusion_cross_correlation_thermal_fire():
    fusion = SensorFusionEngine()
    fusion.update_sensor_reading("temp_1", "TEMPERATURE", 75.0)
    anomalies = fusion.evaluate_telemetry()

    vision_hazards = [{"event_type": "FIRE_SMOKE", "confidence": 0.9}]
    correlated = fusion.cross_correlate_hazards(vision_hazards, anomalies)
    
    assert len(correlated) == 1
    assert correlated[0]["type"] == "CONFIRMED_THERMAL_FIRE_EMERGENCY"
    assert correlated[0]["severity"] == 4
    assert correlated[0]["confidence"] > 0.95
