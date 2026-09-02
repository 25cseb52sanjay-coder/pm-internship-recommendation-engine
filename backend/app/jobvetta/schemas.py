from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class NormalizedJobvettaJob(BaseModel):
    """
    Normalized Jobvetta opportunity object matching project unified job schema.
    """
    external_id: str = Field(..., description="Unique Jobvetta job identifier")
    title: str = Field(..., description="Job or internship title")
    company: str = Field(..., description="Company / Employer name")
    description: Optional[str] = Field(None, description="Full job description")
    location: Optional[str] = Field("India", description="City / State / Region")
    category: Optional[str] = Field("Technology Services", description="Industry / Sector category")
    opportunity_type: str = Field("INTERNSHIP", description="INTERNSHIP, JOB, or UNKNOWN")
    employment_type: Optional[str] = Field(None, description="Full-time, Part-time, Contract, Internship")
    work_mode: str = Field("On-site", description="Remote, Hybrid, On-site")
    salary_min: Optional[float] = Field(None, description="Minimum salary / stipend")
    salary_max: Optional[float] = Field(None, description="Maximum salary / stipend")
    currency: Optional[str] = Field("INR", description="Currency code")
    stipend_str: Optional[str] = Field(None, description="Formatted stipend string")
    skills: List[str] = Field(default_factory=list, description="Extracted skills")
    min_qualification: str = Field("Graduate", description="Minimum education qualification")
    preferred_degree: Optional[str] = Field(None, description="Preferred degree")
    source: str = Field("Jobvetta", description="Source identifier")
    source_url: Optional[str] = Field(None, description="Jobvetta job detail page URL")
    apply_url: Optional[str] = Field(None, description="Original external application URL")
    posted_date: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Job posting timestamp")
    deadline: Optional[str] = Field("2026-12-31", description="Application deadline")
    positions: int = Field(1, description="Open positions count")
    raw_metadata: Optional[Dict[str, Any]] = Field(None, description="Raw API response object")
