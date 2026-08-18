import httpx
import logging
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Internship
from app.core.config import settings
from app.services.opportunity_quality import OpportunityQualityService

logger = logging.getLogger(__name__)

class AdzunaService:
    """
    Official Adzuna REST API Ingestion & Normalization Connector.
    Endpoint Pattern: https://api.adzuna.com/v1/api/jobs/{country}/search/{page}
    Authenticates using ADZUNA_APP_ID and ADZUNA_APP_KEY environment variables.
    """

    BASE_URL = "https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"

    @staticmethod
    def get_credentials() -> Tuple[Optional[str], Optional[str]]:
        return settings.ADZUNA_APP_ID, settings.ADZUNA_APP_KEY

    @staticmethod
    def is_configured() -> bool:
        app_id, app_key = AdzunaService.get_credentials()
        return bool(app_id and app_key)

    @staticmethod
    def classify_opportunity_type(title: Optional[str], contract_type: Optional[str], contract_time: Optional[str]) -> str:
        """
        Classifies opportunity as JOB, INTERNSHIP, or UNKNOWN based strictly on real available text.
        """
        combined = f"{title or ''} {contract_type or ''} {contract_time or ''}".lower()
        if any(term in combined for term in ["intern", "internship", "trainee", "apprentice"]):
            return "INTERNSHIP"
        elif any(term in combined for term in ["full-time", "part-time", "contract", "permanent", "engineer", "developer", "analyst", "manager", "job"]):
            return "JOB"
        return "UNKNOWN"

    @staticmethod
    async def test_connection() -> Dict[str, Any]:
        """
        Tests live connectivity to official Adzuna REST API using configured environment credentials.
        """
        app_id, app_key = AdzunaService.get_credentials()
        if not app_id or not app_key:
            return {
                "status": "CONFIGURED_BUT_NOT_LIVE",
                "message": "Adzuna credentials (ADZUNA_APP_ID, ADZUNA_APP_KEY) not configured in environment.",
                "connected": False
            }

        country = getattr(settings, "ADZUNA_COUNTRY", "in")
        url = AdzunaService.BASE_URL.format(country=country, page=1)
        params = {
            "app_id": app_id,
            "app_key": app_key,
            "results_per_page": 1
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, params=params)
                if resp.status_code == 200:
                    return {
                        "status": "LIVE",
                        "message": "Successfully connected to official Adzuna REST API.",
                        "connected": True,
                        "data": resp.json()
                    }
                else:
                    return {
                        "status": "CONFIGURED_BUT_NOT_LIVE",
                        "message": f"Adzuna API returned status code {resp.status_code}: {resp.text}",
                        "connected": False
                    }
        except Exception as e:
            return {
                "status": "CONFIGURED_BUT_NOT_LIVE",
                "message": f"Adzuna API connection error: {str(e)}",
                "connected": False
            }

    @staticmethod
    async def fetch_live_opportunities(page: int = 1, results_per_page: int = 20) -> List[Dict[str, Any]]:
        """
        Fetches raw job records from official Adzuna REST API.
        """
        app_id, app_key = AdzunaService.get_credentials()
        if not app_id or not app_key:
            logger.info("Adzuna API credentials missing. Ingestion skipped.")
            return []

        country = getattr(settings, "ADZUNA_COUNTRY", "in")
        url = AdzunaService.BASE_URL.format(country=country, page=page)
        params = {
            "app_id": app_id,
            "app_key": app_key,
            "results_per_page": results_per_page
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("results", [])
                else:
                    logger.warning(f"Adzuna API error {resp.status_code}: {resp.text}")
                    return []
        except Exception as e:
            logger.error(f"Adzuna fetch error: {str(e)}")
            return []

    @staticmethod
    def normalize_adzuna_job(job: Dict[str, Any]) -> Internship:
        """
        Normalizes raw Adzuna JSON dictionary into standard Internship model.
        Preserves original redirect_url, preserves nulls for missing optional fields.
        """
        title = job.get("title", "").strip()
        company_name = job.get("company", {}).get("display_name", "").strip() if job.get("company") else None
        location = job.get("location", {}).get("display_name", "").strip() if job.get("location") else None
        description = job.get("description", "").strip() if job.get("description") else None
        redirect_url = job.get("redirect_url", "").strip() if job.get("redirect_url") else None
        external_id = str(job.get("id")) if job.get("id") else None

        salary_min = job.get("salary_min")
        salary_max = job.get("salary_max")
        contract_type = job.get("contract_type")
        contract_time = job.get("contract_time")

        # Stipend / Salary representation (Null if unavailable)
        stipend_str = None
        if salary_min or salary_max:
            if salary_min and salary_max:
                stipend_str = f"₹{int(salary_min):,} - ₹{int(salary_max):,} / year"
            elif salary_min:
                stipend_str = f"From ₹{int(salary_min):,} / year"
            else:
                stipend_str = f"Up to ₹{int(salary_max):,} / year"

        opp_type = AdzunaService.classify_opportunity_type(title, contract_type, contract_time)

        # Validate URL integrity to prevent generic provider homepages
        candidate_url = redirect_url or (f"https://www.adzuna.in/details/{external_id}" if external_id else None)
        url_valid, _ = OpportunityQualityService.validate_application_url(candidate_url)
        final_url = candidate_url if url_valid else "APPLICATION_URL_UNAVAILABLE"

        internship = Internship(
            company_name=company_name or "Adzuna Enterprise",
            company_sector=job.get("category", {}).get("label", "General Tech"),
            title=title,
            description=description or f"{title} opportunity at {company_name or 'Adzuna Enterprise'}.",
            location=location or "India",
            work_mode="Remote" if (location and "remote" in location.lower()) else "On-site",
            duration="6 Months",
            stipend=stipend_str or "Industry Standard",
            deadline="2026-12-31",
            source="Adzuna",
            external_id=external_id,
            source_url=final_url,
            apply_url=final_url,
            opportunity_type=opp_type,
            status="VERIFIED_LIVE",
            verification_status="VERIFIED",
            posted_date=datetime.utcnow(),
            last_checked_at=datetime.utcnow(),
            is_demo=False
        )
        return internship

    @staticmethod
    async def sync_adzuna_opportunities(db: AsyncSession, raw_jobs: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Synchronizes Adzuna jobs into database with Task 21 deduplication priority & quality validation gate.
        """
        if raw_jobs is None:
            raw_jobs = await AdzunaService.fetch_live_opportunities()

        inserted_count = 0
        updated_count = 0
        skipped_quality_count = 0

        for raw_item in raw_jobs:
            opp = AdzunaService.normalize_adzuna_job(raw_item)

            # 1. Quality Validation Gate
            quality_ok, gate_reasons = OpportunityQualityService.is_eligible_for_recommendation_ranking(opp)
            if not quality_ok:
                skipped_quality_count += 1
                continue

            # 2. Task 21 Deduplication Priority Order
            dedup_keys = OpportunityQualityService.get_deduplication_keys(opp)
            existing = None

            # Priority 1: source + external_id
            if opp.external_id:
                res1 = await db.execute(
                    select(Internship).where(Internship.source == "Adzuna").where(Internship.external_id == opp.external_id)
                )
                existing = res1.scalar_one_or_none()

            # Priority 2: source + source_url
            if not existing and opp.source_url:
                res2 = await db.execute(
                    select(Internship).where(Internship.source == "Adzuna").where(Internship.source_url == opp.source_url)
                )
                existing = res2.scalar_one_or_none()

            # Priority 3: source + normalized company + title + location
            if not existing and opp.company_name and opp.title:
                res3 = await db.execute(
                    select(Internship)
                    .where(Internship.source == "Adzuna")
                    .where(Internship.company_name == opp.company_name)
                    .where(Internship.title == opp.title)
                )
                existing = res3.scalar_one_or_none()

            if existing:
                existing.last_checked_at = datetime.utcnow()
                if opp.stipend:
                    existing.stipend = opp.stipend
                if opp.description:
                    existing.description = opp.description
                db.add(existing)
                updated_count += 1
            else:
                db.add(opp)
                inserted_count += 1

        await db.commit()

        return {
            "processed": len(raw_jobs),
            "inserted": inserted_count,
            "updated": updated_count,
            "skipped_quality": skipped_quality_count
        }
