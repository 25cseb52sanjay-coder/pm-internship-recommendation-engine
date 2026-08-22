from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
import enum
from app.db.database import Base

class UserRole(str, enum.Enum):
    STUDENT = "STUDENT"
    ADMIN = "ADMIN"

class ApplicationStatus(str, enum.Enum):
    APPLIED = "APPLIED"
    UNDER_REVIEW = "UNDER_REVIEW"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

class FeedbackType(str, enum.Enum):
    USEFUL = "USEFUL"
    NOT_RELEVANT = "NOT_RELEVANT"
    ALREADY_APPLIED = "ALREADY_APPLIED"
    NOT_INTERESTED = "NOT_INTERESTED"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    role = Column(String(50), default=UserRole.STUDENT, nullable=False)
    full_name = Column(String(255), nullable=False)
    provider = Column(String(50), default="LOCAL", nullable=False)
    google_subject_id = Column(String(255), unique=True, index=True, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    preferred_locale = Column(String(10), default="en", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")

class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    age = Column(Integer, nullable=True)
    qualification = Column(String(100), nullable=True)  # e.g., Bachelor's, Master's, Diploma
    degree = Column(String(100), nullable=True)         # e.g., B.Tech, B.Sc, B.Com, MBA
    course_program = Column(String(150), nullable=True)  # e.g., B.E. / B.Tech, MBA, Diploma
    qualification_type = Column(String(150), nullable=True)  # e.g., Engineering Degree, Postgraduate Degree
    branch = Column(String(100), nullable=True)         # e.g., Computer Science, Mechanical, Finance
    institution = Column(String(255), nullable=True)
    graduation_year = Column(Integer, nullable=True)
    cgpa = Column(Float, nullable=True)
    
    preferred_industry = Column(String(100), nullable=True) # e.g., IT & Software, Public Sector, Manufacturing
    preferred_role = Column(String(100), nullable=True)     # e.g., Data Analyst, Software Intern, Operations
    preferred_location = Column(String(100), nullable=True) # e.g., Delhi, Bangalore, Remote, Any
    work_mode = Column(String(50), nullable=True)          # e.g., Remote, On-site, Hybrid
    preferred_duration = Column(String(50), nullable=True)  # e.g., 3 Months, 6 Months
    
    # Task 27A Academic Discipline & Specialization Columns
    academic_level = Column(String(100), nullable=True) # Undergraduate, Postgraduate, Diploma
    primary_discipline = Column(String(255), nullable=True) # Raw branch text e.g. "Computer Science & Engineering"
    normalized_discipline = Column(String(100), index=True, nullable=True) # e.g. "COMPUTER_SCIENCE"
    specialization = Column(String(255), nullable=True) # e.g. "Artificial Intelligence"
    sub_specialization = Column(String(255), nullable=True)
    secondary_discipline = Column(String(255), nullable=True)
    minor_discipline = Column(String(255), nullable=True)
    
    resume_url = Column(String(255), nullable=True)
    raw_resume_text = Column(Text, nullable=True)
    projects_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")
    skills = relationship("StudentSkill", back_populates="student", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="student", cascade="all, delete-orphan")
    saved_internships = relationship("SavedInternship", back_populates="student", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="student", cascade="all, delete-orphan")
    feedbacks = relationship("RecommendationFeedback", back_populates="student", cascade="all, delete-orphan")
    leetcode_profile = relationship("LeetCodeProfile", back_populates="candidate", uselist=False, cascade="all, delete-orphan")

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    category = Column(String(100), nullable=True) # e.g., Programming, Data Science, Soft Skills, Operations

class StudentSkill(Base):
    __tablename__ = "student_skills"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    proficiency_level = Column(String(50), default="Intermediate") # Beginner, Intermediate, Advanced

    student = relationship("StudentProfile", back_populates="skills")
    skill = relationship("Skill")

class Internship(Base):
    __tablename__ = "internships"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False)
    company_sector = Column(String(100), nullable=False) # Public Sector, Automotive, IT Services, Government, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(255), nullable=False)
    work_mode = Column(String(50), default="On-site") # On-site, Remote, Hybrid
    duration = Column(String(50), nullable=False)    # e.g., 3 Months, 6 Months, 12 Months
    stipend = Column(String(100), nullable=False)     # e.g., ₹12,000 / month (PM Scheme standard ₹5,000 + company top-up)
    deadline = Column(String(50), nullable=False, index=True)
    positions = Column(Integer, default=5)
    
    # Hard Filters & Eligibility Requirements
    min_qualification = Column(String(100), default="Graduate")
    preferred_degree = Column(String(100), nullable=True)
    min_age = Column(Integer, default=21)
    max_age = Column(Integer, default=24)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Task 27A Multi-Discipline Opportunity Fields
    required_disciplines_json = Column(Text, nullable=True) # JSON list e.g. '["COMPUTER_SCIENCE", "INFORMATION_TECHNOLOGY"]'
    accepted_disciplines_json = Column(Text, nullable=True)
    related_disciplines_json = Column(Text, nullable=True)
    discipline_scope = Column(String(50), default="UNKNOWN", index=True) # SPECIFIC_DISCIPLINE, MULTI_DISCIPLINE, ALL_ENGINEERING, ALL_TECHNOLOGY, CROSS_DISCIPLINARY, UNKNOWN
    specializations_json = Column(Text, nullable=True)
    discipline_confidence = Column(Float, default=1.0)
    original_requirement_text = Column(Text, nullable=True)

    # Live Ingestion, Deduplication & Lifecycle Fields (Google Antigravity Spec)
    source = Column(String(100), default="PMIS", index=True) # Source identifier e.g. NCS, PMIS, Greenhouse
    source_id = Column(Integer, ForeignKey("source_registry.id", ondelete="SET NULL"), nullable=True)
    external_id = Column(String(255), index=True, nullable=True) # Original Greenhouse or external job ID
    department = Column(String(255), nullable=True) # Department / functional area
    employment_type = Column(String(100), nullable=True) # Full-time, Part-time, Internship, etc.
    opportunity_type = Column(String(50), default="INTERNSHIP", index=True) # JOB, INTERNSHIP, UNKNOWN
    source_url = Column(String(500), nullable=True)
    apply_url = Column(String(500), nullable=True) # Direct original application link
    duplicate_fingerprint = Column(String(255), index=True, nullable=True)
    fingerprint_sha256 = Column(String(255), unique=True, index=True, nullable=True)
    status = Column(String(50), default="UNVERIFIED", index=True) # DISCOVERED, VALIDATING, VERIFIED_LIVE, UPDATED, EXPIRING_SOON, EXPIRED, CLOSED, ARCHIVED, REJECTED, UNVERIFIED
    verification_status = Column(String(50), default="UNVERIFIED") # PENDING, VERIFIED, REJECTED, UNVERIFIED
    quality_score = Column(Float, default=80.0) # 0 to 100 quality completeness index
    required_education = Column(String(100), default="Graduate")
    first_seen_at = Column(DateTime, default=datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.utcnow)
    last_verified_at = Column(DateTime, default=datetime.utcnow)
    posted_date = Column(DateTime, default=datetime.utcnow)
    last_checked_at = Column(DateTime, default=datetime.utcnow)
    is_demo = Column(Boolean, default=False)

    skills = relationship("InternshipSkill", back_populates="internship", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="internship", cascade="all, delete-orphan")

class InternshipSkill(Base):
    __tablename__ = "internship_skills"

    id = Column(Integer, primary_key=True, index=True)
    internship_id = Column(Integer, ForeignKey("internships.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    is_required = Column(Boolean, default=True) # True = Mandatory, False = Preferred

    internship = relationship("Internship", back_populates="skills")
    skill = relationship("Skill")

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    internship_id = Column(Integer, ForeignKey("internships.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default=ApplicationStatus.APPLIED)
    applied_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("StudentProfile", back_populates="applications")
    internship = relationship("Internship", back_populates="applications")

class SavedInternship(Base):
    __tablename__ = "saved_internships"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    internship_id = Column(Integer, ForeignKey("internships.id", ondelete="CASCADE"), nullable=False)
    saved_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("StudentProfile", back_populates="saved_internships")
    internship = relationship("Internship")

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    internship_id = Column(Integer, ForeignKey("internships.id", ondelete="CASCADE"), nullable=False)
    score = Column(Float, nullable=False) # 0 to 100
    match_category = Column(String(50), nullable=False) # Excellent Match, Strong Match, Good Match, Potential Match
    explanation_json = Column(JSON, nullable=False)
    calculated_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("StudentProfile", back_populates="recommendations")
    internship = relationship("Internship")

class RecommendationFeedback(Base):
    __tablename__ = "recommendation_feedback"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    internship_id = Column(Integer, ForeignKey("internships.id", ondelete="CASCADE"), nullable=False)
    feedback_type = Column(String(50), nullable=False)
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("StudentProfile", back_populates="feedbacks")
    internship = relationship("Internship")

class ScoringWeightsConfig(Base):
    __tablename__ = "scoring_weights_config"

    id = Column(Integer, primary_key=True, index=True)
    skill_match_weight = Column(Float, default=0.35)
    semantic_weight = Column(Float, default=0.25)
    education_weight = Column(Float, default=0.15)
    interest_weight = Column(Float, default=0.10)
    location_weight = Column(Float, default=0.05)
    experience_weight = Column(Float, default=0.05)
    preference_weight = Column(Float, default=0.05)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SourceRegistry(Base):
    __tablename__ = "source_registry"

    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String(100), nullable=False)
    source_url = Column(String(500), nullable=False)
    source_type = Column(String(50), default="OFFICIAL_SCHEME") # OFFICIAL_GOVERNMENT, OFFICIAL_SCHEME, COMPANY_CAREER, AUTHORIZED_API, AUTHORIZED_FEED, LICENSED_PROVIDER
    api_endpoint = Column(String(500), nullable=True)
    authentication_method = Column(String(50), default="NONE") # NONE, API_KEY, OAUTH2, BEARER_TOKEN
    authorization_status = Column(String(50), default="AUTHORIZED") # AUTHORIZED, NOT_CONFIGURED, REVOKED, RATE_LIMITED, UNAVAILABLE
    enabled = Column(Boolean, default=True)
    polling_frequency_seconds = Column(Integer, default=900)
    rate_limit = Column(Integer, default=60)
    priority = Column(Integer, default=1)
    last_success_at = Column(DateTime, nullable=True)
    last_failure_at = Column(DateTime, nullable=True)
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, index=True, nullable=True)
    health_status = Column(String(50), default="ONLINE") # ONLINE, DEGRADED, FAILED, UNAUTHORIZED, RATE_LIMITED, DISABLED, NOT_CONFIGURED
    source_confidence = Column(Float, default=1.0)
    collection_method = Column(String(50), default="AUTOMATED")
    is_active = Column(Boolean, default=True)
    rate_limit_rpm = Column(Integer, default=60)
    last_checked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SchemeRule(Base):
    __tablename__ = "scheme_rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_code = Column(String(50), unique=True, index=True, nullable=False)
    rule_name = Column(String(255), nullable=False)
    rule_version = Column(String(20), default="v1.0")
    min_age = Column(Integer, default=21)
    max_age = Column(Integer, default=24)
    mandatory_degree = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class StudentEducation(Base):
    __tablename__ = "student_education"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    degree_level = Column(String(100), nullable=False) # e.g., Bachelor's, Master's, Diploma
    degree_name = Column(String(100), nullable=False)  # e.g., B.Tech, B.Sc, B.Com
    field_of_study = Column(String(100), nullable=True)
    institution_name = Column(String(255), nullable=False)
    start_year = Column(Integer, nullable=True)
    completion_year = Column(Integer, nullable=True)
    cgpa_or_percentage = Column(Float, nullable=True)

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), default="INFO") # INFO, RECOMMENDATION, ALLOCATION, APPLICATION
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class AlgorithmVersion(Base):
    __tablename__ = "algorithm_versions"

    id = Column(Integer, primary_key=True, index=True)
    algorithm_name = Column(String(100), nullable=False)
    version_tag = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class EligibilityResult(Base):
    __tablename__ = "eligibility_results"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    is_eligible = Column(Boolean, default=True)
    eligibility_status = Column(String(50), default="ELIGIBLE")
    age_valid = Column(Boolean, default=True)
    qualification_valid = Column(Boolean, default=True)
    checked_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), nullable=False)
    entity_name = Column(String(100), nullable=True)
    entity_id = Column(Integer, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(500), unique=True, index=True, nullable=False)
    revoked_at = Column(DateTime, default=datetime.utcnow)

