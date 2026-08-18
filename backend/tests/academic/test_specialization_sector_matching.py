import asyncio
import sys
import os
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.db.database import AsyncSessionLocal, engine, Base
from app.db.models import StudentProfile, Internship, InternshipSkill
from app.services.specialization_sector_matching import SpecializationSectorMatchingEngine
from app.services.recommendation import generate_recommendation_for_student, check_eligibility
from app.services.opportunity_quality import OpportunityQualityService

def test_specialization_sector_matching_suite():
    print("\n======================================================================")
    print("  TASK 27C: MULTI-DISCIPLINE SPECIALIZATION & SECTOR MATCHING SUITE")
    print("======================================================================\n")

    spec_tests = [
        ("CSE + AI/ML", "AI/ML", "AI/ML Engineer", "SPECIALIZATION_EXACT"),
        ("CSE + Cybersecurity", "Cybersecurity", "Cybersecurity Analyst", "SPECIALIZATION_EXACT"),
        ("CSE + Data Science", "Data Science", "Data Science Intern", "SPECIALIZATION_EXACT"),
        ("IT + Cloud", "Cloud", "Cloud Engineering Intern", "SPECIALIZATION_EXACT"),
        ("ECE + VLSI", "VLSI", "VLSI Design Intern", "SPECIALIZATION_EXACT"),
        ("ECE + Embedded", "Embedded Systems", "Embedded Firmware Engineer", "SPECIALIZATION_EXACT"),
        ("ECE + Telecommunications", "Telecommunications", "5G Telecom Intern", "SPECIALIZATION_EXACT"),
        ("EEE + Power Systems", "Power Systems", "Power Grid Intern", "SPECIALIZATION_EXACT"),
        ("EEE + Renewable Energy", "Renewable Energy", "Solar Energy Engineering Intern", "SPECIALIZATION_EXACT"),
        ("EEE + EV", "EV Systems", "Electric Vehicle Battery Intern", "SPECIALIZATION_EXACT"),
        ("Mechanical + Automotive", "Automotive", "Vehicle Powertrain Engineer", "SPECIALIZATION_EXACT"),
        ("Mechanical + Robotics", "Robotics", "Industrial Robotics Engineer", "SPECIALIZATION_EXACT"),
        ("Mechanical + Manufacturing", "Manufacturing", "Production Engineering Intern", "SPECIALIZATION_EXACT"),
        ("Mechanical + CAD/CAM", "CAD/CAM", "CAD Design Engineer", "SPECIALIZATION_EXACT"),
        ("Civil + Structural", "Structural", "Bridge Structural Engineer", "SPECIALIZATION_EXACT"),
        ("Civil + Transportation", "Transportation", "Highway Engineering Intern", "SPECIALIZATION_EXACT"),
        ("Civil + Environmental", "Environmental", "Water Resources Engineer", "SPECIALIZATION_EXACT"),
        ("Chemical + Process Engineering", "Process Engineering", "Refinery Process Engineer", "SPECIALIZATION_EXACT"),
        ("Chemical + Petrochemical", "Petrochemical", "Petrochemical Processing Intern", "SPECIALIZATION_EXACT"),
        ("Biotechnology + Bioinformatics", "Bioinformatics", "Bioinformatics Research Intern", "SPECIALIZATION_EXACT"),
        ("Biomedical", "Biomedical", "Medical Devices Engineer", "SPECIALIZATION_EXACT"),
        ("Aerospace + Avionics", "Aerospace", "Avionics Systems Intern", "SPECIALIZATION_EXACT"),
    ]

    print("  [Test 1-22] Testing 22 Multi-Disciplinary Specialization Matches...")
    for label, candidate_spec, opp_title, expected_level in spec_tests:
        res = SpecializationSectorMatchingEngine.evaluate_specialization_compatibility(
            candidate_raw_spec=candidate_spec,
            opportunity_raw_spec=opp_title,
            opportunity_title=opp_title
        )
        assert res["specialization_match_level"] == expected_level, f"Failed {label}: candidate '{candidate_spec}', opp '{opp_title}', got {res['specialization_match_level']}"
        print(f"    - [OK] {label}: candidate '{candidate_spec}' -> opp '{opp_title}' ({res['specialization_match_level']})")

    # Test 23 & 24: Missing / Unknown Specialization Handling
    print("\n  [Test 23 & 24] Testing Unknown Specialization Handling...")
    res_no_cand = SpecializationSectorMatchingEngine.evaluate_specialization_compatibility(None, "VLSI")
    assert res_no_cand["specialization_match_level"] == "UNKNOWN"
    assert res_no_cand["specialization_match_score"] is None

    res_no_opp = SpecializationSectorMatchingEngine.evaluate_specialization_compatibility("VLSI", None, "", "")
    assert res_no_opp["specialization_match_level"] == "UNKNOWN"
    print("    - Unspecified candidate or opportunity specialization safely returns UNKNOWN without fabrication.")

    # Test 25-27: Related Specialization & Sector Evaluation
    print("\n  [Test 25-27] Testing Related Specialization & Sector Scoring...")
    res_rel_spec = SpecializationSectorMatchingEngine.evaluate_specialization_compatibility("AI/ML", "Data Science", "Data Science")
    assert res_rel_spec["specialization_match_level"] == "SPECIALIZATION_RELATED"
    assert res_rel_spec["specialization_match_score"] == 0.80

    res_sec_exact = SpecializationSectorMatchingEngine.evaluate_sector_compatibility("Automotive", "Automotive & EV Mobility")
    assert res_sec_exact["sector_match_level"] == "SECTOR_EXACT"
    assert res_sec_exact["sector_match_score"] == 0.75

    res_sec_rel = SpecializationSectorMatchingEngine.evaluate_sector_compatibility("Software", "Semiconductors")
    assert res_sec_rel["sector_match_level"] == "SECTOR_RELATED"
    assert res_sec_rel["sector_match_score"] == 0.60
    print("    - Related specialization (0.80), exact sector (0.75), and related sector (0.60) scoring verified.")

    # Test 28-33: Integration & Hard Gate Preservation
    print("\n  [Test 28-33] Testing Recommendation Pipeline Integration & Hard Gates...")
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

            # Test recommendation engine output includes Task 27C payload
            score, category, explanation = generate_recommendation_for_student(
                student=student,
                internship=opp,
                student_skills=["Python", "SQL"]
            )
            assert "specialization_match_level" in explanation
            assert "sector_match_level" in explanation
            assert "allocation_reason" in explanation
            print(f"    - Integrated Recommendation Engine output: spec_level='{explanation['specialization_match_level']}' | sector_level='{explanation['sector_match_level']}' | score={score}%")

    asyncio.run(_run())

    print("\n======================================================================")
    print("  TASK 27C SPECIALIZATION & SECTOR MATCHING: PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_specialization_sector_matching_suite()
