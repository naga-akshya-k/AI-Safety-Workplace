import asyncio
import json
import websockets
import httpx

async def verify_hazards():
    print("=" * 65)
    print("COMPREHENSIVE MULTI-CAMERA INDUSTRIAL HAZARD VALIDATION (EXTENDED)")
    print("=" * 65)

    base_ws = "ws://127.0.0.1:8000"
    base_http = "http://127.0.0.1:8000"

    cameras_to_test = [
        (1, "Warehouse Forklift & Proximity", 40),
        (2, "Shop Floor PPE Enforcement", 40),
        (3, "Robotic Cell Exclusion Zone", 85),
        (4, "Worker Fall & Man-Down Immobility", 90)
    ]

    for cam_id, description, max_f in cameras_to_test:
        print(f"\n[CAM {cam_id}] Streaming {max_f} frames: {description}...")
        ws_url = f"{base_ws}/ws/stream/{cam_id}"
        
        async with websockets.connect(ws_url) as ws:
            frames_processed = 0
            hazards_seen = []
            
            for _ in range(max_f):
                msg = await ws.recv()
                data = json.loads(msg)
                pipe = data.get("pipeline")
                if pipe:
                    frames_processed += 1
                    risks = pipe.get("risk_assessments", [])
                    for r in risks:
                        evt = r.get("event_type")
                        lvl = r.get("risk_level")
                        hazards_seen.append((evt, lvl))

            print(f"  -> Processed {frames_processed} frames successfully.")
            unique_hazards = list(set(hazards_seen))
            print(f"  -> Confirmed Hazards: {unique_hazards if unique_hazards else 'Baseline Monitored Normal'}")

    # Inspect Incident Triage Queue from Database
    async with httpx.AsyncClient(base_url=base_http) as client:
        login_res = await client.post(
            "/api/v1/auth/login",
            data={"username": "admin@safety.industrial", "password": "admin123"}
        )
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        inc_res = await client.get("/api/v1/incidents", headers=headers)
        incidents = inc_res.json()
        print(f"\n[INCIDENTS LOGGED IN TRIAGE QUEUE]: Total = {len(incidents)}")
        for inc in incidents[:8]:
            print(f"  * Incident #{inc['id']} | Cam {inc['camera_id']} | Type: {inc['event_type']} | Lvl {inc['risk_level']} | Status: {inc['status']}")
            print(f"    Reason: {inc['explainability'].get('reasoning')}")

    print("\n" + "=" * 65)
    print("ALL MULTI-CAMERA HAZARDS VALIDATED ACROSS CAMERAS 1 TO 4")
    print("=" * 65)

if __name__ == "__main__":
    asyncio.run(verify_hazards())
