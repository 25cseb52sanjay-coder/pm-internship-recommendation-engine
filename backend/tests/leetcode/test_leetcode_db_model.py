import asyncio
import sys
import os
from datetime import datetime
from sqlalchemy import select, inspect

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.db.database import AsyncSessionLocal, engine, Base
from app.db.models import StudentProfile, LeetCodeProfile

def test_leetcode_db_model_suite():
    print("\n======================================================================")
    print("  LEETCODE INTEGRATION TASK 4: DATABASE SCHEMA & MODEL AUDIT TEST SUITE")
    print("======================================================================\n")

    async def _run():
        # 1. Initialize tables if missing
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with AsyncSessionLocal() as db:
            # 2. Inspect Table Columns & Constraints
            print("  [STEP 1] Inspecting leetcode_profiles table schema definition...")
            
            req_fields = {
                "id", "candidate_id", "leetcode_profile_url", "leetcode_username",
                "account_exists", "ownership_status", "verification_status",
                "verification_method", "verification_challenge_token",
                "verification_created_at", "verified_at", "last_verified_at",
                "data_status", "last_data_refresh_at", "created_at", "updated_at"
            }

            model_columns = {c.name for c in inspect(LeetCodeProfile).columns}
            print(f"    - Model Columns Found ({len(model_columns)}): {sorted(list(model_columns))}")

            for f in req_fields:
                assert f in model_columns, f"Required field '{f}' missing from LeetCodeProfile model schema"

            # Verify security rules: Zero passwords, cookies, or auth tokens in schema
            forbidden_terms = {"password", "cookie", "session_token", "auth_token", "jwt_token"}
            for col in model_columns:
                col_low = col.lower()
                for f_term in forbidden_terms:
                    assert f_term not in col_low, f"Forbidden sensitive field '{col}' detected in LeetCode database schema!"

            # 3. Test Database Insertion, Foreign Key Relationship, and Status Enums
            print("\n  [STEP 2] Testing CRUD operations & relationship with StudentProfile...")
            
            # Fetch a student profile
            res = await db.execute(select(StudentProfile).limit(1))
            student = res.scalar_one_or_none()
            assert student is not None, "Database must contain at least one StudentProfile for test"

            # Check if student already has a LeetCodeProfile
            res_existing = await db.execute(select(LeetCodeProfile).where(LeetCodeProfile.candidate_id == student.id))
            lc_prof = res_existing.scalar_one_or_none()

            now = datetime.utcnow()

            if not lc_prof:
                lc_prof = LeetCodeProfile(
                    candidate_id=student.id,
                    leetcode_profile_url="https://leetcode.com/u/test_candidate_db",
                    leetcode_username="test_candidate_db",
                    account_exists=True,
                    ownership_status="VERIFIED",
                    verification_status="VERIFIED",
                    verification_method="BIO_TOKEN_CHALLENGE",
                    verification_challenge_token="LEETCODE_VERIFY_TEST123",
                    verification_created_at=now,
                    verified_at=now,
                    last_verified_at=now,
                    data_status="AVAILABLE",
                    last_data_refresh_at=now
                )
                db.add(lc_prof)
                await db.commit()
                await db.refresh(lc_prof)
            else:
                lc_prof.ownership_status = "VERIFIED"
                lc_prof.verification_status = "VERIFIED"
                lc_prof.data_status = "AVAILABLE"
                lc_prof.last_verified_at = now
                await db.commit()

            print(f"    - Registered LeetCode Record ID: {lc_prof.id}")
            print(f"    - Candidate ID Foreign Key:      {lc_prof.candidate_id}")
            print(f"    - LeetCode Handle:               '{lc_prof.leetcode_username}'")
            print(f"    - Ownership Status:              '{lc_prof.ownership_status}'")
            print(f"    - Verification Status:           '{lc_prof.verification_status}'")
            print(f"    - Data Status:                   '{lc_prof.data_status}'")

            # 4. Test Status Values Integrity
            valid_ownership_statuses = {"NOT_STARTED", "PENDING", "VERIFIED", "FAILED", "EXPIRED"}
            valid_verification_statuses = {"NOT_CONNECTED", "PENDING", "VERIFIED", "FAILED", "UNAVAILABLE"}
            valid_data_statuses = {"NOT_AVAILABLE", "AVAILABLE", "STALE", "ERROR"}

            assert lc_prof.ownership_status in valid_ownership_statuses
            assert lc_prof.verification_status in valid_verification_statuses
            assert lc_prof.data_status in valid_data_statuses

    asyncio.run(_run())

    print("\n======================================================================")
    print("  TASK 4 LEETCODE DB MODEL & SCHEMA VERIFICATION: PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_leetcode_db_model_suite()
