import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.db.models import Internship

async def check_records():
    async with AsyncSessionLocal() as db:
        res = await db.execute(
            select(Internship).where(
                Internship.is_demo == False
            ).order_by(Internship.id.desc()).limit(30)
        )
        items = res.scalars().all()
        print(f"Total Real Items Found: {len(items)}")
        for idx, item in enumerate(items, 1):
            print(f"[{idx}] ID={item.id} | Source={item.source} | ExtID={item.external_id}")
            print(f"     Title: '{item.title}'")
            print(f"     Company: '{item.company_name}'")
            print(f"     Apply URL: '{item.apply_url}'\n")

if __name__ == "__main__":
    asyncio.run(check_records())
