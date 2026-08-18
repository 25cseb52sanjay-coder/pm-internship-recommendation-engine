import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.db.models import Internship

async def list_live_real_opportunities():
    async with AsyncSessionLocal() as db:
        res = await db.execute(
            select(Internship).where(
                Internship.source == "Greenhouse",
                Internship.is_demo == False
            ).order_by(Internship.id.desc()).limit(30)
        )
        items = res.scalars().all()
        print(f"Total Live Greenhouse Items Sample: {len(items)}")
        for idx, s in enumerate(items, 1):
            print(f"[{idx}] ID={s.id} | Company='{s.company_name}' | ExtID={s.external_id}")
            print(f"     Title: '{s.title}'")
            print(f"     Apply URL: '{s.apply_url}'\n")

if __name__ == "__main__":
    asyncio.run(list_live_real_opportunities())
