import asyncio
import logging
from datetime import datetime
from app.ingestion.celery_app import celery_app
from app.db.database import AsyncSessionLocal
from app.db.models import SourceRegistry, Internship, IngestionRun, IngestionJob, IngestionError, SourceReference, Skill, InternshipSkill
from app.ingestion.source_connectors import PMISConnector, CompanyCareerConnector, LinkedInAuthorizedConnector, InternshalaAuthorizedConnector, NaukriAuthorizedConnector
from app.ingestion.pipeline import validate_internship_payload, normalize_internship_record, generate_internship_sha256_fingerprint, calculate_internship_quality_score, update_internship_verification_state, run_continuous_expiry_sweep
from app.ingestion.services import trigger_candidate_recommendation_refresh, dispatch_candidate_high_match_notifications
from sqlalchemy import select

logger = logging.getLogger(__name__)

def run_async(coro):
    """Helper to execute async code inside Celery synchronous worker threads."""
    loop = asyncio.get_event_loop()
    if loop.is_running():
        return asyncio.ensure_future(coro)
    return loop.run_until_complete(coro)

@celery_app.task(name="app.ingestion.tasks.run_source_ingestion_task")
def run_source_ingestion_task(source_id: int):
    """
    Celery Task: Executes ingestion pipeline for specified source_id.
    """
    async def _execute():
        async with AsyncSessionLocal() as db:
            src_res = await db.execute(select(SourceRegistry).where(SourceRegistry.id == source_id))
            source = src_res.scalar_one_or_none()
            if not source or not source.enabled:
                logger.info(f"Task skipped: Source ID {source_id} not found or disabled.")
                return {"status": "SKIPPED"}

            # Create IngestionRun Audit Record
            run_rec = IngestionRun(
                source_id=source.id,
                started_at=datetime.utcnow(),
                status="RUNNING"
            )
            db.add(run_rec)
            await db.commit()
            await db.refresh(run_rec)

            # Select connector based on source_type / name
            connector = None
            if "PM Internship" in source.source_name or source.source_type == "OFFICIAL_SCHEME":
                connector = PMISConnector(feed_url=source.source_url)
            elif "Company Career" in source.source_name or source.source_type == "COMPANY_CAREER":
                connector = CompanyCareerConnector(feed_url=source.source_url)
            elif "LinkedIn" in source.source_name:
                connector = LinkedInAuthorizedConnector()
            elif "Internshala" in source.source_name:
                connector = InternshalaAuthorizedConnector()
            elif "Naukri" in source.source_name:
                connector = NaukriAuthorizedConnector()
            else:
                connector = PMISConnector(feed_url=source.source_url)

            if not connector.check_authorization():
                run_rec.status = "COMPLETED"
                run_rec.completed_at = datetime.utcnow()
                db.add(run_rec)
                await db.commit()
                return {"status": "NOT_CONFIGURED", "message": "Connector stub in NOT_CONFIGURED state"}

            try:
                raw_items = await connector.fetch()
                run_rec.records_discovered = len(raw_items)

                for raw in raw_items:
                    is_valid, err_msg = validate_internship_payload(raw)
                    if not is_valid:
                        run_rec.records_rejected += 1
                        db.add(IngestionError(run_id=run_rec.run_id, source_id=source.id, error_type="VALIDATION_ERROR", error_message=err_msg, payload_snapshot=str(raw)[:500]))
                        continue

                    norm = connector.normalize(raw)
                    sha256_fp = generate_internship_sha256_fingerprint(norm["company_name"], norm["title"], norm["location"], norm["application_url"])
                    quality = calculate_internship_quality_score(norm, source.source_confidence)

                    # Query existing internship by sha256_fp or duplicate_fingerprint
                    ex_res = await db.execute(select(Internship).where(
                        (Internship.fingerprint_sha256 == sha256_fp) | (Internship.duplicate_fingerprint == sha256_fp)
                    ))
                    existing = ex_res.scalar_one_or_none()

                    if existing:
                        run_rec.duplicates_detected += 1
                        existing.last_seen_at = datetime.utcnow()
                        existing.last_checked_at = datetime.utcnow()
                        db.add(existing)

                        # Record SourceReference link
                        db.add(SourceReference(internship_id=existing.id, source_id=source.id, source_name=source.source_name, source_url=norm["application_url"], last_seen_at=datetime.utcnow()))
                    else:
                        v_status = update_internship_verification_state("DISCOVERED", quality, auto_verify=True)
                        new_opp = Internship(
                            company_name=norm["company_name"],
                            company_sector=norm["company_sector"],
                            title=norm["title"],
                            description=norm["description"],
                            location=norm["location"],
                            work_mode=norm["work_mode"],
                            duration=norm["duration"],
                            stipend=norm["stipend"],
                            deadline=norm["deadline"],
                            positions=norm["positions"],
                            min_qualification=norm["min_qualification"],
                            preferred_degree=norm["preferred_degree"],
                            min_age=norm["min_age"],
                            max_age=norm["max_age"],
                            source_id=source.id,
                            source_url=norm["application_url"],
                            duplicate_fingerprint=sha256_fp,
                            fingerprint_sha256=sha256_fp,
                            status=v_status,
                            verification_status="VERIFIED" if v_status == "VERIFIED_LIVE" else "PENDING",
                            quality_score=quality,
                            required_education=norm["min_qualification"],
                            first_seen_at=datetime.utcnow(),
                            last_seen_at=datetime.utcnow(),
                            last_verified_at=datetime.utcnow(),
                            posted_date=datetime.utcnow(),
                            last_checked_at=datetime.utcnow(),
                            is_demo=False
                        )
                        db.add(new_opp)
                        await db.flush()

                        run_rec.records_created += 1
                        db.add(SourceReference(internship_id=new_opp.id, source_id=source.id, source_name=source.source_name, source_url=norm["application_url"], last_seen_at=datetime.utcnow()))

                        # Attach skills
                        for req_sk in norm.get("required_skills", []):
                            sk_res = await db.execute(select(Skill).where(Skill.name == req_sk))
                            sk_obj = sk_res.scalar_one_or_none()
                            if not sk_obj:
                                sk_obj = Skill(name=req_sk, category="Ingested")
                                db.add(sk_obj)
                                await db.flush()
                            db.add(InternshipSkill(internship_id=new_opp.id, skill_id=sk_obj.id, is_required=True))

                        # Downstream Integration Trigger: Recommendations & Notifications
                        await trigger_candidate_recommendation_refresh(db, new_opp.id)
                        await dispatch_candidate_high_match_notifications(db, new_opp.id)

                source.last_success_at = datetime.utcnow()
                source.last_run_at = datetime.utcnow()
                source.health_status = "ONLINE"
                db.add(source)

                run_rec.status = "COMPLETED"
                run_rec.completed_at = datetime.utcnow()
                db.add(run_rec)
                await db.commit()

                return {
                    "status": "COMPLETED",
                    "discovered": run_rec.records_discovered,
                    "created": run_rec.records_created,
                    "duplicates": run_rec.duplicates_detected
                }

            except Exception as e:
                source.last_failure_at = datetime.utcnow()
                source.health_status = "FAILED"
                db.add(source)

                run_rec.status = "FAILED"
                run_rec.error_count += 1
                run_rec.completed_at = datetime.utcnow()
                db.add(run_rec)

                db.add(IngestionError(run_id=run_rec.run_id, source_id=source.id, error_type="SERVER_ERROR", error_message=str(e)))
                await db.commit()
                logger.error(f"Task Failed for Source ID {source_id}: {e}")
                return {"status": "FAILED", "error": str(e)}

    return run_async(_execute())

@celery_app.task(name="app.ingestion.tasks.expiry_check_task")
def expiry_check_task():
    """Celery Task: Continuous soft-expiry sweep."""
    async def _execute():
        async with AsyncSessionLocal() as db:
            return await run_continuous_expiry_sweep(db)
    return run_async(_execute())

@celery_app.task(name="app.ingestion.tasks.poll_all_enabled_sources_task")
def poll_all_enabled_sources_task():
    """Celery Task: Polls all enabled ingestion sources."""
    async def _execute():
        async with AsyncSessionLocal() as db:
            src_res = await db.execute(select(SourceRegistry).where(SourceRegistry.enabled == True))
            sources = src_res.scalars().all()
            for src in sources:
                run_source_ingestion_task.delay(src.id)
            return {"polled_sources_count": len(sources)}
    return run_async(_execute())
