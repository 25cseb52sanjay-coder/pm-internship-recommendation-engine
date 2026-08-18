import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.ncs.schemas import NCSInternshipSchema
from app.ncs.service import NCSService
from app.db.models import Internship, IngestionRun, IngestionJob
from app.ingestion.pipeline.deduplication import generate_internship_sha256_fingerprint
from app.ingestion.pipeline.quality_score import calculate_internship_quality_score

logger = logging.getLogger(__name__)

class NCSSyncService:
    """
    Background Synchronization Service for National Career Service (NCS) Internships.
    Handles fetching, deduplication, field updates, and expiry management.
    """

    @staticmethod
    async def process_ncs_batch(db: AsyncSession, ncs_items: List[NCSInternshipSchema]) -> Dict[str, Any]:
        """
        Processes a batch of NCSInternshipSchema records.
        Idempotent: Identifies new, updated, duplicate, and expired opportunities.
        Never deletes existing database records blindly.
        """
        logger.info(f"--- Starting NCS Synchronization Batch ({len(ncs_items)} items) ---")
        
        created_count = 0
        updated_count = 0
        duplicate_count = 0
        expired_count = 0
        failed_count = 0

        now = datetime.utcnow()

        for item in ncs_items:
            try:
                # 1. Generate SHA-256 fingerprint for deduplication
                fingerprint = generate_internship_sha256_fingerprint(
                    company_name=item.company,
                    title=item.title,
                    location=item.location,
                    application_url=item.apply_url
                )

                # 2. Check existing record by fingerprint or apply_url
                res = await db.execute(
                    select(Internship).where(
                        (Internship.fingerprint_sha256 == fingerprint) |
                        (Internship.apply_url == item.apply_url)
                    )
                )
                existing = res.scalar_one_or_none()

                # 3. Check if payload indicates expired status or deadline passed
                is_expired = item.status.lower() == "expired"
                if item.deadline:
                    try:
                        deadline_dt = datetime.strptime(item.deadline, "%Y-%m-%d")
                        if deadline_dt < now:
                            is_expired = True
                    except ValueError:
                        pass

                if not existing:
                    # NEW RECORD: Create and persist
                    model_dict = NCSService.map_ncs_schema_to_internship_model(item)
                    q_score = calculate_internship_quality_score(model_dict, 1.0)
                    
                    new_internship = Internship(
                        company_name=model_dict["company_name"],
                        company_sector=model_dict["company_sector"],
                        title=model_dict["title"],
                        description=model_dict["description"],
                        location=model_dict["location"],
                        work_mode=model_dict["work_mode"],
                        duration=model_dict["duration"],
                        stipend=model_dict["stipend"],
                        deadline=model_dict["deadline"],
                        min_qualification=model_dict["min_qualification"],
                        source="NCS",
                        source_url="https://www.ncs.gov.in/internships-jobs",
                        apply_url=item.apply_url,
                        fingerprint_sha256=fingerprint,
                        status="EXPIRED" if is_expired else "VERIFIED_LIVE",
                        verification_status="VERIFIED" if item.status == "active" else "PENDING_VERIFICATION",
                        quality_score=q_score,
                        is_demo=False,
                        first_seen_at=now,
                        last_seen_at=now,
                        last_verified_at=now
                    )
                    db.add(new_internship)
                    created_count += 1
                    logger.info(f"NCS Sync: Created new internship '{item.title}' at '{item.company}'.")

                else:
                    # EXISTING RECORD: Check for updates vs duplicates vs expiry
                    has_changes = False

                    if is_expired and existing.status != "EXPIRED":
                        existing.status = "EXPIRED"
                        expired_count += 1
                        has_changes = True
                        logger.info(f"NCS Sync: Marked internship ID {existing.id} as EXPIRED.")

                    if item.stipend and item.stipend != existing.stipend:
                        existing.stipend = item.stipend
                        has_changes = True

                    if item.deadline and item.deadline != existing.deadline:
                        existing.deadline = item.deadline
                        has_changes = True

                    if item.description and item.description != existing.description:
                        existing.description = item.description
                        has_changes = True

                    existing.last_seen_at = now

                    if has_changes:
                        updated_count += 1
                        logger.info(f"NCS Sync: Updated internship ID {existing.id} ('{item.title}').")
                    else:
                        duplicate_count += 1
                        logger.info(f"NCS Sync: Duplicate identified for internship ID {existing.id} (Unchanged).")

            except Exception as e:
                failed_count += 1
                logger.error(f"NCS Sync Failure on item '{item.title}': {str(e)}")

        await db.commit()

        summary = {
            "status": "SUCCESS" if failed_count == 0 else "PARTIAL_SUCCESS",
            "total_processed": len(ncs_items),
            "records_created": created_count,
            "records_updated": updated_count,
            "duplicates_detected": duplicate_count,
            "records_expired": expired_count,
            "records_failed": failed_count,
            "timestamp": now.isoformat()
        }

        logger.info(
            f"--- NCS Synchronization Batch Complete: "
            f"Created={created_count}, Updated={updated_count}, Duplicates={duplicate_count}, Expired={expired_count}, Failed={failed_count} ---"
        )
        return summary
