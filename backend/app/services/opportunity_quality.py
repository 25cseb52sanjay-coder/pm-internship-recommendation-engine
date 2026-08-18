from typing import Tuple, List, Dict, Any, Optional
from urllib.parse import urlparse
from datetime import datetime
from app.db.models import Internship

class OpportunityQualityService:
    """
    Opportunity Data Quality & Recommendation Gate Service.
    Validates URL syntax, HTTPS scheme, completeness, deduplication keys,
    and expiration before an opportunity can enter AI recommendation ranking.
    """

    @staticmethod
    def is_generic_homepage_url(url: Optional[str]) -> bool:
        """
        Determines whether a URL represents a generic provider homepage, company homepage root,
        or search landing page rather than a specific job/internship application destination.
        """
        if not url or not isinstance(url, str):
            return False
        trimmed = url.strip()
        if trimmed.upper() == "APPLICATION_URL_UNAVAILABLE" or trimmed.lower() in ["none", "null", "undefined"]:
            return True
        try:
            parsed = urlparse(trimmed)
            domain = (parsed.netloc or "").lower()
            path = (parsed.path or "").rstrip("/")

            # 1. Greenhouse provider root
            if ("boards.greenhouse.io" in domain or "greenhouse.io" in domain) and (not path or path == ""):
                return True

            # 2. Adzuna provider root
            if "adzuna" in domain and (not path or path == "" or path in ["/search", "/jobs"]):
                return True

            # 3. PM Scheme & MCA root
            if "pminternship.mca.gov.in" in domain and (not path or path == ""):
                return True
            if domain in ["mca.gov.in", "www.mca.gov.in"] and (not path or path == ""):
                return True

            # 4. NCS root
            if "ncs.gov.in" in domain and (not path or path in ["", "/internships-jobs"]):
                return True

            # 5. Generic domain root (e.g. https://company.com or https://company.com/)
            if domain and (not path or path == "") and not parsed.query:
                return True

            return False
        except Exception:
            return False

    @staticmethod
    def validate_application_url(url: Optional[str]) -> Tuple[bool, str]:
        if not url or not isinstance(url, str):
            return False, "Application URL is missing or empty"
        trimmed = url.strip()
        if not trimmed:
            return False, "Application URL is empty string"
        if trimmed.upper() == "APPLICATION_URL_UNAVAILABLE":
            return False, "Application URL marked explicitly unavailable"
        if trimmed.lower().startswith("javascript:") or trimmed.lower().startswith("data:"):
            return False, "Unsafe URL scheme detected (javascript: or data:)"
        try:
            parsed = urlparse(trimmed)
            if parsed.scheme.lower() not in ["https", "http"]:
                return False, f"Invalid URL scheme '{parsed.scheme}'. Only HTTP/HTTPS allowed."
            if not parsed.netloc:
                return False, "URL missing host domain"
            if OpportunityQualityService.is_generic_homepage_url(trimmed):
                return False, "Generic provider or company homepage rejected as specific application destination"
            return True, "Valid URL"
        except Exception as e:
            return False, f"URL syntax error: {str(e)}"

    @staticmethod
    def evaluate_opportunity_quality(opp: Internship) -> Tuple[str, str, List[str]]:
        """
        Evaluates opportunity quality status ('VALID', 'INCOMPLETE', 'INVALID')
        and active status ('ACTIVE', 'EXPIRED', 'INACTIVE', 'INVALID', 'UNKNOWN').
        Returns (quality_status, opportunity_status, list_of_reasons).
        """
        reasons = []

        # 1. Missing Title Check
        if not opp.title or not opp.title.strip():
            reasons.append("Missing opportunity title")

        # 2. Missing Source Check
        if not opp.source or not opp.source.strip():
            reasons.append("Missing opportunity source connector")

        # 3. Application URL Checks
        target_url = opp.apply_url or opp.source_url
        url_valid, url_reason = OpportunityQualityService.validate_application_url(target_url)
        if not url_valid:
            reasons.append(f"Application URL validation failed: {url_reason}")

        # 4. Status Checks
        raw_status = (opp.status or "ACTIVE").upper()
        if "VERIFIED" in raw_status or raw_status == "ACTIVE":
            opp_status = "ACTIVE"
        elif raw_status in ["EXPIRED", "INACTIVE", "INVALID", "UNKNOWN"]:
            opp_status = raw_status
        else:
            opp_status = "UNKNOWN"

        if opp_status in ["EXPIRED", "INACTIVE", "INVALID"]:
            reasons.append(f"Opportunity status is {opp_status}")

        # 5. Opportunity Type Validation
        opp_type = (opp.opportunity_type or "UNKNOWN").upper()
        if opp_type not in ["JOB", "INTERNSHIP", "UNKNOWN"]:
            opp_type = "UNKNOWN"

        # 6. Expiration Date Check (if deadline exists)
        if opp.deadline:
            try:
                d_date = datetime.strptime(opp.deadline.strip(), "%Y-%m-%d")
                if d_date < datetime.utcnow():
                    opp_status = "EXPIRED"
                    reasons.append(f"Deadline {opp.deadline} has passed")
            except Exception:
                pass

        # Determine Quality Status
        if any("title" in r or "URL" in r or "source connector" in r for r in reasons):
            quality_status = "INVALID"
        elif len(reasons) > 0:
            quality_status = "INCOMPLETE"
        else:
            quality_status = "VALID"

        if quality_status == "INVALID":
            opp_status = "INVALID"

        return quality_status, opp_status, reasons

    @staticmethod
    def get_deduplication_keys(opp: Internship) -> Dict[str, Optional[str]]:
        """
        Generates deduplication keys according to specified priority:
        1. Priority 1: source + external_id
        2. Priority 2: source + source_url
        3. Priority 3: source + normalized company + title + location
        """
        source = (opp.source or "UNKNOWN").strip().lower()

        # Key 1: source + external_id
        key1 = f"{source}::ext::{opp.external_id.strip().lower()}" if opp.external_id and opp.external_id.strip() else None

        # Key 2: source + source_url / apply_url
        raw_url = opp.source_url or opp.apply_url
        key2 = f"{source}::url::{raw_url.strip().lower()}" if raw_url and raw_url.strip() else None

        # Key 3: source + normalized company + title + location
        norm_company = (opp.company_name or "").strip().lower()
        norm_title = (opp.title or "").strip().lower()
        norm_loc = (opp.location or "").strip().lower()
        key3 = f"{source}::meta::{norm_company}::{norm_title}::{norm_loc}" if norm_company and norm_title else None

        return {
            "priority_1_external_id": key1,
            "priority_2_source_url": key2,
            "priority_3_metadata": key3
        }

    @staticmethod
    def is_eligible_for_recommendation_ranking(opp: Internship) -> Tuple[bool, List[str]]:
        """
        Recommendation Gate: Only returns True if opportunity is VALID quality and ACTIVE status.
        """
        quality_status, opp_status, reasons = OpportunityQualityService.evaluate_opportunity_quality(opp)
        is_eligible = (quality_status == "VALID" and opp_status == "ACTIVE")
        return is_eligible, reasons
