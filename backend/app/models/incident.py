from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=True)
    
    event_type = Column(String(100), nullable=False) # ZONE_INTRUSION, PPE_VIOLATION, WORKER_FALL, VEHICLE_PROXIMITY, FIRE_SMOKE, SENSOR_HAZARD
    risk_level = Column(Integer, nullable=False)     # 0: NORMAL, 1: LOW, 2: MEDIUM, 3: HIGH, 4: CRITICAL
    status = Column(String(50), default="PENDING_REVIEW") # PENDING_REVIEW, ACKNOWLEDGED, CONFIRMED_HAZARD, FALSE_POSITIVE_OVERRIDE, RESOLVED
    
    confidence = Column(Float, nullable=False)
    duration_seconds = Column(Float, default=0.0)
    explainability = Column(Text, nullable=False)     # JSON structured reasoning
    recommended_action = Column(String(500), nullable=True)
    
    evidence_snapshot_path = Column(String(500), nullable=True)
    assigned_to_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    operator_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    camera = relationship("Camera", back_populates="incidents")
    zone = relationship("Zone", back_populates="incidents")
    evidence_items = relationship("Evidence", back_populates="incident", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="incident", cascade="all, delete-orphan")
