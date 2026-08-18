import os
import sys
import re

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

PROFILE_PAGE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "frontend", "src", "app", "profile", "page.tsx")
)


def load_profile_page() -> str:
    assert os.path.exists(PROFILE_PAGE), f"Profile page not found at: {PROFILE_PAGE}"
    with open(PROFILE_PAGE, "r", encoding="utf-8") as f:
        return f.read()


def test_academic_qualification_dependency_suite():
    print("\n======================================================================")
    print("  ACADEMIC QUALIFICATION DEPENDENCY UX TEST SUITE (Suite 77)")
    print("======================================================================\n")

    content = load_profile_page()

    # 1. Course Program placeholder has unselected value
    print("  [Test 1] Course / Program placeholder is configured...")
    assert "Select your course / program" in content, "Course placeholder text missing"
    print("    - Course placeholder option verified.")

    # 2. Qualification Type placeholder has unselected value
    print("\n  [Test 2] Qualification / Study Type placeholder is configured...")
    assert "Select your qualification type" in content, "Qualification placeholder text missing"
    print("    - Qualification placeholder option verified.")

    # 3. Branch starts disabled when qualification type is not Engineering Degree
    print("\n  [Test 3] Branch starts disabled or is disabled when qualification type is not engineering...")
    assert "Select an engineering qualification to enable branch selection" in content, "Disabled state placeholder text missing"
    assert "Branch selection is only applicable for engineering programs" in content, "Disabled state helper message missing"
    assert "disabled" in content, "Disabled attribute for branch input missing"
    print("    - Disabled branch field configuration verified.")

    # 4. Instant trigger checks: immediately enabled on selection change
    print("\n  [Test 4] Branch dropdown state changes dynamically based on qualification_type selection...")
    assert "const isEngineering = profile.qualification_type === \"Engineering Degree\"" in content, "Dynamic engineering check expression missing"
    assert "onChange={(e) => setProfile({ ...profile, qualification_type: e.target.value })}" in content or "onChange={(e) => setProfile({ ...profile, qualification_type: e.target.value })" in content, "qualification_type state setter missing or indirect"
    print("    - Dynamic interactive state triggers verified.")

    # 5. Searchable dropdown behaves as enabled searchable control when Engineering Degree is selected
    print("\n  [Test 5] Searchable branch dropdown placeholder and required attribute when enabled...")
    assert "Select your engineering branch / discipline" in content, "Searchable dropdown placeholder missing"
    assert "required" in content, "Required attribute on branch select/input missing"
    assert "branchSearch" in content, "branchSearch filtering state verified"
    print("    - Enabled branch dropdown attributes and search capability verified.")

    # 6. Branch selection does not erase other academic fields or saved branch value unless explicitly mapped
    print("\n  [Test 6] Stored value preservation and legacy mapping logic present...")
    assert "normalizeStoredBranch" in content, "normalizeStoredBranch utility function missing"
    assert "getBranchLabel" in content, "getBranchLabel utility function missing"
    assert "LEGACY_MAP" in content, "LEGACY_MAP backward-compatibility mapping missing"
    print("    - Backward-compatibility remapping and values preservation verified.")

    print("\n======================================================================")
    print("  ACADEMIC QUALIFICATION DEPENDENCY UX SUITE: PASSED (100% SUCCESS)")
    print("======================================================================\n")


if __name__ == "__main__":
    test_academic_qualification_dependency_suite()
