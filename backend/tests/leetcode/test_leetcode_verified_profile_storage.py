import asyncio
import sys
import os
from sqlalchemy import select, inspect

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.db.database import AsyncSessionLocal
from app.db.models import StudentProfile, LeetCodeProfile
from app.leetcode.profile_repository import LeetCodeProfileRepository

def test_leetcode_verified_profile_storage_suite():
    print("\n======================================================================")
    print("  LEETCODE INTEGRATION TASK 8: VERIFIED PROFILE STORAGE AUDIT SUITE")
    print("======================================================================\n")

    async def _run():
        async with AsyncSessionLocal() as db:
            # 1. Fetch test candidate
            res_st = await db.execute(select(StudentProfile).limit(1))
            student = res_st.scalar_one_or_none()
            assert student is not None, "Database must contain at least 1 StudentProfile"
            cand_id = student.id

            # 2. Test Verified Profile Storage
            print("  [STEP 1] Persisting verified LeetCode profile record in PostgreSQL...")
            saved_prof = await LeetCodeProfileRepository.save_verified_profile(
                db=db,
                candidate_id=cand_id,
                leetcode_username="legit_verified_user",
                normalized_profile_url="https://leetcode.com/u/legit_verified_user",
                verification_method="BIO_TOKEN_CHALLENGE",
                data_status="NOT_AVAILABLE"
            )

            print(f"    - Persisted Record ID:       {saved_prof.id}")
            print(f"    - Candidate ID:              {saved_prof.candidate_id}")
            print(f"    - LeetCode Username:        '{saved_prof.leetcode_username}'")
            print(f"    - Normalized Profile URL:   '{saved_prof.leetcode_profile_url}'")
            print(f"    - Ownership Status:         '{saved_prof.ownership_status}'")
            print(f"    - Verification Status:      '{saved_prof.verification_status}'")
            print(f"    - Verification Method:      '{saved_prof.verification_method}'")
            print(f"    - Verified At Timestamp:     '{saved_prof.verified_at}'")
            print(f"    - Data Status:              '{saved_prof.data_status}'")

            assert saved_prof.ownership_status == "VERIFIED"
            assert saved_prof.verification_status == "VERIFIED"
            assert saved_prof.leetcode_username == "legit_verified_user"
            assert saved_prof.leetcode_profile_url == "https://leetcode.com/u/legit_verified_user"
            assert saved_prof.verified_at is not None
            assert saved_prof.verification_challenge_token is None

            # 3. Security Audit on Stored Database Record
            print("\n  [STEP 2] Performing security & privacy audit on stored database model...")
            model_columns = {c.name for c in inspect(LeetCodeProfile).columns}

            forbidden_terms = {"password", "cookie", "session_token", "auth_token", "jwt_token"}
            for col in model_columns:
                for f_term in forbidden_terms:
                    assert f_term not in col.lower(), f"Forbidden column '{col}' detected!"

            print("    - Security Audit Passed: Zero passwords, cookies, or auth tokens in schema.")

            # 4. Verify Database State Retrieval
            print("\n  [STEP 3] Verifying PostgreSQL state retrieval by candidate ID...")
            fetched = await LeetCodeProfileRepository.get_profile_by_candidate(db, cand_id)
            assert fetched is not None
            assert fetched.verification_status == "VERIFIED"
            assert fetched.ownership_status == "VERIFIED"
            print("    - Database state accurately reflects real verification state.")

    asyncio.run(_run())

    print("\n======================================================================")
    print("  TASK 8 LEETCODE VERIFIED PROFILE STORAGE VERIFICATION: PASSED (100%)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_leetcode_verified_profile_storage_suite()
