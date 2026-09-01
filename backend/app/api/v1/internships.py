from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.db.database import get_db
from app.db.models import Internship, SavedInternship, Application, ApplicationStatus, StudentProfile, InternshipSkill
from app.schemas.internship import InternshipOut
from app.api.v1.deps import get_current_student, get_current_user

router = APIRouter()

@router.get("", response_model=List[InternshipOut])
async def list_internships(
    sector: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    work_mode: Optional[str] = Query(None),
    source: Optional[str] = Query(None, description="Filter by internship data source: All, NCS, PMIS, Greenhouse, Company Careers"),
    opportunity_type: Optional[str] = Query(None, description="Filter by opportunity classification: All, Jobs, Internships"),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1, description="Page number for pagination (Point 14 Specification)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page limit"),
    sort_by: Optional[str] = Query("newest", description="Sort order: newest, deadline, stipend"),
    db: AsyncSession = Depends(get_db)
):
    # Strict VERIFIED_LIVE Filtering with Eager Loading (High-Performance Query Execution)
    stmt = select(Internship).options(
        selectinload(Internship.skills).selectinload(InternshipSkill.skill)
    ).where(
        Internship.status == "VERIFIED_LIVE",
        Internship.verification_status == "VERIFIED",
        Internship.is_demo == False
    )
    if sector and isinstance(sector, str) and sector != "All":
        stmt = stmt.where(Internship.company_sector == sector)
    if location and isinstance(location, str) and location != "All":
        stmt = stmt.where(Internship.location.ilike(f"%{location}%"))
    if work_mode and isinstance(work_mode, str) and work_mode != "All":
        stmt = stmt.where(Internship.work_mode == work_mode)
    if source and isinstance(source, str) and source != "All":
        if source.upper() == "NCS":
            stmt = stmt.where(
                or_(
                    Internship.source == "NCS",
                    Internship.source_url.ilike("%ncs.gov.in%"),
                    Internship.apply_url.ilike("%ncs.gov.in%")
                )
            )
        else:
            stmt = stmt.where(Internship.source.ilike(f"%{source}%"))
    if opportunity_type and isinstance(opportunity_type, str) and opportunity_type != "All":
        if opportunity_type.lower() in ("jobs", "job"):
            stmt = stmt.where(Internship.opportunity_type == "JOB")
        elif opportunity_type.lower() in ("internships", "internship"):
            stmt = stmt.where(Internship.opportunity_type == "INTERNSHIP")
    if search and isinstance(search, str):
        stmt = stmt.where(
            (Internship.title.ilike(f"%{search}%")) |
            (Internship.company_name.ilike(f"%{search}%")) |
            (Internship.description.ilike(f"%{search}%"))
        )

    # Sorting
    if sort_by == "newest":
        stmt = stmt.order_by(Internship.created_at.desc())
    elif sort_by == "deadline":
        stmt = stmt.order_by(Internship.deadline.asc())

    # Pagination Offset & Limit (Point 14 Specification)
    offset = (page - 1) * limit
    stmt = stmt.offset(offset).limit(limit)

    res = await db.execute(stmt)
    internships = res.scalars().all()
    output = []
    for item in internships:
        skill_list = []
        for s in item.skills:
            skill_list.append({
                "id": s.skill_id,
                "name": s.skill.name if s.skill else "General Skill",
                "is_required": s.is_required
            })
        item_dict = {
            "id": item.id,
            "company_name": item.company_name,
            "company_sector": item.company_sector,
            "title": item.title,
            "description": item.description,
            "location": item.location,
            "work_mode": item.work_mode,
            "duration": item.duration,
            "stipend": item.stipend,
            "deadline": item.deadline,
            "positions": item.positions,
            "min_qualification": item.min_qualification,
            "preferred_degree": item.preferred_degree,
            "min_age": item.min_age,
            "max_age": item.max_age,
            "skills": skill_list,
            "source": item.source or ("Adzuna" if item.source == "Adzuna" else ("Lever" if item.source == "Lever" else ("Greenhouse" if item.source == "Greenhouse" else ("NCS" if "ncs.gov.in" in (item.source_url or "") else "PMIS")))),
            "source_name": "Adzuna Official API" if item.source == "Adzuna" else ("Greenhouse Official" if item.source == "Greenhouse" else ("Lever Official" if item.source == "Lever" else ("National Career Service (NCS)" if (item.source == "NCS" or "ncs.gov.in" in (item.source_url or "")) else "PM Scheme Official"))),
            "opportunity_type": item.opportunity_type or "INTERNSHIP",
            "apply_url": item.apply_url or item.source_url or (f"https://www.adzuna.in/details/{item.external_id}" if item.source == "Adzuna" and item.external_id else None),
            "application_url": item.apply_url or item.source_url or (f"https://www.adzuna.in/details/{item.external_id}" if item.source == "Adzuna" and item.external_id else None),
            "external_id": item.external_id,
            "created_at": item.created_at
        }
        output.append(item_dict)
    return output

