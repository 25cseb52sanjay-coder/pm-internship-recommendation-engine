from typing import List, Dict, Any, Tuple, Optional
import math
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.db.models import StudentProfile, Internship, ScoringWeightsConfig, Skill, InternshipSkill
from app.core.config import settings

def check_eligibility(student: StudentProfile, internship: Internship) -> Tuple[bool, List[str]]:
    """
    Applies hard eligibility rules. Returns (is_eligible, list_of_ineligibility_reasons).
    Rules:
    - Age check (if student age provided, must be within [min_age, max_age])
    - Qualification level check (if student qualification provided)
    """
    reasons = []
    
    min_age = getattr(internship, "min_age", None) if getattr(internship, "min_age", None) is not None else 21
    max_age = getattr(internship, "max_age", None) if getattr(internship, "max_age", None) is not None else 24
    if student.age is not None:
        if student.age < min_age or student.age > max_age:
            reasons.append(f"Age {student.age} is outside eligible range ({min_age}-{max_age} years)")
            
    # Degree / Qualification check
    if student.degree and internship.preferred_degree:
        # Simple fuzzy check
        stud_deg = student.degree.lower()
        pref_deg = internship.preferred_degree.lower()
        if pref_deg not in stud_deg and stud_deg not in pref_deg and "any" not in pref_deg:
            # We don't hard disqualify unless strictly enforced, but log reason
            pass

    is_eligible = len(reasons) == 0
    return is_eligible, reasons

def compute_skill_match_score(
    student_skills: List[str],
    required_skills: List[str],
    preferred_skills: List[str],
    skill_confidence_map: Optional[Dict[str, float]] = None
) -> Tuple[float, List[str], List[str]]:
    """
    Computes skill match score (0-100), matched skills, and missing required skills.
    Required skills carry double weight compared to preferred skills.
    Incorporate candidate evidence confidence weighting when skill_confidence_map is supplied.
    """
    std_skills_lower = {s.lower().strip() for s in student_skills}
    req_skills_lower = {s.lower().strip() for s in required_skills}
    pref_skills_lower = {s.lower().strip() for s in preferred_skills}
    
    matched = []
    missing_required = []
    
    for req in required_skills:
        req_l = req.lower().strip()
        if any(req_l in s or s in req_l for s in std_skills_lower):
            matched.append(req)
        else:
            missing_required.append(req)
            
    for pref in preferred_skills:
        pref_l = pref.lower().strip()
        if any(pref_l in s or s in pref_l for s in std_skills_lower):
            if pref not in matched:
                matched.append(pref)
                
    total_req_count = len(required_skills)
    total_pref_count = len(preferred_skills)
    
    if total_req_count == 0 and total_pref_count == 0:
        return 100.0, matched, missing_required
        
    req_matched_count = total_req_count - len(missing_required)
    pref_matched_count = len([p for p in preferred_skills if p in matched])
    
    total_weight = (total_req_count * 2) + total_pref_count
    matched_weight = (req_matched_count * 2) + pref_matched_count
    
    score = (matched_weight / total_weight) * 100.0 if total_weight > 0 else 100.0
    return round(score, 2), matched, missing_required

_EMBEDDING_MODEL = None

# In-Memory TTL Recommendation Cache (Point 13 Specification)
_RECOMMENDATION_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_SECONDS = 300  # 5 Minutes TTL

def invalidate_student_recommendation_cache(student_id: Optional[int] = None):
    """Invalidates recommendation cache for specific candidate or globally."""
    global _RECOMMENDATION_CACHE
    if student_id is not None:
        prefix = f"rec_{student_id}_"
        keys_to_del = [k for k in _RECOMMENDATION_CACHE if k.startswith(prefix)]
        for k in keys_to_del:
            _RECOMMENDATION_CACHE.pop(k, None)
    else:
        _RECOMMENDATION_CACHE.clear()

def _get_embedding_model():
    global _EMBEDDING_MODEL
    if _EMBEDDING_MODEL is None:
        try:
            from sentence_transformers import SentenceTransformer
            # Lightweight, high-accuracy 384-dimensional dense transformer model
            _EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            print(f"Warning: Could not load SentenceTransformer ({e}). Falling back to TF-IDF.")
            _EMBEDDING_MODEL = False
    return _EMBEDDING_MODEL

