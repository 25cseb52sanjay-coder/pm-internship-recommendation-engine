import os
import sys
import asyncio
import logging

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))
from sqlalchemy import text
from app.db.database import engine

logger = logging.getLogger(__name__)

async def migrate_greenhouse_database_fields():
    """
    Idempotent schema migration adding Greenhouse integration columns:
    'external_id', 'department', 'employment_type', and 'opportunity_type' to 'internships' table.
    Preserves 100% of existing NCS, PMIS, and third-party internship database records.
    """
    print("\n--- Running Greenhouse Database Schema Alignment Migration ---")
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

        fields_to_add = [
            ("external_id", "VARCHAR(255)"),
            ("department", "VARCHAR(255)"),
            ("employment_type", "VARCHAR(100)"),
            ("opportunity_type", "VARCHAR(50) DEFAULT 'INTERNSHIP'")
        ]

        for field_name, field_type in fields_to_add:
            if field_name not in columns:
                print(f"  - Adding '{field_name}' column to 'internships' table...")
                await conn.execute(text(f"ALTER TABLE internships ADD COLUMN {field_name} {field_type}"))
                print(f"  - '{field_name}' column added successfully.")
            else:
                print(f"  - '{field_name}' column already exists in 'internships' table.")

    print("--- Greenhouse Database Migration Completed Successfully ---\n")

if __name__ == "__main__":
    asyncio.run(migrate_greenhouse_database_fields())
