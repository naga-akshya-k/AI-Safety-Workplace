import time
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.detector import VisionDetector
from app.services.tracker import MultiObjectTracker
from app.services.zone_engine import ZoneEngine
from app.services.ppe_evaluator import PPEEvaluator
from app.services.fall_detector import FallDetector
from app.services.proximity_engine import ProximityEngine
from app.services.fire_smoke_detector import FireSmokeDetector
from app.services.sensor_fusion import SensorFusionEngine
from app.services.risk_engine import RiskEngine, RiskAssessment
from app.services.incident_manager import IncidentManager

class SafetyPerceptionPipeline:
    """
    Master Safety Pipeline Orchestrator.
    Executes multi-stage verification on every video frame.
    Enforces the industrial safety principle:
    Reliable evidence -> AI perception -> Temporal tracking ->
    Spatial/Kinematic validation -> Multi-stage Risk Engine -> HITL Incident Dispatch.
    """
    def __init__(self, detector: Optional[VisionDetector] = None):
        self.detector = detector
        self.tracker = MultiObjectTracker()
        self.zone_engine = ZoneEngine()
        self.fall_detector = FallDetector()
        self.proximity_engine = ProximityEngine()
        self.fire_smoke_detector = FireSmokeDetector()
        self.sensor_fusion = SensorFusionEngine()
        self.risk_engine = RiskEngine()
        self.incident_manager = IncidentManager()

    def set_detector(self, detector: VisionDetector):
        self.detector = detector

    def update_zones(self, zones_data: List[Dict[str, Any]]):
        self.zone_engine.update_zones(zones_data)

    async def process_frame(
        self,
        frame: np.ndarray,
        camera_id: int,
        db: Optional[AsyncSession] = None,
        telemetry_readings: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        start_time = time.time()
        
        # 1. Perception (AI Detection & Pose)
        if self.detector is not None:
            raw_detections = self.detector.detect_all(frame)
        else:
            raw_detections = {"workers": [], "vehicles": [], "ppe_items": []}

        # 2. Multi-Object Tracking (maintain consistent IDs)
        tracked_workers = self.tracker.update(raw_detections["workers"])
        vehicles = raw_detections.get("vehicles", [])
        ppe_items = raw_detections.get("ppe_items", [])

        # 3. Spatial Geofencing & Zone Evaluation (Ground Contact Points)
        active_zone_violations = []
        for worker in tracked_workers:
            t_id = worker.get("track_id", 0)
            ground_pt = self.zone_engine.get_ground_contact_point(worker["bbox"], worker.get("keypoints"))
            worker["ground_pt"] = ground_pt
            violations = self.zone_engine.evaluate_track(t_id, ground_pt, start_time)
            for v in violations:
                active_zone_violations.append(v.to_dict())

        # 4. Hierarchical Spatial PPE Compliance
        ppe_evaluations = []
        for worker in tracked_workers:
            t_id = worker.get("track_id", 0)
            # Default required PPE in industrial areas: hardhat and vest
            res = PPEEvaluator.evaluate_worker_ppe(
                track_id=t_id,
                worker_bbox=worker["bbox"],
                detected_ppe_items=ppe_items,
                required_ppe=["hardhat", "vest"]
            )
            ppe_evaluations.append(res.to_dict())

        # 5. Pose Kinematics & Fall Detection
        fall_evaluations = []
        for worker in tracked_workers:
            t_id = worker.get("track_id", 0)
            f_res = self.fall_detector.evaluate_track(
                track_id=t_id,
                bbox=worker["bbox"],
                keypoints=worker.get("keypoints"),
                current_time=start_time
            )
            fall_evaluations.append(f_res)

        # 6. Machinery / Forklift Collision Proximity
        proximity_alerts = self.proximity_engine.evaluate_proximity(
            workers=tracked_workers,
            vehicles=vehicles,
            current_time=start_time
        )
        proximity_alert_dicts = [p.to_dict() for p in proximity_alerts]

        # 7. Fire & Smoke Detection
        fire_smoke_alerts = self.fire_smoke_detector.evaluate_frame(frame)

        # 8. Sensor Fusion & Telemetry Correlation
        if telemetry_readings:
            for s_id, val in telemetry_readings.items():
                s_type = "TEMPERATURE" if "temp" in s_id.lower() else "TOXIC_GAS" if "gas" in s_id.lower() else "VIBRATION"
                self.sensor_fusion.update_sensor_reading(s_id, s_type, val)
        
        sensor_anomalies = self.sensor_fusion.evaluate_telemetry()
        correlated_events = self.sensor_fusion.cross_correlate_hazards(
            vision_hazards=fire_smoke_alerts,
            sensor_anomalies=sensor_anomalies
        )

        # 9. Explainable Multi-Stage Risk Classification
        risk_assessments: List[RiskAssessment] = self.risk_engine.evaluate_risk(
            zone_violations=active_zone_violations,
            ppe_results=ppe_evaluations,
            fall_results=fall_evaluations,
            proximity_alerts=proximity_alert_dicts,
            sensor_events=correlated_events,
            fire_smoke_events=fire_smoke_alerts
        )

        # 10. Incident Management & HITL Dispatch (Levels 2, 3, 4)
        new_incidents = []
        if db is not None:
            for assessment in risk_assessments:
                if assessment.risk_level >= 2: # Alert worthy
                    entity_id = assessment.details.get("track_id") or assessment.details.get("worker_id") or 0
                    inc = await self.incident_manager.register_incident(
                        db=db,
                        camera_id=camera_id,
                        zone_id=assessment.details.get("zone_id"),
                        event_type=assessment.event_type,
                        entity_id=entity_id,
                        risk_level=assessment.risk_level,
                        confidence=assessment.confidence,
                        duration=1.0,
                        explainability=assessment.to_dict(),
                        recommended_action=assessment.recommended_action,
                        frame=frame,
                        detections_metadata={
                            "workers": tracked_workers,
                            "vehicles": vehicles,
                            "ppe": ppe_items
                        }
                    )
                    if inc:
                        new_incidents.append(inc.id)

        inference_time_ms = round((time.time() - start_time) * 1000, 1)

        # Highest risk level currently in frame
        max_risk_level = max([a.risk_level for a in risk_assessments], default=0)

        return {
            "camera_id": camera_id,
            "timestamp": start_time,
            "max_risk_level": max_risk_level,
            "risk_assessments": [a.to_dict() for a in risk_assessments],
            "tracked_workers": tracked_workers,
            "vehicles": vehicles,
            "ppe_items": ppe_items,
            "zone_violations": active_zone_violations,
            "fall_evaluations": fall_evaluations,
            "proximity_alerts": proximity_alert_dicts,
            "fire_smoke_alerts": fire_smoke_alerts,
            "sensor_anomalies": [s.to_dict() for s in sensor_anomalies],
            "inference_time_ms": inference_time_ms,
            "new_incident_ids": new_incidents
        }
