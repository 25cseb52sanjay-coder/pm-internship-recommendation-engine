import re
from urllib.parse import urlparse
from typing import Dict, Any, Optional

# Reserved non-username path segments on LeetCode
LEETCODE_RESERVED_PATHS = {
    "u", "problems", "contest", "discuss", "explore", "store",
    "developer", "assessment", "jobs", "company", "subscribe",
    "login", "signup", "logout", "account", "profile", "settings",
    "api", "graphql", "static", "assets"
}

# LeetCode username character rules: alphanumeric, underscores, hyphens, 3-30 chars
LEETCODE_USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_-]{3,30}$")

def validate_and_normalize_leetcode_url(raw_input: Optional[str]) -> Dict[str, Any]:
    """
    Validates, sanitizes, and normalizes a submitted LeetCode handle or public profile URL.
    Enforces HTTPS protocol and strict leetcode.com domain check.
    Prevents open redirects and rejects malformed/unrelated URLs.
    
    Returns dict:
    {
        "valid": bool,
        "leetcode_username": str or None,
        "normalized_profile_url": str or None,
        "error": str or None
    }
    """
    if not raw_input or not isinstance(raw_input, str):
        return {
            "valid": False,
            "leetcode_username": None,
            "normalized_profile_url": None,
            "error": "Profile URL or username cannot be empty."
        }

    trimmed = raw_input.strip()
    if not trimmed:
        return {
            "valid": False,
            "leetcode_username": None,
            "normalized_profile_url": None,
            "error": "Profile URL or username cannot be blank."
        }

    # Rejection of dangerous URI schemes
    low_input = trimmed.lower()
    if low_input.startswith("javascript:") or low_input.startswith("data:") or low_input.startswith("file:"):
        return {
            "valid": False,
            "leetcode_username": None,
            "normalized_profile_url": None,
            "error": "Invalid URI scheme detected."
        }

    # Case A: User submitted a plain username handle (e.g. "candidate_dev")
    if not ("/" in trimmed or ":" in trimmed):
        if LEETCODE_USERNAME_REGEX.match(trimmed) and trimmed.lower() not in LEETCODE_RESERVED_PATHS:
            username = trimmed
            return {
                "valid": True,
                "leetcode_username": username,
                "normalized_profile_url": f"https://leetcode.com/u/{username}",
                "error": None
            }
        else:
            return {
                "valid": False,
                "leetcode_username": None,
                "normalized_profile_url": None,
                "error": "Invalid LeetCode username handle format."
            }

    # Case B: User submitted a URL or path string
    target_url = trimmed
    if not (target_url.startswith("http://") or target_url.startswith("https://")):
        target_url = f"https://{target_url}"

    try:
        parsed = urlparse(target_url)
    except Exception:
        return {
            "valid": False,
            "leetcode_username": None,
            "normalized_profile_url": None,
            "error": "Malformed URL format."
        }

    # Strict Protocol Check: Must be HTTP or HTTPS (normalized to HTTPS)
    if parsed.scheme not in ("http", "https"):
        return {
            "valid": False,
            "leetcode_username": None,
            "normalized_profile_url": None,
            "error": "Only HTTP/HTTPS protocols are allowed."
        }

    # Strict Domain / Hostname Check: Must be leetcode.com or www.leetcode.com
    hostname = (parsed.hostname or "").lower()
    allowed_domains = {"leetcode.com", "www.leetcode.com", "leetcode.cn", "www.leetcode.cn"}
    
    if hostname not in allowed_domains:
        return {
            "valid": False,
            "leetcode_username": None,
            "normalized_profile_url": None,
            "error": f"Invalid domain '{hostname}'. Only leetcode.com profile URLs are accepted."
        }

    # Path Normalization & Username Extraction
    path_segments = [seg for seg in parsed.path.split("/") if seg.strip()]
    if not path_segments:
        return {
            "valid": False,
            "leetcode_username": None,
            "normalized_profile_url": None,
            "error": "LeetCode profile URL path is missing username."
        }

    extracted_username = None

    # Handle standard path pattern: /u/username
    if path_segments[0].lower() == "u":
        if len(path_segments) >= 2:
            extracted_username = path_segments[1]
        else:
            return {
                "valid": False,
                "leetcode_username": None,
                "normalized_profile_url": None,
                "error": "LeetCode profile URL is missing username after '/u/'."
            }
    else:
        # Handle alternative path pattern: /username
        extracted_username = path_segments[0]

    # Validate extracted username against security regex & reserved word blocklist
    if not extracted_username or not LEETCODE_USERNAME_REGEX.match(extracted_username):
        return {
            "valid": False,
            "leetcode_username": None,
            "normalized_profile_url": None,
            "error": f"Extracted username '{extracted_username}' contains invalid characters or length."
        }

    if extracted_username.lower() in LEETCODE_RESERVED_PATHS:
        return {
            "valid": False,
            "leetcode_username": None,
            "normalized_profile_url": None,
            "error": f"'{extracted_username}' is a system reserved LeetCode path, not a user profile."
        }

    # Success: Construct canonical normalized HTTPS profile URL
    canonical_domain = "leetcode.cn" if "leetcode.cn" in hostname else "leetcode.com"
    normalized_url = f"https://{canonical_domain}/u/{extracted_username}"

    return {
        "valid": True,
        "leetcode_username": extracted_username,
        "normalized_profile_url": normalized_url,
        "error": None
    }
