from typing import Dict, Any

def calculate_internship_quality_score(
    normalized_record: Dict[str, Any],
    source_confidence: float = 1.0
) -> float:
    """
    Computes quality completeness score (0 to 100) per Google Antigravity Spec.
    Listings below quality threshold are stored but withheld from student recommendations.
    """
    score = 0.0

    # 1. Company Name (Max 15 pts)
    if normalized_record.get("company_name"):
        score += 15.0

    # 2. Title (Max 15 pts)
    if normalized_record.get("title"):
        score += 15.0

    # 3. Location (Max 15 pts)
    if normalized_record.get("location"):
        score += 15.0

    # 4. Description Length & Quality (Max 20 pts)
    desc = normalized_record.get("description", "")
    if len(desc) > 100:
        score += 20.0
    elif len(desc) > 30:
        score += 10.0

    # 5. Required Skills Presence (Max 15 pts)
    skills = normalized_record.get("required_skills", [])
    if len(skills) >= 3:
        score += 15.0
    elif len(skills) >= 1:
        score += 8.0

    # 6. Deadline Presence (Max 10 pts)
    if normalized_record.get("deadline"):
        score += 10.0

    # 7. Application URL Validity (Max 10 pts)
    if normalized_record.get("application_url"):
        score += 10.0

    # Multiply by source confidence factor
    final_score = score * max(0.1, min(1.0, source_confidence))
    return round(final_score, 1)
