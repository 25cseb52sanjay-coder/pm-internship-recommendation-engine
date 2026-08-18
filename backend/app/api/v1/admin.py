from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List

from app.db.database import get_db
from app.db.models import Internship, Skill, InternshipSkill, ScoringWeightsConfig, User
from app.schemas.internship import InternshipCreate, InternshipOut
from app.schemas.analytics import AdminAnalyticsOut
from app.schemas.recommendation import WeightsConfigSchema
from app.api.v1.deps import get_current_admin
from app.services.analytics import get_admin_analytics

router = APIRouter()

@router.get("/analytics", response_model=AdminAnalyticsOut)
async def fetch_analytics(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    data = await get_admin_analytics(db)
    return AdminAnalyticsOut(**data)

@router.post("/internships", response_model=InternshipOut)
async def create_internship(
    data: InternshipCreate,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    internship = Internship(
        company_name=data.company_name,
        company_sector=data.company_sector,
        title=data.title,
        description=data.description,
        location=data.location,
        work_mode=data.work_mode,
        duration=data.duration,
        stipend=data.stipend,
        deadline=data.deadline,
        positions=data.positions,
        min_qualification=data.min_qualification,
        preferred_degree=data.preferred_degree,
        min_age=data.min_age,
        max_age=data.max_age
    )
    db.add(internship)
    await db.flush()

    for sk_name in data.required_skills:
        skill_res = await db.execute(select(Skill).where(Skill.name == sk_name))
        skill = skill_res.scalar_one_or_none()
        if not skill:
            skill = Skill(name=sk_name, category="Technical")
            db.add(skill)
            await db.flush()
        db.add(InternshipSkill(internship_id=internship.id, skill_id=skill.id, is_required=True))

    for sk_name in data.preferred_skills:
        skill_res = await db.execute(select(Skill).where(Skill.name == sk_name))
        skill = skill_res.scalar_one_or_none()
        if not skill:
            skill = Skill(name=sk_name, category="Technical")
            db.add(skill)
            await db.flush()
        db.add(InternshipSkill(internship_id=internship.id, skill_id=skill.id, is_required=False))

    await db.commit()
    await db.refresh(internship, ["skills"])
    for s in internship.skills:
        await db.refresh(s, ["skill"])
    return internship

@router.delete("/internships/{internship_id}")
async def delete_internship(
    internship_id: int,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(Internship).where(Internship.id == internship_id))
    item = res.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Internship not found")
    await db.delete(item)
    await db.commit()
    return {"message": "Internship deleted successfully"}

@router.get("/weights", response_model=WeightsConfigSchema)
async def get_weights(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(ScoringWeightsConfig).order_by(ScoringWeightsConfig.id.desc()))
    cfg = res.scalar_one_or_none()
    if not cfg:
        cfg = ScoringWeightsConfig()
        db.add(cfg)
        await db.commit()
        await db.refresh(cfg)
    return cfg

@router.put("/weights", response_model=WeightsConfigSchema)
async def update_weights(
    data: WeightsConfigSchema,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(ScoringWeightsConfig).order_by(ScoringWeightsConfig.id.desc()))
    cfg = res.scalar_one_or_none()
    if not cfg:
        cfg = ScoringWeightsConfig()
        db.add(cfg)

    cfg.skill_match_weight = data.skill_match_weight
    cfg.semantic_weight = data.semantic_weight
    cfg.education_weight = data.education_weight
    cfg.interest_weight = data.interest_weight
    cfg.location_weight = data.location_weight
    cfg.experience_weight = data.experience_weight
    cfg.preference_weight = data.preference_weight

    await db.commit()
    await db.refresh(cfg)
    return cfg

from pydantic import BaseModel, EmailStr
from app.core.security import get_password_hash
from app.db.models import UserRole
from sqlalchemy import func

class AdminCredentialUpdate(BaseModel):
    admin_email: EmailStr
    admin_password: str

@router.get("/credentials/status")
async def get_admin_credentials_status(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Returns current active Admin metadata in the database."""
    res = await db.execute(select(User).where(User.role == UserRole.ADMIN))
    admins = res.scalars().all()
    return {
        "status": "Active",
        "active_admin_count": len(admins),
        "authorized_admin_emails": [a.email for a in admins],
        "access_control_mode": "Strict Single/Multi Admin Database Enforcement"
    }

@router.post("/credentials/update")
async def update_admin_credentials(
    data: AdminCredentialUpdate,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Updates or provisions an Admin account with exact email and password.
    Enforces that ONLY this configured email & password combination will have Admin access.
    """
    clean_email = data.admin_email.strip().lower()
    raw_pass = data.admin_password.strip()
    if len(raw_pass) < 6:
        raise HTTPException(status_code=400, detail="Admin password must be at least 6 characters long.")

    res_admin = await db.execute(select(User).where(User.role == UserRole.ADMIN))
    existing_admins = res_admin.scalars().all()

    # Clear all previous dummy admin accounts to enforce single active admin
    await db.execute(delete(User).where(User.role == UserRole.ADMIN))
    await db.flush()

    res = await db.execute(select(User).where(func.lower(func.trim(User.email)) == clean_email))
    user = res.scalar_one_or_none()

    if not user:
        user = User(
            email=clean_email,
            password_hash=get_password_hash(raw_pass),
            full_name="Configured PM Scheme Administrator",
            role=UserRole.ADMIN,
            provider="LOCAL"
        )
        db.add(user)
    else:
        user.password_hash = get_password_hash(raw_pass)
        user.role = UserRole.ADMIN
        db.add(user)

    await db.commit()
    await db.refresh(user)

    return {
        "message": f"Successfully updated Admin credentials for '{clean_email}'. ONLY this email and password can access the Admin Portal.",
        "admin_email": user.email,
        "role": user.role,
        "status": "ENFORCED"
    }

class AdminCredentialDelete(BaseModel):
    admin_email: EmailStr

@router.delete("/credentials/delete")
async def delete_admin_credential(
    email: str,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Deletes the specified Admin account and password permanently from the database."""
    clean_email = email.strip().lower()
    res = await db.execute(select(User).where(func.lower(func.trim(User.email)) == clean_email, User.role == UserRole.ADMIN))
    user = res.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail=f"Admin account '{clean_email}' not found in database.")

    await db.delete(user)
    await db.commit()

    return {
        "message": f"Successfully deleted Admin account '{clean_email}' and purged credentials from database.",
        "deleted_email": clean_email,
        "status": "DELETED"
    }
