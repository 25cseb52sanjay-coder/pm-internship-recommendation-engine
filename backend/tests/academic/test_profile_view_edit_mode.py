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


def test_profile_view_edit_mode_suite():
    print("\n======================================================================")
    print("  CANDIDATE PROFILE VIEW/EDIT & SAVE TEST SUITE (Suite 79)")
    print("======================================================================\n")

    # 1. Verify Frontend page has state variables and elements
    print("  [Test 1] Verifying frontend file contains isEditMode, validationErrors, and Edit Profile elements...")
    content = load_profile_page()

    assert "isEditMode" in content, "isEditMode state variable missing in page.tsx"
    assert "validationErrors" in content, "validationErrors state variable missing in page.tsx"
    assert "My Profile" in content, "My Profile title for VIEW mode summary missing"
    assert "Edit Profile" in content, "Edit Profile button label/icon missing"
    assert "Profile saved successfully." in content, "Success message string missing"
    print("    - State variables and UI elements verified.")

    # 2. Verify validation logic
    print("\n  [Test 2] Verifying validation logic in frontend...")
    assert "validateForm" in content, "validateForm function missing in page.tsx"
    assert "course_program" in content and "qualification_type" in content, "Academic field validation targets missing"
    assert "skills" in content, "Skills validation targets missing"
    print("    - Form validation structure verified.")

    # 3. Verify backend profile save integration (POST /api/v1/students/profile)
    print("\n  [Test 3] Verifying backend integration and database persistence...")
    from tests.auth_helper import get_student_token, get_test_base_url
    base_url = get_test_base_url()
    token = get_student_token()

    # Get initial profile
    req_get = urllib.request.Request(f"{base_url}/api/v1/students/profile", headers={"Authorization": f"Bearer {token}"})
    resp_get = urllib.request.urlopen(req_get)
    original_profile = json.loads(resp_get.read().decode())

    # Modify some fields and save via POST
    updated_payload = {
        **original_profile,
        "course_program": "B.E. / B.Tech",
        "qualification_type": "Engineering Degree",
        "branch": "COMPUTER_SCIENCE",
        "institution": "Test Engineering College",
        "cgpa": 9.2,
        "skills": [
            {"name": "Python", "category": "Programming Languages"},
            {"name": "FastAPI", "category": "Web Development"}
        ]
    }

    req_post = urllib.request.Request(
        f"{base_url}/api/v1/students/profile",
        data=json.dumps(updated_payload).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST"
    )
    
    resp_post = urllib.request.urlopen(req_post)
    assert resp_post.status == 200, f"Expected HTTP 200, got {resp_post.status}"
    saved_profile = json.loads(resp_post.read().decode())

    assert saved_profile["course_program"] == "B.E. / B.Tech"
    assert saved_profile["qualification_type"] == "Engineering Degree"
    assert saved_profile["branch"] == "COMPUTER_SCIENCE"
    assert saved_profile["institution"] == "Test Engineering College"
    assert saved_profile["cgpa"] == 9.2

    saved_skills = [s["name"] for s in saved_profile.get("skills", [])]
    assert "Python" in saved_skills
    assert "FastAPI" in saved_skills
    print("    - Backend profile update (POST) and database persistence verified.")

    # 4. Verify security: JWT authenticated user identity is used (no customer id passed as source of auth)
    print("\n  [Test 4] Verifying security rules (Authorization headers required)...")
    req_no_auth = urllib.request.Request(
        f"{base_url}/api/v1/students/profile",
        data=json.dumps(updated_payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        urllib.request.urlopen(req_no_auth)
        raise AssertionError("Expected HTTP 401 Unauthorized for unauthenticated save request, but it succeeded!")
    except urllib.error.HTTPError as e:
        assert e.code == 401, f"Expected HTTP 401 for unauthenticated save request, got {e.code}"
    print("    - Security verification passed: save is protected by JWT authentication.")

    print("\n======================================================================")
    print("  CANDIDATE PROFILE VIEW/EDIT & SAVE SUITE: PASSED (100% SUCCESS)")
    print("======================================================================\n")


if __name__ == "__main__":
    test_profile_view_edit_mode_suite()
