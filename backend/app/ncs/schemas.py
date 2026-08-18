from typing import List, Optional
from pydantic import BaseModel, Field

class NCSInternshipSchema(BaseModel):
    """
    Data model schema for National Career Service (NCS) internship listings.
    Matches the required NCS integration specification.
    """
    source: str = Field(default="NCS", description="Data source identifier")
    title: str = Field(..., description="Internship position title")
    company: str = Field(..., description="Employing company or organization name")
    location: str = Field(default="India", description="Work location or city")
    skills: List[str] = Field(default_factory=list, description="List of required or preferred skills")
    eligibility: str = Field(default="Graduate", description="Eligibility requirements or qualifications")
    stipend: str = Field(default="As per government norms", description="Stipend amount or pay structure")
    duration: str = Field(default="3 Months", description="Internship tenure or duration")
    deadline: str = Field(default="", description="Application deadline date (YYYY-MM-DD)")
    description: str = Field(default="", description="Full description of internship role and responsibilities")
    apply_url: str = Field(..., description="Direct original NCS application link for student redirection")
    status: str = Field(default="active", description="Listing status: active, pending, or expired")

    class Config:
        json_schema_extra = {
            "example": {
                "source": "NCS",
                "title": "Data Analytics & GIS Intern",
                "company": "National Career Service / Ministry of Labour & Employment",
                "location": "New Delhi",
                "skills": ["Python", "SQL", "GIS"],
                "eligibility": "B.Sc / B.Tech Graduate",
                "stipend": "₹12,000 / month",
                "duration": "6 Months",
                "deadline": "2026-12-31",
                "description": "Assist in public employment data modeling and GIS geospatial mapping.",
                "apply_url": "https://www.ncs.gov.in/internships-jobs",
                "status": "active"
            }
        }
