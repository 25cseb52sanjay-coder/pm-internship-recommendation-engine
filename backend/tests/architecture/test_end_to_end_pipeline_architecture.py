import asyncio
import sys
import os

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.database import AsyncSessionLocal, engine, Base
from app.db.models import StudentProfile, Internship, InternshipSkill, Skill, StudentSkill
from app.services.opportunity_quality import OpportunityQualityService
from app.services.recommendation import check_eligibility, generate_recommendation_for_student
from app.services.academic_discipline import AcademicDisciplineService
from app.services.branch_compatibility import BranchCompatibilityEngine
from app.services.specialization_sector_matching import SpecializationSectorMatchingEngine
from app.services.opportunity_role_intelligence import OpportunityRoleIntelligence
from app.services.candidate_evidence import CandidateEvidenceService

def test_end_to_end_pipeline_architecture_suite():
    print("\n======================================================================")
    print("  10-STAGE CANONICAL END-TO-END PIPELINE ARCHITECTURE AUDIT")
    print("======================================================================\n")

    async def _run():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with AsyncSessionLocal() as db:
            # Stage 1: Real Opportunities
            print("  [Stage 1] Real Opportunity Ingestion...")
            res_opp = await db.execute(
                select(Internship).options(
                    selectinload(Internship.skills).selectinload(InternshipSkill.skill)
                ).where(Internship.is_demo == False).limit(1)
            )
            opp = res_opp.scalar_one_or_none()
            assert opp is not None, "Real opportunity MUST exist in database!"
            print(f"    - Ingested Real Opportunity: '{opp.title}' from Source: '{opp.source}'")

            # Stage 2: Task 21 — Data Quality
            print("\n  [Stage 2] Task 21 — Data Quality & Active/Valid Gate...")
            is_quality_ok, gate_reasons = OpportunityQualityService.is_eligible_for_recommendation_ranking(opp)
            assert is_quality_ok is True, f"Opportunity MUST pass Data Quality Gate! Reasons: {gate_reasons}"
            print("    - Passed Task 21 Data Quality Gate 100%.")

            # Stage 3: Task 20 — Hard Eligibility
            print("\n  [Stage 3] Task 20 — Hard Mandatory Eligibility Gate...")
            res_st = await db.execute(select(StudentProfile).limit(1))
            student = res_st.scalar_one_or_none()
            assert student is not None
            is_eligible, elig_reasons = check_eligibility(student, opp)
            assert is_eligible is True, "Candidate MUST pass hard mandatory eligibility check!"
            print("    - Passed Task 20 Hard Eligibility Gate 100%.")

            # Stage 4: Task 27A — Academic Discipline
            print("\n  [Stage 4] Task 27A — Academic Discipline Normalization...")
            cand_discipline = AcademicDisciplineService.normalize_discipline(student.primary_discipline or student.branch)
            assert cand_discipline["normalized"] is not None
            print(f"    - Normalized Candidate Discipline: '{cand_discipline['raw']}' -> {cand_discipline['normalized']}")

            # Stage 5: Task 27B — Branch Compatibility
            print("\n  [Stage 5] Task 27B — Branch Compatibility Engine...")
            branch_eval = BranchCompatibilityEngine.evaluate_compatibility(
                candidate_raw_branch=student.primary_discipline or student.branch,
                discipline_scope=opp.discipline_scope or "UNKNOWN"
            )
            assert branch_eval["compatibility_level"] != "INCOMPATIBLE", "Candidate branch MUST be compatible!"
            print(f"    - Branch Compatibility Level: {branch_eval['compatibility_level']} (Score: {branch_eval['compatibility_score']})")

            # Stage 6: Task 27C — Specialization + Sector
            print("\n  [Stage 6] Task 27C — Specialization & Sector Matching...")
            spec_eval = SpecializationSectorMatchingEngine.evaluate_specialization_compatibility(
                candidate_raw_spec=student.specialization,
                opportunity_raw_spec=opp.title,
                opportunity_title=opp.title
            )
            sector_eval = SpecializationSectorMatchingEngine.evaluate_sector_compatibility(
                candidate_target_sector=student.preferred_industry,
                opportunity_sector=opp.company_sector
            )
            print(f"    - Specialization Level: {spec_eval['specialization_match_level']} | Sector Level: {sector_eval['sector_match_level']}")

            # Stage 7: Task 27D — Actual Role + Domain Intelligence
            print("\n  [Stage 7] Task 27D — Actual Role & Domain Intelligence...")
            opp_role = OpportunityRoleIntelligence.classify_opportunity_role(opp.title, opp.description)
            role_eval = OpportunityRoleIntelligence.evaluate_role_compatibility(
                candidate_target_role=student.preferred_role,
                candidate_specialization=student.specialization,
                opportunity_role_info=opp_role
            )
            print(f"    - Role Match Level: {role_eval['role_match_level']} | Domain: '{opp_role['role_family']}'")

            # Stage 8: Candidate Evidence + Skills & AI Ranking
            print("\n  [Stage 8] Candidate Evidence + Skills & AI Ranking...")
            skills_res = await db.execute(
                select(Skill.name).join(StudentSkill, Skill.id == StudentSkill.skill_id).where(StudentSkill.student_id == student.id)
            )
            st_skill_names = list(skills_res.scalars().all()) or ["Python", "SQL"]

            score, category, exp_dict = generate_recommendation_for_student(
                student=student,
                internship=opp,
                student_skills=st_skill_names
            )
            assert score >= 0.0 and score <= 100.0
            print(f"    - AI Match Index: {score}/100 | Category: '{category}'")

            # Stage 9: Structured Explainability Payload
            print("\n  [Stage 9] Structured Explainability Payload...")
            assert "academic_match_level" in exp_dict
            assert "specialization_match_level" in exp_dict
            assert "role_match_level" in exp_dict
            assert "evidence_used" in exp_dict
            assert "confidence" in exp_dict
            print(f"    - Explanation Allocation Reason: '{exp_dict.get('allocation_reason', exp_dict.get('recommendation_reason'))}'")

            # Stage 10: Original Apply URL Direct Redirection
            print("\n  [Stage 10] Apply Now -> Original Source URL Target Verification...")
            target_apply_url = opp.apply_url or opp.source_url
            assert target_apply_url is not None and (target_apply_url.startswith("http://") or target_apply_url.startswith("https://"))
            print(f"    - Direct Target Destination URL: '{target_apply_url}'")

    asyncio.run(_run())

    print("\n======================================================================")
    print("  10-STAGE CANONICAL PIPELINE ARCHITECTURE: VERIFIED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_end_to_end_pipeline_architecture_suite()
