import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import engine, Base, AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.camera import Camera
from app.models.zone import Zone
from sqlalchemy import select

@pytest.fixture(autouse=True)
async def setup_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        user_res = await db.execute(select(User).filter(User.email == "admin@safety.industrial"))
        if not user_res.scalars().first():
            admin_user = User(
                email="admin@safety.industrial",
                hashed_password=get_password_hash("admin123"),
                full_name="Chief Safety Officer",
                role="ADMIN"
            )
            db.add(admin_user)
            await db.commit()

        cam_res = await db.execute(select(Camera).filter(Camera.id == 1))
        if not cam_res.scalars().first():
            cam1 = Camera(
                id=1,
                name="Shop Floor Assembly & Robot Cell 01",
                location="Building 3 - Bay B",
                stream_source="0",
                fps=30.0,
                width=1280,
                height=720,
                status="HEALTHY"
            )
            db.add(cam1)
            await db.commit()

            zone1 = Zone(
                camera_id=1,
                name="Robotic Danger Perimeter",
                zone_type="EXCLUSION_ZONE",
                polygon_coords="[[380, 280], [900, 280], [900, 620], [380, 620]]",
                required_ppe='["hardhat", "vest"]',
                severity_level=4,
                dwell_threshold_seconds=3
            )
            db.add(zone1)
            await db.commit()

    yield

@pytest.mark.anyio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "HEALTHY"
        assert "Enterprise AI Safety" in data["service"]

@pytest.mark.anyio
async def test_auth_and_camera_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Login with seeded admin
        login_res = await client.post(
            "/api/v1/auth/login",
            data={"username": "admin@safety.industrial", "password": "admin123"}
        )
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Check /auth/me
        me_res = await client.get("/api/v1/auth/me", headers=headers)
        assert me_res.status_code == 200
        assert me_res.json()["email"] == "admin@safety.industrial"
        assert me_res.json()["role"] == "ADMIN"

        # 3. List Cameras (seed Camera 1 exists)
        cam_res = await client.get("/api/v1/cameras", headers=headers)
        assert cam_res.status_code == 200
        cams = cam_res.json()
        assert len(cams) >= 1
        assert cams[0]["id"] == 1

        # 4. List Zones for Camera 1
        zone_res = await client.get("/api/v1/zones/camera/1", headers=headers)
        assert zone_res.status_code == 200
        zones = zone_res.json()
        assert len(zones) >= 1

        # 5. Summary Analytics
        analytics_res = await client.get("/api/v1/analytics/summary", headers=headers)
        assert analytics_res.status_code == 200
        summary = analytics_res.json()
        assert "compliance_rate_percent" in summary
        assert "severity_breakdown" in summary
