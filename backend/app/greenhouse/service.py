import logging
from typing import List, Dict, Any, Optional
from app.greenhouse.connector import GreenhouseConnector, DEFAULT_GREENHOUSE_BOARDS
from app.greenhouse.schemas import GreenhouseJobSchema, NormalizedGreenhouseJob
from app.greenhouse.classifier import classify_greenhouse_opportunity

logger = logging.getLogger(__name__)

class GreenhouseService:
    """
    Greenhouse Service wrapping official Greenhouse Job Board API operations.
    Retrieves real live published job data from Greenhouse partner boards.
    """

    def __init__(self, connector: Optional[GreenhouseConnector] = None):
        self.connector = connector or GreenhouseConnector()

    async def verify_connection(self, board_token: str = "stripe") -> Dict[str, Any]:
        """
        Verifies live connection to official Greenhouse Job Board API endpoint.
        URL: https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true
        """
        logger.info(f"Verifying live Greenhouse API connection for board: {board_token}")
        jobs_raw = await self.connector.fetch_board_jobs(board_token)
        
        valid_count = 0
        parsed_jobs: List[GreenhouseJobSchema] = []
        for raw in jobs_raw:
            if self.connector.validate_raw(raw):
                valid_count += 1
                try:
                    parsed = GreenhouseJobSchema(**raw)
                    parsed_jobs.append(parsed)
                except Exception as e:
                    logger.debug(f"Pydantic parse warning for job {raw.get('id')}: {e}")

        return {
            "status": "CONNECTED" if valid_count > 0 else "NO_JOBS_OR_ERROR",
            "board_token": board_token,
            "api_endpoint": f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true",
            "total_jobs_fetched": len(jobs_raw),
            "valid_schema_jobs": valid_count,
            "sample_jobs": [
                {
                    "id": j.id,
                    "title": j.title,
                    "location": j.location.name if j.location else "N/A",
                    "apply_url": j.absolute_url
                }
                for j in parsed_jobs[:3]
            ]
        }

    async def fetch_all_real_published_jobs(self, board_tokens: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Fetches all real published job listings across configured Greenhouse company boards.
        """
        conn = GreenhouseConnector(boards=board_tokens) if board_tokens else self.connector
        raw_jobs = await conn.fetch()
        
        normalized_records: List[Dict[str, Any]] = []
        for raw in raw_jobs:
            if conn.validate_raw(raw):
                normalized = conn.normalize(raw)
                normalized_records.append(normalized)

        logger.info(f"GreenhouseService: Prepared {len(normalized_records)} normalized real job listings.")
        return normalized_records

    async def fetch_and_normalize_jobs(self, board_tokens: Optional[List[str]] = None) -> List[NormalizedGreenhouseJob]:
        """
        Fetches real published jobs from official Greenhouse API and normalizes them
        into the standardized NormalizedGreenhouseJob schema.
        Ensures data quality, URL validation, and deduplication.
        """
        conn = GreenhouseConnector(boards=board_tokens) if board_tokens else self.connector
        raw_jobs = await conn.fetch()

        normalized_list: List[NormalizedGreenhouseJob] = []
        seen_ids = set()

        for raw in raw_jobs:
            # 1. Mandatory Data Quality Checks
            job_id = raw.get("id")
            title = raw.get("title")
            apply_url = raw.get("absolute_url")

            if not job_id or not str(job_id).strip():
                logger.warning("Skipping Greenhouse job record: Missing valid job ID.")
                continue

            if not title or not str(title).strip():
                logger.warning(f"Skipping Greenhouse job record ID {job_id}: Missing valid title.")
                continue

            if not apply_url or not (str(apply_url).startswith("http://") or str(apply_url).startswith("https://")):
                logger.warning(f"Skipping Greenhouse job record ID {job_id}: Invalid apply_url format '{apply_url}'.")
                continue

            # 2. In-batch Deduplication
            ext_id_str = str(job_id)
            if ext_id_str in seen_ids:
                logger.debug(f"Skipping in-batch duplicate Greenhouse job ID: {ext_id_str}")
                continue
            seen_ids.add(ext_id_str)

            # 3. Clean optional fields without inventing fake data
            board_token = raw.get("_board_token", "Greenhouse")
            company_name = board_token.capitalize()

            loc_obj = raw.get("location")
            location_str = None
            if isinstance(loc_obj, dict) and loc_obj.get("name"):
                location_str = str(loc_obj["name"]).strip()

            content_raw = raw.get("content")
            description_str = None
            if content_raw and isinstance(content_raw, str) and content_raw.strip():
                description_str = content_raw.strip()

            updated_str = raw.get("updated_at")

            # 4. Classify opportunity type (JOB, INTERNSHIP, UNKNOWN)
            depts = raw.get("departments")
            opp_type = classify_greenhouse_opportunity(
                title=str(title).strip(),
                description=description_str,
                departments=depts,
                raw_record=raw
            )

            # 5. Construct Normalized Model
            norm_item = NormalizedGreenhouseJob(
                external_id=ext_id_str,
                title=str(title).strip(),
                company=company_name,
                location=location_str, # None if missing
                description=description_str, # None if missing
                source="Greenhouse",
                source_url=str(apply_url).strip(),
                apply_url=str(apply_url).strip(),
                updated_at=updated_str,
                status="active",
                opportunity_type=opp_type
            )
            normalized_list.append(norm_item)

        logger.info(f"GreenhouseService: Successfully fetched & normalized {len(normalized_list)} real jobs.")
        return normalized_list
