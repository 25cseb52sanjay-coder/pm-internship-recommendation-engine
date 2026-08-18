import asyncio
import sys
import os
import json
from sqlalchemy import select

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.db.database import AsyncSessionLocal, engine, Base
from app.db.models import StudentProfile, Internship
from app.services.branch_compatibility import BranchCompatibilityEngine
from app.services.recommendation import generate_recommendation_for_student, check_eligibility
from app.services.opportunity_quality import OpportunityQualityService

def test_branch_compatibility_engine_suite():
    print("\n======================================================================")
    print("  TASK 27B: MULTI-DISCIPLINE BRANCH COMPATIBILITY ENGINE TEST SUITE")
    print("======================================================================\n")

    async def _run():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # 1. Exact & Related Branch Compatibility Tests
        print("  [Test 1-15] Testing Exact & Related Branch Compatibility Scenarios...")
        
        # Test 1: CSE -> CSE (STRONG_MATCH)
        res1 = BranchCompatibilityEngine.evaluate_compatibility("Computer Science & Engineering", ["COMPUTER_SCIENCE"])
        assert res1["compatibility_level"] == "STRONG_MATCH" and res1["compatibility_score"] == 1.0

        # Test 2: IT -> IT (STRONG_MATCH)
        res2 = BranchCompatibilityEngine.evaluate_compatibility("Information Technology", ["INFORMATION_TECHNOLOGY"])
        assert res2["compatibility_level"] == "STRONG_MATCH" and res2["compatibility_score"] == 1.0

        # Test 3: CSE -> Software Eng (RELATED_MATCH)
        res3 = BranchCompatibilityEngine.evaluate_compatibility("Computer Science", ["SOFTWARE_ENGINEERING"])
        assert res3["compatibility_level"] == "RELATED_MATCH" and res3["compatibility_score"] == 0.75

        # Test 4: ECE -> ECE (STRONG_MATCH)
        res4 = BranchCompatibilityEngine.evaluate_compatibility("Electronics and Communication Engineering", ["ELECTRONICS_COMMUNICATION"])
        assert res4["compatibility_level"] == "STRONG_MATCH" and res4["compatibility_score"] == 1.0

        # Test 5 & 6: ECE -> VLSI / Embedded Systems (RELATED_MATCH)
        res5 = BranchCompatibilityEngine.evaluate_compatibility("ECE", ["VLSI"])
        assert res5["compatibility_level"] in ["STRONG_MATCH", "RELATED_MATCH"]

        res6 = BranchCompatibilityEngine.evaluate_compatibility("ECE", ["EMBEDDED_SYSTEMS"])
        assert res6["compatibility_level"] == "RELATED_MATCH" and res6["compatibility_score"] == 0.75

        # Test 7: EEE -> Electrical (STRONG_MATCH)
        res7 = BranchCompatibilityEngine.evaluate_compatibility("EEE", ["ELECTRICAL_ELECTRONICS"])
        assert res7["compatibility_level"] == "STRONG_MATCH"

        # Test 8-10: Mechanical -> Mech / Automotive / Robotics (STRONG & RELATED)
        res8 = BranchCompatibilityEngine.evaluate_compatibility("Mechanical Engineering", ["MECHANICAL"])
        assert res8["compatibility_level"] == "STRONG_MATCH"

        res9 = BranchCompatibilityEngine.evaluate_compatibility("Mechanical", ["AUTOMOTIVE"])
        assert res9["compatibility_level"] == "RELATED_MATCH"

        res10 = BranchCompatibilityEngine.evaluate_compatibility("Mechanical", ["ROBOTICS"])
        assert res10["compatibility_level"] in ["STRONG_MATCH", "RELATED_MATCH"]

        # Test 11-15: Civil, Chemical, Aerospace, Biotech (STRONG & RELATED)
        res11 = BranchCompatibilityEngine.evaluate_compatibility("Civil Engineering", ["CIVIL"])
        assert res11["compatibility_level"] == "STRONG_MATCH"

        res12 = BranchCompatibilityEngine.evaluate_compatibility("Civil", ["STRUCTURAL"])
        assert res12["compatibility_level"] == "RELATED_MATCH"

        res13 = BranchCompatibilityEngine.evaluate_compatibility("Chemical Engineering", ["CHEMICAL"])
        assert res13["compatibility_level"] == "STRONG_MATCH"

        res14 = BranchCompatibilityEngine.evaluate_compatibility("Aerospace Engineering", ["AEROSPACE"])
        assert res14["compatibility_level"] == "STRONG_MATCH"

        res15 = BranchCompatibilityEngine.evaluate_compatibility("Biotechnology", ["BIOTECHNOLOGY"])
        assert res15["compatibility_level"] == "STRONG_MATCH"

        print("    - All 15 branch matching & relationship scenarios verified 100%.")

        # 2. Incompatible Discipline Rejection
        print("\n  [Test 16 & 22] Testing Incompatible Discipline Rejection...")
        res_incomp = BranchCompatibilityEngine.evaluate_compatibility("Civil Engineering", ["COMPUTER_SCIENCE"])
        assert res_incomp["compatibility_level"] == "INCOMPATIBLE"
        assert res_incomp["compatibility_score"] == 0.0
        print("    - Civil candidate correctly evaluated as INCOMPATIBLE for Computer Science requirement.")

        # 3. Scope Tests (ALL_ENGINEERING / ALL_TECHNOLOGY / MULTI_DISCIPLINE / UNKNOWN)
        print("\n  [Test 17-21] Testing Broad Scope & UNKNOWN Handling...")
        res_eng = BranchCompatibilityEngine.evaluate_compatibility("Mechanical Engineering", discipline_scope="ALL_ENGINEERING")
        assert res_eng["compatibility_level"] == "BROAD_SCOPE_MATCH"

        res_tech = BranchCompatibilityEngine.evaluate_compatibility("Computer Science", discipline_scope="ALL_TECHNOLOGY")
        assert res_tech["compatibility_level"] == "BROAD_SCOPE_MATCH"

        res_multi = BranchCompatibilityEngine.evaluate_compatibility("CSE", required_disciplines=["MECHANICAL", "COMPUTER_SCIENCE"], discipline_scope="MULTI_DISCIPLINE")
        assert res_multi["compatibility_level"] == "STRONG_MATCH"

        res_unk_cand = BranchCompatibilityEngine.evaluate_compatibility("Unknown Quantum Branch", required_disciplines=["COMPUTER_SCIENCE"])
        assert res_unk_cand["compatibility_level"] == "UNKNOWN"
        assert res_unk_cand["compatibility_score"] is None

        res_unk_opp = BranchCompatibilityEngine.evaluate_compatibility("Computer Science", required_disciplines=[], discipline_scope="UNKNOWN")
        assert res_unk_opp["compatibility_level"] == "UNKNOWN"
        print("    - ALL_ENGINEERING, ALL_TECHNOLOGY, MULTI_DISCIPLINE, and UNKNOWN handling verified.")

        # 4. Recommendation Engine Pipeline Integration Check
        print("\n  [Test 23-28] Testing Pipeline Integration & Hard Gate Preservation...")
        from sqlalchemy.orm import selectinload
        from app.db.models import InternshipSkill

        async with AsyncSessionLocal() as db:
            res_st = await db.execute(select(StudentProfile).limit(1))
            student = res_st.scalar_one_or_none()
            res_opp = await db.execute(
                select(Internship).options(
                    selectinload(Internship.skills).selectinload(InternshipSkill.skill)
                ).where(Internship.status == "VERIFIED_LIVE").limit(1)
            )
            opp = res_opp.scalar_one_or_none()

            assert student is not None and opp is not None

            # Test Task 20 eligibility remains hard gate
            underage_st = StudentProfile(age=17, degree="B.Tech")
            is_elig, _ = check_eligibility(underage_st, opp)
            assert is_elig is False

            # Test Task 21 quality gate remains active
            invalid_opp = Internship(title="", company_name="Fake Corp", source="Adzuna", apply_url="javascript:alert(1)", status="INVALID")
            is_q_ok, _ = OpportunityQualityService.is_eligible_for_recommendation_ranking(invalid_opp)
            assert is_q_ok is False

            # Test recommendation engine output includes Task 27B academic match payload
            score, category, explanation = generate_recommendation_for_student(
                student=student,
                internship=opp,
                student_skills=["Python", "SQL"]
            )
            assert "academic_match_level" in explanation
            assert "academic_match_score" in explanation
            print(f"    - Integrated Recommendation Engine output: academic_match_level='{explanation['academic_match_level']}' | score={score}%")

    asyncio.run(_run())

    print("\n======================================================================")
    print("  TASK 27B BRANCH COMPATIBILITY ENGINE: PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_branch_compatibility_engine_suite()
