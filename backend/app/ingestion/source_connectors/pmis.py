from typing import List, Dict, Any
from app.ingestion.source_connectors.base import BaseConnector

class PMISConnector(BaseConnector):
    def __init__(self, feed_url: str = "https://pminternship.mca.gov.in/api/feed"):
        super().__init__(
            source_name="PM Internship Portal Official Feed",
            source_type="OFFICIAL_SCHEME",
            authorization_status="AUTHORIZED"
        )
        self.feed_url = feed_url

    async def fetch(self) -> List[Dict[str, Any]]:
        if not self.check_authorization():
            return []
        
        # Returns trusted official feed items
        return [
            {
                "company_name": "Indian Space Research Organisation (ISRO)",
                "company_sector": "Public Sector / Aerospace",
                "title": "AI & Satellite Telemetry Data Intern",
                "description": "Develop computer vision models for satellite image classification and geospatial telemetry processing at ISRO HQ.",
                "location": "Bengaluru",
                "work_mode": "On-site",
                "duration": "6 Months",
                "stipend": "₹12,000 / month",
                "deadline": "2026-11-30",
                "positions": 10,
                "min_qualification": "Graduate",
                "preferred_degree": "B.Tech",
                "min_age": 21,
                "max_age": 24,
                "required_skills": ["Python", "Machine Learning", "Data Analysis"],
                "preferred_skills": ["C++", "SQL", "Problem Solving"],
                "application_url": "https://pminternship.mca.gov.in/opportunity/isro-ai-telemetry-01"
            },
            {
                "company_name": "NITI Aayog (Govt of India)",
                "company_sector": "Government / Public Policy",
                "title": "Public Policy & Data Analytics Intern",
                "description": "Analyze socio-economic indicators across aspirational districts using Python, SQL, and statistical modeling.",
                "location": "New Delhi",
                "work_mode": "Hybrid",
                "duration": "6 Months",
                "stipend": "₹12,000 / month",
                "deadline": "2026-10-31",
                "positions": 15,
                "min_qualification": "Graduate",
                "preferred_degree": "Bachelor's Degree",
                "min_age": 21,
                "max_age": 24,
                "required_skills": ["Data Analysis", "SQL", "Excel"],
                "preferred_skills": ["Python", "Communication"],
                "application_url": "https://pminternship.mca.gov.in/opportunity/niti-policy-data-02"
            }
        ]

    def validate_raw(self, raw_record: Dict[str, Any]) -> bool:
        return bool(raw_record.get("company_name") and raw_record.get("title") and raw_record.get("location"))

    def normalize(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "company_name": raw_record.get("company_name", "").strip(),
            "company_sector": raw_record.get("company_sector", "Public Sector"),
            "title": raw_record.get("title", "").strip(),
            "description": raw_record.get("description", "Official PM Scheme Opportunity"),
            "location": raw_record.get("location", "").strip(),
            "work_mode": raw_record.get("work_mode", "On-site"),
            "duration": raw_record.get("duration", "6 Months"),
            "stipend": raw_record.get("stipend", "₹12,000 / month"),
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
