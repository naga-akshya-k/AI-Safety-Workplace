from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class ZoneBase(BaseModel):
    name: str
    zone_type: str # EXCLUSION_ZONE, PPE_MANDATORY, HAZARD_ZONE, MACHINERY_COLLISION
    polygon_coords: List[List[float]] # [[x1, y1], [x2, y2], ...]
    required_ppe: Optional[List[str]] = []
    severity_level: Optional[int] = 3
    dwell_threshold_seconds: Optional[int] = 3
    is_active: Optional[bool] = True

class ZoneCreate(ZoneBase):
    camera_id: int

class ZoneUpdate(BaseModel):
    name: Optional[str] = None
    zone_type: Optional[str] = None
    polygon_coords: Optional[List[List[float]]] = None
    required_ppe: Optional[List[str]] = None
    severity_level: Optional[int] = None
    dwell_threshold_seconds: Optional[int] = None
    is_active: Optional[bool] = None

class ZoneOut(ZoneBase):
    id: int
    camera_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
