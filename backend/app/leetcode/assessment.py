import logging
from typing import Dict, Any, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import LeetCodeProfile
from app.leetcode.metrics_service import LeetCodeMetricsService

logger = logging.getLogger(__name__)

class LeetCodeSkillAssessmentService:
    """
    Explainable Skill Assessment Engine for verified LeetCode profile metrics.
    Evaluates coding capability across 7 dimensions without single-score reduction
    or arbitrary candidate rejection.
    """

    @staticmethod
    async def evaluate_candidate(
        db: AsyncSession,
        candidate_id: int
    ) -> Dict[str, Any]:
        """
        Evaluates a candidate's verified LeetCode coding capability across 7 dimensions:
        1. problem_solving_exposure
        2. difficulty_progression
        3. algorithmic_skill
        4. programming_language_experience
        5. competitive_programming
        6. topic_strength
        7. recent_activity
        
        Strict Non-Negotiable Rules:
        - Only evaluates verified profiles (verification_status == VERIFIED).
        - Never claims skills unsupported by evidence.
        - Never rates a candidate as expert solely for solving easy problems.
        - Never uses LeetCode metrics as sole eligibility criterion or for automatic rejection.
        """
        stmt = select(LeetCodeProfile).where(LeetCodeProfile.candidate_id == candidate_id)
        res = await db.execute(stmt)
        lc_prof = res.scalar_one_or_none()

        if not lc_prof:
            return {
                "assessment_status": "DATA_UNAVAILABLE",
                "candidate_id": candidate_id,
                "confidence": "NONE",
                "strengths": [],
                "areas_to_improve": ["Connect your verified LeetCode profile to highlight coding background."],
                "language_strengths": [],
                "topic_strengths": [],
                "difficulty_profile": {"easy": None, "medium": None, "hard": None, "ratio_medium_hard": None},
                "evidence": {},
                "explanation": "No LeetCode profile linked."
            }

        # Rule 1: Only evaluate VERIFIED profiles as verified candidates
        if lc_prof.verification_status != "VERIFIED" or lc_prof.ownership_status != "VERIFIED":
            return {
                "assessment_status": "UNVERIFIED_CANDIDATE",
                "candidate_id": candidate_id,
                "leetcode_username": lc_prof.leetcode_username,
                "confidence": "NONE",
                "strengths": [],
                "areas_to_improve": ["Complete ownership verification to link your LeetCode metrics."],
                "language_strengths": [],
                "topic_strengths": [],
                "difficulty_profile": {"easy": None, "medium": None, "hard": None, "ratio_medium_hard": None},
                "evidence": {},
                "explanation": f"Profile '@{lc_prof.leetcode_username}' is unverified. Assessment requires verified profile ownership."
            }

        # Fetch candidate metrics
        metrics_res = await LeetCodeMetricsService.get_candidate_metrics(db, candidate_id)
        
        if metrics_res["data_status"] not in ("AVAILABLE", "STALE") or not metrics_res.get("metrics"):
            return {
                "assessment_status": "DATA_UNAVAILABLE",
                "candidate_id": candidate_id,
                "leetcode_username": lc_prof.leetcode_username,
                "confidence": "LOW",
                "strengths": [f"Verified ownership of LeetCode profile @{lc_prof.leetcode_username}."],
                "areas_to_improve": ["Sync metrics when a live LeetCode data provider becomes active."],
                "language_strengths": [],
                "topic_strengths": [],
                "difficulty_profile": {"easy": None, "medium": None, "hard": None, "ratio_medium_hard": None},
                "evidence": {
                    "verification_status": "VERIFIED",
                    "ownership_verified_at": lc_prof.verified_at.isoformat() if lc_prof.verified_at else None
                },
                "explanation": "Profile ownership verified, but detailed problem statistics are currently unavailable from provider."
            }

        # Metrics are legitimately available from verified profile
        m = metrics_res["metrics"]

        # Parse metrics safely without inventing missing values
        total_solved = m.get("total_problems_solved")
        easy_solved = m.get("easy_solved")
        medium_solved = m.get("medium_solved")
        hard_solved = m.get("hard_solved")
        languages = m.get("languages") or {}
        skills = m.get("skills") or []
        badges = m.get("badges") or []
        contest_rating = m.get("contest_rating")
        contest_rank = m.get("contest_rank")
        recent_activity = m.get("recent_activity") or []

        strengths: List[str] = []
        areas_to_improve: List[str] = []
        language_strengths: List[Dict[str, Any]] = []
        topic_strengths: List[str] = []
        evidence: Dict[str, Any] = {
            "verified_handle": lc_prof.leetcode_username,
            "verification_method": lc_prof.verification_method,
            "data_freshness": metrics_res["data_status"]
        }

        # Dimension 1 & 2: Problem Solving Exposure & Difficulty Progression
        medium_hard_count = 0
        if easy_solved is not None:
            evidence["easy_solved"] = easy_solved
        if medium_solved is not None:
            evidence["medium_solved"] = medium_solved
            medium_hard_count += medium_solved
        if hard_solved is not None:
            evidence["hard_solved"] = hard_solved
            medium_hard_count += hard_solved

        if total_solved is not None:
            evidence["total_problems_solved"] = total_solved

            if total_solved >= 300 and medium_hard_count >= 100:
                strengths.append(f"Strong problem-solving track record ({total_solved} total solved, {medium_hard_count} Medium/Hard).")
            elif total_solved >= 100:
                strengths.append(f"Consistent problem-solving exposure ({total_solved} total problems solved).")
            elif total_solved > 0:
                strengths.append(f"Demonstrated coding practice ({total_solved} problems solved).")
                areas_to_improve.append("Expand problem-solving volume across data structure topics.")

            # Rule: Don't call student expert solely for easy problems
            if easy_solved is not None and (total_solved - easy_solved == 0) and total_solved >= 30:
                areas_to_improve.append("Transition to Medium-difficulty problems to build algorithmic depth.")

        # Dimension 3: Algorithmic Skill / Difficulty Profile
        ratio_str = None
        if medium_solved is not None and hard_solved is not None and easy_solved is not None:
            total_calc = easy_solved + medium_solved + hard_solved
            if total_calc > 0:
                med_hard_pct = round(((medium_solved + hard_solved) / total_calc) * 100, 1)
                ratio_str = f"{med_hard_pct}% Medium/Hard"
                if med_hard_pct >= 40:
                    strengths.append(f"High algorithmic depth ({med_hard_pct}% of solved problems are Medium or Hard).")

        difficulty_profile = {
            "easy": easy_solved,
            "medium": medium_solved,
            "hard": hard_solved,
            "ratio_medium_hard": ratio_str
        }

        # Dimension 4: Programming Language Experience (only from real data)
        if isinstance(languages, dict) and len(languages) > 0:
            for lang, count in languages.items():
                language_strengths.append({"language": lang, "solved_count": count})
                evidence[f"lang_{lang}"] = count
            top_lang = max(languages.items(), key=lambda x: x[1])
            strengths.append(f"Primary implementation language: {top_lang[0]} ({top_lang[1]} problems).")

        # Dimension 5: Competitive Programming
        if contest_rating is not None:
            evidence["contest_rating"] = contest_rating
            if contest_rank is not None:
                evidence["contest_rank"] = contest_rank
            strengths.append(f"Active contest participant (Contest Rating: {contest_rating}).")

        # Dimension 6: Topic Strength
        if isinstance(skills, list) and len(skills) > 0:
            topic_strengths = skills
            evidence["topics_verified"] = skills
            strengths.append(f"Verified proficiency in key topics: {', '.join(skills[:3])}.")

        # Dimension 7: Recent Activity
        if isinstance(recent_activity, list) and len(recent_activity) > 0:
            evidence["recent_activity_count"] = len(recent_activity)
            strengths.append("Active recent coding activity on platform.")

        confidence = "HIGH" if (total_solved is not None and total_solved >= 100 and len(language_strengths) > 0) else ("MEDIUM" if total_solved else "LOW")

        return {
            "assessment_status": "VERIFIED_ASSESSMENT",
            "candidate_id": candidate_id,
            "leetcode_username": lc_prof.leetcode_username,
            "confidence": confidence,
            "strengths": strengths,
            "areas_to_improve": areas_to_improve,
            "language_strengths": language_strengths,
            "topic_strengths": topic_strengths,
            "difficulty_profile": difficulty_profile,
            "evidence": evidence,
            "explanation": f"Explainable skill assessment generated from verified LeetCode profile @{lc_prof.leetcode_username}."
        }
