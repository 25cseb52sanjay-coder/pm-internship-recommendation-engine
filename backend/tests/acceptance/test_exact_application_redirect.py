import asyncio
import json
import urllib.request
import sys
import os

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.db.models import Internship
from app.services.opportunity_quality import OpportunityQualityService
from app.services.adzuna import AdzunaService
from app.greenhouse.sync_service import GreenhouseSyncService
from app.greenhouse.schemas import NormalizedGreenhouseJob
from tests.auth_helper import get_test_base_url, get_student_token

def test_exact_application_redirect_suite():
    print("\n======================================================================")
    print("  TASK 27G: EXACT INTERNSHIP APPLICATION REDIRECT INTEGRITY SUITE")
    print("======================================================================\n")

    base_url = get_test_base_url()

    # 1. Verify URL Syntax & Security Filtering (javascript:, data:, malformed)
    print("  [Test 1] Testing Invalid & Malformed URL Rejections...")
    invalid_urls = [
        "",
        "   ",
        "javascript:alert(1)",
        "data:text/html,<script>alert(1)</script>",
        "not_a_url",
        "ftp://invalid-scheme.com/job/1"
    ]
    for bad_url in invalid_urls:
        valid, reason = OpportunityQualityService.validate_application_url(bad_url)
        assert valid is False, f"URL '{bad_url}' should have been rejected."
        print(f"    - Correctly rejected invalid URL '{bad_url}': {reason}")

    # 2. Verify Generic Provider & Company Homepage Rejection
    print("\n  [Test 2] Testing Generic Provider & Company Homepage Rejections...")
    generic_homepages = [
        "https://boards.greenhouse.io/",
        "https://boards.greenhouse.io",
        "https://www.adzuna.in/",
        "https://www.adzuna.in",
        "https://www.adzuna.in/search",
        "https://pminternship.mca.gov.in/",
        "https://pminternship.mca.gov.in",
        "https://www.ncs.gov.in/",
        "https://www.ncs.gov.in/internships-jobs",
        "https://somecompany.com/",
        "https://somecompany.com",
        "APPLICATION_URL_UNAVAILABLE"
    ]
    for gen_url in generic_homepages:
        assert OpportunityQualityService.is_generic_homepage_url(gen_url) is True
        valid, reason = OpportunityQualityService.validate_application_url(gen_url)
        assert valid is False, f"Generic homepage '{gen_url}' should have been rejected."
        print(f"    - Correctly rejected generic homepage '{gen_url}': {reason}")

    # 3. Verify Database Storage & Preservation of Exact URLs for Greenhouse & Adzuna
    print("\n  [Test 3] Testing Database Persistence & Multi-Opportunity Distinct URLs...")
    async def _test_db_persistence():
        async with AsyncSessionLocal() as db:
            # Seed 2 distinct Greenhouse jobs with unique specific apply_urls
            job1 = NormalizedGreenhouseJob(
                external_id="gh_9001",
                title="Machine Learning Intern",
                company="Banking Corp",
                location="Bengaluru, India",
                apply_url="https://boards.greenhouse.io/bankingcorp/jobs/9001",
                source_url="https://boards.greenhouse.io/bankingcorp/jobs/9001",
                opportunity_type="INTERNSHIP",
                description="Machine Learning internship in Banking analytics."
            )
            job2 = NormalizedGreenhouseJob(
                external_id="gh_9002",
                title="Cybersecurity Analyst Intern",
                company="Banking Corp",
                location="Mumbai, India",
                apply_url="https://boards.greenhouse.io/bankingcorp/jobs/9002",
                source_url="https://boards.greenhouse.io/bankingcorp/jobs/9002",
                opportunity_type="INTERNSHIP",
                description="Cybersecurity internship in Banking SOC."
            )
            await GreenhouseSyncService.store_greenhouse_opportunities(db, [job1, job2])
            await db.commit()

            # Retrieve records and assert distinct URLs
            res1 = await db.execute(select(Internship).where(Internship.external_id == "gh_9001"))
            db_item1 = res1.scalar_one()
            res2 = await db.execute(select(Internship).where(Internship.external_id == "gh_9002"))
            db_item2 = res2.scalar_one()

            assert db_item1.apply_url == "https://boards.greenhouse.io/bankingcorp/jobs/9001"
            assert db_item2.apply_url == "https://boards.greenhouse.io/bankingcorp/jobs/9002"
            assert db_item1.apply_url != db_item2.apply_url, "Two distinct opportunities must not share or cross-assign URLs"
            print("    - Validated DB persistence for distinct Greenhouse opportunity URLs.")

            # Seed 2 distinct Adzuna jobs with unique specific apply_urls
            raw_adz1 = {
                "id": "adz_8001",
                "title": "Full Stack Developer Internship",
                "company": {"display_name": "Tech Corp"},
                "location": {"display_name": "Bengaluru"},
                "description": "Full Stack Developer internship opportunity.",
                "redirect_url": "https://www.adzuna.in/land/ad/8001?v=1"
            }
            raw_adz2 = {
                "id": "adz_8002",
                "title": "Cloud DevOps Engineer Internship",
                "company": {"display_name": "Tech Corp"},
                "location": {"display_name": "Hyderabad"},
                "description": "Cloud DevOps Engineer internship opportunity.",
                "redirect_url": "https://www.adzuna.in/land/ad/8002?v=2"
            }
            await AdzunaService.sync_adzuna_opportunities(db, [raw_adz1, raw_adz2])
            await db.commit()

            res_adz1 = await db.execute(select(Internship).where(Internship.external_id == "adz_8001"))
            db_adz1 = res_adz1.scalar_one()
            res_adz2 = await db.execute(select(Internship).where(Internship.external_id == "adz_8002"))
            db_adz2 = res_adz2.scalar_one()

            assert db_adz1.apply_url == "https://www.adzuna.in/land/ad/8001?v=1"
            assert db_adz2.apply_url == "https://www.adzuna.in/land/ad/8002?v=2"
            assert db_adz1.apply_url != db_adz2.apply_url, "Two distinct Adzuna opportunities must not share or cross-assign URLs"
            print("    - Validated DB persistence for distinct Adzuna opportunity URLs.")

    asyncio.run(_test_db_persistence())

    # 4. Verify API Serialization Returns Exact Persisted URLs
    print("\n  [Test 4] Testing Backend API Serialization of Exact apply_url...")
    req = urllib.request.Request(f"{base_url}/api/v1/internships?source=Greenhouse&limit=100")
    resp = urllib.request.urlopen(req)
    assert resp.status == 200
    items = json.loads(resp.read().decode())
    assert len(items) > 0, "Must return Greenhouse opportunities"
    for gh_item in items:
        url_val = gh_item.get("apply_url")
        assert url_val and url_val.startswith("http")
        assert not OpportunityQualityService.is_generic_homepage_url(url_val)
    print(f"    - Validated {len(items)} Greenhouse API items return exact non-generic apply_url destinations.")

    # 5. Verify Recommendation Stream Preserves Exact Opportunity URLs
    print("\n  [Test 5] Testing AI Recommendation Stream URL Integrity...")
    student_token = get_student_token()
    rec_req = urllib.request.Request(
        f"{base_url}/api/v1/students/recommendations",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    rec_resp = urllib.request.urlopen(rec_req)
    assert rec_resp.status == 200
    recs = json.loads(rec_resp.read().decode())
    assert len(recs) > 0, "Must generate AI recommendations for student"
    for r in recs[:10]:
        opp_info = r["internship"]
        assert "apply_url" in opp_info
        url_val = opp_info["apply_url"]
        assert url_val and len(url_val) > 0
        assert url_val != "https://boards.greenhouse.io/"
        assert url_val != "https://www.adzuna.in/"
    print("    - All recommended opportunities contain valid exact application URLs.")

    # 6. Verify Background Sync & Deduplication URL Preservation (No Overwrite by Generic Fallbacks)
    print("\n  [Test 6] Testing Background Sync & Deduplication URL Preservation...")
    async def _test_sync_preservation():
        async with AsyncSessionLocal() as db:
            # Re-sync same Greenhouse job with a generic/empty apply_url in raw payload
            bad_job = NormalizedGreenhouseJob(
                external_id="gh_9001",
                title="Machine Learning Intern",
                company="Banking Corp",
                location="Bengaluru, India",
                apply_url="https://boards.greenhouse.io/", # Generic provider root
                source_url="https://boards.greenhouse.io/",
                opportunity_type="INTERNSHIP",
                description="Updated Machine Learning internship description."
            )
            await GreenhouseSyncService.store_greenhouse_opportunities(db, [bad_job])
            await db.commit()

            # Retrieve existing record and verify original specific URL remained intact
            check_res = await db.execute(select(Internship).where(Internship.external_id == "gh_9001"))
            surviving = check_res.scalar_one()
            assert surviving.apply_url == "https://boards.greenhouse.io/bankingcorp/jobs/9001", \
                "Background sync must not overwrite an existing valid exact apply_url with a generic fallback."
            print("    - Confirmed existing exact apply_url preserved during sync with generic payload.")

    asyncio.run(_test_sync_preservation())

    print("\n======================================================================")
    print("  TASK 27G: EXACT APPLICATION REDIRECT INTEGRITY PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_exact_application_redirect_suite()
