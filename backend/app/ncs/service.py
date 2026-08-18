from typing import Dict, Any
from app.ncs.schemas import NCSInternshipSchema
from app.db.models import Internship

class NCSService:
    """
    Service adapter for mapping National Career Service (NCS) schemas
    to the main database Internship model without modifying existing database tables.
    """
    @staticmethod
    def map_ncs_schema_to_internship_model(ncs_item: NCSInternshipSchema) -> Dict[str, Any]:
        """
        Maps a validated NCSInternshipSchema instance into the standard
        internships database table column layout.
        """
        return {
            "title": ncs_item.title,
            "company_name": ncs_item.company,
            "company_sector": "Government / Public Sector (NCS)",
            "description": ncs_item.description or f"NCS Internship Opportunity at {ncs_item.company}",
            "location": ncs_item.location,
            "work_mode": "On-site",
            "duration": ncs_item.duration,
            "stipend": ncs_item.stipend,
            "deadline": ncs_item.deadline or "2026-12-31",
            "min_qualification": ncs_item.eligibility,
            "required_skills": ncs_item.skills,
            "source": "NCS",
            "apply_url": ncs_item.apply_url,
            "application_url": ncs_item.apply_url,
            "source_name": "National Career Service (NCS)",
            "source_url": "https://www.ncs.gov.in/internships-jobs",
            "original_listing_url": ncs_item.apply_url,
            "verification_status": "VERIFIED" if ncs_item.status == "active" else "PENDING_VERIFICATION"
        }
