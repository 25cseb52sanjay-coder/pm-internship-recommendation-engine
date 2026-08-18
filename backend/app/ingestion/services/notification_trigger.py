from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Internship, Recommendation, Notification
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

async def dispatch_candidate_high_match_notifications(
    db: AsyncSession,
    internship_id: int
) -> int:
    """
    Downstream Notification Trigger Service (Google Antigravity Spec Specification).
    Dispatches notifications for candidate recommendation scores exceeding match score threshold.
    """
    res = await db.execute(select(Internship).where(Internship.id == internship_id))
    internship = res.scalar_one_or_none()
    if not internship:
        return 0

    threshold = settings.RECOMMENDATION_MATCH_THRESHOLD

    rec_res = await db.execute(
        select(Recommendation).where(
            Recommendation.internship_id == internship_id,
            Recommendation.score >= threshold
        )
    )
    high_matches = rec_res.scalars().all()

    dispatched_count = 0
    for rec in high_matches:
        # Check if notification already sent
        notif_res = await db.execute(
            select(Notification).where(
                Notification.user_id == rec.student_id,
                Notification.title.like(f"%{internship.title}%")
            )
        )
        if notif_res.scalar_one_or_none():
            continue

        notif = Notification(
            user_id=rec.student_id,
            title=f"High Match Opportunity: {internship.title}",
            message=f"You have a {rec.score}% compatibility match for '{internship.title}' at {internship.company_name} ({internship.location}).",
            notification_type="RECOMMENDATION"
        )
        db.add(notif)
        dispatched_count += 1

    if dispatched_count > 0:
        await db.commit()
        logger.info(f"Notification Trigger: Dispatched {dispatched_count} high-match notifications for internship ID {internship_id}.")

    return dispatched_count
