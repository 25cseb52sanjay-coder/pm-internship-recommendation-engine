from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class NormalizedAdzunaJob(BaseModel):
    """
    Normalized data model for real Adzuna job & internship requisitions.
    """
    external_id: str = Field(..., description="Original unique Adzuna job requisition ID")
    title: str = Field(..., description="Requisition job or internship title")
    company: str = Field(..., description="Employer / Company display name")
    location: str = Field(..., description="Geographic location or city")
    description: str = Field(..., description="Requisition content or description text")
    category: str = Field(..., description="Adzuna job category label")
    salary_min: Optional[float] = Field(None, description="Minimum salary if specified")
    salary_max: Optional[float] = Field(None, description="Maximum salary if specified")
    contract_type: Optional[str] = Field(None, description="Contract type e.g. permanent, contract")
    contract_time: Optional[str] = Field(None, description="Contract time e.g. full_time, part_time")
    created: Optional[str] = Field(None, description="ISO timestamp of posting creation")
    opportunity_type: str = Field("UNKNOWN", description="Classification value: JOB, INTERNSHIP, or UNKNOWN")
    source: str = Field("Adzuna", description="Data source identifier")
    source_url: str = Field(..., description="Original Adzuna canonical listing URL")
    apply_url: str = Field(..., description="Original Adzuna direct application redirect URL")

class AdzunaFetchResponse(BaseModel):
    """
    Response schema for multi-query normalized Adzuna job fetching.
    """
    status_code: int
    total_fetched: int
    total_normalized: int
    queries_executed: List[str]
    normalized_jobs: List[NormalizedAdzunaJob]