@router.get("/{internship_id}", response_model=InternshipOut)
async def get_internship_detail(internship_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Internship).where(Internship.id == internship_id))
    item = res.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Internship opportunity not found")
    await db.refresh(item, ["skills"])
    skill_list = []
    for s in item.skills:
        await db.refresh(s, ["skill"])
        skill_list.append({
            "id": s.skill_id,
            "name": s.skill.name if s.skill else "General Skill",
            "is_required": s.is_required
        })
    return {
        "id": item.id,
        "company_name": item.company_name,
        "company_sector": item.company_sector,
        "title": item.title,
        "description": item.description,
        "location": item.location,
        "work_mode": item.work_mode,
        "duration": item.duration,
        "stipend": item.stipend,
        "deadline": item.deadline,
        "positions": item.positions,
        "min_qualification": item.min_qualification,
        "preferred_degree": item.preferred_degree,
        "min_age": item.min_age,
        "max_age": item.max_age,
        "skills": skill_list,
        "source": item.source or ("Adzuna" if item.source == "Adzuna" else ("Lever" if item.source == "Lever" else ("Greenhouse" if item.source == "Greenhouse" else ("NCS" if "ncs.gov.in" in (item.source_url or "") else "PMIS")))),
        "source_name": "Adzuna Official API" if item.source == "Adzuna" else ("Greenhouse Official" if item.source == "Greenhouse" else ("Lever Official" if item.source == "Lever" else ("National Career Service (NCS)" if (item.source == "NCS" or "ncs.gov.in" in (item.source_url or "")) else "PM Scheme Official"))),
        "opportunity_type": item.opportunity_type or "INTERNSHIP",
        "apply_url": item.apply_url or item.source_url or (f"https://www.adzuna.in/details/{item.external_id}" if item.source == "Adzuna" and item.external_id else None),
        "application_url": item.apply_url or item.source_url or (f"https://www.adzuna.in/details/{item.external_id}" if item.source == "Adzuna" and item.external_id else None),
        "external_id": item.external_id,
        "created_at": item.created_at
    }

@router.post("/{internship_id}/save")
async def save_internship(
    internship_id: int,
    student: StudentProfile = Depends(get_current_student),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(SavedInternship).where(
        SavedInternship.student_id == student.id,
        SavedInternship.internship_id == internship_id
    ))
    existing = res.scalar_one_or_none()
    if existing:
        return {"message": "Internship already saved"}
        
    saved = SavedInternship(student_id=student.id, internship_id=internship_id)
    db.add(saved)
    await db.commit()
    return {"message": "Internship saved successfully"}

@router.post("/{internship_id}/apply")
async def apply_internship(
    internship_id: int,
    student: StudentProfile = Depends(get_current_student),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(Application).where(
        Application.student_id == student.id,
        Application.internship_id == internship_id
    ))
    existing = res.scalar_one_or_none()
    if existing:
        return {"message": "Application already submitted for this internship"}
        
    app = Application(
        student_id=student.id,
        internship_id=internship_id,
        status=ApplicationStatus.APPLIED
    )
    db.add(app)
    await db.commit()
    return {"message": "Application submitted successfully under PM Internship Scheme"}
