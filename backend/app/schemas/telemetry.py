from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class SensorReading(BaseModel):
    sensor_id: str
    sensor_type: str # TEMPERATURE, TOXIC_GAS, COMBUSTIBLE_GAS, VIBRATION, ACOUSTIC, ESTOP
    zone_id: Optional[int] = None
    value: float
    unit: str
    status: str # NORMAL, WARNING, CRITICAL
    timestamp: datetime

class MultiModalFusionRequest(BaseModel):
    camera_id: int
    sensors: Dict[str, SensorReading]
