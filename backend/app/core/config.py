from pydantic import BaseModel
from typing import List
import os

class Settings(BaseModel):
    PROJECT_NAME: str = "Enterprise AI Safety & Workplace Intelligence System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security & Auth
    SECRET_KEY: str = "industrial-safety-super-secret-key-production-change-384729103"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 12 # 12 hours for 24/7 industrial shift
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./ai_safety.db"
    
    # Storage Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    EVIDENCE_DIR: str = os.path.join(DATA_DIR, "evidence")
    MODEL_WEIGHTS_DIR: str = os.path.join(BASE_DIR, "models_cache")
    
    # Vision & Safety Thresholds
    PERSON_DETECTION_CONF: float = 0.35  # Biased toward high recall to avoid missed workers
    PPE_DETECTION_CONF: float = 0.40
    POSE_ESTIMATION_CONF: float = 0.30
    FIRE_SMOKE_CONF: float = 0.45
    
    # Multi-Object Tracking
    TRACK_BUFFER_FRAMES: int = 30
    TRACK_MATCH_THRESH: float = 0.8
    
    # Safety Kinematics & Zone Dwell Timers (in seconds)
    ZONE_DWELL_WARNING_SECONDS: float = 2.0
    ZONE_DWELL_CRITICAL_SECONDS: float = 4.0
    FALL_IMMOBILITY_CRITICAL_SECONDS: float = 3.5
    PROXIMITY_COLLISION_TTC_SECONDS: float = 2.5
    PROXIMITY_COLLISION_METERS: float = 2.2
    
    # Fail-Safe Degradation
    MIN_HEALTHY_FPS: float = 8.0
    CAMERA_TIMEOUT_SECONDS: float = 5.0
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "*"
    ]

settings = Settings()
os.makedirs(settings.EVIDENCE_DIR, exist_ok=True)
os.makedirs(settings.MODEL_WEIGHTS_DIR, exist_ok=True)
