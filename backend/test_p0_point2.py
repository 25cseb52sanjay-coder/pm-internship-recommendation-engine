import asyncio
from app.db.database import AsyncSessionLocal
from app.db.models import StudentProfile, Internship, Skill, InternshipSkill
from app.services.recommendation import generate_recommendation_for_student
from sqlalchemy import select

def test_recommendation_explainability():
    print("\n======================================================================")
    print("  AUDIT TEST: P0 POINT 2 — RECOMMENDATION EXPLAINABILITY PAYLOAD")
    print("======================================================================\n")

    # Mock Candidate & Opportunity
    student = StudentProfile(
        id=1,
        degree="B.Tech",
        branch="Computer Science",
        age=22,
        preferred_location="Mumbai",
        work_mode="On-site",
        preferred_duration="6 Months",
        projects_summary="AI & Python Data Engineering Projects"
    )
    
    internship = Internship(
        id=1,
        title="AI Engineering Intern",
        company_name="ISRO Telemetry",
        company_sector="Public Sector / Aerospace",
        description="Develop AI data processing pipelines using Python, SQL, and Deep Learning models.",
        location="Mumbai",
        work_mode="On-site",
        duration="6 Months",
        min_age=21,
        max_age=24,
        preferred_degree="B.Tech"
    )

    # Attach required and preferred skills
    skill1 = Skill(id=1, name="Python", category="Programming")
    skill2 = Skill(id=2, name="SQL", category="Database")
    skill3 = Skill(id=3, name="PyTorch", category="AI")
    
    sk1 = InternshipSkill(skill=skill1, is_required=True)
    sk2 = InternshipSkill(skill=skill2, is_required=True)
    sk3 = InternshipSkill(skill=skill3, is_required=True)

    internship.skills = [sk1, sk2, sk3]

    # Candidate skills (has Python, SQL, missing PyTorch)
    candidate_skills = ["Python", "SQL"]

    score, match_cat, payload = generate_recommendation_for_student(
        student=student,
        internship=internship,
        student_skills=candidate_skills
    )

    print(f"  [1] Overall Score: {score}/100 | Category: '{match_cat}'")
    print(f"  [2] Matched Skills: {payload['matched_skills']}")
    print(f"  [3] Missing Required Skills: {payload['missing_required_skills']}")
    print(f"  [4] Dynamic Strengths Count: {len(payload['strengths'])} -> {payload['strengths']}")
    print(f"  [5] Dynamic Weaknesses Count: {len(payload['weaknesses'])} -> {payload['weaknesses']}")
    print(f"  [6] Category Breakdown: {payload['breakdown']}")

    # Verification assertions
    assert "strengths" in payload, "Missing 'strengths' in explanation payload"
    assert "weaknesses" in payload, "Missing 'weaknesses' in explanation payload"
    assert "breakdown" in payload, "Missing 'breakdown' in explanation payload"
    assert len(payload['matched_skills']) == 2, f"Expected 2 matched skills, got {len(payload['matched_skills'])}"
    assert "PyTorch" in payload['missing_required_skills'], "Expected 'PyTorch' in missing_required_skills"

    print("\n======================================================================")
    print("  VERIFICATION RESULT: P0 POINT 2 PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_recommendation_explainability()
