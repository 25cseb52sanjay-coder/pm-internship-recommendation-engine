from typing import List, Dict, Any, Optional
import logging

from app.ingestion.source_connectors.base import BaseConnector
from app.ncs.schemas import NCSInternshipSchema

logger = logging.getLogger(__name__)

class NCSConnector(BaseConnector):
    """
    Isolated National Career Service (NCS) Data-Source Connector.
    Prepared to receive data from an authorized NCS API, feed, or permitted public source.
    Data fetching is intentionally dormant (Task 1 Architecture Preparation).
    """
    def __init__(self, target_url: str = "https://www.ncs.gov.in/internships-jobs", api_key: Optional[str] = None):
        auth_status = "AUTHORIZED" if api_key else "NOT_CONFIGURED"
        super().__init__(
            source_name="National Career Service (NCS)",
            source_type="GOVERNMENT_PORTAL",
            authorization_status=auth_status
        )
        self.target_url = target_url
        self.api_key = api_key

    async def fetch(self) -> List[Dict[str, Any]]:
        """
        Stub fetch method. External fetching is intentionally disabled in Task 1.
        Returns empty list until authorized API or feed connector is configured.
        """
        logger.info(f"NCSConnector fetch invoked (Status: {self.authorization_status}). External fetching dormant.")
        return []

    def validate_raw(self, raw_record: Dict[str, Any]) -> bool:
        """Validates presence of required fields in raw NCS payload."""
        return bool(raw_record.get("title") and raw_record.get("company") and raw_record.get("apply_url"))

    def normalize(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalizes raw payload into standardized NCSInternshipSchema dictionary format.
        """
        schema_data = {
            "source": "NCS",
            "title": str(raw_record.get("title", "")).strip(),
            "company": str(raw_record.get("company", "")).strip(),
            "location": str(raw_record.get("location", "India")).strip(),
            "skills": raw_record.get("skills", []),
            "eligibility": str(raw_record.get("eligibility", "Graduate")).strip(),
            "stipend": str(raw_record.get("stipend", "As per government norms")).strip(),
            "duration": str(raw_record.get("duration", "3 Months")).strip(),
            "deadline": str(raw_record.get("deadline", "")).strip(),
            "description": str(raw_record.get("description", "")).strip(),
            "apply_url": str(raw_record.get("apply_url", self.target_url)).strip(),
            "status": str(raw_record.get("status", "active")).strip().lower()
        }
        validated = NCSInternshipSchema(**schema_data)
        return validated.model_dump()
