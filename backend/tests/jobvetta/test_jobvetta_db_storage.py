import os
import sys
import asyncio
from sqlalchemy import select

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.db.database import AsyncSessionLocal
from app.db.models import Internship
from app.jobvetta.schemas import NormalizedJobvettaJob
from app.jobvetta.sync_service import JobvettaSyncService

async def test_jobvetta_db_persistence_and_deduplication():
    """Tests storing normalized Jobvetta opportunities in PostgreSQL and verifying SHA-256 deduplication."""
    async with AsyncSessionLocal() as db:
        test_job = NormalizedJobvettaJob(
            external_id="test_jv_unique_001",
            title="Backend Python Engineering Intern",
            company="Jobvetta Partner Org",
            description="Build scalable FastAPI microservices and database engines.",
            location="Remote",
            category="Information Technology",
            opportunity_type="INTERNSHIP",
            stipend_str="₹18,000 / month",
            skills=["Python", "FastAPI", "SQL"],
            source="Jobvetta",
            source_url="https://www.jobvetta.com/jobs/test_jv_unique_001",
            apply_url="https://www.jobvetta.com/apply/test_jv_unique_001"
        )

        # 1. Store opportunity
        res = await JobvettaSyncService.store_jobvetta_opportunities(db, [test_job])
        assert res["records_created"] >= 1 or res["records_updated"] >= 1

        # 2. Verify stored DB record
        stmt = select(Internship).where(
            (Internship.source == "Jobvetta") &
            (Internship.external_id == "test_jv_unique_001")
        )
        db_res = await db.execute(stmt)
        record = db_res.scalar_one_or_none()

        assert record is not None
        assert record.title == "Backend Python Engineering Intern"
        assert record.company_name == "Jobvetta Partner Org"
        assert record.apply_url == "https://www.jobvetta.com/apply/test_jv_unique_001"
        assert record.status == "VERIFIED_LIVE"
        assert record.verification_status == "VERIFIED"

        # 3. Test Deduplication: Re-running store should update, not duplicate
        res_dup = await JobvettaSyncService.store_jobvetta_opportunities(db, [test_job])
        assert res_dup["records_created"] == 0
        assert res_dup["records_updated"] >= 1
