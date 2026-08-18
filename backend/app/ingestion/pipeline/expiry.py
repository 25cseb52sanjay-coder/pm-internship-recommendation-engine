from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.db.models import Internship, AuditLog
import logging

logger = logging.getLogger(__name__)

async def run_continuous_expiry_sweep(db: AsyncSession) -> int:
    """
    Continuous soft-expiry sweep (Google Antigravity Spec Specification).
    Transitions listings past application deadline or inactive to EXPIRED state.
    Strictly prohibits hard deletion.
    """
    now_str = datetime.utcnow().strftime("%Y-%m-%d")
    
    # Query live listings past application deadline
    stmt = select(Internship).where(
        Internship.status.in_(["VERIFIED_LIVE", "DISCOVERED", "VALIDATING", "UPDATED"]),
        Internship.deadline < now_str
    )
    res = await db.execute(stmt)
    stale_listings = res.scalars().all()

    expired_count = 0
    for item in stale_listings:
        prev_status = item.status
        item.status = "EXPIRED"
        item.last_checked_at = datetime.utcnow()
        db.add(item)

        # Audit Log state transition
        audit = AuditLog(
            event_type="INTERNSHIP_EXPIRED",
            entity_name="internships",
            entity_id=item.id,
            details=f"Soft state transition: '{prev_status}' -> 'EXPIRED' (Application deadline {item.deadline} passed)."
        )
        db.add(audit)
        expired_count += 1

    if expired_count > 0:
        await db.commit()
        logger.info(f"Expiry Daemon: Successfully soft-expired {expired_count} stale internship listings.")

    return expired_count
