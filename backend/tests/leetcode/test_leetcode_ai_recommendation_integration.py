import asyncio
import sys
import os
from sqlalchemy import select, text
from sqlalchemy.orm import selectinload

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.db.database import AsyncSessionLocal, engine, Base
from app.db.models import StudentProfile, Internship, InternshipSkill, LeetCodeProfile
from app.leetcode.profile_repository import LeetCodeProfileRepository
from app.services.recommendation import generate_recommendation_for_student, check_eligibility

def test_leetcode_ai_recommendation_integration_suite():
    print("\n======================================================================")
    print("  LEETCODE INTEGRATION TASK 12: AI RECOMMENDATION INTEGRATION AUDIT SUITE")
    print("======================================================================\n")

    async def _run():
        async with AsyncSessionLocal() as db:
            # 1. Fetch Student & Internship with eager loading
            res_st = await db.execute(select(StudentProfile).limit(1))
            student = res_st.scalar_one_or_none()
            assert student is not None

            res_opp = await db.execute(
                select(Internship).options(
                    selectinload(Internship.skills).selectinload(InternshipSkill.skill)
                ).limit(1)
            )
            opp = res_opp.scalar_one_or_none()
            assert opp is not None

            # 2. Test Recommendation without LeetCode Profile
            print("  [STEP 1] Testing AI recommendation without LeetCode profile...")
            score_base, cat_base, exp_base = generate_recommendation_for_student(
                student=student,
                internship=opp,
                student_skills=["Python", "SQL"],
                leetcode_profile=None
            )
            print(f"    - Base Compatibility Score: {score_base}/100 | Category: '{cat_base}'")
            assert score_base >= 0.0 and score_base <= 100.0

            # 3. Test Recommendation with UNVERIFIED LeetCode Profile
            print("\n  [STEP 2] Testing AI recommendation with UNVERIFIED LeetCode profile (Must NOT boost)...")
            unverif_prof = LeetCodeProfile(
                candidate_id=student.id,
                leetcode_username="unverif_user",
                verification_status="PENDING",
                ownership_status="PENDING",
                total_problems_solved=500
            )

            score_unverif, cat_unverif, exp_unverif = generate_recommendation_for_student(
                student=student,
                internship=opp,
                student_skills=["Python", "SQL"],
                leetcode_profile=unverif_prof
            )
            print(f"    - Unverified Score:         {score_unverif}/100")
            assert score_unverif == score_base, "Unverified profile MUST NOT boost recommendation score!"

            # 4. Test Recommendation with VERIFIED LeetCode Profile & Real Metrics
            print("\n  [STEP 3] Testing AI recommendation with VERIFIED LeetCode profile...")
            verif_prof = LeetCodeProfile(
                candidate_id=student.id,
                leetcode_username="verified_pro_coder",
                verification_status="VERIFIED",
                ownership_status="VERIFIED",
                total_problems_solved=380,
                medium_solved=210,
                hard_solved=50,
                contest_rating=1950.0
            )

            # Ensure internship title/description triggers tech role matching
            opp.title = "Software Engineering Intern"
            opp.description = "Develop Python and C++ backend software services."

            score_verif, cat_verif, exp_verif = generate_recommendation_for_student(
                student=student,
                internship=opp,
                student_skills=["Python", "SQL"],
                leetcode_profile=verif_prof
            )

            print(f"    - Base Score:               {score_base}/100")
            print(f"    - Verified LeetCode Score: {score_verif}/100")
            print(f"    - Match Reasons ({len(exp_verif['reasons'])}):")
            for r in exp_verif["reasons"]:
                print(f"      • {r}")

            assert score_verif >= score_base, "Verified LeetCode evidence MUST contribute positive match signal!"
            assert any("Verified LeetCode Evidence:" in r for r in exp_verif["reasons"]), "Must include explainable LeetCode match reason!"

    asyncio.run(_run())

    print("\n======================================================================")
    print("  TASK 12 LEETCODE AI RECOMMENDATION INTEGRATION: PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_leetcode_ai_recommendation_integration_suite()
