from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    location = Column(String(200), nullable=False)
    stream_source = Column(String(500), nullable=False)  # file path, RTSP url, or simulated stream id
    fps = Column(Float, default=30.0)
    width = Column(Integer, default=1280)
    height = Column(Integer, default=720)
    is_active = Column(Boolean, default=True)
    status = Column(String(50), default="UNKNOWN")  # HEALTHY, DEGRADED, OFFLINE, UNKNOWN
    current_fps = Column(Float, default=0.0)
    last_frame_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    zones = relationship("Zone", back_populates="camera", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="camera")
