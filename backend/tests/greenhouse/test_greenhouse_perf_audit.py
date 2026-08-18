import urllib.request
import json
import time
import sys
import os

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from tests.auth_helper import get_test_base_url, get_student_token

def test_greenhouse_perf_and_redirection_audit():
    print("\n======================================================================")
    print("  GREENHOUSE PERFORMANCE & APPLY NOW REDIRECTION AUDIT TEST SUITE")
    print("======================================================================\n")

    base_url = get_test_base_url()
    token = get_student_token()

    # 1. Benchmark GET /api/v1/internships (Direct DB Query, Eager Loading)
    print("  [STEP 1] Measuring GET /api/v1/internships loading speed from PostgreSQL...")
    start_time = time.time()
    req = urllib.request.Request(f"{base_url}/api/v1/internships?source=Greenhouse&limit=50")
    resp = urllib.request.urlopen(req)
    duration_ms = (time.time() - start_time) * 1000
    assert resp.status == 200
    items = json.loads(resp.read().decode())
    print(f"    - Returned {len(items)} real Greenhouse opportunities in {duration_ms:.2f} ms")
    assert len(items) > 0
    assert duration_ms < 500.0, f"Response took {duration_ms:.2f} ms, must be under 500 ms"

    # 2. Benchmark GET /api/v1/students/recommendations speed (Initial Generation & Cache)
    print("\n  [STEP 2] Measuring GET /api/v1/students/recommendations initial AI generation speed...")
    start_rec = time.time()
    req_rec = urllib.request.Request(
        f"{base_url}/api/v1/students/recommendations",
        headers={"Authorization": f"Bearer {token}"}
    )
    resp_rec = urllib.request.urlopen(req_rec)
    rec_duration_ms = (time.time() - start_rec) * 1000
    assert resp_rec.status == 200
    recs = json.loads(resp_rec.read().decode())
    print(f"    - Returned {len(recs)} AI recommendations in {rec_duration_ms:.2f} ms")
    assert len(recs) > 0
    assert rec_duration_ms < 15000.0, f"Recommendation stream initial load took {rec_duration_ms:.2f} ms, must be under 15000 ms"

    # Test Cached Hit Speed
    print("\n  [STEP 2b] Measuring GET /api/v1/students/recommendations cached load speed...")
    start_cache = time.time()
    req_cache = urllib.request.Request(
        f"{base_url}/api/v1/students/recommendations",
        headers={"Authorization": f"Bearer {token}"}
    )
    resp_cache = urllib.request.urlopen(req_cache)
    cache_duration_ms = (time.time() - start_cache) * 1000
    assert resp_cache.status == 200
    recs_cached = json.loads(resp_cache.read().decode())
    print(f"    - Returned {len(recs_cached)} cached AI recommendations in {cache_duration_ms:.2f} ms")
    assert cache_duration_ms < 100.0, f"Cached recommendation load took {cache_duration_ms:.2f} ms, must be under 100 ms"

    # 3. Verify Apply Now URL integrity for both JOB and INTERNSHIP
    print("\n  [STEP 3] Verifying canonical apply_url for JOB and INTERNSHIP...")
    greenhouse_items = [r["internship"] for r in recs if r.get("internship", {}).get("source") == "Greenhouse"]
    jobs = [g for g in greenhouse_items if g.get("opportunity_type") == "JOB"]
    internships = [g for g in greenhouse_items if g.get("opportunity_type") == "INTERNSHIP"]

    assert len(jobs) > 0, "Must contain Greenhouse JOB opportunities"
    assert len(internships) > 0, "Must contain Greenhouse INTERNSHIP opportunities"

    sample_job = jobs[0]
    sample_intern = internships[0]

    print(f"    - JOB:        '{sample_job['title']}' ({sample_job['company_name']})")
    print(f"      • Apply URL: {sample_job['apply_url']}")
    assert sample_job["apply_url"].startswith("https://") or sample_job["apply_url"].startswith("http://")

    print(f"    - INTERNSHIP: '{sample_intern['title']}' ({sample_intern['company_name']})")
    print(f"      • Apply URL: {sample_intern['apply_url']}")
    assert sample_intern["apply_url"].startswith("https://") or sample_intern["apply_url"].startswith("http://")

    print("\n======================================================================")
    print("  PERFORMANCE AND APPLY REDIRECT AUDIT: PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_greenhouse_perf_and_redirection_audit()
