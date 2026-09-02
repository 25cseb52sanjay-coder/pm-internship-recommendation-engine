import os
import time
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from typing import List

from app.db.database import get_db
from app.db.models import User, StudentProfile, Skill, StudentSkill, Internship, ScoringWeightsConfig, RecommendationFeedback, FeedbackType, Recommendation, InternshipSkill
from app.schemas.student import StudentProfileCreate, StudentProfileOut, SkillGapOut, FeedbackCreate, SkillBase
from app.schemas.recommendation import RecommendationOut, RecommendationExplanation
from app.api.v1.deps import get_current_student, get_current_user
from app.services.resume_parser import parse_resume_file, sync_student_education_record
from app.services.recommendation import generate_recommendation_for_student, check_eligibility, build_skill_gap_analysis, _RECOMMENDATION_CACHE, CACHE_TTL_SECONDS
from app.core.config import settings

router = APIRouter()

@router.get("/profile", response_model=StudentProfileOut)
async def get_profile(
    student: StudentProfile = Depends(get_current_student),
    db: AsyncSession = Depends(get_db)
):
    user_res = await db.execute(select(User).where(User.id == student.user_id))
    user = user_res.scalar_one_or_none()
    user_name = user.full_name if user else ""

    skills_res = await db.execute(
        select(Skill.id, Skill.name, Skill.category, StudentSkill.proficiency_level)
        .join(StudentSkill, Skill.id == StudentSkill.skill_id)
        .where(StudentSkill.student_id == student.id)
    )
    skills = [
        {"id": r[0], "name": r[1], "category": r[2], "proficiency_level": r[3]}
        for r in skills_res.all()
    ]

    # Fetch candidate's LeetCode Profile
    from app.db.models import LeetCodeProfile
    lc_prof_res = await db.execute(select(LeetCodeProfile).where(LeetCodeProfile.candidate_id == student.id))
    leetcode_prof = lc_prof_res.scalar_one_or_none()

    leetcode_username = None
    leetcode_verification_status = "NOT_CONNECTED"
    leetcode_metrics_status = "NOT_AVAILABLE"
    leetcode_total_solved = None
    leetcode_easy_solved = None
    leetcode_medium_solved = None
    leetcode_hard_solved = None
    leetcode_badges = None
    leetcode_contest_rating = None

    if leetcode_prof:
        leetcode_username = leetcode_prof.leetcode_username
        leetcode_verification_status = leetcode_prof.verification_status
        from app.leetcode.metrics_service import LeetCodeMetricsService
        # Read from DB first (cached)
        m_res = await LeetCodeMetricsService.get_candidate_metrics(db, student.id)

        # Fetch from LeetCode only if metrics missing or stale (>24 hours)
        if not m_res.get("metrics") or m_res.get("data_status") == "STALE":
            m_res = await LeetCodeMetricsService.fetch_and_update_metrics(db, student.id)

        if m_res.get("metrics"):
            metrics = m_res["metrics"]
            leetcode_metrics_status = "SUCCESS"
            leetcode_total_solved = metrics.get("total_problems_solved")
            leetcode_easy_solved = metrics.get("easy_solved")
            leetcode_medium_solved = metrics.get("medium_solved")
            leetcode_hard_solved = metrics.get("hard_solved")
            leetcode_badges = metrics.get("badges")
            leetcode_contest_rating = metrics.get("contest_rating")
        else:
            leetcode_metrics_status = "UNAVAILABLE"

    return {
        "id": student.id,
        "user_id": student.user_id,
        "full_name": user_name,
        "name": user_name,
        "phone": student.phone,
        "age": student.age,
        "qualification": student.qualification,
        "degree": student.degree,
        "course_program": student.course_program,
        "qualification_type": student.qualification_type,
        "branch": student.branch,
        "institution": student.institution,
        "graduation_year": student.graduation_year,
        "cgpa": student.cgpa,
        "preferred_industry": student.preferred_industry,
        "preferred_role": student.preferred_role,
        "preferred_location": student.preferred_location,
        "work_mode": student.work_mode,
        "preferred_duration": student.preferred_duration,
        "resume_url": (
            "/uploads/" + student.resume_url.split("/uploads/")[-1]
            if student.resume_url and "/uploads/" in student.resume_url
            else student.resume_url
        ),
        "projects_summary": student.projects_summary,
        "skills": skills,
        "leetcode_username": leetcode_username,
        "leetcode_verification_status": leetcode_verification_status,
        "leetcode_metrics_status": leetcode_metrics_status,
        "leetcode_total_solved": leetcode_total_solved,
        "leetcode_easy_solved": leetcode_easy_solved,
        "leetcode_medium_solved": leetcode_medium_solved,
        "leetcode_hard_solved": leetcode_hard_solved,
        "leetcode_badges": leetcode_badges,
        "leetcode_contest_rating": leetcode_contest_rating
    }

