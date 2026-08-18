import sys
import os

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.leetcode.url_validator import validate_and_normalize_leetcode_url

def test_leetcode_url_validation_suite():
    print("\n======================================================================")
    print("  LEETCODE INTEGRATION TASK 3: PROFILE URL VALIDATION AUDIT TEST SUITE")
    print("======================================================================\n")

    # 1. Test Valid LeetCode URLs & Handles
    print("  [STEP 1] Testing Valid LeetCode Profile URLs and Plain Handles...")
    valid_test_cases = [
        ("https://leetcode.com/u/candidate_dev", "candidate_dev", "https://leetcode.com/u/candidate_dev"),
        ("https://www.leetcode.com/u/john_doe_99/", "john_doe_99", "https://leetcode.com/u/john_doe_99"),
        ("http://leetcode.com/alice-123", "alice-123", "https://leetcode.com/u/alice-123"),
        ("leetcode.com/u/py_master", "py_master", "https://leetcode.com/u/py_master"),
        ("candidate_dev", "candidate_dev", "https://leetcode.com/u/candidate_dev"),
        ("https://leetcode.cn/u/chinese_coder", "chinese_coder", "https://leetcode.cn/u/chinese_coder"),
    ]

    for raw, expected_username, expected_url in valid_test_cases:
        res = validate_and_normalize_leetcode_url(raw)
        print(f"    - Input: '{raw}'")
        print(f"      • Valid:        {res['valid']}")
        print(f"      • Username:     '{res['leetcode_username']}'")
        print(f"      • Normalized:   '{res['normalized_profile_url']}'")

        assert res["valid"] is True, f"Expected valid=True for '{raw}'"
        assert res["leetcode_username"] == expected_username, f"Expected username '{expected_username}', got '{res['leetcode_username']}'"
        assert res["normalized_profile_url"] == expected_url, f"Expected URL '{expected_url}', got '{res['normalized_profile_url']}'"
        assert res["error"] is None

    # 2. Test Invalid, Spoofed, & Malicious URLs
    print("\n  [STEP 2] Testing Invalid, Spoofed, and Malicious Input Payloads...")
    invalid_test_cases = [
        ("https://github.com/candidate_dev", "Unrelated domain (github.com)"),
        ("https://hackerrank.com/u/hacker", "Unrelated domain (hackerrank.com)"),
        ("https://leetcode.com.attacker.com/u/hacker", "Subdomain spoofing attack"),
        ("javascript:alert('xss')", "JavaScript XSS payload"),
        ("data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==", "Data URI payload"),
        ("file:///C:/Windows/System32/cmd.exe", "Local File URI payload"),
        ("https://leetcode.com/problems", "Reserved path (/problems)"),
        ("https://leetcode.com/contest", "Reserved path (/contest)"),
        ("https://leetcode.com/u/contest", "Reserved word username (/u/contest)"),
        ("https://leetcode.com/u/", "Missing username after /u/"),
        ("https://leetcode.com/u/ab", "Username too short (< 3 chars)"),
        ("https://leetcode.com/u/user<script>", "Special HTML characters in handle"),
        ("", "Empty string"),
        (None, "None value"),
        ("   ", "Whitespace string")
    ]

    for raw, reason in invalid_test_cases:
        res = validate_and_normalize_leetcode_url(raw)
        print(f"    - Invalid Input ({reason}): '{raw}'")
        print(f"      • Valid:  {res['valid']} | Error: '{res['error']}'")

        assert res["valid"] is False, f"Expected valid=False for '{raw}' ({reason})"
        assert res["leetcode_username"] is None
        assert res["normalized_profile_url"] is None
        assert res["error"] is not None

    print("\n======================================================================")
    print("  TASK 3 LEETCODE PROFILE URL VALIDATION VERIFICATION: PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_leetcode_url_validation_suite()
