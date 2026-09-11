import os
import json
import time
import cv2
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.incident import Incident
from app.models.evidence import Evidence
from app.core.config import settings

class IncidentManager:
    def __init__(self, cooldown_seconds: float = 20.0):
        self.cooldown_seconds = cooldown_seconds
        # (camera_id, event_type, entity_id) -> (last_alert_time, last_severity, incident_id)
        self.active_incidents: Dict[Tuple[int, str, Any], Tuple[float, int, int]] = {}

    def should_create_incident(self, camera_id: int, event_type: str, entity_id: Any, current_severity: int, now: float) -> Tuple[bool, bool, Optional[int]]:
        """
        Returns:
        (should_create, is_escalation, existing_incident_id)
        """
        key = (camera_id, event_type, entity_id)
        if key not in self.active_incidents:
            return (True, False, None)

        last_time, last_sev, inc_id = self.active_incidents[key]
        
        # Immediate bypass if severity escalates (e.g. Level 2 -> Level 4)
        if current_severity > last_sev:
            return (True, True, inc_id)

        # Cooldown check
        if now - last_time >= self.cooldown_seconds:
            return (True, False, inc_id)

        return (False, False, inc_id)

    async def register_incident(
        self,
        db: AsyncSession,
        camera_id: int,
        zone_id: Optional[int],
        event_type: str,
        entity_id: Any,
        risk_level: int,
        confidence: float,
        duration: float,
        explainability: Dict[str, Any],
        recommended_action: str,
        frame: Optional[np.ndarray],
        detections_metadata: Dict[str, Any]
    ) -> Incident:
        now = time.time()
        should_create, is_escalation, existing_inc_id = self.should_create_incident(
            camera_id, event_type, entity_id, risk_level, now
        )

        if not should_create:
            # Still in cooldown; update duration of existing incident if available
            if existing_inc_id:
                result = await db.execute(select(Incident).filter(Incident.id == existing_inc_id))
                inc = result.scalars().first()
                if inc:
                    inc.duration_seconds += duration
                    await db.commit()
                    return inc
            return None

        # Save Evidence snapshot
        snapshot_filename = f"evidence_cam{camera_id}_{event_type}_{int(now)}.jpg"
        snapshot_path = os.path.join(settings.EVIDENCE_DIR, snapshot_filename)
        rel_snapshot_path = f"/data/evidence/{snapshot_filename}"

        if frame is not None:
            # Annotate frame with evidence watermark
            annotated_frame = frame.copy()
            h, w = annotated_frame.shape[:2]
            cv2.putText(
                annotated_frame,
                f"SAFETY ALERT: {event_type} (Risk Lvl {risk_level})",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255) if risk_level >= 3 else (0, 165, 255),
                2
            )
            cv2.imwrite(snapshot_path, annotated_frame)
        else:
            rel_snapshot_path = None

        new_incident = Incident(
            camera_id=camera_id,
            zone_id=zone_id,
            event_type=event_type,
            risk_level=risk_level,
            status="PENDING_REVIEW",
            confidence=confidence,
            duration_seconds=duration,
            explainability=json.dumps(explainability),
            recommended_action=recommended_action,
            evidence_snapshot_path=rel_snapshot_path
        )
        db.add(new_incident)
        await db.commit()
        await db.refresh(new_incident)

        # Store detailed evidence item
        evidence_item = Evidence(
            incident_id=new_incident.id,
            frame_path=rel_snapshot_path or "",
            detections_metadata=json.dumps(detections_metadata),
            telemetry_metadata=json.dumps(explainability.get("telemetry", {}))
        )
        db.add(evidence_item)
        await db.commit()

        # Update cooldown tracking
        key = (camera_id, event_type, entity_id)
        self.active_incidents[key] = (now, risk_level, new_incident.id)

        return new_incident
