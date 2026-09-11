from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.camera import Camera
from app.schemas.camera import CameraCreate, CameraUpdate, CameraOut
from app.api.deps import get_current_user, require_role
from app.services.stream_manager import stream_manager

router = APIRouter(prefix="/cameras", tags=["Cameras"])

@router.get("", response_model=List[CameraOut])
async def list_cameras(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Camera))
    cameras = result.scalars().all()
    # Update with live streaming health stats
    for cam in cameras:
        if cam.id in stream_manager.streams:
            st = stream_manager.streams[cam.id]
            cam.status = st.status
            cam.current_fps = round(st.calculated_fps, 1)
        else:
            cam.status = "UNKNOWN"
            cam.current_fps = 0.0
    return cameras

@router.post("", response_model=CameraOut)
async def create_camera(
    camera_in: CameraCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(["ADMIN", "SAFETY_MANAGER"]))
):
    camera = Camera(
        name=camera_in.name,
        location=camera_in.location,
        stream_source=camera_in.stream_source,
        fps=camera_in.fps or 30.0,
        width=camera_in.width or 1280,
        height=camera_in.height or 720,
        status="UNKNOWN"
    )
    db.add(camera)
    await db.commit()
    await db.refresh(camera)
    
    # Initialize stream
    stream_manager.get_or_create_stream(camera.id, camera.stream_source)
    return camera

@router.get("/{camera_id}", response_model=CameraOut)
async def get_camera(camera_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Camera).filter(Camera.id == camera_id))
    camera = result.scalars().first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    if camera.id in stream_manager.streams:
        st = stream_manager.streams[camera.id]
        camera.status = st.status
        camera.current_fps = round(st.calculated_fps, 1)
    return camera

@router.delete("/{camera_id}")
async def delete_camera(
    camera_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(["ADMIN"]))
):
    result = await db.execute(select(Camera).filter(Camera.id == camera_id))
    camera = result.scalars().first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    stream_manager.stop_stream(camera_id)
    await db.delete(camera)
    await db.commit()
    return {"status": "success", "message": f"Camera {camera_id} removed"}
