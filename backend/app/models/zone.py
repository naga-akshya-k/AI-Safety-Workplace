from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Zone(Base):
    __tablename__ = "zones"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    name = Column(String(100), nullable=False)
    zone_type = Column(String(50), nullable=False)  # EXCLUSION_ZONE, PPE_MANDATORY, HAZARD_ZONE, MACHINERY_COLLISION
    polygon_coords = Column(Text, nullable=False)   # JSON string of [[x1, y1], [x2, y2], ...] normalized 0..1
    required_ppe = Column(Text, default="[]")       # JSON array of ["hardhat", "vest"]
    severity_level = Column(Integer, default=3)     # 1 (Low) to 4 (Critical)
    dwell_threshold_seconds = Column(Integer, default=3) # time before alarm escalates
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    camera = relationship("Camera", back_populates="zones")
    incidents = relationship("Incident", back_populates="zone")
