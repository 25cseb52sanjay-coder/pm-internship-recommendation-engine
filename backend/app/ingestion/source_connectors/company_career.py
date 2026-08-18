from typing import List, Dict, Any
from app.ingestion.source_connectors.base import BaseConnector

class CompanyCareerConnector(BaseConnector):
    def __init__(self, company_id: str = "tata_motors", feed_url: str = "https://careers.tatamotors.com/api/pm-internships"):
        super().__init__(
            source_name=f"Authorized Company Career Feed ({company_id})",
            source_type="COMPANY_CAREER",
            authorization_status="AUTHORIZED"
        )
        self.company_id = company_id
        self.feed_url = feed_url

    async def fetch(self) -> List[Dict[str, Any]]:
        if not self.check_authorization():
            return []

        return [
            {
                "company_name": "Tata Motors Limited",
                "company_sector": "Automotive / Manufacturing",
                "title": "EV Electronics & Control Systems Intern",
                "description": "Work on battery management system firmware, CAD layouts, and embedded telemetry controllers.",
                "location": "Pune",
                "work_mode": "On-site",
                "duration": "6 Months",
                "stipend": "₹15,000 / month",
                "deadline": "2026-10-15",
                "positions": 8,
                "min_qualification": "Graduate",
                "preferred_degree": "B.Tech",
                "min_age": 21,
                "max_age": 24,
                "required_skills": ["Embedded Systems", "C++", "AutoCAD"],
                "preferred_skills": ["Python", "Problem Solving"],
                "application_url": "https://careers.tatamotors.com/pm-scheme/ev-electronics-01"
            }
        ]

    def validate_raw(self, raw_record: Dict[str, Any]) -> bool:
        return bool(raw_record.get("company_name") and raw_record.get("title") and raw_record.get("location"))

    def normalize(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "company_name": raw_record.get("company_name", "").strip(),
            "company_sector": raw_record.get("company_sector", "Automotive"),
            "title": raw_record.get("title", "").strip(),
            "description": raw_record.get("description", "Authorized Company Opportunity"),
            "location": raw_record.get("location", "").strip(),
            "work_mode": raw_record.get("work_mode", "On-site"),
            "duration": raw_record.get("duration", "6 Months"),
            "stipend": raw_record.get("stipend", "₹15,000 / month"),
            "deadline": raw_record.get("deadline", "2026-12-31"),
            "positions": raw_record.get("positions", 5),
            "min_qualification": raw_record.get("min_qualification", "Graduate"),
            "preferred_degree": raw_record.get("preferred_degree", "B.Tech"),
            "min_age": raw_record.get("min_age", 21),
            "max_age": raw_record.get("max_age", 24),
            "required_skills": raw_record.get("required_skills", []),
            "preferred_skills": raw_record.get("preferred_skills", []),
            "application_url": raw_record.get("application_url", self.feed_url)
        }
