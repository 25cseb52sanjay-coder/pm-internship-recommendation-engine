import asyncio
from sqlalchemy import select, update
from app.db.database import AsyncSessionLocal
from app.db.models import Internship

async def purge_unverified_listings():
    print("Executing strict database update: Setting synthetic/demo and unverified records to UNVERIFIED...")
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Internship))
        all_opps = res.scalars().all()

        updated_count = 0
        for opp in all_opps:
            # Listing is unverified if it lacks a validated source_url, or is a seed/demo listing, or has a test epoch title
            is_unverified = (
                opp.is_demo or
                not opp.source_url or
                opp.source_url == "" or
                "1786" in opp.title or
                opp.id <= 8 # Seed database records
            )

            if is_unverified or opp.status == "VERIFIED_LIVE":
                opp.status = "UNVERIFIED"
                opp.verification_status = "UNVERIFIED"
                opp.is_demo = True
                db.add(opp)
                updated_count += 1

        await db.commit()
        print(f"Database Migration Complete: {updated_count} records updated to UNVERIFIED status.")

if __name__ == "__main__":
    asyncio.run(purge_unverified_listings())
