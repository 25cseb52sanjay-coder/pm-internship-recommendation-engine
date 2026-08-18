from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class SourceRegistryCreate(BaseModel):
    source_name: str
    source_url: str
    source_type: str = "OFFICIAL_SCHEME" # OFFICIAL_GOVERNMENT, OFFICIAL_SCHEME, COMPANY_CAREER, AUTHORIZED_API, AUTHORIZED_FEED, LICENSED_PROVIDER
    api_endpoint: Optional[str] = None
    authentication_method: str = "NONE"
    authorization_status: str = "AUTHORIZED" # AUTHORIZED, NOT_CONFIGURED, REVOKED, RATE_LIMITED, UNAVAILABLE
    enabled: bool = True
    polling_frequency_seconds: int = 900
    rate_limit: int = 60
    priority: int = 1
    source_confidence: float = 1.0

class SourceRegistryUpdate(BaseModel):
    source_name: Optional[str] = None
    source_url: Optional[str] = None
    api_endpoint: Optional[str] = None
    authorization_status: Optional[str] = None
    enabled: Optional[bool] = None
    polling_frequency_seconds: Optional[int] = None
    rate_limit: Optional[int] = None
    priority: Optional[int] = None
    health_status: Optional[str] = None

class SourceRegistryOut(BaseModel):
    id: int
    source_name: str
    source_url: str
    source_type: str
    api_endpoint: Optional[str] = None
    authentication_method: str
    authorization_status: str
    enabled: bool
    polling_frequency_seconds: int
    rate_limit: int
    priority: int
    last_success_at: Optional[datetime] = None
    last_failure_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    health_status: str
    source_confidence: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class IngestionRunOut(BaseModel):
    run_id: int
    source_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str
    records_discovered: int
    records_created: int
    records_updated: int
    records_unchanged: int
    records_rejected: int
    duplicates_detected: int
    expired_records: int
    error_count: int

    class Config:
        from_attributes = True

class IngestionErrorOut(BaseModel):
    id: int
    run_id: Optional[int] = None
    source_id: Optional[int] = None
    error_type: str
    error_message: str
    payload_snapshot: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class IngestionStatusSummary(BaseModel):
    total_sources: int
    healthy_sources: int
    failed_sources: int
    last_successful_run: Optional[datetime] = None
    next_scheduled_run: Optional[datetime] = None
    new_internships: int
    updated_internships: int
    duplicates: int
    rejected_listings: int
    expired_listings: int
    failed_jobs: int
    source_health_breakdown: Dict[str, int]
