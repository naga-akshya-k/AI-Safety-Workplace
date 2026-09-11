import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

from app.core.config import settings
from app.core.database import engine, Base, AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.camera import Camera
from app.models.zone import Zone
from app.api import auth, cameras, zones, incidents, telemetry, analytics, ws
from app.api.ws import init_pipeline_models

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed default admin user & demo cameras/zones if not present
    async with AsyncSessionLocal() as db:
        user_res = await db.execute(select(User).filter(User.email == "admin@safety.industrial"))
        if not user_res.scalars().first():
            admin_user = User(
                email="admin@safety.industrial",
                hashed_password=get_password_hash("admin123"),
                full_name="Chief Safety Officer",
                role="ADMIN"
            )
            operator_user = User(
                email="operator@safety.industrial",
                hashed_password=get_password_hash("operator123"),
                full_name="Control Room Operator",
                role="OPERATOR"
            )
            db.add_all([admin_user, operator_user])
            await db.commit()

        # Seed 4 Industrial Demonstration Cameras if not present
        cam_res = await db.execute(select(Camera))
        if not cam_res.scalars().first():
            base_dir = settings.BASE_DIR
            c1 = Camera(
                id=1,
                name="Loading Dock & Forklift Corridor",
                location="Warehouse Bay 4",
                stream_source=os.path.join(base_dir, "data", "sample_videos", "warehouse_forklift_corridor.mp4"),
                fps=20.0,
                width=1280,
                height=720,
                status="HEALTHY"
            )
            c2 = Camera(
                id=2,
                name="Shop Floor Assembly & Walkway",
                location="Plant Building 2",
                stream_source=os.path.join(base_dir, "data", "sample_videos", "shopfloor_ppe_compliance.mp4"),
                fps=20.0,
                width=1280,
                height=720,
                status="HEALTHY"
            )
            c3 = Camera(
                id=3,
                name="Robotic Fabrication Cell 03",
                location="Welding & Machining Hall",
                stream_source=os.path.join(base_dir, "data", "sample_videos", "robotic_cell_intrusion.mp4"),
                fps=20.0,
                width=1280,
                height=720,
                status="HEALTHY"
            )
            c4 = Camera(
                id=4,
                name="High-Rack Storage Aisle 03",
                location="Logistics Hub Section C",
                stream_source=os.path.join(base_dir, "data", "sample_videos", "worker_fall_mandown.mp4"),
                fps=20.0,
                width=1280,
                height=720,
                status="HEALTHY"
            )
            db.add_all([c1, c2, c3, c4])
            await db.commit()

            z1 = Zone(
                camera_id=1,
                name="Forklift High-Speed Transit Lane",
                zone_type="MACHINERY_COLLISION",
                polygon_coords="[[190, 60], [1070, 60], [1070, 670], [190, 670]]",
                required_ppe='["hardhat", "vest"]',
                severity_level=4,
                dwell_threshold_seconds=2
            )
            z2 = Zone(
                camera_id=2,
                name="Mandatory PPE Assembly Corridor",
                zone_type="PPE_MANDATORY",
                polygon_coords="[[380, 70], [870, 70], [870, 660], [380, 660]]",
                required_ppe='["hardhat", "vest"]',
                severity_level=3,
                dwell_threshold_seconds=2
            )
            z3 = Zone(
                camera_id=3,
                name="Robotic Arm Exclusion Perimeter",
                zone_type="EXCLUSION_ZONE",
                polygon_coords="[[390, 240], [890, 240], [890, 630], [390, 630]]",
                required_ppe='["hardhat", "vest"]',
                severity_level=4,
                dwell_threshold_seconds=3
            )
            z4 = Zone(
                camera_id=4,
                name="High-Rack Transit Zone",
                zone_type="HAZARD_ZONE",
                polygon_coords="[[340, 90], [940, 90], [940, 690], [340, 690]]",
                required_ppe='["hardhat", "vest"]',
                severity_level=4,
                dwell_threshold_seconds=2
            )
            db.add_all([z1, z2, z3, z4])
            await db.commit()

    # Warmup AI models asynchronously
    asyncio.create_task(asyncio.to_thread(init_pipeline_models))

    yield

    # Shutdown
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for local dev flexibility
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount evidence static files
os.makedirs(settings.EVIDENCE_DIR, exist_ok=True)
app.mount("/data/evidence", StaticFiles(directory=settings.EVIDENCE_DIR), name="evidence")

# Include Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(cameras.router, prefix=settings.API_V1_STR)
app.include_router(zones.router, prefix=settings.API_V1_STR)
app.include_router(incidents.router, prefix=settings.API_V1_STR)
app.include_router(telemetry.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)
app.include_router(ws.router)

@app.get("/health")
def health_check():
    return {
        "status": "HEALTHY",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }
