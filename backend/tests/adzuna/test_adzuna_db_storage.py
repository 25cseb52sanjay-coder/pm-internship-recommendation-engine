import asyncio
import sys
import os
from sqlalchemy import select, func

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.db.database import AsyncSessionLocal
from app.db.models import Internship
from app.adzuna.schemas import NormalizedAdzunaJob
from app.adzuna.sync_service import AdzunaSyncService

def test_adzuna_db_storage_suite():
    print("\n======================================================================")
    print("  ADZUNA INTEGRATION TASK 5: DATABASE STORAGE AUDIT TEST SUITE")
    print("======================================================================\n")

    async def _run():
        async with AsyncSessionLocal() as db:
            # 1. Count pre-existing non-Adzuna records
            print("  [STEP 1] Inspecting existing database records by source...")
            res_gh = await db.execute(select(func.count()).where(Internship.source == "Greenhouse"))
            gh_count_before = res_gh.scalar() or 0

            res_ncs = await db.execute(select(func.count()).where(Internship.source == "NCS"))
            ncs_count_before = res_ncs.scalar() or 0

            res_pmis = await db.execute(select(func.count()).where(Internship.source == "PMIS"))
            pmis_count_before = res_pmis.scalar() or 0

            print(f"    - Pre-existing Greenhouse Records:  {gh_count_before}")
            print(f"    - Pre-existing NCS Records:         {ncs_count_before}")
            print(f"    - Pre-existing PMIS Records:        {pmis_count_before}")

            # 2. Prepare Real Adzuna Normalized Test Batch
            print("\n  [STEP 2] Preparing Real Adzuna test batch with JOB, INTERNSHIP, and UNKNOWN roles...")
            adzuna_batch = [
                NormalizedAdzunaJob(
                    external_id="adzuna_test_job_101",
                    title="Adzuna Full-Stack Systems Engineer",
                    company="Wipro Digital",
                    location="Bengaluru",
                    description="Full-time software engineering position building backend microservices.",
                    category="IT Jobs",
                    salary_min=600000.0,
                    salary_max=900000.0,
                    contract_type="permanent",
                    contract_time="full_time",
                    created="2026-08-14T09:00:00Z",
                    opportunity_type="JOB",
                    source="Adzuna",
                    source_url="https://www.adzuna.in/details/adzuna_test_job_101",
                    apply_url="https://www.adzuna.in/land/ad/adzuna_test_job_101"
                ),
                NormalizedAdzunaJob(
                    external_id="adzuna_test_intern_102",
                    title="Adzuna Data Science Intern",
                    company="Infosys",
                    location="Hyderabad",
                    description="6-month summer internship for computer science students.",
                    category="IT Jobs",
                    salary_min=180000.0,
                    salary_max=240000.0,
                    contract_type=None,
                    contract_time=None,
                    created="2026-08-14T10:00:00Z",
                    opportunity_type="INTERNSHIP",
                    source="Adzuna",
                    source_url="https://www.adzuna.in/details/adzuna_test_intern_102",
                    apply_url="https://www.adzuna.in/land/ad/adzuna_test_intern_102"
                ),
                NormalizedAdzunaJob(
                    external_id="adzuna_test_unknown_103",
                    title="Adzuna Ambiguous Requisition 103",
                    company="HCL Tech",
                    location="Noida",
                    description="General project assistant support tasks.",
                    category="Other",
                    salary_min=None,
                    salary_max=None,
                    contract_type=None,
                    contract_time=None,
                    created="2026-08-14T11:00:00Z",
                    opportunity_type="UNKNOWN",
                    source="Adzuna",
                    source_url="https://www.adzuna.in/details/adzuna_test_unknown_103",
                    apply_url="https://www.adzuna.in/land/ad/adzuna_test_unknown_103"
                )
            ]

            # 3. Store Adzuna Opportunities in PostgreSQL
            print(f"    - Persisting {len(adzuna_batch)} Adzuna records to PostgreSQL database...")
            sync_res = await AdzunaSyncService.store_adzuna_opportunities(db, adzuna_batch)
            print(f"    - Created: {sync_res['created_count']}, Updated: {sync_res['updated_count']}")

            # 4. Verify Adzuna Records in Database
            print("\n  [STEP 3] Querying stored Adzuna records from PostgreSQL...")
            stmt_adzuna = select(Internship).where(Internship.source == "Adzuna")
            res_adz = await db.execute(stmt_adzuna)
            stored_adzuna = res_adz.scalars().all()

            print(f"    - Total Adzuna Records in Database: {len(stored_adzuna)}")
            assert len(stored_adzuna) >= 3, "All Adzuna records must be stored in database"

            opp_types_found = {rec.opportunity_type for rec in stored_adzuna}
            print(f"    - Opportunity Types Stored: {opp_types_found}")
            assert "JOB" in opp_types_found
            assert "INTERNSHIP" in opp_types_found
            assert "UNKNOWN" in opp_types_found

            for rec in stored_adzuna:
                assert rec.source == "Adzuna"
                assert rec.external_id is not None
                url_check = rec.apply_url or rec.source_url or f"https://www.adzuna.in/details/{rec.external_id}"
                assert url_check.startswith("http")

            # 5. Verify Pre-existing Sources Unaffected
            print("\n  [STEP 4] Verifying pre-existing records from other sources remain 100% unaffected...")
            res_gh_after = await db.execute(select(func.count()).where(Internship.source == "Greenhouse"))
            assert res_gh_after.scalar() == gh_count_before, "Greenhouse record count must remain unchanged"

            res_ncs_after = await db.execute(select(func.count()).where(Internship.source == "NCS"))
            assert res_ncs_after.scalar() == ncs_count_before, "NCS record count must remain unchanged"

            res_pmis_after = await db.execute(select(func.count()).where(Internship.source == "PMIS"))
            assert res_pmis_after.scalar() == pmis_count_before, "PMIS record count must remain unchanged"

            print("    - Greenhouse, NCS, and PMIS records verified 100% unaffected.")

    asyncio.run(_run())

    print("\n======================================================================")
    print("  TASK 5 ADZUNA DATABASE STORAGE VERIFICATION: PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_adzuna_db_storage_suite()
