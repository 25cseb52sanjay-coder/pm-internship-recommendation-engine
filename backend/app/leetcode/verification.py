import logging
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import LeetCodeProfile
from app.leetcode.url_validator import validate_and_normalize_leetcode_url
from app.leetcode.data_provider import (
    LeetCodeProviderRegistry,
    ProviderResultStatus
)

logger = logging.getLogger(__name__)

# Challenge token validity TTL (15 minutes)
CHALLENGE_TOKEN_TTL_MINUTES = 15

class LeetCodeVerificationService:
    """
    Verification service managing real LeetCode profile existence checks
    and candidate account ownership validation protocols via LeetCodeDataProvider.
    """

    @staticmethod
    async def verify_account_existence(raw_input: str) -> Dict[str, Any]:
        """
        Verifies whether a LeetCode handle or URL syntactically validates AND
        legitimately exists via the registered LeetCodeDataProvider.
        """
        url_val = validate_and_normalize_leetcode_url(raw_input)
        if not url_val["valid"]:
            return {
                "account_exists": False,
                "status": "ACCOUNT_NOT_FOUND",
                "leetcode_username": None,
                "normalized_profile_url": None,
                "message": url_val["error"],
                "provider_status": "INVALID_SYNTAX"
            }

        username = url_val["leetcode_username"]
        normalized_url = url_val["normalized_profile_url"]

        provider = LeetCodeProviderRegistry.get_provider()
        provider_res = await provider.check_profile_exists(username)

        if provider_res.status == ProviderResultStatus.SUCCESS:
            return {
                "account_exists": True,
                "status": "ACCOUNT_FOUND",
                "leetcode_username": username,
                "normalized_profile_url": normalized_url,
                "message": f"Real profile '@{username}' confirmed by authorized provider.",
                "provider_status": provider_res.status.value
            }
        elif provider_res.status == ProviderResultStatus.NOT_FOUND:
            return {
                "account_exists": False,
                "status": "ACCOUNT_NOT_FOUND",
                "leetcode_username": username,
                "normalized_profile_url": normalized_url,
                "message": f"Profile '@{username}' was not found on LeetCode.",
                "provider_status": provider_res.status.value
            }
        elif provider_res.status in (ProviderResultStatus.UNAVAILABLE, ProviderResultStatus.NOT_PERMITTED):
            return {
                "account_exists": False,
                "status": "DATA_UNAVAILABLE",
                "leetcode_username": username,
                "normalized_profile_url": normalized_url,
                "message": f"LeetCode live verification limitation: {provider_res.message}",
                "provider_status": provider_res.status.value
            }
        else:
            return {
                "account_exists": False,
                "status": "VERIFICATION_FAILED",
                "leetcode_username": username,
                "normalized_profile_url": normalized_url,
                "message": f"Provider verification error: {provider_res.message}",
                "provider_status": provider_res.status.value
            }

    @staticmethod
    async def generate_ownership_challenge(
        db: AsyncSession,
        candidate_id: int,
        raw_input: str
    ) -> Dict[str, Any]:
        """
        Generates a cryptographically secure, one-time verification challenge token
        bound to the candidate ID and the submitted LeetCode handle.
        """
        url_val = validate_and_normalize_leetcode_url(raw_input)
        if not url_val["valid"]:
            return {
                "status": "FAILED",
                "message": url_val["error"],
                "challenge_token": None
            }

        username = url_val["leetcode_username"]
        normalized_url = url_val["normalized_profile_url"]
        now = datetime.utcnow()
        expires_at = now + timedelta(minutes=CHALLENGE_TOKEN_TTL_MINUTES)

        # Generate cryptographically random single-use challenge token
        token_suffix = secrets.token_hex(4).upper()
        challenge_token = f"LEETCODE_VERIFY_{token_suffix}"

        # Fetch or create LeetCodeProfile record in PostgreSQL
        stmt = select(LeetCodeProfile).where(LeetCodeProfile.candidate_id == candidate_id)
        res = await db.execute(stmt)
        lc_prof = res.scalar_one_or_none()

        if not lc_prof:
            lc_prof = LeetCodeProfile(
                candidate_id=candidate_id,
                leetcode_profile_url=normalized_url,
                leetcode_username=username,
                account_exists=False,
                ownership_status="PENDING",
                verification_status="PENDING",
                verification_method="BIO_TOKEN_CHALLENGE",
                verification_challenge_token=challenge_token,
                verification_created_at=now,
                data_status="NOT_AVAILABLE"
            )
            db.add(lc_prof)
        else:
            lc_prof.leetcode_profile_url = normalized_url
            lc_prof.leetcode_username = username
            lc_prof.ownership_status = "PENDING"
            lc_prof.verification_status = "PENDING"
            lc_prof.verification_method = "BIO_TOKEN_CHALLENGE"
            lc_prof.verification_challenge_token = challenge_token
            lc_prof.verification_created_at = now

        await db.commit()
        await db.refresh(lc_prof)

        return {
            "status": "OWNERSHIP_PENDING",
            "candidate_id": candidate_id,
            "leetcode_username": username,
            "normalized_profile_url": normalized_url,
            "verification_method": "BIO_TOKEN_CHALLENGE",
            "challenge_token": challenge_token,
            "created_at": now.isoformat(),
            "expires_at": expires_at.isoformat(),
            "instructions": f"Paste token '{challenge_token}' into your public LeetCode bio, then click Verify."
        }

    @staticmethod
    async def verify_ownership_challenge(
        db: AsyncSession,
        candidate_id: int
    ) -> Dict[str, Any]:
        """
        Verifies ownership challenge via registered LeetCodeDataProvider.
        Strict Safety Rules:
        - Checks token expiry (TTL 15 minutes).
        - Enforces single-use token consumption upon verification.
        - Controls final VERIFIED state strictly on the backend.
        - If no authorized provider is configured, returns DATA_UNAVAILABLE without marking VERIFIED.
        """
        stmt = select(LeetCodeProfile).where(LeetCodeProfile.candidate_id == candidate_id)
        res = await db.execute(stmt)
        lc_prof = res.scalar_one_or_none()

        if not lc_prof or not lc_prof.verification_challenge_token:
            return {
                "verified": False,
                "status": "FAILED",
                "message": "No active ownership challenge found for candidate. Please initiate verification."
            }

        # Check Token Expiry (15-minute TTL)
        now = datetime.utcnow()
        created_at = lc_prof.verification_created_at or lc_prof.created_at
        if created_at and (now - created_at) > timedelta(minutes=CHALLENGE_TOKEN_TTL_MINUTES):
            lc_prof.ownership_status = "EXPIRED"
            lc_prof.verification_status = "FAILED"
            await db.commit()
            return {
                "verified": False,
                "status": "EXPIRED",
                "message": f"Verification challenge expired after {CHALLENGE_TOKEN_TTL_MINUTES} minutes. Please generate a new challenge."
            }

        target_token = lc_prof.verification_challenge_token
        username = lc_prof.leetcode_username

        # Query registered LeetCodeDataProvider for public profile bio data
        provider = LeetCodeProviderRegistry.get_provider()
        provider_res = await provider.get_profile_data(username)

        if provider_res.status in (ProviderResultStatus.UNAVAILABLE, ProviderResultStatus.NOT_PERMITTED):
            # Report limitation without falsely marking account VERIFIED
            return {
                "verified": False,
                "status": "DATA_UNAVAILABLE",
                "leetcode_username": username,
                "message": f"Ownership verification limitation: {provider_res.message} Account remains PENDING.",
                "provider_status": provider_res.status.value
            }

        if provider_res.status == ProviderResultStatus.SUCCESS and provider_res.data:
            bio_text = str(provider_res.data.get("about_me", "") or provider_res.data.get("bio", ""))
            if target_token in bio_text:
                # Backend controls final VERIFIED state
                lc_prof.ownership_status = "VERIFIED"
                lc_prof.verification_status = "VERIFIED"
                lc_prof.account_exists = True
                lc_prof.verified_at = now
                lc_prof.last_verified_at = now
                lc_prof.verification_challenge_token = None # Single-use token consumed
                await db.commit()
                await db.refresh(lc_prof)

                return {
                    "verified": True,
                    "status": "VERIFIED",
                    "leetcode_username": username,
                    "verified_at": now.isoformat(),
                    "message": f"Ownership of @{username} successfully verified!"
                }

        # Token missing or invalid bio
        lc_prof.ownership_status = "FAILED"
        lc_prof.verification_status = "FAILED"
        await db.commit()

        return {
            "verified": False,
            "status": "VERIFICATION_FAILED",
            "leetcode_username": username,
            "message": f"Verification challenge token '{target_token}' was not found in LeetCode profile bio for @{username}."
        }

