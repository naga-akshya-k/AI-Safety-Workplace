import asyncio
import os
from sqlalchemy import select, delete
from app.core.database import engine, Base, AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.camera import Camera
from app.models.zone import Zone
from app.models.incident import Incident
from app.models.evidence import Evidence
from app.models.audit_log import AuditLog

async def seed():
    print("=" * 60)
    print("SEEDING INDUSTRIAL MULTI-CAMERA WORKPLACE SCENARIOS")
    print("=" * 60)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Clear existing cameras & zones to ensure fresh demo config
        await db.execute(delete(Zone))
        await db.execute(delete(Camera))
        await db.commit()

        # Seed Users
        admin_res = await db.execute(select(User).filter(User.email == "admin@safety.industrial"))
        if not admin_res.scalars().first():
            admin_user = User(
                email="admin@safety.industrial",
                hashed_password=get_password_hash("admin123"),
                full_name="Chief Safety Officer",
                role="ADMIN"
            )
            op_user = User(
                email="operator@safety.industrial",
                hashed_password=get_password_hash("operator123"),
                full_name="Control Room Operator",
                role="OPERATOR"
            )
            db.add_all([admin_user, op_user])
            await db.commit()
            print("[PASS] Seeded Admin and Operator user accounts.")

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # CAMERA 1: Warehouse Forklift Corridor
        cam1_path = os.path.join(base_dir, "data", "sample_videos", "warehouse_forklift_corridor.mp4")
        cam1 = Camera(
            id=1,
            name="Loading Dock & Forklift Corridor",
            location="Warehouse Bay 4",
            stream_source=cam1_path,
            fps=20.0,
            width=1280,
            height=720,
            status="HEALTHY"
        )
        db.add(cam1)
        await db.commit()

        zone1 = Zone(
            camera_id=1,
            name="Forklift High-Speed Transit Lane",
            zone_type="MACHINERY_COLLISION",
            polygon_coords="[[190, 60], [1070, 60], [1070, 670], [190, 670]]",
            required_ppe='["hardhat", "vest"]',
            severity_level=4,
            dwell_threshold_seconds=2
        )
        db.add(zone1)

        # CAMERA 2: Shop Floor PPE Enforcement Walkway
        cam2_path = os.path.join(base_dir, "data", "sample_videos", "shopfloor_ppe_compliance.mp4")
        cam2 = Camera(
            id=2,
            name="Shop Floor Assembly & Main Walkway",
            location="Plant Building 2",
            stream_source=cam2_path,
            fps=20.0,
            width=1280,
            height=720,
            status="HEALTHY"
        )
        db.add(cam2)
        await db.commit()

        zone2 = Zone(
            camera_id=2,
            name="Mandatory PPE Assembly Corridor",
            zone_type="PPE_MANDATORY",
            polygon_coords="[[380, 70], [870, 70], [870, 660], [380, 660]]",
            required_ppe='["hardhat", "vest"]',
            severity_level=3,
            dwell_threshold_seconds=2
        )
        db.add(zone2)

        # CAMERA 3: Robotic Arm Cell Perimeter
        cam3_path = os.path.join(base_dir, "data", "sample_videos", "robotic_cell_intrusion.mp4")
        cam3 = Camera(
            id=3,
            name="Robotic Fabrication Cell 03",
            location="Welding & Machining Hall",
            stream_source=cam3_path,
            fps=20.0,
            width=1280,
            height=720,
            status="HEALTHY"
        )
        db.add(cam3)
        await db.commit()

        zone3 = Zone(
            camera_id=3,
            name="Robotic Arm Exclusion Perimeter",
            zone_type="EXCLUSION_ZONE",
            polygon_coords="[[390, 240], [890, 240], [890, 630], [390, 630]]",
            required_ppe='["hardhat", "vest"]',
            severity_level=4,
            dwell_threshold_seconds=3
        )
        db.add(zone3)

        # CAMERA 4: Storage Aisle 3 - Man-Down Area
        cam4_path = os.path.join(base_dir, "data", "sample_videos", "worker_fall_mandown.mp4")
        cam4 = Camera(
            id=4,
            name="High-Rack Storage Aisle 03",
            location="Logistics Hub Section C",
            stream_source=cam4_path,
            fps=20.0,
            width=1280,
            height=720,
            status="HEALTHY"
        )
        db.add(cam4)
        await db.commit()

        zone4 = Zone(
            camera_id=4,
            name="High-Rack Transit Zone",
            zone_type="HAZARD_ZONE",
            polygon_coords="[[340, 90], [940, 90], [940, 690], [340, 690]]",
            required_ppe='["hardhat", "vest"]',
            severity_level=4,
            dwell_threshold_seconds=2
        )
        db.add(zone4)

        await db.commit()
        print("[PASS] Seeded all 4 Cameras with active geofences and industrial safety rules.")

if __name__ == "__main__":
    asyncio.run(seed())
