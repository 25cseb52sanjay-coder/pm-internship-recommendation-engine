from typing import List, Dict, Any, Optional
import json
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import StudentProfile, StudentSkill, Skill, LeetCodeProfile, CandidateEvidence

VERIFICATION_LEVEL_CONFIDENCE = {
    "SELF_DECLARED": 0.50,
    "DOCUMENTED": 0.80,
    "ASSESSED": 0.90,
    "VERIFIED_EXTERNAL": 1.00,
    "DATA_UNAVAILABLE": 0.00
}

class CandidateEvidenceService:
    """
    Unified Candidate Evidence Layer.
    Aggregates provenances, verification statuses, and confidence scores across academic records,
    self-declared profile skills, resume parsing, platform assessments, and external providers.
    """

    @staticmethod
    async def build_candidate_evidence_profile(db: AsyncSession, candidate_id: int) -> Dict[str, Any]:
        # 1. Fetch Candidate Profile & Skills
        res_st = await db.execute(select(StudentProfile).where(StudentProfile.id == candidate_id))
        student = res_st.scalar_one_or_none()
        if not student:
            return {"candidate_id": candidate_id, "evidences": [], "skill_confidence_map": {}, "status": "NOT_FOUND"}

        skills_res = await db.execute(
            select(Skill.name).join(StudentSkill, Skill.id == StudentSkill.skill_id).where(StudentSkill.student_id == candidate_id)
        )
        self_declared_skills = list(skills_res.scalars().all())

        # 2. Fetch LeetCode Profile
        res_lc = await db.execute(select(LeetCodeProfile).where(LeetCodeProfile.candidate_id == candidate_id))
        leetcode_prof = res_lc.scalar_one_or_none()

        evidences: List[Dict[str, Any]] = []

        # --- Source A: Academic Records ---
        if student.degree:
            evidences.append({
                "candidate_id": candidate_id,
                "evidence_type": "ACADEMIC",
                "value": f"Degree: {student.degree} ({student.branch or 'General'})",
                "source": "Academic Record",
                "verification_status": "DOCUMENTED",
                "confidence": VERIFICATION_LEVEL_CONFIDENCE["DOCUMENTED"],
                "metadata": {"degree": student.degree, "branch": student.branch, "cgpa": student.cgpa}
            })

        # --- Source B: Self-Declared Skills ---
        for skill_name in self_declared_skills:
            evidences.append({
                "candidate_id": candidate_id,
                "evidence_type": "SKILL",
                "value": skill_name,
                "source": "Candidate Profile",
                "verification_status": "SELF_DECLARED",
                "confidence": VERIFICATION_LEVEL_CONFIDENCE["SELF_DECLARED"],
                "metadata": {"declared_by_user": True}
            })

        # --- Source C: Resume Data / Projects ---
        if student.projects_summary or student.raw_resume_text:
            evidences.append({
                "candidate_id": candidate_id,
                "evidence_type": "RESUME",
                "value": "Parsed Resume & Projects Summary",
                "source": "Resume Parsing",
                "verification_status": "DOCUMENTED",
                "confidence": VERIFICATION_LEVEL_CONFIDENCE["DOCUMENTED"],
                "metadata": {"has_projects": bool(student.projects_summary), "has_raw_resume": bool(student.raw_resume_text)}
            })

        # --- Source D: Verified LeetCode Evidence ---
        if leetcode_prof and leetcode_prof.verification_status == "VERIFIED" and leetcode_prof.total_problems_solved is not None:
            evidences.append({
                "candidate_id": candidate_id,
                "evidence_type": "LEETCODE",
                "value": f"LeetCode Verified Profile: @{leetcode_prof.leetcode_username} ({leetcode_prof.total_problems_solved} solved)",
                "source": "LeetCode",
                "verification_status": "VERIFIED_EXTERNAL",
                "confidence": VERIFICATION_LEVEL_CONFIDENCE["VERIFIED_EXTERNAL"],
                "metadata": {
                    "username": leetcode_prof.leetcode_username,
                    "total_solved": leetcode_prof.total_problems_solved,
                    "medium_solved": leetcode_prof.medium_solved,
                    "hard_solved": leetcode_prof.hard_solved,
                    "contest_rating": leetcode_prof.contest_rating
                }
            })
        else:
            evidences.append({
                "candidate_id": candidate_id,
                "evidence_type": "LEETCODE",
                "value": "LeetCode Profile Evidence",
                "source": "LeetCode",
                "verification_status": "DATA_UNAVAILABLE",
                "confidence": VERIFICATION_LEVEL_CONFIDENCE["DATA_UNAVAILABLE"],
                "metadata": {"reason": "Provider unconfigured or profile unverified"}
            })

        # Build Skill-to-Max-Confidence Map for AI Recommendation Weighting
        skill_confidence_map: Dict[str, float] = {}
        for ev in evidences:
            if ev["evidence_type"] == "SKILL":
                s_name = ev["value"].strip()
                curr_conf = skill_confidence_map.get(s_name, 0.0)
                skill_confidence_map[s_name] = max(curr_conf, ev["confidence"])

        return {
            "candidate_id": candidate_id,
            "evidences": evidences,
            "skill_confidence_map": skill_confidence_map,
            "total_evidence_sources": len(set(e["source"] for e in evidences if e["verification_status"] != "DATA_UNAVAILABLE")),
            "status": "SUCCESS"
        }

    @staticmethod
    async def sync_candidate_profile_evidence(db: AsyncSession, candidate_id: int) -> Dict[str, Any]:
        """
        Synchronizes real candidate profile, academic, resume, certification, assessment,
        and external LeetCode records into CandidateEvidence table in PostgreSQL.
        Enforces deduplication on (candidate_id, source, evidence_type, value).
        """
        profile_summary = await CandidateEvidenceService.build_candidate_evidence_profile(db, candidate_id)
        if profile_summary.get("status") != "SUCCESS":
            return {"status": "FAILED", "reason": "Candidate profile not found"}

        evidences_to_sync = profile_summary.get("evidences", [])
        synced_count = 0
        updated_count = 0

        for item in evidences_to_sync:
            # Query existing evidence by (candidate_id, source, evidence_type, value)
            stmt = select(CandidateEvidence).where(
                CandidateEvidence.candidate_id == candidate_id,
                CandidateEvidence.source == item["source"],
                CandidateEvidence.evidence_type == item["evidence_type"],
                CandidateEvidence.value == item["value"]
            )
            res_exist = await db.execute(stmt)
            existing_rec = res_exist.scalar_one_or_none()

            meta_str = json.dumps(item.get("metadata", {}))

            if existing_rec:
                # Update existing record
                existing_rec.verification_status = item["verification_status"]
                existing_rec.confidence = item["confidence"]
                existing_rec.metadata_json = meta_str
                existing_rec.updated_at = datetime.utcnow()
                updated_count += 1
            else:
                # Insert new record
                new_rec = CandidateEvidence(
                    candidate_id=candidate_id,
                    evidence_type=item["evidence_type"],
                    value=item["value"],
                    source=item["source"],
                    verification_status=item["verification_status"],
                    confidence=item["confidence"],
                    metadata_json=meta_str,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(new_rec)
                synced_count += 1

        await db.commit()
        return {
            "candidate_id": candidate_id,
            "status": "SUCCESS",
            "inserted": synced_count,
            "updated": updated_count,
            "total_items": len(evidences_to_sync)
        }
