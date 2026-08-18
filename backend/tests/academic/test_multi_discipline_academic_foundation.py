import asyncio
import sys
import os
import json
from sqlalchemy import select

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.db.database import AsyncSessionLocal, engine, Base
from app.db.models import StudentProfile, Internship
from app.services.academic_discipline import AcademicDisciplineService

from sqlalchemy import text

def test_multi_discipline_academic_foundation_suite():
    print("\n======================================================================")
    print("  TASK 27A: MULTI-DISCIPLINE ACADEMIC DATA FOUNDATION TEST SUITE")
    print("======================================================================\n")

    async def _run():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
            # Migration check for student_profiles table
            for col_def in [
                "academic_level VARCHAR(100)",
                "primary_discipline VARCHAR(255)",
                "normalized_discipline VARCHAR(100)",
                "specialization VARCHAR(255)",
                "sub_specialization VARCHAR(255)",
                "secondary_discipline VARCHAR(255)",
                "minor_discipline VARCHAR(255)"
            ]:
                try:
                    await conn.execute(text(f"ALTER TABLE student_profiles ADD COLUMN {col_def}"))
                except Exception:
                    pass

            # Migration check for internships table
            for col_def in [
                "required_disciplines_json TEXT",
                "accepted_disciplines_json TEXT",
                "related_disciplines_json TEXT",
                "discipline_scope VARCHAR(50) DEFAULT 'UNKNOWN'",
                "specializations_json TEXT",
                "discipline_confidence FLOAT DEFAULT 1.0",
                "original_requirement_text TEXT"
            ]:
                try:
                    await conn.execute(text(f"ALTER TABLE internships ADD COLUMN {col_def}"))
                except Exception:
                    pass

        async with AsyncSessionLocal() as db:
            # 1. Normalization Tests
            print("  [Test 1-7] Testing Standardized Discipline Normalizations...")
            
            cse_norm = AcademicDisciplineService.normalize_discipline("Computer Science & Engineering")
            assert cse_norm["normalized"] == "COMPUTER_SCIENCE"
            assert cse_norm["raw"] == "Computer Science & Engineering"
            print("    - CSE Normalization: 'Computer Science & Engineering' -> COMPUTER_SCIENCE")

            it_norm = AcademicDisciplineService.normalize_discipline("Information Technology")
            assert it_norm["normalized"] == "INFORMATION_TECHNOLOGY"
            print("    - IT Normalization: 'Information Technology' -> INFORMATION_TECHNOLOGY")

            ece_norm = AcademicDisciplineService.normalize_discipline("Electronics and Communication Engineering")
            assert ece_norm["normalized"] == "ELECTRONICS_COMMUNICATION"
            print("    - ECE Normalization: 'Electronics and Communication Engineering' -> ELECTRONICS_COMMUNICATION")

            eee_norm = AcademicDisciplineService.normalize_discipline("EEE")
            assert eee_norm["normalized"] == "ELECTRICAL_ELECTRONICS"
            print("    - EEE Normalization: 'EEE' -> ELECTRICAL_ELECTRONICS")

            vlsi_norm = AcademicDisciplineService.normalize_discipline("VLSI Design")
            assert vlsi_norm["normalized"] in ["VLSI", "VLSI_MICROELECTRONICS"]
            print(f"    - VLSI Normalization: 'VLSI Design' -> {vlsi_norm['normalized']}")

            mech_norm = AcademicDisciplineService.normalize_discipline("Mechanical")
            assert mech_norm["normalized"] == "MECHANICAL"
            print("    - Mechanical Normalization: 'Mechanical' -> MECHANICAL")

            civil_norm = AcademicDisciplineService.normalize_discipline("Civil Engineering")
            assert civil_norm["normalized"] == "CIVIL"
            print("    - Civil Normalization: 'Civil Engineering' -> CIVIL")

            # 2. Unknown Discipline & Original Wording Preservation
            print("\n  [Test 8 & 9] Testing Unknown Discipline & Original Wording Preservation...")
            unknown_norm = AcademicDisciplineService.normalize_discipline("Quantum Computing & Photonics Eng")
            assert unknown_norm["normalized"] == "UNKNOWN"
            assert unknown_norm["raw"] == "Quantum Computing & Photonics Eng"
            assert unknown_norm["is_known"] is False
            print("    - Unknown discipline raw wording preserved with UNKNOWN normalized key.")

            # 3. Candidate Academic Model Persistence
            print("\n  [Test 10] Testing Candidate Academic Profile Model Persistence...")
            res_st = await db.execute(select(StudentProfile).limit(1))
            student = res_st.scalar_one_or_none()
            assert student is not None

            student.academic_level = "Undergraduate"
            student.primary_discipline = "Computer Science & Engineering"
            student.normalized_discipline = cse_norm["normalized"]
            student.specialization = "Artificial Intelligence"
            await db.commit()
            await db.refresh(student)

            assert student.academic_level == "Undergraduate"
            assert student.primary_discipline == "Computer Science & Engineering"
            assert student.normalized_discipline == "COMPUTER_SCIENCE"
            assert student.specialization == "Artificial Intelligence"
            print("    - Candidate Academic Profile fields persisted successfully.")

            # 4. Opportunity Discipline Model & Scope Classification
            print("\n  [Test 11-13] Testing Opportunity Discipline Scope & Persistence...")
            scope_single = AcademicDisciplineService.classify_opportunity_discipline_scope(["COMPUTER_SCIENCE"], "CS Graduates")
            assert scope_single == "SPECIFIC_DISCIPLINE"

            scope_multi = AcademicDisciplineService.classify_opportunity_discipline_scope(["COMPUTER_SCIENCE", "INFORMATION_TECHNOLOGY"], "CS or IT")
            assert scope_multi == "MULTI_DISCIPLINE"

            scope_unknown = AcademicDisciplineService.classify_opportunity_discipline_scope([], None)
            assert scope_unknown == "UNKNOWN"
            print("    - Opportunity Discipline Scope classifications verified.")

            res_opp = await db.execute(select(Internship).limit(1))
            opp = res_opp.scalar_one_or_none()
            assert opp is not None

            opp.required_disciplines_json = json.dumps(["COMPUTER_SCIENCE", "INFORMATION_TECHNOLOGY"])
            opp.accepted_disciplines_json = json.dumps(["COMPUTER_SCIENCE", "INFORMATION_TECHNOLOGY", "ELECTRONICS_COMMUNICATION"])
            opp.discipline_scope = scope_multi
            opp.original_requirement_text = "Degree in Computer Science, Information Technology, or ECE required."
            await db.commit()
            await db.refresh(opp)

            assert opp.discipline_scope == "MULTI_DISCIPLINE"
            assert "COMPUTER_SCIENCE" in json.loads(opp.required_disciplines_json)
            print("    - Opportunity Discipline fields persisted successfully.")

            # 5. Backward Compatibility
            print("\n  [Test 14] Testing Backward Compatibility with Unmodified Records...")
            res_all_opps = await db.execute(select(Internship))
            all_opps = res_all_opps.scalars().all()
            for item in all_opps:
                assert hasattr(item, "discipline_scope")
                assert item.discipline_scope in ["SPECIFIC_DISCIPLINE", "MULTI_DISCIPLINE", "ALL_ENGINEERING", "ALL_TECHNOLOGY", "CROSS_DISCIPLINARY", "UNKNOWN"]
            print(f"    - Verified backward compatibility across {len(all_opps)} existing internship records.")

    asyncio.run(_run())

    print("\n======================================================================")
    print("  TASK 27A MULTI-DISCIPLINE ACADEMIC FOUNDATION: PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_multi_discipline_academic_foundation_suite()
