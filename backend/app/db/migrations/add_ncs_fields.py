import os
import sys
import asyncio
import logging

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))
from sqlalchemy import text
from app.db.database import engine

logger = logging.getLogger(__name__)

async def migrate_ncs_database_fields():
    """
    Idempotent schema migration adding 'source' and 'apply_url' columns to 'internships' table
    if they do not already exist. Preserves 100% of existing internship database records.
    """
    print("\n--- Running NCS Database Schema Alignment Migration ---")
    async with engine.begin() as conn:
        # Check existing columns in internships table
        if engine.dialect.name == "sqlite":
            result = await conn.execute(text("PRAGMA table_info(internships)"))
            columns = [row[1] for row in result.fetchall()]
        else:
            result = await conn.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name='internships'"
            ))
            columns = [row[0] for row in result.fetchall()]

        if "source" not in columns:
            print("  - Adding 'source' column to 'internships' table...")
            await conn.execute(text("ALTER TABLE internships ADD COLUMN source VARCHAR(100) DEFAULT 'PMIS'"))
            print("  - 'source' column added successfully.")
        else:
            print("  - 'source' column already exists in 'internships' table.")

        if "apply_url" not in columns:
            print("  - Adding 'apply_url' column to 'internships' table...")
            await conn.execute(text("ALTER TABLE internships ADD COLUMN apply_url VARCHAR(500)"))
            print("  - 'apply_url' column added successfully.")
        else:
            print("  - 'apply_url' column already exists in 'internships' table.")

        # Populate apply_url from source_url for existing records if null
        if "source_url" in columns:
            await conn.execute(text("UPDATE internships SET apply_url = source_url WHERE apply_url IS NULL AND source_url IS NOT NULL"))
        await conn.execute(text("UPDATE internships SET source = 'PMIS' WHERE source IS NULL"))

    print("--- NCS Database Migration Completed Successfully ---\n")

if __name__ == "__main__":
    asyncio.run(migrate_ncs_database_fields())
