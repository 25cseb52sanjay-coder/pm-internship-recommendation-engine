import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import LeetCodeProfile
from app.leetcode.data_provider import (
    LeetCodeProviderRegistry,
    ProviderResultStatus
)

logger = logging.getLogger(__name__)

# Data freshness threshold (24 hours)
METRICS_STALE_THRESHOLD_HOURS = 24

class LeetCodeMetricsService:
    """
    Service for retrieving and managing real LeetCode profile metrics.
    Enforces strict safety rules:
    - Never fabricates missing metrics or estimates problem counts.
    - Never uses web scraping, crawling, or private undocumented endpoints.
    - Stores None/null for unavailable metrics (never defaults missing metrics to 0).
    - Tracks freshness (last_data_refresh_at) and flags stale metrics.
    """

    @staticmethod
    async def fetch_and_update_metrics(
        db: AsyncSession,
        candidate_id: int
    ) -> Dict[str, Any]:
        """
        Retrieves real profile metrics via registered LeetCodeDataProvider.
        If no authorized provider exists, safely reports DATA_UNAVAILABLE without fabricating values.
        """
        stmt = select(LeetCodeProfile).where(LeetCodeProfile.candidate_id == candidate_id)
        res = await db.execute(stmt)
        lc_prof = res.scalar_one_or_none()

        if not lc_prof or lc_prof.verification_status != "VERIFIED":
            return {
                "status": "NOT_VERIFIED",
                "candidate_id": candidate_id,
                "data_status": "NOT_AVAILABLE",
                "message": "Candidate LeetCode profile is not verified. Verification required before metrics retrieval.",
                "metrics": None
            }

        username = lc_prof.leetcode_username
        provider = LeetCodeProviderRegistry.get_provider()
        provider_res = await provider.get_profile_statistics(username)

        now = datetime.utcnow()

        if provider_res.status in (ProviderResultStatus.UNAVAILABLE, ProviderResultStatus.NOT_PERMITTED):
            # Record limitation without fabricating data
            lc_prof.data_status = "NOT_AVAILABLE"
            await db.commit()
            return {
                "status": "DATA_UNAVAILABLE",
                "candidate_id": candidate_id,
                "leetcode_username": username,
                "data_status": "NOT_AVAILABLE",
                "message": f"LeetCode real metrics limitation: {provider_res.message} Architecture ready.",
                "last_data_refresh_at": lc_prof.last_data_refresh_at.isoformat() if lc_prof.last_data_refresh_at else None,
                "metrics": None
            }

        if provider_res.status == ProviderResultStatus.SUCCESS and provider_res.data:
            stats = provider_res.data

            # Update real metrics from authorized provider
            lc_prof.total_problems_solved = stats.get("total_problems_solved")
            lc_prof.easy_solved = stats.get("easy_solved")
            lc_prof.medium_solved = stats.get("medium_solved")
            lc_prof.hard_solved = stats.get("hard_solved")

            lc_prof.languages_json = json.dumps(stats.get("languages")) if stats.get("languages") is not None else None
            lc_prof.skills_json = json.dumps(stats.get("skills")) if stats.get("skills") is not None else None
            lc_prof.badges_json = json.dumps(stats.get("badges")) if stats.get("badges") is not None else None

            lc_prof.contest_rating = stats.get("contest_rating")
            lc_prof.contest_rank = stats.get("contest_rank")
            lc_prof.recent_activity_json = json.dumps(stats.get("recent_activity")) if stats.get("recent_activity") is not None else None

            lc_prof.data_status = "AVAILABLE"
            lc_prof.last_data_refresh_at = now

            await db.commit()
            await db.refresh(lc_prof)

            return {
                "status": "SUCCESS",
                "candidate_id": candidate_id,
                "leetcode_username": username,
                "data_status": "AVAILABLE",
                "last_data_refresh_at": now.isoformat(),
                "metrics": {
                    "username": username,
                    "total_problems_solved": lc_prof.total_problems_solved,
                    "easy_solved": lc_prof.easy_solved,
                    "medium_solved": lc_prof.medium_solved,
                    "hard_solved": lc_prof.hard_solved,
                    "languages": json.loads(lc_prof.languages_json) if lc_prof.languages_json else None,
                    "skills": json.loads(lc_prof.skills_json) if lc_prof.skills_json else None,
                    "badges": json.loads(lc_prof.badges_json) if lc_prof.badges_json else None,
                    "contest_rating": lc_prof.contest_rating,
                    "contest_rank": lc_prof.contest_rank,
                    "recent_activity": json.loads(lc_prof.recent_activity_json) if lc_prof.recent_activity_json else None
                }
            }

        # Error handling
        lc_prof.data_status = "ERROR"
        await db.commit()
        return {
            "status": "ERROR",
            "candidate_id": candidate_id,
            "leetcode_username": username,
            "data_status": "ERROR",
            "message": f"Provider metrics error: {provider_res.message}",
            "metrics": None
        }

    @staticmethod
    async def get_candidate_metrics(
        db: AsyncSession,
        candidate_id: int
    ) -> Dict[str, Any]:
        """
        Fetches stored metrics from database and checks data freshness.
        """
        stmt = select(LeetCodeProfile).where(LeetCodeProfile.candidate_id == candidate_id)
        res = await db.execute(stmt)
        lc_prof = res.scalar_one_or_none()

        if not lc_prof:
            return {
                "data_status": "NOT_AVAILABLE",
                "metrics": None,
                "message": "No LeetCode profile found for candidate."
            }

        # Check Freshness Threshold (24 hours)
        current_status = lc_prof.data_status
        if lc_prof.last_data_refresh_at:
            if (datetime.utcnow() - lc_prof.last_data_refresh_at) > timedelta(hours=METRICS_STALE_THRESHOLD_HOURS):
                current_status = "STALE"

        metrics_data = None
        if lc_prof.data_status == "AVAILABLE":
            metrics_data = {
                "username": lc_prof.leetcode_username,
                "total_problems_solved": lc_prof.total_problems_solved,
                "easy_solved": lc_prof.easy_solved,
                "medium_solved": lc_prof.medium_solved,
                "hard_solved": lc_prof.hard_solved,
                "languages": json.loads(lc_prof.languages_json) if lc_prof.languages_json else None,
                "skills": json.loads(lc_prof.skills_json) if lc_prof.skills_json else None,
                "badges": json.loads(lc_prof.badges_json) if lc_prof.badges_json else None,
                "contest_rating": lc_prof.contest_rating,
                "contest_rank": lc_prof.contest_rank,
                "recent_activity": json.loads(lc_prof.recent_activity_json) if lc_prof.recent_activity_json else None
            }

        return {
            "candidate_id": candidate_id,
            "leetcode_username": lc_prof.leetcode_username,
            "verification_status": lc_prof.verification_status,
            "data_status": current_status,
            "last_data_refresh_at": lc_prof.last_data_refresh_at.isoformat() if lc_prof.last_data_refresh_at else None,
            "metrics": metrics_data
        }
