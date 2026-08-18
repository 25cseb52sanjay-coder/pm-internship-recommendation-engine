from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.schemas.internship import InternshipOut

class ScoreBreakdown(BaseModel):
    skill_match: float
    semantic_similarity: float
    education_match: float
    career_interest: float
    location_match: float
    experience_relevance: float
    internship_preference: float

class RecommendationExplanation(BaseModel):
    summary: str
    matched_skills: List[str]
    missing_required_skills: List[str]
    education_status: str
    location_status: str
    breakdown: ScoreBreakdown
    reasons: List[str]
    strengths: List[str] = []
    weaknesses: List[str] = []

    # Task 19 Specification Additions
    overall_match_score: Optional[float] = None
    missing_skills: List[str] = []
    qualification_match: Optional[str] = None
    location_match: Optional[str] = None
    experience_match: Optional[str] = None
    opportunity_type_match: Optional[str] = None
    evidence_used: List[Dict[str, Any]] = []
    confidence: str = "MEDIUM" # HIGH, MEDIUM, LOW
    recommendation_reason: Optional[str] = None

class RecommendationOut(BaseModel):
    id: Optional[int] = None
    internship: InternshipOut
    score: float
    match_category: str # Excellent Match, Strong Match, Good Match, Potential Match
    explanation: RecommendationExplanation

class WeightsConfigSchema(BaseModel):
    skill_match_weight: float = 0.35
    semantic_weight: float = 0.25
    education_weight: float = 0.15
    interest_weight: float = 0.10
    location_weight: float = 0.05
    experience_weight: float = 0.05
    preference_weight: float = 0.05

    class Config:
        from_attributes = True
