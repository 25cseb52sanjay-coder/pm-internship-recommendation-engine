import httpx
import logging
from typing import List, Dict, Any, Optional
from app.ingestion.source_connectors.base import BaseConnector
from app.adzuna.config import AdzunaConfig

logger = logging.getLogger(__name__)

BASE_ADZUNA_API_URL = "https://api.adzuna.com/v1/api/jobs"

class AdzunaConnector(BaseConnector):
    """
    Official Connector for the Adzuna REST API v1.
    Endpoint: GET https://api.adzuna.com/v1/api/jobs/{country}/search/{page}
    Documentation: https://developer.adzuna.com/overview
    """

    def __init__(
        self,
        country: str = "in",
        query: str = "software internship",
        results_per_page: int = 20,
        app_id: Optional[str] = None,
        app_key: Optional[str] = None
    ):
        configured_id, configured_key = AdzunaConfig.get_credentials()
        self.app_id = app_id or configured_id
        self.app_key = app_key or configured_key
        
        auth_status = "AUTHORIZED" if bool(self.app_id and self.app_key) else "NOT_CONFIGURED"

        super().__init__(
            source_name="Adzuna Official REST API",
            source_type="ADZUNA_API",
            authorization_status=auth_status
        )
        
        self.country = country.lower().strip()
        self.query = query
        self.results_per_page = results_per_page
        self.timeout = 15.0

    async def fetch_jobs(self, page: int = 1, query: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetches live jobs from Adzuna REST API endpoint.
        URL format: GET https://api.adzuna.com/v1/api/jobs/{country}/search/{page}
        Query parameters: app_id, app_key, results_per_page, what
        """
        if not self.check_authorization():
            logger.warning("AdzunaConnector: API credentials not configured. Skipping request.")
            return {"status_code": 401, "results": [], "count": 0, "error": "NOT_CONFIGURED"}

        search_query = query or self.query
        url = f"{BASE_ADZUNA_API_URL}/{self.country}/search/{page}"
        
        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "results_per_page": self.results_per_page,
            "what": search_query,
            "content-type": "application/json"
        }

        # Mask app_id for clean logging without exposing app_key
        masked_id = f"{self.app_id[:4]}***" if self.app_id and len(self.app_id) >= 4 else "***"
        logger.info(f"Connecting to Adzuna API endpoint: {url} (country='{self.country}', page={page}, app_id='{masked_id}', query='{search_query}')")

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            try:
                response = await client.get(url, params=params)
                status_code = response.status_code

                if status_code == 200:
                    payload = response.json()
                    results = payload.get("results", [])
                    total_count = payload.get("count", len(results))
                    logger.info(f"Successfully retrieved {len(results)} real jobs from Adzuna API (Total available: {total_count}).")
                    return {
                        "status_code": 200,
                        "results": results,
                        "count": total_count,
                        "page": page,
                        "query": search_query
                    }
                else:
                    logger.error(f"Adzuna API request failed with HTTP status {status_code}")
                    return {
                        "status_code": status_code,
                        "results": [],
                        "count": 0,
                        "error": f"HTTP {status_code}"
                    }
            except Exception as e:
                logger.error(f"Error connecting to Adzuna API: {str(e)}")
                return {
                    "status_code": 500,
                    "results": [],
                    "count": 0,
                    "error": str(e)
                }

    async def fetch(self) -> List[Dict[str, Any]]:
        """Fetch raw listings across page 1 for standard connector ingestion interface."""
        res = await self.fetch_jobs(page=1)
        return res.get("results", [])

    def validate_raw(self, raw_record: Dict[str, Any]) -> bool:
        """Validate minimum required fields in raw Adzuna job item."""
        return bool(
            raw_record.get("id") and
            raw_record.get("title") and
            raw_record.get("redirect_url")
        )

    def normalize(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize raw Adzuna job payload to internal model dictionary."""
        company_obj = raw_record.get("company") or {}
        company_name = company_obj.get("display_name") if isinstance(company_obj, dict) else str(company_obj or "Adzuna Partner")
        
        location_obj = raw_record.get("location") or {}
        location_str = location_obj.get("display_name") if isinstance(location_obj, dict) else str(location_obj or "India")

        category_obj = raw_record.get("category") or {}
        category_label = category_obj.get("label") if isinstance(category_obj, dict) else str(category_obj or "Technology")

        ext_id = str(raw_record.get("id"))
        redirect_url = raw_record.get("redirect_url") or f"https://www.adzuna.in/details/{ext_id}"
        
        title = raw_record.get("title", "")
        description = raw_record.get("description", "")
        contract_type = raw_record.get("contract_type")
        contract_time = raw_record.get("contract_time")

        from app.adzuna.classifier import classify_adzuna_opportunity
        opp_type = classify_adzuna_opportunity(
            title=title,
            description=description,
            category=category_label,
            contract_type=contract_type,
            contract_time=contract_time,
            raw_record=raw_record
        )

        return {
            "external_id": ext_id,
            "source_job_id": ext_id,
            "company_name": company_name or "Adzuna Enterprise",
            "company": company_name or "Adzuna Enterprise",
            "company_sector": category_label or "Technology Services",
            "category": category_label or "Technology Services",
            "title": title,
            "description": description,
            "location": location_str or "India",
            "salary_min": float(raw_record.get("salary_min")) if raw_record.get("salary_min") is not None else None,
            "salary_max": float(raw_record.get("salary_max")) if raw_record.get("salary_max") is not None else None,
            "contract_type": contract_type,
            "contract_time": contract_time,
            "created": raw_record.get("created"),
            "created_at": raw_record.get("created"),
            "opportunity_type": opp_type,
            "source": "Adzuna",
            "source_name": "Adzuna Job Board API",
            "source_url": redirect_url,
            "apply_url": redirect_url
        }

    def normalize_to_schema(self, raw_record: Dict[str, Any]):
        """Normalizes raw payload into Pydantic NormalizedAdzunaJob schema."""
        from app.adzuna.schemas import NormalizedAdzunaJob
        d = self.normalize(raw_record)
        return NormalizedAdzunaJob(
            external_id=d["external_id"],
            title=d["title"],
            company=d["company"],
            location=d["location"],
            description=d["description"],
            category=d["category"],
            salary_min=d["salary_min"],
            salary_max=d["salary_max"],
            contract_type=d["contract_type"],
            contract_time=d["contract_time"],
            created=d["created"],
            opportunity_type=d["opportunity_type"],
            source=d["source"],
            source_url=d["source_url"],
            apply_url=d["apply_url"]
        )
