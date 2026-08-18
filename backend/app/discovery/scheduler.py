import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import DiscoverySearchQuery
from app.discovery.tasks import run_discovery_sweep_task

logger = logging.getLogger(__name__)

async def trigger_due_discovery_sweeps(db: AsyncSession) -> int:
    """
    Scheduler trigger executing discovery sweeps for active search queries.
    """
    res = await db.execute(select(DiscoverySearchQuery).where(DiscoverySearchQuery.enabled == True))
    queries = res.scalars().all()

    try:
        run_discovery_sweep_task.delay()
    except Exception:
        pass

    return len(queries)
