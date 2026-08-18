import asyncio
import sys
import os
from datetime import datetime, timedelta
from sqlalchemy import select

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.db.database import AsyncSessionLocal
from app.db.models import StudentProfile, LeetCodeProfile
from app.leetcode.verification import LeetCodeVerificationService
from app.leetcode.data_provider import (
    LeetCodeDataProvider,
    LeetCodeProviderRegistry,
    ProviderResultStatus,
    ProviderResult
)

def test_leetcode_ownership_verification_suite():
    print("\n======================================================================")
    print("  LEETCODE INTEGRATION TASK 7: OWNERSHIP VERIFICATION AUDIT TEST SUITE")
    print("======================================================================\n")

    async def _run():
        async with AsyncSessionLocal() as db:
            # Fetch a test student profile
            res_st = await db.execute(select(StudentProfile).limit(1))
            student = res_st.scalar_one_or_none()
            assert student is not None, "Database must contain at least 1 StudentProfile for test"
            cand_id = student.id

            # 1. Test Challenge Generation & Binding
            print("  [STEP 1] Generating ownership challenge token bound to candidate and handle...")
            gen_res = await LeetCodeVerificationService.generate_ownership_challenge(
                db, candidate_id=cand_id, raw_input="https://leetcode.com/u/ownership_test_dev"
            )
            print(f"    - Candidate ID:       {gen_res['candidate_id']}")
            print(f"    - Handle:             '{gen_res['leetcode_username']}'")
            print(f"    - Challenge Token:    '{gen_res['challenge_token']}'")
            print(f"    - Expiry Timestamp:   '{gen_res['expires_at']}'")
            print(f"    - System Status:      '{gen_res['status']}'")

            assert gen_res["status"] == "OWNERSHIP_PENDING"
            assert gen_res["challenge_token"].startswith("LEETCODE_VERIFY_")
            assert gen_res["leetcode_username"] == "ownership_test_dev"

            # 2. Test Verification with Unconfigured Provider (Must Report Limitation & Remain Unverified)
            print("\n  [STEP 2] Verifying challenge with Unconfigured Provider (Must NOT falsely verify)...")
            LeetCodeProviderRegistry.reset()
            ver_unconf = await LeetCodeVerificationService.verify_ownership_challenge(db, candidate_id=cand_id)
            print(f"    - Verified:           {ver_unconf['verified']}")
            print(f"    - System Status:      '{ver_unconf['status']}'")
            print(f"    - Message:            '{ver_unconf['message']}'")

            assert ver_unconf["verified"] is False
            assert ver_unconf["status"] == "DATA_UNAVAILABLE"
            assert "limitation" in ver_unconf["message"].lower()

            # 3. Test Successful Ownership Verification via Permitted Provider
            print("\n  [STEP 3] Testing successful ownership verification via Authorized Provider...")
            target_token = gen_res["challenge_token"]

            class MockAuthorizedBioProvider(LeetCodeDataProvider):
                async def check_profile_exists(self, username: str) -> ProviderResult:
                    return ProviderResult(status=ProviderResultStatus.SUCCESS, message="Exists", timestamp="2026-08-14T00:00:00Z")
                async def get_profile_data(self, username: str) -> ProviderResult:
                    return ProviderResult(
                        status=ProviderResultStatus.SUCCESS,
                        message="Profile data retrieved",
                        data={"username": username, "about_me": f"Software Dev | {target_token} | ML Enthusiast"},
                        timestamp="2026-08-14T00:00:00Z"
                    )
                async def get_profile_statistics(self, username: str) -> ProviderResult:
                    return ProviderResult(status=ProviderResultStatus.SUCCESS, message="Stats", timestamp="2026-08-14T00:00:00Z")
                async def get_provider_status(self) -> dict:
                    return {"is_configured": True}

            LeetCodeProviderRegistry.set_provider(MockAuthorizedBioProvider())

            ver_success = await LeetCodeVerificationService.verify_ownership_challenge(db, candidate_id=cand_id)
            print(f"    - Verified:           {ver_success['verified']}")
            print(f"    - System Status:      '{ver_success['status']}'")
            print(f"    - Message:            '{ver_success['message']}'")

            assert ver_success["verified"] is True
            assert ver_success["status"] == "VERIFIED"

            # 4. Verify Single-Use Token Consumption in PostgreSQL
            print("\n  [STEP 4] Verifying single-use token consumption in PostgreSQL...")
            res_lc = await db.execute(select(LeetCodeProfile).where(LeetCodeProfile.candidate_id == cand_id))
            db_prof = res_lc.scalar_one_or_none()

            assert db_prof.ownership_status == "VERIFIED"
            assert db_prof.verification_status == "VERIFIED"
            assert db_prof.verification_challenge_token is None, "Challenge token MUST be consumed (None) after verification!"
            print("    - Single-use token consumption verified 100% in database.")

            # Reset provider registry
            LeetCodeProviderRegistry.reset()

    asyncio.run(_run())

    print("\n======================================================================")
    print("  TASK 7 LEETCODE OWNERSHIP VERIFICATION: PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_leetcode_ownership_verification_suite()
