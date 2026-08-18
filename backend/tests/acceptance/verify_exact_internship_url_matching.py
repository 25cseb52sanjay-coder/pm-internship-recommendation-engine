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

def verify_exact_internship_url_matching():
    print("\n======================================================================")
    print("  EXACT INTERNSHIP-TO-APPLICATION URL PAIRING AUDIT")
    print("======================================================================\n")

    base_url = get_test_base_url()

    # Define 10 distinct opportunities across Greenhouse and Adzuna
    test_opportunities = [
        {
            "ext_id": "pair_gh_001",
            "title": "Machine Learning Engineer Intern",
            "company": "Alpha Tech",
            "source": "Greenhouse",
            "expected_url": "https://boards.greenhouse.io/alphatech/jobs/10001"
        },
        {
            "ext_id": "pair_gh_002",
            "title": "VLSI Design & Hardware Intern",
            "company": "Semicon Systems",
            "source": "Greenhouse",
            "expected_url": "https://boards.greenhouse.io/semiconsystems/jobs/10002"
        },
        {
            "ext_id": "pair_gh_003",
            "title": "Robotics Systems & Automation Intern",
            "company": "RoboWorks",
            "source": "Greenhouse",
            "expected_url": "https://boards.greenhouse.io/roboworks/jobs/10003"
        },
        {
            "ext_id": "pair_gh_004",
            "title": "Structural Engineering Design Intern",
            "company": "BuildCorp",
            "source": "Greenhouse",
            "expected_url": "https://boards.greenhouse.io/buildcorp/jobs/10004"
        },
        {
            "ext_id": "pair_gh_005",
            "title": "Electric Vehicle Powertrain Intern",
            "company": "EV Dynamics",
            "source": "Greenhouse",
            "expected_url": "https://boards.greenhouse.io/evdynamics/jobs/10005"
        },
        {
            "ext_id": "pair_adz_006",
            "title": "Full Stack Developer Internship",
            "company": "WebScale Labs",
            "source": "Adzuna",
            "expected_url": "https://www.adzuna.in/land/ad/20006?v=6"
        },
        {
            "ext_id": "pair_adz_007",
            "title": "Cybersecurity SOC Analyst Internship",
            "company": "SecureNet",
            "source": "Adzuna",
            "expected_url": "https://www.adzuna.in/land/ad/20007?v=7"
        },
        {
            "ext_id": "pair_adz_008",
            "title": "Cloud DevOps Infrastructure Internship",
            "company": "CloudOps Inc",
            "source": "Adzuna",
            "expected_url": "https://www.adzuna.in/land/ad/20008?v=8"
        },
        {
            "ext_id": "pair_adz_009",
            "title": "Automotive Vehicle Dynamics Internship",
            "company": "AutoTech Motors",
            "source": "Adzuna",
            "expected_url": "https://www.adzuna.in/land/ad/20009?v=9"
        },
        {
            "ext_id": "pair_adz_010",
            "title": "Bioinformatics & Genomic Data Internship",
            "company": "BioData Solutions",
            "source": "Adzuna",
            "expected_url": "https://www.adzuna.in/land/ad/20010?v=10"
        }
    ]

    async def _seed_and_verify_pairs():
        async with AsyncSessionLocal() as db:
            for opp in test_opportunities:
                if opp["source"] == "Greenhouse":
                    gh_job = NormalizedGreenhouseJob(
                        external_id=opp["ext_id"],
                        title=opp["title"],
                        company=opp["company"],
                        location="India",
                        apply_url=opp["expected_url"],
                        source_url=opp["expected_url"],
                        opportunity_type="INTERNSHIP",
                        description=f"{opp['title']} position at {opp['company']}."
                    )
                    await GreenhouseSyncService.store_greenhouse_opportunities(db, [gh_job])
                else:
                    raw_adz = {
                        "id": opp["ext_id"],
                        "title": opp["title"],
                        "company": {"display_name": opp["company"]},
                        "location": {"display_name": "India"},
                        "description": f"{opp['title']} position at {opp['company']}.",
                        "redirect_url": opp["expected_url"]
                    }
                    await AdzunaService.sync_adzuna_opportunities(db, [raw_adz])

            await db.commit()

            # Ensure verification_status="VERIFIED" for API visibility
            for opp in test_opportunities:
                res = await db.execute(select(Internship).where(Internship.external_id == opp["ext_id"]))
                item = res.scalar_one_or_none()
                if item:
                    item.verification_status = "VERIFIED"
                    item.status = "VERIFIED_LIVE"
            await db.commit()

    asyncio.run(_seed_and_verify_pairs())

    print("  [Step 1] Verifying 1-to-1 Opportunity-to-URL Pairing across 10 distinct listings...\n")

    mismatch_count = 0
    generic_count = 0
    cross_assign_count = 0

    all_urls_seen = set()

    for idx, opp in enumerate(test_opportunities, 1):
        # Query API for this specific company's listing
        encoded_company = urllib.parse.quote(opp["company"])
        req = urllib.request.Request(f"{base_url}/api/v1/internships?search={encoded_company}")
        resp = urllib.request.urlopen(req)
        items = json.loads(resp.read().decode())
        
        card_data = next((i for i in items if i.get("external_id") == opp["ext_id"] or i.get("title") == opp["title"]), None)
        assert card_data is not None, f"API must return opportunity '{opp['title']}' for {opp['company']}"

        card_title = card_data["title"]
        card_company = card_data["company_name"]
        card_url = card_data["apply_url"]

        # Check 1: Does card title match expected opportunity title?
        assert card_title == opp["title"], f"Title mismatch: Expected '{opp['title']}', got '{card_title}'"
        assert card_company == opp["company"], f"Company mismatch: Expected '{opp['company']}', got '{card_company}'"

        # Check 2: Does card apply_url match exact specific expected_url?
        if card_url != opp["expected_url"]:
            print(f"  [FAIL] Mismatch for Card #{idx} '{card_title}': Expected '{opp['expected_url']}', got '{card_url}'")
            mismatch_count += 1
        
        # Check 3: Is it a generic homepage?
        if OpportunityQualityService.is_generic_homepage_url(card_url):
            print(f"  [FAIL] Generic Homepage Detected for Card #{idx} '{card_title}': '{card_url}'")
            generic_count += 1

        # Check 4: Cross-assignment check (Ensure URL has not been assigned to any other card)
        if card_url in all_urls_seen:
            print(f"  [FAIL] Cross-Assignment Detected for Card #{idx} '{card_title}': URL '{card_url}' already assigned to another opportunity!")
            cross_assign_count += 1
        all_urls_seen.add(card_url)

        print(f"  [Card #{idx:02d} OK] '{card_title}' ({card_company})")
        print(f"           • Target External ID: {opp['ext_id']}")
        print(f"           • Displayed Card URL: {card_url}")
        print(f"           • Verification:       EXACT MATCH TO THIS INTERNSHIP (Zero Cross-Talk)\n")

    assert mismatch_count == 0, f"Found {mismatch_count} URL pairings that did not belong to the displayed internship!"
    assert generic_count == 0, f"Found {generic_count} generic homepage URLs!"
    assert cross_assign_count == 0, f"Found {cross_assign_count} cross-assigned URLs!"

    print("======================================================================")
    print("  EXACT INTERNSHIP-TO-APPLICATION URL PAIRING AUDIT: PASSED (100%)")
    print("======================================================================\n")

if __name__ == "__main__":
    verify_exact_internship_url_matching()
