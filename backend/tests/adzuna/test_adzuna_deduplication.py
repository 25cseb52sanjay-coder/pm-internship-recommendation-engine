import asyncio
import sys
import os
from uuid import uuid4
from sqlalchemy import select, func

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.db.database import AsyncSessionLocal
from app.db.models import Internship
from app.adzuna.schemas import NormalizedAdzunaJob
from app.adzuna.sync_service import AdzunaSyncService

def test_adzuna_deduplication_suite():
    print("\n======================================================================")
    print("  ADZUNA INTEGRATION TASK 8: DEDUPLICATION & UPDATES AUDIT TEST SUITE")
    print("======================================================================\n")

    async def _run():
        async with AsyncSessionLocal() as db:
            # 1. Prepare Unique Test Requisitions
            unique_suffix = uuid4().hex[:8]
            test_id_1 = f"adzuna_dedup_test_{unique_suffix}_801"
            test_id_2 = f"adzuna_dedup_test_{unique_suffix}_802"

            batch_initial = [
                NormalizedAdzunaJob(
                    external_id=test_id_1,
                    title="Adzuna Initial Software Intern Title",
                    company="Wipro Initial Company",
                    location="Bengaluru",
                    description="Initial description text for requisition 801.",
                    category="IT Jobs",
                    salary_min=300000.0,
                    salary_max=450000.0,
                    contract_type="permanent",
                    contract_time="full_time",
                    created="2026-08-14T08:00:00Z",
                    opportunity_type="INTERNSHIP",
                    source="Adzuna",
                    source_url=f"https://www.adzuna.in/details/{test_id_1}",
                    apply_url=f"https://www.adzuna.in/land/ad/{test_id_1}?v=1"
                ),
                NormalizedAdzunaJob(
                    external_id=test_id_2,
                    title="Adzuna Initial Full-Time Developer",
                    company="Infosys Initial Company",
                    location="Hyderabad",
                    description="Initial description text for requisition 802.",
                    category="IT Jobs",
                    salary_min=700000.0,
                    salary_max=1000000.0,
                    contract_type="permanent",
                    contract_time="full_time",
                    created="2026-08-14T08:30:00Z",
                    opportunity_type="JOB",
                    source="Adzuna",
                    source_url=f"https://www.adzuna.in/details/{test_id_2}",
                    apply_url=f"https://www.adzuna.in/land/ad/{test_id_2}?v=1"
                )
            ]

            # 2. Run #1: Initial Sync Execution
            print("  [STEP 1] Executing Sync Run #1 (Initial Requisition Insertion)...")
            res_run1 = await AdzunaSyncService.store_adzuna_opportunities(db, batch_initial)
            print(f"    - Run 1 Results: Created={res_run1['created_count']}, Updated={res_run1['updated_count']}")

            assert res_run1["created_count"] >= 2, "Must create 2 new records on initial run"

            stmt1 = select(Internship).where(
                (Internship.source == "Adzuna") & 
                (Internship.external_id.in_([test_id_1, test_id_2]))
            )
            count1 = len((await db.execute(stmt1)).scalars().all())
            print(f"    - Database Record Count for Requisitions: {count1}")
            assert count1 == 2

            # 3. Run #2: Modified Requisitions Sync Execution (Test In-Place Updates)
            print("\n  [STEP 2] Executing Sync Run #2 with updated title, location, salary, and apply_url...")
            batch_updated = [
                NormalizedAdzunaJob(
                    external_id=test_id_1,
                    title="Adzuna UPDATED Software Intern Title (v2)",
                    company="Wipro Digital Technologies",
                    location="Bengaluru, Karnataka (Remote)",
                    description="UPDATED description text for requisition 801 with 2026 requirements.",
                    category="Software & Technology",
                    salary_min=350000.0,
                    salary_max=500000.0,
                    contract_type="contract",
                    contract_time="full_time",
                    created="2026-08-14T08:00:00Z",
                    opportunity_type="INTERNSHIP",
                    source="Adzuna",
                    source_url=f"https://www.adzuna.in/details/{test_id_1}",
                    apply_url=f"https://www.adzuna.in/land/ad/{test_id_1}?v=UPDATED_2"
                ),
                NormalizedAdzunaJob(
                    external_id=test_id_2,
                    title="Adzuna UPDATED Senior Staff Developer (v2)",
                    company="Infosys Enterprise Solutions",
                    location="Hyderabad / Remote",
                    description="UPDATED description text for requisition 802 with 2026 requirements.",
                    category="Software & Technology",
                    salary_min=850000.0,
                    salary_max=1200000.0,
                    contract_type="permanent",
                    contract_time="full_time",
                    created="2026-08-14T08:30:00Z",
                    opportunity_type="JOB",
                    source="Adzuna",
                    source_url=f"https://www.adzuna.in/details/{test_id_2}",
                    apply_url=f"https://www.adzuna.in/land/ad/{test_id_2}?v=UPDATED_2"
                )
            ]

            res_run2 = await AdzunaSyncService.store_adzuna_opportunities(db, batch_updated)
            print(f"    - Run 2 Results: Created={res_run2['created_count']}, Updated={res_run2['updated_count']}")

            assert res_run2["created_count"] == 0, "Repeated sync must NOT create duplicate records (Created must be 0)"
            assert res_run2["updated_count"] == 2, "Existing records must be updated in-place (Updated must be 2)"

            # 4. Verify Field Updates & Zero Duplicates
            print("\n  [STEP 3] Verifying in-place field updates and zero duplicate generation...")
            stmt2 = select(Internship).where(
                (Internship.source == "Adzuna") & 
                (Internship.external_id.in_([test_id_1, test_id_2]))
            )
            records_run2 = (await db.execute(stmt2)).scalars().all()
            assert len(records_run2) == 2, "Must remain exactly 2 records in database without duplication"

            for rec in records_run2:
                if rec.external_id == test_id_1:
                    print(f"    - Record 801 Title Updated: '{rec.title}'")
                    print(f"    - Record 801 Apply URL:     '{rec.apply_url}'")
                    assert rec.title == "Adzuna UPDATED Software Intern Title (v2)"
                    assert "UPDATED_2" in rec.apply_url
                elif rec.external_id == test_id_2:
                    print(f"    - Record 802 Title Updated: '{rec.title}'")
                    print(f"    - Record 802 Apply URL:     '{rec.apply_url}'")
                    assert rec.title == "Adzuna UPDATED Senior Staff Developer (v2)"
                    assert "UPDATED_2" in rec.apply_url

            # 5. Run #3: Idempotency Re-execution Audit
            print("\n  [STEP 4] Executing Sync Run #3 (Idempotency Re-Execution Audit)...")
            res_run3 = await AdzunaSyncService.store_adzuna_opportunities(db, batch_updated)
            print(f"    - Run 3 Results: Created={res_run3['created_count']}, Updated={res_run3['updated_count']}")

            assert res_run3["created_count"] == 0, "Idempotent re-run must create 0 new records"

            print("\n======================================================================")
            print("  TASK 8 ADZUNA DEDUPLICATION VERIFICATION: PASSED (100% SUCCESS)")
            print("======================================================================\n")

    asyncio.run(_run())

if __name__ == "__main__":
    test_adzuna_deduplication_suite()
