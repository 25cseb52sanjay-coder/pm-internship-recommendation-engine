import asyncio
from sqlalchemy import select, delete
from app.db.database import AsyncSessionLocal
from app.db.models import Internship, SourceReference, IngestionRun, IngestionError, InternshipSkill

async def cleanup_test_records():
    print("Cleaning up test runner artifact records from database...")
    async with AsyncSessionLocal() as db:
        # Delete internship records created by test runners with epoch timestamp suffixes
        res = await db.execute(select(Internship).where(Internship.title.like("%-%17866%")))
        test_opps = res.scalars().all()
        
        count = 0
        for item in test_opps:
            await db.execute(delete(InternshipSkill).where(InternshipSkill.internship_id == item.id))
            await db.execute(delete(SourceReference).where(SourceReference.internship_id == item.id))
            await db.delete(item)
            count += 1
            
        await db.commit()
        print(f"Successfully cleaned up {count} test runner internship records from database.")

if __name__ == "__main__":
    asyncio.run(cleanup_test_records())
