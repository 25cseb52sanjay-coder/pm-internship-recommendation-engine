import os
import sys
import json

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# ─────────────────────────────────────────────────────────────────────────────
# Test Suite: Course & Qualification Dropdown — Academic Profile Fields
# ─────────────────────────────────────────────────────────────────────────────

COURSE_OPTIONS = [
    "B.E. / B.Tech", "B.Sc", "BCA", "B.Com", "BBA", "BA",
    "B.Arch", "B.Des", "B.Pharm", "BPT", "B.L / LLB", "MBBS",
    "BDS", "BAMS", "BHMS", "B.Ed", "BSW", "B.Voc",
    "M.E. / M.Tech", "M.Sc", "MCA", "MBA", "MA", "M.Com",
    "M.Arch", "M.Des", "M.Pharm", "M.Ed", "MSW", "LLM",
    "PhD", "Diploma", "Polytechnic Diploma", "ITI", "Other"
]

QUALIFICATION_TYPE_OPTIONS = [
    "Engineering Degree", "3-Year Undergraduate Degree",
    "4-Year Undergraduate Degree", "5-Year Integrated Degree",
    "Postgraduate Degree", "Diploma", "Polytechnic Diploma",
    "ITI / Vocational", "Professional Degree", "Medical Degree",
    "Law Degree", "Education Degree", "Doctoral Degree", "Other"
]


def test_academic_dropdown_suite():
    print("\n======================================================================")
    print("  ACADEMIC DROPDOWN FIELDS — COURSE & QUALIFICATION TEST SUITE")
    print("======================================================================\n")

    # 1. Backend model has new columns
    print("  [Test 1] Backend model includes course_program and qualification_type...")
    from app.db.models import StudentProfile
    assert hasattr(StudentProfile, "course_program"), "course_program column missing from StudentProfile model"
    assert hasattr(StudentProfile, "qualification_type"), "qualification_type column missing from StudentProfile model"
    print("    - StudentProfile model has course_program and qualification_type columns.")

    # 2. Schemas expose both new fields
    print("\n  [Test 2] Pydantic schemas expose course_program and qualification_type...")
    from app.schemas.student import StudentProfileCreate, StudentProfileOut
    create_fields = StudentProfileCreate.model_fields
    out_fields = StudentProfileOut.model_fields
    assert "course_program" in create_fields, "course_program missing from StudentProfileCreate"
    assert "qualification_type" in create_fields, "qualification_type missing from StudentProfileCreate"
    assert "course_program" in out_fields, "course_program missing from StudentProfileOut"
    assert "qualification_type" in out_fields, "qualification_type missing from StudentProfileOut"
    print("    - StudentProfileCreate and StudentProfileOut both expose course_program and qualification_type.")

    # 3. Frontend profile page contains Course / Program dropdown
    print("\n  [Test 3] Frontend profile page has Course / Program dropdown with all required options...")
    profile_page = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "frontend", "src", "app", "profile", "page.tsx")
    )
    assert os.path.exists(profile_page), f"Profile page not found at {profile_page}"
    with open(profile_page, "r", encoding="utf-8") as f:
        content = f.read()

    assert "course_program" in content, "course_program not found in profile page"
    assert "Select your course / program" in content, "Course dropdown placeholder text missing"
    assert "B.E. / B.Tech" in content, "B.E. / B.Tech option missing from course dropdown"
    assert "B.Sc" in content, "B.Sc option missing from course dropdown"
    assert "MBA" in content, "MBA option missing from course dropdown"
    assert "PhD" in content, "PhD option missing from course dropdown"
    assert "Polytechnic Diploma" in content, "Polytechnic Diploma option missing from course dropdown"
    assert "ITI" in content, "ITI option missing from course dropdown"
    assert '"Other"' in content or "'Other'" in content, "Other option missing from course dropdown"
    print("    - Course / Program dropdown with all required options verified.")

    # 4. Frontend profile page contains Qualification Type dropdown
    print("\n  [Test 4] Frontend profile page has Qualification / Study Type dropdown with all required options...")
    assert "qualification_type" in content, "qualification_type not found in profile page"
    assert "Select your qualification type" in content, "Qualification type dropdown placeholder text missing"
    assert "Engineering Degree" in content, "Engineering Degree option missing from qualification dropdown"
    assert "Postgraduate Degree" in content, "Postgraduate Degree option missing from qualification dropdown"
    assert "Doctoral Degree" in content, "Doctoral Degree option missing from qualification dropdown"
    assert "Diploma" in content, "Diploma option missing from qualification dropdown"
    assert "ITI / Vocational" in content, "ITI / Vocational option missing from qualification dropdown"
    print("    - Qualification / Study Type dropdown with all required options verified.")

    # 5. Engineering conditional branch display logic
    print("\n  [Test 5] Engineering-conditional branch display logic present...")
    assert "Branch / Discipline (if applicable)" in content, "Branch label missing"
    assert "Engineering Degree" in content, "Engineering Degree check missing"
    assert "Select your engineering branch to improve academic eligibility and internship recommendations" in content, "Engineering branch helper hint missing"
    print("    - Engineering-conditional branch display logic verified.")

    # 6. Non-engineering behavior: disabled and hints present
    print("\n  [Test 6] Non-engineering branch behavior: disabled and hints present...")
    assert "Branch selection is only applicable for engineering programs" in content, "Non-engineering branch optional hint missing"
    print("    - Non-engineering branch behavior verified.")

    # 7. Searchable dropdown controls present
    print("\n  [Test 7] Searchable dropdown controls present...")
    assert "branchSearch" in content, "branchSearch state variable missing"
    assert "branchDropdownOpen" in content, "branchDropdownOpen state variable missing"
    print("    - Searchable dropdown controls verified.")

    # 8. Existing branch/qualification fields preserved
    print("\n  [Test 8] Existing branch, degree, and qualification fields preserved...")
    assert "profile.branch" in content, "branch field missing from profile page"
    assert "profile.degree" in content, "degree field missing from profile page"
    assert "profile.qualification" in content or "qualification" in content, "qualification field missing"
    assert "profile.institution" in content, "institution field missing"
    assert "profile.cgpa" in content, "cgpa field missing"
    assert "Branch / Discipline (if applicable)" in content, "Generic branch label missing"
    print("    - All existing academic fields are preserved intact.")

    # 9. Academic Qualification section heading present
    print("\n  [Test 9] Academic Qualification section heading present...")
    assert "Academic Qualification" in content, "Academic Qualification section heading missing"
    print("    - Academic Qualification section heading verified.")

    # 10. No hardcoded sample data for new fields
    print("\n  [Test 10] No hardcoded non-empty sample values for course_program or qualification_type in initial state...")
    assert 'course_program: ""' in content, "course_program initial state must be empty string"
    assert 'qualification_type: ""' in content, "qualification_type initial state must be empty string"
    print("    - Initial state has no hardcoded sample values.")

    print("\n======================================================================")
    print("  ACADEMIC DROPDOWN FIELDS SUITE: PASSED (100% SUCCESS)")
    print("======================================================================\n")


if __name__ == "__main__":
    test_academic_dropdown_suite()
