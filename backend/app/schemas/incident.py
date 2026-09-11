from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any, Dict
from datetime import datetime

class IncidentBase(BaseModel):
    camera_id: int
    zone_id: Optional[int] = None
    event_type: str
    risk_level: int # 0 to 4
    confidence: float
    duration_seconds: float
    explainability: Dict[str, Any]
    recommended_action: Optional[str] = None
    evidence_snapshot_path: Optional[str] = None

class IncidentCreate(IncidentBase):
    pass

class IncidentReviewAction(BaseModel):
    action: str # ACKNOWLEDGE, CONFIRM, OVERRIDE, RESOLVE
    notes: Optional[str] = None
    override_reason: Optional[str] = None

class AuditLogOut(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    previous_status: str
    new_status: str
    reason: Optional[str]
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

class IncidentOut(IncidentBase):
    id: int
    status: str
    assigned_to_user_id: Optional[int] = None
    operator_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    audit_logs: Optional[List[AuditLogOut]] = []
    model_config = ConfigDict(from_attributes=True)
