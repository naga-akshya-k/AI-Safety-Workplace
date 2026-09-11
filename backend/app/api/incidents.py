import json
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.incident import Incident
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.incident import IncidentOut, IncidentReviewAction
from app.api.deps import get_current_user

router = APIRouter(prefix="/incidents", tags=["Incidents"])

@router.get("", response_model=List[IncidentOut])
async def list_incidents(
    camera_id: Optional[int] = None,
    risk_level: Optional[int] = None,
    status_filter: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    query = select(Incident).options(selectinload(Incident.audit_logs)).order_by(desc(Incident.created_at))
    
    if camera_id:
        query = query.filter(Incident.camera_id == camera_id)
    if risk_level is not None:
        query = query.filter(Incident.risk_level >= risk_level)
    if status_filter:
        query = query.filter(Incident.status == status_filter)

    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    incidents = result.scalars().all()

    out_list = []
    for inc in incidents:
        exp = json.loads(inc.explainability) if isinstance(inc.explainability, str) else inc.explainability
        out_list.append(IncidentOut(
            id=inc.id,
            camera_id=inc.camera_id,
            zone_id=inc.zone_id,
            event_type=inc.event_type,
            risk_level=inc.risk_level,
            status=inc.status,
            confidence=inc.confidence,
            duration_seconds=inc.duration_seconds,
            explainability=exp,
            recommended_action=inc.recommended_action,
            evidence_snapshot_path=inc.evidence_snapshot_path,
            assigned_to_user_id=inc.assigned_to_user_id,
            operator_notes=inc.operator_notes,
            created_at=inc.created_at,
            updated_at=inc.updated_at,
            audit_logs=inc.audit_logs
        ))
    return out_list

@router.get("/{incident_id}", response_model=IncidentOut)
async def get_incident(incident_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Incident).options(selectinload(Incident.audit_logs)).filter(Incident.id == incident_id)
    )
    inc = result.scalars().first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    exp = json.loads(inc.explainability) if isinstance(inc.explainability, str) else inc.explainability
    return IncidentOut(
        id=inc.id,
        camera_id=inc.camera_id,
        zone_id=inc.zone_id,
        event_type=inc.event_type,
        risk_level=inc.risk_level,
        status=inc.status,
        confidence=inc.confidence,
        duration_seconds=inc.duration_seconds,
        explainability=exp,
        recommended_action=inc.recommended_action,
        evidence_snapshot_path=inc.evidence_snapshot_path,
        assigned_to_user_id=inc.assigned_to_user_id,
        operator_notes=inc.operator_notes,
        created_at=inc.created_at,
        updated_at=inc.updated_at,
        audit_logs=inc.audit_logs
    )

@router.post("/{incident_id}/review", response_model=IncidentOut)
async def review_incident(
    incident_id: int,
    review_in: IncidentReviewAction,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Human-In-The-Loop (HITL) Audit Action.
    Enforces human accountability:
    Action can be: ACKNOWLEDGE, CONFIRM, OVERRIDE, RESOLVE.
    """
    result = await db.execute(
        select(Incident).options(selectinload(Incident.audit_logs)).filter(Incident.id == incident_id)
    )
    inc = result.scalars().first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    action_map = {
        "ACKNOWLEDGE": "ACKNOWLEDGED",
        "CONFIRM": "CONFIRMED_HAZARD",
        "OVERRIDE": "FALSE_POSITIVE_OVERRIDE",
        "RESOLVE": "RESOLVED"
    }

    if review_in.action not in action_map:
        raise HTTPException(status_code=400, detail=f"Invalid action: must be one of {list(action_map.keys())}")

    previous_status = inc.status
    new_status = action_map[review_in.action]

    inc.status = new_status
    if review_in.notes:
        inc.operator_notes = f"{inc.operator_notes or ''}\n[{current_user.full_name}]: {review_in.notes}".strip()

    # Record Audit Log entry
    audit_entry = AuditLog(
        incident_id=inc.id,
        user_id=current_user.id,
        action=review_in.action,
        previous_status=previous_status,
        new_status=new_status,
        reason=review_in.override_reason or review_in.notes
    )
    db.add(audit_entry)
    await db.commit()
    await db.refresh(inc)

    exp = json.loads(inc.explainability) if isinstance(inc.explainability, str) else inc.explainability
    return IncidentOut(
        id=inc.id,
        camera_id=inc.camera_id,
        zone_id=inc.zone_id,
        event_type=inc.event_type,
        risk_level=inc.risk_level,
        status=inc.status,
        confidence=inc.confidence,
        duration_seconds=inc.duration_seconds,
        explainability=exp,
        recommended_action=inc.recommended_action,
        evidence_snapshot_path=inc.evidence_snapshot_path,
        assigned_to_user_id=inc.assigned_to_user_id,
        operator_notes=inc.operator_notes,
        created_at=inc.created_at,
        updated_at=inc.updated_at,
        audit_logs=inc.audit_logs
    )
