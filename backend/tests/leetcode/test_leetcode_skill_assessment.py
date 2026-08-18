import asyncio
import sys
import os
from sqlalchemy import select, text

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.db.database import AsyncSessionLocal, engine, Base
from app.db.models import StudentProfile, LeetCodeProfile
from app.leetcode.profile_repository import LeetCodeProfileRepository
from app.leetcode.assessment import LeetCodeSkillAssessmentService
from app.leetcode.data_provider import (
    LeetCodeDataProvider,
    LeetCodeProviderRegistry,
    ProviderResultStatus,
    ProviderResult
)

def test_leetcode_skill_assessment_suite():
    print("\n======================================================================")
    print("  LEETCODE INTEGRATION TASK 10: SKILL ASSESSMENT AUDIT TEST SUITE")
    print("======================================================================\n")

    async def _run():
        # Ensure database table schema is updated
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
            res_st = await db.execute(select(StudentProfile).limit(1))
            student = res_st.scalar_one_or_none()
            assert student is not None
            cand_id = student.id

            # 1. Test Unverified Profile Assessment Guardrail
            print("  [STEP 1] Testing unverified profile assessment guardrail...")
            stmt = select(LeetCodeProfile).where(LeetCodeProfile.candidate_id == cand_id)
            res_lc = await db.execute(stmt)
            prof = res_lc.scalar_one_or_none()
            if prof:
                prof.verification_status = "PENDING"
                prof.ownership_status = "PENDING"
                await db.commit()

            unverif_res = await LeetCodeSkillAssessmentService.evaluate_candidate(db, cand_id)
            print(f"    - Unverified Candidate Status: '{unverif_res['assessment_status']}'")
            print(f"    - Confidence:                 '{unverif_res['confidence']}'")
            print(f"    - Explanation:                '{unverif_res['explanation']}'")

            assert unverif_res["assessment_status"] == "UNVERIFIED_CANDIDATE"
            assert unverif_res["confidence"] == "NONE"

            # 2. Test Verified Profile Assessment with Real Metrics
            print("\n  [STEP 2] Testing verified profile evaluation with multi-dimensional metrics...")
            await LeetCodeProfileRepository.save_verified_profile(
                db, cand_id, "assessment_hero_user", "https://leetcode.com/u/assessment_hero_user", "BIO_TOKEN_CHALLENGE", "NOT_AVAILABLE"
            )

            class AuthorizedMockAssessmentProvider(LeetCodeDataProvider):
                async def check_profile_exists(self, username: str) -> ProviderResult:
                    return ProviderResult(status=ProviderResultStatus.SUCCESS, message="OK", timestamp="2026-08-14T00:00:00Z")
                async def get_profile_data(self, username: str) -> ProviderResult:
                    return ProviderResult(status=ProviderResultStatus.SUCCESS, message="OK", timestamp="2026-08-14T00:00:00Z")
                async def get_profile_statistics(self, username: str) -> ProviderResult:
                    return ProviderResult(
                        status=ProviderResultStatus.SUCCESS,
                        message="Fetched",
                        data={
                            "username": username,
                            "total_problems_solved": 380,
                            "easy_solved": 120,
                            "medium_solved": 210,
                            "hard_solved": 50,
                            "languages": {"Python": 250, "Java": 130},
                            "skills": ["Dynamic Programming", "Trees & Graphs", "Binary Search"],
                            "badges": [{"name": "Knight Badge", "icon": "https://assets.leetcode.com/knight.png"}],
                            "contest_rating": 1920.0,
                            "contest_rank": 8400,
                            "recent_activity": [{"id": 1, "title": "Merge K Sorted Lists"}]
                        },
                        timestamp="2026-08-14T00:00:00Z"
                    )
                async def get_provider_status(self) -> dict:
                    return {"is_configured": True}

            LeetCodeProviderRegistry.set_provider(AuthorizedMockAssessmentProvider())

            # Update metrics first
            from app.leetcode.metrics_service import LeetCodeMetricsService
            await LeetCodeMetricsService.fetch_and_update_metrics(db, cand_id)

            eval_res = await LeetCodeSkillAssessmentService.evaluate_candidate(db, cand_id)
            print(f"    - Assessment Status:   '{eval_res['assessment_status']}'")
            print(f"    - Confidence Index:    '{eval_res['confidence']}'")
            print(f"    - Strengths Found ({len(eval_res['strengths'])}):")
            for s in eval_res["strengths"]:
                print(f"      • {s}")
            print(f"    - Difficulty Profile:  {eval_res['difficulty_profile']}")
            print(f"    - Language Strengths: {eval_res['language_strengths']}")
            print(f"    - Topic Strengths:    {eval_res['topic_strengths']}")

            assert eval_res["assessment_status"] == "VERIFIED_ASSESSMENT"
            assert eval_res["confidence"] == "HIGH"
            assert len(eval_res["strengths"]) >= 3
            assert eval_res["difficulty_profile"]["medium"] == 210
            assert eval_res["difficulty_profile"]["ratio_medium_hard"] is not None

            # 3. Test Rule: Easy-Only Problem Solving Non-Expert Classification
            print("\n  [STEP 3] Testing non-misleading rule (Easy-only problems does NOT grant expert status)...")
            class EasyOnlyMockProvider(LeetCodeDataProvider):
                async def check_profile_exists(self, username: str) -> ProviderResult:
                    return ProviderResult(status=ProviderResultStatus.SUCCESS, message="OK", timestamp="2026-08-14T00:00:00Z")
                async def get_profile_data(self, username: str) -> ProviderResult:
                    return ProviderResult(status=ProviderResultStatus.SUCCESS, message="OK", timestamp="2026-08-14T00:00:00Z")
                async def get_profile_statistics(self, username: str) -> ProviderResult:
                    return ProviderResult(
                        status=ProviderResultStatus.SUCCESS,
                        message="Fetched",
                        data={
                            "username": username,
                            "total_problems_solved": 150,
                            "easy_solved": 150,
                            "medium_solved": 0,
                            "hard_solved": 0,
                            "languages": {"Python": 150},
                            "skills": ["Basic Math"],
                            "recent_activity": []
                        },
                        timestamp="2026-08-14T00:00:00Z"
                    )
                async def get_provider_status(self) -> dict:
                    return {"is_configured": True}

            LeetCodeProviderRegistry.set_provider(EasyOnlyMockProvider())
            await LeetCodeMetricsService.fetch_and_update_metrics(db, cand_id)

            easy_eval = await LeetCodeSkillAssessmentService.evaluate_candidate(db, cand_id)
            print(f"    - Easy-Only Areas to Improve: {easy_eval['areas_to_improve']}")
            assert any("Medium-difficulty" in area for area in easy_eval["areas_to_improve"]), "Must suggest transitioning to Medium problems!"

            # Reset provider registry
            LeetCodeProviderRegistry.reset()

    asyncio.run(_run())

    print("\n======================================================================")
    print("  TASK 10 LEETCODE SKILL ASSESSMENT AUDIT: PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_leetcode_skill_assessment_suite()
