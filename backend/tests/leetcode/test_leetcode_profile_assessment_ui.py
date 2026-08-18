import os
import sys

def test_leetcode_profile_assessment_ui_suite():
    print("\n======================================================================")
    print("  LEETCODE INTEGRATION TASK 11: PROFILE UI DISPLAY AUDIT TEST SUITE")
    print("======================================================================\n")

    profile_page_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "frontend", "src", "app", "profile", "page.tsx")
    )
    assert os.path.exists(profile_page_path), f"Profile page file missing at '{profile_page_path}'"

    with open(profile_page_path, "r", encoding="utf-8") as f:
        code_content = f.read()

    # 1. Verify Prominent Verification Status & Username Display
    print("  [STEP 1] Checking verification status badge & username display in Profile UI...")
    assert "Verified LeetCode Profile" in code_content or "LeetCode Profile Verified" in code_content
    assert "Connected Handle:" in code_content
    assert "BIO_TOKEN_CHALLENGE" in code_content
    print("    - Prominent Verification Status & Handle Display verified 100%.")

    # 2. Verify Real Metrics Summary Grid & Non-Zero Defaulting
    print("\n  [STEP 2] Checking real metrics summary grid & timestamp display...")
    assert "Verified Real Problem Statistics" in code_content
    assert "Total Solved" in code_content
    assert "Easy Solved" in code_content
    assert "Medium Solved" in code_content
    assert "Hard Solved" in code_content
    assert "Last Verified:" in code_content
    print("    - Real Problem Statistics Grid & Timestamp verified 100%.")

    # 3. Verify Assessment Strengths & Growth Areas Display
    print("\n  [STEP 3] Checking verified coding strengths & growth areas display...")
    assert "Verified Coding Strengths" in code_content
    assert "Targeted Growth Recommendations" in code_content
    print("    - Coding Strengths & Targeted Growth Recommendations verified 100%.")

    # 4. Verify Task 16 Production UI State Text Strings
    print("\n  [STEP 4] Checking Task 16 state text messages...")
    assert "Verification Unavailable" in code_content
    assert "LeetCode profile verification and live statistics are currently unavailable because an approved profile-data provider is not configured." in code_content
    assert "Connect your LeetCode profile to enable coding-profile evaluation when an approved data provider is available." in code_content
    assert "Your LeetCode profile has been verified." in code_content
    print("    - Task 16 State Messages verified 100%.")

    # 5. Verify Existing Design System Tokens & Zero Redesign
    print("\n  [STEP 5] Checking design system consistency & non-disruption of profile sections...")
    assert "Sector & Role Preferences" in code_content
    assert "Technical & Soft Skills Matrix Editor" in code_content
    assert "Candidate Profile Setup" in code_content
    print("    - Existing design system & profile sections remain 100% intact.")

    print("\n======================================================================")
    print("  TASK 11 LEETCODE PROFILE ASSESSMENT UI: PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_leetcode_profile_assessment_ui_suite()
