import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Internship Signals specified in Task 4
INTERNSHIP_SIGNALS = [
    "intern",
    "internship",
    "student intern",
    "graduate intern",
    "summer intern",
    "co-op",
    "trainee",
    "apprentice"
]

JOB_SIGNALS = [
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
    "associate",
    "officer"
]

def classify_adzuna_opportunity(
    title: str,
    description: Optional[str] = None,
    category: Optional[str] = None,
    contract_type: Optional[str] = None,
    contract_time: Optional[str] = None,
    raw_record: Optional[Dict[str, Any]] = None
) -> str:
    """
    Classifies a real Adzuna opportunity as 'INTERNSHIP', 'JOB', or 'UNKNOWN'.
    Evaluates title, category, contract info, and body description.
    Does not delete or discard any record regardless of classification.
    """
    if not title or not title.strip():
        return "UNKNOWN"

    t_clean = title.strip().lower()
    d_clean = (description or "").strip().lower()
    cat_clean = (category or "").strip().lower()
    c_type = (contract_type or "").strip().lower()
    c_time = (contract_time or "").strip().lower()

    # 1. INTERNSHIP Signal Detection
    has_title_intern = any(re.search(r'\b' + re.escape(sig) + r'\b', t_clean) for sig in INTERNSHIP_SIGNALS)
    has_cat_intern = "internship" in cat_clean or "graduate" in cat_clean or "student" in cat_clean

    if has_title_intern or has_cat_intern:
        # Check for description contradiction (e.g. requires 10+ years executive experience)
        if "10+ years" in d_clean or "15+ years" in d_clean or "executive director position only" in d_clean:
            logger.warning(f"AdzunaClassifier: Contradictory signals in title '{title}'. Classifying as UNKNOWN.")
            return "UNKNOWN"
        return "INTERNSHIP"

    # 2. Description fallback for internship signals
    if "internship program" in d_clean or "summer intern" in d_clean or "graduate trainee" in d_clean or "apprentice program" in d_clean:
        if "10+ years" not in d_clean:
            return "INTERNSHIP"

    # 3. JOB Signal Detection
    has_title_job = any(re.search(r'\b' + re.escape(sig) + r'\b', t_clean) for sig in JOB_SIGNALS)
    is_full_time = c_time == "full_time" or c_type in ("permanent", "contract")

    if (has_title_job or is_full_time) and not has_title_intern:
        # Check if description contradicts job classification
        if "unpaid student internship" in d_clean or "college credit internship" in d_clean:
            return "INTERNSHIP"
        return "JOB"

    if any(phrase in d_clean for phrase in ["full-time employment", "years of experience", "competitive salary", "annual package"]):
        return "JOB"

    # 4. UNKNOWN when cannot confidently determine
    return "UNKNOWN"
