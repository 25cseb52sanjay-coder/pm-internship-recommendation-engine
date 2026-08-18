import re
from datetime import datetime, timezone
from typing import Dict, Any, List

WORK_MODE_MAP = {
    "remote": "Remote",
    "work from home": "Remote",
    "wfh": "Remote",
    "hybrid": "Hybrid",
    "onsite": "On-site",
    "on-site": "On-site",
    "in-office": "On-site",
    "office": "On-site"
}

EDUCATION_MAP = {
    "b.tech": "B.Tech",
    "btech": "B.Tech",
    "b.e.": "B.Tech",
    "b.sc": "B.Sc",
    "bsc": "B.Sc",
    "b.com": "B.Com",
    "bcom": "B.Com",
    "bba": "BBA",
    "mba": "MBA",
    "m.tech": "M.Tech",
    "graduate": "Graduate",
    "bachelor's": "Graduate"
}

def normalize_text(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.strip())

def normalize_work_mode(raw_mode: str) -> str:
    if not raw_mode:
        return "On-site"
    clean = raw_mode.strip().lower()
    return WORK_MODE_MAP.get(clean, "On-site")

def normalize_education_degree(raw_degree: str) -> str:
    if not raw_degree:
        return "Graduate"
    clean = raw_degree.strip().lower()
    for key, val in EDUCATION_MAP.items():
        if key in clean:
            return val
    return raw_degree.strip()

def normalize_stipend_format(raw_stipend: str) -> str:
    if not raw_stipend:
        return "₹12,000 / month"
    clean = raw_stipend.strip()
    if not clean.startswith("₹") and not clean.startswith("Rs"):
        digits = re.findall(r"\d+", clean)
        if digits:
            num = int(digits[0])
            return f"₹{num:,} / month"
    return clean

def normalize_date_utc(raw_date: Any) -> str:
    if isinstance(raw_date, datetime):
        return raw_date.strftime("%Y-%m-%d")
    if isinstance(raw_date, str) and raw_date:
        return raw_date.strip()
    return "2026-12-31"

def normalize_internship_record(raw_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes raw internship record fields into canonical standardized format.
    """
    return {
        "company_name": normalize_text(raw_record.get("company_name", "")),
        "company_sector": normalize_text(raw_record.get("company_sector", "General Enterprise")),
        "title": normalize_text(raw_record.get("title", "")),
        "description": normalize_text(raw_record.get("description", "PM Internship Scheme Opportunity")),
        "location": normalize_text(raw_record.get("location", "")),
        "work_mode": normalize_work_mode(raw_record.get("work_mode", "On-site")),
        "duration": normalize_text(raw_record.get("duration", "6 Months")),
        "stipend": normalize_stipend_format(raw_record.get("stipend", "₹12,000 / month")),
        "deadline": normalize_date_utc(raw_record.get("deadline", "2026-12-31")),
        "positions": int(raw_record.get("positions", 5)),
        "min_qualification": normalize_education_degree(raw_record.get("min_qualification", "Graduate")),
        "preferred_degree": normalize_education_degree(raw_record.get("preferred_degree", "B.Tech")),
        "min_age": int(raw_record.get("min_age", 21)),
        "max_age": int(raw_record.get("max_age", 24)),
        "required_skills": [normalize_text(s) for s in raw_record.get("required_skills", []) if s],
        "preferred_skills": [normalize_text(s) for s in raw_record.get("preferred_skills", []) if s],
        "application_url": raw_record.get("application_url", "").strip() or raw_record.get("source_url", "").strip()
    }
