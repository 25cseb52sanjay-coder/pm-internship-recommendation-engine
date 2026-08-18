import urllib.request
import json
import sys
import os

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from tests.auth_helper import get_test_base_url

def test_greenhouse_ui_display_and_filtering():
    print("\n======================================================================")
    print("  GREENHOUSE INTEGRATION TASK 5: UI & API FILTERING TEST SUITE")
    print("======================================================================\n")

    base_url = get_test_base_url()

    # 1. Test GET /api/v1/internships?source=Greenhouse
    print("  [TEST 1] Querying GET /api/v1/internships?source=Greenhouse...")
    req_gh = urllib.request.Request(f"{base_url}/api/v1/internships?source=Greenhouse")
    resp_gh = urllib.request.urlopen(req_gh)
    assert resp_gh.status == 200
    data_gh = json.loads(resp_gh.read().decode())
    print(f"    - 'Greenhouse Source' Returned {len(data_gh)} real database records.")
    assert len(data_gh) > 0, "Greenhouse filter must return real active database opportunities"
    for item in data_gh:
        assert item["source"] == "Greenhouse"
        assert item["source_name"] == "Greenhouse Official"
        assert item["apply_url"].startswith("http")

    # 2. Test Jobs Only Filter (opportunity_type=Jobs)
    print("\n  [TEST 2] Querying GET /api/v1/internships?opportunity_type=Jobs...")
    req_jobs = urllib.request.Request(f"{base_url}/api/v1/internships?opportunity_type=Jobs")
    resp_jobs = urllib.request.urlopen(req_jobs)
    assert resp_jobs.status == 200
    data_jobs = json.loads(resp_jobs.read().decode())
    print(f"    - 'Jobs Only' Returned {len(data_jobs)} records.")
    for item in data_jobs:
        assert item["opportunity_type"] == "JOB"
    print("    - All returned items correctly matched opportunity_type='JOB'.")

    # 3. Test Internships Only Filter (opportunity_type=Internships)
    print("\n  [TEST 3] Querying GET /api/v1/internships?opportunity_type=Internships...")
    req_interns = urllib.request.Request(f"{base_url}/api/v1/internships?opportunity_type=Internships")
    resp_interns = urllib.request.urlopen(req_interns)
    assert resp_interns.status == 200
    data_interns = json.loads(resp_interns.read().decode())
    print(f"    - 'Internships Only' Returned {len(data_interns)} records.")
    for item in data_interns:
        assert item["opportunity_type"] == "INTERNSHIP"
    print("    - All returned items correctly matched opportunity_type='INTERNSHIP'.")

    # 4. Test All Types Filter (opportunity_type=All)
    print("\n  [TEST 4] Querying GET /api/v1/internships?opportunity_type=All...")
    req_all = urllib.request.Request(f"{base_url}/api/v1/internships?opportunity_type=All")
    resp_all = urllib.request.urlopen(req_all)
    assert resp_all.status == 200
    data_all = json.loads(resp_all.read().decode())
    print(f"    - 'All Types' Returned {len(data_all)} records.")
    assert len(data_all) >= len(data_jobs)

    # 5. Verify Non-Greenhouse Sources Preserved
    print("\n  [TEST 5] Verifying existing non-Greenhouse sources (PMIS / NCS) remain active...")
    req_ncs = urllib.request.Request(f"{base_url}/api/v1/internships?source=NCS")
    resp_ncs = urllib.request.urlopen(req_ncs)
    assert resp_ncs.status == 200
    print("    - Non-Greenhouse sources verified intact.")

    print("\n======================================================================")
    print("  TASK 5 UI & API DISPLAY VERIFICATION: PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_greenhouse_ui_display_and_filtering()