class SourceReference(Base):
    __tablename__ = "source_references"

    id = Column(Integer, primary_key=True, index=True)
    internship_id = Column(Integer, ForeignKey("internships.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(Integer, ForeignKey("source_registry.id", ondelete="CASCADE"), nullable=False, index=True)
    source_name = Column(String(100), nullable=False)
    source_url = Column(String(500), nullable=True)
    external_id = Column(String(255), nullable=True)
    first_seen_at = Column(DateTime, default=datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.utcnow)
    source_confidence = Column(Float, default=1.0)

class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    run_id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("source_registry.id", ondelete="CASCADE"), nullable=False, index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="RUNNING") # RUNNING, COMPLETED, FAILED, PARTIAL
    records_discovered = Column(Integer, default=0)
    records_created = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_unchanged = Column(Integer, default=0)
    records_rejected = Column(Integer, default=0)
    duplicates_detected = Column(Integer, default=0)
    expired_records = Column(Integer, default=0)
    error_count = Column(Integer, default=0)

class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"

    job_id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("ingestion_runs.run_id", ondelete="CASCADE"), nullable=False, index=True)
    job_type = Column(String(50), nullable=False) # ingestion, parsing, normalization, deduplication, verification, expiry_check
    status = Column(String(50), default="PENDING") # PENDING, RUNNING, SUCCESS, FAILED, RETRYING
    attempt_count = Column(Integer, default=0)
    idempotency_key = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    next_retry_at = Column(DateTime, nullable=True)

