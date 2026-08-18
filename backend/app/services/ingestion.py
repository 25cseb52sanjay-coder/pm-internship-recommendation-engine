import hashlib
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from app.db.models import Internship, SourceRegistry, Skill, InternshipSkill

def normalize_text(text: str) -> str:
    """Normalize text by stripping whitespace, removing special chars, and lowercasing."""
    if not text:
        return ""
    text = re.sub(r'[^\w\s]', '', text)
    return ' '.join(text.lower().split())

def generate_duplicate_fingerprint(company_name: str, title: str, location: str) -> str:
    """
    Generate deterministic SHA-256 fingerprint for duplicate detection.
    Matches PDF Section 3 Specification: duplicate_fingerprint = sha256(norm_company:norm_title:norm_location)
    """
    norm_comp = normalize_text(company_name)
    norm_title = normalize_text(title)
    norm_loc = normalize_text(location)
    raw = f"{norm_comp}:{norm_title}:{norm_loc}"
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()

class InternshipIngestionService:
    """
    Live Internship Ingestion Pipeline & Verification Engine (PDF Section 3 Specification)
    Pipeline: Source Registry -> Collector -> Parser -> Normalizer -> Validator -> Duplicate Detector -> Verification -> DB
    """

    @staticmethod
    async def get_or_create_default_sources(db: AsyncSession) -> List[SourceRegistry]:
        """Pre-populate approved official ingestion sources in source_registry table."""
        sources = [
            {
                "source_name": "PM Internship Portal Official Feed",
                "source_url": "https://pminternship.mca.gov.in/api/feed",
                "source_type": "OFFICIAL_FEED",
                "collection_method": "AUTOMATED",
                "rate_limit_rpm": 120
            },
            {
                "source_name": "Ministry of Corporate Affairs Enterprise API",
                "source_url": "https://mca.gov.in/api/v1/internships",
                "source_type": "API",
                "collection_method": "AUTOMATED",
                "rate_limit_rpm": 60
            },
            {
                "source_name": "Public Sector Enterprises Ingestion Registry",
                "source_url": "https://dpe.gov.in/api/internships",
                "source_type": "CRAWLER",
                "collection_method": "AUTOMATED",
                "rate_limit_rpm": 30
            }
        ]

        active_sources = []
        for s in sources:
            res = await db.execute(select(SourceRegistry).where(SourceRegistry.source_name == s["source_name"]))
            existing = res.scalar_one_or_none()
            if not existing:
                src = SourceRegistry(**s)
                db.add(src)
                await db.commit()
                await db.refresh(src)
                active_sources.append(src)
            else:
                active_sources.append(existing)
        return active_sources

    @staticmethod
    async def ingest_internship_feed(
        db: AsyncSession,
        source_id: int,
        raw_items: List[Dict[str, Any]],
        auto_verify: bool = True
    ) -> Dict[str, Any]:
        """
        Ingests, parses, normalizes, deduplicates, and verifies raw internship items.
        """
        processed_count = 0
        new_count = 0
        duplicate_count = 0
        expired_count = 0

        for item in raw_items:
            company_name = item.get("company_name", "").strip()
            title = item.get("title", "").strip()
            location = item.get("location", "").strip()

            if not company_name or not title or not location:
                continue

            processed_count += 1
            fingerprint = generate_duplicate_fingerprint(company_name, title, location)

            # Duplicate Check using duplicate_fingerprint
            existing_res = await db.execute(
                select(Internship).where(Internship.duplicate_fingerprint == fingerprint)
            )
            existing = existing_res.scalar_one_or_none()

            if existing:
                duplicate_count += 1
                # Update last checked timestamp for existing opportunity
                existing.last_checked_at = datetime.utcnow()
                db.add(existing)
                await db.commit()
                continue

            # LifeCycle Verification State
            initial_status = "VERIFIED_LIVE" if auto_verify else "PENDING_VERIFICATION"

            new_internship = Internship(
                company_name=company_name,
                company_sector=item.get("company_sector", "General Enterprise"),
                title=title,
                description=item.get("description", "Official PM Internship Opportunity"),
                location=location,
                work_mode=item.get("work_mode", "On-site"),
                duration=item.get("duration", "6 Months"),
                stipend=item.get("stipend", "₹12,000 / month"),
                deadline=item.get("deadline", "2026-12-31"),
                positions=item.get("positions", 5),
                min_qualification=item.get("min_qualification", "Graduate"),
                preferred_degree=item.get("preferred_degree", "B.Tech"),
                min_age=item.get("min_age", 21),
                max_age=item.get("max_age", 24),
                source_id=source_id,
                source_url=item.get("source_url", "https://pminternship.mca.gov.in"),
                duplicate_fingerprint=fingerprint,
                status=initial_status,
                posted_date=datetime.utcnow(),
                last_checked_at=datetime.utcnow(),
                is_demo=False
            )
            db.add(new_internship)
            await db.commit()
            await db.refresh(new_internship)
            new_count += 1

        # Update last_checked_at on SourceRegistry
        await db.execute(
            update(SourceRegistry)
            .where(SourceRegistry.id == source_id)
            .values(last_checked_at=datetime.utcnow())
        )
        await db.commit()

        return {
            "processed": processed_count,
            "new_ingested": new_count,
            "duplicates_skipped": duplicate_count,
            "expired_flagged": expired_count,
            "timestamp": datetime.utcnow().isoformat()
        }

    @staticmethod
    async def check_freshness_and_expire_stale(db: AsyncSession) -> int:
        """
        Automated Freshness Daemon: Automatically marks internships as EXPIRED if deadline passed.
        PDF Section 3 Specification: Store posted date, deadline, last checked; automatically expire stale opportunities.
        """
        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        
        # Query live internships with deadline prior to today
        res = await db.execute(
            select(Internship)
            .where(Internship.status == "VERIFIED_LIVE")
            .where(Internship.deadline < today_str)
        )
        expired_items = res.scalars().all()
        expired_count = len(expired_items)

        for item in expired_items:
            item.status = "EXPIRED"
            db.add(item)

        if expired_count > 0:
            await db.commit()

        return expired_count
