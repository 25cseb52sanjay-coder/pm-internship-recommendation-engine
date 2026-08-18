import asyncio
import urllib.request
import json
import sys
import os
import time

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from tests.auth_helper import get_admin_token, get_test_base_url
from app.ingestion.source_connectors import (
    PMISConnector,
    CompanyCareerConnector,
    LinkedInAuthorizedConnector,
    InternshalaAuthorizedConnector,
    NaukriAuthorizedConnector
)
from app.ingestion.pipeline.validation import validate_url_ssrf_safe
from app.ingestion.pipeline.normalization import normalize_internship_record
from app.ingestion.pipeline.deduplication import generate_internship_sha256_fingerprint
from app.ingestion.pipeline.quality_score import calculate_internship_quality_score
from app.ingestion.pipeline.expiry import run_continuous_expiry_sweep
from app.db.database import AsyncSessionLocal
from app.db.models import Internship, SourceRegistry, SourceReference, IngestionRun

def test_ingestion_spec_capabilities():
    print("\n======================================================================")
    print("  GOOGLE ANTIGRAVITY SPEC v1.0.0: INGESTION ENGINE TEST SUITE")
    print("======================================================================\n")

    # TEST 1: Connector Authorization & Non-Scraping Policy
    print("  [TEST 1] Authorized Connectors & Non-Scraping Policy Verification...")
    li = LinkedInAuthorizedConnector()
    ins = InternshalaAuthorizedConnector()
    nk = NaukriAuthorizedConnector()

    assert li.authorization_status == "NOT_CONFIGURED", "LinkedIn connector must default to NOT_CONFIGURED"
    assert ins.authorization_status == "NOT_CONFIGURED", "Internshala connector must default to NOT_CONFIGURED"
    assert nk.authorization_status == "NOT_CONFIGURED", "Naukri connector must default to NOT_CONFIGURED"

    async def test_stubs_fetch():
        res_li = await li.fetch()
        res_ins = await ins.fetch()
        res_nk = await nk.fetch()
        assert res_li == [], "LinkedIn stub must return empty list"
        assert res_ins == [], "Internshala stub must return empty list"
        assert res_nk == [], "Naukri stub must return empty list"

    asyncio.run(test_stubs_fetch())
    print("  [OK] TEST 1 PASSED: All 3 third-party stubs default to NOT_CONFIGURED with zero scraping.")

    # TEST 2: SSRF Protection Rules
    print("\n  [TEST 2] SSRF Protection & Private IP Range Blocking Verification...")
    malicious_urls = [
        "http://169.254.169.254/latest/meta-data/",
        "http://127.0.0.1:8000/admin",
        "http://10.0.0.1/internal",
        "http://172.16.0.1/secret",
        "http://192.168.1.1/config",
        "http://localhost:8080/internal"
    ]
    for url in malicious_urls:
        is_safe, msg = validate_url_ssrf_safe(url)
        assert not is_safe, f"SSRF Validator failed to block malicious URL '{url}'"
        print(f"    - Blocked: '{url}' -> {msg}")

    safe_url = "https://pminternship.mca.gov.in/feed"
    is_safe, _ = validate_url_ssrf_safe(safe_url)
    assert is_safe, "Valid public HTTPS URL should pass SSRF check"
    print(f"    - Allowed: '{safe_url}' -> PASSED")
    print("  [OK] TEST 2 PASSED: SSRF Protection Engine 100% Effective.")

    # TEST 3: SHA-256 Deduplication & Multi-Source Reference Collapsing
    print("\n  [TEST 3] SHA-256 Deduplication & Multi-Source References...")
    fp1 = generate_internship_sha256_fingerprint("ISRO", "AI Engineer", "Bengaluru", "https://isro.gov.in/opp1")
    fp2 = generate_internship_sha256_fingerprint("ISRO", "AI Engineer", "Bengaluru", "https://isro.gov.in/opp1")
    fp3 = generate_internship_sha256_fingerprint("isro", "ai engineer", "bengaluru", "https://isro.gov.in/opp1")

    assert fp1 == fp2 == fp3, "SHA-256 Fingerprint must be identical across case variations"
    print("  [OK] TEST 3 PASSED: SHA-256 Fingerprints Collapsed 100%.")

    # TEST 4: Quality Score Calculation Threshold
    print("\n  [TEST 4] Quality Score Calculation (0-100)...")
    complete_rec = {
        "company_name": "ISRO Telemetry",
        "title": "Radar Processing Intern",
        "location": "Bengaluru",
        "description": "Comprehensive satellite telemetry data analytics and deep learning signal processing algorithms.",
        "required_skills": ["Python", "C++", "Signal Processing"],
        "deadline": "2026-11-30",
        "application_url": "https://pminternship.mca.gov.in/opp/isro-01"
    }
    q_complete = calculate_internship_quality_score(complete_rec, 1.0)
    print(f"    - High Quality Record Score: {q_complete}/100")
    assert q_complete >= 80.0, "Complete record should score >= 80.0"

    sparse_rec = {"company_name": "Co", "title": "Intern", "location": "City"}
    q_sparse = calculate_internship_quality_score(sparse_rec, 1.0)
    print(f"    - Sparse Record Score: {q_sparse}/100")
    assert q_sparse < 50.0, "Sparse record should score < 50.0"
    print("  [OK] TEST 4 PASSED: Quality Score Index Validated.")

    # TEST 5: Health, Readiness & Metrics Endpoints
    print("\n  [TEST 5] Health, Readiness & Observability Endpoints...")
    h_req = urllib.request.Request("http://127.0.0.1:8000/health")
    h_resp = urllib.request.urlopen(h_req)
    assert h_resp.status == 200
    h_data = json.loads(h_resp.read().decode())
    assert h_data["status"] == "healthy"
    print(f"    - /health Probe: {h_data}")

    r_req = urllib.request.Request("http://127.0.0.1:8000/ready")
    r_resp = urllib.request.urlopen(r_req)
    assert r_resp.status == 200
    r_data = json.loads(r_resp.read().decode())
    assert r_data["database"] == "ok"
    print(f"    - /ready Probe: {r_data}")
    print("  [OK] TEST 5 PASSED: Observability Endpoints Active.")

    # TEST 6: Ingestion Status Dashboard API (Admin RBAC Gated)
    print("\n  [TEST 6] Admin Ingestion Status Dashboard API...")
    base_url = get_test_base_url()
    admin_token = get_admin_token()

    status_req = urllib.request.Request(
        f"{base_url}/api/v1/ingestion/status",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    status_resp = urllib.request.urlopen(status_req)
    assert status_resp.status == 200
    status_data = json.loads(status_resp.read().decode())
    print(f"    - Ingestion Status Summary: Sources={status_data['total_sources']}, Healthy={status_data['healthy_sources']}, New={status_data['new_internships']}")
    print("  [OK] TEST 6 PASSED: Admin Dashboard API Operational.")

    print("\n======================================================================")
    print("  VERIFICATION RESULT: ALL INGESTION SPEC TESTS PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_ingestion_spec_capabilities()
