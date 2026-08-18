import urllib.request
import json
import sys
import os

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from tests.auth_helper import get_student_token, get_admin_token, get_test_base_url

def test_admin_rbac_enforcement():
    print("\n======================================================================")
    print("  AUDIT TEST: P0 POINT 7 — ADMIN ROLE-BASED ACCESS CONTROL (RBAC)")
    print("======================================================================\n")

    base_url = get_test_base_url()

    # 1. Login as STUDENT user to get Student JWT Token via auth_helper
    student_token = get_student_token()
    print("  [1] Student Authentication: SUCCESS (Student JWT Issued)")

    # 2. Login as ADMIN user to get Admin JWT Token via auth_helper
    admin_token = get_admin_token()
    print("  [2] Admin Authentication: SUCCESS (Admin JWT Issued)")

    # 3. Test Student Attempt on Admin Analytics API -> MUST RETURN HTTP 403 FORBIDDEN
    try:
        stud_req = urllib.request.Request(
            f'{base_url}/api/v1/admin/analytics',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        urllib.request.urlopen(stud_req)
        print("  ✗ Student Access to Admin Analytics: FAILED (Unauthorized Access Allowed)")
        sys.exit(1)
    except urllib.error.HTTPError as e:
        print(f"  [3] Student Access to Admin Analytics: DENIED (HTTP {e.code} Forbidden - {e.reason})")
        assert e.code == 403, f"Expected HTTP 403 Forbidden, got {e.code}"

    # 4. Test Student Attempt on Admin Scheme Rules Config API -> MUST RETURN HTTP 403 FORBIDDEN
    try:
        rule_payload = json.dumps({'rule_code': 'HACK_01', 'rule_name': 'Unauthorized Rule', 'min_age': 18, 'max_age': 30}).encode()
        stud_rule_req = urllib.request.Request(
            f'{base_url}/api/v1/rules/configure',
            data=rule_payload,
            headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {student_token}'}
        )
        urllib.request.urlopen(stud_rule_req)
        print("  ✗ Student Access to Scheme Rules Config: FAILED")
        sys.exit(1)
    except urllib.error.HTTPError as e:
        print(f"  [4] Student Access to Scheme Rules Config: DENIED (HTTP {e.code} Forbidden - {e.reason})")
        assert e.code == 403, f"Expected HTTP 403 Forbidden, got {e.code}"

    # 5. Test Authorized Admin Access on Admin Analytics API -> MUST RETURN HTTP 200 OK
    admin_req = urllib.request.Request(
        f'{base_url}/api/v1/admin/analytics',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    admin_resp = urllib.request.urlopen(admin_req)
    print(f"  [5] Authorized Admin Access to Analytics: PASSED (HTTP {admin_resp.status} OK)")
    assert admin_resp.status == 200

    print("\n======================================================================")
    print("  VERIFICATION RESULT: P0 POINT 7 PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_admin_rbac_enforcement()
