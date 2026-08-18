import logging
from typing import Dict, Any, List, Optional
from app.adzuna.connector import AdzunaConnector
from app.adzuna.config import AdzunaConfig

logger = logging.getLogger(__name__)

DEFAULT_ADZUNA_SEARCH_QUERIES = [
    "intern",
    "internship",
    "software intern",
    "engineering intern",
    "data science intern",
    "AI ML intern",
    "Java intern",
    "Python intern"
]

class AdzunaService:
    """
    High-level service manager for Adzuna REST API authentication & live listing verification.
    """

    def __init__(self, connector: Optional[AdzunaConnector] = None):
        self.connector = connector or AdzunaConnector()

    async def verify_live_connection(
        self,
        country: str = "in",
        query: str = "software internship",
        page: int = 1,
        results_per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Executes an authentication & live connection test against official Adzuna REST API.
        Endpoint: GET https://api.adzuna.com/v1/api/jobs/{country}/search/{page}
        """
        if not AdzunaConfig.is_configured() and not (self.connector.app_id and self.connector.app_key):
            logger.warning("Adzuna API credentials not configured in environment (ADZUNA_APP_ID/ADZUNA_APP_KEY missing).")
            return {
                "status_code": 401,
                "connection_status": "NOT_CONFIGURED",
                "api_endpoint": f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}",
                "total_listings_found": 0,
                "retrieved_listings_count": 0,
                "sample_listings": [],
                "error": "Adzuna API credentials missing in environment settings."
            }

        connector = AdzunaConnector(
            country=country,
            query=query,
            results_per_page=results_per_page,
            app_id=self.connector.app_id,
            app_key=self.connector.app_key
        )

        res = await connector.fetch_jobs(page=page, query=query)
        status_code = res.get("status_code", 500)
        results = res.get("results", [])
        total_count = res.get("count", len(results))

        if status_code == 200:
            conn_status = "CONNECTED"
            error_msg = None
        elif status_code in (401, 403):
            conn_status = "AUTHENTICATION_FAILED"
            error_msg = "Adzuna API rejected APP_ID or APP_KEY credentials."
        else:
            conn_status = "FAILED"
            error_msg = res.get("error", f"HTTP {status_code}")

        # Format sample listings safely without credential leaks
        sample_listings = []
        for raw in results[:5]:
            if connector.validate_raw(raw):
                norm = connector.normalize(raw)
                sample_listings.append({
                    "id": norm["source_job_id"],
                    "title": norm["title"],
                    "company": norm["company_name"],
                    "location": norm["location"],
                    "apply_url": norm["apply_url"]
                })

        return {
            "status_code": status_code,
            "connection_status": conn_status,
            "api_endpoint": f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}",
            "country": country,
            "search_query": query,
            "total_listings_found": total_count,
            "retrieved_listings_count": len(results),
            "sample_listings": sample_listings,
            "error": error_msg
        }

    async def fetch_and_normalize_jobs(
        self,
        queries: Optional[List[str]] = None,
        country: str = "in",
        pages_per_query: int = 1,
        results_per_page: int = 20
    ) -> List[Any]:
        """
        Fetches real published jobs across configured search queries from Adzuna API
        and normalizes them into NormalizedAdzunaJob instances.
        Deduplicates by external_id across queries.
        """
        from app.adzuna.schemas import NormalizedAdzunaJob

        active_queries = queries or DEFAULT_ADZUNA_SEARCH_QUERIES
        connector = AdzunaConnector(
            country=country,
            results_per_page=results_per_page,
            app_id=self.connector.app_id,
            app_key=self.connector.app_key
        )

        seen_ids = set()
        normalized_list: List[NormalizedAdzunaJob] = []

        for q in active_queries:
            for p in range(1, pages_per_query + 1):
                res = await connector.fetch_jobs(page=p, query=q)
                results = res.get("results", [])
                for raw in results:
                    if connector.validate_raw(raw):
                        norm_schema = connector.normalize_to_schema(raw)
                        if norm_schema.external_id not in seen_ids:
                            seen_ids.add(norm_schema.external_id)
                            normalized_list.append(norm_schema)

        logger.info(f"AdzunaService: Fetched & normalized {len(normalized_list)} unique real Adzuna requisitions across {len(active_queries)} queries.")
        return normalized_list
