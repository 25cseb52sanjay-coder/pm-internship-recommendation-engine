from pydantic import BaseModel
from typing import List, Optional, Any

class LeverCategoriesSchema(BaseModel):
    commitment: Optional[str] = None
    location: Optional[str] = None
    team: Optional[str] = None
    department: Optional[str] = None
    allLocations: Optional[List[str]] = None

class LeverPostingSchema(BaseModel):
    id: str
    text: str
    hostedUrl: Optional[str] = None
    applyUrl: Optional[str] = None
    categories: Optional[LeverCategoriesSchema] = None
    createdAt: Optional[Any] = None
    descriptionPlain: Optional[str] = None
    description: Optional[str] = None

class NormalizedLeverJob(BaseModel):
    external_id: str
    title: str
    company: str
    location: Optional[str] = None
    description: Optional[str] = None
    source: str = "Lever"
    source_url: str
    apply_url: str
    updated_at: Optional[Any] = None
    status: str = "active"
    opportunity_type: str = "UNKNOWN"
    commitment: Optional[str] = None
    team: Optional[str] = None
