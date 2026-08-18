from datetime import datetime
from typing import Dict, Any

def update_internship_verification_state(
    current_status: str,
    quality_score: float,
    auto_verify: bool = True
) -> str:
    """
    Determines verification state transition for newly normalized opportunity.
    """
    if quality_score < 40.0:
        return "REJECTED"
    if auto_verify and quality_score >= 50.0:
        return "VERIFIED_LIVE"
    return "VALIDATING"
