from typing import Tuple

def verify_content_recency(html_content: str) -> Tuple[bool, str]:
    """
    Checks if extracted page content is recent rather than stale cached archive.
    """
    if not html_content or len(html_content) < 50:
        return False, "Insufficient content length for recency check"

    # Verify absence of explicit archive indicators
    lower = html_content.lower()
    if "wayback machine" in lower or "cached page" in lower or "archive.org" in lower:
        return False, "Stale web archive page detected"

    return True, "Content recency check passed"
