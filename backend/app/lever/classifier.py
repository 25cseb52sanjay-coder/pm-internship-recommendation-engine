import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

INTERNSHIP_KEYWORDS = [
    "intern",
    "internship",
    "student intern",
    "graduate intern",
    "summer intern",
    "co-op",
    "cooperative education",
    "apprentice",
    "trainee"
]

JOB_KEYWORDS = [
    "engineer",
    "developer",
    "analyst",
    "designer",
    "manager",
    "consultant",
    "director",
    "lead",
    "senior",
    "principal",
    "architect",
    "specialist",
    "administrator",
    "executive",
    "recruiter",
    "counsel",
    "officer"
]

def classify_lever_opportunity(
    title: str,
    description: Optional[str] = None,
    categories: Optional[Dict[str, Any]] = None,
    raw_record: Optional[Dict[str, Any]] = None
) -> str:
    """
    Classifies a real Lever opportunity as 'INTERNSHIP', 'JOB', or 'UNKNOWN'.
    """
    if not title:
        return "UNKNOWN"

    t_clean = title.strip().lower()
    d_clean = (description or "").strip().lower()

    commitment = ""
    team = ""
    if categories and isinstance(categories, dict):
        commitment = str(categories.get("commitment") or "").lower()
        team = str(categories.get("team") or "").lower()

    # 1. INTERNSHIP Signal Detection
    has_title_intern = any(re.search(r'\b' + re.escape(kw) + r'\b', t_clean) for kw in INTERNSHIP_KEYWORDS)
    has_commitment_intern = any(kw in commitment for kw in ["intern", "internship", "co-op"])
    has_team_intern = any(kw in team for kw in ["university", "early career", "campus", "internship"])

    if has_title_intern or has_commitment_intern or has_team_intern:
        if "10+ years" in d_clean or "15+ years" in d_clean:
            return "UNKNOWN"
        return "INTERNSHIP"

    # 2. JOB Signal Detection
    has_title_job = any(re.search(r'\b' + re.escape(kw) + r'\b', t_clean) for kw in JOB_KEYWORDS)
    if has_title_job or "full-time" in commitment or "full time" in commitment:
        return "JOB"

    # 3. Description fallback
    if "internship" in d_clean or "summer intern" in d_clean:
        return "INTERNSHIP"

    if any(re.search(r'\b' + re.escape(kw) + r'\b', d_clean) for kw in ["full-time employment", "full time job", "years of experience"]):
        return "JOB"

    return "UNKNOWN"
