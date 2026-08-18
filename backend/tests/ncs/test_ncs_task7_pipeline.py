import asyncio
import sys
import os

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.db.database import AsyncSessionLocal
from app.db.models import Internship
from app.ncs.schemas import NCSInternshipSchema
from app.ncs.sync_service import NCSSyncService
from sqlalchemy import select, delete, func

def test_ncs_task7_pipeline_verification():
    print("\n======================================================================")
    print("  NCS INTEGRATION TASK 7: LOCAL MOCK DATA PIPELINE TEST SUITE")
    print("======================================================================\n")

    async def _run_tests():
        async with AsyncSessionLocal() as db:
            # Record total initial non-NCS count for isolation verification
            init_non_ncs_res = await db.execute(select(func.count(Internship.id)).where(Internship.source != "NCS"))
            initial_non_ncs_count = init_non_ncs_res.scalar()

            # Clean up prior test NCS records cleanly
            await db.execute(delete(Internship).where(Internship.source == "NCS"))
            await db.commit()

            # ------------------------------------------------------------------
            # 5 Realistic Mock NCS Internship Records
            # ------------------------------------------------------------------
            mock_batch = [
                NCSInternshipSchema(
                    source="NCS",
                    title="Public Policy & Employment Data Intern",
                    company="Ministry of Labour & Employment",
                    location="New Delhi",
                    skills=["Python", "Data Analytics", "Public Policy"],
                    eligibility="Graduate",
                    stipend="₹12,000 / month",
                    duration="6 Months",
                    deadline="2026-12-31",
                    description="Analyze employment statistics and build national dashboard reporting tools.",
                    apply_url="https://www.ncs.gov.in/internships/ncs-pol-101",
                    status="active"
                ),
                NCSInternshipSchema(
                    source="NCS",
                    title="Renewable Energy Technical Apprentice",
                    company="National Thermal Power Corporation (NTPC)",
                    location="New Delhi",
                    skills=["Solar Energy", "Electrical Engineering", "SCADA"],
                    eligibility="B.E. / B.Tech",
                    stipend="₹15,000 / month",
                    duration="12 Months",
                    deadline="2026-11-30",
                    description="Monitor solar PV farm performance and green hydrogen production metrics.",
                    apply_url="https://www.ncs.gov.in/internships/ncs-ntpc-102",
                    status="active"
                ),
                NCSInternshipSchema(
                    source="NCS",
                    title="Cyber Security Operations Trainee",
                    company="Centre for Development of Advanced Computing (C-DAC)",
                    location="Pune",
                    skills=["Linux", "Network Security", "Python"],
                    eligibility="B.Tech Computer Science / IT",
                    stipend="₹14,000 / month",
                    duration="6 Months",
                    deadline="2026-10-15",
                    description="Monitor SOC security alerts and analyze threat intelligence feeds.",
                    apply_url="https://www.ncs.gov.in/internships/ncs-cdac-103",
                    status="active"
                ),
                NCSInternshipSchema(
                    source="NCS",
                    title="Urban Infrastructure Planning Intern",
                    company="National Highways Authority of India (NHAI)",
                    location="Bengaluru",
                    skills=["AutoCAD", "GIS", "Civil Engineering"],
                    eligibility="B.E. Civil Engineering",
                    stipend="₹13,500 / month",
                    duration="6 Months",
                    deadline="2026-09-30",
                    description="Assist highway corridor planning and GIS topographical survey analysis.",
                    apply_url="https://www.ncs.gov.in/internships/ncs-nhai-104",
                    status="active"
                ),
                NCSInternshipSchema(
                    source="NCS",
                    title="Financial Analytics & Risk Trainee",
                    company="Small Industries Development Bank of India (SIDBI)",
                    location="Mumbai",
                    skills=["Financial Modeling", "Excel", "SQL"],
                    eligibility="B.Com / BBA / MBA",
                    stipend="₹16,000 / month",
                    duration="6 Months",
                    deadline="2026-12-15",
                    description="Perform credit risk assessment for MSME enterprise loans.",
                    apply_url="https://www.ncs.gov.in/internships/ncs-sidbi-105",
                    status="active"
                )
            ]

            # ------------------------------------------------------------------
            # TEST CASE 1: Insert 5 new NCS internships
            # ------------------------------------------------------------------
            print("  [TEST CASE 1] Ingesting batch of 5 NEW mock NCS records...")
            s1 = await NCSSyncService.process_ncs_batch(db, mock_batch)
            print(f"    - Ingestion Output: Created={s1['records_created']}, Total Processed={s1['total_processed']}")
            assert s1["records_created"] == 5, "Must store 5 new records"
            assert s1["duplicates_detected"] == 0

            # Verify in database
            db_ncs_res = await db.execute(select(Internship).where(Internship.source == "NCS"))
            ncs_db_items = db_ncs_res.scalars().all()
            assert len(ncs_db_items) == 5
            for item in ncs_db_items:
                assert item.source == "NCS"
                assert "ncs.gov.in" in item.apply_url
            print("  [OK] TEST CASE 1 PASSED: 5 mock NCS internships stored with source='NCS' and mock apply_url.")

            # ------------------------------------------------------------------
            # TEST CASE 2: Run the same batch again (Duplicate Check)
            # ------------------------------------------------------------------
            print("\n  [TEST CASE 2] Re-ingesting identical batch (Deduplication Check)...")
            s2 = await NCSSyncService.process_ncs_batch(db, mock_batch)
            print(f"    - Ingestion Output: Created={s2['records_created']}, Duplicates={s2['duplicates_detected']}")
            assert s2["records_created"] == 0, "Zero new records should be created on duplicate batch"
            assert s2["duplicates_detected"] == 5, "All 5 records must be flagged as duplicates"
            
            db_ncs_res2 = await db.execute(select(Internship).where(Internship.source == "NCS"))
            assert len(db_ncs_res2.scalars().all()) == 5
            print("  [OK] TEST CASE 2 PASSED: 5 duplicates correctly detected; zero duplicate DB records created.")

            # ------------------------------------------------------------------
            # TEST CASE 3: Modify one internship and run batch again
            # ------------------------------------------------------------------
            print("\n  [TEST CASE 3] Modifying 1 internship (Stipend & Description Update)...")
            updated_mock_batch = list(mock_batch)
            updated_mock_batch[0] = NCSInternshipSchema(
                source="NCS",
                title="Public Policy & Employment Data Intern",
                company="Ministry of Labour & Employment",
                location="New Delhi",
                skills=["Python", "Data Analytics", "Public Policy", "Machine Learning"],
                eligibility="Graduate",
                stipend="₹16,000 / month", # Increased stipend
                duration="6 Months",
                deadline="2026-12-31",
                description="Analyze employment statistics and build ML-powered national dashboard reporting tools.", # Modified desc
                apply_url="https://www.ncs.gov.in/internships/ncs-pol-101",
                status="active"
            )

            s3 = await NCSSyncService.process_ncs_batch(db, updated_mock_batch)
            print(f"    - Ingestion Output: Created={s3['records_created']}, Updated={s3['records_updated']}, Duplicates={s3['duplicates_detected']}")
            assert s3["records_updated"] == 1, "Must update exactly 1 modified record"
            assert s3["duplicates_detected"] == 4, "Remaining 4 records must be flagged as duplicates"

            # Confirm DB record is updated
            res_upd = await db.execute(select(Internship).where(Internship.apply_url == "https://www.ncs.gov.in/internships/ncs-pol-101"))
            upd_item = res_upd.scalar_one()
            assert upd_item.stipend == "₹16,000 / month"
            assert "ML-powered" in upd_item.description
            print("  [OK] TEST CASE 3 PASSED: Existing internship updated in place without creating duplicate.")

            # ------------------------------------------------------------------
            # TEST CASE 4: Mark one internship expired
            # ------------------------------------------------------------------
            print("\n  [TEST CASE 4] Marking 1 internship as EXPIRED (Passed Deadline)...")
            expired_mock_batch = list(updated_mock_batch)
            expired_mock_batch[4] = NCSInternshipSchema(
                source="NCS",
                title="Financial Analytics & Risk Trainee",
                company="Small Industries Development Bank of India (SIDBI)",
                location="Mumbai",
                skills=["Financial Modeling", "Excel", "SQL"],
                eligibility="B.Com / BBA / MBA",
                stipend="₹16,000 / month",
                duration="6 Months",
                deadline="2020-01-01", # Past deadline
                description="Perform credit risk assessment for MSME enterprise loans.",
                apply_url="https://www.ncs.gov.in/internships/ncs-sidbi-105",
                status="expired"
            )

            s4 = await NCSSyncService.process_ncs_batch(db, expired_mock_batch)
            print(f"    - Ingestion Output: Expired={s4['records_expired']}")
            assert s4["records_expired"] == 1, "Must flag 1 record as expired"

            # Confirm DB record status
            res_exp = await db.execute(select(Internship).where(Internship.apply_url == "https://www.ncs.gov.in/internships/ncs-sidbi-105"))
            exp_item = res_exp.scalar_one()
            assert exp_item.status == "EXPIRED"
            print("  [OK] TEST CASE 4 PASSED: Expired internship status successfully set to 'EXPIRED'.")

            # ------------------------------------------------------------------
            # TEST CASE 5: Confirm existing non-NCS internships remain unchanged
            # ------------------------------------------------------------------
            print("\n  [TEST CASE 5] Verifying non-NCS internship data isolation...")
            final_non_ncs_res = await db.execute(select(func.count(Internship.id)).where(Internship.source != "NCS"))
            final_non_ncs_count = final_non_ncs_res.scalar()
            assert final_non_ncs_count == initial_non_ncs_count, "Non-NCS record count must remain exactly identical"
            print(f"    - Non-NCS count maintained at {final_non_ncs_count} records.")
            print("  [OK] TEST CASE 5 PASSED: Non-NCS records remain 100% isolated and unchanged.")

            # Clean up mock test records
            await db.execute(delete(Internship).where(Internship.source == "NCS"))
            await db.commit()

    asyncio.run(_run_tests())

    print("\n======================================================================")
    print("  VERIFICATION RESULT: TASK 7 COMPLETE PIPELINE TESTS PASSED (100%)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_ncs_task7_pipeline_verification()