class IngestionError(Base):
    __tablename__ = "ingestion_errors"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("ingestion_runs.run_id", ondelete="CASCADE"), nullable=True, index=True)
    source_id = Column(Integer, ForeignKey("source_registry.id", ondelete="CASCADE"), nullable=True, index=True)
    error_type = Column(String(50), nullable=False) # TRANSIENT_ERROR, PERMANENT_ERROR, AUTH_ERROR, RATE_LIMIT_ERROR, SERVER_ERROR, VALIDATION_ERROR
    error_message = Column(Text, nullable=False)
    payload_snapshot = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class DiscoverySearchQuery(Base):
    __tablename__ = "discovery_search_queries"

    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(String(500), unique=True, index=True, nullable=False)
    category = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    branch = Column(String(100), nullable=True)
    skill_tag = Column(String(100), nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, index=True, nullable=True)
    result_count_last_run = Column(Integer, default=0)
    enabled = Column(Boolean, default=True)

class DiscoveryCandidate(Base):
    __tablename__ = "discovery_candidates"

    id = Column(Integer, primary_key=True, index=True)
    search_query_id = Column(Integer, ForeignKey("discovery_search_queries.id", ondelete="SET NULL"), nullable=True, index=True)
    result_url = Column(String(500), nullable=False)
    discovered_at = Column(DateTime, default=datetime.utcnow)
    fetch_status = Column(String(50), default="PENDING") # PENDING, FETCHED, FETCH_FAILED
    extraction_status = Column(String(50), default="PENDING") # PENDING, EXTRACTED, EXTRACTION_FAILED
    verification_status = Column(String(50), default="PENDING", index=True) # PENDING, FETCH_FAILED, NOT_IDENTIFIABLE_EMPLOYER, NOT_INTERNSHIP_CONTENT, APPLICATION_URL_INVALID, DEADLINE_INVALID_OR_EXPIRED, STALE_CONTENT, VERIFIED, REJECTED
    quality_score = Column(Float, default=0.0)
    employer_domain = Column(String(255), nullable=True)
    official_domain_match = Column(Boolean, default=False)
    application_url_valid = Column(Boolean, default=False)
    deadline_extracted = Column(String(50), nullable=True)
    content_recency_check_passed = Column(Boolean, default=False)
    fingerprint_sha256 = Column(String(255), index=True, nullable=True)
    linked_internship_id = Column(Integer, ForeignKey("internships.id", ondelete="SET NULL"), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    extracted_payload_json = Column(Text, nullable=True)

class DiscoveryRun(Base):
    __tablename__ = "discovery_runs"

    run_id = Column(Integer, primary_key=True, index=True)
    search_query_id = Column(Integer, ForeignKey("discovery_search_queries.id", ondelete="SET NULL"), nullable=True, index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="RUNNING") # RUNNING, COMPLETED, FAILED
    urls_discovered = Column(Integer, default=0)
    urls_fetched = Column(Integer, default=0)
    urls_verified = Column(Integer, default=0)
    urls_rejected = Column(Integer, default=0)
    duplicates_detected = Column(Integer, default=0)
    error_count = Column(Integer, default=0)

class LeetCodeProfile(Base):
    __tablename__ = "leetcode_profiles"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    leetcode_profile_url = Column(String(500), nullable=True)
    leetcode_username = Column(String(100), index=True, nullable=True)
    account_exists = Column(Boolean, default=False)

    # Status Values: NOT_STARTED, PENDING, VERIFIED, FAILED, EXPIRED
    ownership_status = Column(String(50), default="NOT_STARTED", index=True)

    # Status Values: NOT_CONNECTED, PENDING, VERIFIED, FAILED, UNAVAILABLE
    verification_status = Column(String(50), default="NOT_CONNECTED", index=True)

    verification_method = Column(String(100), default="BIO_TOKEN_CHALLENGE")
    verification_challenge_token = Column(String(100), nullable=True)

    verification_created_at = Column(DateTime, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    last_verified_at = Column(DateTime, nullable=True)

    # Status Values: NOT_AVAILABLE, AVAILABLE, STALE, ERROR
    data_status = Column(String(50), default="NOT_AVAILABLE", index=True)
    last_data_refresh_at = Column(DateTime, nullable=True)

    # Real Profile Metrics (All nullable=True to prevent marking missing metrics as 0)
    total_problems_solved = Column(Integer, nullable=True)
    easy_solved = Column(Integer, nullable=True)
    medium_solved = Column(Integer, nullable=True)
    hard_solved = Column(Integer, nullable=True)
    languages_json = Column(Text, nullable=True)
    skills_json = Column(Text, nullable=True)
    badges_json = Column(Text, nullable=True)
    contest_rating = Column(Float, nullable=True)
    contest_rank = Column(Integer, nullable=True)
    recent_activity_json = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    candidate = relationship("StudentProfile", back_populates="leetcode_profile")

class CandidateEvidence(Base):
    __tablename__ = "candidate_evidences"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    evidence_type = Column(String(50), nullable=False, index=True) # SKILL, ACADEMIC, RESUME, CERTIFICATION, ASSESSMENT, LEETCODE
    value = Column(Text, nullable=False)
    source = Column(String(100), nullable=False) # Candidate Profile, Academic Record, Resume Parsing, Platform Assessment, LeetCode
    verification_status = Column(String(50), nullable=False, index=True) # SELF_DECLARED, DOCUMENTED, ASSESSED, VERIFIED_EXTERNAL, DATA_UNAVAILABLE
    confidence = Column(Float, default=0.5) # 0.0 to 1.0
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    candidate = relationship("StudentProfile", backref="evidences")