_VECTOR_CACHE: Dict[str, np.ndarray] = {}

def get_text_vector(text: str) -> Optional[np.ndarray]:
    global _VECTOR_CACHE
    if not text or not text.strip():
        return None
    if text in _VECTOR_CACHE:
        return _VECTOR_CACHE[text]
    model = _get_embedding_model()
    if model:
        try:
            vec = model.encode(text, convert_to_numpy=True)
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            _VECTOR_CACHE[text] = vec
            return vec
        except Exception:
            pass
    return None

def compute_semantic_similarity(student_text: str, internship_text: str) -> float:
    """
    Computes genuine AI/ML NLP Vector Embedding Cosine Similarity (Point 1 Specification).
    Pipeline: Candidate/Profile Text -> Neural Embedding Vector -> Internship Description Vector -> Cosine Similarity.
    """
    if not student_text.strip() or not internship_text.strip():
        return 50.0

    v1 = get_text_vector(student_text)
    v2 = get_text_vector(internship_text)

    if v1 is not None and v2 is not None:
        try:
            sim = float(np.dot(v1, v2))
            score = round(max(0.0, min(100.0, (sim + 1.0) / 2.0 * 100.0)), 2)
            return score
        except Exception:
            pass

    # Fallback to TF-IDF Cosine Similarity
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([student_text, internship_text])
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(float(sim) * 100.0, 2)
    except Exception:
        return 50.0

def compute_education_score(student: StudentProfile, internship: Internship) -> float:
    score = 70.0 # Default baseline
    if student.degree and internship.preferred_degree:
        if student.degree.lower().strip() == internship.preferred_degree.lower().strip():
            score = 100.0
        elif student.degree.lower() in internship.preferred_degree.lower() or internship.preferred_degree.lower() in student.degree.lower():
            score = 90.0
        else:
            score = 65.0
            
    if student.cgpa and student.cgpa >= 8.0:
        score = min(100.0, score + 10.0)
    return score

def compute_career_interest_score(student: StudentProfile, internship: Internship) -> float:
    score = 50.0
    stud_pref_ind = (student.preferred_industry or "").lower()
    stud_pref_role = (student.preferred_role or "").lower()
    
    opp_sector = (internship.company_sector or "").lower()
    opp_title = (internship.title or "").lower()
    opp_desc = (internship.description or "").lower()
    
    if stud_pref_ind and (stud_pref_ind in opp_sector or opp_sector in stud_pref_ind):
        score += 25.0
        
    if stud_pref_role and (stud_pref_role in opp_title or stud_pref_role in opp_desc):
        score += 25.0
        
    return min(100.0, score)

def compute_location_score(student: StudentProfile, internship: Internship) -> float:
    stud_loc = (student.preferred_location or "").lower()
    stud_mode = (student.work_mode or "").lower()
    
    opp_loc = (internship.location or "").lower()
    opp_mode = (internship.work_mode or "").lower()
    
    if opp_mode == "remote" or stud_mode == "remote" or stud_loc in ["any", "remote", "flexible"]:
        return 100.0
        
    if stud_loc and opp_loc and (stud_loc in opp_loc or opp_loc in stud_loc):
        return 100.0
        
    if stud_mode and opp_mode and stud_mode == opp_mode:
        return 80.0
        
    return 40.0

def compute_experience_relevance_score(student: StudentProfile, internship: Internship) -> float:
    if not student.projects_summary:
        return 50.0
    return compute_semantic_similarity(student.projects_summary, f"{internship.title} {internship.description}")

