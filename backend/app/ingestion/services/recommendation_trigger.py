from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Internship, StudentProfile, Recommendation, Skill, StudentSkill
from app.services.recommendation import generate_recommendation_for_student
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

async def trigger_candidate_recommendation_refresh(
    db: AsyncSession,
    internship_id: int
) -> int:
    """
    Downstream Integration Service (Google Antigravity Spec Specification).
    Evaluates candidate hard eligibility and AI compatibility scores when a new
    or updated internship is ingested.
    """
    res = await db.execute(select(Internship).where(Internship.id == internship_id))
    internship = res.scalar_one_or_none()
    if not internship:
        return 0

    await db.refresh(internship, ["skills"])
    for s in internship.skills:
        await db.refresh(s, ["skill"])

    # Query all active student profiles
    stud_res = await db.execute(select(StudentProfile))
    students = stud_res.scalars().all()

    processed_count = 0
    for student in students:
        await db.refresh(student, ["skills"])
        sk_res = await db.execute(
            select(Skill.name).join(StudentSkill, Skill.id == StudentSkill.skill_id)
            .where(StudentSkill.student_id == student.id)
        )
        cand_skills = list(sk_res.scalars().all())

        score, match_category, explanation = generate_recommendation_for_student(
            student=student,
            internship=internship,
            student_skills=cand_skills
        )

        # Upsert recommendation record
        rec_res = await db.execute(
            select(Recommendation).where(
                Recommendation.student_id == student.id,
                Recommendation.internship_id == internship.id
            )
        )
        rec = rec_res.scalar_one_or_none()
        if not rec:
            rec = Recommendation(
                student_id=student.id,
                internship_id=internship.id,
                score=score,
                match_category=match_category,
                explanation_json=explanation,
                algorithm_version="OPT_ALLOCATOR_V2.0"
            )
            db.add(rec)
        else:
            rec.score = score
            rec.match_category = match_category
            rec.explanation_json = explanation
            db.add(rec)

        processed_count += 1

    await db.commit()
    logger.info(f"Recommendation Trigger: Processed candidate matching for internship ID {internship_id} ({processed_count} candidates evaluated).")
    return processed_count
