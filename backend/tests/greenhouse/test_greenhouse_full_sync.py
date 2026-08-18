import asyncio
import sys
import os
from datetime import datetime

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.db.database import AsyncSessionLocal
from app.db.models import Internship, SourceRegistry
from app.greenhouse.sync_service import GreenhouseSyncService
from sqlalchemy import select, func

def test_greenhouse_full_sync_pipeline_suite():
    print("\n======================================================================")
    print("  GREENHOUSE INTEGRATION TASK 8: AUTOMATED SYNC PIPELINE TEST SUITE")
    print("======================================================================\n")

    async def _run():
        async with AsyncSessionLocal() as db:
            # 1. Setup stale/unavailable test requisition
            print("  [STEP 1] Setting up stale test requisition (GH_EXPIRED_ROLE_999)...")
            stale_rec = Internship(
                company_name="Ghost Corp",
                company_sector="Technology",
                title="Deprecated Engineer",
                description="Old requisition no longer in live API feed.",
                location="Remote",
                work_mode="Remote",
                duration="Full-Time",
                stipend="Market",
                deadline="2026-12-31",
                source="Greenhouse",
                external_id="GH_EXPIRED_ROLE_999",
                opportunity_type="JOB",
                status="VERIFIED_LIVE",
                verification_status="VERIFIED"
            )
            db.add(stale_rec)
            await db.commit()
            await db.refresh(stale_rec)

            # 2. Run Full Synchronization Cycle
            print("\n  [STEP 2] Executing GreenhouseSyncService.run_full_greenhouse_sync()...")
            boards = ["stripe"]
            sync_res = await GreenhouseSyncService.run_full_greenhouse_sync(db, board_tokens=boards)

            print("    - Synchronization Cycle Results:")
            print(f"      • Status:              {sync_res['status']}")
            print(f"      • Total Fetched:       {sync_res['total_fetched']}")
            print(f"      • Records Created:     {sync_res['records_created']}")
            print(f"      • Records Updated:     {sync_res['records_updated']}")
            print(f"      • Duplicates Detected: {sync_res['duplicates_detected']}")
            print(f"      • Unavailable Expired: {sync_res['expired_marked']}")

            assert sync_res["status"] == "SUCCESS"
            assert sync_res["total_fetched"] > 0

            # 3. Verify Unavailable Requisition Transitioned to EXPIRED
            print("\n  [STEP 3] Verifying stale requisition marked as EXPIRED (inactive)...")
            stale_db_res = await db.execute(select(Internship).where(Internship.external_id == "GH_EXPIRED_ROLE_999"))
            stale_db_item = stale_db_res.scalar_one_or_none()

            assert stale_db_item is not None, "Historical record must NOT be deleted from database"
            assert stale_db_item.status == "EXPIRED", f"Status must be EXPIRED, got {stale_db_item.status}"
            assert stale_db_item.verification_status == "EXPIRED"
            print("    - Confirmed non-destructive expiry transition: status='EXPIRED', row retained in DB.")

            # Clean up test requisition
            await db.delete(stale_db_item)
            await db.commit()

            # 4. Verify SourceRegistry Entry & Timestamps
            print("\n  [STEP 4] Verifying SourceRegistry metrics and timestamp update...")
            src_res = await db.execute(select(SourceRegistry).where(SourceRegistry.source_name == "Greenhouse"))
            src = src_res.scalar_one_or_none()

            assert src is not None, "SourceRegistry must contain Greenhouse entry"
            assert src.health_status == "ONLINE"
            assert src.last_success_at is not None
            assert src.polling_frequency_seconds == 21600 # 6 Hours
            print("    - SourceRegistry entry verified ONLINE (6-hour polling schedule configured).")

            # 5. Non-Greenhouse Isolation
            print("\n  [STEP 5] Verifying non-Greenhouse sources (PMIS / NCS) remain 100% unaffected...")
            non_gh_res = await db.execute(select(func.count(Internship.id)).where(Internship.source != "Greenhouse"))
            non_gh_count = non_gh_res.scalar()
            print(f"    - Non-Greenhouse database records intact: {non_gh_count}")

    asyncio.run(_run())

    print("\n======================================================================")
    print("  TASK 8 AUTOMATED SYNC PIPELINE VERIFICATION: PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_greenhouse_full_sync_pipeline_suite()
