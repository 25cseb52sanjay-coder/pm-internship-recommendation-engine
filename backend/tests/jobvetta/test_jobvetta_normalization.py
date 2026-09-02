import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.jobvetta.connector import JobvettaConnector
from app.jobvetta.schemas import NormalizedJobvettaJob

def test_jobvetta_raw_validation_and_normalization():
    """Tests Jobvetta payload validation and normalization into project unified job model."""
    connector = JobvettaConnector(api_key="mock_key")

    raw_sample = {
        "id": "jobvetta_109283",
        "title": "Full Stack Software Engineering Intern",
        "company": {"name": "Tech Corp Pvt Ltd"},
        "description": "Develop modern web applications using React, Python FastAPI, PostgreSQL, and Docker microservices.",
        "location": {"display_name": "Bengaluru, Karnataka"},
        "category": "Software & Web Development",
        "salary_min": 15000,
        "salary_max": 25000,
        "employment_type": "Internship",
        "apply_url": "https://www.jobvetta.com/apply/109283"
    }

    assert connector.validate_raw(raw_sample)
    norm = connector.normalize_to_schema(raw_sample)

    assert norm.external_id == "jobvetta_109283"
    assert norm.title == "Full Stack Software Engineering Intern"
    assert norm.company == "Tech Corp Pvt Ltd"
    assert norm.location == "Bengaluru, Karnataka"
    assert norm.opportunity_type == "INTERNSHIP"
    assert norm.category == "Information Technology"
    assert norm.source == "Jobvetta"
    assert norm.apply_url == "https://www.jobvetta.com/apply/109283"
    assert "React" in norm.skills
    assert "Python" in norm.skills
