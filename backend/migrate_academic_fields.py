import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.db.database import engine
from sqlalchemy import text

async def migrate():
    async with engine.begin() as conn:
        result = await conn.execute(text("PRAGMA table_info(student_profiles)"))
        existing = [r[1] for r in result.fetchall()]  # column index 1 = name

        if 'course_program' not in existing:
            await conn.execute(text(
                "ALTER TABLE student_profiles ADD COLUMN course_program VARCHAR(150)"
            ))
            print("Added course_program column.")
        else:
            print("course_program already exists.")

        if 'qualification_type' not in existing:
            await conn.execute(text(
                "ALTER TABLE student_profiles ADD COLUMN qualification_type VARCHAR(150)"
            ))
            print("Added qualification_type column.")
        else:
            print("qualification_type already exists.")

    print("Migration complete.")

asyncio.run(migrate())
