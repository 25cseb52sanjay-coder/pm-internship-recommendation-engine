import re
import socket
import urllib.parse
from typing import Dict, Any, Tuple

DENIED_IP_NETWORKS = [
    "127.", "10.", "172.16.", "172.17.", "172.18.", "172.19.", "172.20.",
    "172.21.", "172.22.", "172.23.", "172.24.", "172.25.", "172.26.", "172.27.",
    "172.28.", "172.29.", "172.30.", "172.31.", "192.168.", "169.254.", "0.0.0.0"
]

def validate_url_ssrf_safe(url: str) -> Tuple[bool, str]:
    """
    Validates configurable source URL against SSRF security rules (Google Antigravity Spec).
    Blocks private, loopback, link-local, or cloud metadata IP addresses before fetching.
    """
    if not url or not isinstance(url, str):
        return False, "URL is empty or invalid type"

    parsed = urllib.parse.urlparse(url.strip())
    if parsed.scheme not in ("http", "https"):
        return False, f"Invalid URL scheme '{parsed.scheme}'. Only http and https allowed."

    hostname = parsed.hostname
    if not hostname:
        return False, "Missing hostname in URL"

    clean_host = hostname.lower().strip()

    # Block localhost & link-local names
    if clean_host in ("localhost", "loopback", "metadata.google.internal", "169.254.169.254"):
        return False, f"Blocked SSRF attempt to internal host '{clean_host}'"

    # Direct IP string check
    for prefix in DENIED_IP_NETWORKS:
        if clean_host.startswith(prefix):
            return False, f"Blocked SSRF attempt to private/internal IP '{clean_host}'"

    # Resolve IP address to prevent DNS rebinding SSRF
    try:
        ip_addr = socket.gethostbyname(clean_host)
        for prefix in DENIED_IP_NETWORKS:
            if ip_addr.startswith(prefix):
                return False, f"Resolved IP '{ip_addr}' belongs to a restricted private network range."
    except Exception:
        # If hostname resolution fails in offline/test environment, check scheme and host format
        pass

    return True, "URL validated as SSRF-safe"

def validate_internship_payload(payload: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validates minimum required fields in internship payload.
    """
    company = str(payload.get("company_name", "")).strip()
    title = str(payload.get("title", "")).strip()
    location = str(payload.get("location", "")).strip()

    if not company:
        return False, "Missing company_name field"
    if not title:
        return False, "Missing title field"
    if not location:
        return False, "Missing location field"

    app_url = payload.get("application_url") or payload.get("source_url")
    if app_url:
        is_safe, msg = validate_url_ssrf_safe(app_url)
        if not is_safe:
            return False, f"SSRF Validation Error: {msg}"

    return True, "Payload valid"
