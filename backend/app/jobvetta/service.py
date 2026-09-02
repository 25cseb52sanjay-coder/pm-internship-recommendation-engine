import logging
from typing import List, Dict, Any, Optional
from app.jobvetta.connector import JobvettaConnector
from app.jobvetta.schemas import NormalizedJobvettaJob

logger = logging.getLogger(__name__)

DEFAULT_JOBVETTA_SEARCH_QUERIES = [
    "software engineering internship",
    "full stack developer",
    "web developer",
    "data analyst",
    "product management intern",
    "python developer",
    "react developer",
    "cybersecurity intern"
]

class JobvettaService:
    """
    High-level orchestration service for querying Jobvetta API and fetching normalized opportunities.
    """

    def __init__(self, connector: Optional[JobvettaConnector] = None):
        self.connector = connector or JobvettaConnector()

    async def fetch_and_normalize_jobs(
        self,
        queries: Optional[List[str]] = None,
        location: str = "India",
        limit_per_query: int = 15
    ) -> List[NormalizedJobvettaJob]:
        """
        Fetches live opportunities from Jobvetta REST API across search queries and returns normalized objects.
        """
        search_queries = queries or DEFAULT_JOBVETTA_SEARCH_QUERIES
        normalized_results: List[NormalizedJobvettaJob] = []
        seen_external_ids = set()

        if not self.connector.check_authorization():
            logger.info("JobvettaService: JOBVETTA_API_KEY is not configured (Stub / Unauthorized Mode). Returning 0 live items.")
            return []

        logger.info(f"JobvettaService: Executing search across {len(search_queries)} queries.")

        for q in search_queries:
            try:
                res = await self.connector.fetch_jobs(q=q, location=location, limit=limit_per_query)
                status_code = res.get("status_code", 500)

                if status_code == 429:
                    logger.warning(f"JobvettaService: HTTP 429 Rate Limit encountered during query '{q}'. Stopping batch.")
                    break
                elif status_code != 200:
                    logger.warning(f"JobvettaService: Query '{q}' returned status {status_code}. Skipping.")
                    continue

                raw_jobs = res.get("results", [])
                for raw in raw_jobs:
                    if self.connector.validate_raw(raw):
                        norm_job = self.connector.normalize_to_schema(raw)
                        if norm_job.external_id and norm_job.external_id not in seen_external_ids:
                            seen_external_ids.add(norm_job.external_id)
                            normalized_results.append(norm_job)

            except Exception as e:
                logger.error(f"JobvettaService error processing query '{q}': {str(e)}")

        logger.info(f"JobvettaService: Total unique normalized jobs fetched: {len(normalized_results)}")
        return normalized_results
