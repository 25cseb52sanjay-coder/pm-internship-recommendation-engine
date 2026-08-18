import os
import sys
import json
import urllib.request

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

PROFILE_PAGE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "frontend", "src", "app", "profile", "page.tsx")
)


def load_profile_page() -> str:
    assert os.path.exists(PROFILE_PAGE), f"Profile page not found at: {PROFILE_PAGE}"
    with open(PROFILE_PAGE, "r", encoding="utf-8") as f:
        return f.read()


def test_skills_category_dropdown_suite():
    print("\n======================================================================")
    print("  TECHNICAL & SOFT SKILLS MATRIX SELECTORS TEST SUITE (Suite 78)")
    print("======================================================================\n")

    # 1. Verify Pydantic schema changes
    print("  [Test 1] Verifying StudentProfileCreate schema has List[Any] annotation for skills...")
    from app.schemas.student import StudentProfileCreate
    field_info = StudentProfileCreate.model_fields["skills"]
    assert str(field_info.annotation) == "typing.List[typing.Any]", f"skills field must be List[Any], got {field_info.annotation}"
    print("    - StudentProfileCreate schema verified (List[Any] accepted).")

    # 2. Verify backend update_profile robustness with strings, dicts and models
    print("\n  [Test 2] Verifying backend update_profile robustness manually...")
    from tests.auth_helper import get_student_token, get_test_base_url
    base_url = get_test_base_url()
    token = get_student_token()

    # GET profile
    req_get = urllib.request.Request(f"{base_url}/api/v1/students/profile", headers={"Authorization": f"Bearer {token}"})
    resp_get = urllib.request.urlopen(req_get)
    profile = json.loads(resp_get.read().decode())

    # We send mixed skills payload containing: string, legacy model representation, and the new category-skill dict
    profile["skills"] = [
        "C++",
        {"name": "React", "category": "Web Development"},
        {"category": "AI / Machine Learning", "skill": "Machine Learning", "display_category": "AI / Machine Learning", "display_skill": "Machine Learning"}
    ]

    req_post = urllib.request.Request(
        f"{base_url}/api/v1/students/profile",
        data=json.dumps(profile).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST"
    )
    
    resp_post = urllib.request.urlopen(req_post)
    assert resp_post.status == 200, f"Expected HTTP 200, got {resp_post.status}"
    updated_profile = json.loads(resp_post.read().decode())
    
    # Verify that the skills were correctly processed and linked
    saved_skills = updated_profile.get("skills", [])
    saved_names = [s["name"] for s in saved_skills]
    
    assert "C++" in saved_names, f"C++ missing from saved skills: {saved_names}"
    assert "React" in saved_names, f"React missing from saved skills: {saved_names}"
    assert "Machine Learning" in saved_names, f"Machine Learning missing from saved skills: {saved_names}"
    print("    - Mixed format saving and parsing successfully verified in backend database.")

    # 3. Verify Frontend file contains required Category Options and Skill Mappings
    print("\n  [Test 3] Verifying frontend file contains CATEGORY_OPTIONS and SKILL_MAPPING...")
    content = load_profile_page()

    assert "CATEGORY_OPTIONS" in content, "CATEGORY_OPTIONS constant missing in page.tsx"
    assert "SKILL_MAPPING" in content, "SKILL_MAPPING constant missing in page.tsx"
    assert "Programming Languages" in content, "Programming Languages category missing in page.tsx"
    assert "AI / Machine Learning" in content, "AI / Machine Learning category missing in page.tsx"
    assert "Databases" in content, "Databases category missing in page.tsx"
    print("    - Taxonomy and category mapping presence verified.")

    # 4. Verify Frontend has correct searchable dropdown states and selectors UI
    print("\n  [Test 4] Verifying dependent dropdown components and state hooks in frontend UI...")
    assert "selectedSkillCategory" in content, "selectedSkillCategory state variable missing"
    assert "selectedSkillName" in content, "selectedSkillName state variable missing"
    assert "customSkillName" in content, "customSkillName state variable missing"
    assert "categoryDropdownOpen" in content, "categoryDropdownOpen state variable missing"
    assert "skillDropdownOpen" in content, "skillDropdownOpen state variable missing"
    assert "Select a skill category" in content, "Category selector placeholder missing"
    assert "Select a skill" in content, "Skill selector placeholder missing"
    assert "Select a category first" in content, "Disabled skill selector placeholder missing"
    print("    - Dependent searchable dropdown states and placeholder strings verified.")

    # 5. Verify Frontend logic for Category selection triggers, and Other custom input
    print("\n  [Test 5] Verifying dependency trigger, Add Skill button, and custom input for Other category...")
    assert "disabled={!selectedSkillCategory}" in content, "Skill dropdown must be disabled when category is not selected"
    assert "selectedSkillCategory === \"Other\"" in content, "Other category path must be supported"
    assert "+ Add Skill" in content or "Add Skill" in content, "Add Skill button label verified"
    assert "display_category" in content, "display_category key present in stored structure"
    assert "display_skill" in content, "display_skill key present in stored structure"
    print("    - Dependency triggers, dynamic interactive states, and stored structure keys verified.")

    print("\n======================================================================")
    print("  TECHNICAL & SOFT SKILLS MATRIX SELECTORS SUITE: PASSED (100% SUCCESS)")
    print("======================================================================\n")


if __name__ == "__main__":
    try:
        test_skills_category_dropdown_suite()
    except AssertionError as e:
        print(f"Assertion Error: {e}")
        sys.exit(1)
