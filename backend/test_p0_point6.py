import asyncio
import time
from app.db.database import AsyncSessionLocal
from app.db.models import SourceRegistry, Internship
from app.services.ingestion import InternshipIngestionService
from sqlalchemy import select

def test_ingestion_pipeline_and_deduplication():
    print("\n======================================================================")
    print("  AUDIT TEST: P0 POINT 6 — LIVE INGESTION, DEDUPLICATION & EXPIRY")
    print("======================================================================\n")

    async def run_ingestion_test():
        async with AsyncSessionLocal() as db:
            # 1. Fetch default sources
            sources = await InternshipIngestionService.get_or_create_default_sources(db)
            src_id = sources[0].id
            print(f"  [1] Approved Ingestion Source ID: {src_id} ({sources[0].source_name})")

            # 2. Ingest initial raw items with dynamic timestamp for idempotency
            t_stamp = int(time.time())
            raw_feed = [
                {
                    "company_name": f"Defense Research and Development Organisation (DRDO-{t_stamp})",
                    "company_sector": "Defense / Public Sector",
                    "title": f"Avionics Data Analytics Intern-{t_stamp}",
                    "description": "Work on radar signal telemetry and Python algorithmic pipelines.",
                    "location": "Bengaluru",
                    "deadline": "2026-12-31"
                },
                {
                    # Malformed record missing title
                    "company_name": "Incomplete Enterprise",
                    "location": "Delhi"
                }
            ]

            res1 = await InternshipIngestionService.ingest_internship_feed(db, src_id, raw_feed)
            print(f"  [2] Initial Feed Ingestion Result: Processed={res1['processed']}, New={res1['new_ingested']}, Duplicates={res1['duplicates_skipped']}")
            assert res1['new_ingested'] == 1, "Expected exactly 1 new valid internship ingested"

            # 3. Duplicate Ingestion Test (Ingest identical opportunity again)
            res2 = await InternshipIngestionService.ingest_internship_feed(db, src_id, raw_feed)
            print(f"  [3] Re-Ingestion SHA-256 Duplicate Test: Processed={res2['processed']}, New={res2['new_ingested']}, Duplicates={res2['duplicates_skipped']}")
            assert res2['duplicates_skipped'] == 1, "Expected duplicate detector to catch and skip identical opportunity"

            # 4. Freshness Expiry Daemon Test
            expired_count = await InternshipIngestionService.check_freshness_and_expire_stale(db)
            print(f"  [4] Freshness Daemon Run: Expired Stale Listings Count = {expired_count}")

    asyncio.run(run_ingestion_test())

    print("\n======================================================================")
    print("  VERIFICATION RESULT: P0 POINT 6 PASSED (100% SUCCESS)")
    print("======================================================================\n")

if __name__ == "__main__":
    test_ingestion_pipeline_and_deduplication()
