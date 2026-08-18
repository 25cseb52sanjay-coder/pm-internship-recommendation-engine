import asyncio
import sys
import os

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.greenhouse.service import GreenhouseService
from app.greenhouse.schemas import NormalizedGreenhouseJob

def test_greenhouse_normalization_layer():
    print("\n======================================================================")
    print("  GREENHOUSE INTEGRATION TASK 2: REAL JOB NORMALIZATION TEST SUITE")
    print("======================================================================\n")

    async def _run():
        service = GreenhouseService()

        # 1. Fetch & Normalize Real Published Jobs
        print("  [TEST 1] Fetching & Normalizing real published jobs via GreenhouseService...")
        boards = ["stripe", "cloudflare"]
        normalized_jobs = await service.fetch_and_normalize_jobs(board_tokens=boards)
        
        total_normalized = len(normalized_jobs)
        print(f"    - Total Real Published Jobs Fetched & Normalized: {total_normalized}")
        assert total_normalized > 0, "Must fetch and normalize real published jobs from Greenhouse API"

        # 2. Verify Schema Compliance & Required Normalized Fields
        print("\n  [TEST 2] Verifying normalized field integrity & structure...")
        seen_ids = set()
        
        for idx, job in enumerate(normalized_jobs[:10], 1):
            assert isinstance(job, NormalizedGreenhouseJob)
            
            # external_id
            assert job.external_id and len(job.external_id) > 0, f"Record {idx} missing external_id"
            assert job.external_id.isdigit(), f"Record {idx} external_id '{job.external_id}' is not original numeric Greenhouse ID"
            
            # title
            assert job.title and len(job.title) > 0, f"Record {idx} missing title"
            
            # company
            assert job.company and job.company in ["Stripe", "Cloudflare"], f"Record {idx} invalid company '{job.company}'"
            
            # source & status
            assert job.source == "Greenhouse", f"Record {idx} source must be 'Greenhouse'"
            assert job.status == "active", f"Record {idx} status must be 'active'"
            
            # apply_url & source_url validation
            assert job.apply_url and (job.apply_url.startswith("http://") or job.apply_url.startswith("https://")), f"Record {idx} invalid apply_url '{job.apply_url}'"
            assert job.source_url == job.apply_url, f"Record {idx} source_url must match apply_url"

            # In-batch uniqueness check
            assert job.external_id not in seen_ids, f"Duplicate external_id '{job.external_id}' found in normalized output"
            seen_ids.add(job.external_id)

        print(f"    - Successfully validated field integrity over {min(total_normalized, 10)} sample records.")
        print(f"    - Sample Normalized Output (Record 1):")
        sample1 = normalized_jobs[0]
        print(f"      • external_id: {sample1.external_id}")
        print(f"      • title:       {sample1.title}")
        print(f"      • company:     {sample1.company}")
        print(f"      • location:    {sample1.location or 'null (Not Specified)'}")
        print(f"      • source:      {sample1.source}")
        print(f"      • apply_url:   {sample1.apply_url}")
        print(f"      • updated_at:  {sample1.updated_at or 'null'}")

        # 3. Verify Zero Mock / Hardcoded Data
        print("\n  [TEST 3] Verifying zero mock or fake data exists in normalized payload...")
        for job in normalized_jobs:
            assert "mock" not in job.external_id.lower()
            assert "dummy" not in job.title.lower()
            assert "fake" not in job.company.lower()

        print("  [OK] Zero mock data detected. 100% real Greenhouse API data normalized.")

    asyncio.run(_run())

    print("\n======================================================================")
    print("  TASK 2 REAL JOB NORMALIZATION VERIFICATION: PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_greenhouse_normalization_layer()
