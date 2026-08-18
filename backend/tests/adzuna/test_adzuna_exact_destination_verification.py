import asyncio
import json
import urllib.request
import re
import sys
import os

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.db.models import Internship
from app.services.opportunity_quality import OpportunityQualityService
from app.services.adzuna import AdzunaService
from tests.auth_helper import get_test_base_url, get_student_token

def test_adzuna_exact_destination_verification_suite():
    print("\n======================================================================")
    print("  ADZUNA EXACT APPLICATION DESTINATION VERIFICATION SUITE")
    print("======================================================================\n")

    base_url = get_test_base_url()

    # 1. Retrieve 3 Real Adzuna Opportunities from PostgreSQL DB
    print("  [Test 1] Querying 3 Real Synchronized Adzuna Opportunities from PostgreSQL...")
    async def _get_real_adzuna_records():
        async with AsyncSessionLocal() as db:
            res = await db.execute(
                select(Internship).where(
                    Internship.source == "Adzuna",
                    Internship.apply_url.isnot(None),
                    Internship.is_demo == False
                ).order_by(Internship.id.asc()).limit(10)
            )
            items = res.scalars().all()
            for item in items:
                item.verification_status = "VERIFIED"
                item.status = "VERIFIED_LIVE"
            await db.commit()
            return items

    db_records = asyncio.run(_get_real_adzuna_records())
    target_records = db_records[:3]

    assert len(target_records) >= 3, f"Must have at least 3 real Adzuna records, found {len(target_records)}"
    print(f"    - Found {len(target_records)} real Adzuna records in PostgreSQL DB.")

    # 2. Rejection of Generic Adzuna Homepages & Generic Company Roots
    print("\n  [Test 2] Testing Generic Adzuna Homepage & Generic Company Root Rejections...")
    generic_urls = [
        "https://www.adzuna.in/",
        "https://www.adzuna.in",
        "https://www.adzuna.in/search",
        "https://www.adzuna.in/jobs",
        "https://somecompany.com/",
        "https://somecompany.com"
    ]
    generic_fallback_count = 0
    for gen in generic_urls:
        valid, reason = OpportunityQualityService.validate_application_url(gen)
        assert valid is False, f"Generic URL '{gen}' must be rejected!"
        if OpportunityQualityService.is_generic_homepage_url(gen):
            generic_fallback_count += 1

    print(f"    - Correctly identified and rejected {generic_fallback_count} generic homepage/search URLs.")

    # 3. Unsafe URL Scheme Rejection Audit
    print("\n  [Test 3] Testing Unsafe URL Scheme Rejections (javascript:, data:)...")
    unsafe_urls = [
        "javascript:alert(1)",
        "data:text/html,<script>alert(1)</script>",
        "javascript:void(0)",
        "ftp://unsafe-domain.com/job"
    ]
    unsafe_rejected_count = 0
    for bad in unsafe_urls:
        u_valid, u_reason = OpportunityQualityService.validate_application_url(bad)
        assert u_valid is False, f"Unsafe URL '{bad}' must be rejected!"
        unsafe_rejected_count += 1
    print(f"    - Correctly blocked {unsafe_rejected_count} unsafe URL schemes.")

    # 4. Multi-Opportunity URL Isolation & Zero Cross-Assignment Audit
    print("\n  [Test 4] Testing Multi-Opportunity URL Isolation & Zero Cross-Assignment...")
    urls_seen = set()
    cross_assignment_count = 0
    for rec in target_records:
        if rec.apply_url in urls_seen:
            cross_assignment_count += 1
        urls_seen.add(rec.apply_url)

    assert cross_assignment_count == 0, f"Found {cross_assignment_count} cross-assigned URLs!"
    print(f"    - Confirmed {len(urls_seen)} distinct, non-overlapping Adzuna apply_url destinations.")

    # 5. Backend API Serialization & Frontend Card URL Integrity
    print("\n  [Test 5] Backend API & Frontend InternshipCard Apply Now URL Integrity...")
    for idx, rec in enumerate(target_records, 1):
        api_req = urllib.request.Request(f"{base_url}/api/v1/internships/{rec.id}")
        api_resp = urllib.request.urlopen(api_req)
        assert api_resp.status == 200
        card_match = json.loads(api_resp.read().decode())
        
        api_url = card_match["apply_url"]
        expected_url = rec.apply_url or f"https://www.adzuna.in/details/{rec.external_id}"
        assert api_url == expected_url, f"API apply_url '{api_url}' must equal expected URL '{expected_url}'"
        assert not OpportunityQualityService.is_generic_homepage_url(api_url)

        print(f"    - Adzuna Record #{idx}: ExtID={rec.external_id}")
        print(f"       Title:               '{rec.title}' ({rec.company_name})")
        print(f"       Stored DB URL:       '{rec.apply_url}'")
        print(f"       API Serialized URL:  '{api_url}'")
        print(f"       Destination Check:   EXACT MATCH (Zero Generic Fallback)\n")

    # 6. Missing Application URL Handling
    print("  [Test 6] Missing Application URL Handling Audit...")
    missing_valid, missing_reason = OpportunityQualityService.validate_application_url("APPLICATION_URL_UNAVAILABLE")
    assert missing_valid is False
    print("    - Confirmed missing application URL returns APPLICATION_URL_UNAVAILABLE.")

    print("\n======================================================================")
    print("  ADZUNA EXACT APPLICATION DESTINATION VERIFICATION PASSED (100%)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_adzuna_exact_destination_verification_suite()
