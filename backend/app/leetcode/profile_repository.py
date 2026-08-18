import logging
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import LeetCodeProfile

logger = logging.getLogger(__name__)

class LeetCodeProfileRepository:
    """
    Repository for persisting and retrieving verified LeetCode profile records in PostgreSQL.
    Enforces strict data integrity: only stores VERIFIED state after legitimate ownership confirmation.
    Zero passwords, session cookies, auth tokens, or fabricated statistics stored.
    """

    @staticmethod
    async def get_profile_by_candidate(db: AsyncSession, candidate_id: int) -> Optional[LeetCodeProfile]:
        """
        Retrieves the LeetCodeProfile record for a given student candidate.
        """
        stmt = select(LeetCodeProfile).where(LeetCodeProfile.candidate_id == candidate_id)
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    @staticmethod
    async def save_verified_profile(
        db: AsyncSession,
        candidate_id: int,
        leetcode_username: str,
        normalized_profile_url: str,
        verification_method: str = "BIO_TOKEN_CHALLENGE",
        data_status: str = "NOT_AVAILABLE"
    ) -> LeetCodeProfile:
        """
        Persists a legitimately verified LeetCode profile.
        Sets ownership_status = VERIFIED, verification_status = VERIFIED, and verified_at timestamp.
        Consumes verification challenge token to ensure single-use security.
        """
        now = datetime.utcnow()
        stmt = select(LeetCodeProfile).where(LeetCodeProfile.candidate_id == candidate_id)
        res = await db.execute(stmt)
        lc_prof = res.scalar_one_or_none()

        if not lc_prof:
            lc_prof = LeetCodeProfile(
                candidate_id=candidate_id,
                leetcode_profile_url=normalized_profile_url,
                leetcode_username=leetcode_username,
                account_exists=True,
                ownership_status="VERIFIED",
                verification_status="VERIFIED",
                verification_method=verification_method,
                verification_challenge_token=None, # Single-use token consumed
                verified_at=now,
                last_verified_at=now,
                data_status=data_status,
                last_data_refresh_at=now if data_status == "AVAILABLE" else None
            )
            db.add(lc_prof)
        else:
            lc_prof.leetcode_profile_url = normalized_profile_url
            lc_prof.leetcode_username = leetcode_username
            lc_prof.account_exists = True
            lc_prof.ownership_status = "VERIFIED"
            lc_prof.verification_status = "VERIFIED"
            lc_prof.verification_method = verification_method
            lc_prof.verification_challenge_token = None # Single-use token consumed
            lc_prof.verified_at = now
            lc_prof.last_verified_at = now
            lc_prof.data_status = data_status
            if data_status == "AVAILABLE":
                lc_prof.last_data_refresh_at = now
            elif data_status == "NOT_AVAILABLE":
                lc_prof.total_problems_solved = None
                lc_prof.easy_solved = None
                lc_prof.medium_solved = None
                lc_prof.hard_solved = None
                lc_prof.languages_json = None
                lc_prof.skills_json = None
                lc_prof.badges_json = None
                lc_prof.contest_rating = None
                lc_prof.contest_rank = None
                lc_prof.recent_activity_json = None

        await db.commit()
        await db.refresh(lc_prof)
        return lc_prof

    @staticmethod
    async def update_data_status(
        db: AsyncSession,
        candidate_id: int,
        data_status: str
    ) -> Optional[LeetCodeProfile]:
        """
        Updates profile data availability status without altering ownership verification state.
        """
        stmt = select(LeetCodeProfile).where(LeetCodeProfile.candidate_id == candidate_id)
        res = await db.execute(stmt)
        lc_prof = res.scalar_one_or_none()

        if lc_prof:
            now = datetime.utcnow()
            lc_prof.data_status = data_status
            if data_status == "AVAILABLE":
                lc_prof.last_data_refresh_at = now
            await db.commit()
            await db.refresh(lc_prof)

        return lc_prof
