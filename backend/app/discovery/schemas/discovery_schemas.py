from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class DiscoverySearchQueryCreate(BaseModel):
    query_text: str
    category: Optional[str] = "General"
    city: Optional[str] = "Bengaluru"
    branch: Optional[str] = "B.Tech"
    skill_tag: Optional[str] = "Python"
    enabled: bool = True

class DiscoverySearchQueryUpdate(BaseModel):
    query_text: Optional[str] = None
    category: Optional[str] = None
    city: Optional[str] = None
    branch: Optional[str] = None
    skill_tag: Optional[str] = None
    enabled: Optional[bool] = None

class DiscoverySearchQueryOut(BaseModel):
    id: int
    query_text: str
    category: Optional[str] = None
    city: Optional[str] = None
    branch: Optional[str] = None
    skill_tag: Optional[str] = None
    generated_at: datetime
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    result_count_last_run: int
    enabled: bool

    class Config:
        from_attributes = True

class DiscoveryCandidateOut(BaseModel):
    id: int
    search_query_id: Optional[int] = None
    result_url: str
    discovered_at: datetime
    fetch_status: str
    extraction_status: str
    verification_status: str
    quality_score: float
    employer_domain: Optional[str] = None
    official_domain_match: bool
    application_url_valid: bool
    deadline_extracted: Optional[str] = None
    content_recency_check_passed: bool
    fingerprint_sha256: Optional[str] = None
    linked_internship_id: Optional[int] = None
    rejection_reason: Optional[str] = None

    class Config:
        from_attributes = True

class DiscoveryCandidateUpdate(BaseModel):
    verification_status: str # VERIFIED, REJECTED, PENDING
    rejection_reason: Optional[str] = None

class DiscoveryRunOut(BaseModel):
    run_id: int
    search_query_id: Optional[int] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str
    urls_discovered: int
    urls_fetched: int
    urls_verified: int
    urls_rejected: int
    duplicates_detected: int
    error_count: int

    class Config:
        from_attributes = True

class DiscoveryStatusSummary(BaseModel):
    queries_executed_today: int
    urls_discovered: int
    urls_verified: int
    urls_rejected: int
    rejection_breakdown: Dict[str, int]
    candidates_pending_review: int
    duplicates_merged: int
    search_provider_quota_remaining: int
