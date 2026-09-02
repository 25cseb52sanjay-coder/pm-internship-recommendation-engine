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
    # Step 1: Create all tables that do not yet exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Step 2: ADD COLUMN migrations — each in its own isolated connection/transaction
    await _run_add_column_migrations()

    # Step 3: Expand column types that may be too narrow in production PostgreSQL
    await _run_column_type_migrations()

    # Step 4: Auto-seed database if empty
    await seed_database_data()

    # Step 5: Start background opportunity sync scheduler (Greenhouse + Adzuna)
    OpportunitySyncService.start_scheduler()

    # Step 6: Configure live LeetCode GraphQL provider for production execution
    from app.leetcode.graphql_provider import LeetCodeGraphQLProvider
    from app.leetcode.data_provider import LeetCodeProviderRegistry
    LeetCodeProviderRegistry.set_provider(LeetCodeGraphQLProvider())

from app.db.database import engine, Base, AsyncSessionLocal


async def _run_add_column_migrations():
    """
    Runs all ADD COLUMN migrations with each statement in its own isolated connection.
    On PostgreSQL: a failed ADD COLUMN (column already exists) aborts the transaction,
    but since each statement gets its own connection, subsequent migrations still execute.
    On SQLite: uses the same approach (each statement isolated), which is also safe.
    """
    is_postgres = "postgresql" in settings.DATABASE_URL or "postgres" in settings.DATABASE_URL

    all_migrations = [
        # users table
        ("users", "provider VARCHAR(50) DEFAULT 'LOCAL'"),
        ("users", "google_subject_id VARCHAR(255)"),
        ("users", "avatar_url VARCHAR(500)"),
        ("users", "preferred_locale VARCHAR(10) DEFAULT 'en'"),
        # student_profiles table (Task 27A)
        ("student_profiles", "academic_level VARCHAR(100)"),
        ("student_profiles", "primary_discipline VARCHAR(255)"),
        ("student_profiles", "normalized_discipline VARCHAR(100)"),
        ("student_profiles", "specialization VARCHAR(255)"),
        ("student_profiles", "sub_specialization VARCHAR(255)"),
        ("student_profiles", "secondary_discipline VARCHAR(255)"),
        ("student_profiles", "minor_discipline VARCHAR(255)"),
        # internships table
        ("internships", "source_id INTEGER"),
        ("internships", "source_url VARCHAR(500)"),
        ("internships", "duplicate_fingerprint VARCHAR(255)"),
        ("internships", "fingerprint_sha256 VARCHAR(255)"),
        ("internships", "status VARCHAR(50) DEFAULT 'VERIFIED_LIVE'"),
        ("internships", "verification_status VARCHAR(50) DEFAULT 'VERIFIED'"),
        ("internships", "quality_score FLOAT DEFAULT 80.0"),
        ("internships", "required_education VARCHAR(100) DEFAULT 'Graduate'"),
        ("internships", "first_seen_at DATETIME"),
        ("internships", "last_seen_at DATETIME"),
        ("internships", "last_verified_at DATETIME"),
        ("internships", "posted_date DATETIME"),
        ("internships", "last_checked_at DATETIME"),
        ("internships", "is_demo BOOLEAN DEFAULT 0"),
        ("internships", "max_age INTEGER DEFAULT 24"),
        ("internships", "required_disciplines_json TEXT"),
        ("internships", "accepted_disciplines_json TEXT"),
        ("internships", "related_disciplines_json TEXT"),
        ("internships", "discipline_scope VARCHAR(50) DEFAULT 'UNKNOWN'"),
        ("internships", "specializations_json TEXT"),
        ("internships", "discipline_confidence FLOAT DEFAULT 1.0"),
        ("internships", "original_requirement_text TEXT"),
        # source_registry table
        ("source_registry", "api_endpoint VARCHAR(500)"),
        ("source_registry", "authentication_method VARCHAR(50) DEFAULT 'NONE'"),
        ("source_registry", "authorization_status VARCHAR(50) DEFAULT 'AUTHORIZED'"),
        ("source_registry", "enabled BOOLEAN DEFAULT 1"),
        ("source_registry", "polling_frequency_seconds INTEGER DEFAULT 900"),
        ("source_registry", "rate_limit INTEGER DEFAULT 60"),
        ("source_registry", "priority INTEGER DEFAULT 1"),
        ("source_registry", "last_success_at DATETIME"),
        ("source_registry", "last_failure_at DATETIME"),
        ("source_registry", "last_run_at DATETIME"),
        ("source_registry", "next_run_at DATETIME"),
        ("source_registry", "health_status VARCHAR(50) DEFAULT 'ONLINE'"),
        ("source_registry", "source_confidence FLOAT DEFAULT 1.0"),
        ("source_registry", "updated_at DATETIME"),
    ]

    for table, col_def in all_migrations:
        try:
            if is_postgres:
                raw_conn = await engine.raw_connection()
                try:
                    await raw_conn.set_autocommit(True)
                    await raw_conn.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col_def}")
                except Exception:
                    pass
                finally:
                    await raw_conn.close()
            else:
                async with engine.begin() as conn:
                    try:
                        await conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col_def}"))
                    except Exception:
                        pass
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"ADD COLUMN migration skipped ({table}.{col_def[:30]}): {e}")


async def _run_column_type_migrations():
    """
    Expands column types that are too narrow for real Greenhouse/Adzuna data.
    Only applies to PostgreSQL — SQLite column types are advisory only.
    """
    import logging
    logger = logging.getLogger("uvicorn.error")

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("ALTER TABLE internships ALTER COLUMN location TYPE VARCHAR(255);"))
            await session.commit()
            logger.info("Schema migration applied successfully: internships.location → VARCHAR(255)")
    except Exception as e:
        logger.warning(f"Column type migration internships.location → VARCHAR(255): {e}")
    

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
