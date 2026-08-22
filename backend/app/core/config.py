import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "PM Internship Recommendation Engine"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days for demo ease
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./pm_internships.db")
    
    # OAuth Google Settings
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "609018289565-qltf0pmrvl7hi1tbu6k445ikb6p3q4ea.apps.googleusercontent.com")
    
    # Uploads
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
    
    # Default AI Scoring Weights (configurable at runtime via admin)
    DEFAULT_SKILL_MATCH_WEIGHT: float = 0.35
    DEFAULT_SEMANTIC_WEIGHT: float = 0.25
    DEFAULT_EDUCATION_WEIGHT: float = 0.15
    DEFAULT_INTEREST_WEIGHT: float = 0.10
    DEFAULT_LOCATION_WEIGHT: float = 0.05
    DEFAULT_EXPERIENCE_WEIGHT: float = 0.05
    DEFAULT_PREFERENCE_WEIGHT: float = 0.05

    # Redis & Celery Config
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", os.getenv("REDIS_URL", "redis://localhost:6379/0"))

    # Ingestion Engine & Quality Thresholds
    RECOMMENDATION_MATCH_THRESHOLD: float = float(os.getenv("RECOMMENDATION_MATCH_THRESHOLD", "75.0"))
    INGESTION_QUALITY_SCORE_THRESHOLD: float = float(os.getenv("INGESTION_QUALITY_SCORE_THRESHOLD", "50.0"))
    PROMETHEUS_METRICS_ENABLED: bool = os.getenv("PROMETHEUS_METRICS_ENABLED", "true").lower() == "true"

    # Connector Authorization Credentials (Optional / NOT_CONFIGURED default)
    LINKEDIN_API_KEY: Optional[str] = os.getenv("LINKEDIN_API_KEY", None)
    INTERNSHALA_API_KEY: Optional[str] = os.getenv("INTERNSHALA_API_KEY", None)
    NAUKRI_API_KEY: Optional[str] = os.getenv("NAUKRI_API_KEY", None)

    # Adzuna Official REST API Authorization Credentials
    ADZUNA_APP_ID: Optional[str] = os.getenv("ADZUNA_APP_ID", None)
    ADZUNA_APP_KEY: Optional[str] = os.getenv("ADZUNA_APP_KEY", None)

    # Discovery Engine Configuration
    SEARCH_PROVIDER_API_KEY: Optional[str] = os.getenv("SEARCH_PROVIDER_API_KEY", None)
    SEARCH_PROVIDER_ENDPOINT: str = os.getenv("SEARCH_PROVIDER_ENDPOINT", "https://api.bing.microsoft.com/v7.0/search")
    SEARCH_PROVIDER_QUOTA_PER_DAY: int = int(os.getenv("SEARCH_PROVIDER_QUOTA_PER_DAY", "1000"))
    DISCOVERY_INTERVAL_SECONDS: int = int(os.getenv("DISCOVERY_INTERVAL_SECONDS", "1800"))
    RECHECK_INTERVAL_SECONDS: int = int(os.getenv("RECHECK_INTERVAL_SECONDS", "7200"))
    DEADLINE_CHECK_INTERVAL_SECONDS: int = int(os.getenv("DEADLINE_CHECK_INTERVAL_SECONDS", "1800"))
    DOMAIN_TRUST_STRICT_MODE: bool = os.getenv("DOMAIN_TRUST_STRICT_MODE", "true").lower() == "true"
    PLAYWRIGHT_ALLOWED_DOMAINS: str = os.getenv("PLAYWRIGHT_ALLOWED_DOMAINS", "careers.isro.gov.in,nitiaayog.gov.in,tatamotors.com,bhel.com")

    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development").lower()
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,https://pminternship.mca.gov.in")

    class Config:
        case_sensitive = True

    def validate_production_security(self):
        """
        Production Environment Hardening Validation (PDF Section 7 Security Spec).
        Fails fast if production environment lacks mandatory security configurations.
        """
        if self.ENVIRONMENT == "production":
            KNOWN_DEV_SECRETS = [
                "sih-pm-internship-recommendation-secret-key-2026",
                "your_production_secret_key_here",
                "secret",
                "changeme",
                "default"
            ]
            if not self.SECRET_KEY or self.SECRET_KEY in KNOWN_DEV_SECRETS or len(self.SECRET_KEY) < 32:
                raise ValueError(
                    "CRITICAL PRODUCTION SECURITY FAILURE: A strong, cryptographically secure SECRET_KEY (>= 32 characters) "
                    "must be provided in production environment!"
                )

            if not self.DATABASE_URL or "sqlite" in self.DATABASE_URL.lower():
                raise ValueError(
                    "CRITICAL PRODUCTION SECURITY FAILURE: Production environment requires a PostgreSQL database URL "
                    "(postgresql+asyncpg://...). SQLite is strictly prohibited in production!"
                )

            if not self.CORS_ORIGINS or "*" in self.CORS_ORIGINS:
                raise ValueError(
                    "CRITICAL PRODUCTION SECURITY FAILURE: CORS_ORIGINS must be explicitly configured in production without wildcards ('*')!"
                )

settings = Settings()
settings.validate_production_security()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