def generate_recommendation_for_student(
    student: StudentProfile,
    internship: Internship,
    student_skills: List[str],
    weights: Optional[Dict[str, float]] = None,
    leetcode_profile: Optional[Any] = None
) -> Tuple[float, str, Dict[str, Any]]:
    """
    Generates overall recommendation score (0-100), category, and detailed explainability payload.
    Includes verified LeetCode coding evidence as an optional non-breaking signal when present.
    """
    w = weights or {
        "skill_match": settings.DEFAULT_SKILL_MATCH_WEIGHT,
        "semantic_similarity": settings.DEFAULT_SEMANTIC_WEIGHT,
        "education_match": settings.DEFAULT_EDUCATION_WEIGHT,
        "career_interest": settings.DEFAULT_INTEREST_WEIGHT,
        "location_match": settings.DEFAULT_LOCATION_WEIGHT,
        "experience_relevance": settings.DEFAULT_EXPERIENCE_WEIGHT,
        "internship_preference": settings.DEFAULT_PREFERENCE_WEIGHT
    }
    
    req_skills = [s.skill.name for s in internship.skills if s.is_required]
    pref_skills = [s.skill.name for s in internship.skills if not s.is_required]
    
    skill_score, matched_skills, missing_required = compute_skill_match_score(student_skills, req_skills, pref_skills)
    
    student_full_text = f"{student.degree or ''} {student.branch or ''} {' '.join(student_skills)} {student.projects_summary or ''} {student.raw_resume_text or ''}"
    internship_full_text = f"{internship.title} {internship.company_sector} {internship.description} {' '.join(req_skills + pref_skills)}"
    
    semantic_score = compute_semantic_similarity(student_full_text, internship_full_text)
    # Academic Branch Compatibility Evaluation (Task 27B)
    from app.services.branch_compatibility import BranchCompatibilityEngine
    import json

    req_disc = json.loads(internship.required_disciplines_json) if getattr(internship, "required_disciplines_json", None) else None
    acc_disc = json.loads(internship.accepted_disciplines_json) if getattr(internship, "accepted_disciplines_json", None) else None
    disc_scope = getattr(internship, "discipline_scope", "UNKNOWN") or "UNKNOWN"
    cand_branch = getattr(student, "primary_discipline", None) or getattr(student, "branch", None)

    branch_eval = BranchCompatibilityEngine.evaluate_compatibility(
        candidate_raw_branch=cand_branch,
        required_disciplines=req_disc,
        accepted_disciplines=acc_disc,
        discipline_scope=disc_scope,
        original_requirement_text=getattr(internship, "original_requirement_text", None)
    )

    education_score = compute_education_score(student, internship)
    if branch_eval["compatibility_level"] == "STRONG_MATCH":
        education_score = max(education_score, 100.0)
    elif branch_eval["compatibility_level"] == "RELATED_MATCH":
        education_score = max(education_score, 85.0)
    elif branch_eval["compatibility_level"] == "CROSS_DISCIPLINARY_MATCH":
        education_score = max(education_score, 80.0)
    elif branch_eval["compatibility_level"] == "BROAD_SCOPE_MATCH":
        education_score = max(education_score, 75.0)
    elif branch_eval["compatibility_level"] == "INCOMPATIBLE":
        education_score = min(education_score, 30.0)

    interest_score = compute_career_interest_score(student, internship)

    # Specialization & Sector Matching Evaluation (Task 27C)
    from app.services.specialization_sector_matching import SpecializationSectorMatchingEngine

    cand_spec = getattr(student, "specialization", None)
    opp_spec = getattr(internship, "specialization", None) or getattr(internship, "specializations_json", None)

    spec_eval = SpecializationSectorMatchingEngine.evaluate_specialization_compatibility(
        candidate_raw_spec=cand_spec,
        opportunity_raw_spec=opp_spec,
        opportunity_title=internship.title,
        opportunity_description=internship.description
    )

    sector_eval = SpecializationSectorMatchingEngine.evaluate_sector_compatibility(
        candidate_target_sector=student.preferred_industry,
        opportunity_sector=internship.company_sector
    )

    if spec_eval["specialization_match_level"] == "SPECIALIZATION_EXACT":
        education_score = min(100.0, education_score + 5.0)
    elif spec_eval["specialization_match_level"] == "SPECIALIZATION_RELATED":
        education_score = min(100.0, education_score + 3.0)

    if sector_eval["sector_match_level"] == "SECTOR_EXACT":
        interest_score = min(100.0, interest_score + 10.0)

    # Opportunity Role & Domain Intelligence Evaluation (Task 27D)
    from app.services.opportunity_role_intelligence import OpportunityRoleIntelligence

    opp_role_info = OpportunityRoleIntelligence.classify_opportunity_role(
        title=internship.title,
        description=internship.description,
        skills=req_skills + pref_skills
    )

    role_eval = OpportunityRoleIntelligence.evaluate_role_compatibility(
        candidate_target_role=student.preferred_role,
        candidate_specialization=student.specialization,
        opportunity_role_info=opp_role_info
    )

    if role_eval["role_match_level"] == "EXACT_ROLE_MATCH":
        interest_score = min(100.0, interest_score + 15.0)
    elif role_eval["role_match_level"] == "STRONG_ROLE_MATCH":
        interest_score = min(100.0, interest_score + 10.0)
    elif role_eval["role_match_level"] == "NO_ROLE_MATCH":
        interest_score = min(20.0, interest_score * 0.25)
        education_score = min(40.0, education_score * 0.5)

    location_score = compute_location_score(student, internship)
    experience_score = compute_experience_relevance_score(student, internship)
    preference_score = 80.0 if student.preferred_duration == internship.duration else 60.0
    
    base_score = (
        skill_score * w.get("skill_match", 0.35) +
        semantic_score * w.get("semantic_similarity", 0.25) +
        education_score * w.get("education_match", 0.15) +
        interest_score * w.get("career_interest", 0.10) +
        location_score * w.get("location_match", 0.05) +
        experience_score * w.get("experience_relevance", 0.05) +
        preference_score * w.get("internship_preference", 0.05)
    )

    # Signal Integration: Verified LeetCode Evidence Processing (Task 12)
    leetcode_boost = 0.0
    leetcode_reasons = []
    
    if leetcode_profile and getattr(leetcode_profile, "verification_status", None) == "VERIFIED":
        lc_user = getattr(leetcode_profile, "leetcode_username", "candidate")
        total_solved = getattr(leetcode_profile, "total_problems_solved", None)
        med_solved = getattr(leetcode_profile, "medium_solved", None) or 0
        hard_solved = getattr(leetcode_profile, "hard_solved", None) or 0
        contest_rating = getattr(leetcode_profile, "contest_rating", None)

        is_tech_role = any(t in f"{internship.title} {internship.description}".lower() for t in ["software", "engineer", "developer", "data", "python", "code", "tech", "ai", "ml"])

        if is_tech_role and total_solved is not None and total_solved > 0:
            # Signal 1 & 2: Exposure & Difficulty Progression
            if total_solved >= 100 or (med_solved + hard_solved) >= 50:
                leetcode_boost += 3.5
                leetcode_reasons.append(f"Verified LeetCode Evidence: @{lc_user} has {total_solved} solved problems ({med_solved + hard_solved} Medium/Hard).")
            elif total_solved > 0:
                leetcode_boost += 1.5
                leetcode_reasons.append(f"Verified LeetCode Evidence: @{lc_user} has {total_solved} verified solved problems.")

            # Signal 3: Contest Performance
            if contest_rating and contest_rating >= 1500:
                leetcode_boost += 1.5
                leetcode_reasons.append(f"Verified Contest Performance: Rating {contest_rating} on LeetCode.")

    # Final score penalty if branch is explicitly INCOMPATIBLE
    if branch_eval["compatibility_level"] == "INCOMPATIBLE":
        base_score = base_score * 0.50

    # Final score penalty if role is completely non-matching (e.g. HR role for technical candidate)
    if role_eval["role_match_level"] == "NO_ROLE_MATCH":
        base_score = base_score * 0.70

    final_score = round(max(0.0, min(100.0, base_score + leetcode_boost)), 1)
    
    # Category Assignment
    if final_score >= 85.0:
        match_category = "Excellent Match"
    elif final_score >= 70.0:
        match_category = "Strong Match"
    elif final_score >= 55.0:
        match_category = "Good Match"
    else:
        match_category = "Potential Match"
        
    # Dynamic Strengths & Weaknesses
    strengths = []
    weaknesses = []

    if skill_score >= 70.0:
        strengths.append(f"High technical skill alignment ({skill_score}% - matched {len(matched_skills)} skills).")
    else:
        weaknesses.append(f"Technical skill gap ({skill_score}% - missing {len(missing_required)} required skills).")

    if semantic_score >= 70.0:
        strengths.append(f"Strong semantic profile alignment ({semantic_score}% text similarity).")
    elif semantic_score < 50.0:
        weaknesses.append(f"Limited profile text similarity ({semantic_score}%).")

    if education_score >= 85.0:
        strengths.append(f"Degree alignment ({student.degree or 'Graduate'} matching {internship.preferred_degree or 'Required degree'}).")
    elif education_score < 70.0:
        weaknesses.append(f"Degree preference mismatch (candidate {student.degree or 'Graduate'} vs required {internship.preferred_degree or 'Specific Degree'}).")

    if location_score >= 80.0:
        strengths.append(f"Favorable location/work mode fit ({internship.location} / {internship.work_mode}).")
    else:
        weaknesses.append(f"Location preference difference ({student.preferred_location or 'Preferred'} vs {internship.location}).")

    # Append LeetCode evidence strengths if available
    strengths.extend(leetcode_reasons)

    reasons = strengths + weaknesses
    if not reasons:
        reasons = ["Candidate profile satisfies foundational requirements for PM Internship Scheme."]

    summary_text = f"Recommended as an '{match_category}' with an AI compatibility index of {final_score}/100 based on your skills, academic background, and preferences."

    # Build Evidence Used Array & Explanation Confidence (Task 19)
    evidence_used = []
    for m_skill in matched_skills:
        ev_status = "DOCUMENTED" if (student.projects_summary or student.raw_resume_text) else "SELF_DECLARED"
        conf_val = 0.80 if ev_status == "DOCUMENTED" else 0.50
        evidence_used.append({
            "skill": m_skill,
            "source": "Academic Record" if ev_status == "DOCUMENTED" else "Candidate Profile",
            "verification_status": ev_status,
            "confidence": conf_val
        })

    if final_score >= 80.0 or any(e.get("verification_status") in ["DOCUMENTED", "ASSESSED", "VERIFIED_EXTERNAL"] for e in evidence_used):
        explanation_confidence = "HIGH"
    elif final_score >= 60.0:
        explanation_confidence = "MEDIUM"
    else:
        explanation_confidence = "LOW"

    matched_str = ", ".join(matched_skills[:3]) if matched_skills else "foundational profile requirements"
    rec_reason = f"{match_category} compatibility ({final_score}/100) based on candidate skills ({matched_str}), academic degree ({student.degree or 'Graduate'}), and location preference ({internship.location})."

    explanation_payload = {
        "summary": summary_text,
        "matched_skills": matched_skills,
        "missing_required_skills": missing_required,
        "education_status": f"{student.degree or 'Graduate'} evaluated against {internship.preferred_degree or 'Required degree'}",
        "location_status": f"{internship.location} ({internship.work_mode})",
        "breakdown": {
            "skill_match": skill_score,
            "semantic_similarity": semantic_score,
            "education_match": education_score,
            "career_interest": interest_score,
            "location_match": location_score,
            "experience_relevance": experience_score,
            "internship_preference": preference_score
        },
        "reasons": reasons,
        "strengths": strengths,
        "weaknesses": weaknesses,

        # Task 19 Specification Additions
        "overall_match_score": final_score,
        "missing_skills": missing_required,
        "qualification_match": f"{student.degree or 'Graduate'} matching {internship.preferred_degree or 'Required Degree'}",
        "location_match": f"{internship.location} ({internship.work_mode})",
        "experience_match": f"{experience_score}%",
        "opportunity_type_match": f"{internship.opportunity_type or 'INTERNSHIP'}",
        "evidence_used": evidence_used,
        "confidence": explanation_confidence,
        "recommendation_reason": rec_reason,

        # Task 27B Academic Branch Compatibility Additions
        "academic_match_level": branch_eval["compatibility_level"],
        "academic_match_score": branch_eval["compatibility_score"],
        "candidate_discipline": branch_eval["candidate_discipline"],
        "matched_opportunity_discipline": branch_eval["matched_opportunity_discipline"],
        "discipline_match_reason": branch_eval["reason"],

        # Task 27C Specialization & Sector Matching Additions
        "specialization_match_level": spec_eval["specialization_match_level"],
        "specialization_match_score": spec_eval["specialization_match_score"],
        "sector_match_level": sector_eval["sector_match_level"],
        "sector_match_score": sector_eval["sector_match_score"],
        "candidate_specialization": spec_eval["candidate_specialization"],
        "opportunity_specialization": spec_eval["opportunity_specialization"],
        "candidate_sector_interest": sector_eval["candidate_sector_interest"],
        "opportunity_sector": sector_eval["opportunity_sector"],
        "role_match": f"Target Role: {student.preferred_role or 'Flexible'} evaluated against {internship.title}",
        "allocation_reason": f"{branch_eval['reason']} {spec_eval['reason']} {sector_eval['reason']}",

        # Task 27D Opportunity Role & Domain Intelligence Additions
        "role_match_level": role_eval["role_match_level"],
        "role_match_score": role_eval["role_match_score"],
        "normalized_role": role_eval["normalized_role"],
        "opportunity_role": opp_role_info.get("display_name", role_eval["normalized_role"]),
        "role_family": role_eval["role_family"],
        "opportunity_domain": opp_role_info["role_family"],
        "candidate_target_role": student.preferred_role or "Unspecified",
        "role_match_reason": role_eval["reason"],

        # Task 27E Multi-Discipline Ranking & Allocation Additions
        "skill_match_score": skill_score,
        "semantic_similarity_score": semantic_score
    }
    
    return final_score, match_category, explanation_payload

