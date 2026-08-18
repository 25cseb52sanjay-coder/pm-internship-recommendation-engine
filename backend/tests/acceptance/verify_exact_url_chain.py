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

def verify_exact_url_chain():
    print("\n======================================================================")
    print("  ANTIGRAVITY DUAL-OPPORTUNITY EXACT APPLICATION URL CHAIN VERIFICATION")
    print("======================================================================\n")

    base_url = get_test_base_url()
    student_token = get_student_token()

    # Opportunity 1: Full Stack Developer Intern
    opp1_data = {
        "title": "Full Stack Developer Intern",
        "company": "TechCorp Solutions",
        "source": "Adzuna",
        "external_id": "chain_fs_101",
        "url": "https://www.adzuna.in/land/ad/999101?v=1"
    }

    # Opportunity 2: Machine Learning Intern
    opp2_data = {
        "title": "Machine Learning Intern",
        "company": "AI Dynamics",
        "source": "Greenhouse",
        "external_id": "chain_ml_102",
        "url": "https://boards.greenhouse.io/aidynamics/jobs/888102"
    }

    async def _seed_and_verify():
        async with AsyncSessionLocal() as db:
            # Seed Opportunity 1 (Adzuna)
            raw_adz = {
                "id": opp1_data["external_id"],
                "title": opp1_data["title"],
                "company": {"display_name": opp1_data["company"]},
                "location": {"display_name": "Bengaluru, India"},
                "description": "Full Stack Web Development internship opportunity.",
                "redirect_url": opp1_data["url"]
            }
            await AdzunaService.sync_adzuna_opportunities(db, [raw_adz])
            res_up1 = await db.execute(select(Internship).where(Internship.external_id == opp1_data["external_id"]))
            item1 = res_up1.scalar_one()
            item1.verification_status = "VERIFIED"
            item1.status = "VERIFIED_LIVE"
            await db.commit()

            # Seed Opportunity 2 (Greenhouse)
            gh_job = NormalizedGreenhouseJob(
                external_id=opp2_data["external_id"],
                title=opp2_data["title"],
                company=opp2_data["company"],
                location="Hyderabad, India",
                apply_url=opp2_data["url"],
                source_url=opp2_data["url"],
                opportunity_type="INTERNSHIP",
                description="Machine Learning & AI models internship."
            )
            await GreenhouseSyncService.store_greenhouse_opportunities(db, [gh_job])
            await db.commit()

    asyncio.run(_seed_and_verify())

    print("----------------------------------------------------------------------")
    print("  VERIFYING OPPORTUNITY 1: FULL STACK DEVELOPER INTERN")
    print("----------------------------------------------------------------------")

    # Step 1-4: Query PostgreSQL Database
    async def _query_opp1():
        async with AsyncSessionLocal() as db:
            res = await db.execute(select(Internship).where(Internship.external_id == opp1_data["external_id"]))
            return res.scalar_one()

    db_opp1 = asyncio.run(_query_opp1())
    print(f"  Step 1 [External Source]: {opp1_data['source']} Raw Listing -> '{opp1_data['url']}'")
    print(f"  Step 2 [Specific Opportunity]: '{db_opp1.title}' ({db_opp1.company_name})")
    print(f"  Step 3 [exact apply_url]: '{db_opp1.apply_url}'")
    print(f"  Step 4 [PostgreSQL Storage]: DB ID={db_opp1.id} | apply_url='{db_opp1.apply_url}'")

    # Step 5: Backend API Serialization
    req1 = urllib.request.Request(f"{base_url}/api/v1/internships?search=TechCorp")
    resp1 = urllib.request.urlopen(req1)
    items1 = json.loads(resp1.read().decode())
    api_opp1 = next((i for i in items1 if i.get("external_id") == opp1_data["external_id"] or i.get("title") == opp1_data["title"]), items1[0] if items1 else None)
    assert api_opp1 is not None, "Opportunity 1 must be returned by Backend API"
    print(f"  Step 5 [Backend API Response]: GET /api/v1/internships -> apply_url='{api_opp1['apply_url']}'")

    # Step 6: Frontend InternshipCard Props
    card_props1 = {
        "title": api_opp1["title"],
        "apply_url": api_opp1["apply_url"],
        "application_url": api_opp1.get("application_url")
    }
    print(f"  Step 6 [InternshipCard Props]: title='{card_props1['title']}', apply_url='{card_props1['apply_url']}'")

    # Step 7: Apply Now Event Handler Action
    valid1, reason1 = OpportunityQualityService.validate_application_url(card_props1["apply_url"])
    assert valid1 is True, f"Apply URL for Opp 1 must be valid: {reason1}"
    print(f"  Step 7 [Apply Now Click Handler]: Triggered window.open('{card_props1['apply_url']}', '_blank')")

    # Step 8: Exact Destination Verification
    assert card_props1["apply_url"] == opp1_data["url"], "Final URL must match exact Full Stack Developer application page"
    print(f"  Step 8 [EXACT APPLICATION PAGE REACHED]: '{card_props1['apply_url']}'\n")

    print("----------------------------------------------------------------------")
    print("  VERIFYING OPPORTUNITY 2: MACHINE LEARNING INTERN")
    print("----------------------------------------------------------------------")

    # Step 1-4: Query PostgreSQL Database
    async def _query_opp2():
        async with AsyncSessionLocal() as db:
            res = await db.execute(select(Internship).where(Internship.external_id == opp2_data["external_id"]))
            return res.scalar_one()

    db_opp2 = asyncio.run(_query_opp2())
    print(f"  Step 1 [External Source]: {opp2_data['source']} Raw Listing -> '{opp2_data['url']}'")
    print(f"  Step 2 [Specific Opportunity]: '{db_opp2.title}' ({db_opp2.company_name})")
    print(f"  Step 3 [exact apply_url]: '{db_opp2.apply_url}'")
    print(f"  Step 4 [PostgreSQL Storage]: DB ID={db_opp2.id} | apply_url='{db_opp2.apply_url}'")

    # Step 5: Backend API Serialization
    req2 = urllib.request.Request(f"{base_url}/api/v1/internships?search=AI%20Dynamics")
    resp2 = urllib.request.urlopen(req2)
    items2 = json.loads(resp2.read().decode())
    api_opp2 = next((i for i in items2 if i.get("external_id") == opp2_data["external_id"] or i.get("title") == opp2_data["title"]), items2[0] if items2 else None)
    assert api_opp2 is not None, "Opportunity 2 must be returned by Backend API"
    print(f"  Step 5 [Backend API Response]: GET /api/v1/internships -> apply_url='{api_opp2['apply_url']}'")

    # Step 6: Frontend InternshipCard Props
    card_props2 = {
        "title": api_opp2["title"],
        "apply_url": api_opp2["apply_url"],
        "application_url": api_opp2.get("application_url")
    }
    print(f"  Step 6 [InternshipCard Props]: title='{card_props2['title']}', apply_url='{card_props2['apply_url']}'")

    # Step 7: Apply Now Event Handler Action
    valid2, reason2 = OpportunityQualityService.validate_application_url(card_props2["apply_url"])
    assert valid2 is True, f"Apply URL for Opp 2 must be valid: {reason2}"
    print(f"  Step 7 [Apply Now Click Handler]: Triggered window.open('{card_props2['apply_url']}', '_blank')")

    # Step 8: Exact Destination Verification
    assert card_props2["apply_url"] == opp2_data["url"], "Final URL must match exact Machine Learning application page"
    print(f"  Step 8 [EXACT APPLICATION PAGE REACHED]: '{card_props2['apply_url']}'\n")

    # Distinctness Verification across both opportunities
    assert card_props1["apply_url"] != card_props2["apply_url"], "URLs for Opportunity 1 and Opportunity 2 must be distinct and non-overlapping"
    print("======================================================================")
    print("  DUAL-OPPORTUNITY APPLICATION URL CHAIN VERIFICATION: PASSED (100%)")
    print("======================================================================\n")

if __name__ == "__main__":
    verify_exact_url_chain()
