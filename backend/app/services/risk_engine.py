from typing import Dict, List, Any, Optional
import time

class RiskAssessment:
    LEVEL_NAMES = {
        0: "NORMAL",
        1: "LOW",
        2: "MEDIUM",
        3: "HIGH",
        4: "CRITICAL"
    }

    def __init__(
        self,
        risk_level: int,
        event_type: str,
        confidence: float,
        reasoning: str,
        recommended_action: str,
        details: Dict[str, Any]
    ):
        self.risk_level = min(4, max(0, risk_level))
        self.risk_name = self.LEVEL_NAMES[self.risk_level]
        self.event_type = event_type
        self.confidence = min(1.0, max(0.0, confidence))
        self.reasoning = reasoning
        self.recommended_action = recommended_action
        self.details = details

    def to_dict(self) -> Dict[str, Any]:
        return {
            "risk_level": self.risk_level,
            "risk_name": self.risk_name,
            "event_type": self.event_type,
            "confidence": round(self.confidence, 3),
            "reasoning": self.reasoning,
            "recommended_action": self.recommended_action,
            "details": self.details,
            "timestamp": time.time()
        }

class RiskEngine:
    @staticmethod
    def evaluate_risk(
        zone_violations: List[Dict[str, Any]],
        ppe_results: List[Dict[str, Any]],
        fall_results: List[Dict[str, Any]],
        proximity_alerts: List[Dict[str, Any]],
        sensor_events: List[Dict[str, Any]],
        fire_smoke_events: List[Dict[str, Any]]
    ) -> List[RiskAssessment]:
        """
        Deterministic, explainable multi-stage risk classification.
        Aggregates multiple domain assessments into prioritized operational actions.
        """
        assessments: List[RiskAssessment] = []

        # 1. Critical Worker Fall / Man-Down
        for f in fall_results:
            if f.get("is_hazard"):
                track_id = f.get("track_id")
                immobility = f.get("immobility_seconds", 0.0)
                assessments.append(RiskAssessment(
                    risk_level=4, # CRITICAL
                    event_type="WORKER_FALL",
                    confidence=0.92,
                    reasoning=f"Worker #{track_id} recumbent pose detected with sustained immobility for {immobility}s (spine angle {f.get('spine_angle')}°).",
                    recommended_action="Dispatch immediate medical and safety emergency response to location.",
                    details=f
                ))

        # 2. Worker-Machinery / Vehicle Proximity Breach
        for p in proximity_alerts:
            sev = p.get("severity", 3)
            w_id = p.get("worker_id")
            v_id = p.get("vehicle_id")
            dist = p.get("distance_meters")
            ttc = p.get("ttc_seconds")
            
            if sev >= 4:
                assessments.append(RiskAssessment(
                    risk_level=4,
                    event_type="VEHICLE_PROXIMITY",
                    confidence=0.94,
                    reasoning=f"Critical collision hazard: Vehicle #{v_id} approaching Worker #{w_id} at {dist}m (TTC: {ttc}s).",
                    recommended_action="Trigger automated vehicle slowdown/E-stop interlock and operator audible warning.",
                    details=p
                ))
            else:
                assessments.append(RiskAssessment(
                    risk_level=3,
                    event_type="VEHICLE_PROXIMITY",
                    confidence=0.88,
                    reasoning=f"Worker #{w_id} within caution envelope of moving machinery #{v_id} ({dist}m).",
                    recommended_action="Sound proximity advisory buzzer and notify vehicle operator.",
                    details=p
                ))

        # 3. Fire & Smoke
        for fs in fire_smoke_events:
            assessments.append(RiskAssessment(
                risk_level=4,
                event_type="FIRE_SMOKE",
                confidence=fs.get("confidence", 0.85),
                reasoning=f"Visual flame/smoke signature confirmed across consecutive frames in monitored area.",
                recommended_action="Initiate evacuation alarm and notify plant fire brigade.",
                details=fs
            ))

        # 4. Sensor Correlated Events
        for sc in sensor_events:
            assessments.append(RiskAssessment(
                risk_level=sc.get("severity", 4),
                event_type="SENSOR_HAZARD",
                confidence=sc.get("confidence", 0.95),
                reasoning=sc.get("reasoning", "Sensor anomaly detected."),
                recommended_action="Follow hazardous environment emergency protocol.",
                details=sc
            ))

        # 5. Zone Violations & PPE in Zones
        for zv in zone_violations:
            z_type = zv.get("zone_type")
            z_name = zv.get("zone_name")
            dwell = zv.get("dwell_time", 0.0)
            t_id = zv.get("track_id")

            # Match PPE status for this worker
            worker_ppe = next((p for p in ppe_results if p.get("track_id") == t_id), None)
            missing_ppe = worker_ppe.get("missing_items", []) if worker_ppe else []

            if z_type == "EXCLUSION_ZONE":
                assessments.append(RiskAssessment(
                    risk_level=3 if dwell < 5.0 else 4,
                    event_type="ZONE_INTRUSION",
                    confidence=0.96,
                    reasoning=f"Worker #{t_id} entered restricted exclusion zone '{z_name}' (dwell time: {dwell}s).",
                    recommended_action=f"Clear personnel from restricted zone '{z_name}' immediately.",
                    details=zv
                ))
            elif z_type == "PPE_MANDATORY" and missing_ppe:
                assessments.append(RiskAssessment(
                    risk_level=3 if "hardhat" in missing_ppe else 2,
                    event_type="PPE_VIOLATION",
                    confidence=0.89,
                    reasoning=f"Worker #{t_id} in '{z_name}' lacking mandatory safety gear: {', '.join(missing_ppe)} (dwell time: {dwell}s).",
                    recommended_action=f"Enforce mandatory PPE ({', '.join(missing_ppe)}) before continuing work in '{z_name}'.",
                    details={"zone": zv, "ppe": worker_ppe}
                ))
            else:
                assessments.append(RiskAssessment(
                    risk_level=zv.get("severity", 2),
                    event_type="ZONE_INTRUSION",
                    confidence=0.90,
                    reasoning=f"Worker #{t_id} in hazardous zone '{z_name}' for {dwell}s.",
                    recommended_action="Monitor worker dwell time and ensure safety compliance.",
                    details=zv
                ))

        # 6. Standalone PPE Non-Compliance (Outside specific zones)
        for ppe in ppe_results:
            t_id = ppe.get("track_id")
            # If already reported under a zone violation, don't duplicate
            if not ppe.get("compliant") and not any(a.event_type == "PPE_VIOLATION" and a.details.get("track_id") == t_id for a in assessments):
                missing = ppe.get("missing_items", [])
                assessments.append(RiskAssessment(
                    risk_level=2, # MEDIUM
                    event_type="PPE_VIOLATION",
                    confidence=0.85,
                    reasoning=f"Worker #{t_id} observed without required safety gear: {', '.join(missing)}.",
                    recommended_action=f"Remind worker to don {', '.join(missing)}.",
                    details=ppe
                ))

        return assessments
