from fastapi import APIRouter, Depends
from typing import Dict, Any, List
from app.schemas.telemetry import MultiModalFusionRequest, SensorReading
from app.services.ai_pipeline import SafetyPerceptionPipeline

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])

# In-memory latest telemetry cache
latest_sensor_data: Dict[str, Any] = {}

@router.post("/ingest")
async def ingest_sensor_telemetry(payload: MultiModalFusionRequest):
    """
    Ingests live industrial sensor signals (e.g. gas detectors, heat sensors, machine vibration).
    """
    for s_id, s_reading in payload.sensors.items():
        latest_sensor_data[s_id] = s_reading.dict()
    return {"status": "success", "sensors_updated": len(payload.sensors)}

@router.get("/live")
async def get_live_telemetry():
    return latest_sensor_data
