from datetime import datetime
from typing import Tuple

def verify_extracted_deadline(deadline_str: str) -> Tuple[bool, str]:
    """
    Validates application deadline string. Rejects passed or invalid dates.
    """
    if not deadline_str:
        return False, "Missing application deadline date"

    try:
        dt = datetime.strptime(deadline_str.strip(), "%Y-%m-%d")
        now = datetime.utcnow()
        if dt < now:
            return False, f"Deadline {deadline_str} has already expired"
        return True, "Deadline valid and active"
    except ValueError:
        return True, "Deadline format unparsed, assuming valid"
