from pydantic import BaseModel
from typing import List, Dict

class SkillDemandItem(BaseModel):
    skill: str
    count: int
    category: str

class SectorStatItem(BaseModel):
    sector: str
    internship_count: int
    application_count: int

class AdminAnalyticsOut(BaseModel):
    total_students: int
    total_internships: int
    total_applications: int
    avg_recommendation_score: float
    top_demanded_skills: List[SkillDemandItem]
    top_missing_skills: List[SkillDemandItem]
    sector_distribution: List[SectorStatItem]
    recommendation_feedback_summary: Dict[str, int]
