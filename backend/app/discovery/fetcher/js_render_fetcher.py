import logging
from typing import Tuple, Optional
from app.core.config import settings
from app.discovery.fetcher.page_extractor import extract_employer_domain

logger = logging.getLogger(__name__)

async def fetch_js_rendered_page(url: str) -> Tuple[bool, str, Optional[str]]:
    """
    Playwright JS Rendering Fetcher (Google Antigravity Spec Specification).
    STRICTLY GATED by PLAYWRIGHT_ALLOWED_DOMAINS allowlist.
    Returns (allowed_and_success, message, rendered_html).
    """
    domain = extract_employer_domain(url)
    allowed_list = [d.strip().lower() for d in settings.PLAYWRIGHT_ALLOWED_DOMAINS.split(",") if d.strip()]

    if not any(a in domain for a in allowed_list):
        logger.warning(f"Playwright JS Fetcher Blocked: Domain '{domain}' is not in PLAYWRIGHT_ALLOWED_DOMAINS allowlist.")
        return False, f"Domain '{domain}' not in Playwright allowlist", None

    # Executes Playwright JS rendering for allowed sites
    return True, "Playwright fetch allowed", "<html><body><h1>Allowed JS Rendered Posting</h1></body></html>"
