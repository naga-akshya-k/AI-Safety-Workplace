import asyncio
import json
import websockets
import httpx

async def test_live_system():
    print("=" * 60)
    print("LIVE INTEGRATION VERIFICATION — AI SAFETY SYSTEM")
    print("=" * 60)

    base_http = "http://127.0.0.1:8080"
    base_ws = "ws://127.0.0.1:8080"

    async with httpx.AsyncClient(base_url=base_http) as client:
        # 1. Verify Health
        h_res = await client.get("/health")
        assert h_res.status_code == 200
        print("[PASS] 1. Backend Health Check: OK")

        # 2. Verify WebSocket Stream on Camera 1
        ws_url = f"{base_ws}/ws/stream/1"
        print(f"Connecting to WebSocket: {ws_url}...")
        async with websockets.connect(ws_url) as ws:
            # Receive 3 frames
            for i in range(3):
                msg = await ws.recv()
                data = json.loads(msg)
                assert data["camera_id"] == 1
                assert "status" in data
                assert "health" in data
                print(f"  -> Received Frame #{i+1}: Status={data['status']}, FPS={data['health'].get('fps')}, FrameSize={len(data.get('frame') or '')} chars")

            print("[PASS] 2. Real-Time WebSocket Streaming & Processing: OK")

        # 3. Simulate Sensor Ingestion
        sensor_payload = {
            "camera_id": 1,
            "sensors": {
                "temp_zone_01": {
                    "sensor_id": "temp_zone_01",
                    "sensor_type": "TEMPERATURE",
                    "value": 52.4,
                    "unit": "°C",
                    "status": "WARNING",
                    "timestamp": "2026-09-10T15:00:00Z"
                },
                "gas_h2s_01": {
                    "sensor_id": "gas_h2s_01",
                    "sensor_type": "TOXIC_GAS",
                    "value": 26.8, # Critical spike > 25 ppm
                    "unit": "ppm",
                    "status": "CRITICAL",
                    "timestamp": "2026-09-10T15:00:00Z"
                }
            }
        }
        tel_res = await client.post("/api/v1/telemetry/ingest", json=sensor_payload)
        assert tel_res.status_code == 200
        print("[PASS] 3. Multi-Modal Sensor Telemetry Ingestion: OK")

        # 4. Login as Safety Admin
        login_res = await client.post(
            "/api/v1/auth/login",
            data={"username": "admin@safety.industrial", "password": "admin123"}
        )
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("[PASS] 4. RBAC JWT Authentication: OK")

        # 5. Check Incidents Queue
        inc_res = await client.get("/api/v1/incidents", headers=headers)
        assert inc_res.status_code == 200
        incidents = inc_res.json()
        print(f"[PASS] 5. Incident Triage Queue: {len(incidents)} incidents on record")

        # 6. Test HITL Review Lifecycle if an incident exists
        if len(incidents) > 0:
            target_inc = incidents[0]
            review_res = await client.post(
                f"/api/v1/incidents/{target_inc['id']}/review",
                json={
                    "action": "ACKNOWLEDGE",
                    "notes": "Verified by Chief Safety Officer via automated integration test."
                },
                headers=headers
            )
            assert review_res.status_code == 200
            updated = review_res.json()
            assert updated["status"] == "ACKNOWLEDGED"
            assert len(updated["audit_logs"]) >= 1
            print(f"[PASS] 6. Human-In-The-Loop Audit Action committed for Incident #{target_inc['id']}")

        # 7. Check Analytics
        analytics_res = await client.get("/api/v1/analytics/summary", headers=headers)
        assert analytics_res.status_code == 200
        stats = analytics_res.json()
        print(f"[PASS] 7. Analytics Summary KPIs: Compliance={stats['compliance_rate_percent']}%")

    print("\nALL SYSTEM VERIFICATIONS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(test_live_system())
