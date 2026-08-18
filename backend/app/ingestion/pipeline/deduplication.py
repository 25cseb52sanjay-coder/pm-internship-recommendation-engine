import hashlib
from typing import Dict, Any

def generate_internship_sha256_fingerprint(
    company_name: str,
    title: str,
    location: str,
    application_url: str = ""
) -> str:
    """
    Generates SHA-256 fingerprint over normalized (company + title + location + application_url).
    Identical opportunities from multiple sources resolve to the same fingerprint hash.
    """
    c_clean = company_name.strip().lower()
    t_clean = title.strip().lower()
    l_clean = location.strip().lower()
    u_clean = application_url.strip().lower()

    raw_string = f"{c_clean}|{t_clean}|{l_clean}|{u_clean}"
    return hashlib.sha256(raw_string.encode('utf-8')).hexdigest()

def check_is_duplicate_opportunity(
    fingerprint_sha256: str,
    existing_fingerprints: set
) -> bool:
    """Checks if fingerprint SHA-256 already exists in dataset."""
    return fingerprint_sha256 in existing_fingerprints
