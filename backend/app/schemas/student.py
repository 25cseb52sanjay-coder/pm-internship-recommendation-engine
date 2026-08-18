from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union

class SkillBase(BaseModel):
    id: Optional[int] = None
    name: str
    category: Optional[str] = None
    proficiency_level: Optional[str] = "Intermediate"

    class Config:
        from_attributes = True

class StudentProfileCreate(BaseModel):
    full_name: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    age: Optional[int] = None
    qualification: Optional[str] = None
    degree: Optional[str] = None
    course_program: Optional[str] = None
    qualification_type: Optional[str] = None
    branch: Optional[str] = None
    institution: Optional[str] = None
    graduation_year: Optional[int] = None
    cgpa: Optional[float] = None
    preferred_industry: Optional[str] = None
    preferred_role: Optional[str] = None
    preferred_location: Optional[str] = None
    work_mode: Optional[str] = None
    preferred_duration: Optional[str] = None
    projects_summary: Optional[str] = None
    skills: List[Any] = []

class StudentProfileOut(BaseModel):
    id: int
    user_id: int
    full_name: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    age: Optional[int] = None
    qualification: Optional[str] = None
    degree: Optional[str] = None
    course_program: Optional[str] = None
    qualification_type: Optional[str] = None
    branch: Optional[str] = None
    institution: Optional[str] = None
    graduation_year: Optional[int] = None
    cgpa: Optional[float] = None
    preferred_industry: Optional[str] = None
    preferred_role: Optional[str] = None
    preferred_location: Optional[str] = None
    work_mode: Optional[str] = None
    preferred_duration: Optional[str] = None
    resume_url: Optional[str] = None
    projects_summary: Optional[str] = None
    skills: List[SkillBase] = []

    class Config:
        from_attributes = True

class MissingSkillItem(BaseModel):
    skill: str
    priority: str # High, Medium, Low
    category: str
    recommendation_course: str

class SkillGapOut(BaseModel):
    student_skills: List[str]
    missing_required_skills: List[MissingSkillItem]
    career_path_suggestions: List[str]
    readiness_score: float # 0 - 100

class FeedbackCreate(BaseModel):
    internship_id: int
    feedback_type: str # USEFUL, NOT_RELEVANT, ALREADY_APPLIED, NOT_INTERESTED
    comments: Optional[str] = None
