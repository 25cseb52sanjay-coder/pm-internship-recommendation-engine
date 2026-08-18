from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime

from app.db.database import get_db
from app.db.models import SourceRegistry, IngestionRun, IngestionJob, IngestionError, Internship, User
from app.api.v1.deps import get_current_admin
from app.ingestion.schemas.ingestion_schemas import IngestionStatusSummary, IngestionRunOut, IngestionErrorOut

router = APIRouter()

@router.get("/status", response_model=IngestionStatusSummary)
async def get_ingestion_status(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns administrative summary dashboard metrics for ingestion pipeline (Google Antigravity Spec).
    """
    # Total Sources
    src_res = await db.execute(select(SourceRegistry))
    sources = src_res.scalars().all()

    total_sources = len(sources)
    healthy_sources = sum(1 for s in sources if s.health_status == "ONLINE")
    failed_sources = sum(1 for s in sources if s.health_status in ("FAILED", "DEGRADED"))

    # Health Breakdown Map
    health_map = {}
    for s in sources:
        health_map[s.health_status] = health_map.get(s.health_status, 0) + 1

    # Last successful run timestamp
    succ_res = await db.execute(
        select(func.max(IngestionRun.completed_at)).where(IngestionRun.status == "COMPLETED")
    )
    last_success = succ_res.scalar()

    # Next scheduled run
    next_res = await db.execute(
        select(func.min(SourceRegistry.next_run_at)).where(SourceRegistry.enabled == True)
    )
    next_sched = next_res.scalar()

    # Internship Counts by Lifecycle State
    new_res = await db.execute(select(func.count(Internship.id)).where(Internship.status.in_(["DISCOVERED", "VERIFIED_LIVE"])))
    new_cnt = new_res.scalar() or 0

    upd_res = await db.execute(select(func.count(Internship.id)).where(Internship.status == "UPDATED"))
    upd_cnt = upd_res.scalar() or 0

    rej_res = await db.execute(select(func.count(Internship.id)).where(Internship.status == "REJECTED"))
    rej_cnt = rej_res.scalar() or 0

    exp_res = await db.execute(select(func.count(Internship.id)).where(Internship.status == "EXPIRED"))
    exp_cnt = exp_res.scalar() or 0

    # Duplicates & Errors Summary
    dup_res = await db.execute(select(func.sum(IngestionRun.duplicates_detected)))
    dup_cnt = dup_res.scalar() or 0

    err_res = await db.execute(select(func.count(IngestionError.id)))
    err_cnt = err_res.scalar() or 0

    failed_jobs_res = await db.execute(select(func.count(IngestionJob.job_id)).where(IngestionJob.status == "FAILED"))
    failed_jobs_cnt = failed_jobs_res.scalar() or 0

    return IngestionStatusSummary(
        total_sources=total_sources,
        healthy_sources=healthy_sources,
        failed_sources=failed_sources,
        last_successful_run=last_success,
        next_scheduled_run=next_sched,
        new_internships=new_cnt,
        updated_internships=upd_cnt,
        duplicates=dup_cnt,
        rejected_listings=rej_cnt,
        expired_listings=exp_cnt,
        failed_jobs=failed_jobs_cnt,
        source_health_breakdown=health_map
    )

@router.get("/runs", response_model=List[IngestionRunOut])
async def list_ingestion_runs(
    limit: int = Query(20, ge=1, le=100),
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Lists history of ingestion runs (Admin Only)."""
    res = await db.execute(select(IngestionRun).order_by(IngestionRun.started_at.desc()).limit(limit))
    return res.scalars().all()

@router.get("/errors", response_model=List[IngestionErrorOut])
async def list_ingestion_errors(
    limit: int = Query(50, ge=1, le=200),
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Lists structured ingestion error logs (Admin Only)."""
    res = await db.execute(select(IngestionError).order_by(IngestionError.created_at.desc()).limit(limit))
    return res.scalars().all()