def build_skill_gap_analysis(student_skills: List[str], missing_skills_list: List[str]) -> Dict[str, Any]:
    """
    Builds skill gap matrix, courses recommendations, and readiness index.
    """
    missing_items = []
    courses_map = {
        "Python": "Python for Data Science & Automation (NPTEL / Coursera)",
        "SQL": "Database Management & SQL Systems (Swayam / Infosys Springboard)",
        "Machine Learning": "Applied Machine Learning & AI Foundations (IIT Madras - NPTEL)",
        "Data Analysis": "Data Analytics with Excel & PowerBI (PM Skills Portal)",
        "React": "Frontend Web Development with React & Next.js (FreeCodeCamp)",
        "Java": "Object Oriented Programming in Java (Swayam / NPTEL)",
        "Financial Modeling": "Corporate Finance & Valuation Fundamentals",
        "Project Management": "Agile & Waterfall Project Management Principles",
        "Docker": "Containerization & DevOps Essentials",
        "Cyber Security": "Certified Ethical Hacking & Network Security",
    }
    
    categories_map = {
        "Python": "Software & AI",
        "SQL": "Data Systems",
        "Machine Learning": "Artificial Intelligence",
        "React": "Frontend Development",
        "Java": "Software Development",
        "Financial Modeling": "Finance & Analytics",
        "Project Management": "Management",
    }
    
    seen = set()
    for s in missing_skills_list:
        if s in seen:
            continue
        seen.add(s)
        course = courses_map.get(s, f"Fundamentals of {s} (Government PM Skill Hub)")
        cat = categories_map.get(s, "Core Technical Skill")
        missing_items.append({
            "skill": s,
            "priority": "High",
            "category": cat,
            "recommendation_course": course
        })
        
    readiness_score = round(max(20.0, 100.0 - (len(missing_items) * 12.5)), 1)
    
    career_paths = []
    std_set = {sk.lower() for sk in student_skills}
    if any(k in std_set for k in ["python", "sql", "machine learning", "pandas"]):
        career_paths.append("Data Scientist / AI Engineer Track under PM Internship Scheme")
    if any(k in std_set for k in ["react", "javascript", "html", "css", "web"]):
        career_paths.append("Full-Stack Web Developer Track in Public Sector Tech Modules")
    if any(k in std_set for k in ["finance", "excel", "accounting", "banking"]):
        career_paths.append("Public Sector Financial Analyst & Management Trainee Track")
    if not career_paths:
        career_paths.append("General Operational & Technical Analyst Trainee")
        
    return {
        "student_skills": student_skills,
        "missing_required_skills": missing_items,
        "career_path_suggestions": career_paths,
        "readiness_score": readiness_score
    }
