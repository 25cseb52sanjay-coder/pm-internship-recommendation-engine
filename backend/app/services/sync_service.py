import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import AsyncSessionLocal
from app.core.config import settings
from app.greenhouse.sync_service import GreenhouseSyncService
from app.services.adzuna import AdzunaService

logger = logging.getLogger(__name__)

class OpportunitySyncService:
    """
    Centralized Background Opportunity Synchronization Service (Task 23 Specification).
    Periodically synchronizes real opportunities from Greenhouse and Adzuna into PostgreSQL database.
    - Non-blocking: Runs in background without stalling web requests.
    - Isolated: Errors in one source do not block other sources.
    - Idempotent: Applies Task 21 quality gate & deduplication.
    - Dormant NCS: NCS sync is skipped / remains dormant because no authorized API key is configured.
    """

    _sync_lock = asyncio.Lock()
    _scheduler_task: Optional[asyncio.Task] = None
    _is_running: bool = False

    @staticmethod
    def get_sync_interval_seconds() -> int:
        return getattr(settings, "SYNC_INTERVAL_SECONDS", int(getattr(settings, "DISCOVERY_INTERVAL_SECONDS", 1800)))

    @staticmethod
    async def run_full_sync() -> Dict[str, Any]:
        """
        Executes a complete background synchronization run across all active configured sources.
        Guarantees concurrency isolation so overlapping sync jobs cannot run simultaneously.
        """
        if OpportunitySyncService._sync_lock.locked():
            logger.warning("OpportunitySyncService sync already in progress. Skipping overlapping run.")
            return {
                "status": "SKIPPED_OVERLAPPING",
                "timestamp": datetime.utcnow().isoformat(),
                "message": "A synchronization run is currently active. Overlapping execution prevented."
            }

        async with OpportunitySyncService._sync_lock:
            start_time = datetime.utcnow()
            results: Dict[str, Any] = {
                "start_time": start_time.isoformat(),
                "sources": {},
                "status": "SUCCESS"
            }

            async with AsyncSessionLocal() as db:
                # 1. Greenhouse Sync Execution
                try:
                    gh_res = await GreenhouseSyncService.run_full_greenhouse_sync(db)
                    results["sources"]["Greenhouse"] = {"status": "SUCCESS", "details": gh_res}
                except Exception as e:
                    logger.error(f"Greenhouse background sync failure: {str(e)}", exc_info=True)
                    results["sources"]["Greenhouse"] = {"status": "FAILED", "error": str(e)}
                    results["status"] = "PARTIAL_SUCCESS"

                # 2. Adzuna Sync Execution
                try:
                    if AdzunaService.is_configured():
                        adz_res = await AdzunaService.sync_adzuna_opportunities(db)
                        results["sources"]["Adzuna"] = {"status": "SUCCESS", "details": adz_res}
                    else:
                        results["sources"]["Adzuna"] = {
                            "status": "CONFIGURED_BUT_NOT_LIVE",
                            "message": "Adzuna credentials (ADZUNA_APP_ID, ADZUNA_APP_KEY) not configured in environment."
                        }
                except Exception as e:
                    logger.error(f"Adzuna background sync failure: {str(e)}", exc_info=True)
                    results["sources"]["Adzuna"] = {"status": "FAILED", "error": str(e)}
                    results["status"] = "PARTIAL_SUCCESS"

                # 3. Lever Sync Execution
                try:
                    from app.lever.sync_service import LeverSyncService
                    lever_res = await LeverSyncService.run_full_lever_sync(db)
                    results["sources"]["Lever"] = {"status": "SUCCESS", "details": lever_res}
                except Exception as e:
                    logger.error(f"Lever background sync failure: {str(e)}", exc_info=True)
                    results["sources"]["Lever"] = {"status": "FAILED", "error": str(e)}
                    results["status"] = "PARTIAL_SUCCESS"

                # 4. Jobvetta Sync Execution
                try:
                    from app.jobvetta.sync_service import JobvettaSyncService
                    jv_res = await JobvettaSyncService.run_full_jobvetta_sync(db)
                    results["sources"]["Jobvetta"] = {"status": "SUCCESS", "details": jv_res}
                except Exception as e:
                    logger.error(f"Jobvetta background sync failure: {str(e)}", exc_info=True)
                    results["sources"]["Jobvetta"] = {"status": "FAILED", "error": str(e)}
                    results["status"] = "PARTIAL_SUCCESS"

                # 5. NCS Sync Execution (Dormant Architecture Preservation)
                results["sources"]["NCS"] = {
                    "status": "DORMANT",
                    "message": "NCS API integration is dormant. Live ingestion requires restricted institutional API authorization."
                }

            end_time = datetime.utcnow()
            results["end_time"] = end_time.isoformat()
            results["duration_seconds"] = round((end_time - start_time).total_seconds(), 2)

            return results

    @staticmethod
    async def _background_scheduler_loop():
        """
        Background scheduler loop running at configured SYNC_INTERVAL_SECONDS.
        """
        interval = OpportunitySyncService.get_sync_interval_seconds()
        logger.info(f"Started OpportunitySyncService background scheduler loop (Interval: {interval}s).")
        
        while OpportunitySyncService._is_running:
            try:
                if OpportunitySyncService._is_running:
                    await OpportunitySyncService.run_full_sync()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                logger.info("OpportunitySyncService background scheduler loop cancelled.")
                break
            except Exception as e:
                logger.error(f"OpportunitySyncService scheduler loop error: {str(e)}", exc_info=True)

    @classmethod
    def start_scheduler(cls):
        """Starts background periodic synchronization task if not already running."""
        if not cls._is_running:
            cls._is_running = True
            cls._scheduler_task = asyncio.create_task(cls._background_scheduler_loop())

    @classmethod
    def stop_scheduler(cls):
        """Stops background periodic synchronization task gracefully."""
        if cls._is_running:
            cls._is_running = False
            if cls._scheduler_task:
                cls._scheduler_task.cancel()
                cls._scheduler_task = None
