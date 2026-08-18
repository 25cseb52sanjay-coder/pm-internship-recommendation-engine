from typing import Tuple
from app.discovery.fetcher.page_extractor import extract_employer_domain

KNOWN_TRUSTED_DOMAINS = [
    "isro.gov.in",
    "nitiaayog.gov.in",
    "tatamotors.com",
    "bhel.com",
    "sbi.co.in",
    "infosys.com",
    "coalindia.in",
    "ril.com",
    "pminternship.mca.gov.in"
]

def verify_employer_domain_trust(company_name: str, result_url: str) -> Tuple[bool, str, str]:
    """
    Verifies employer domain match against known enterprise/govt domains (Google Antigravity Spec).
    Borderline mismatches return False so candidate is queued for admin manual review.
    Returns (is_official_match, domain_name, status_reason).
    """
    domain = extract_employer_domain(result_url)
    if not domain:
        return False, "", "Empty or unparseable URL domain"

    for trusted in KNOWN_TRUSTED_DOMAINS:
        if trusted in domain:
            return True, domain, "Official employer domain match verified"

    return False, domain, "Domain mismatch: Requires manual admin review"
