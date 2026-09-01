import logging
from typing import List, Dict, Any, Optional
from app.lever.connector import LeverConnector, DEFAULT_LEVER_SITES
from app.lever.schemas import LeverPostingSchema, NormalizedLeverJob
from app.lever.classifier import classify_lever_opportunity
from app.core.config import settings

logger = logging.getLogger(__name__)

def get_configured_lever_sites() -> List[str]:
    sites_setting = getattr(settings, "LEVER_POSTING_SITES", "palantir,spotify")
    if isinstance(sites_setting, str):
        parsed = [s.strip().lower() for s in sites_setting.split(",") if s.strip()]
        return parsed if parsed else DEFAULT_LEVER_SITES
    elif isinstance(sites_setting, list):
        return [str(s).strip().lower() for s in sites_setting if str(s).strip()]
    return DEFAULT_LEVER_SITES

class LeverService:
    """
    Lever Service wrapping official Lever Postings API operations.
    Retrieves real live published job data from Lever company site slugs.
    """

    def __init__(self, connector: Optional[LeverConnector] = None):
        self.connector = connector or LeverConnector(sites=get_configured_lever_sites())

    async def verify_connection(self, site_name: str = "palantir") -> Dict[str, Any]:
        """
        Verifies live connection to official Lever Postings API endpoint.
        URL: https://api.lever.co/v0/postings/{site_name}?mode=json
        """
        logger.info(f"Verifying live Lever API connection for site: {site_name}")
        postings_raw = await self.connector.fetch_site_postings(site_name)

        valid_count = 0
        parsed_postings: List[LeverPostingSchema] = []
        for raw in postings_raw:
            if self.connector.validate_raw(raw):
                valid_count += 1
                try:
                    parsed = LeverPostingSchema(**raw)
                    parsed_postings.append(parsed)
                except Exception as e:
                    logger.debug(f"Pydantic parse warning for Lever posting {raw.get('id')}: {e}")

        return {
            "status": "CONNECTED" if valid_count > 0 else "NO_POSTINGS_OR_ERROR",
            "site_name": site_name,
            "api_endpoint": f"https://api.lever.co/v0/postings/{site_name}?mode=json",
            "total_postings_fetched": len(postings_raw),
            "valid_schema_postings": valid_count,
            "sample_postings": [
                {
                    "id": p.id,
                    "title": p.text,
                    "location": p.categories.location if p.categories else "N/A",
                    "apply_url": p.applyUrl or p.hostedUrl
                }
                for p in parsed_postings[:3]
            ]
        }

    async def fetch_and_normalize_jobs(self, sites: Optional[List[str]] = None) -> List[NormalizedLeverJob]:
        """
        Fetches real published jobs from official Lever API and normalizes them
        into NormalizedLeverJob schema.
        """
        active_sites = sites or get_configured_lever_sites()
        conn = LeverConnector(sites=active_sites)
        raw_postings = await conn.fetch()

        normalized_list: List[NormalizedLeverJob] = []
        seen_ids = set()

        for raw in raw_postings:
            posting_id = raw.get("id")
            title = raw.get("text")
            apply_url = raw.get("applyUrl") or raw.get("hostedUrl")

            if not posting_id or not str(posting_id).strip():
                logger.warning("Skipping Lever posting record: Missing valid ID.")
                continue

            if not title or not str(title).strip():
                logger.warning(f"Skipping Lever posting record ID {posting_id}: Missing valid title.")
                continue

            if not apply_url or not (str(apply_url).startswith("http://") or str(apply_url).startswith("https://")):
                logger.warning(f"Skipping Lever posting record ID {posting_id}: Invalid apply_url '{apply_url}'.")
                continue

            ext_id_str = str(posting_id)
            if ext_id_str in seen_ids:
                logger.debug(f"Skipping in-batch duplicate Lever posting ID: {ext_id_str}")
                continue
            seen_ids.add(ext_id_str)

            site_name = raw.get("_site_name", "Lever")
            company_name = site_name.capitalize()

            categories = raw.get("categories") or {}
            location_str = categories.get("location") if isinstance(categories, dict) else None
            commitment_str = categories.get("commitment") if isinstance(categories, dict) else None
            team_str = categories.get("team") if isinstance(categories, dict) else None

            description_raw = raw.get("descriptionPlain") or raw.get("description")
            description_str = None
            if description_raw and isinstance(description_raw, str) and description_raw.strip():
                description_str = description_raw.strip()

            hosted_url = raw.get("hostedUrl") or apply_url

            opp_type = classify_lever_opportunity(
                title=str(title).strip(),
                description=description_str,
                categories=categories,
                raw_record=raw
            )

            norm_item = NormalizedLeverJob(
                external_id=ext_id_str,
                title=str(title).strip(),
                company=company_name,
                location=location_str,
                description=description_str,
                source="Lever",
                source_url=str(hosted_url).strip(),
                apply_url=str(apply_url).strip(),
                updated_at=raw.get("createdAt"),
                status="active",
                opportunity_type=opp_type,
                commitment=commitment_str,
                team=team_str
            )
            normalized_list.append(norm_item)

        logger.info(f"LeverService: Successfully fetched & normalized {len(normalized_list)} real jobs across {len(active_sites)} sites.")
        return normalized_list
