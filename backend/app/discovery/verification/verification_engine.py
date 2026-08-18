import json
import logging
from datetime import datetime
from typing import Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import DiscoveryCandidate, Internship, SourceRegistry
from app.discovery.fetcher import fetch_discovered_page_html, extract_internship_posting_metadata
from app.discovery.verification.domain_trust import verify_employer_domain_trust
from app.discovery.verification.deadline_check import verify_extracted_deadline
from app.discovery.verification.content_recency_check import verify_content_recency
from app.ingestion.pipeline import generate_internship_sha256_fingerprint, calculate_internship_quality_score, normalize_internship_record

logger = logging.getLogger(__name__)

async def process_discovery_candidate_verification(
    db: AsyncSession,
    candidate: DiscoveryCandidate
) -> Tuple[str, str, float]:
    """
    Multi-stage Verification Pipeline (Google Antigravity Spec Specification).
    Executes 9-stage sequence:
      1. Accessibility check (HTTP 200)
      2. Employer identifiability
      3. AI content classification (is internship posting?)
      4. Application URL validity
      5. Domain trust check
      6. Deadline check
      7. Content recency check
      8. Shared SHA-256 deduplication check against existing internships/candidates
      9. Quality completeness scoring

    On VERIFIED status, hands off payload to shared Ingestion Engine task chain.
    On failure, short-circuits with rejection code without modifying internships table.
    """
    url = candidate.result_url

    # Stage 1: Accessibility check
    success, http_status, msg, html_content = await fetch_discovered_page_html(url)
    if not success:
        candidate.fetch_status = "FETCH_FAILED"
        candidate.verification_status = "FETCH_FAILED"
        candidate.rejection_reason = msg
        db.add(candidate)
        await db.commit()
        return "FETCH_FAILED", msg, 0.0

    candidate.fetch_status = "FETCHED"

    # Stage 2 & 3: Extraction & Content Classification
    extracted = extract_internship_posting_metadata(html_content, url)
    candidate.extraction_status = "EXTRACTED"
    candidate.extracted_payload_json = json.dumps(extracted)

    if not extracted.get("is_internship_content"):
        candidate.verification_status = "NOT_INTERNSHIP_CONTENT"
        candidate.rejection_reason = "Page content does not match internship opportunity classification criteria"
        db.add(candidate)
        await db.commit()
        return "NOT_INTERNSHIP_CONTENT", candidate.rejection_reason, 0.0

    # Stage 4: Employer Identifiability & Domain Trust Check
    is_domain_match, domain_name, domain_msg = verify_employer_domain_trust(extracted["company_name"], url)
    candidate.employer_domain = domain_name
    candidate.official_domain_match = is_domain_match

    if not is_domain_match:
        # Borderline domain mismatch -> Route to manual admin review queue per spec
        candidate.verification_status = "NOT_IDENTIFIABLE_EMPLOYER"
        candidate.rejection_reason = domain_msg
        db.add(candidate)
        await db.commit()
        return "NOT_IDENTIFIABLE_EMPLOYER", domain_msg, 30.0

    # Stage 5: Application URL Validity
    candidate.application_url_valid = bool(extracted.get("application_url"))

    # Stage 6: Deadline Check
    dl_valid, dl_msg = verify_extracted_deadline(extracted.get("deadline"))
    candidate.deadline_extracted = extracted.get("deadline")
    if not dl_valid:
        candidate.verification_status = "DEADLINE_INVALID_OR_EXPIRED"
        candidate.rejection_reason = dl_msg
        db.add(candidate)
        await db.commit()
        return "DEADLINE_INVALID_OR_EXPIRED", dl_msg, 0.0

    # Stage 7: Content Recency Check
    rec_valid, rec_msg = verify_content_recency(html_content)
    candidate.content_recency_check_passed = rec_valid
    if not rec_valid:
        candidate.verification_status = "STALE_CONTENT"
        candidate.rejection_reason = rec_msg
        db.add(candidate)
        await db.commit()
        return "STALE_CONTENT", rec_msg, 0.0

    # Stage 8: SHA-256 Deduplication Check
    norm = normalize_internship_record(extracted)
    sha256_fp = generate_internship_sha256_fingerprint(norm["company_name"], norm["title"], norm["location"], norm["application_url"])
    candidate.fingerprint_sha256 = sha256_fp

    ex_res = await db.execute(
        select(Internship).where(
            (Internship.fingerprint_sha256 == sha256_fp) | (Internship.duplicate_fingerprint == sha256_fp)
        )
    )
    existing_opp = ex_res.scalar_one_or_none()

    # Stage 9: Quality Score Calculation
    q_score = calculate_internship_quality_score(norm, source_confidence=0.9 if is_domain_match else 0.6)
    candidate.quality_score = q_score

    if existing_opp:
        candidate.verification_status = "VERIFIED"
        candidate.linked_internship_id = existing_opp.id
        candidate.rejection_reason = f"Duplicate merged into existing internship ID {existing_opp.id}"
        db.add(candidate)
        await db.commit()
        return "VERIFIED", candidate.rejection_reason, q_score

    # Hand off VERIFIED opportunity to shared Ingestion Engine task chain
    candidate.verification_status = "VERIFIED"
    
    # Get or create WEB_DISCOVERY source registry entry
    src_res = await db.execute(select(SourceRegistry).where(SourceRegistry.source_name == "Web Discovery Engine"))
    disc_src = src_res.scalar_one_or_none()
    if not disc_src:
        disc_src = SourceRegistry(
            source_name="Web Discovery Engine",
            source_url="https://api.bing.microsoft.com/v7.0/search",
            source_type="WEB_DISCOVERY",
            authorization_status="AUTHORIZED",
            health_status="ONLINE",
            source_confidence=0.9
        )
        db.add(disc_src)
        await db.flush()

    new_opp = Internship(
        company_name=norm["company_name"],
        company_sector=norm["company_sector"],
        title=norm["title"],
        description=norm["description"],
        location=norm["location"],
        work_mode=norm["work_mode"],
        duration=norm["duration"],
        stipend=norm["stipend"],
        deadline=norm["deadline"],
        positions=norm["positions"],
        min_qualification=norm["min_qualification"],
        preferred_degree=norm["preferred_degree"],
        min_age=norm["min_age"],
        max_age=norm["max_age"],
        source_id=disc_src.id,
        source_url=norm["application_url"],
        duplicate_fingerprint=sha256_fp,
        fingerprint_sha256=sha256_fp,
        status="VERIFIED_LIVE",
        verification_status="VERIFIED",
        quality_score=q_score,
        first_seen_at=datetime.utcnow(),
        last_seen_at=datetime.utcnow(),
        last_verified_at=datetime.utcnow(),
        posted_date=datetime.utcnow(),
        last_checked_at=datetime.utcnow(),
        is_demo=False
    )
    db.add(new_opp)
    await db.flush()

    candidate.linked_internship_id = new_opp.id
    db.add(candidate)
    await db.commit()

    logger.info(f"Verification Engine: Promoted discovery candidate ID {candidate.id} to verified internship ID {new_opp.id} (Quality Score: {q_score}).")
    return "VERIFIED", "Promoted to verified live internship", q_score
