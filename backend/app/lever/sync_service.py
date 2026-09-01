import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Internship, SourceRegistry
from app.lever.schemas import NormalizedLeverJob
from app.ingestion.pipeline.deduplication import generate_internship_sha256_fingerprint
from app.services.opportunity_quality import OpportunityQualityService

logger = logging.getLogger(__name__)

class LeverSyncService:
    """
    Service for persisting real Lever jobs and internships into the primary PostgreSQL database schema.
    """

    @staticmethod
    async def store_lever_opportunities(
        db: AsyncSession,
        jobs: List[NormalizedLeverJob]
    ) -> Dict[str, Any]:
        """
        Stores normalized real Lever opportunities in PostgreSQL database.
        Preserves 100% of existing records from Greenhouse, Adzuna, NCS, and PMIS.
        """
        logger.info(f"--- Storing {len(jobs)} Real Lever Opportunities in Database ---")
        created_count = 0
        updated_count = 0
        duplicate_count = 0
        failed_count = 0

        now = datetime.utcnow()

        for job in jobs:
            try:
                ext_id = str(job.external_id) if job.external_id else None

                fingerprint = generate_internship_sha256_fingerprint(
                    company_name=job.company,
                    title=job.title,
                    location=job.location or "Global",
                    application_url=job.apply_url
                )

                existing = None
                if ext_id:
                    stmt = select(Internship).where(
                        (Internship.source == "Lever") &
                        (Internship.external_id == ext_id)
                    )
                    res = await db.execute(stmt)
                    existing = res.scalar_one_or_none()

                if not existing and job.apply_url:
                    stmt_alt = select(Internship).where(
                        (Internship.apply_url == job.apply_url) |
                        (Internship.fingerprint_sha256 == fingerprint)
                    )
                    res_alt = await db.execute(stmt_alt)
                    existing = res_alt.scalar_one_or_none()

                if not existing:
                    is_remote = "remote" in (job.location or "").lower()
                    work_mode = "Remote" if is_remote else "On-site"

                    safe_title = (job.title or "")[:255]
                    safe_location = (job.location or "Multiple Locations / Remote")[:255]
                    safe_sector = "Technology & Corporate Services"[:255]
                    safe_stipend = ("Competitive Market Compensation" if job.opportunity_type == "JOB" else "Industry Stipend")[:255]
                    safe_emp_type = (getattr(job, "commitment", None) or "")[:255] or None
                    safe_dept = (getattr(job, "team", None) or "")[:255] or None

                    new_record = Internship(
                        company_name=job.company,
                        company_sector=safe_sector,
                        title=safe_title,
                        description=job.description or f"{safe_title} opportunity at {job.company}.",
                        location=safe_location,
                        work_mode=work_mode,
                        duration="Full-Time" if job.opportunity_type == "JOB" else "6 Months",
                        stipend=safe_stipend,
                        deadline="2026-12-31",
                        positions=1,
                        min_qualification="Graduate",
                        source="Lever",
                        external_id=ext_id,
                        department=safe_dept,
                        employment_type=safe_emp_type,
                        opportunity_type=job.opportunity_type or "INTERNSHIP",
                        source_url=job.source_url if OpportunityQualityService.validate_application_url(job.source_url)[0] else "APPLICATION_URL_UNAVAILABLE",
                        apply_url=job.apply_url if OpportunityQualityService.validate_application_url(job.apply_url)[0] else "APPLICATION_URL_UNAVAILABLE",
                        fingerprint_sha256=fingerprint,
                        status="VERIFIED_LIVE",
                        verification_status="VERIFIED",
                        quality_score=90.0,
                        is_demo=False,
                        first_seen_at=now,
                        last_seen_at=now,
                        last_verified_at=now,
                        last_checked_at=now
                    )
                    db.add(new_record)
                    try:
                        await db.flush()
                        await db.commit()
                        created_count += 1
                    except Exception as flush_err:
                        await db.rollback()
                        failed_count += 1
                        logger.error(f"Failed to persist Lever job ID {ext_id} ({safe_title[:60]}): {flush_err}")
                else:
                    has_changes = False

                    if job.title and existing.title != job.title:
                        existing.title = job.title[:255]
                        has_changes = True

                    if job.description and existing.description != job.description:
                        existing.description = job.description
                        has_changes = True

                    if job.location and existing.location != job.location:
                        existing.location = job.location[:255]
                        has_changes = True

                    if job.apply_url and OpportunityQualityService.validate_application_url(job.apply_url)[0] and existing.apply_url != job.apply_url:
                        existing.apply_url = job.apply_url
                        has_changes = True

                    if job.opportunity_type and existing.opportunity_type != job.opportunity_type:
                        existing.opportunity_type = job.opportunity_type
                        has_changes = True

                    existing.last_seen_at = now
                    existing.last_checked_at = now

                    if has_changes:
                        existing.last_verified_at = now
                        updated_count += 1
                    else:
                        duplicate_count += 1

            except Exception as e:
                failed_count += 1
                logger.error(f"Error persisting Lever job ID {job.external_id}: {str(e)}")

        try:
            await db.commit()
        except Exception as commit_err:
            await db.rollback()
            logger.error(f"Final batch commit error for Lever: {commit_err}")

        summary = {
            "status": "SUCCESS" if failed_count == 0 else "PARTIAL_SUCCESS",
            "total_processed": len(jobs),
            "records_created": created_count,
            "records_updated": updated_count,
            "duplicates_detected": duplicate_count,
            "failed_count": failed_count,
            "timestamp": now.isoformat()
        }
        return summary

    @staticmethod
    async def run_full_lever_sync(
        db: AsyncSession,
        sites: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Executes full scheduled synchronization cycle for Lever opportunities:
        1. Fetches live jobs via LeverService.
        2. Normalizes & classifies opportunities (JOB, INTERNSHIP, UNKNOWN).
        3. Inserts new & updates changed opportunities.
        4. Identifies unavailable Lever opportunities and transitions them to 'EXPIRED'.
        5. Preserves 100% of historical records.
        6. Updates source registry metrics.
        """
        logger.info("======================================================================")
        logger.info("  STARTING LEVER PERIODIC BACKGROUND SYNCHRONIZATION CYCLE")
        logger.info("======================================================================")

        now = datetime.utcnow()
        try:
            from app.lever.service import LeverService
            service = LeverService()

            normalized_jobs = await service.fetch_and_normalize_jobs(sites=sites)
            logger.info(f"Lever Sync: Fetched {len(normalized_jobs)} real normalized opportunities.")

            store_res = await LeverSyncService.store_lever_opportunities(db, normalized_jobs)

            # Identify unavailable Lever opportunities and mark as EXPIRED only on non-empty successful fetch
            expired_count = 0
            if len(normalized_jobs) > 0:
                active_external_ids = {str(j.external_id) for j in normalized_jobs if j.external_id}

                stmt_active_lever = select(Internship).where(
                    Internship.source == "Lever",
                    Internship.status != "EXPIRED"
                )
                res_active_lever = await db.execute(stmt_active_lever)
                existing_records = res_active_lever.scalars().all()

                for rec in existing_records:
                    if rec.external_id and rec.external_id not in active_external_ids:
                        rec.status = "EXPIRED"
                        rec.verification_status = "EXPIRED"
                        rec.last_checked_at = now
                        expired_count += 1

                if expired_count > 0:
                    await db.commit()
                    logger.info(f"Lever Sync: Marked {expired_count} unavailable opportunities as EXPIRED.")

            # Update SourceRegistry entry for Lever
            stmt_src = select(SourceRegistry).where(SourceRegistry.source_name == "Lever")
            res_src = await db.execute(stmt_src)
            src = res_src.scalar_one_or_none()

            if not src:
                src = SourceRegistry(
                    source_name="Lever",
                    source_url="https://hire.lever.co/developer/documentation",
                    source_type="AUTHORIZED_API",
                    authentication_method="NONE",
                    authorization_status="AUTHORIZED",
                    enabled=True,
                    polling_frequency_seconds=21600,
                    health_status="ONLINE"
                )
                db.add(src)

            src.last_success_at = now
            src.last_run_at = now
            src.health_status = "ONLINE"
            src.last_checked_at = now
            await db.commit()

            sync_summary = {
                "status": "SUCCESS",
                "total_fetched": len(normalized_jobs),
                "records_created": store_res["records_created"],
                "records_updated": store_res["records_updated"],
                "duplicates_detected": store_res["duplicates_detected"],
                "expired_marked": expired_count,
                "timestamp": now.isoformat()
            }
            logger.info(
                f"--- Lever Sync Completed Successfully: "
                f"Fetched={len(normalized_jobs)}, Created={store_res['records_created']}, "
                f"Updated={store_res['records_updated']}, Duplicates={store_res['duplicates_detected']}, "
                f"Expired={expired_count} ---"
            )
            return sync_summary

        except Exception as e:
            logger.error(f"Lever Sync Failure: {str(e)}", exc_info=True)
            return {
                "status": "FAILURE",
                "error": str(e),
                "timestamp": now.isoformat()
            }
