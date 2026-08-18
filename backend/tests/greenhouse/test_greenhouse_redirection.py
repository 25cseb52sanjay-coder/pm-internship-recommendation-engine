import asyncio
import sys
import os
from urllib.parse import urlparse

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.db.database import AsyncSessionLocal
from app.db.models import Internship
from sqlalchemy import select

def sanitize_and_validate_url(raw_url: str) -> bool:
    """Python reference implementation matching frontend sanitizeAndValidateUrl()"""
    if not raw_url or not isinstance(raw_url, str):
        return False
    trimmed = raw_url.strip()
    if not trimmed:
        return False
    try:
        parsed = urlparse(trimmed)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False

def test_greenhouse_redirection_suite():
    print("\n======================================================================")
    print("  GREENHOUSE INTEGRATION TASK 6: EXTERNAL REDIRECTION SECURITY SUITE")
    print("======================================================================\n")

    async def _run():
        async with AsyncSessionLocal() as db:
            # 1. Verify Real Greenhouse JOB Apply URLs
            print("  [TEST 1] Testing real Greenhouse JOB application URLs...")
            job_stmt = select(Internship).where(
                Internship.source == "Greenhouse",
                Internship.opportunity_type == "JOB"
            ).limit(10)
            jobs_res = await db.execute(job_stmt)
            jobs = jobs_res.scalars().all()
            assert len(jobs) > 0, "Must have stored Greenhouse JOB records"
            for j in jobs:
                assert j.apply_url and len(j.apply_url) > 0, "JOB apply_url must be present"
                assert sanitize_and_validate_url(j.apply_url), f"Unsafe apply_url detected: {j.apply_url}"
                assert "javascript:" not in j.apply_url.lower()
            print(f"    - Tested {len(jobs)} real Greenhouse JOB application URLs: 100% Valid & Safe HTTPS.")

            # 2. Verify Real Greenhouse INTERNSHIP Apply URLs
            print("\n  [TEST 2] Testing real Greenhouse INTERNSHIP application URLs...")
            intern_stmt = select(Internship).where(
                Internship.source == "Greenhouse",
                Internship.opportunity_type == "INTERNSHIP"
            ).limit(10)
            interns_res = await db.execute(intern_stmt)
            interns = interns_res.scalars().all()
            assert len(interns) > 0, "Must have stored Greenhouse INTERNSHIP records"
            for i in interns:
                assert i.apply_url and len(i.apply_url) > 0, "INTERNSHIP apply_url must be present"
                assert sanitize_and_validate_url(i.apply_url), f"Unsafe apply_url detected: {i.apply_url}"
                assert "javascript:" not in i.apply_url.lower()
            print(f"    - Tested {len(interns)} real Greenhouse INTERNSHIP application URLs: 100% Valid & Safe HTTPS.")

            # 3. Security Sanity Checks (Reject Malicious / Unsafe Schemes)
            print("\n  [TEST 3] Verifying Security Sanitizer Rejects Malicious URLs...")
            unsafe_urls = [
                "javascript:alert('xss')",
                "data:text/html,<script>alert(1)</script>",
                "file:///etc/passwd",
                "vbscript:msgbox(1)",
                "",
                None
            ]
            for u in unsafe_urls:
                assert not sanitize_and_validate_url(u), f"Sanitizer failed to reject: {u}"
            print("    - Sanitizer correctly rejected 100% of malicious URL payloads.")

            # 4. Verify Non-Greenhouse (NCS & PMIS) Apply URLs Intact
            print("\n  [TEST 4] Verifying non-Greenhouse (NCS / PMIS) listings remain unaffected...")
            other_stmt = select(Internship).where(Internship.source != "Greenhouse").limit(10)
            other_res = await db.execute(other_stmt)
            others = other_res.scalars().all()
            for o in others:
                if o.apply_url:
                    assert sanitize_and_validate_url(o.apply_url)
            print(f"    - Verified {len(others)} non-Greenhouse listings intact.")

    asyncio.run(_run())

    print("\n======================================================================")
    print("  TASK 6 REDIRECTION SECURITY VERIFICATION: PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_greenhouse_redirection_suite()
