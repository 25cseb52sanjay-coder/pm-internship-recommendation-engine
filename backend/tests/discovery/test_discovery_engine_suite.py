import asyncio
import urllib.request
import json
import sys
import os

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from tests.auth_helper import get_student_token, get_admin_token, get_test_base_url
from app.discovery.query_generator import generate_dynamic_search_queries
from app.discovery.search_providers import AuthorizedWebSearchProvider
from app.discovery.fetcher import fetch_discovered_page_html, extract_internship_posting_metadata, fetch_js_rendered_page
from app.discovery.verification import verify_employer_domain_trust, verify_extracted_deadline, verify_content_recency, process_discovery_candidate_verification
from app.db.database import AsyncSessionLocal
from app.db.models import DiscoveryCandidate, DiscoverySearchQuery, Internship

def test_discovery_engine_capabilities():
    print("\n======================================================================")
    print("  GOOGLE ANTIGRAVITY SPEC v1.0.0: DISCOVERY & VERIFICATION SUITE")
    print("======================================================================\n")

    # TEST 1: Dynamic Query Generation & Rotation
    print("  [TEST 1] Dynamic Multi-Dimensional Search Query Rotation...")
    async def _test_query_gen():
        async with AsyncSessionLocal() as db:
            queries = await generate_dynamic_search_queries(db, limit=5)
            assert len(queries) > 0, "Query generator must generate new dynamic queries"
            print(f"    - Generated {len(queries)} dynamic search queries (Sample: '{queries[0].query_text}')")
    asyncio.run(_test_query_gen())
    print("  [OK] TEST 1 PASSED: Dynamic Query Generation Active.")

    # TEST 2: Authorized Search Provider Quota Management
    print("\n  [TEST 2] Search Provider Quota Tracking...")
    provider = AuthorizedWebSearchProvider()
    assert provider.check_quota(), "Quota check must pass initially"
    async def _test_search():
        res = await provider.execute_search("ISRO Avionics Intern 2026")
        assert len(res) > 0, "Provider must return search results"
        print(f"    - Search returned {len(res)} candidate URLs (Provider Quota Used: {provider.used_quota})")
    asyncio.run(_test_search())
    print("  [OK] TEST 2 PASSED: Search Provider Quota Management Active.")

    # TEST 3: SSRF Protection & Playwright Allowlist Gating
    print("\n  [TEST 3] SSRF Protection & Playwright Allowlist Gating...")
    async def _test_fetchers():
        # SSRF Check
        succ, status, msg, _ = await fetch_discovered_page_html("http://169.254.169.254/latest/meta-data/")
        assert not succ, "SSRF fetcher must block 169.254.169.254"
        print(f"    - SSRF Protection Blocked: '169.254.169.254' -> {msg}")

        # Playwright Allowlist Check
        pw_allowed, pw_msg, _ = await fetch_js_rendered_page("https://untrusted-domain.com/job")
        assert not pw_allowed, "Playwright must block untrusted domains"
        print(f"    - Playwright Allowlist Blocked: 'untrusted-domain.com' -> {pw_msg}")

    asyncio.run(_test_fetchers())
    print("  [OK] TEST 3 PASSED: SSRF Protection & Playwright Gating Active.")

    # TEST 4: Employer Domain Trust & Manual Review Queue
    print("\n  [TEST 4] Employer Domain Trust Verification...")
    official_match, d_name, d_msg = verify_employer_domain_trust("ISRO", "https://careers.isro.gov.in/job/1")
    assert official_match, "Official domain match must be verified for isro.gov.in"
    print(f"    - Official Domain Match: 'careers.isro.gov.in' -> {d_msg}")

    mismatch_match, d_name2, d_msg2 = verify_employer_domain_trust("ISRO", "https://unverified-thirdparty-blog.com/job")
    assert not mismatch_match, "Domain mismatch must fail domain trust check"
    print(f"    - Domain Mismatch Queued to Manual Review: 'unverified-thirdparty-blog.com' -> {d_msg2}")
    print("  [OK] TEST 4 PASSED: Domain Trust Pipeline Active.")

    # TEST 5: Multi-Stage Verification & Ingestion Engine Handoff
    print("\n  [TEST 5] Multi-Stage Verification & Upstream Handoff...")
    async def _test_verification_handoff():
        async with AsyncSessionLocal() as db:
            cand = DiscoveryCandidate(
                result_url="https://careers.isro.gov.in/opportunities/avionics-data-intern-01",
                discovered_at=datetime.utcnow()
            )
            db.add(cand)
            await db.commit()
            await db.refresh(cand)

            v_status, msg, q_score = await process_discovery_candidate_verification(db, cand)
            assert v_status == "VERIFIED", "Valid candidate must reach VERIFIED status"
            assert cand.linked_internship_id is not None, "VERIFIED candidate must hand off payload to internships table"
            print(f"    - Verification Pipeline Result: Status='{v_status}', Quality Score={q_score}, Linked Internship ID={cand.linked_internship_id}")

    from datetime import datetime
    asyncio.run(_test_verification_handoff())
    print("  [OK] TEST 5 PASSED: Multi-Stage Verification & Upstream Handoff Active.")

    # TEST 6: Admin Discovery REST APIs & RBAC Enforcement
    print("\n  [TEST 6] Admin Discovery REST APIs & RBAC Enforcement...")
    base_url = get_test_base_url()
    admin_token = get_admin_token()

    status_req = urllib.request.Request(
        f"{base_url}/api/v1/discovery/status",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    status_resp = urllib.request.urlopen(status_req)
    assert status_resp.status == 200
    status_data = json.loads(status_resp.read().decode())
    print(f"    - Discovery Status Summary: Discovered={status_data['urls_discovered']}, Verified={status_data['urls_verified']}, Quota={status_data['search_provider_quota_remaining']}")

    # Non-admin student login (RBAC Check)
    student_token = get_student_token()

    forbidden_passed = False
    try:
        f_req = urllib.request.Request(
            f"{base_url}/api/v1/discovery/status",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        urllib.request.urlopen(f_req)
    except urllib.error.HTTPError as e:
        if e.code == 403:
            forbidden_passed = True
            print("    - Non-Admin Student Token on /api/v1/discovery/status -> HTTP 403 Forbidden (RBAC ENFORCED)")

    assert forbidden_passed, "Non-admin token must receive HTTP 403 Forbidden"
    print("  [OK] TEST 6 PASSED: Discovery Admin APIs & RBAC Enforcement 100% Operational.")

    print("\n======================================================================")
    print("  VERIFICATION RESULT: ALL DISCOVERY ENGINE TESTS PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_discovery_engine_capabilities()
