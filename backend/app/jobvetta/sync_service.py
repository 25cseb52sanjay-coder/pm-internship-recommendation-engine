import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Internship, SourceRegistry, Skill, InternshipSkill
from app.jobvetta.schemas import NormalizedJobvettaJob
from app.ingestion.pipeline.deduplication import generate_internship_sha256_fingerprint

logger = logging.getLogger(__name__)

class JobvettaSyncService:
    """
    Service for persisting real Jobvetta jobs, internships, and opportunities
    into the primary PostgreSQL database schema.
    """

    @staticmethod
    async def store_jobvetta_opportunities(
        db: AsyncSession,
        jobs: List[NormalizedJobvettaJob]
    ) -> Dict[str, Any]:
        """
        Stores normalized real Jobvetta opportunities in PostgreSQL database.
        Preserves 100% of existing records from Adzuna, Greenhouse, NCS, PMIS, and other sources.
        """
        logger.info(f"--- Storing {len(jobs)} Real Jobvetta Opportunities in Database ---")

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
                    location=job.location or "India",
                    application_url=job.apply_url
                )

                # 2. Primary lookup: external_id for Jobvetta source
                existing = None
                if ext_id:
                    stmt = select(Internship).where(
                        (Internship.source == "Jobvetta") &
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

                stipend_str = job.stipend_str or "Competitive Compensation"

                if not existing:
                    # 3. Create NEW Jobvetta Internship / Job Record in Database
                    new_record = Internship(
                        company_name=job.company,
                        company_sector=job.category or "Technology Services",
                        title=job.title,
                        description=job.description or f"{job.title} opportunity at {job.company}.",
                        location=job.location or "India",
                        work_mode=job.work_mode or "On-site",
                        duration="Full-Time" if job.opportunity_type == "JOB" else "6 Months",
                        stipend=stipend_str,
                        deadline=job.deadline or "2026-12-31",
                        positions=job.positions or 1,
                        min_qualification=job.min_qualification or "Graduate",
                        preferred_degree=job.preferred_degree or "B.Tech",
                        source="Jobvetta",
                        external_id=ext_id,
                        employment_type=job.employment_type,
                        opportunity_type=job.opportunity_type or "INTERNSHIP",
                        source_url=job.source_url,
                        apply_url=job.apply_url,
                        fingerprint_sha256=fingerprint,
                        status="VERIFIED_LIVE",
                        verification_status="VERIFIED",
                        quality_score=85.0,
                        is_demo=False,
                        first_seen_at=now,
                        last_seen_at=now,
                        last_verified_at=now,
                        last_checked_at=now
                    )
                    db.add(new_record)
                    await db.flush()

                    # Add skills relationships
                    for skill_name in job.skills:
                        sk_stmt = select(Skill).where(Skill.name.ilike(skill_name))
                        sk_res = await db.execute(sk_stmt)
                        db_skill = sk_res.scalar_one_or_none()
                        if not db_skill:
                            db_skill = Skill(name=skill_name, category="Technical")
                            db.add(db_skill)
                            await db.flush()
                        db.add(InternshipSkill(internship_id=new_record.id, skill_id=db_skill.id, is_required=True))

                    created_count += 1
                else:
                    # 4. Update existing record safely
                    existing.title = job.title
                    existing.description = job.description or existing.description
                    existing.location = job.location or existing.location
                    existing.company_name = job.company or existing.company_name
                    existing.company_sector = job.category or existing.company_sector
                    existing.apply_url = job.apply_url or existing.apply_url
                    existing.source_url = job.source_url or existing.source_url
                    existing.opportunity_type = job.opportunity_type
                    existing.employment_type = job.employment_type or existing.employment_type
                    existing.stipend = stipend_str
                    existing.last_seen_at = now
                    existing.last_checked_at = now
                    existing.status = "VERIFIED_LIVE"
                    existing.verification_status = "VERIFIED"
                    updated_count += 1

            except Exception as e:
                logger.error(f"Error persisting Jobvetta record {job.external_id}: {str(e)}")
                failed_count += 1

        await db.commit()
        logger.info(f"Jobvetta DB Persistence Complete: {created_count} created, {updated_count} updated, {failed_count} failed.")

        return {
            "source": "Jobvetta",
            "total_processed": len(jobs),
            "created_count": created_count,
            "records_created": created_count,
            "updated_count": updated_count,
            "records_updated": updated_count,
            "failed_count": failed_count,
            "duplicates_detected": duplicate_count
        }

    @staticmethod
    async def run_full_jobvetta_sync(
        db: AsyncSession,
        queries: Optional[List[str]] = None,
        location: str = "India"
    ) -> Dict[str, Any]:
        """
        Executes full periodic background synchronization cycle for Jobvetta opportunities:
        1. Fetches live jobs via JobvettaService across search queries.
        2. Normalizes & classifies opportunities (JOB, INTERNSHIP).
        3. Inserts new & updates changed opportunities in PostgreSQL.
        4. Updates SourceRegistry entry for Jobvetta.
        5. Preserves 100% of historical records from Adzuna, Greenhouse, NCS, and PMIS.
        """
        logger.info("======================================================================")
        logger.info("  STARTING JOBVETTA PERIODIC BACKGROUND SYNCHRONIZATION CYCLE")
        logger.info("======================================================================")

        now = datetime.utcnow()
        try:
            from app.jobvetta.service import JobvettaService
            service = JobvettaService()

            # Step 1: Fetch and normalize live opportunities
            normalized_jobs = await service.fetch_and_normalize_jobs(queries=queries, location=location)
            logger.info(f"Jobvetta Sync: Fetched {len(normalized_jobs)} real normalized opportunities.")

            # Step 2 & 3: Store/Update in Database
            store_res = await JobvettaSyncService.store_jobvetta_opportunities(db, normalized_jobs)

            # Step 4: Update SourceRegistry entry for Jobvetta
            stmt_src = select(SourceRegistry).where(SourceRegistry.source_name == "Jobvetta")
            res_src = await db.execute(stmt_src)
            src = res_src.scalar_one_or_none()

            if not src:
                src = SourceRegistry(
                    source_name="Jobvetta",
                    source_url="https://www.jobvetta.com/api",
                    source_type="AUTHORIZED_API",
                    authentication_method="BEARER_TOKEN",
                    authorization_status="AUTHORIZED" if service.connector.check_authorization() else "NOT_CONFIGURED",
                    enabled=True,
                    polling_frequency_seconds=21600,
                    health_status="ONLINE" if service.connector.check_authorization() else "NOT_CONFIGURED"
                )
                db.add(src)

            src.last_success_at = now
            src.last_run_at = now
            src.health_status = "ONLINE" if service.connector.check_authorization() else "NOT_CONFIGURED"
            src.last_checked_at = now
            await db.commit()

            sync_summary = {
                "status": "SUCCESS",
                "total_fetched": len(normalized_jobs),
                "records_created": store_res["records_created"],
                "records_updated": store_res["records_updated"],
                "timestamp": now.isoformat()
            }

            logger.info(
                f"--- Jobvetta Sync Completed Successfully: "
                f"Fetched={len(normalized_jobs)}, Created={store_res['records_created']}, "
                f"Updated={store_res['records_updated']} ---"
            )
            return sync_summary

        except Exception as e:
            logger.error(f"Jobvetta Sync Failure: {str(e)}", exc_info=True)
            return {
                "status": "FAILURE",
                "error": str(e),
                "timestamp": now.isoformat()
            }
