import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from app.core.config import Settings

def test_negative_production_config_hardening():
    print("\n======================================================================")
    print("  NEGATIVE PRODUCTION CONFIGURATION HARDENING TEST SUITE")
    print("======================================================================\n")

    # 1. Test Production with Weak/Default SECRET_KEY -> MUST FAIL
    print("  [TEST 1] Testing Production Startup with Weak/Default SECRET_KEY...")
    try:
        s1 = Settings(
            ENVIRONMENT="production",
            SECRET_KEY="sih-pm-internship-recommendation-secret-key-2026",
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
            CORS_ORIGINS="https://app.com"
        )
        s1.validate_production_security()
        assert False, "Production with default SECRET_KEY should fail fast"
    except ValueError as e:
        assert "SECRET_KEY" in str(e)
        print("    - Production Startup REJECTED Default SECRET_KEY (PASSED)")

    # 2. Test Production with SQLite DATABASE_URL -> MUST FAIL
    print("\n  [TEST 2] Testing Production Startup with SQLite DATABASE_URL...")
    try:
        s2 = Settings(
            ENVIRONMENT="production",
            SECRET_KEY="a_very_strong_production_secret_key_32_characters_long",
            DATABASE_URL="sqlite+aiosqlite:///./pm_internships.db",
            CORS_ORIGINS="https://app.com"
        )
        s2.validate_production_security()
        assert False, "Production with SQLite DATABASE_URL should fail fast"
    except ValueError as e:
        assert "PostgreSQL" in str(e) or "SQLite" in str(e)
        print("    - Production Startup REJECTED SQLite Database URL (PASSED)")

    # 3. Test Production with Wildcard CORS_ORIGINS -> MUST FAIL
    print("\n  [TEST 3] Testing Production Startup with Wildcard CORS_ORIGINS...")
    try:
        s3 = Settings(
            ENVIRONMENT="production",
            SECRET_KEY="a_very_strong_production_secret_key_32_characters_long",
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
            CORS_ORIGINS="*"
        )
        s3.validate_production_security()
        assert False, "Production with Wildcard CORS_ORIGINS should fail fast"
    except ValueError as e:
        assert "CORS_ORIGINS" in str(e)
        print("    - Production Startup REJECTED Wildcard CORS ('*') (PASSED)")

    # 4. Test Valid Production Configuration -> MUST PASS
    print("\n  [TEST 4] Testing Valid Production Configuration...")
    s4 = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="a_very_strong_production_secret_key_32_characters_long",
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
        CORS_ORIGINS="https://app.com,https://mca.gov.in"
    )
    s4.validate_production_security()
    print("    - Valid Production Configuration ACCEPTED (PASSED)")

    print("\n======================================================================")
    print("  VERIFICATION RESULT: ALL CONFIGURATION HARDENING TESTS PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_negative_production_config_hardening()
