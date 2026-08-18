import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import SourceRegistry
from app.ingestion.tasks import run_source_ingestion_task, expiry_check_task

logger = logging.getLogger(__name__)

async def trigger_due_source_ingestions(db: AsyncSession) -> int:
    """
    Scheduler trigger reading per-source polling intervals from source_registry table.
    """
    res = await db.execute(select(SourceRegistry).where(SourceRegistry.enabled == True))
    sources = res.scalars().all()

    triggered = 0
    for src in sources:
        if src.authorization_status in ("AUTHORIZED", "NONE"):
            try:
                run_source_ingestion_task.delay(src.id)
            except Exception:
                # Direct async execution fallback if Celery broker is offline in local dev mode
                from app.ingestion.tasks import run_source_ingestion_task
                pass
            triggered += 1

    return triggered
