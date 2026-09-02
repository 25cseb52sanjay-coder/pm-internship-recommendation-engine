import httpx
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.ingestion.source_connectors.base import BaseConnector
from app.jobvetta.config import JobvettaConfig
from app.jobvetta.schemas import NormalizedJobvettaJob
from app.jobvetta.classifier import JobvettaClassifier

logger = logging.getLogger(__name__)

DEFAULT_JOBVETTA_API_URL = "https://api.jobvetta.com/v1/jobs"

class JobvettaConnector(BaseConnector):
    """
    Official Connector for the Jobvetta REST API v1.
    Endpoints:
      - GET https://api.jobvetta.com/v1/jobs
      - GET https://api.jobvetta.com/v1/jobs/{job_id}
    Headers:
      - Authorization: Bearer JOBVETTA_API_KEY
    Documentation: https://www.jobvetta.com/api
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        configured_key, configured_base_url = JobvettaConfig.get_credentials()
        self.api_key = api_key or configured_key
        self.base_url = (base_url or configured_base_url).rstrip("/")
        auth_status = "AUTHORIZED" if bool(self.api_key and self.api_key.strip()) else "NOT_CONFIGURED"

        super().__init__(
            source_name="Jobvetta Official REST API",
            source_type="JOBVETTA_API",
            authorization_status=auth_status
        )

        self.timeout = 15.0

    def get_headers(self) -> Dict[str, str]:
        """Returns HTTP Authorization headers for Jobvetta API."""
        headers = {
            "Accept": "application/json",
            "User-Agent": "PM-Internship-Recommendation-Engine/1.0"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key.strip()}"
        return headers

    async def fetch_jobs(
        self,
        q: Optional[str] = None,
        location: Optional[str] = None,
        days: Optional[int] = None,
        limit: int = 20,
        page: int = 1
    ) -> Dict[str, Any]:
        """
        Fetches live jobs from Jobvetta REST API GET /jobs endpoint.
        Query parameters: q, location, days, limit, page
        """
        if not self.check_authorization():
            logger.warning("JobvettaConnector: JOBVETTA_API_KEY not configured. Skipping live API call.")
            return {"status_code": 401, "results": [], "count": 0, "error": "NOT_CONFIGURED"}

        url = f"{self.base_url}/jobs"
        params: Dict[str, Any] = {"limit": limit, "page": page}
        if q:
            params["q"] = q
        if location:
            params["location"] = location
        if days:
            params["days"] = days

        masked_key = f"{self.api_key[:4]}***" if self.api_key and len(self.api_key) >= 4 else "***"
        logger.info(f"Connecting to Jobvetta API GET /jobs (q='{q}', location='{location}', limit={limit}, key='{masked_key}')")

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            try:
                response = await client.get(url, headers=self.get_headers(), params=params)
                status_code = response.status_code

                if status_code == 200:
                    payload = response.json()
                    results = payload.get("data", payload.get("jobs", payload.get("results", [])))
                    if isinstance(payload, list):
                        results = payload

                    total_count = payload.get("total", payload.get("count", len(results))) if isinstance(payload, dict) else len(results)
                    logger.info(f"Successfully retrieved {len(results)} opportunities from Jobvetta API (Total: {total_count}).")
                    return {
                        "status_code": 200,
                        "results": results,
                        "count": total_count,
                        "page": page,
                        "query": q
                    }
                elif status_code == 429:
                    logger.warning("Jobvetta API rate limit exceeded (HTTP 429). Deferring request.")
                    return {
                        "status_code": 429,
                        "results": [],
                        "count": 0,
                        "error": "RATE_LIMITED"
                    }
                elif status_code in (401, 403):
                    logger.error(f"Jobvetta API authentication failed (HTTP {status_code}). Check JOBVETTA_API_KEY.")
                    return {
                        "status_code": status_code,
                        "results": [],
                        "count": 0,
                        "error": "UNAUTHORIZED"
                    }
                else:
                    logger.error(f"Jobvetta API request failed with HTTP status {status_code}")
                    return {
                        "status_code": status_code,
                        "results": [],
                        "count": 0,
                        "error": f"HTTP {status_code}"
                    }
            except Exception as e:
                logger.error(f"Error connecting to Jobvetta API: {str(e)}")
                return {
                    "status_code": 500,
                    "results": [],
                    "count": 0,
                    "error": str(e)
                }

    async def fetch_job_detail(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetches individual job details from Jobvetta API GET /jobs/{job_id}.
        """
        if not self.check_authorization():
            return None

        url = f"{self.base_url}/jobs/{job_id}"
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            try:
                response = await client.get(url, headers=self.get_headers())
                if response.status_code == 200:
                    payload = response.json()
                    return payload.get("data", payload.get("job", payload))
                return None
            except Exception as e:
                logger.error(f"Error fetching Jobvetta job detail {job_id}: {str(e)}")
                return None

    async def fetch(self) -> List[Dict[str, Any]]:
        """Implementation of BaseConnector.fetch() for general ingestion."""
        res = await self.fetch_jobs(limit=50)
        return res.get("results", [])

    def validate_raw(self, raw_record: Dict[str, Any]) -> bool:
        """Validates presence of minimum mandatory fields in Jobvetta raw record."""
        if not isinstance(raw_record, dict):
            return False
        has_id = bool(raw_record.get("id") or raw_record.get("job_id") or raw_record.get("_id") or raw_record.get("external_id"))
        has_title = bool(raw_record.get("title") or raw_record.get("job_title") or raw_record.get("name"))
        has_company = bool(raw_record.get("company") or raw_record.get("company_name") or raw_record.get("employer"))
        return has_id and has_title and has_company

    def normalize(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes raw record into dict representation."""
        norm_obj = self.normalize_to_schema(raw_record)
        return norm_obj.model_dump()

    def normalize_to_schema(self, raw: Dict[str, Any]) -> NormalizedJobvettaJob:
        """
        Normalizes a raw Jobvetta API job record into a NormalizedJobvettaJob.
        """
        ext_id = str(raw.get("id") or raw.get("job_id") or raw.get("_id") or raw.get("external_id") or "")
        title = (raw.get("title") or raw.get("job_title") or raw.get("name") or "Opportunity").strip()
        comp = raw.get("company") or raw.get("company_name") or raw.get("employer") or "Hiring Company"
        if isinstance(comp, dict):
            company_name = comp.get("name") or comp.get("display_name") or "Hiring Company"
        else:
            company_name = str(comp).strip()

        desc = raw.get("description") or raw.get("job_description") or raw.get("summary") or f"{title} at {company_name}"

        loc = raw.get("location") or raw.get("job_location") or raw.get("city") or "India"
        if isinstance(loc, dict):
            location_str = loc.get("display_name") or loc.get("city") or loc.get("name") or "India"
        else:
            location_str = str(loc).strip()

        emp_type = raw.get("employment_type") or raw.get("job_type") or raw.get("type") or ""
        opp_type = JobvettaClassifier.classify_opportunity_type(title, desc, str(emp_type))
        work_mode = JobvettaClassifier.classify_work_mode(location_str, desc)
        sector = JobvettaClassifier.classify_sector(str(raw.get("category", "")), title, desc)
        extracted_skills = JobvettaClassifier.extract_skills(title, desc)

        # Parse salary / stipend fields
        sal_min = raw.get("salary_min") or raw.get("stipend_min") or raw.get("min_salary")
        sal_max = raw.get("salary_max") or raw.get("stipend_max") or raw.get("max_salary")
        curr = raw.get("currency") or "INR"

        stipend_str = "Competitive Compensation"
        if sal_min and sal_max:
            stipend_str = f"₹{int(sal_min):,} - ₹{int(sal_max):,} / month" if opp_type == "INTERNSHIP" else f"₹{int(sal_min):,} - ₹{int(sal_max):,} / year"
        elif sal_min:
            stipend_str = f"From ₹{int(sal_min):,} / month" if opp_type == "INTERNSHIP" else f"From ₹{int(sal_min):,} / year"
        elif sal_max:
            stipend_str = f"Up to ₹{int(sal_max):,} / month" if opp_type == "INTERNSHIP" else f"Up to ₹{int(sal_max):,} / year"

        # URLs
        apply_url = raw.get("apply_url") or raw.get("application_url") or raw.get("url") or raw.get("redirect_url")
        source_url = raw.get("jobvetta_url") or raw.get("source_url") or (f"https://www.jobvetta.com/jobs/{ext_id}" if ext_id else "https://www.jobvetta.com/")

        if not apply_url:
            apply_url = source_url

        return NormalizedJobvettaJob(
            external_id=ext_id,
            title=title,
            company=company_name,
            description=desc,
            location=location_str,
            category=sector,
            opportunity_type=opp_type,
            employment_type=str(emp_type) if emp_type else None,
            work_mode=work_mode,
            salary_min=float(sal_min) if sal_min else None,
            salary_max=float(sal_max) if sal_max else None,
            currency=curr,
            stipend_str=stipend_str,
            skills=extracted_skills,
            min_qualification="Graduate",
            preferred_degree="B.Tech" if "software" in title.lower() or "developer" in title.lower() else "Graduate",
            source="Jobvetta",
            source_url=source_url,
            apply_url=apply_url,
            raw_metadata=raw
        )