@router.post("/profile")
async def update_profile(
    profile_in: StudentProfileCreate,
    student: StudentProfile = Depends(get_current_student),
    db: AsyncSession = Depends(get_db)
):
    name_to_update = profile_in.full_name or profile_in.name
    if name_to_update:
        user_res = await db.execute(select(User).where(User.id == student.user_id))
        user = user_res.scalar_one_or_none()
        if user:
            user.full_name = name_to_update.strip()
            await db.flush()

    for field, val in profile_in.model_dump(exclude_unset=True).items():
        if field not in ("skills", "full_name", "name") and hasattr(student, field):
            setattr(student, field, val)

    if profile_in.skills is not None:
        await db.execute(delete(StudentSkill).where(StudentSkill.student_id == student.id))
        for sk_item in profile_in.skills:
            skill_name_clean = ""
            skill_category_clean = "General"
            
            # Handle various incoming formats (str, dict, models)
            if isinstance(sk_item, str):
                skill_name_clean = sk_item.strip()
            elif isinstance(sk_item, dict):
                skill_name_clean = (
                    sk_item.get("skill", "").strip()
                    or sk_item.get("display_skill", "").strip()
                    or sk_item.get("name", "").strip()
                )
                skill_category_clean = (
                    sk_item.get("category", "").strip()
                    or sk_item.get("display_category", "").strip()
                    or "General"
                )
            elif hasattr(sk_item, "name"):
                skill_name_clean = sk_item.name.strip()
                if hasattr(sk_item, "category") and sk_item.category:
                    skill_category_clean = sk_item.category.strip()
            elif hasattr(sk_item, "skill"):
                skill_name_clean = sk_item.skill.strip()
                if hasattr(sk_item, "category") and sk_item.category:
                    skill_category_clean = sk_item.category.strip()

            if not skill_name_clean:
                continue
            
            skill_res = await db.execute(select(Skill).where(Skill.name == skill_name_clean))
            skill = skill_res.scalar_one_or_none()
            if not skill:
                skill = Skill(name=skill_name_clean, category=skill_category_clean)
                db.add(skill)
                await db.flush()
            else:
                if skill.category == "General" and skill_category_clean != "General":
                    skill.category = skill_category_clean
                    await db.flush()
            
            st_skill = StudentSkill(student_id=student.id, skill_id=skill.id, proficiency_level="Intermediate")
            db.add(st_skill)

    await db.commit()
    await db.refresh(student)
    return await get_profile(student, db)

from app.core.middleware import sanitize_upload_filename, validate_file_mime_type

