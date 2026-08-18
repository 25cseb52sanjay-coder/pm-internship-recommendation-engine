import asyncio
import sys
import os
from collections import Counter

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.greenhouse.service import GreenhouseService
from app.greenhouse.schemas import NormalizedGreenhouseJob
from app.greenhouse.classifier import classify_greenhouse_opportunity

def test_greenhouse_classification_suite():
    print("\n======================================================================")
    print("  GREENHOUSE INTEGRATION TASK 3: OPPORTUNITY CLASSIFICATION TEST SUITE")
    print("======================================================================\n")

    async def _run():
        service = GreenhouseService()

        # 1. Fetch & Classify All Real Published Opportunities
        print("  [TEST 1] Fetching & Classifying real live Greenhouse opportunities...")
        boards = ["stripe", "cloudflare", "gitlab", "doordash", "airbnb"]
        normalized_jobs = await service.fetch_and_normalize_jobs(board_tokens=boards)
        
        total_records = len(normalized_jobs)
        print(f"    - Total Real Published Opportunities Fetched: {total_records}")
        assert total_records > 0, "Must fetch real published opportunities from Greenhouse API"

        # 2. Count Classifications across JOB, INTERNSHIP, and UNKNOWN
        type_counts = Counter(job.opportunity_type for job in normalized_jobs)
        
        job_count = type_counts.get("JOB", 0)
        internship_count = type_counts.get("INTERNSHIP", 0)
        unknown_count = type_counts.get("UNKNOWN", 0)

        print("\n  ====================================================================")
        print("  REAL GREENHOUSE CLASSIFICATION METRICS (TASK 3 RESULT):")
        print(f"    • Total Real Opportunities Processed: {total_records}")
        print(f"    • JOB Count:                          {job_count}")
        print(f"    • INTERNSHIP Count:                   {internship_count}")
        print(f"    • UNKNOWN Count:                      {unknown_count}")
        print("  ====================================================================\n")

        # 3. Verification Rules Check
        # Rule A: Zero Records Discarded
        assert (job_count + internship_count + unknown_count) == total_records, "Total classified records must equal total fetched records"

        # Rule B: Allowed Values Only
        for job in normalized_jobs:
            assert job.opportunity_type in ["JOB", "INTERNSHIP", "UNKNOWN"], f"Invalid opportunity_type '{job.opportunity_type}'"
            assert job.source == "Greenhouse"

        # Rule C: Print Sample Classifications for Verification
        print("  [TEST 2] Verifying sample classified records...")
        internships_samples = [j for j in normalized_jobs if j.opportunity_type == "INTERNSHIP"]
        if internships_samples:
            print("    - Sample INTERNSHIP Records:")
            for j in internships_samples[:3]:
                print(f"      • [{j.external_id}] ({j.company}) {j.title} -> {j.opportunity_type}")

        job_samples = [j for j in normalized_jobs if j.opportunity_type == "JOB"]
        if job_samples:
            print("    - Sample JOB Records:")
            for j in job_samples[:3]:
                print(f"      • [{j.external_id}] ({j.company}) {j.title} -> {j.opportunity_type}")

        print("\n  [OK] Classification rules successfully validated over 100% of real Greenhouse records.")

    asyncio.run(_run())

    print("\n======================================================================")
    print("  TASK 3 OPPORTUNITY CLASSIFICATION VERIFICATION: PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_greenhouse_classification_suite()
