import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Internship
from app.greenhouse.schemas import NormalizedGreenhouseJob
from app.ingestion.pipeline.deduplication import generate_internship_sha256_fingerprint
from app.services.opportunity_quality import OpportunityQualityService

logger = logging.getLogger(__name__)

class GreenhouseSyncService:
    """
    Service for persisting real Greenhouse jobs, internships, and UNKNOWN opportunities
    into the primary PostgreSQL database schema.
    """

    @staticmethod
    async def store_greenhouse_opportunities(
        db: AsyncSession,
        jobs: List[NormalizedGreenhouseJob]
    ) -> Dict[str, Any]:
        """
        Stores normalized real Greenhouse opportunities in PostgreSQL.
        Preserves 100% of existing records from NCS, PMIS, and other sources.
        """
        logger.info(f"--- Storing {len(jobs)} Real Greenhouse Opportunities in Database ---")
        
        created_count = 0
        updated_count = 0
        duplicate_count = 0
        failed_count = 0

        now = datetime.utcnow()

        for job in jobs:
            try:
                ext_id = str(job.external_id) if job.external_id else None

                # 1. Generate SHA-256 fingerprint hash
                fingerprint = generate_internship_sha256_fingerprint(
                    company_name=job.company,
                    title=job.title,
                    location=job.location or "Global",
                    application_url=job.apply_url
                )

                # 2. Primary lookup: external_id for Greenhouse source
                existing = None
                if ext_id:
                    stmt = select(Internship).where(
                        (Internship.source == "Greenhouse") &
                        (Internship.external_id == ext_id)
                    )
                    res = await db.execute(stmt)
                    existing = res.scalar_one_or_none()

                # Fallback lookup by apply_url or fingerprint if external_id not matched
                if not existing and job.apply_url:
                    stmt_alt = select(Internship).where(
                        (Internship.apply_url == job.apply_url) |
                        (Internship.fingerprint_sha256 == fingerprint)
                    )
                    res_alt = await db.execute(stmt_alt)
                    existing = res_alt.scalar_one_or_none()

                if not existing:
                    # 3. Create NEW Internship / Job Record in Database
                    is_remote = "remote" in (job.location or "").lower()
                    work_mode = "Remote" if is_remote else "On-site"

                    new_record = Internship(
                        company_name=job.company,
                        company_sector="Technology & Corporate Services",
                        title=job.title,
                        description=job.description or f"{job.title} opportunity at {job.company}.",
                        location=job.location or "Multiple Locations / Remote",
                        work_mode=work_mode,
                        duration="Full-Time" if job.opportunity_type == "JOB" else "6 Months",
                        stipend="Competitive Market Compensation" if job.opportunity_type == "JOB" else "Industry Stipend",
                        deadline="2026-12-31", # Standard open requisition window
                        positions=1,
                        min_qualification="Graduate",
                        source="Greenhouse",
                        external_id=ext_id,
                        department=getattr(job, "department", None),
                        employment_type=getattr(job, "employment_type", None),
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
                    created_count += 1
                else:
                    # 4. Existing record: check for field updates
                    has_changes = False

                    if job.title and existing.title != job.title:
                        existing.title = job.title
                        has_changes = True

                    if job.description and existing.description != job.description:
                        existing.description = job.description
                        has_changes = True

                    if job.location and existing.location != job.location:
                        existing.location = job.location
                        has_changes = True

                    if job.apply_url and OpportunityQualityService.validate_application_url(job.apply_url)[0] and existing.apply_url != job.apply_url:
                        existing.apply_url = job.apply_url
                        has_changes = True

                    if job.opportunity_type and existing.opportunity_type != job.opportunity_type:
                        existing.opportunity_type = job.opportunity_type
                        has_changes = True

                    dept = getattr(job, "department", None)
                    if dept and existing.department != dept:
                        existing.department = dept
                        has_changes = True

                    emp_type = getattr(job, "employment_type", None)
                    if emp_type and existing.employment_type != emp_type:
                        existing.employment_type = emp_type
                        has_changes = True

                    # Update timestamps
                    existing.last_seen_at = now
                    existing.last_checked_at = now

                    if has_changes:
                        existing.last_verified_at = now
                        updated_count += 1
                    else:
                        duplicate_count += 1

            except Exception as e:
                failed_count += 1
                logger.error(f"Error persisting Greenhouse job ID {job.external_id}: {str(e)}")

        await db.commit()

        summary = {
            "status": "SUCCESS" if failed_count == 0 else "PARTIAL_SUCCESS",
            "total_processed": len(jobs),
            "records_created": created_count,
            "records_updated": updated_count,
            "duplicates_detected": duplicate_count,
            "failed_count": failed_count,
            "timestamp": now.isoformat()
        }

        logger.info(
            f"--- Greenhouse Database Persistence Complete: "
            f"Created={created_count}, Updated={updated_count}, Duplicates={duplicate_count}, Failed={failed_count} ---"
        )
        return summary

    @staticmethod
    async def run_full_greenhouse_sync(
        db: AsyncSession,
        board_tokens: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Executes full scheduled synchronization cycle for Greenhouse opportunities:
        1. Fetches live jobs via GreenhouseService.
        2. Normalizes & classifies opportunities (JOB, INTERNSHIP, UNKNOWN).
        3. Inserts new & updates changed opportunities.
        4. Identifies opportunities no longer present in current fetch and transitions them to 'EXPIRED' (inactive).
        5. Preserves 100% of historical records without deleting data.
        6. Updates source registry metrics and writes structured logs.
        """
        logger.info("======================================================================")
        logger.info("  STARTING GREENHOUSE PERIODIC BACKGROUND SYNCHRONIZATION CYCLE")
        logger.info("======================================================================")

        now = datetime.utcnow()
        try:
            from app.greenhouse.service import GreenhouseService
            service = GreenhouseService()

            # Step 1: Fetch and normalize live opportunities
            normalized_jobs = await service.fetch_and_normalize_jobs(board_tokens=board_tokens)
            logger.info(f"Greenhouse Sync: Fetched {len(normalized_jobs)} real normalized opportunities.")

            # Step 2 & 3: Store/Update in Database via store_greenhouse_opportunities
            store_res = await GreenhouseSyncService.store_greenhouse_opportunities(db, normalized_jobs)

            # Step 4: Identify unavailable opportunities and mark as EXPIRED (inactive)
            active_external_ids = {str(j.external_id) for j in normalized_jobs if j.external_id}

            stmt_active_gh = select(Internship).where(
                Internship.source == "Greenhouse",
                Internship.status != "EXPIRED"
            )
            res_active_gh = await db.execute(stmt_active_gh)
            existing_records = res_active_gh.scalars().all()

            expired_count = 0
            for rec in existing_records:
                if rec.external_id and rec.external_id not in active_external_ids:
                    rec.status = "EXPIRED"
                    rec.verification_status = "EXPIRED"
                    rec.last_checked_at = now
                    expired_count += 1

            if expired_count > 0:
                await db.commit()
                logger.info(f"Greenhouse Sync: Marked {expired_count} unavailable opportunities as EXPIRED.")

            # Step 5: Update SourceRegistry entry for Greenhouse
            from app.db.models import SourceRegistry
            stmt_src = select(SourceRegistry).where(SourceRegistry.source_name == "Greenhouse")
            res_src = await db.execute(stmt_src)
            src = res_src.scalar_one_or_none()

            if not src:
                src = SourceRegistry(
                    source_name="Greenhouse",
                    source_url="https://developers.greenhouse.io/job-board.html",
                    source_type="AUTHORIZED_API",
                    authentication_method="NONE",
                    authorization_status="AUTHORIZED",
                    enabled=True,
                    polling_frequency_seconds=21600, # 6 Hours configurable default
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
                f"--- Greenhouse Sync Completed Successfully: "
                f"Fetched={len(normalized_jobs)}, Created={store_res['records_created']}, "
                f"Updated={store_res['records_updated']}, Duplicates={store_res['duplicates_detected']}, "
                f"Expired={expired_count} ---"
            )
            return sync_summary

        except Exception as e:
            logger.error(f"Greenhouse Sync Failure: {str(e)}", exc_info=True)
            return {
                "status": "FAILURE",
                "error": str(e),
                "timestamp": now.isoformat()
            }
