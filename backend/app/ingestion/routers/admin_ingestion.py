from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List, Optional
from datetime import datetime

from app.db.database import get_db
from app.db.models import SourceRegistry, User, IngestionRun
from app.api.v1.deps import get_current_admin
from app.ingestion.schemas.ingestion_schemas import SourceRegistryCreate, SourceRegistryUpdate, SourceRegistryOut, IngestionRunOut
from app.ingestion.pipeline.validation import validate_url_ssrf_safe

router = APIRouter()

@router.post("/run", status_code=status.HTTP_202_ACCEPTED)
async def trigger_full_ingestion(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Triggers manual full ingestion run across all active sources (Admin Only - Google Antigravity Spec).
    """
    res = await db.execute(select(SourceRegistry).where(SourceRegistry.enabled == True))
    sources = res.scalars().all()

    triggered_ids = []
    for src in sources:
        try:
            from app.ingestion.tasks import run_source_ingestion_task
            run_source_ingestion_task.delay(src.id)
        except Exception:
            pass
        triggered_ids.append(src.id)

    return {
        "message": "Full ingestion job initiated successfully",
        "triggered_source_ids": triggered_ids,
        "count": len(triggered_ids),
        "timestamp": datetime.utcnow()
    }

@router.get("/sources", response_model=List[SourceRegistryOut])
async def list_sources(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Lists registered ingestion sources (Admin Only)."""
    res = await db.execute(select(SourceRegistry).order_by(SourceRegistry.priority.asc()))
    sources = res.scalars().all()
    if not sources:
        # Seed default sources per spec
        default_sources = [
            SourceRegistry(
                source_name="PM Internship Portal Official Feed",
                source_url="https://pminternship.mca.gov.in/api/feed",
                source_type="OFFICIAL_SCHEME",
                authorization_status="AUTHORIZED",
                health_status="ONLINE",
                source_confidence=1.0,
                priority=1
            ),
            SourceRegistry(
                source_name="Company Career Authorized Feed (Tata Motors)",
                source_url="https://careers.tatamotors.com/api/pm-internships",
                source_type="COMPANY_CAREER",
                authorization_status="AUTHORIZED",
                health_status="ONLINE",
                source_confidence=0.95,
                priority=2
            ),
            SourceRegistry(
                source_name="LinkedIn Authorized API Stub",
                source_url="https://api.linkedin.com/v2/jobs",
                source_type="AUTHORIZED_API",
                authorization_status="NOT_CONFIGURED",
                health_status="NOT_CONFIGURED",
                source_confidence=0.9,
                priority=3,
                enabled=False
            ),
            SourceRegistry(
                source_name="Internshala Authorized Feed Stub",
                source_url="https://internshala.com/api/v1/feed",
                source_type="AUTHORIZED_FEED",
                authorization_status="NOT_CONFIGURED",
                health_status="NOT_CONFIGURED",
                source_confidence=0.85,
                priority=4,
                enabled=False
            ),
            SourceRegistry(
                source_name="Naukri Authorized API Stub",
                source_url="https://api.naukri.com/v1/jobs",
                source_type="AUTHORIZED_API",
                authorization_status="NOT_CONFIGURED",
                health_status="NOT_CONFIGURED",
                source_confidence=0.85,
                priority=5,
                enabled=False
            )
        ]
        for ds in default_sources:
            db.add(ds)
        await db.commit()
        res = await db.execute(select(SourceRegistry).order_by(SourceRegistry.priority.asc()))
        sources = res.scalars().all()

    return sources

@router.post("/sources", response_model=SourceRegistryOut, status_code=status.HTTP_201_CREATED)
async def create_source(
    data: SourceRegistryCreate,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Registers new ingestion source with SSRF protection check (Admin Only)."""
    # SSRF Protection Check
    is_safe, msg = validate_url_ssrf_safe(data.source_url)
    if not is_safe:
        raise HTTPException(status_code=400, detail=f"SSRF Security Violation: {msg}")

    if data.api_endpoint:
        is_safe_ep, msg_ep = validate_url_ssrf_safe(data.api_endpoint)
        if not is_safe_ep:
            raise HTTPException(status_code=400, detail=f"SSRF Security Violation in api_endpoint: {msg_ep}")

    src = SourceRegistry(
        source_name=data.source_name,
        source_url=data.source_url,
        source_type=data.source_type,
        api_endpoint=data.api_endpoint,
        authentication_method=data.authentication_method,
        authorization_status=data.authorization_status,
        enabled=data.enabled,
        polling_frequency_seconds=data.polling_frequency_seconds,
        rate_limit=data.rate_limit,
        priority=data.priority,
        source_confidence=data.source_confidence,
        health_status="ONLINE" if data.authorization_status == "AUTHORIZED" else "NOT_CONFIGURED"
    )
    db.add(src)
    await db.commit()
    await db.refresh(src)
    return src

@router.patch("/sources/{source_id}", response_model=SourceRegistryOut)
async def update_source(
    source_id: int,
    data: SourceRegistryUpdate,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Updates ingestion source configuration (Admin Only)."""
    res = await db.execute(select(SourceRegistry).where(SourceRegistry.id == source_id))
    src = res.scalar_one_or_none()
    if not src:
        raise HTTPException(status_code=404, detail="Source registry record not found")

    if data.source_url:
        is_safe, msg = validate_url_ssrf_safe(data.source_url)
        if not is_safe:
            raise HTTPException(status_code=400, detail=f"SSRF Security Violation: {msg}")
        src.source_url = data.source_url

    if data.source_name is not None:
        src.source_name = data.source_name
    if data.authorization_status is not None:
        src.authorization_status = data.authorization_status
    if data.enabled is not None:
        src.enabled = data.enabled
    if data.polling_frequency_seconds is not None:
        src.polling_frequency_seconds = data.polling_frequency_seconds
    if data.rate_limit is not None:
        src.rate_limit = data.rate_limit
    if data.priority is not None:
        src.priority = data.priority
    if data.health_status is not None:
        src.health_status = data.health_status

    db.add(src)
    await db.commit()
    await db.refresh(src)
    return src

@router.post("/sources/{source_id}/run", status_code=status.HTTP_202_ACCEPTED)
async def run_specific_source_ingestion(
    source_id: int,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Triggers ingestion run for specific source ID (Admin Only)."""
    res = await db.execute(select(SourceRegistry).where(SourceRegistry.id == source_id))
    src = res.scalar_one_or_none()
    if not src:
        raise HTTPException(status_code=404, detail="Source registry record not found")

    try:
        from app.ingestion.tasks import run_source_ingestion_task
        run_source_ingestion_task.delay(source_id)
    except Exception:
        pass

    return {
        "message": f"Ingestion job initiated for source '{src.source_name}'",
        "source_id": source_id,
        "timestamp": datetime.utcnow()
    }
