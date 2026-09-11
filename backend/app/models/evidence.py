from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    frame_path = Column(String(500), nullable=False)
    detections_metadata = Column(Text, nullable=False)  # JSON string of bounding boxes, tracks, keypoints
    telemetry_metadata = Column(Text, nullable=True)   # JSON string of sensor readings at frame time
    created_at = Column(DateTime, default=datetime.utcnow)

    incident = relationship("Incident", back_populates="evidence_items")
