import re
from typing import Tuple, List

TECH_SKILL_KEYWORDS = [
    "python", "java", "javascript", "typescript", "react", "next.js", "node.js",
    "fastapi", "django", "flask", "sql", "postgresql", "mysql", "mongodb", "aws",
    "docker", "kubernetes", "git", "ci/cd", "rest api", "graphql", "machine learning",
    "data science", "data analytics", "c++", "c#", "html", "css", "tailwind",
    "product management", "ui/ux", "agile", "scrum", "devops", "cybersecurity"
]

class JobvettaClassifier:
    """
    Classifier for Jobvetta opportunities.
    Maps sector categories, opportunity types (JOB vs INTERNSHIP), work mode, and skills.
    """

    @staticmethod
    def classify_opportunity_type(title: str, description: str, employment_type: str = "") -> str:
        """Classifies opportunity as INTERNSHIP, JOB, or UNKNOWN."""
        combined = f"{title} {description} {employment_type}".lower()
        if any(term in combined for term in ["intern", "internship", "trainee", "apprentice", "fellowship", "stipend"]):
            return "INTERNSHIP"
        elif any(term in combined for term in ["full-time", "full time", "developer", "engineer", "analyst", "manager"]):
            return "JOB"
        return "INTERNSHIP"

    @staticmethod
    def classify_work_mode(location: str, description: str) -> str:
        """Determines work mode: Remote, Hybrid, or On-site."""
        combined = f"{location} {description}".lower()
        if "remote" in combined or "work from home" in combined or "wfh" in combined:
            return "Remote"
        elif "hybrid" in combined:
            return "Hybrid"
        return "On-site"

    @staticmethod
    def classify_sector(category_raw: str, title: str, description: str) -> str:
        """Maps sector to standardized scheme sector."""
        combined = f"{category_raw} {title} {description}".lower()
        if any(term in combined for term in ["software", "tech", "it", "web", "data", "ai", "machine learning", "cyber"]):
            return "Information Technology"
        elif any(term in combined for term in ["finance", "banking", "fintech", "accounting"]):
            return "Banking & Financial Services"
        elif any(term in combined for term in ["health", "bio", "pharma", "medical"]):
            return "Healthcare & Pharmaceuticals"
        elif any(term in combined for term in ["auto", "mechanical", "electrical", "manufacturing", "civil"]):
            return "Engineering & Manufacturing"
        elif any(term in combined for term in ["hr", "recruitment", "hiring"]):
            return "HR Tech & Platforms"
        return "Technology Services"

    @staticmethod
    def extract_skills(title: str, description: str) -> List[str]:
        """Extracts relevant technical and professional skills from title & description."""
        combined = f"{title} {description}".lower()
        found_skills = []
        for kw in TECH_SKILL_KEYWORDS:
            if re.search(r'\b' + re.escape(kw) + r'\b', combined):
                found_skills.append(kw.title())
        return list(dict.fromkeys(found_skills))[:8]
