import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Mandatory Classification Keywords specified in Task 3
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

def classify_greenhouse_opportunity(
    title: str,
    description: Optional[str] = None,
    departments: Optional[list] = None,
    raw_record: Optional[Dict[str, Any]] = None
) -> str:
    """
    Classifies a real Greenhouse opportunity as 'INTERNSHIP', 'JOB', or 'UNKNOWN'.
    Does not delete or discard any record regardless of classification.
    """
    if not title:
        return "UNKNOWN"

    t_clean = title.strip().lower()
    d_clean = (description or "").strip().lower()

    # Department / Metadata signal check
    dept_names = []
    if departments:
        for dept in departments:
            if isinstance(dept, dict) and dept.get("name"):
                dept_names.append(str(dept["name"]).lower())
            elif isinstance(dept, str):
                dept_names.append(dept.lower())

    dept_str = " ".join(dept_names)

    # 1. INTERNSHIP Signal Detection
    has_title_intern = any(re.search(r'\b' + re.escape(kw) + r'\b', t_clean) for kw in INTERNSHIP_KEYWORDS)
    has_dept_intern = any(kw in dept_str for kw in ["university", "early career", "campus", "internship"])

    if has_title_intern or has_dept_intern:
        # Contradiction check: Check if description explicitly rejects internship (e.g., 10+ years experience required)
        if "10+ years" in d_clean or "15+ years" in d_clean or "executive director position only" in d_clean:
            logger.warning(f"Contradictory signals for title '{title}': Marking as UNKNOWN.")
            return "UNKNOWN"
        return "INTERNSHIP"

    # 2. JOB Signal Detection
    has_title_job = any(re.search(r'\b' + re.escape(kw) + r'\b', t_clean) for kw in JOB_KEYWORDS)

    if has_title_job and not has_title_intern:
        # Check if description contradicts job classification
        if "this is an unpaid student internship" in d_clean:
            return "INTERNSHIP"
        return "JOB"

    # 3. Description fallback signal check if title is ambiguous
    if "internship" in d_clean or "summer intern" in d_clean or "co-op program" in d_clean:
        return "INTERNSHIP"

    if any(re.search(r'\b' + re.escape(kw) + r'\b', d_clean) for kw in ["full-time employment", "full time job", "years of experience"]):
        return "JOB"

    # 4. UNKNOWN when cannot confidently determine
    return "UNKNOWN"
