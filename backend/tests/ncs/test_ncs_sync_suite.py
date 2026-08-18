import asyncio
import sys
import os

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.db.database import AsyncSessionLocal
from app.db.models import Internship
from app.ncs.schemas import NCSInternshipSchema
from app.ncs.sync_service import NCSSyncService
from sqlalchemy import select, delete

def test_ncs_sync_lifecycle():
    print("\n======================================================================")
    print("  NCS BACKGROUND SYNCHRONIZATION LIFECYCLE TEST SUITE")
    print("======================================================================\n")

    async def _run_tests():
        async with AsyncSessionLocal() as db:
            # Cleanup any existing test NCS records first
            await db.execute(delete(Internship).where(Internship.source == "NCS"))
            await db.commit()

            # Item 1 & 2 definition
            item1 = NCSInternshipSchema(
                source="NCS",
                title="Public Policy & Data Analytics Intern",
                company="Ministry of Labour & Employment",
                location="New Delhi",
                skills=["Python", "Data Analysis", "SQL"],
                eligibility="B.Tech / B.Sc Graduate",
                stipend="₹12,000 / month",
                duration="6 Months",
                deadline="2026-12-31",
                description="Analyze national employment trends and build statistical monitoring dashboards.",
                apply_url="https://www.ncs.gov.in/internships/policy-data-01",
                status="active"
            )

            item2 = NCSInternshipSchema(
                source="NCS",
                title="Geospatial GIS Data Trainee",
                company="National Remote Sensing Centre (NRSC)",
                location="Hyderabad",
                skills=["GIS", "Python", "Remote Sensing"],
                eligibility="Graduate",
                stipend="₹14,000 / month",
                duration="6 Months",
                deadline="2026-11-30",
                description="Process satellite GIS rasters and geospatial vector layers.",
                apply_url="https://www.ncs.gov.in/internships/gis-trainee-02",
                status="active"
            )

            # TEST 1: Process New Records
            print("  [TEST 1] Processing batch with 2 NEW NCS records...")
            s1 = await NCSSyncService.process_ncs_batch(db, [item1, item2])
            print(f"    - Summary: Created={s1['records_created']}, Updated={s1['records_updated']}, Duplicates={s1['duplicates_detected']}")
            assert s1["records_created"] == 2, "Must create 2 new records"
            assert s1["duplicates_detected"] == 0
            print("  [OK] TEST 1 PASSED: 2 new NCS records successfully persisted.")

            # TEST 2: Process Duplicate Batch
            print("\n  [TEST 2] Processing identical batch (Duplicate Detection)...")
            s2 = await NCSSyncService.process_ncs_batch(db, [item1, item2])
            print(f"    - Summary: Created={s2['records_created']}, Updated={s2['records_updated']}, Duplicates={s2['duplicates_detected']}")
            assert s2["records_created"] == 0, "Zero new records should be created"
            assert s2["duplicates_detected"] == 2, "Must detect 2 duplicate records"
            print("  [OK] TEST 2 PASSED: 2 duplicate records accurately detected and skipped.")

            # TEST 3: Process Field Update
            print("\n  [TEST 3] Processing item update (Modified Stipend & Description)...")
            item1_updated = NCSInternshipSchema(
                source="NCS",
                title="Public Policy & Data Analytics Intern",
                company="Ministry of Labour & Employment",
                location="New Delhi",
                skills=["Python", "Data Analysis", "SQL"],
                eligibility="B.Tech / B.Sc Graduate",
                stipend="₹15,000 / month", # Updated stipend
                duration="6 Months",
                deadline="2026-12-31",
                description="Analyze national employment trends and build AI-assisted statistical dashboards.", # Updated desc
                apply_url="https://www.ncs.gov.in/internships/policy-data-01",
                status="active"
            )
            s3 = await NCSSyncService.process_ncs_batch(db, [item1_updated])
            print(f"    - Summary: Created={s3['records_created']}, Updated={s3['records_updated']}, Duplicates={s3['duplicates_detected']}")
            assert s3["records_updated"] == 1, "Must record 1 updated record"
            
            # Verify updated database values
            res = await db.execute(select(Internship).where(Internship.apply_url == "https://www.ncs.gov.in/internships/policy-data-01"))
            db_item = res.scalar_one()
            assert db_item.stipend == "₹15,000 / month"
            print("  [OK] TEST 3 PASSED: Field update correctly applied to existing database record.")

            # TEST 4: Expiry Handling
            print("\n  [TEST 4] Processing expired record (Passed Deadline)...")
            item2_expired = NCSInternshipSchema(
                source="NCS",
                title="Geospatial GIS Data Trainee",
                company="National Remote Sensing Centre (NRSC)",
                location="Hyderabad",
                skills=["GIS", "Python", "Remote Sensing"],
                eligibility="Graduate",
                stipend="₹14,000 / month",
                duration="6 Months",
                deadline="2020-01-01", # Past deadline
                description="Process satellite GIS rasters and geospatial vector layers.",
                apply_url="https://www.ncs.gov.in/internships/gis-trainee-02",
                status="expired"
            )
            s4 = await NCSSyncService.process_ncs_batch(db, [item2_expired])
            print(f"    - Summary: Created={s4['records_created']}, Expired={s4['records_expired']}")
            assert s4["records_expired"] == 1, "Must record 1 expired record"
            
            # Verify status in database
            res = await db.execute(select(Internship).where(Internship.apply_url == "https://www.ncs.gov.in/internships/gis-trainee-02"))
            db_exp_item = res.scalar_one()
            assert db_exp_item.status == "EXPIRED"
            print("  [OK] TEST 4 PASSED: Expired record correctly marked as EXPIRED in database.")

            # Clean up test records
            await db.execute(delete(Internship).where(Internship.source == "NCS"))
            await db.commit()

    asyncio.run(_run_tests())

    print("\n======================================================================")
    print("  VERIFICATION RESULT: ALL NCS SYNC LIFECYCLE TESTS PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_ncs_sync_lifecycle()
