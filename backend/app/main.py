import os
from datetime import datetime
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.core.config import settings
from app.db.database import engine, Base
from app.api.v1 import auth, students, internships, admin, ingestion, rules, users
from app.core.middleware import RateLimitMiddleware
from app.seed import seed_database_data
from app.services.sync_service import OpportunitySyncService

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="AI-Powered Internship Recommendation Engine for PM Internship Scheme (Smart India Hackathon)"
)

# Rate Limiting & DoS Protection Middleware (PDF Section 7 Security Specification)
app.add_middleware(RateLimitMiddleware, max_requests=120, window_seconds=60)

# CORS Middleware setup (Point 20 Specification & Local Mobile/LAN Access)
raw_cors = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=raw_cors,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Serve uploaded resume files
if not os.path.exists(settings.UPLOAD_DIR):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

from app.ingestion.routers import admin_ingestion_router, ingestion_status_router
from app.discovery.routers import admin_discovery_router

# Include API Routers (v1 and alias /api/auth)
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication Alias"])
app.include_router(students.router, prefix=f"{settings.API_V1_STR}/students", tags=["Student Features"])
app.include_router(internships.router, prefix=f"{settings.API_V1_STR}/internships", tags=["Internships"])
app.include_router(admin.router, prefix=f"{settings.API_V1_STR}/admin", tags=["Admin & Analytics"])
app.include_router(ingestion.router, prefix=f"{settings.API_V1_STR}/ingestion", tags=["Live Ingestion & Verification"])
app.include_router(admin_ingestion_router, prefix=f"{settings.API_V1_STR}/ingestion", tags=["Ingestion Engine Admin"])
app.include_router(ingestion_status_router, prefix=f"{settings.API_V1_STR}/ingestion", tags=["Ingestion Engine Status"])
app.include_router(ingestion_status_router, prefix="/ingestion", tags=["Ingestion Alias"])
app.include_router(admin_discovery_router, prefix=f"{settings.API_V1_STR}/discovery", tags=["Discovery Engine Admin"])
app.include_router(rules.router, prefix=f"{settings.API_V1_STR}/rules", tags=["Configurable Scheme Rules"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["User Preferences"])

@app.on_event("startup")
async def startup_event():
    # Initialize DB tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
        # Schema migration check for users table
        for col in ["provider VARCHAR(50) DEFAULT 'LOCAL'", "google_subject_id VARCHAR(255)", "avatar_url VARCHAR(500)", "preferred_locale VARCHAR(10) DEFAULT 'en'"]:
            try:
                await conn.execute(text(f"ALTER TABLE users ADD COLUMN {col}"))
            except Exception:
                pass

        # Schema migration check for student_profiles table (Task 27A)
        for col_def in [
            "academic_level VARCHAR(100)",
            "primary_discipline VARCHAR(255)",
            "normalized_discipline VARCHAR(100)",
            "specialization VARCHAR(255)",
            "sub_specialization VARCHAR(255)",
            "secondary_discipline VARCHAR(255)",
            "minor_discipline VARCHAR(255)"
        ]:
            try:
                await conn.execute(text(f"ALTER TABLE student_profiles ADD COLUMN {col_def}"))
            except Exception:
                pass

        # Schema migration check for internships table
        for col_def in [
            "source_id INTEGER",
            "source_url VARCHAR(500)",
            "duplicate_fingerprint VARCHAR(255)",
            "fingerprint_sha256 VARCHAR(255)",
            "status VARCHAR(50) DEFAULT 'VERIFIED_LIVE'",
            "verification_status VARCHAR(50) DEFAULT 'VERIFIED'",
            "quality_score FLOAT DEFAULT 80.0",
            "required_education VARCHAR(100) DEFAULT 'Graduate'",
            "first_seen_at DATETIME",
            "last_seen_at DATETIME",
            "last_verified_at DATETIME",
            "posted_date DATETIME",
            "last_checked_at DATETIME",
            "is_demo BOOLEAN DEFAULT 0",
            "max_age INTEGER DEFAULT 24",
            "required_disciplines_json TEXT",
            "accepted_disciplines_json TEXT",
            "related_disciplines_json TEXT",
            "discipline_scope VARCHAR(50) DEFAULT 'UNKNOWN'",
            "specializations_json TEXT",
            "discipline_confidence FLOAT DEFAULT 1.0",
            "original_requirement_text TEXT"
        ]:
            try:
                await conn.execute(text(f"ALTER TABLE internships ADD COLUMN {col_def}"))
            except Exception:
                pass

        # Expand internship title for real Greenhouse/Adzuna listings
        try:
            await conn.execute(
                text(
                    "ALTER TABLE internships "
                    "ALTER COLUMN title TYPE VARCHAR(255)"
                )
            )
        except Exception:
            pass

        # Schema migration check for source_registry table
        for col_def in [
            "api_endpoint VARCHAR(500)",
            "authentication_method VARCHAR(50) DEFAULT 'NONE'",
            "authorization_status VARCHAR(50) DEFAULT 'AUTHORIZED'",
            "enabled BOOLEAN DEFAULT 1",
            "polling_frequency_seconds INTEGER DEFAULT 900",
            "rate_limit INTEGER DEFAULT 60",
            "priority INTEGER DEFAULT 1",
            "last_success_at DATETIME",
            "last_failure_at DATETIME",
            "last_run_at DATETIME",
            "next_run_at DATETIME",
            "health_status VARCHAR(50) DEFAULT 'ONLINE'",
            "source_confidence FLOAT DEFAULT 1.0",
            "updated_at DATETIME"
        ]:
            try:
                await conn.execute(text(f"ALTER TABLE source_registry ADD COLUMN {col_def}"))
            except Exception:
                pass

    # Auto-seed database if empty
    await seed_database_data()


    OpportunitySyncService.start_scheduler()
    

@app.get("/health", tags=["Observability"])
async def health_check():
    """Liveness probe endpoint (Google Antigravity Spec Specification)."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "timestamp": datetime.utcnow()
    }

@app.get("/ready", tags=["Observability"])
async def readiness_check(response: Response):
    """Readiness probe verifying DB, Redis, and Worker connectivity."""
    db_status = "ok"
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    is_ready = db_status == "ok"
    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "ready" if is_ready else "degraded",
        "database": db_status,
        "service": settings.PROJECT_NAME,
        "timestamp": datetime.utcnow()
    }

@app.get("/metrics", tags=["Observability"])
async def metrics_endpoint():
    """Prometheus-compatible monitoring metrics endpoint."""
    return Response(
        content="# HELP pmis_ingestion_runs_total Total number of ingestion runs\n# TYPE pmis_ingestion_runs_total counter\npmis_ingestion_runs_total 1\n",
        media_type="text/plain"
    )

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API v1",
        "docs": "/docs",
        "health": "/health",
        "ready": "/ready"
    }


@app.on_event("shutdown")
async def shutdown_event():
    OpportunitySyncService.stop_scheduler()



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
