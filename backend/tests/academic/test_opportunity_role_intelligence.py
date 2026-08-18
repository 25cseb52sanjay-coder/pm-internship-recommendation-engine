import asyncio
import sys
import os
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.db.database import AsyncSessionLocal, engine, Base
from app.db.models import StudentProfile, Internship, InternshipSkill
from app.services.opportunity_role_intelligence import OpportunityRoleIntelligence
from app.services.recommendation import generate_recommendation_for_student, check_eligibility
from app.services.opportunity_quality import OpportunityQualityService

def test_opportunity_role_intelligence_suite():
    print("\n======================================================================")
    print("  TASK 27D: MULTI-DISCIPLINE OPPORTUNITY ROLE & DOMAIN INTELLIGENCE SUITE")
    print("======================================================================\n")

    # 1. Multi-Discipline Role Classification & Matching
    print("  [Test 1-7] Testing Multi-Discipline Exact Role Matching...")

    cse_role = OpportunityRoleIntelligence.classify_opportunity_role("Software Engineering Intern")
    assert cse_role["normalized_role"] == "SOFTWARE_ENGINEERING"
    assert cse_role["role_family"] == "technology"

    ece_role = OpportunityRoleIntelligence.classify_opportunity_role("VLSI Design Engineer")
    assert ece_role["normalized_role"] == "VLSI"
    assert ece_role["role_family"] == "electronics"

    eee_role = OpportunityRoleIntelligence.classify_opportunity_role("Power Systems Engineering Intern")
    assert eee_role["normalized_role"] == "POWER_SYSTEMS"
    assert eee_role["role_family"] == "electrical"

    mech_role = OpportunityRoleIntelligence.classify_opportunity_role("CAD Mechanical Design Engineer")
    assert mech_role["normalized_role"] == "MECHANICAL_DESIGN"
    assert mech_role["role_family"] == "mechanical"

    civil_role = OpportunityRoleIntelligence.classify_opportunity_role("Bridge Structural Engineering Intern")
    assert civil_role["normalized_role"] == "STRUCTURAL_ENGINEERING"
    assert civil_role["role_family"] == "civil"

    chem_role = OpportunityRoleIntelligence.classify_opportunity_role("Refinery Process Engineer")
    assert chem_role["normalized_role"] == "PROCESS_ENGINEERING"
    assert chem_role["role_family"] == "chemical_materials"

    bio_role = OpportunityRoleIntelligence.classify_opportunity_role("Biotechnology Research Intern")
    assert bio_role["normalized_role"] == "BIOTECHNOLOGY"
    assert bio_role["role_family"] == "life_sciences"

    print("    - Multi-discipline role classifications across CSE, ECE, EEE, Mech, Civil, Chem, Bio verified 100%.")

    # 2. Key Design Principle: Role Importance > Company Sector
    print("\n  [Test 8-11] Testing Key Principle: Role Importance > Company Sector...")

    # Case A: Automotive Company + Software Role + CSE Candidate -> HIGH ROLE RELEVANCE
    sw_in_auto = OpportunityRoleIntelligence.classify_opportunity_role("Software Engineer - Autonomous Driving", "Automotive firmware & software")
    match_sw_auto = OpportunityRoleIntelligence.evaluate_role_compatibility("Software Engineering", "Software Engineering", sw_in_auto)
    assert match_sw_auto["role_match_level"] == "EXACT_ROLE_MATCH"
    assert match_sw_auto["role_match_score"] == 1.0
    print("    - [OK] Software Engineering role at Automotive company -> EXACT_ROLE_MATCH (1.0).")

    # Case B: Semiconductor Company + HR Role + ECE Candidate -> LOW ROLE RELEVANCE (NO_ROLE_MATCH)
    hr_in_semi = OpportunityRoleIntelligence.classify_opportunity_role("Human Resources Recruiter", "Talent acquisition at Semiconductor Corp")
    match_hr_semi = OpportunityRoleIntelligence.evaluate_role_compatibility("VLSI", "VLSI Design", hr_in_semi)
    assert match_hr_semi["role_match_level"] == "NO_ROLE_MATCH"
    assert match_hr_semi["role_match_score"] == 0.0
    print("    - [OK] Human Resources role at Semiconductor company for ECE candidate -> NO_ROLE_MATCH (0.0).")

    # Case C: Banking Company + Cybersecurity Role + CSE Candidate -> HIGH ROLE RELEVANCE
    sec_in_bank = OpportunityRoleIntelligence.classify_opportunity_role("Cybersecurity SOC Analyst", "Financial cybersecurity")
    match_sec_bank = OpportunityRoleIntelligence.evaluate_role_compatibility("Cybersecurity", "Cybersecurity", sec_in_bank)
    assert match_sec_bank["role_match_level"] == "EXACT_ROLE_MATCH"
    print("    - [OK] Cybersecurity role at Banking company -> EXACT_ROLE_MATCH (1.0).")

    # Test 12-15: Related & Unknown Role Handling
    print("\n  [Test 12-15] Testing Related & Unknown Role Handling...")
    rel_match = OpportunityRoleIntelligence.evaluate_role_compatibility("Web Development", None, cse_role)
    assert rel_match["role_match_level"] == "STRONG_ROLE_MATCH"
    assert rel_match["role_match_score"] == 0.90

    unk_role = OpportunityRoleIntelligence.classify_opportunity_role("Unspecified Project Intern", "")
    assert unk_role["normalized_role"] == "UNKNOWN"

    unk_match = OpportunityRoleIntelligence.evaluate_role_compatibility(None, None, unk_role)
    assert unk_match["role_match_level"] == "UNKNOWN"
    assert unk_match["role_match_score"] is None
    print("    - Related role match (0.90) and UNKNOWN role handling verified.")

    # 4. Pipeline Integration & Hard Gate Preservation
    print("\n  [Test 16-27] Testing Recommendation Pipeline Integration & Hard Gates...")
    async def _run():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

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

            # Test recommendation engine output includes Task 27D payload
            score, category, explanation = generate_recommendation_for_student(
                student=student,
                internship=opp,
                student_skills=["Python", "SQL"]
            )
            assert "role_match_level" in explanation
            assert "normalized_role" in explanation
            assert "role_family" in explanation
            assert "opportunity_domain" in explanation
            print(f"    - Integrated Recommendation Engine output: role_level='{explanation['role_match_level']}' | domain='{explanation['opportunity_domain']}' | score={score}%")

    asyncio.run(_run())

    print("\n======================================================================")
    print("  TASK 27D OPPORTUNITY ROLE & DOMAIN INTELLIGENCE: PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_opportunity_role_intelligence_suite()
