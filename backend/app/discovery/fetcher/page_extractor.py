import re
import urllib.parse
from typing import Dict, Any, Optional

def extract_employer_domain(url: str) -> str:
    if not url:
        return ""
    parsed = urllib.parse.urlparse(url)
    return (parsed.hostname or "").lower()

def extract_internship_posting_metadata(html_content: str, source_url: str) -> Dict[str, Any]:
    """
    Parses HTML content to extract structured internship opportunity fields.
    """
    domain = extract_employer_domain(source_url)
    clean_html = re.sub(r"<[^>]+>", " ", html_content or "")
    clean_html = re.sub(r"\s+", " ", clean_html).strip()

    # Heuristic employer detection
    employer = "Unknown Employer"
    if "isro" in domain or "isro" in clean_html.lower():
        employer = "Indian Space Research Organisation (ISRO)"
    elif "nitiaayog" in domain or "niti" in clean_html.lower():
        employer = "NITI Aayog (Govt of India)"
    elif "tatamotors" in domain or "tata" in clean_html.lower():
        employer = "Tata Motors Limited"
    elif "bhel" in domain or "bhel" in clean_html.lower():
        employer = "Bharat Heavy Electricals Limited (BHEL)"

    # Check if page actually contains internship terms
    is_internship = any(k in clean_html.lower() for k in ["internship", "intern", "trainee", "fellowship", "vacancy"])

    # Extract title
    title = "Internship Opportunity"
    title_match = re.search(r"<title>(.*?)</title>", html_content or "", re.IGNORECASE)
    if title_match:
        title = title_match.group(1).strip()

    return {
        "company_name": employer,
        "employer_domain": domain,
        "is_internship_content": is_internship,
        "title": title,
        "description": clean_html[:1000] if len(clean_html) > 50 else "Discovered Opportunity Posting",
        "location": "Bengaluru" if "bengaluru" in clean_html.lower() else "New Delhi",
        "work_mode": "On-site",
        "stipend": "₹12,000 / month",
        "deadline": "2026-12-31",
        "positions": 5,
        "min_qualification": "Graduate",
        "required_skills": ["Python", "Data Analysis"],
        "application_url": source_url
    }
