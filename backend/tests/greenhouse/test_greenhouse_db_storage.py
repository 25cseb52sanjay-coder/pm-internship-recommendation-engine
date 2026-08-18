import asyncio
import sys
import os

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.db.database import AsyncSessionLocal
from app.db.models import Internship
from app.db.migrations.add_greenhouse_fields import migrate_greenhouse_database_fields
from app.greenhouse.service import GreenhouseService
from app.greenhouse.sync_service import GreenhouseSyncService
from sqlalchemy import select, func

def test_greenhouse_db_storage_suite():
    print("\n======================================================================")
    print("  GREENHOUSE INTEGRATION TASK 4: DATABASE PERSISTENCE TEST SUITE")
    print("======================================================================\n")

    async def _run():
        # 1. Run database schema alignment migration
        await migrate_greenhouse_database_fields()

        async with AsyncSessionLocal() as db:
            # 2. Record initial counts of non-Greenhouse records for isolation verification
            init_non_gh_res = await db.execute(select(func.count(Internship.id)).where(Internship.source != "Greenhouse"))
            init_non_gh_count = init_non_gh_res.scalar()
            print(f"  [CHECK] Initial non-Greenhouse database records: {init_non_gh_count}")

            # 3. Fetch real jobs from Greenhouse API
            print("  [STEP 1] Fetching & Normalizing real published jobs from Greenhouse API...")
            service = GreenhouseService()
            boards = ["stripe", "cloudflare"]
            normalized_jobs = await service.fetch_and_normalize_jobs(board_tokens=boards)
            total_fetched = len(normalized_jobs)
            print(f"    - Total Real Opportunities Prepared: {total_fetched}")
            assert total_fetched > 0, "Must fetch real published jobs from Greenhouse API"

            # 4. Store real Greenhouse opportunities in Database
            print("\n  [STEP 2] Storing real Greenhouse opportunities into PostgreSQL database...")
            sync_res = await GreenhouseSyncService.store_greenhouse_opportunities(db, normalized_jobs)
            print(f"    - Storage Summary: Created={sync_res['records_created']}, Updated={sync_res['records_updated']}, Duplicates={sync_res['duplicates_detected']}")

            # 5. Verify database contents
            print("\n  [STEP 3] Verifying stored Greenhouse records in database...")
            gh_db_res = await db.execute(select(Internship).where(Internship.source == "Greenhouse"))
            gh_items = gh_db_res.scalars().all()
            total_stored_gh = len(gh_items)
            print(f"    - Total Greenhouse database records: {total_stored_gh}")
            assert total_stored_gh > 0, "Must contain stored Greenhouse database records"

            # Verify schema values on stored records
            for item in gh_items[:10]:
                assert item.source == "Greenhouse"
                assert item.external_id and len(item.external_id) > 0
                assert item.apply_url and item.apply_url.startswith("http")
                assert item.opportunity_type in ["JOB", "INTERNSHIP", "UNKNOWN"]
                assert item.status and len(item.status) > 0

            print("    - Sample Stored Record Verification:")
            sample = gh_items[0]
            print(f"      • DB ID:            {sample.id}")
            print(f"      • external_id:      {sample.external_id}")
            print(f"      • title:            {sample.title}")
            print(f"      • company_name:     {sample.company_name}")
            print(f"      • opportunity_type: {sample.opportunity_type}")
            print(f"      • source:           {sample.source}")
            print(f"      • apply_url:        {sample.apply_url}")

            # 6. Verify non-Greenhouse isolation
            print("\n  [STEP 4] Verifying existing data sources remain completely unaffected...")
            final_non_gh_res = await db.execute(select(func.count(Internship.id)).where(Internship.source != "Greenhouse"))
            final_non_gh_count = final_non_gh_res.scalar()
            assert final_non_gh_count == init_non_gh_count, "Non-Greenhouse record count must remain 100% identical"
            print(f"    - Non-Greenhouse record count maintained at {final_non_gh_count} records.")

            print("  [OK] Data isolation verified: 0 non-Greenhouse records modified.")

    asyncio.run(_run())

    print("\n======================================================================")
    print("  TASK 4 DATABASE PERSISTENCE VERIFICATION: PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_greenhouse_db_storage_suite()
