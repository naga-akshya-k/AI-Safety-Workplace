from typing import Dict, List, Any, Optional
import time

class SensorAnomaly:
    def __init__(self, sensor_id: str, sensor_type: str, value: float, unit: str, severity: int, description: str):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.value = value
        self.unit = unit
        self.severity = severity
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sensor_id": self.sensor_id,
            "sensor_type": self.sensor_type,
            "value": round(self.value, 2),
            "unit": self.unit,
            "severity": self.severity,
            "description": self.description
        }

class SensorFusionEngine:
    THRESHOLDS = {
        "TOXIC_GAS": {"warning": 10.0, "critical": 25.0, "unit": "ppm"},
        "COMBUSTIBLE_GAS": {"warning": 10.0, "critical": 20.0, "unit": "% LEL"},
        "TEMPERATURE": {"warning": 48.0, "critical": 70.0, "unit": "°C"},
        "VIBRATION": {"warning": 4.5, "critical": 11.2, "unit": "mm/s RMS"}
    }

    def __init__(self):
        # sensor_id -> { "type": str, "value": float, "unit": str, "timestamp": float, "zone_id": Optional[int] }
        self.latest_readings: Dict[str, Dict[str, Any]] = {}

    def update_sensor_reading(self, sensor_id: str, sensor_type: str, value: float, zone_id: Optional[int] = None):
        self.latest_readings[sensor_id] = {
            "type": sensor_type,
            "value": value,
            "unit": self.THRESHOLDS.get(sensor_type, {}).get("unit", ""),
            "timestamp": time.time(),
            "zone_id": zone_id
        }

    def evaluate_telemetry(self) -> List[SensorAnomaly]:
        anomalies: List[SensorAnomaly] = []
        for s_id, s_data in self.latest_readings.items():
            stype = s_data["type"]
            val = s_data["value"]
            cfg = self.THRESHOLDS.get(stype)
            if not cfg:
                continue

            if val >= cfg["critical"]:
                anomalies.append(SensorAnomaly(
                    sensor_id=s_id,
                    sensor_type=stype,
                    value=val,
                    unit=cfg["unit"],
                    severity=4, # CRITICAL
                    description=f"Critical threshold breach: {stype} reached {val} {cfg['unit']}"
                ))
            elif val >= cfg["warning"]:
                anomalies.append(SensorAnomaly(
                    sensor_id=s_id,
                    sensor_type=stype,
                    value=val,
                    unit=cfg["unit"],
                    severity=2, # MEDIUM
                    description=f"Advisory threshold: {stype} at {val} {cfg['unit']}"
                ))
        return anomalies

    def cross_correlate_hazards(
        self,
        vision_hazards: List[Dict[str, Any]],
        sensor_anomalies: List[SensorAnomaly]
    ) -> List[Dict[str, Any]]:
        """
        Industrial Multi-Modal Fusion:
        Combines optical vision with physical telemetry.
        Never declares SAFE if a critical sensor alarms even when camera view is clear.
        """
        correlated_events = []

        # Check for smoke + elevated temp
        has_vision_smoke = any(h.get("event_type") == "FIRE_SMOKE" for h in vision_hazards)
        temp_readings = [s for s in sensor_anomalies if s.sensor_type == "TEMPERATURE"]

        if has_vision_smoke and temp_readings:
            highest_temp = max(t.value for t in temp_readings)
            correlated_events.append({
                "type": "CONFIRMED_THERMAL_FIRE_EMERGENCY",
                "severity": 4, # Level 4 CRITICAL
                "confidence": 0.98,
                "reasoning": f"Optical fire/smoke signature corroborated by temperature spike ({highest_temp} °C). Immediate suppression protocol required."
            })

        # Check for toxic gas in zone with present workers
        gas_anomalies = [s for s in sensor_anomalies if s.sensor_type in ["TOXIC_GAS", "COMBUSTIBLE_GAS"] and s.severity >= 3]
        if gas_anomalies:
            for g in gas_anomalies:
                correlated_events.append({
                    "type": "HAZARDOUS_ATMOSPHERE_BREACH",
                    "severity": 4,
                    "confidence": 0.95,
                    "reasoning": f"{g.description}. Hazardous atmosphere detected. Mandatory area evacuation."
                })

        return correlated_events
