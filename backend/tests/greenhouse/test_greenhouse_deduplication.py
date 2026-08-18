import asyncio
import sys
import os

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.db.database import AsyncSessionLocal
from app.db.models import Internship
from app.greenhouse.schemas import NormalizedGreenhouseJob
from app.greenhouse.sync_service import GreenhouseSyncService
from sqlalchemy import select, func

def test_greenhouse_deduplication_suite():
    print("\n======================================================================")
    print("  GREENHOUSE INTEGRATION TASK 7: DEDUPLICATION & UPDATES TEST SUITE")
    print("======================================================================\n")

    async def _run():
        async with AsyncSessionLocal() as db:
            # Prepare mock/sample Greenhouse jobs with external_id
            sample_jobs = [
                NormalizedGreenhouseJob(
                    external_id="GH_TEST_9901",
                    title="Software Engineer, Intern (Test Requisition)",
                    company="Stripe Test",
                    location="San Francisco, CA / Remote",
                    description="Real time internship role for software engineering students.",
                    source="Greenhouse",
                    source_url="https://stripe.com/jobs/search?gh_jid=GH_TEST_9901",
                    apply_url="https://stripe.com/jobs/search?gh_jid=GH_TEST_9901",
                    status="active",
                    opportunity_type="INTERNSHIP"
                ),
                NormalizedGreenhouseJob(
                    external_id="GH_TEST_9902",
                    title="Senior Backend Engineer (Test Requisition)",
                    company="Cloudflare Test",
                    location="Austin, TX",
                    description="Real time engineering role for backend infrastructure.",
                    source="Greenhouse",
                    source_url="https://cloudflare.com/jobs/search?gh_jid=GH_TEST_9902",
                    apply_url="https://cloudflare.com/jobs/search?gh_jid=GH_TEST_9902",
                    status="active",
                    opportunity_type="JOB"
                )
            ]

            # 1. Initial Sync Pass
            print("  [STEP 1] Running Pass 1 Sync with 2 Requisitions...")
            res1 = await GreenhouseSyncService.store_greenhouse_opportunities(db, sample_jobs)
            print(f"    - Pass 1 Results: Created={res1['records_created']}, Updated={res1['records_updated']}, Duplicates={res1['duplicates_detected']}")
            assert res1["records_created"] == 2

            # Query count of test records in DB
            count_res1 = await db.execute(select(func.count(Internship.id)).where(Internship.external_id.in_(["GH_TEST_9901", "GH_TEST_9902"])))
            c1 = count_res1.scalar()
            assert c1 == 2, "Must store 2 records in database"

            # 2. Repeated Sync Pass (Identical Data)
            print("\n  [STEP 2] Running Pass 2 Repeated Sync (Identical Data)...")
            res2 = await GreenhouseSyncService.store_greenhouse_opportunities(db, sample_jobs)
            print(f"    - Pass 2 Results: Created={res2['records_created']}, Updated={res2['records_updated']}, Duplicates={res2['duplicates_detected']}")
            assert res2["records_created"] == 0, "Repeated sync must create 0 new records"
            assert res2["duplicates_detected"] == 2, "Repeated sync must detect 2 duplicates"

            count_res2 = await db.execute(select(func.count(Internship.id)).where(Internship.external_id.in_(["GH_TEST_9901", "GH_TEST_9902"])))
            c2 = count_res2.scalar()
            assert c2 == 2, "Database record count must remain exactly 2 (Zero duplicate rows)"

            # 3. Field Update Sync Pass (Changed Title and Location)
            print("\n  [STEP 3] Running Pass 3 Sync with Updated Fields (Title & Location changed)...")
            updated_jobs = [
                NormalizedGreenhouseJob(
                    external_id="GH_TEST_9901",
                    title="Software Engineer, Intern (UPDATED TITLE)",
                    company="Stripe Test",
                    location="New York, NY / Remote",
                    description="Real time internship role for software engineering students.",
                    source="Greenhouse",
                    source_url="https://stripe.com/jobs/search?gh_jid=GH_TEST_9901",
                    apply_url="https://stripe.com/jobs/search?gh_jid=GH_TEST_9901",
                    status="active",
                    opportunity_type="INTERNSHIP"
                ),
                sample_jobs[1] # Unchanged
            ]
            res3 = await GreenhouseSyncService.store_greenhouse_opportunities(db, updated_jobs)
            print(f"    - Pass 3 Results: Created={res3['records_created']}, Updated={res3['records_updated']}, Duplicates={res3['duplicates_detected']}")
            assert res3["records_created"] == 0
            assert res3["records_updated"] == 1
            assert res3["duplicates_detected"] == 1

            # Verify record updated in DB
            db_item_res = await db.execute(select(Internship).where(Internship.external_id == "GH_TEST_9901"))
            db_item = db_item_res.scalar_one()
            assert db_item.title == "Software Engineer, Intern (UPDATED TITLE)"
            assert db_item.location == "New York, NY / Remote"
            print("    - Successfully updated existing DB record fields in place.")

            # Clean up test requisitions
            await db.delete(db_item)
            db_item2_res = await db.execute(select(Internship).where(Internship.external_id == "GH_TEST_9902"))
            db_item2 = db_item2_res.scalar_one_or_none()
            if db_item2:
                await db.delete(db_item2)
            await db.commit()

    asyncio.run(_run())

    print("\n======================================================================")
    print("  TASK 7 DEDUPLICATION & UPDATE VERIFICATION: PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_greenhouse_deduplication_suite()
