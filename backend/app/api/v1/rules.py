from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.db.database import get_db
from app.db.models import SchemeRule
from app.api.v1.deps import get_current_admin
from app.services.eligibility import DynamicEligibilityService

router = APIRouter()

class SchemeRuleCreateRequest(BaseModel):
    rule_code: str
    rule_name: str
    rule_version: str = "v1.0"
    min_age: int = 21
    max_age: int = 24
    mandatory_degree: Optional[str] = None
    is_active: bool = True

@router.get("/active")
async def get_active_rule(db: AsyncSession = Depends(get_db)):
    """Fetch active versioned scheme eligibility rule configuration."""
    rule = await DynamicEligibilityService.get_active_scheme_rule(db)
    return rule

@router.post("/configure")
async def configure_scheme_rule(
    req: SchemeRuleCreateRequest,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(get_current_admin)
):
    """
    Configurable Rules Engine API (PDF Section 2 & 4 Specification).
    Allows administrators to dynamically version and update eligibility rules without hardcoding constants.
    """
    if req.min_age >= req.max_age:
        raise HTTPException(status_code=400, detail="min_age must be strictly less than max_age")

    # If new rule is set to active, deactivate previous rules
    if req.is_active:
        res = await db.execute(select(SchemeRule).where(SchemeRule.is_active == True))
        active_rules = res.scalars().all()
        for r in active_rules:
            r.is_active = False
            db.add(r)

    new_rule = SchemeRule(
        rule_code=req.rule_code,
        rule_name=req.rule_name,
        rule_version=req.rule_version,
        min_age=req.min_age,
        max_age=req.max_age,
        mandatory_degree=req.mandatory_degree,
        is_active=req.is_active
    )
    db.add(new_rule)
    await db.commit()
    await db.refresh(new_rule)

    return {
        "status": "SUCCESS",
        "message": f"Successfully published scheme rule version {new_rule.rule_version} ({new_rule.rule_code}).",
        "active_rule": new_rule
    }
