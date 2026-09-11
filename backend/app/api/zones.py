import json
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.zone import Zone
from app.schemas.zone import ZoneCreate, ZoneUpdate, ZoneOut
from app.api.deps import get_current_user, require_role

router = APIRouter(prefix="/zones", tags=["Zones"])

@router.get("/camera/{camera_id}", response_model=List[ZoneOut])
async def list_zones_for_camera(camera_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Zone).filter(Zone.camera_id == camera_id))
    zones = result.scalars().all()
    # Parse json polygon_coords and required_ppe
    out_list = []
    for z in zones:
        coords = json.loads(z.polygon_coords) if isinstance(z.polygon_coords, str) else z.polygon_coords
        req_ppe = json.loads(z.required_ppe) if isinstance(z.required_ppe, str) else z.required_ppe
        out_list.append(ZoneOut(
            id=z.id,
            camera_id=z.camera_id,
            name=z.name,
            zone_type=z.zone_type,
            polygon_coords=coords,
            required_ppe=req_ppe,
            severity_level=z.severity_level,
            dwell_threshold_seconds=z.dwell_threshold_seconds,
            is_active=z.is_active,
            created_at=z.created_at
        ))
    return out_list

@router.post("", response_model=ZoneOut)
async def create_zone(
    zone_in: ZoneCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(["ADMIN", "SAFETY_MANAGER"]))
):
    zone = Zone(
        camera_id=zone_in.camera_id,
        name=zone_in.name,
        zone_type=zone_in.zone_type,
        polygon_coords=json.dumps(zone_in.polygon_coords),
        required_ppe=json.dumps(zone_in.required_ppe or []),
        severity_level=zone_in.severity_level or 3,
        dwell_threshold_seconds=zone_in.dwell_threshold_seconds or 3,
        is_active=zone_in.is_active if zone_in.is_active is not None else True
    )
    db.add(zone)
    await db.commit()
    await db.refresh(zone)
    return ZoneOut(
        id=zone.id,
        camera_id=zone.camera_id,
        name=zone.name,
        zone_type=zone.zone_type,
        polygon_coords=zone_in.polygon_coords,
        required_ppe=zone_in.required_ppe or [],
        severity_level=zone.severity_level,
        dwell_threshold_seconds=zone.dwell_threshold_seconds,
        is_active=zone.is_active,
        created_at=zone.created_at
    )

@router.delete("/{zone_id}")
async def delete_zone(
    zone_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(["ADMIN", "SAFETY_MANAGER"]))
):
    result = await db.execute(select(Zone).filter(Zone.id == zone_id))
    zone = result.scalars().first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    await db.delete(zone)
    await db.commit()
    return {"status": "success", "message": f"Zone {zone_id} deleted"}
