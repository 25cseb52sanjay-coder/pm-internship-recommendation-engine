from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class InternshipSkillSchema(BaseModel):
    id: Optional[int] = None
    name: str
    is_required: bool = True

    class Config:
        from_attributes = True

class InternshipCreate(BaseModel):
    company_name: str
    company_sector: str
    title: str
    description: str
    location: str
    work_mode: str = "On-site"
    duration: str = "6 Months"
    stipend: str = "₹12,000 / month"
    deadline: str
    positions: int = 5
    min_qualification: str = "Graduate"
    preferred_degree: Optional[str] = None
    min_age: int = 21
    max_age: int = 24
    required_skills: List[str] = []
    preferred_skills: List[str] = []

class InternshipOut(BaseModel):
    id: int
    company_name: str
    company_sector: str
    title: str
    description: str
    location: str
    work_mode: str
    duration: str
    stipend: str
    deadline: str
    positions: int
    min_qualification: str
    preferred_degree: Optional[str] = None
    min_age: int
    max_age: int
    skills: List[InternshipSkillSchema] = []
    source: Optional[str] = "PMIS"
    source_name: Optional[str] = "PM Scheme Official"
    opportunity_type: Optional[str] = "INTERNSHIP"
    apply_url: Optional[str] = None
    application_url: Optional[str] = None
    external_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
