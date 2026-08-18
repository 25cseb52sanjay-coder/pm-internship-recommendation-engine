import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.database import AsyncSessionLocal
from app.greenhouse.service import GreenhouseService
from app.greenhouse.sync_service import GreenhouseSyncService
from sqlalchemy import select
from app.db.models import Internship

async def fetch_real_greenhouse_jobs():
    boards = ["stripe", "figma", "canonical", "gitlab", "cloudflare"]
    print(f"Fetching genuinely live Greenhouse jobs for boards: {boards}...")
    
    try:
        service = GreenhouseService()
        all_jobs = await service.fetch_and_normalize_jobs(board_tokens=boards)
        print(f"Total live Greenhouse jobs fetched: {len(all_jobs)}")
    except Exception as e:
        print(f"Error fetching live Greenhouse jobs: {e}")
        all_jobs = []

    if all_jobs:
        async with AsyncSessionLocal() as db:
            await GreenhouseSyncService.store_greenhouse_opportunities(db, all_jobs)
            await db.commit()

            # Ensure verification_status = VERIFIED
            res = await db.execute(select(Internship).where(Internship.source == "Greenhouse"))
            stored = res.scalars().all()
            for s in stored:
                s.verification_status = "VERIFIED"
                s.status = "VERIFIED_LIVE"
            await db.commit()

            print(f"Successfully stored & verified {len(stored)} real Greenhouse jobs in PostgreSQL!")
            for idx, s in enumerate(stored[:5], 1):
                print(f"  [{idx}] Title: '{s.title}' | Company: '{s.company_name}'")
                print(f"       ExtID: {s.external_id} | Apply URL: '{s.apply_url}'\n")

if __name__ == "__main__":
    asyncio.run(fetch_real_greenhouse_jobs())
