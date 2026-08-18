import httpx
import logging
from typing import List, Dict, Any, Optional
from app.ingestion.source_connectors.base import BaseConnector

logger = logging.getLogger(__name__)

BASE_GREENHOUSE_BOARDS_URL = "https://boards-api.greenhouse.io/v1/boards"

# Popular public tech company board tokens using Greenhouse Job Board API
DEFAULT_GREENHOUSE_BOARDS = [
    "stripe",
    "cloudflare",
    "gitlab",
    "airbnb"
]

class GreenhouseConnector(BaseConnector):
    """
    Official Connector for the public Greenhouse Job Board API v1.
    Endpoint: GET https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true
    """

    def __init__(self, boards: Optional[List[str]] = None):
        super().__init__(
            source_name="Greenhouse Official Job Board API",
            source_type="GREENHOUSE_API",
            authorization_status="AUTHORIZED"
        )
        self.boards = boards or DEFAULT_GREENHOUSE_BOARDS
        self.timeout = 15.0

    async def fetch_board_jobs(self, board_token: str) -> List[Dict[str, Any]]:
        """
        Fetch real published job listings from a specific Greenhouse board token.
        """
        url = f"{BASE_GREENHOUSE_BOARDS_URL}/{board_token}/jobs?content=true"
        logger.info(f"Connecting to official Greenhouse Job Board API for board '{board_token}': {url}")
        
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            response = await client.get(url)
            if response.status_code == 200:
                payload = response.json()
                jobs = payload.get("jobs", [])
                logger.info(f"Successfully retrieved {len(jobs)} real published jobs from Greenhouse board '{board_token}'.")
                # Inject board metadata into raw payload for downstream processing
                for j in jobs:
                    j["_board_token"] = board_token
                return jobs
            else:
                logger.error(f"Failed to fetch jobs from Greenhouse board '{board_token}': HTTP {response.status_code}")
                return []

    async def fetch_job_detail(self, board_token: str, job_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch detailed content for a specific job from Greenhouse API.
        Endpoint: GET https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs/{job_id}
        """
        url = f"{BASE_GREENHOUSE_BOARDS_URL}/{board_token}/jobs/{job_id}"
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            response = await client.get(url)
            if response.status_code == 200:
                return response.json()
            return None

    async def fetch(self) -> List[Dict[str, Any]]:
        """
        Fetch real published jobs across all configured Greenhouse company board tokens.
        """
        if not self.check_authorization():
            return []

        all_jobs: List[Dict[str, Any]] = []
        for board_token in self.boards:
            try:
                jobs = await self.fetch_board_jobs(board_token)
                all_jobs.extend(jobs)
            except Exception as e:
                logger.error(f"Error connecting to Greenhouse API for board '{board_token}': {str(e)}")
        
        logger.info(f"GreenhouseConnector: Total real jobs retrieved across {len(self.boards)} boards = {len(all_jobs)}")
        return all_jobs

    def validate_raw(self, raw_record: Dict[str, Any]) -> bool:
        """Validate presence of required fields in raw Greenhouse job payload."""
        return bool(
            raw_record.get("id") and
            raw_record.get("title") and
            raw_record.get("absolute_url")
        )

    def normalize(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize raw Greenhouse payload to standard model format."""
        company = raw_record.get("_board_token", "Greenhouse Partner").capitalize()
        title = raw_record.get("title", "")
        location_obj = raw_record.get("location") or {}
        location_str = location_obj.get("name") if isinstance(location_obj, dict) else str(location_obj)
        
        return {
            "source_job_id": str(raw_record.get("id")),
            "board_token": raw_record.get("_board_token"),
            "company_name": company,
            "title": title,
            "location": location_str or "Remote / Multiple",
            "apply_url": raw_record.get("absolute_url"),
            "updated_at": raw_record.get("updated_at"),
            "content": raw_record.get("content", "")
        }
