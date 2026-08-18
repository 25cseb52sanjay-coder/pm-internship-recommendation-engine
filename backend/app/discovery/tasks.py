import asyncio
import logging
from datetime import datetime
from sqlalchemy import select

from app.ingestion.celery_app import celery_app
from app.db.database import AsyncSessionLocal
from app.db.models import DiscoverySearchQuery, DiscoveryCandidate, DiscoveryRun
from app.discovery.query_generator import generate_dynamic_search_queries
from app.discovery.search_providers import AuthorizedWebSearchProvider
from app.discovery.verification import process_discovery_candidate_verification

logger = logging.getLogger(__name__)

def run_async(coro):
    loop = asyncio.get_event_loop()
    if loop.is_running():
        return asyncio.ensure_future(coro)
    return loop.run_until_complete(coro)

@celery_app.task(name="app.discovery.tasks.run_discovery_sweep_task")
def run_discovery_sweep_task():
    """
    Celery Task: Executes web discovery sweep across rotated search queries.
    """
    async def _execute():
        async with AsyncSessionLocal() as db:
            # 1. Generate & rotate queries
            queries = await generate_dynamic_search_queries(db, limit=5)
            if not queries:
                q_res = await db.execute(select(DiscoverySearchQuery).where(DiscoverySearchQuery.enabled == True).limit(5))
                queries = q_res.scalars().all()

            search_provider = AuthorizedWebSearchProvider()

            for query in queries:
                # Audit Run Record
                run_rec = DiscoveryRun(
                    search_query_id=query.id,
                    started_at=datetime.utcnow(),
                    status="RUNNING"
                )
                db.add(run_rec)
                await db.commit()
                await db.refresh(run_rec)

                try:
                    search_results = await search_provider.execute_search(query.query_text, num_results=5)
                    run_rec.urls_discovered = len(search_results)
                    query.result_count_last_run = len(search_results)
                    query.last_run_at = datetime.utcnow()
                    db.add(query)

                    for item in search_results:
                        url = item.get("url")
                        if not url:
                            continue

                        # Check existing candidate
                        cand_res = await db.execute(select(DiscoveryCandidate).where(DiscoveryCandidate.result_url == url))
                        cand = cand_res.scalar_one_or_none()

                        if not cand:
                            cand = DiscoveryCandidate(
                                search_query_id=query.id,
                                result_url=url,
                                discovered_at=datetime.utcnow()
                            )
                            db.add(cand)
                            await db.flush()

                        run_rec.urls_fetched += 1
                        status_code, msg, q_score = await process_discovery_candidate_verification(db, cand)

                        if status_code == "VERIFIED":
                            run_rec.urls_verified += 1
                        else:
                            run_rec.urls_rejected += 1

                    run_rec.status = "COMPLETED"
                    run_rec.completed_at = datetime.utcnow()
                    db.add(run_rec)
                    await db.commit()

                except Exception as e:
                    run_rec.status = "FAILED"
                    run_rec.error_count += 1
                    run_rec.completed_at = datetime.utcnow()
                    db.add(run_rec)
                    await db.commit()
                    logger.error(f"Discovery Sweep Task Error for query ID {query.id}: {e}")

            return {"status": "COMPLETED", "queries_executed": len(queries)}

    return run_async(_execute())
