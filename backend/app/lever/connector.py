import httpx
import logging
from typing import List, Dict, Any, Optional
from app.ingestion.source_connectors.base import BaseConnector

logger = logging.getLogger(__name__)

BASE_LEVER_POSTINGS_URL = "https://api.lever.co/v0/postings"

# Default public tech company board site slugs on Lever
DEFAULT_LEVER_SITES = [
    "palantir",
    "spotify"
]

class LeverConnector(BaseConnector):
    """
    Official Connector for the public Lever Postings API v0.
    Endpoint: GET https://api.lever.co/v0/postings/{site_name}?mode=json
    """

    def __init__(self, sites: Optional[List[str]] = None):
        super().__init__(
            source_name="Lever Official Public Postings API",
            source_type="LEVER_API",
            authorization_status="AUTHORIZED"
        )
        self.sites = sites or DEFAULT_LEVER_SITES
        self.timeout = 15.0

    async def fetch_site_postings(self, site_name: str) -> List[Dict[str, Any]]:
        """
        Fetch real published job postings from a specific Lever company site slug.
        """
        url = f"{BASE_LEVER_POSTINGS_URL}/{site_name}?mode=json"
        logger.info(f"Connecting to official Lever Postings API for site '{site_name}': {url}")

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            response = await client.get(url)
            if response.status_code == 200:
                postings = response.json()
                if not isinstance(postings, list):
                    logger.warning(f"Lever Postings API for '{site_name}' returned non-list payload.")
                    return []
                logger.info(f"Successfully retrieved {len(postings)} real published postings from Lever site '{site_name}'.")
                for p in postings:
                    if isinstance(p, dict):
                        p["_site_name"] = site_name
                return postings
            else:
                logger.error(f"Failed to fetch postings from Lever site '{site_name}': HTTP {response.status_code}")
                return []

    async def fetch(self) -> List[Dict[str, Any]]:
        """
        Fetch real published postings across all configured Lever company site slugs.
        """
        if not self.check_authorization():
            return []

        all_postings: List[Dict[str, Any]] = []
        for site_name in self.sites:
            try:
                postings = await self.fetch_site_postings(site_name)
                all_postings.extend(postings)
            except Exception as e:
                logger.error(f"Error connecting to Lever API for site '{site_name}': {str(e)}")

        logger.info(f"LeverConnector: Total real postings retrieved across {len(self.sites)} sites = {len(all_postings)}")
        return all_postings

    def validate_raw(self, raw_record: Dict[str, Any]) -> bool:
        """Validate presence of required fields in raw Lever posting payload."""
        return bool(
            raw_record.get("id") and
            raw_record.get("text") and
            (raw_record.get("hostedUrl") or raw_record.get("applyUrl"))
        )

    def normalize(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize raw Lever payload to standard model format."""
        site = raw_record.get("_site_name", "Lever Partner").capitalize()
        title = raw_record.get("text", "")
        categories = raw_record.get("categories") or {}
        location_str = categories.get("location") if isinstance(categories, dict) else None
        apply_url = raw_record.get("applyUrl") or raw_record.get("hostedUrl")

        return {
            "source_job_id": str(raw_record.get("id")),
            "site_name": raw_record.get("_site_name"),
            "company_name": site,
            "title": title,
            "location": location_str or "Remote / Multiple",
            "apply_url": apply_url,
            "source_url": raw_record.get("hostedUrl") or apply_url,
            "updated_at": raw_record.get("createdAt"),
            "content": raw_record.get("descriptionPlain") or raw_record.get("description") or ""
        }
