import asyncio
import base64
import cv2
import json
import time
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.camera import Camera
from app.models.zone import Zone
from app.services.stream_manager import stream_manager
from app.services.ai_pipeline import SafetyPerceptionPipeline
from app.services.detector import VisionDetector

router = APIRouter(tags=["WebSockets"])

# Shared pipeline instance
pipeline = SafetyPerceptionPipeline()

def init_pipeline_models():
    """Initializes models when ready."""
    try:
        det = VisionDetector()
        pipeline.set_detector(det)
    except Exception as e:
        print(f"[WS] AI Detector warming up or loading: {e}")

@router.websocket("/ws/stream/{camera_id}")
async def websocket_stream_endpoint(websocket: WebSocket, camera_id: int):
    await websocket.accept()
    print(f"[WS] Client connected to Camera {camera_id} stream")

    # Fetch camera & zone configuration from database
    async with AsyncSessionLocal() as db:
        cam_res = await db.execute(select(Camera).filter(Camera.id == camera_id))
        camera = cam_res.scalars().first()
        if not camera:
            await websocket.send_json({"error": "Camera not found"})
            await websocket.close()
            return

        source = camera.stream_source
        
        # Load active zones for this camera
        zones_res = await db.execute(select(Zone).filter(Zone.camera_id == camera_id, Zone.is_active == True))
        zones = zones_res.scalars().all()
        zones_data = []
        for z in zones:
            coords = json.loads(z.polygon_coords) if isinstance(z.polygon_coords, str) else z.polygon_coords
            req_ppe = json.loads(z.required_ppe) if isinstance(z.required_ppe, str) else z.required_ppe
            zones_data.append({
                "id": z.id,
                "name": z.name,
                "zone_type": z.zone_type,
                "polygon_coords": coords,
                "required_ppe": req_ppe,
                "severity_level": z.severity_level,
                "dwell_threshold_seconds": z.dwell_threshold_seconds
            })
        pipeline.update_zones(zones_data)

    stream = stream_manager.get_or_create_stream(camera_id, source)

    try:
        while True:
            # Poll frame from stream worker
            has_frame, frame, health = stream.get_frame()

            if not has_frame or frame is None:
                # Fail-safe notification to client: Do not claim SAFE!
                await websocket.send_json({
                    "camera_id": camera_id,
                    "status": "UNKNOWN / MONITORING_DEGRADED",
                    "health": health,
                    "frame": None,
                    "pipeline": None,
                    "timestamp": time.time()
                })
                await asyncio.sleep(0.5)
                continue

            # Run safety perception pipeline
            async with AsyncSessionLocal() as db:
                pipeline_res = await pipeline.process_frame(
                    frame=frame,
                    camera_id=camera_id,
                    db=db
                )

            # Compress frame to JPEG for live web preview
            h, w = frame.shape[:2]
            # Resize if large to ensure ultra-low latency streaming
            if w > 854:
                scale = 854.0 / w
                display_frame = cv2.resize(frame, (854, int(h * scale)))
            else:
                display_frame = frame

            _, buffer = cv2.imencode('.jpg', display_frame, [cv2.IMWRITE_JPEG_QUALITY, 65])
            jpg_base64 = base64.b64encode(buffer).decode('utf-8')

            # Send payload
            payload = {
                "camera_id": camera_id,
                "status": health.get("status", "HEALTHY"),
                "health": health,
                "frame": f"data:image/jpeg;base64,{jpg_base64}",
                "pipeline": pipeline_res,
                "zones": zones_data,
                "timestamp": time.time()
            }
            await websocket.send_text(json.dumps(payload))

            # Maintain ~15 FPS target for UI reactivity
            await asyncio.sleep(0.065)

    except WebSocketDisconnect:
        print(f"[WS] Client disconnected from Camera {camera_id}")
    except Exception as e:
        print(f"[WS] Exception in stream {camera_id}: {e}")
        try:
            await websocket.close()
        except:
            pass
