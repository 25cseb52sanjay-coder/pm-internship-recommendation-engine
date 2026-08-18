from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import SchemeRule, StudentProfile, EligibilityResult

class DynamicEligibilityService:
    """
    Dynamic Configurable Scheme Eligibility Engine (PDF Section 2 & 4 Specification)
    Hard filter evaluating candidate profile attributes deterministically against versioned scheme rules.
    """

    @staticmethod
    async def get_active_scheme_rule(db: AsyncSession) -> SchemeRule:
        """Fetch active scheme rule from scheme_rules table, or initialize default PMIS v1.0 rule."""
        res = await db.execute(select(SchemeRule).where(SchemeRule.is_active == True))
        active_rule = res.scalars().first()

        if not active_rule:
            active_rule = SchemeRule(
                rule_code="PMIS_DEFAULT_RULE_V1",
                rule_name="Prime Minister's Internship Scheme Official Eligibility Criteria",
                rule_version="v1.0",
                min_age=21,
                max_age=24,
                mandatory_degree=None,
                is_active=True
            )
            db.add(active_rule)
            await db.commit()
            await db.refresh(active_rule)

        return active_rule

    @staticmethod
    async def evaluate_student_eligibility(
        db: AsyncSession,
        student_id: int,
        rule_override: Optional[SchemeRule] = None
    ) -> Dict[str, Any]:
        """
        Evaluates candidate hard eligibility deterministically against active versioned scheme rules.
        Saves determination outcome into eligibility_results database table.
        """
        # Fetch candidate profile
        prof_res = await db.execute(select(StudentProfile).where(StudentProfile.id == student_id))
        profile = prof_res.scalar_one_or_none()

        if not profile:
            return {
                "is_eligible": False,
                "eligibility_status": "PROFILE_NOT_FOUND",
                "age_valid": False,
                "qualification_valid": False,
                "reasons": ["Candidate profile does not exist."]
            }

        # Fetch active rule configuration
        rule = rule_override or await DynamicEligibilityService.get_active_scheme_rule(db)

        # 1. Age Verification (Must be within min_age and max_age)
        candidate_age = profile.age or 22
        age_valid = (rule.min_age <= candidate_age <= rule.max_age)

        # 2. Qualification Verification
        qual = (profile.qualification or "").strip().lower()
        degree = (profile.degree or "").strip().lower()
        qualification_valid = True
        
        if rule.mandatory_degree and rule.mandatory_degree.strip():
            target_deg = rule.mandatory_degree.strip().lower()
            qualification_valid = (target_deg in qual or target_deg in degree)

        # Overall Hard Eligibility Determination
        is_eligible = age_valid and qualification_valid
        
        reasons = []
        if not age_valid:
            reasons.append(f"Candidate age ({candidate_age}) outside official PM Scheme limits ({rule.min_age}–{rule.max_age} years).")
        if not qualification_valid:
            reasons.append(f"Candidate degree ({profile.degree}) does not satisfy mandatory requirement ({rule.mandatory_degree}).")

        eligibility_status = "ELIGIBLE" if is_eligible else "INELIGIBLE"

        # Record determination in eligibility_results table
        res_record = await db.execute(
            select(EligibilityResult).where(EligibilityResult.student_id == student_id)
        )
        existing_result = res_record.scalar_one_or_none()

        if existing_result:
            existing_result.is_eligible = is_eligible
            existing_result.eligibility_status = eligibility_status
            existing_result.age_valid = age_valid
            existing_result.qualification_valid = qualification_valid
            existing_result.checked_at = datetime.utcnow()
            db.add(existing_result)
        else:
            new_result = EligibilityResult(
                student_id=student_id,
                is_eligible=is_eligible,
                eligibility_status=eligibility_status,
                age_valid=age_valid,
                qualification_valid=qualification_valid,
                checked_at=datetime.utcnow()
            )
            db.add(new_result)

        await db.commit()

        return {
            "student_id": student_id,
            "is_eligible": is_eligible,
            "eligibility_status": eligibility_status,
            "age_valid": age_valid,
            "qualification_valid": qualification_valid,
            "rule_code": rule.rule_code,
            "rule_version": rule.rule_version,
            "reasons": reasons if reasons else ["Meets all official scheme eligibility parameters."]
        }