@router.post("/resume")
async def upload_resume(
    file: UploadFile = File(...),
    student: StudentProfile = Depends(get_current_student),
    db: AsyncSession = Depends(get_db)
):
    allowed = [".pdf", ".docx", ".doc", ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"]
    safe_name = sanitize_upload_filename(file.filename)
    ext = os.path.splitext(safe_name)[1].lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF, DOCX, or Image file (PNG, JPG, WEBP).")

    # Read and validate file content size (Max 10MB limit - Point 10 Specification)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds maximum allowed boundary of 10MB.")

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Validate Magic Bytes / File MIME Header
    validate_file_mime_type(content, safe_name)

    filename = f"resume_student_{student.id}_{safe_name}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    with open(filepath, "wb") as buffer:
        buffer.write(content)
        
    parsed = parse_resume_file(filepath)
    student.resume_url = f"/uploads/{filename}"
    student.raw_resume_text = parsed["raw_text"]
    if parsed["phone"] and not student.phone:
        student.phone = parsed["phone"]
    if parsed["degree"] and not student.degree:
        student.degree = parsed["degree"]
    if parsed["branch"] and not student.branch:
        student.branch = parsed["branch"]
    if parsed["institution"] and not student.institution:
        student.institution = parsed["institution"]
    if parsed["completion_year"] and not student.graduation_year:
        student.graduation_year = parsed["completion_year"]
    if parsed["cgpa"] and not student.cgpa:
        student.cgpa = parsed["cgpa"]
    if parsed["projects_summary"]:
        student.projects_summary = parsed["projects_summary"]

    # Sync structured education record into student_education table
    await sync_student_education_record(db, student.id, parsed)

    # Auto-add extracted skills
    if parsed["skills"]:
        existing_skills_res = await db.execute(
            select(Skill.name).join(StudentSkill, Skill.id == StudentSkill.skill_id).where(StudentSkill.student_id == student.id)
        )
        existing_names = set(existing_skills_res.scalars().all())
        for sk in parsed["skills"]:
            if sk not in existing_names:
                skill_res = await db.execute(select(Skill).where(Skill.name == sk))
                skill_obj = skill_res.scalar_one_or_none()
                if not skill_obj:
                    skill_obj = Skill(name=sk, category="Extracted")
                    db.add(skill_obj)
                    await db.flush()
                db.add(StudentSkill(student_id=student.id, skill_id=skill_obj.id, proficiency_level="Intermediate"))

    await db.commit()
    await db.refresh(student)
    
    return {
        "message": "Resume uploaded and analyzed successfully",
        "parsed_data": parsed
    }

@router.delete("/resume")
async def delete_resume(
    student: StudentProfile = Depends(get_current_student),
    db: AsyncSession = Depends(get_db)
):
    if student.resume_url:
        # Delete file if exists
        filename = student.resume_url.split("/")[-1]
        filepath = os.path.join(settings.UPLOAD_DIR, filename)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception:
                pass
    student.resume_url = None
    student.raw_resume_text = None
    await db.commit()
    return {"message": "Uploaded document/image removed successfully"}

@router.get("/recommendations", response_model=List[RecommendationOut])
async def get_recommendations(
    student: StudentProfile = Depends(get_current_student),
    db: AsyncSession = Depends(get_db)
):
    # In-Memory Cache Lookup (Point 13 TTL Specification for High Performance)
    cache_key = f"rec_{student.id}"
    now_ts = time.time()
    if cache_key in _RECOMMENDATION_CACHE:
        entry = _RECOMMENDATION_CACHE[cache_key]
        if now_ts - entry.get("timestamp", 0) < CACHE_TTL_SECONDS:
            return entry.get("data", [])

    # Fetch weights config
    weights_res = await db.execute(select(ScoringWeightsConfig).order_by(ScoringWeightsConfig.id.desc()))
    weights_obj = weights_res.scalar_one_or_none()
    custom_weights = None
    if weights_obj:
        custom_weights = {
            "skill_match": weights_obj.skill_match_weight,
            "semantic_similarity": weights_obj.semantic_weight,
            "education_match": weights_obj.education_weight,
            "career_interest": weights_obj.interest_weight,
            "location_match": weights_obj.location_weight,
            "experience_relevance": weights_obj.experience_weight,
            "internship_preference": weights_obj.preference_weight
        }

    # Get student skills
    skills_res = await db.execute(
        select(Skill.name).join(StudentSkill, Skill.id == StudentSkill.skill_id).where(StudentSkill.student_id == student.id)
    )
    student_skills = list(skills_res.scalars().all())

    # Get live verified internships with eager loading (High-Performance Query Execution)
    internships_res = await db.execute(
        select(Internship).options(
            selectinload(Internship.skills).selectinload(InternshipSkill.skill)
        ).where(
            Internship.status == "VERIFIED_LIVE",
            Internship.verification_status == "VERIFIED",
            Internship.is_demo == False
        ).order_by(Internship.created_at.desc())
    )
    internships = internships_res.scalars().all()

    # Fetch candidate's verified LeetCode profile (if present)
    from app.db.models import LeetCodeProfile
    lc_prof_res = await db.execute(select(LeetCodeProfile).where(LeetCodeProfile.candidate_id == student.id))
    leetcode_prof = lc_prof_res.scalar_one_or_none()

    recommendations = []
    for opp in internships:
        formatted_skills = []
        for s in opp.skills:
            if s.skill:
                formatted_skills.append({"id": s.skill.id, "name": s.skill.name, "is_required": s.is_required})

        # Task 21: Opportunity Data Quality & Recommendation Gate
        from app.services.opportunity_quality import OpportunityQualityService
        is_quality_ok, _ = OpportunityQualityService.is_eligible_for_recommendation_ranking(opp)
        if not is_quality_ok:
            continue

        # Hard Eligibility Check
        is_eligible, _ = check_eligibility(student, opp)
        if not is_eligible:
            continue

        score, category, explanation_dict = generate_recommendation_for_student(
            student=student,
            internship=opp,
            student_skills=student_skills,
            weights=custom_weights,
            leetcode_profile=leetcode_prof
        )

        opp_dict = {
            "id": opp.id,
            "company_name": opp.company_name,
            "company_sector": opp.company_sector,
            "title": opp.title,
            "description": opp.description,
            "location": opp.location,
            "work_mode": opp.work_mode,
            "duration": opp.duration,
            "stipend": opp.stipend,
            "deadline": opp.deadline,
            "positions": opp.positions,
            "min_qualification": opp.min_qualification,
            "preferred_degree": opp.preferred_degree,
            "min_age": opp.min_age,
            "max_age": opp.max_age,
            "skills": formatted_skills,
            "source": opp.source or ("Jobvetta" if opp.source == "Jobvetta" else ("Adzuna" if opp.source == "Adzuna" else ("NCS" if "ncs.gov.in" in (opp.source_url or "") else "PMIS"))),
            "source_name": "Jobvetta Official API" if opp.source == "Jobvetta" else ("Adzuna Official API" if opp.source == "Adzuna" else ("Greenhouse Official" if opp.source == "Greenhouse" else ("National Career Service (NCS)" if (opp.source == "NCS" or "ncs.gov.in" in (opp.source_url or "")) else "PM Scheme Official"))),
            "opportunity_type": opp.opportunity_type or "INTERNSHIP",
            "apply_url": opp.apply_url or opp.source_url or (f"https://www.adzuna.in/details/{opp.external_id}" if opp.source == "Adzuna" and opp.external_id else None),
            "application_url": opp.apply_url or opp.source_url or (f"https://www.adzuna.in/details/{opp.external_id}" if opp.source == "Adzuna" and opp.external_id else None),
            "external_id": opp.external_id,
            "created_at": opp.created_at
        }

        rec_out = RecommendationOut(
            internship=opp_dict,
            score=score,
            match_category=category,
            explanation=RecommendationExplanation(**explanation_dict)
        )
        recommendations.append(rec_out)

    # Sort by score descending
    recommendations.sort(key=lambda x: x.score, reverse=True)
    _RECOMMENDATION_CACHE[cache_key] = {
        "timestamp": time.time(),
        "data": recommendations
    }
    return recommendations

@router.get("/skill-gaps", response_model=SkillGapOut)
async def get_skill_gaps(
    student: StudentProfile = Depends(get_current_student),
    db: AsyncSession = Depends(get_db)
):
    skills_res = await db.execute(
        select(Skill.name).join(StudentSkill, Skill.id == StudentSkill.skill_id).where(StudentSkill.student_id == student.id)
    )
    student_skills = list(skills_res.scalars().all())

    # Fetch top internships matching student
    recs = await get_recommendations(student, db)
    missing_all = []
    for r in recs[:5]: # Top 5 internships
        missing_all.extend(r.explanation.missing_required_skills)

    analysis = build_skill_gap_analysis(student_skills, missing_all)
    return SkillGapOut(**analysis)

@router.post("/feedback")
async def post_feedback(
    data: FeedbackCreate,
    student: StudentProfile = Depends(get_current_student),
    db: AsyncSession = Depends(get_db)
):
    fb = RecommendationFeedback(
        student_id=student.id,
        internship_id=data.internship_id,
        feedback_type=data.feedback_type,
        comments=data.comments
    )
    db.add(fb)
    await db.commit()
    return {"message": "Feedback recorded successfully"}


# ------------------------------------------------------------------
# LeetCode Profile Verification & Live Metrics Endpoints
# ------------------------------------------------------------------

from app.schemas.student import LeetCodeConnectRequest, LeetCodeConnectResponse
from app.leetcode.url_validator import validate_and_normalize_leetcode_url
from app.db.models import LeetCodeProfile

@router.post("/leetcode/connect", response_model=LeetCodeConnectResponse)
async def connect_leetcode_profile(
    req: LeetCodeConnectRequest,
    student: StudentProfile = Depends(get_current_student),
    db: AsyncSession = Depends(get_db)
):
    """
    Direct LeetCode Profile Connection:
    1. Validates and normalizes the public profile URL (e.g. https://leetcode.com/u/25CSEB52SANJAY/).
    2. Checks 24-hour cache in database; if missing or stale (>24h), queries public LeetCode GraphQL provider.
    3. Persists total_problems_solved and returns {"leetcode_username": username, "problems_solved": count}.
    """
    val_res = validate_and_normalize_leetcode_url(req.leetcode_url)
    if not val_res["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=val_res.get("error", "Invalid LeetCode profile URL.")
        )

    username = val_res["leetcode_username"]

    # Retrieve or create student LeetCodeProfile record
    stmt = select(LeetCodeProfile).where(LeetCodeProfile.candidate_id == student.id)
    res = await db.execute(stmt)
    lc_prof = res.scalar_one_or_none()

    if not lc_prof:
        lc_prof = LeetCodeProfile(
            candidate_id=student.id,
            leetcode_username=username,
            profile_url=val_res["normalized_url"],
            account_exists=True,
            verification_status="CONNECTED",
            ownership_status="CONNECTED",
            data_status="NOT_AVAILABLE"
        )
        db.add(lc_prof)
        await db.commit()
        await db.refresh(lc_prof)
    else:
        lc_prof.leetcode_username = username
        lc_prof.profile_url = val_res["normalized_url"]
        lc_prof.verification_status = "CONNECTED"
        lc_prof.ownership_status = "CONNECTED"
        await db.commit()

    # Fetch cached or updated metrics enforcing 24-hour cache
    m_res = await LeetCodeMetricsService.get_candidate_metrics(db, student.id)
    if not m_res.get("metrics") or m_res.get("data_status") == "STALE":
        m_res = await LeetCodeMetricsService.fetch_and_update_metrics(db, student.id)

    problems_solved = None
    if m_res.get("metrics"):
        problems_solved = m_res["metrics"].get("total_problems_solved")

    return {
        "leetcode_username": username,
        "problems_solved": problems_solved
    }


@router.get("/leetcode/metrics")
async def get_leetcode_metrics(
    student: StudentProfile = Depends(get_current_student),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves stored real profile metrics or fetches live metrics if verified.
    """
    return await LeetCodeMetricsService.fetch_and_update_metrics(db, student.id)


@router.delete("/leetcode")
async def disconnect_leetcode_profile(
    student: StudentProfile = Depends(get_current_student),
    db: AsyncSession = Depends(get_db)
):
    """
    Disconnects and removes the candidate's LeetCode profile record.
    """
    from app.db.models import LeetCodeProfile
    stmt = select(LeetCodeProfile).where(LeetCodeProfile.candidate_id == student.id)
    res = await db.execute(stmt)
    lc_prof = res.scalar_one_or_none()
    if lc_prof:
        await db.delete(lc_prof)
        await db.commit()
    return {"message": "LeetCode profile disconnected successfully"}
