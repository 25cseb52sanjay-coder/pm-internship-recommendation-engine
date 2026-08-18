from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import DiscoverySearchQuery
import logging

logger = logging.getLogger(__name__)

INDIAN_CITIES = ["Bengaluru", "New Delhi", "Mumbai", "Pune", "Hyderabad", "Chennai", "Kolkata", "Bhopal", "Jamnagar"]
BRANCHES = ["B.Tech", "B.Sc", "B.Com", "BBA", "MBA", "M.Tech"]
SKILLS = ["Python", "Machine Learning", "Data Analysis", "SQL", "React", "Embedded Systems", "Financial Modeling", "AutoCAD"]
ROLES = ["AI & Data Analytics Intern", "Public Policy Intern", "EV Electronics Intern", "Financial Analyst Trainee", "Full-Stack Development Intern"]

QUERY_PATTERNS = [
    '"{role}" {city} 2026',
    '"{skill} intern" {city} India',
    'site:*.com/careers "{role}" India',
    'site:*.gov.in internship {city}',
    'site:*.org internship India'
]

async def generate_dynamic_search_queries(db: AsyncSession, limit: int = 10) -> List[DiscoverySearchQuery]:
    """
    Generates and rotates search queries dynamically across date, city, branch, skill, and role dimensions.
    Deduplicates against existing discovery_search_queries table records.
    """
    new_queries = []
    current_year = datetime.utcnow().year

    for city in INDIAN_CITIES[:4]:
        for role in ROLES[:3]:
            for skill in SKILLS[:3]:
                pattern = f'"{role}" {city} {skill} {current_year}'

                # Check deduplication
                res = await db.execute(
                    select(DiscoverySearchQuery).where(DiscoverySearchQuery.query_text == pattern)
                )
                if not res.scalar_one_or_none():
                    q_obj = DiscoverySearchQuery(
                        query_text=pattern,
                        category="Dynamic Generation",
                        city=city,
                        branch="B.Tech",
                        skill_tag=skill,
                        enabled=True
                    )
                    db.add(q_obj)
                    new_queries.append(q_obj)
                    if len(new_queries) >= limit:
                        break
            if len(new_queries) >= limit:
                break
        if len(new_queries) >= limit:
            break

    if not new_queries:
        # Fallback: Return active existing queries or generate timestamped variation
        res = await db.execute(
            select(DiscoverySearchQuery).where(DiscoverySearchQuery.enabled == True).limit(limit)
        )
        existing = res.scalars().all()
        if existing:
            return list(existing)
        
        # Fresh timestamped generation
        ts = int(datetime.utcnow().timestamp())
        q_obj = DiscoverySearchQuery(
            query_text=f'"AI & Data Analytics Intern" Bengaluru Python {current_year} batch_{ts}',
            category="Dynamic Generation",
            city="Bengaluru",
            branch="B.Tech",
            skill_tag="Python",
            enabled=True
        )
        db.add(q_obj)
        await db.commit()
        return [q_obj]

    if new_queries:
        await db.commit()
        logger.info(f"Query Generator: Generated {len(new_queries)} dynamic search queries.")

    return new_queries
