import asyncio
import sys
import os
from datetime import datetime, timedelta
from sqlalchemy import select, text

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.db.database import AsyncSessionLocal, engine, Base
from app.db.models import StudentProfile, LeetCodeProfile
from app.leetcode.profile_repository import LeetCodeProfileRepository
from app.leetcode.metrics_service import LeetCodeMetricsService
from app.leetcode.data_provider import (
    LeetCodeDataProvider,
    LeetCodeProviderRegistry,
    ProviderResultStatus,
    ProviderResult
)

def test_leetcode_real_profile_metrics_suite():
    print("\n======================================================================")
    print("  LEETCODE INTEGRATION TASK 9: REAL PROFILE METRICS AUDIT TEST SUITE")
    print("======================================================================\n")

    async def _run():
        # Ensure schema table columns exist in database
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            for col_def in [
                ("total_problems_solved", "INTEGER"),
                ("easy_solved", "INTEGER"),
                ("medium_solved", "INTEGER"),
                ("hard_solved", "INTEGER"),
                ("languages_json", "TEXT"),
                ("skills_json", "TEXT"),
                ("badges_json", "TEXT"),
                ("contest_rating", "FLOAT"),
                ("contest_rank", "INTEGER"),
                ("recent_activity_json", "TEXT")
            ]:
                try:
                    await conn.execute(text(f"ALTER TABLE leetcode_profiles ADD COLUMN {col_def[0]} {col_def[1]}"))
                except Exception:
                    pass

        async with AsyncSessionLocal() as db:
            # Fetch test student
            res_st = await db.execute(select(StudentProfile).limit(1))
            student = res_st.scalar_one_or_none()
            assert student is not None, "Database must contain at least 1 StudentProfile"
            cand_id = student.id

            # Ensure profile is verified for metric test
            await LeetCodeProfileRepository.save_verified_profile(
                db, cand_id, "metrics_audit_user", "https://leetcode.com/u/metrics_audit_user", "BIO_TOKEN_CHALLENGE", "NOT_AVAILABLE"
            )

            # 1. Test Default Unconfigured Provider (Must NOT Fabricate Zeroes or Mock Data)
            print("  [STEP 1] Testing metric retrieval with default Unconfigured Provider...")
            LeetCodeProviderRegistry.reset()
            res_unconf = await LeetCodeMetricsService.fetch_and_update_metrics(db, cand_id)

            print(f"    - Candidate ID:       {res_unconf['candidate_id']}")
            print(f"    - System Status:      '{res_unconf['status']}'")
            print(f"    - Data Status:        '{res_unconf['data_status']}'")
            print(f"    - Metrics Object:     {res_unconf['metrics']}")
            print(f"    - Message:            '{res_unconf['message']}'")

            assert res_unconf["status"] == "DATA_UNAVAILABLE"
            assert res_unconf["metrics"] is None, "Must NOT fabricate missing metrics or return zeroes!"
            assert "limitation" in res_unconf["message"].lower()

            # Verify Database State: Columns must remain None (not 0)
            res_lc = await db.execute(select(LeetCodeProfile).where(LeetCodeProfile.candidate_id == cand_id))
            db_prof = res_lc.scalar_one_or_none()
            assert db_prof.total_problems_solved is None, "Missing metric MUST remain None, not 0!"
            assert db_prof.easy_solved is None

            # 2. Test Real Metrics Population via Authorized Provider
            print("\n  [STEP 2] Testing real metrics population via Authorized Provider...")

            class MockAuthorizedMetricsProvider(LeetCodeDataProvider):
                async def check_profile_exists(self, username: str) -> ProviderResult:
                    return ProviderResult(status=ProviderResultStatus.SUCCESS, message="OK", timestamp="2026-08-14T00:00:00Z")
                async def get_profile_data(self, username: str) -> ProviderResult:
                    return ProviderResult(status=ProviderResultStatus.SUCCESS, message="OK", timestamp="2026-08-14T00:00:00Z")
                async def get_profile_statistics(self, username: str) -> ProviderResult:
                    return ProviderResult(
                        status=ProviderResultStatus.SUCCESS,
                        message="Real metrics fetched",
                        data={
                            "username": username,
                            "total_problems_solved": 342,
                            "easy_solved": 150,
                            "medium_solved": 160,
                            "hard_solved": 32,
                            "languages": {"Python": 200, "C++": 142},
                            "skills": ["Algorithms", "Dynamic Programming", "Graphs"],
                            "badges": [{"name": "50 Days Badge 2026", "icon": "https://assets.leetcode.com/badge50.png"}],
                            "contest_rating": 1845.5,
                            "contest_rank": 12450,
                            "recent_activity": [{"submission_id": 998822, "title": "Two Sum", "status": "Accepted"}]
                        },
                        timestamp="2026-08-14T00:00:00Z"
                    )
                async def get_provider_status(self) -> dict:
                    return {"is_configured": True}

            LeetCodeProviderRegistry.set_provider(MockAuthorizedMetricsProvider())

            res_auth = await LeetCodeMetricsService.fetch_and_update_metrics(db, cand_id)
            print(f"    - System Status:      '{res_auth['status']}'")
            print(f"    - Data Status:        '{res_auth['data_status']}'")
            print(f"    - Total Solved:       {res_auth['metrics']['total_problems_solved']}")
            print(f"    - Contest Rating:     {res_auth['metrics']['contest_rating']}")
            print(f"    - Languages:          {res_auth['metrics']['languages']}")
            print(f"    - Last Refresh At:    '{res_auth['last_data_refresh_at']}'")

            assert res_auth["status"] == "SUCCESS"
            assert res_auth["data_status"] == "AVAILABLE"
            assert res_auth["metrics"]["total_problems_solved"] == 342
            assert res_auth["metrics"]["contest_rating"] == 1845.5

            # 3. Test Freshness Tracking & Stale Data Distinction (24h TTL)
            print("\n  [STEP 3] Testing metrics freshness tracking & STALE data flag...")
            db_prof.last_data_refresh_at = datetime.utcnow() - timedelta(hours=25) # Simulate 25h old data
            await db.commit()

            fetched_metrics = await LeetCodeMetricsService.get_candidate_metrics(db, cand_id)
            print(f"    - Evaluated Data Status (25h old): '{fetched_metrics['data_status']}'")
            assert fetched_metrics["data_status"] == "STALE", "Data older than 24h MUST be flagged as STALE!"

            # Reset provider registry
            LeetCodeProviderRegistry.reset()

    asyncio.run(_run())

    print("\n======================================================================")
    print("  TASK 9 LEETCODE REAL PROFILE METRICS AUDIT: PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_leetcode_real_profile_metrics_suite()
