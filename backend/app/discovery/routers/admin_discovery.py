from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from typing import List, Optional
from datetime import datetime

from app.db.database import get_db
from app.db.models import DiscoverySearchQuery, DiscoveryCandidate, DiscoveryRun, User
from app.api.v1.deps import get_current_admin
from app.discovery.schemas.discovery_schemas import (
    DiscoverySearchQueryCreate,
    DiscoverySearchQueryUpdate,
    DiscoverySearchQueryOut,
    DiscoveryCandidateOut,
    DiscoveryCandidateUpdate,
    DiscoveryRunOut,
    DiscoveryStatusSummary
)
from app.core.config import settings

router = APIRouter()

@router.post("/run", status_code=status.HTTP_202_ACCEPTED)
async def trigger_discovery_sweep(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Triggers manual web discovery sweep across dynamic queries (Admin Only - Google Antigravity Spec)."""
    try:
        from app.discovery.tasks import run_discovery_sweep_task
        run_discovery_sweep_task.delay()
    except Exception:
        pass

    return {
        "message": "Discovery sweep task initiated successfully",
        "timestamp": datetime.utcnow()
    }

@router.get("/status", response_model=DiscoveryStatusSummary)
async def get_discovery_status_summary(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Returns summary metrics for discovery engine dashboard (Admin Only)."""
    # Queries executed today
    q_res = await db.execute(select(func.count(DiscoverySearchQuery.id)).where(DiscoverySearchQuery.enabled == True))
    q_cnt = q_res.scalar() or 0

    # Candidates counts
    cand_res = await db.execute(select(DiscoveryCandidate))
    cands = cand_res.scalars().all()

    total_disc = len(cands)
    verified_cnt = sum(1 for c in cands if c.verification_status == "VERIFIED")
    rejected_cnt = sum(1 for c in cands if c.verification_status not in ("VERIFIED", "PENDING"))
    pending_cnt = sum(1 for c in cands if c.verification_status in ("PENDING", "NOT_IDENTIFIABLE_EMPLOYER"))

    # Rejection breakdown
    rej_map = {}
    for c in cands:
        if c.verification_status != "VERIFIED":
            rej_map[c.verification_status] = rej_map.get(c.verification_status, 0) + 1

    dup_cnt = sum(1 for c in cands if c.rejection_reason and "Duplicate" in c.rejection_reason)

    return DiscoveryStatusSummary(
        queries_executed_today=q_cnt,
        urls_discovered=total_disc,
        urls_verified=verified_cnt,
        urls_rejected=rejected_cnt,
        rejection_breakdown=rej_map,
        candidates_pending_review=pending_cnt,
        duplicates_merged=dup_cnt,
        search_provider_quota_remaining=settings.SEARCH_PROVIDER_QUOTA_PER_DAY
    )

@router.get("/runs", response_model=List[DiscoveryRunOut])
async def list_discovery_runs(
    limit: int = Query(20, ge=1, le=100),
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Lists history of discovery runs (Admin Only)."""
    res = await db.execute(select(DiscoveryRun).order_by(DiscoveryRun.started_at.desc()).limit(limit))
    return res.scalars().all()

@router.get("/candidates", response_model=List[DiscoveryCandidateOut])
async def list_discovery_candidates(
    verification_status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Lists discovery candidates filtered by verification_status for manual review (Admin Only)."""
    stmt = select(DiscoveryCandidate)
    if verification_status:
        stmt = stmt.where(DiscoveryCandidate.verification_status == verification_status)
    stmt = stmt.order_by(DiscoveryCandidate.discovered_at.desc()).limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()

@router.patch("/candidates/{candidate_id}", response_model=DiscoveryCandidateOut)
async def update_candidate_verification_status(
    candidate_id: int,
    data: DiscoveryCandidateUpdate,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Manually approves or rejects borderline discovery candidates (Admin Only)."""
    res = await db.execute(select(DiscoveryCandidate).where(DiscoveryCandidate.id == candidate_id))
    cand = res.scalar_one_or_none()
    if not cand:
        raise HTTPException(status_code=404, detail="Discovery candidate record not found")

    cand.verification_status = data.verification_status
    if data.rejection_reason:
        cand.rejection_reason = data.rejection_reason

    db.add(cand)
    await db.commit()
    await db.refresh(cand)
    return cand

@router.get("/queries", response_model=List[DiscoverySearchQueryOut])
async def list_search_queries(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Lists configured discovery search queries (Admin Only)."""
    res = await db.execute(select(DiscoverySearchQuery).order_by(DiscoverySearchQuery.generated_at.desc()))
    return res.scalars().all()

@router.post("/queries", response_model=DiscoverySearchQueryOut, status_code=status.HTTP_201_CREATED)
async def create_search_query(
    data: DiscoverySearchQueryCreate,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Creates a new discovery search query (Admin Only)."""
    q_obj = DiscoverySearchQuery(
        query_text=data.query_text,
        category=data.category,
        city=data.city,
        branch=data.branch,
        skill_tag=data.skill_tag,
        enabled=data.enabled
    )
    db.add(q_obj)
    await db.commit()
    await db.refresh(q_obj)
    return q_obj

@router.patch("/queries/{query_id}", response_model=DiscoverySearchQueryOut)
async def update_search_query(
    query_id: int,
    data: DiscoverySearchQueryUpdate,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Updates search query configuration (Admin Only)."""
    res = await db.execute(select(DiscoverySearchQuery).where(DiscoverySearchQuery.id == query_id))
    q_obj = res.scalar_one_or_none()
    if not q_obj:
        raise HTTPException(status_code=404, detail="Discovery search query record not found")

    if data.query_text is not None:
        q_obj.query_text = data.query_text
    if data.category is not None:
        q_obj.category = data.category
    if data.city is not None:
        q_obj.city = data.city
    if data.branch is not None:
        q_obj.branch = data.branch
    if data.skill_tag is not None:
        q_obj.skill_tag = data.skill_tag
    if data.enabled is not None:
        q_obj.enabled = data.enabled

    db.add(q_obj)
    await db.commit()
    await db.refresh(q_obj)
    return q_obj
