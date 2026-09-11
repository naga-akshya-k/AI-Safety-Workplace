from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class CameraBase(BaseModel):
    name: str
    location: str
    stream_source: str
    fps: Optional[float] = 30.0
    width: Optional[int] = 1280
    height: Optional[int] = 720
    is_active: Optional[bool] = True

class CameraCreate(CameraBase):
    pass

class CameraUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    stream_source: Optional[str] = None
    is_active: Optional[bool] = None

class CameraOut(CameraBase):
    id: int
    status: str
    current_fps: float
    last_frame_time: Optional[datetime] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
