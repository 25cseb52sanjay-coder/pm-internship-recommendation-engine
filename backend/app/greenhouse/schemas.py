from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime

class GreenhouseLocationSchema(BaseModel):
    name: Optional[str] = None

class GreenhouseDepartmentSchema(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None

class GreenhouseOfficeSchema(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    location: Optional[str] = None

class GreenhouseJobSchema(BaseModel):
    id: int
    internal_job_id: Optional[int] = None
    title: str
    location: Optional[GreenhouseLocationSchema] = None
    absolute_url: str
    updated_at: Optional[str] = None
    requisition_id: Optional[str] = None
    content: Optional[str] = None
    departments: List[GreenhouseDepartmentSchema] = []
    offices: List[GreenhouseOfficeSchema] = []
    metadata: Optional[List[Any]] = None

class GreenhouseBoardJobsResponse(BaseModel):
    jobs: List[GreenhouseJobSchema] = []

class NormalizedGreenhouseJob(BaseModel):
    external_id: str
    title: str
    company: str
    location: Optional[str] = None
    description: Optional[str] = None
    source: str = "Greenhouse"
    source_url: str
    apply_url: str
    updated_at: Optional[str] = None
    status: str = "active"
    opportunity_type: str = "UNKNOWN"
